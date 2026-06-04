import os
from pathlib import Path

import pytest

from hannah_montana_ai.training.collector import (
    ProviderCredentialError,
    collect_naver_news,
    collect_open_dart,
    load_local_env,
)


def test_load_local_env_does_not_override_existing_secret(monkeypatch, tmp_path: Path) -> None:
    env_path = tmp_path / "secrets.local.env"
    env_path.write_text(
        "NAVER_NEWS_CLIENT_ID=from-file\n"
        "NAVER_NEWS_CLIENT_SECRET=from-file-secret\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("NAVER_NEWS_CLIENT_ID", "existing")

    load_local_env(env_path)

    assert "NAVER_NEWS_CLIENT_SECRET" in os.environ
    assert os.environ["NAVER_NEWS_CLIENT_ID"] == "existing"


def test_naver_collection_requires_credentials_before_network(monkeypatch) -> None:
    monkeypatch.delenv("NAVER_NEWS_CLIENT_ID", raising=False)
    monkeypatch.delenv("NAVER_NEWS_CLIENT_SECRET", raising=False)

    with pytest.raises(ProviderCredentialError) as error:
        collect_naver_news(max_per_query=1, sleep_seconds=0, max_retries=0)

    message = str(error.value)
    assert "NAVER_NEWS_CLIENT_ID" in message
    assert "NAVER_NEWS_CLIENT_SECRET" in message
    assert "=" not in message


def test_open_dart_collection_requires_credentials_before_network(monkeypatch) -> None:
    monkeypatch.delenv("OPEN_DART_API_KEY", raising=False)

    with pytest.raises(ProviderCredentialError) as error:
        collect_open_dart(days=1, pages=1, sleep_seconds=0)

    message = str(error.value)
    assert "OPEN_DART_API_KEY" in message
    assert "=" not in message
