#!/bin/zsh

set -euo pipefail
umask 077

PROJECT_ROOT="${0:A:h:h}"
cd "$PROJECT_ROOT"

RUN_ROOT="$PROJECT_ROOT/artifacts/runtime/impact-strong-baseline-study"
LOCK_DIR="$RUN_ROOT/runner.lock"
PID_FILE="$RUN_ROOT/runner.pid"
SENTIMENT_LOCK="$PROJECT_ROOT/artifacts/runtime/sentiment-v6-study/runner.lock"
mkdir -p "$RUN_ROOT"

if [[ -d "$SENTIMENT_LOCK" ]]; then
  print -u2 -- "감성 연구 실행기가 MPS를 사용 중이므로 중요도 비교 학습을 시작하지 않습니다."
  exit 78
fi
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  print -u2 -- "이미 중요도 공개 비교군 실행기가 동작 중입니다: $LOCK_DIR"
  exit 73
fi
print -r -- "$$" >| "$PID_FILE"
trap 'rm -f "$PID_FILE"; rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT INT TERM HUP

uv run python scripts/lock_k_fnspid_impact_strong_baseline_study.py
print -- "{\"event\":\"IMPACT_STRONG_BASELINE_STUDY_STARTED\",\"pid\":$$,\"started_at\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"

run_one() {
  local preset="$1"
  local source="$2"
  local seed="$3"
  local preset_slug="${preset:l:s/_/-/}"
  local source_slug="${source:l}"
  local root="artifacts/impact/strong-baselines/${preset_slug}/${source_slug}/seed${seed}"
  local report="reports/strong_baselines/impact/${preset_slug}/${source_slug}/seed${seed}.json"
  local predictions="reports/strong_baselines/impact/${preset_slug}/${source_slug}/seed${seed}-predictions.jsonl"
  local baseline="reports/k-fnspid-impact-training-report.json"
  local -a recipe=()
  local -a source_args=()

  if uv run python scripts/verify_k_fnspid_impact_baseline_artifact.py \
    --report "$report" --model-preset "$preset" --source-type "$source" --seed "$seed" \
    >/dev/null 2>&1; then
    print -- "{\"event\":\"IMPACT_BASELINE_REUSED\",\"preset\":\"${preset}\",\"source\":\"${source}\",\"seed\":${seed}}"
    return
  fi
  if [[ -e "$report" || -e "$root" || -e "$predictions" ]]; then
    print -u2 -- "불완전하거나 변조된 중요도 비교 artifact가 남아 있습니다: ${preset}/${source}/seed${seed}"
    exit 74
  fi

  if [[ "$source" == "SHARED" ]]; then
    recipe=(--max-length 256 --epochs 3 --learning-rate 2e-4 --focal-gamma 1.5 --ordinal-loss-weight 0.30 --label-smoothing 0.02)
    if [[ "$preset" == "KLUE_ROBERTA_LARGE" ]]; then
      recipe+=(--batch-size 1 --gradient-accumulation 32 --gradient-checkpointing)
    else
      recipe+=(--batch-size 8 --gradient-accumulation 4)
    fi
  elif [[ "$source" == "NEWS" ]]; then
    baseline="reports/k-fnspid-impact-news-training-report.json"
    source_args=(--source-type NEWS)
    recipe=(--max-length 256 --epochs 3 --learning-rate 2e-4 --focal-gamma 1.5 --ordinal-loss-weight 0.30 --label-smoothing 0.02 --batch-size 16 --gradient-accumulation 4)
    if [[ "$preset" == "KLUE_ROBERTA_LARGE" ]]; then
      recipe+=(--gradient-checkpointing)
    fi
    recipe+=(--initial-adapter-path "artifacts/impact/strong-baselines/${preset_slug}/shared/seed42" --evaluation-only)
  else
    baseline="reports/k-fnspid-impact-disclosure-training-report.json"
    source_args=(--source-type DISCLOSURE)
    recipe=(--max-length 128 --epochs 1 --learning-rate 5e-5 --focal-gamma 1.0 --ordinal-loss-weight 0.20 --label-smoothing 0.01)
    if [[ "$preset" == "KLUE_ROBERTA_LARGE" ]]; then
      recipe+=(--batch-size 1 --gradient-accumulation 32 --gradient-checkpointing)
    else
      recipe+=(--batch-size 16 --gradient-accumulation 2)
    fi
    recipe+=(--initial-adapter-path "artifacts/impact/strong-baselines/${preset_slug}/shared/seed42")
  fi

  mkdir -p "${report:h}" "${predictions:h}" "${root:h}"
  uv run python scripts/train_k_fnspid_transformer.py \
    --model-preset "$preset" \
    --seed "$seed" \
    --output-dir "$root" \
    --report-path "$report" \
    --predictions-path "$predictions" \
    --baseline-report-path "$baseline" \
    "${source_args[@]}" \
    "${recipe[@]}"

  uv run python scripts/verify_k_fnspid_impact_baseline_artifact.py \
    --report "$report" --model-preset "$preset" --source-type "$source" --seed "$seed"
}

aggregate_one() {
  local preset="$1"
  local source="$2"
  local preset_slug="${preset:l:s/_/-/}"
  local source_slug="${source:l}"
  local output="reports/strong_baselines/impact/${preset_slug}/${source_slug}/multiseed.json"
  uv run python scripts/aggregate_k_fnspid_runs.py \
    --report "reports/strong_baselines/impact/${preset_slug}/${source_slug}/seed17.json" \
    --report "reports/strong_baselines/impact/${preset_slug}/${source_slug}/seed42.json" \
    --report "reports/strong_baselines/impact/${preset_slug}/${source_slug}/seed73.json" \
    --output "$output"
}

for preset in KR_FINBERT_SC KLUE_ROBERTA_LARGE; do
  for seed in 17 42 73; do
    run_one "$preset" SHARED "$seed"
  done
  aggregate_one "$preset" SHARED
  run_one "$preset" NEWS 73
  for seed in 17 42 73; do
    run_one "$preset" DISCLOSURE "$seed"
  done
  aggregate_one "$preset" DISCLOSURE
done

uv run python scripts/evaluate_k_fnspid_impact_strong_baselines.py \
  --output reports/k-fnspid-impact-strong-baseline-matrix.json \
  --bootstrap-samples 2000 \
  --seed 20260718

print -- "{\"event\":\"IMPACT_STRONG_BASELINE_STUDY_COMPLETED\",\"completed_at\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
