#!/bin/zsh

set -euo pipefail
umask 077

PROJECT_ROOT="${0:A:h:h}"
cd "$PROJECT_ROOT"

RUN_ROOT="$PROJECT_ROOT/artifacts/runtime/impact-kr-finbert-recovery"
LOCK_DIR="$RUN_ROOT/runner.lock"
PID_FILE="$RUN_ROOT/runner.pid"
SENTIMENT_LOCK="$PROJECT_ROOT/artifacts/runtime/sentiment-v6-study/runner.lock"
mkdir -p "$RUN_ROOT"

[[ ! -d "$SENTIMENT_LOCK" ]] || {
  print -u2 -- "감성 연구 실행기가 MPS를 사용 중입니다."
  exit 78
}
mkdir "$LOCK_DIR" 2>/dev/null || {
  print -u2 -- "KR-FinBERT-SC 복구 실행기가 이미 동작 중입니다."
  exit 73
}
print -r -- "$$" >| "$PID_FILE"
trap 'rm -f "$PID_FILE"; rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT INT TERM HUP

verify_hash() {
  local expected="$1"
  local file_path="$2"
  local actual="$(shasum -a 256 "$file_path" | awk '{print $1}')"
  [[ "$actual" == "$expected" ]] || {
    print -u2 -- "잠긴 파일 해시가 다릅니다: $file_path"
    exit 76
  }
}

verify_hash 9ef2b862eb0c20c96e5ecdd851613b8291b6b1bed8deabbcfea1d83f6806d2da \
  reports/k-fnspid-impact-strong-baseline-study-contract.json
verify_hash 1377ffe0c08f517d1b13d1547d02dbeeef08007a56bcb8e268aa19a5d4f9c67e \
  scripts/train_k_fnspid_transformer.py
verify_hash 7cef53d44044f6240230a8153d923ba41d1b47180c16609d3af2d7d92c06cb53 \
  scripts/verify_k_fnspid_impact_baseline_artifact.py

verify_one() {
  local source="$1"
  local seed="$2"
  local source_slug="${source:l}"
  uv run python scripts/verify_k_fnspid_impact_baseline_artifact.py \
    --report "reports/strong_baselines/impact/kr-finbert_sc/${source_slug}/seed${seed}.json" \
    --model-preset KR_FINBERT_SC \
    --source-type "$source" \
    --seed "$seed"
}

for seed in 17 42 73; do
  verify_one SHARED "$seed"
done
verify_one NEWS 73

run_disclosure() {
  local seed="$1"
  local root="artifacts/impact/strong-baselines/kr-finbert_sc/disclosure/seed${seed}"
  local report="reports/strong_baselines/impact/kr-finbert_sc/disclosure/seed${seed}.json"
  local predictions="reports/strong_baselines/impact/kr-finbert_sc/disclosure/seed${seed}-predictions.jsonl"

  if verify_one DISCLOSURE "$seed" >/dev/null 2>&1; then
    print -- "{\"event\":\"IMPACT_BASELINE_REUSED\",\"preset\":\"KR_FINBERT_SC\",\"source\":\"DISCLOSURE\",\"seed\":${seed}}"
    return
  fi
  if [[ -e "$report" || -e "$root" || -e "$predictions" ]]; then
    print -u2 -- "불완전하거나 변조된 공시 비교 artifact가 남아 있습니다: seed${seed}"
    exit 74
  fi

  mkdir -p "${report:h}" "${predictions:h}" "${root:h}"
  uv run python scripts/train_k_fnspid_transformer.py \
    --model-preset KR_FINBERT_SC \
    --seed "$seed" \
    --output-dir "$root" \
    --report-path "$report" \
    --predictions-path "$predictions" \
    --baseline-report-path reports/k-fnspid-impact-disclosure-training-report.json \
    --source-type DISCLOSURE \
    --max-length 128 \
    --epochs 1 \
    --learning-rate 5e-5 \
    --focal-gamma 1.0 \
    --ordinal-loss-weight 0.20 \
    --label-smoothing 0.01 \
    --batch-size 16 \
    --gradient-accumulation 2 \
    --initial-adapter-path artifacts/impact/strong-baselines/kr-finbert_sc/shared/seed42
  verify_one DISCLOSURE "$seed"
}

print -- "{\"event\":\"KR_FINBERT_IMPACT_RECOVERY_STARTED\",\"pid\":$$}"
for seed in 17 42 73; do
  run_disclosure "$seed"
done

uv run python scripts/aggregate_k_fnspid_runs.py \
  --report reports/strong_baselines/impact/kr-finbert_sc/disclosure/seed17.json \
  --report reports/strong_baselines/impact/kr-finbert_sc/disclosure/seed42.json \
  --report reports/strong_baselines/impact/kr-finbert_sc/disclosure/seed73.json \
  --output reports/strong_baselines/impact/kr-finbert_sc/disclosure/multiseed.json

print -- "{\"event\":\"KR_FINBERT_IMPACT_RECOVERY_COMPLETED\"}"
