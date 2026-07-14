from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_production_uses_single_container_with_rollback() -> None:
    deploy = _read("scripts/deploy-prod.sh")

    assert "previous_image" in deploy
    assert "rollback" in deploy
    assert "active-slot" not in deploy
    assert "inactive=blue" not in deploy
    assert "inactive=green" not in deploy
    assert "--network \"${NETWORK}\"" in deploy
    assert "GHCR_USERNAME" in deploy


def test_qwen_is_pinned_and_private() -> None:
    compose = _read("deploy/compose/hannah-qwen.yml")
    local_compose = _read("compose.local.yml")
    downloader = _read("scripts/download-qwen-model.sh")
    workflow = _read(".github/workflows/ci.yml")

    assert "llama.cpp:server@sha256:" in compose
    assert "user: \"65532:65532\"" in compose
    assert "mem_limit: 6g" in compose
    assert "127.0.0.1:18081:8080" in compose
    assert "external: true" in compose
    assert "7485fe6f11af29433bc51cab58009521f205840f5b4ae3a32fa7f92e8534fdf5" in downloader
    assert "http://hannah-qwen:8080" in workflow
    assert "secrets.HANNAH_KOREAN_TRANSLATION_LLM_ENDPOINT" not in workflow
    assert "http://hannah-qwen:8080" in local_compose
    assert "host.docker.internal" not in local_compose
    assert "hannah-qwen" in local_compose
