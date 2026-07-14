#!/usr/bin/env bash
set -euo pipefail

MODEL_DIR="${1:?model directory is required}"
MODEL_FILE="${MODEL_DIR}/Qwen3-4B-Q4_K_M.gguf"
MODEL_URL='https://huggingface.co/Qwen/Qwen3-4B-GGUF/resolve/bc640142c66e1fdd12af0bd68f40445458f3869b/Qwen3-4B-Q4_K_M.gguf?download=true'
MODEL_SHA256=7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5

file_sha256() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  else
    shasum -a 256 "$1" | awk '{print $1}'
  fi
}

install -d -m 0755 "${MODEL_DIR}"
if [[ -f "${MODEL_FILE}" ]] \
  && [[ "$(file_sha256 "${MODEL_FILE}")" == "${MODEL_SHA256}" ]]; then
  exit 0
fi

temporary="$(mktemp "${MODEL_DIR}/qwen.XXXXXX")"
trap 'rm -f "${temporary:-}"' EXIT
curl --fail --location --proto '=https' --tlsv1.2 \
  --retry 5 --retry-all-errors --output "${temporary}" "${MODEL_URL}"
[[ "$(file_sha256 "${temporary}")" == "${MODEL_SHA256}" ]]
chmod 0444 "${temporary}"
mv "${temporary}" "${MODEL_FILE}"
trap - EXIT
