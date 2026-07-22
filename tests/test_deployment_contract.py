from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_production_uses_single_container_with_rollback() -> None:
    deploy = _read("scripts/deploy-prod.sh")
    workflow = _read(".github/workflows/ci.yml")

    assert "previous_image" in deploy
    assert "rollback" in deploy
    assert "active-slot" not in deploy
    assert "inactive=blue" not in deploy
    assert "inactive=green" not in deploy
    assert '--network "${NETWORK}"' in deploy
    assert "GHCR_USERNAME" in deploy
    assert "https://api.github.com/user" in workflow
    assert "secrets.GHCR_TOKEN" in workflow
    assert "secrets.GHCR_USERNAME" not in workflow


def test_ci_installs_transformer_runtime_for_model_contracts() -> None:
    workflow = _read(".github/workflows/ci.yml")

    assert "uv sync --all-groups --extra transformer" in workflow


def test_ci_restores_only_required_lfs_inputs_before_model_contracts() -> None:
    workflow = _read(".github/workflows/ci.yml")

    assert "git lfs pull" in workflow
    assert "data/k_fnspid/v4/documents.parquet" in workflow
    assert "data/external/kf_deberta_benchmark/ratings_train.csv" in workflow
    assert "data/external/kf_deberta_benchmark/ratings_val.csv" in workflow
    assert '--exclude=""' in workflow
    assert "CI LFS 포인터가 남아 있습니다" in workflow


def test_ci_restores_and_hash_verifies_pinned_dapt_base_model() -> None:
    workflow = _read(".github/workflows/ci.yml")
    restore = _read("scripts/restore_ci_dapt_base_model.py")

    assert "scripts/restore_ci_dapt_base_model.py" in workflow
    assert "HF_HUB_DISABLE_TELEMETRY" in workflow
    assert "dapt.BASE_MODEL" in restore
    assert "dapt.BASE_REVISION" in restore
    assert "dapt.BASE_FILE_HASHES" in restore
    assert "dapt.sha256_file(path)" in restore


def test_production_preserves_current_model_for_runtime_only_deployment() -> None:
    workflow = _read(".github/workflows/ci.yml")
    overlay = _read("Dockerfile.runtime-overlay")
    release_condition = "if: steps.sentiment_release.outputs.active == 'true'"

    assert "- name: 활성 감성 릴리스 확인" in workflow
    assert "if [[ -f releases/sentiment/current.json ]]" in workflow
    assert "승격된 감성 릴리스가 없어 기존 운영 이미지를 유지합니다." in workflow
    assert workflow.count(release_condition) == 8
    assert "deploy-runtime-overlay:" in workflow
    assert "현재 운영 이미지 고정" in workflow
    assert "git merge-base --is-ancestor" in workflow
    assert "docker buildx imagetools inspect" in workflow
    assert "BASE_IMAGE=${{ steps.current_image.outputs.pinned }}" in workflow
    assert "Dockerfile.runtime-overlay" in workflow
    assert "ARG BASE_IMAGE" in overlay
    assert "FROM ${BASE_IMAGE}" in overlay
    assert "COPY releases" not in overlay
    assert "COPY src ./src" in overlay
    assert "VERIFY_SENTIMENT_RELEASE=true" in workflow
    assert "VERIFY_SENTIMENT_RELEASE=false" in workflow
    assert "verify_image_has_no_release" in _read("scripts/deploy-prod.sh")
    assert "test ! -e /app/releases/sentiment/current.json" in _read(
        "scripts/deploy-prod.sh"
    )


def test_oci_ssh_requires_pinned_key_and_password_authentication() -> None:
    workflow = _read(".github/workflows/ci.yml")
    askpass = _read("scripts/ssh-askpass.sh")

    assert "secrets.PROD_SSH_PASSWORD" in workflow
    assert "StrictHostKeyChecking yes" in workflow
    assert "PreferredAuthentications publickey,password" in workflow
    assert "SSH_ASKPASS" in workflow
    assert "scripts/ssh-askpass.sh" in workflow
    assert "ControlMaster" not in workflow
    assert "ControlPersist" not in workflow
    assert '"${PROD_SSH_PASSWORD}"' in askpass


def test_qwen_is_pinned_and_private() -> None:
    compose = _read("deploy/compose/hannah-qwen.yml")
    local_compose = _read("compose.local.yml")
    downloader = _read("scripts/download-qwen-model.sh")
    workflow = _read(".github/workflows/ci.yml")

    assert "llama.cpp:server@sha256:" in compose
    assert 'user: "65532:65532"' in compose
    assert "mem_limit: 10g" in compose
    assert "cpus: 3.0" in compose
    assert '- "4096"' in compose
    assert "127.0.0.1:18081:8080" in compose
    assert "external: true" in compose
    assert "7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5" in downloader
    assert "http://hannah-qwen:8080" in workflow
    assert "HANNAH_KOREAN_TRANSLATION_LLM_TIMEOUT_SECONDS=600" in workflow
    assert "secrets.HANNAH_KOREAN_TRANSLATION_LLM_ENDPOINT" not in workflow
    assert "http://hannah-qwen:8080" in local_compose
    assert "host.docker.internal" not in local_compose
    assert "hannah-qwen" in local_compose


def test_production_requires_discord_and_exports_metrics() -> None:
    workflow = _read(".github/workflows/ci.yml")
    main = _read("src/hannah_montana_ai/main.py")

    assert "secrets.HANNAH_DISCORD_WEBHOOK_URL" in workflow
    assert "HANNAH_RUNTIME_ENVIRONMENT=production" in workflow
    assert '@app.get("/metrics", include_in_schema=False)' in main


def test_maintenance_token_is_derived_from_the_shared_oci_host_root() -> None:
    workflow = _read(".github/workflows/ci.yml")
    bootstrap = _read("scripts/bootstrap-host.sh")
    runtime_secrets = _read("scripts/runtime-secrets.sh")
    deploy = _read("scripts/deploy-prod.sh")

    assert "secrets.HANNAH_AI_MAINTENANCE_TOKEN" not in workflow
    assert "scripts/runtime-secrets.sh" in workflow
    assert "ensure_runtime_root_secret" in bootstrap
    assert "HANA_RUNTIME_SECRET_DIR=/opt/hana-runtime" in runtime_secrets
    assert "root-secret" in runtime_secrets
    assert "openssl rand -hex 32" in runtime_secrets
    assert "flock -x" in runtime_secrets
    assert "hana/ai/maintenance-auth/v1" in deploy
    assert 'HANNAH_AI_MAINTENANCE_TOKEN=${ai_token}' in deploy
    assert '--env-file "${RUNTIME_APP_ENV}"' in deploy
