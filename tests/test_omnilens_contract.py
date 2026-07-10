import re
from base64 import b64encode
from typing import Any

from fastapi.testclient import TestClient

from hannah_montana_ai.api.routes import get_analyzer
from hannah_montana_ai.core.config import get_settings
from hannah_montana_ai.domain.schemas import (
    AlertAnalysisRequest,
    AlertAnalysisResponse,
    ForeignOwnershipTimeseriesPredictionRequest,
    ForeignOwnershipTimeseriesPredictionResponse,
    TaxDocumentVerificationRequest,
    TaxDocumentVerificationResponse,
)
from hannah_montana_ai.main import app

EXPECTED_REQUEST_FIELDS = {
    "source_type",
    "title",
    "snippet",
    "content",
    "image_urls",
    "canonical_url",
    "content_hash",
    "source_license_policy",
    "original_url",
    "stock_universe",
}

EXPECTED_STOCK_CANDIDATE_FIELDS = {
    "stock_code",
    "stock_name",
    "stock_name_en",
    "aliases",
}

EXPECTED_RESPONSE_FIELDS = {
    "stock_code",
    "stock_name",
    "source_type",
    "original_title",
    "translated_title",
    "summary",
    "summary_lines",
    "translated_summary",
    "content_availability",
    "original_content",
    "translated_content",
    "original_body",
    "translated_body",
    "body_source_type",
    "image_urls",
    "event_tags",
    "glossary_terms",
    "translation_quality_flags",
    "translation_provider",
    "translation_model_version",
    "translation_status",
    "sentiment",
    "importance",
    "related_stocks",
    "holder_target",
    "watchlist_target",
    "duplicate_key",
    "cluster_key",
    "model_version",
    "event_confidence",
    "sentiment_confidence",
    "importance_confidence",
    "stock_match_confidence",
}

EXPECTED_FOREIGN_OWNERSHIP_REQUEST_FIELDS = {
    "stock_code",
    "side",
    "quantity",
    "foreign_owned_quantity",
    "foreign_ownership_rate",
    "foreign_limit_quantity",
    "foreign_limit_exhaustion_rate",
    "base_date",
    "observed_intraday_volume",
    "history",
}

EXPECTED_FOREIGN_OWNERSHIP_HISTORY_FIELDS = {
    "base_date",
    "foreign_owned_quantity",
    "foreign_ownership_rate",
    "foreign_limit_quantity",
    "foreign_limit_exhaustion_rate",
}

EXPECTED_FOREIGN_OWNERSHIP_RESPONSE_FIELDS = {
    "stock_code",
    "predicted_foreign_owned_quantity",
    "min_foreign_owned_quantity",
    "max_foreign_owned_quantity",
    "predicted_foreign_net_acquired_quantity",
    "predicted_foreign_limit_quantity",
    "min_foreign_limit_quantity",
    "max_foreign_limit_quantity",
    "min_foreign_limit_exhaustion_rate",
    "base_foreign_limit_exhaustion_rate",
    "max_foreign_limit_exhaustion_rate",
    "order_impact_rate",
    "intraday_uncertainty_rate",
    "observed_intraday_volume",
    "trend_daily_change_rate",
    "history_observation_count",
    "history_window_days",
    "base_date",
    "calculated_at",
    "confidence_level",
    "confidence_score",
    "model_version",
    "source",
}


def test_omnilens_spring_client_schema_field_names_are_stable() -> None:
    request_schema = AlertAnalysisRequest.model_json_schema()
    response_schema = AlertAnalysisResponse.model_json_schema()
    stock_schema = request_schema["$defs"]["StockCandidate"]

    assert set(request_schema["properties"]) == EXPECTED_REQUEST_FIELDS
    assert set(stock_schema["properties"]) == EXPECTED_STOCK_CANDIDATE_FIELDS
    assert set(response_schema["properties"]) == EXPECTED_RESPONSE_FIELDS


