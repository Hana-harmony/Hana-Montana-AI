import re
from base64 import b64encode

from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from hanah_tax_ocr import pipeline as tax_ocr_pipeline
from hanah_tax_ocr.schemas import OCRPage, OCRResult, OCRWordBox
from hannah_montana_ai.api.routes import get_analyzer
from hannah_montana_ai.core.config import get_settings
from hannah_montana_ai.main import app
from hannah_montana_ai.services import feature_contracts


def test_korean_stock_order_status_contract_packs_foreign_limit_vi_and_price_limit() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/stocks/order-status",
        json={
            "stock_code": "005930",
            "stock_name": "삼성전자",
            "stock_name_en": "Samsung Electronics",
            "market": "KOSPI",
            "issued_shares": 100_000_000,
            "foreign_owned_quantity": 39_900_000,
            "foreign_limit_rate": 40.0,
            "intraday_foreign_net_buy_quantity": 50_000,
            "prediction_confidence_interval_percent": 0.04,
            "current_price": 84_500,
            "previous_close_price": 65_000,
            "upper_limit_price": 84_500,
            "lower_limit_price": 45_500,
            "dynamic_vi_activated": True,
            "trading_session_status": "SINGLE_PRICE",
            "local_currency": "USD",
            "local_fx_rate": 0.00072,
        },
    )

    assert response.status_code == 200
    envelope = response.json()
    assert envelope["success"] is True
    assert envelope["status"] == 200
    assert envelope["code"] == "COMMON_000"
    payload = envelope["data"]
    assert payload["stock_code"] == "005930"
    assert payload["foreign_ownership_rate"] == 39.9
    assert payload["foreign_limit_exhaustion_rate"] == 99.75
    assert payload["foreign_limit_remaining_quantity"] == 100_000
    assert payload["fx_predicted_rate_min"] == 39.91
    assert payload["fx_predicted_rate_max"] == 39.99
    assert payload["foreign_limit_usage_status"] == "CAUTION"
    assert payload["foreign_limit_warning"] is True
    assert payload["vi_activation_status"] == "Y"
    assert payload["vi_activation_reason"] == ["DYNAMIC_VI", "SINGLE_PRICE_SESSION"]
    assert payload["price_limit_status"] == "UPPER"
    assert payload["immediate_execution_available"] is False
    assert payload["buy_order_available"] is False
    assert payload["sell_order_available"] is False
    assert payload["order_availability_indicator"] == "LIMITED"
    assert payload["order_restriction_reasons"] == [
        "REALTIME_EXECUTION_LIMITED",
        "FOREIGN_LIMIT_CAUTION",
    ]
    assert payload["local_current_price"] == 60.84
    assert payload["prediction_model_version"] == "foreign-ownership-boundary-v1"
    assert payload["trading_state_model_version"] == "krx-vi-price-limit-state-v1"
    assert payload["data_source"] == "KIS/PredictEngine"


