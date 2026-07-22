#!/bin/zsh

set -euo pipefail
umask 077

PROJECT_ROOT="${0:A:h:h}"
cd "$PROJECT_ROOT"

RUN_ROOT="$PROJECT_ROOT/artifacts/runtime/sentiment-v6-study"
LOCK_DIR="$RUN_ROOT/runner.lock"
PID_FILE="$RUN_ROOT/runner.pid"
mkdir -p "$RUN_ROOT"

release_stale_lock() {
  local recorded_pid=""
  [[ -f "$PID_FILE" ]] && recorded_pid="$(<"$PID_FILE")"
  if [[ "$recorded_pid" =~ '^[0-9]+$' ]] && kill -0 "$recorded_pid" 2>/dev/null; then
    return
  fi
  rm -f "$PID_FILE"
  rmdir "$LOCK_DIR" 2>/dev/null || true
}

cleanup_lock() {
  local recorded_pid=""
  [[ -f "$PID_FILE" ]] && recorded_pid="$(<"$PID_FILE")"
  if [[ "$recorded_pid" == "$$" ]]; then
    rm -f "$PID_FILE"
    rmdir "$LOCK_DIR" 2>/dev/null || true
  fi
}

[[ -d "$LOCK_DIR" ]] && release_stale_lock
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  print -u2 -- "이미 sentiment v6 연구 실행기가 동작 중입니다: $LOCK_DIR"
  exit 73
fi
print -r -- "$$" >| "$PID_FILE"
trap cleanup_lock EXIT INT TERM HUP

print -- "{\"event\":\"STUDY_RUNNER_STARTED\",\"pid\":$$,\"started_at\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"

run_candidate() {
  local seed="$1"
  local output_dir="artifacts/sentiment/v6-candidates/seed${seed}"
  local report_path="reports/candidates/kf-deberta-sentiment-v6-seed${seed}.json"
  local migration_path="artifacts/sentiment/v6-candidates/.seed${seed}-training-checkpoints/stage1/epoch-002/context-migration.json"
  local stage2_migration_path="artifacts/sentiment/v6-candidates/.seed${seed}-training-checkpoints/stage2/epoch-004/context-migration.json"
  local -a migration_args=()
  local -a stage2_migration_args=()

  if [[ -f "$report_path" && -d "$output_dir" ]]; then
    print -- "{\"event\":\"CANDIDATE_SKIPPED_COMPLETE\",\"seed\":${seed}}"
    return
  fi
  if [[ -e "$report_path" || -e "$output_dir" ]]; then
    print -u2 -- "seed ${seed} 후보의 artifact/report가 불완전하게 남아 있습니다."
    exit 74
  fi
  if [[ -f "$migration_path" ]]; then
    migration_args=(--checkpoint-context-migration "$migration_path")
  fi
  if [[ -f "$stage2_migration_path" ]]; then
    stage2_migration_args=(--stage2-checkpoint-context-migration "$stage2_migration_path")
  fi

  uv run python scripts/train_kf_deberta_sentiment_v6.py \
    --base-source artifacts/pretraining/kf-deberta-k-fnspid-v4-dapt-temporal-v2 \
    --output-dir "$output_dir" \
    --report-path "$report_path" \
    --seed "$seed" \
    --device mps \
    --gradient-checkpointing \
    "${migration_args[@]}" \
    "${stage2_migration_args[@]}"
}

run_baseline() {
  local seed="$1"
  local output_dir="artifacts/sentiment/fair_baselines/kr-finbert-sc-v6/seed${seed}"
  local report_path="reports/fair_baselines/kr-finbert-sc-v6/seed${seed}.json"

  if [[ -f "$report_path" && -d "$output_dir" ]]; then
    print -- "{\"event\":\"BASELINE_SKIPPED_COMPLETE\",\"seed\":${seed}}"
    return
  fi
  if [[ -e "$report_path" || -e "$output_dir" ]]; then
    print -u2 -- "seed ${seed} 기준선의 artifact/report가 불완전하게 남아 있습니다."
    exit 75
  fi

  uv run python scripts/train_kr_finbert_sc_sentiment_v6.py \
    --seed "$seed" \
    --device mps \
    --gradient-checkpointing
}

