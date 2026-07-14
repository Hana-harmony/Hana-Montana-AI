import os
from http.client import RemoteDisconnected
from pathlib import Path

import pytest

from hannah_montana_ai.training import collector
from hannah_montana_ai.training.collector import (
    ProviderCredentialError,
    collect_naver_news,
    collect_open_dart,
    load_local_env,
)


def test_load_local_env_does_not_override_existing_secret(monkeypatch, tmp_path: Path) -> None:
    env_path = tmp_path / "secrets.local.env"
    env_path.write_text(
        "\n".join(
            [
                f"{'NAVER_NEWS_CLIENT_ID'}=from-file",
                f"{'NAVER_NEWS_CLIENT_SECRET'}=from-file-secret",
            ]
        )
        + "\n",
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


def test_open_dart_collection_follows_provider_pagination(monkeypatch) -> None:
    monkeypatch.setenv("OPEN_DART_API_KEY", "local-dart-key")
    monkeypatch.setattr(collector.time, "sleep", lambda _: None)
    requested_pages: list[int] = []

    def fake_json_request(request):
        page_no = int(request.full_url.split("page_no=")[1].split("&")[0])
        requested_pages.append(page_no)
        return {
            "total_page": 3,
            "list": [
                {
                    "rcept_no": f"2026061700000{page_no}",
                    "report_nm": f"단일판매ㆍ공급계약체결 {page_no}",
                    "corp_name": "한화시스템",
                    "rcept_dt": "20260617",
                }
            ],
        }

    monkeypatch.setattr(collector, "_json_request", fake_json_request)

    result = collect_open_dart(days=1, pages=None, sleep_seconds=0)

    assert requested_pages == [1, 2, 3]
    assert len(result.alerts) == 3
    assert result.status.successful_requests == 3


def test_open_dart_collection_honors_page_budget(monkeypatch) -> None:
    monkeypatch.setenv("OPEN_DART_API_KEY", "local-dart-key")
    monkeypatch.setattr(collector.time, "sleep", lambda _: None)
    requested_pages: list[int] = []

    def fake_json_request(request):
        page_no = int(request.full_url.split("page_no=")[1].split("&")[0])
        requested_pages.append(page_no)
        return {
            "total_page": 5,
            "list": [
                {
                    "rcept_no": f"2026061700000{page_no}",
                    "report_nm": "주요사항보고서",
                    "corp_name": "테스트",
                    "rcept_dt": "20260617",
                }
            ],
        }

    monkeypatch.setattr(collector, "_json_request", fake_json_request)

    collect_open_dart(days=1, pages=2, sleep_seconds=0)

    assert requested_pages == [1, 2]


def test_naver_collection_retries_timeout_without_losing_shard(monkeypatch) -> None:
    monkeypatch.setenv("NAVER_NEWS_CLIENT_ID", "local-client-id")
    monkeypatch.setenv("NAVER_NEWS_CLIENT_SECRET", "local-client-secret")
    monkeypatch.setattr(collector.time, "sleep", lambda _: None)
    call_count = 0

    def fake_json_request(_request):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise TimeoutError("read timed out")
        return {
            "items": [
                {
                    "title": "삼성전자 공급계약 기대",
                    "description": "반도체 수주 기대가 커졌다",
                    "originallink": "https://example.test/news/1",
                    "pubDate": "Fri, 05 Jun 2026 10:00:00 +0900",
                }
            ]
        }

    monkeypatch.setattr(collector, "_json_request", fake_json_request)

    result = collect_naver_news(
        max_per_query=1,
        sleep_seconds=0,
        max_retries=1,
        queries=("삼성전자",),
    )

    assert len(result.alerts) == 1
    assert result.status.attempted_requests == 2
    assert result.status.successful_requests == 1
    assert result.status.failed_requests == 1
    assert result.status.completed is True


def test_naver_collection_records_timeout_without_secret_or_url(monkeypatch) -> None:
    monkeypatch.setenv("NAVER_NEWS_CLIENT_ID", "local-client-id")
    monkeypatch.setenv("NAVER_NEWS_CLIENT_SECRET", "local-client-secret")
    monkeypatch.setattr(collector.time, "sleep", lambda _: None)

    def fake_json_request(_request):
        raise TimeoutError("read timed out")

    monkeypatch.setattr(collector, "_json_request", fake_json_request)

    result = collect_naver_news(
        max_per_query=1,
        sleep_seconds=0,
        max_retries=1,
        queries=("삼성전자",),
    )

    assert result.alerts == []
    assert result.status.attempted_requests == 2
    assert result.status.successful_requests == 0
    assert result.status.failed_requests == 2
    assert result.status.completed is False
    assert result.status.errors
    error_message = " ".join(result.status.errors)
    assert "TimeoutError" in error_message
    assert "local-client" not in error_message
    assert "openapi.naver.com" not in error_message


def test_naver_collection_retries_remote_disconnect(monkeypatch) -> None:
    monkeypatch.setenv("NAVER_NEWS_CLIENT_ID", "local-client-id")
    monkeypatch.setenv("NAVER_NEWS_CLIENT_SECRET", "local-client-secret")
    monkeypatch.setattr(collector.time, "sleep", lambda _: None)
    call_count = 0

    def fake_json_request(_request):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RemoteDisconnected("Remote end closed connection without response")
        return {
            "items": [
                {
                    "title": "하나금융지주 실적 기대",
                    "description": "은행주 투자 심리가 개선됐다",
                    "originallink": "https://example.test/news/2",
                    "pubDate": "Fri, 05 Jun 2026 10:00:00 +0900",
                }
            ]
        }

    monkeypatch.setattr(collector, "_json_request", fake_json_request)

    result = collect_naver_news(
        max_per_query=1,
        sleep_seconds=0,
        max_retries=1,
        queries=("하나금융지주",),
    )

    assert len(result.alerts) == 1
    assert result.status.attempted_requests == 2
    assert result.status.successful_requests == 1
    assert result.status.failed_requests == 1
    assert result.status.completed is True