def test_intelligence_event_uses_qwen_summary_and_full_translation() -> None:
    get_settings.cache_clear()
    get_analyzer.cache_clear()
    client = TestClient(app)
    response = client.post(
        "/api/v1/intelligence/events",
        json={
            "source_type": "NEWS",
            "title": "삼성전자 2분기 영업이익 증가",
            "snippet": "반도체 수요 회복으로 실적 개선 기대가 커졌다.",
            "content": (
                "삼성전자는 반도체 수요 회복과 공급계약 증가로 영업이익 개선이 예상된다고 밝혔다."
            ),
            "original_url": "https://example.com/news/intelligence-1",
            "provider": "naver-news",
            "published_at": "2026-06-17T09:00:00+09:00",
            "target_language": "en",
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
    envelope = response.json()
    assert envelope["success"] is True
    assert envelope["status"] == 200
    assert envelope["code"] == "COMMON_000"
    payload = envelope["data"]
    assert re.fullmatch(r"[0-9a-f]{64}", payload["duplicate_key"])
    assert payload["stock_code"] == "005930"
    assert payload["news_disclosure_type"] == "NEWS"
    assert payload["original_title"] == "삼성전자 2분기 영업이익 증가"
    assert payload["translated_title"] == "Financial event update"
    assert payload["summary"]
    assert payload["translated_summary"] == payload["summary"]
    assert payload["original_content"] == payload["original_body"]
    assert "삼성전자는 반도체 수요 회복" in payload["original_body"]
    assert payload["translated_content"] == payload["translated_body"]
    assert payload["translated_body"] == "The complete source reports a financial event."
    assert payload["translation_status"] == "TRANSLATED"
    assert payload["content_availability"] == "FULL_TEXT"
    assert payload["body_source_type"] == "FULL_TEXT"
    assert payload["sentiment"] == "POSITIVE"
    assert payload["importance"] in {"MEDIUM", "HIGH"}
    assert "EARNINGS" in payload["event_tags"]
    assert payload["event_tag"] in payload["event_tags"]
    assert payload["is_watchlist_target"] is True
    assert payload["glossary_terms"] == [
        {
            "source_term": "삼성전자",
            "normalized_term": "삼성전자",
            "english_term": "Samsung Electronics",
            "category": "company",
            "description": "Verified English name for the matched listed company.",
        }
    ]
    assert "FINANCIAL_GLOSSARY_APPLIED" not in payload["translation_quality_flags"]
    assert "CONTENT_TRANSLATION_UNAVAILABLE" not in payload["translation_quality_flags"]
    assert payload["translation_provider"] == "local-open-source-qwen3-translation"
    assert 0.0 <= payload["event_confidence"] <= 1.0
    assert 0.0 <= payload["sentiment_confidence"] <= 1.0
    assert 0.0 <= payload["importance_confidence"] <= 1.0
    assert payload["stock_match_confidence"] == 1.0
    assert payload["data_source"] == "Naver/OpenDART/NLP/QwenTranslationAdapter"


def test_tax_refund_status_contract_computes_case_01_advance_payment() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/tax/refund-status",
        json={
            "investor_id": "US_USER_1234",
            "tax_residency_country": "US",
            "tax_year": "2023-2024",
            "instant_payout_requested": True,
            "instant_payout_fee_rate": 3.0,
            "documents": [
                {
                    "document_type": "RESIDENCE_CERTIFICATE",
                    "file_name": "cert_res_2024.pdf",
                    "verification_status": "VERIFIED",
                    "ocr_confidence": 0.94,
                    "fraud_risk_score": 0.03,
                },
                {
                    "document_type": "TREATY_APPLICATION",
                    "file_name": "treaty_application.jpg",
                    "verification_status": "VERIFIED",
                    "ocr_confidence": 0.91,
                    "fraud_risk_score": 0.04,
                },
            ],
            "transactions": [
                {
                    "transaction_type": "DIVIDEND",
                    "gross_dividend_amount": 1_000_000,
                    "withheld_tax": 220_000,
                    "listed_market_trade": True,
                    "ownership_rate_percent": 0.2,
                },
                {
                    "transaction_type": "SELL",
                    "sell_proceeds": 3_000_000,
                    "capital_gain": 1_136_364,
                    "withheld_tax": 220_000,
                    "listed_market_trade": True,
                    "ownership_rate_percent": 0.2,
                },
            ],
        },
    )

    assert response.status_code == 200
    envelope = response.json()
    assert envelope["success"] is True
    assert envelope["status"] == 200
    assert envelope["code"] == "COMMON_000"
    payload = envelope["data"]
    assert payload["investor_id"] == "US_USER_1234"
    assert payload["tax_year"] == "2023-2024"
    assert payload["tax_case_type"] == "CASE_01"
    assert payload["refund_workflow_status"] == "ELIGIBLE_FOR_INSTANT_PAYOUT"
    assert re.fullmatch(r"TX-[0-9A-F]{10}", payload["government_verification_ref"])
    assert payload["document_verification_status"] == "VERIFIED"
    assert payload["required_documents_completed"] is True
    assert payload["total_withheld_tax"] == 440_000
    assert payload["dividend_refund_amount"] == 70_000
    assert payload["capital_gains_refund_amount"] == 250_000
    assert payload["eligible_refund_amount"] == 320_000
    assert payload["national_tax_refund_amount"] == 288_000
    assert payload["local_tax_refund_amount"] == 32_000
    assert payload["instant_payout_fee_rate"] == 3.0
    assert payload["instant_payout_fee_amount"] == 9_600
    assert payload["instant_payout_amount"] == 310_400
    assert payload["compliance_sandbox_flag"] == "Y"
    assert payload["clawback_required_if_rejected"] is True
    assert payload["required_next_actions"] == ["CONFIRM_INSTANT_PAYOUT_TERMS"]
    assert "자동 환수" in payload["risk_disclosure_message"]
    assert payload["tax_model_version"] == "us-treaty-refund-case-engine-v1"
    assert payload["document_model_version"] == "ocr-fraud-risk-gate-v1"


def test_tax_document_verification_contract_gates_ocr_and_forgery_risk() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/tax/documents/verify",
        json={
            "document_type": "RESIDENCE_CERTIFICATE",
            "file_name": "cert_res_2024.pdf",
            "extracted_text": "Certificate of Resident Status United States",
            "ocr_confidence": 0.94,
            "fraud_signal_score": 0.03,
            "expected_residency_country": "US",
            "extracted_fields": {
                "taxpayer_name": "Maria L Chen",
                "tin": "987-65-4321",
                "tax_year": "2026",
                "issue_date": "January 12, 2026",
                "residency_country": "United States of America",
                "residency_country_code": "US",
            },
        },
    )

    assert response.status_code == 200
    envelope = response.json()
    assert envelope["success"] is True
    assert envelope["status"] == 200
    assert envelope["code"] == "COMMON_000"
    payload = envelope["data"]
    assert payload["document_type"] == "RESIDENCE_CERTIFICATE"
    assert payload["verification_status"] == "VERIFIED"
    assert payload["ocr_confidence"] == 0.94
    assert payload["fraud_risk_score"] == 0.03
    assert payload["risk_level"] == "LOW"
    assert payload["manual_review_required"] is False
    assert payload["extracted_fields"]["taxpayer_name"] == "Maria L Chen"
    assert payload["extracted_fields"]["residency_country_code"] == "US"
    assert payload["missing_required_fields"] == []
    assert payload["rejection_reasons"] == []
    assert payload["document_model_version"] == "ocr-fraud-risk-gate-v1"


