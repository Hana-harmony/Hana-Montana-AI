#!/usr/bin/env bash
set -euo pipefail

APP_DIR=/opt/hannah-montana-ai
APP_NAME=hannah-montana-ai
APP_PORT=18000
NETWORK=hana-omni-connect-internal
RUNTIME_APP_ENV="${APP_DIR}/runtime-application.env"
PROVIDER_APP_ENV="${APP_DIR}/provider-application.env"

source "${APP_DIR}/deploy.env"
source "${APP_DIR}/runtime-secrets.sh"

: "${IMAGE:?IMAGE is required}"
: "${GHCR_USERNAME:?GHCR_USERNAME is required}"
: "${GHCR_TOKEN:?GHCR_TOKEN is required}"
: "${VERIFY_SENTIMENT_RELEASE:=true}"
test -s "${PROVIDER_APP_ENV}"

case "${VERIFY_SENTIMENT_RELEASE}" in
  true)
    test -s "${APP_DIR}/sentiment-release-public-key.pem"
    release_mount_args=(
      --mount
      "type=bind,src=${APP_DIR}/sentiment-release-public-key.pem,dst=/run/secrets/sentiment-release-public-key.pem,readonly"
    )
    ;;
  false)
    release_mount_args=()
    ;;
  *)
    echo 'VERIFY_SENTIMENT_RELEASE must be true or false' >&2
    exit 1
    ;;
esac

write_runtime_secret_env() {
  local ai_token temp_file
  ai_token="$(derive_runtime_secret_hex 'hana/ai/maintenance-auth/v1')"
  temp_file="$(mktemp "${APP_DIR}/.runtime-application.XXXXXX")"

  umask 077
  printf '%s\n' \
    "HANNAH_AI_MAINTENANCE_TOKEN=${ai_token}" \
    "HANNAH_SENTIMENT_RELEASE_REQUIRED=${VERIFY_SENTIMENT_RELEASE}" \
    > "${temp_file}"
  chmod 600 "${temp_file}"
  mv "${temp_file}" "${RUNTIME_APP_ENV}"
}

write_runtime_secret_env

run_container() {
  local image="$1"
  docker run -d \
    --name "${APP_NAME}" \
    --restart unless-stopped \
    --read-only \
    --cap-drop ALL \
    --security-opt no-new-privileges:true \
    --pids-limit 512 \
    --memory 7g \
    --cpus 1.5 \
    --env-file "${APP_DIR}/application.env" \
    --env-file "${PROVIDER_APP_ENV}" \
    "${release_mount_args[@]}" \
    --env-file "${RUNTIME_APP_ENV}" \
    --network "${NETWORK}" \
    --tmpfs /tmp:rw,noexec,nosuid,size=512m \
    --tmpfs /app/.cache:rw,noexec,nosuid,size=256m,uid=65532,gid=65532 \
    -p "127.0.0.1:${APP_PORT}:8000" \
    "${image}"
}

verify_image_release() {
  local image="$1"
  docker run --rm \
    --read-only \
    --cap-drop ALL \
    --security-opt no-new-privileges:true \
    --network none \
    --pids-limit 128 \
    --memory 2g \
    --cpus 1 \
    --env-file "${APP_DIR}/application.env" \
    --env-file "${PROVIDER_APP_ENV}" \
    --mount "type=bind,src=${APP_DIR}/sentiment-release-public-key.pem,dst=/run/secrets/sentiment-release-public-key.pem,readonly" \
    --entrypoint python \
    "${image}" \
    /app/scripts/verify_sentiment_release.py \
    --current /app/releases/sentiment/current.json \
    --project-root /app \
    --base-model-runtime-path /release-tree-bound-v6 \
    --runtime-environment production \
    --attestation-mode dsse-ed25519-v1 \
    --public-key /run/secrets/sentiment-release-public-key.pem
}

verify_image_has_no_release() {
  local image="$1"
  docker run --rm \
    --read-only \
    --cap-drop ALL \
    --security-opt no-new-privileges:true \
    --network none \
    --pids-limit 32 \
    --memory 128m \
    --cpus 0.25 \
    --entrypoint /bin/sh \
    "${image}" \
    -eu -c 'test ! -e /app/releases/sentiment/current.json'
}

wait_until_ready() {
  for _ in $(seq 1 120); do
    if curl --fail --silent --show-error "http://127.0.0.1:${APP_PORT}/ready" >/dev/null; then
      return 0
    fi
    sleep 2
  done
  return 1
}

stop_container() {
  if docker container inspect "${APP_NAME}" >/dev/null 2>&1; then
    docker stop --time 30 "${APP_NAME}" >/dev/null || true
    docker rm "${APP_NAME}" >/dev/null 2>&1 || true
  fi
}

previous_image="$(docker inspect --format '{{.Config.Image}}' "${APP_NAME}" 2>/dev/null || true)"

rollback() {
  docker logs --tail 200 "${APP_NAME}" 2>/dev/null || true
  docker rm -f "${APP_NAME}" >/dev/null 2>&1 || true
  if [[ -n "${previous_image}" ]]; then
    run_container "${previous_image}" >/dev/null
    wait_until_ready || true
  fi
  exit 1
}

install_nginx_config() {
  local upstream_path=/etc/nginx/conf.d/hannah-montana-ai-upstream.conf
  local server_path=/etc/nginx/conf.d/hannah-montana-ai.conf
  local backup_dir
  local had_upstream=false
  local had_server=false
  backup_dir="$(mktemp -d)"

  if sudo test -f "${upstream_path}"; then
    sudo cat "${upstream_path}" > "${backup_dir}/upstream.conf"
    had_upstream=true
  fi
  if sudo test -f "${server_path}"; then
    sudo cat "${server_path}" > "${backup_dir}/server.conf"
    had_server=true
  fi

  printf 'upstream hannah_montana_ai { server 127.0.0.1:%s; keepalive 16; }\n' "${APP_PORT}" > "${backup_dir}/new-upstream.conf"
  if ! sudo install -o root -g root -m 0644 "${backup_dir}/new-upstream.conf" "${upstream_path}" \
    || ! sudo install -o root -g root -m 0644 "${APP_DIR}/hannah-montana-ai.conf" "${server_path}" \
    || ! sudo nginx -t; then
    if [[ "${had_upstream}" == true ]]; then
      sudo install -o root -g root -m 0644 "${backup_dir}/upstream.conf" "${upstream_path}"
    else
      sudo rm -f "${upstream_path}"
    fi
    if [[ "${had_server}" == true ]]; then
      sudo install -o root -g root -m 0644 "${backup_dir}/server.conf" "${server_path}"
    else
      sudo rm -f "${server_path}"
    fi
    sudo nginx -t >/dev/null 2>&1 || true
    rm -rf "${backup_dir}"
    return 1
  fi

  rm -rf "${backup_dir}"
}

docker network inspect "${NETWORK}" >/dev/null 2>&1 \
  || docker network create "${NETWORK}" >/dev/null
printf '%s' "${GHCR_TOKEN}" | docker login ghcr.io -u "${GHCR_USERNAME}" --password-stdin
docker pull "${IMAGE}"
if [[ "${VERIFY_SENTIMENT_RELEASE}" == true ]]; then
  verify_image_release "${IMAGE}"
else
  verify_image_has_no_release "${IMAGE}"
fi

install_nginx_config

stop_container
run_container "${IMAGE}" >/dev/null || rollback
wait_until_ready || rollback

sudo systemctl reload nginx || rollback
curl --fail --silent --show-error http://127.0.0.1:18090/ready >/dev/null || rollback
docker image prune -f >/dev/null