def test_omnilens_foreign_ownership_prediction_schema_field_names_are_stable() -> None:
    request_schema = ForeignOwnershipTimeseriesPredictionRequest.model_json_schema()
    response_schema = ForeignOwnershipTimeseriesPredictionResponse.model_json_schema()
    history_schema = request_schema["$defs"]["ForeignOwnershipHistoryPoint"]

    assert set(request_schema["properties"]) == EXPECTED_FOREIGN_OWNERSHIP_REQUEST_FIELDS
    assert set(history_schema["properties"]) == EXPECTED_FOREIGN_OWNERSHIP_HISTORY_FIELDS
    assert set(response_schema["properties"]) == EXPECTED_FOREIGN_OWNERSHIP_RESPONSE_FIELDS


def test_omnilens_tax_document_verification_schema_accepts_ocr_payload() -> None:
    request_schema = TaxDocumentVerificationRequest.model_json_schema()
    response_schema = TaxDocumentVerificationResponse.model_json_schema()

    assert "document_content_base64" in request_schema["properties"]
    assert "content_type" in request_schema["properties"]
    assert "verification_status" in response_schema["properties"]


def test_omnilens_spring_client_payload_is_accepted_without_service_token() -> None:
    get_settings.cache_clear()
    get_analyzer.cache_clear()

    client = TestClient(app)
    response = client.post(
        "/api/v1/alerts/analyze",
        json={
            "source_type": "DISCLOSURE",
            "title": "삼성전자 공급계약 체결 공시",
            "snippet": "반도체 장비 공급계약 체결로 매출 확대가 기대된다.",
            "original_url": "https://example.com/dart/contract",
            "stock_universe": [
                {
                    "stock_code": "005930",
                    "stock_name": "삼성전자",
                    "stock_name_en": "Samsung Electronics",
                    "aliases": ["Samsung Elec"],
                }
            ],
        },
    )

    assert response.status_code == 200
    payload: dict[str, Any] = response.json()
    assert payload["success"] is True
    assert payload["code"] == "COMMON_000"
    data = payload["data"]
    assert set(data) == EXPECTED_RESPONSE_FIELDS
    assert data["stock_code"] == "005930"
    assert data["stock_name"] == "삼성전자"
    assert data["source_type"] == "DISCLOSURE"
    assert data["original_title"] == "삼성전자 공급계약 체결 공시"
    assert "CONTRACT" in data["event_tags"]
    assert data["related_stocks"] == ["005930"]
    assert isinstance(data["holder_target"], bool)
    assert isinstance(data["watchlist_target"], bool)
    assert 0.0 <= data["event_confidence"] <= 1.0
    assert 0.0 <= data["sentiment_confidence"] <= 1.0
    assert 0.0 <= data["importance_confidence"] <= 1.0
    assert data["stock_match_confidence"] == 1.0
    assert re.fullmatch(r"[0-9a-f]{64}", data["duplicate_key"])
    assert data["model_version"]


def test_tax_document_verification_runs_embedded_ocr_review_contract() -> None:
    client = TestClient(app)
    text = """
    United States of America
    Certification of U.S. Tax Residency
    US_USER_1234 987-65-4321
    Year 2026
    January 12, 2026
    """

    response = client.post(
        "/api/v1/tax/documents/verify",
        json={
            "document_type": "RESIDENCE_CERTIFICATE",
            "file_name": "residence.txt",
            "document_content_base64": b64encode(text.encode()).decode(),
            "content_type": "text/plain",
            "ocr_confidence": 0.91,
            "fraud_signal_score": 0.03,
            "expected_residency_country": "US",
        },
    )

    assert response.status_code == 200
    payload: dict[str, Any] = response.json()
    assert payload["success"] is True
    data = payload["data"]
    assert data["document_type"] == "RESIDENCE_CERTIFICATE"
    assert data["document_model_version"] == "hanah-tax-ocr-e2e-review-v2"
    assert data["extracted_fields"]["residency_country_code"] == "US"
    assert data["fraud_risk_score"] >= 0.03