def test_tax_document_verification_rejects_high_forgery_risk() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/tax/documents/verify",
        json={
            "document_type": "TREATY_APPLICATION",
            "file_name": "treaty_application.jpg",
            "extracted_text": "Treaty application",
            "ocr_confidence": 0.91,
            "fraud_signal_score": 0.81,
            "expected_residency_country": "US",
            "extracted_fields": {
                "first_name": "Maria",
                "last_name": "Chen",
                "address": "Los Angeles, CA",
                "tin": "987-65-4321",
                "residency_country": "United States of America",
                "residency_country_code": "US",
                "dividend_tax_rate": "15%",
                "signature_date": "2026-01-12",
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["verification_status"] == "REJECTED"
    assert payload["risk_level"] == "HIGH"
    assert payload["manual_review_required"] is True
    assert "HIGH_FORGERY_RISK" in payload["rejection_reasons"]


def test_tax_document_verification_runs_real_ocr_engine_for_image_payload(
    monkeypatch: MonkeyPatch,
) -> None:
    calls: list[str] = []
    check_calls: list[str] = []

    class FakeTesseractOCREngine:
        def __init__(self, **kwargs: object) -> None:
            pass

        def run(self, image_path: str) -> OCRResult:
            calls.append(str(image_path))
            return OCRResult(
                pages=[
                    OCRPage(
                        page_number=1,
                        raw_text=(
                            "Department of the Treasury Internal Revenue Service "
                            "Certification of U.S. Tax Residency "
                            "I certify that US_USER_1234 is a resident of the "
                            "United States of America for purposes of U.S. taxation. "
                            "Taxpayer: US USER 1234 TIN: 987-65-4321 "
                            "Tax Year: 2026 Date: January 15, 2026"
                        ),
                        words=[
                            OCRWordBox(
                                text="United States of America",
                                confidence=0.93,
                            )
                        ],
                    )
                ]
            )

        def run_regions(self, image_path: str, region_specs: object) -> dict[str, OCRPage]:
            return {}

    def fake_document_checks(*args: object, **kwargs: object) -> dict[str, bool]:
        check_calls.append(str(args[1]))
        return {"seal_present": True, "signature_present": True}

    monkeypatch.setattr(feature_contracts, "TesseractOCREngine", FakeTesseractOCREngine)
    monkeypatch.setattr(tax_ocr_pipeline, "compute_document_checks", fake_document_checks)

    client = TestClient(app)
    response = client.post(
        "/api/v1/tax/documents/verify",
        json={
            "document_type": "RESIDENCE_CERTIFICATE",
            "file_name": "residence.png",
            "document_content_base64": b64encode(b"fake-image-bytes").decode(),
            "content_type": "image/png",
            "ocr_confidence": 0.0,
            "fraud_signal_score": 0.03,
            "expected_residency_country": "US",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert calls
    assert check_calls
    assert payload["verification_status"] == "VERIFIED"
    assert payload["ocr_confidence"] == 0.93
    assert payload["document_model_version"] == "hanah-tax-ocr-e2e-review-v2"
    assert payload["manual_review_required"] is False
    assert payload["missing_required_fields"] == []
    assert payload["rejection_reasons"] == []