run_ablation() {
  local mode="$1"
  local seed="$2"
  local slug="${mode:l:s/_/-/}"
  local output_dir="artifacts/sentiment/v6-ablations/${slug}/seed${seed}"
  local report_path="reports/ablations/v6/${slug}/kf-deberta-sentiment-v6-${slug}-seed${seed}.json"

  if [[ "$mode" == "FULL" ]]; then
    if [[ -f "$report_path" && ! -e "$output_dir" ]]; then
      print -- "{\"event\":\"ABLATION_REUSE_SKIPPED_COMPLETE\",\"mode\":\"${mode}\",\"seed\":${seed}}"
      return
    fi
    if [[ -e "$report_path" || -e "$output_dir" ]]; then
      print -u2 -- "${mode} seed ${seed} 재사용 영수증 또는 불필요한 중복 artifact가 남아 있습니다."
      exit 76
    fi
    uv run python scripts/train_kf_deberta_sentiment_v6_ablation.py \
      --mode "$mode" \
      --seed "$seed" \
      --base-source artifacts/pretraining/kf-deberta-k-fnspid-v4-dapt-temporal-v2 \
      --gradient-checkpointing \
      --reuse-full-candidate
    return
  fi

  if [[ -f "$report_path" && -d "$output_dir" ]]; then
    print -- "{\"event\":\"ABLATION_SKIPPED_COMPLETE\",\"mode\":\"${mode}\",\"seed\":${seed}}"
    return
  fi
  if [[ -e "$report_path" || -e "$output_dir" ]]; then
    print -u2 -- "${mode} seed ${seed} 제거 실험의 artifact/report가 불완전하게 남아 있습니다."
    exit 76
  fi

  uv run python scripts/train_kf_deberta_sentiment_v6_ablation.py \
    --mode "$mode" \
    --seed "$seed" \
    --base-source artifacts/pretraining/kf-deberta-k-fnspid-v4-dapt-temporal-v2 \
    --device mps \
    --gradient-checkpointing
}

aggregate_ablation_mode() {
  local mode="$1"
  local slug="${mode:l:s/_/-/}"
  local selection_path="reports/ablations/v6/${slug}/selection.json"
  local winner_path="reports/ablations/v6/${slug}/winner-manifest.json"
  local -a validation_args=()

  if [[ -e "$selection_path" && -e "$winner_path" ]]; then
    validation_args=(--validate-only)
    print -- "{\"event\":\"ABLATION_AGGREGATE_VALIDATING_EXISTING\",\"mode\":\"${mode}\"}"
  elif [[ -e "$selection_path" || -e "$winner_path" ]]; then
    print -u2 -- "${mode} 집계 출력이 일부만 존재합니다."
    exit 77
  fi

  uv run python scripts/train_kf_deberta_sentiment_v6_ablation.py \
    --mode "$mode" \
    --seed 17 \
    --base-source artifacts/pretraining/kf-deberta-k-fnspid-v4-dapt-temporal-v2 \
    --gradient-checkpointing \
    --aggregate \
    "${validation_args[@]}"
}

aggregate_ablation_matrix() {
  local matrix_path="reports/ablations/v6/matrix.json"
  local -a validation_args=()

  if [[ -e "$matrix_path" ]]; then
    validation_args=(--validate-only)
    print -- '{"event":"ABLATION_MATRIX_VALIDATING_EXISTING"}'
  fi
  uv run python scripts/train_kf_deberta_sentiment_v6_ablation.py \
    --aggregate-matrix \
    "${validation_args[@]}"
}

for seed in 17 42 73; do
  run_candidate "$seed"
done

for seed in 17 42 73; do
  run_baseline "$seed"
done
uv run python scripts/train_kr_finbert_sc_sentiment_v6.py --aggregate-only

for mode in NO_K NEWS_ONLY DISCLOSURE_ONLY FULL; do
  for seed in 17 42 73; do
    run_ablation "$mode" "$seed"
  done
  aggregate_ablation_mode "$mode"
done
aggregate_ablation_matrix

print -- "{\"event\":\"STUDY_RUNNER_COMPLETED\",\"completed_at\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
