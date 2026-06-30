from fastapi.testclient import TestClient

from hannah_montana_ai.core.config import get_settings
from hannah_montana_ai.main import app


def test_foreign_ownership_prediction_uses_daily_timeseries() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/market/foreign-ownership/predict",
        json={
            "stock_code": "005930",
            "side": "BUY",
            "quantity": 1,
            "foreign_owned_quantity": 995,
            "foreign_ownership_rate": 49.75,
            "foreign_limit_quantity": 1000,
            "foreign_limit_exhaustion_rate": 99.5,
            "base_date": "2025-06-04",
            "observed_intraday_volume": 0,
            "history": [
                {
                    "base_date": "2025-05-31",
                    "foreign_owned_quantity": 980,
                    "foreign_ownership_rate": 49.0,
                    "foreign_limit_quantity": 1000,
                    "foreign_limit_exhaustion_rate": 98.0,
                },
                {
                    "base_date": "2025-06-01",
                    "foreign_owned_quantity": 985,
                    "foreign_ownership_rate": 49.25,
                    "foreign_limit_quantity": 1000,
                    "foreign_limit_exhaustion_rate": 98.5,
                },
                {
                    "base_date": "2025-06-02",
                    "foreign_owned_quantity": 989,
                    "foreign_ownership_rate": 49.45,
                    "foreign_limit_quantity": 1000,
                    "foreign_limit_exhaustion_rate": 98.9,
                },
                {
                    "base_date": "2025-06-03",
                    "foreign_owned_quantity": 992,
                    "foreign_ownership_rate": 49.6,
                    "foreign_limit_quantity": 1000,
                    "foreign_limit_exhaustion_rate": 99.2,
                },
                {
                    "base_date": "2025-06-04",
                    "foreign_owned_quantity": 995,
                    "foreign_ownership_rate": 49.75,
                    "foreign_limit_quantity": 1000,
                    "foreign_limit_exhaustion_rate": 99.5,
                },
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    data = payload["data"]
    assert data["stock_code"] == "005930"
    assert data["predicted_foreign_owned_quantity"] == 995
    assert data["predicted_foreign_net_acquired_quantity"] == 0
    assert data["predicted_foreign_limit_quantity"] == 1000
    assert data["base_foreign_limit_exhaustion_rate"] == 99.5
    assert data["history_observation_count"] == 5
    assert data["history_window_days"] == 4
    assert data["order_impact_rate"] == 0.0
    assert data["observed_intraday_volume"] == 0
    assert data["confidence_level"] == "AI_FOREIGN_OWNED_QUANTITY_PERSISTENCE_BASELINE"
    assert data["confidence_score"] == 0.58
    assert data["model_version"] == "hannah-foreign-owned-quantity-persistence-v1"
    assert data["source"] == "HANNAH_MONTANA_AI_FOREIGN_OWNED_QUANTITY_BASELINE"


def test_foreign_ownership_prediction_ignores_intraday_volume() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/market/foreign-ownership/predict",
        json={
            "stock_code": "005930",
            "side": "BUY",
            "quantity": 1,
            "foreign_owned_quantity": 995,
            "foreign_ownership_rate": 49.75,
            "foreign_limit_quantity": 1000,
            "foreign_limit_exhaustion_rate": 99.5,
            "base_date": "2025-06-04",
            "observed_intraday_volume": 1_000_000,
            "history": [],
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["observed_intraday_volume"] == 0
    assert data["confidence_level"] == "AI_FOREIGN_OWNED_QUANTITY_PERSISTENCE_BASELINE"
    assert data["confidence_score"] == 0.42
    assert "blocking" not in data
    assert "orderable" not in data


def test_foreign_ownership_retrain_requires_maintenance_token(monkeypatch) -> None:
    monkeypatch.setenv("HANNAH_AI_MAINTENANCE_TOKEN", "maintenance-secret")
    get_settings.cache_clear()
    client = TestClient(app)

    response = client.post(
        "/api/v1/market/foreign-ownership/model/retrain",
        json={
            "history": [
                {
                    "stock_code": "005930",
                    "base_date": f"2025-01-{day_index % 28 + 1:02d}",
                    "foreign_owned_quantity": 1_000_000 + day_index,
                    "foreign_limit_quantity": 2_000_000,
                }
                for day_index in range(120)
            ],
            "restricted_stock_codes": ["005930"],
        },
    )

    assert response.status_code == 401
    assert response.json()["code"] == "AUTH_001"
    get_settings.cache_clear()
