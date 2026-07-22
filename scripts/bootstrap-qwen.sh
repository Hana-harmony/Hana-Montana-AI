#!/usr/bin/env bash
set -euo pipefail

APP_DIR=/opt/hannah-montana-ai
MODEL_DIR="${APP_DIR}/models"
COMPOSE_FILE="${APP_DIR}/hannah-qwen.yml"

if [[ ! -s "${COMPOSE_FILE}" ]]; then
  echo "Qwen compose file is missing" >&2
  exit 1
fi

"${APP_DIR}/download-qwen-model.sh" "${MODEL_DIR}"

docker network inspect hana-omni-connect-internal >/dev/null 2>&1 \
  || docker network create hana-omni-connect-internal >/dev/null
docker compose -f "${COMPOSE_FILE}" pull
docker compose -f "${COMPOSE_FILE}" up -d --remove-orphans

for _ in $(seq 1 180); do
  if curl --fail --silent --show-error http://127.0.0.1:18081/health >/dev/null; then
    exit 0
  fi
  sleep 2
done

docker logs --tail 200 hannah-qwen || true
exit 1
