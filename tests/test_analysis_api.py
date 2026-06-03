from fastapi.testclient import TestClient

from hannah_montana_ai.api.routes import get_analyzer
from hannah_montana_ai.core.config import get_settings
from hannah_montana_ai.main import app


def test_analyze_alert_returns_financial_labels() -> None:
    get_settings.cache_clear()
    get_analyzer.cache_clear()

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
    assert payload["stock_code"] == "005930"
    assert payload["sentiment"] == "POSITIVE"
    assert "EARNINGS" in payload["event_tags"]


def test_health_endpoint_is_available() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_alert_detects_critical_disclosure_risk() -> None:
    get_settings.cache_clear()
    get_analyzer.cache_clear()

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
    assert payload["stock_code"] == "123456"
    assert payload["sentiment"] == "NEGATIVE"
    assert payload["importance"] == "CRITICAL"
    assert payload["holder_target"] is True
