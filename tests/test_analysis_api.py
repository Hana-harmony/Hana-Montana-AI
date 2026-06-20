import json
import logging

from fastapi.testclient import TestClient

from hannah_montana_ai.api import routes
from hannah_montana_ai.api.routes import get_analyzer, get_audit_logger
from hannah_montana_ai.core.config import get_settings
from hannah_montana_ai.main import app
from hannah_montana_ai.services.model import ModelArtifactNotFoundError


def test_analyze_alert_returns_financial_labels() -> None:
    get_settings.cache_clear()
    get_analyzer.cache_clear()
    get_audit_logger.cache_clear()

    client = TestClient(app)
    response = client.post(
        "/api/v1/alerts/analyze",
        json={
            "source_type": "NEWS",
            "title": "삼성전자 2분기 영업이익 증가",
            "snippet": "반도체 수요 회복으로 실적 개선 기대가 커졌다.",
            "original_url": "https://example.com/news/1",
            "stock_universe": [
                {
                    "stock_code": "005930",
                    "stock_name": "삼성전자",
                    "stock_name_en": "Samsung Electronics",
                }
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["status"] == 200
    assert payload["code"] == "COMMON_000"
    assert payload["data"]["stock_code"] == "005930"
    assert payload["data"]["sentiment"] == "POSITIVE"
    assert "EARNINGS" in payload["data"]["event_tags"]
    assert 0.0 <= payload["data"]["event_confidence"] <= 1.0
    assert 0.0 <= payload["data"]["sentiment_confidence"] <= 1.0
    assert 0.0 <= payload["data"]["importance_confidence"] <= 1.0
    assert payload["data"]["stock_match_confidence"] == 1.0


def test_validation_error_returns_common_error_shape() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/alerts/analyze",
        json={
            "source_type": "NEWS",
            "title": "",
            "original_url": "not-a-url",
        },
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["success"] is False
    assert payload["status"] == 422
    assert payload["code"] == "COMMON_002"
    assert payload["errors"]


def test_analyze_alert_uses_internal_stock_universe_when_request_candidates_are_empty() -> None:
    get_settings.cache_clear()
    get_analyzer.cache_clear()
    get_audit_logger.cache_clear()

    client = TestClient(app)
    response = client.post(
        "/api/v1/alerts/analyze",
        json={
            "source_type": "NEWS",
            "title": "삼성전자 2분기 영업이익 증가",
            "snippet": "반도체 수요 회복으로 실적 개선 기대가 커졌다.",
            "original_url": "https://example.com/news/internal-stock-universe",
            "stock_universe": [],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["stock_code"] == "005930"
    assert payload["data"]["stock_name"] == "삼성전자"


def test_analyze_alert_writes_structured_audit_log_without_raw_content(caplog) -> None:
    get_settings.cache_clear()
    get_analyzer.cache_clear()
    get_audit_logger.cache_clear()
    caplog.set_level(logging.INFO, logger="hannah_montana_ai.audit.analysis")

    client = TestClient(app)
    response = client.post(
        "/api/v1/alerts/analyze",
        json={
            "source_type": "NEWS",
            "title": "삼성전자 2분기 영업이익 증가",
            "snippet": "반도체 수요 회복으로 실적 개선 기대가 커졌다.",
            "original_url": "https://example.com/news/audit-success",
            "stock_universe": [
                {
                    "stock_code": "005930",
                    "stock_name": "삼성전자",
                    "stock_name_en": "Samsung Electronics",
                }
            ],
        },
    )

    assert response.status_code == 200
    audit_payload = json.loads(caplog.records[-1].message)
    assert audit_payload["event"] == "analysis_audit"
    assert audit_payload["outcome"] == "success"
    assert audit_payload["model_version"] == response.json()["data"]["model_version"]
    assert audit_payload["stock_code"] == "005930"
    assert audit_payload["stock_match_confidence"] == 1.0
    assert "event_confidence" in audit_payload
    assert audit_payload["latency_ms"] >= 0
    assert "title_hash" in audit_payload
    assert "original_url_hash" in audit_payload
    assert "삼성전자 2분기 영업이익 증가" not in caplog.text
    assert "https://example.com/news/audit-success" not in caplog.text


def test_health_endpoint_is_available() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_docs_expose_analysis_contract() -> None:
    client = TestClient(app)
    response = client.get("/openapi.json")

    assert response.status_code == 200
    payload = response.json()
    assert payload["info"]["title"] == "Hannah-Montana-AI"
    assert "/api/v1/alerts/analyze" in payload["paths"]


def test_analyze_alert_detects_critical_disclosure_risk() -> None:
    get_settings.cache_clear()
    get_analyzer.cache_clear()
    get_audit_logger.cache_clear()

    client = TestClient(app)
    response = client.post(
        "/api/v1/alerts/analyze",
        json={
            "source_type": "DISCLOSURE",
            "title": "위험기업 감사의견 거절로 상장폐지 위험 발생",
            "original_url": "https://example.com/disclosure/1",
            "stock_universe": [
                {
                    "stock_code": "123456",
                    "stock_name": "위험기업",
                    "stock_name_en": "Risk Company",
                }
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["stock_code"] == "123456"
    assert payload["data"]["sentiment"] == "NEGATIVE"
    assert payload["data"]["importance"] == "CRITICAL"
    assert payload["data"]["holder_target"] is True


def test_analyze_alert_fails_closed_when_model_artifact_is_unavailable(monkeypatch, caplog) -> None:
    get_analyzer.cache_clear()
    get_audit_logger.cache_clear()
    caplog.set_level(logging.INFO, logger="hannah_montana_ai.audit.analysis")

    def unavailable_analyzer():
        raise ModelArtifactNotFoundError("missing artifact")

    monkeypatch.setattr(routes, "get_analyzer", unavailable_analyzer)

    client = TestClient(app)
    response = client.post(
        "/api/v1/alerts/analyze",
        json={
            "source_type": "NEWS",
            "title": "삼성전자 실적 개선",
            "original_url": "https://example.com/news/model-missing",
            "stock_universe": [],
        },
    )

    assert response.status_code == 503
    payload = response.json()
    assert payload["success"] is False
    assert payload["status"] == 503
    assert payload["code"] == "AI_001"
    assert payload["message"] == "ML model artifact is unavailable"
    audit_payload = json.loads(caplog.records[-1].message)
    assert audit_payload["event"] == "analysis_audit"
    assert audit_payload["outcome"] == "failure"
    assert audit_payload["failure_reason"] == "model_artifact_unavailable"
    assert audit_payload["latency_ms"] >= 0
