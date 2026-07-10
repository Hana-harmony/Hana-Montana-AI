#!/usr/bin/env bash
set -euo pipefail

MODEL_PATH="${HANNAH_QWEN3_4B_GGUF_PATH:-${HOME}/.cache/hana/models/Qwen3-4B-Q4_K_M.gguf}"
HOST="${HANNAH_QWEN3_HOST:-127.0.0.1}"
PORT="${HANNAH_QWEN3_PORT:-18081}"
MODEL_ALIAS="${HANNAH_QWEN3_MODEL_ALIAS:-Qwen3-4B-GGUF-Q4}"
CONTEXT_SIZE="${HANNAH_QWEN3_CONTEXT_SIZE:-16384}"
THREADS="${HANNAH_QWEN3_THREADS:-4}"
PARALLEL="${HANNAH_QWEN3_PARALLEL:-4}"

if ! command -v llama-server >/dev/null 2>&1; then
  echo "Qwen3 GGUF 실행을 위해 llama-server가 필요합니다." >&2
  exit 1
fi

if [[ ! -f "${MODEL_PATH}" ]]; then
  echo "Qwen3 GGUF 모델 파일이 없습니다: ${MODEL_PATH}" >&2
  echo "HANNAH_QWEN3_4B_GGUF_PATH에 Qwen3-4B Q4 GGUF 경로를 지정하세요." >&2
  exit 1
fi

exec llama-server \
  --host "${HOST}" \
  --port "${PORT}" \
  --model "${MODEL_PATH}" \
  --alias "${MODEL_ALIAS}" \
  --ctx-size "${CONTEXT_SIZE}" \
  --threads "${THREADS}" \
  --parallel "${PARALLEL}" \
  --reasoning off \
  --temp 0
