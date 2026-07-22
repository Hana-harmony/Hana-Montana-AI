#!/bin/zsh

set -euo pipefail
umask 077

PROJECT_ROOT="${0:A:h:h}"
cd "$PROJECT_ROOT"

QUEUE_ROOT="$PROJECT_ROOT/artifacts/runtime/impact-strong-baseline-queue"
QUEUE_LOCK="$QUEUE_ROOT/queue.lock"
QUEUE_PID="$QUEUE_ROOT/queue.pid"
SENTIMENT_LOCK="$PROJECT_ROOT/artifacts/runtime/sentiment-v6-study/runner.lock"
mkdir -p "$QUEUE_ROOT"

release_stale_lock() {
  local recorded_pid=""
  [[ -f "$QUEUE_PID" ]] && recorded_pid="$(<"$QUEUE_PID")"
  if [[ "$recorded_pid" =~ '^[0-9]+$' ]] && kill -0 "$recorded_pid" 2>/dev/null; then
    return
  fi
  rm -f "$QUEUE_PID"
  rmdir "$QUEUE_LOCK" 2>/dev/null || true
}

[[ -d "$QUEUE_LOCK" ]] && release_stale_lock

if ! mkdir "$QUEUE_LOCK" 2>/dev/null; then
  print -u2 -- "이미 중요도 비교 대기열이 동작 중입니다: $QUEUE_LOCK"
  exit 73
fi
print -r -- "$$" >| "$QUEUE_PID"
trap 'rm -f "$QUEUE_PID"; rmdir "$QUEUE_LOCK" 2>/dev/null || true' EXIT INT TERM HUP

print -- "{\"event\":\"IMPACT_STRONG_BASELINE_QUEUED\",\"pid\":$$,\"queued_at\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
while [[ -d "$SENTIMENT_LOCK" ]]; do
  sleep 60
done

print -- "{\"event\":\"IMPACT_STRONG_BASELINE_DEQUEUED\",\"started_at\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
rm -f "$QUEUE_PID"
rmdir "$QUEUE_LOCK"
trap - EXIT INT TERM HUP
exec "$PROJECT_ROOT/scripts/run_impact_strong_baseline_study.sh"
