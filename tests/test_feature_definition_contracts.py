import re

from fastapi.testclient import TestClient

from hannah_montana_ai.api.routes import get_analyzer
from hannah_montana_ai.core.config import get_settings
from hannah_montana_ai.main import app


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
            "local_currency": "HKD",
            "local_fx_rate": 0.0058,
        },
    )

    assert response.status_code == 200
    payload = response.json()
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
    assert payload["local_current_price"] == 490.1
    assert payload["prediction_model_version"] == "foreign-ownership-boundary-v1"
    assert payload["trading_state_model_version"] == "krx-vi-price-limit-state-v1"
    assert payload["data_source"] == "KIS/KRX/PredictEngine"


def test_korean_stock_intelligence_event_contract_translates_summarizes_and_targets() -> None:
    get_settings.cache_clear()
    get_analyzer.cache_clear()
    client = TestClient(app)
    response = client.post(
        "/api/v1/intelligence/events",
        json={
            "source_type": "NEWS",
            "title": "삼성전자 2분기 영업이익 증가",
            "snippet": "반도체 수요 회복으로 실적 개선 기대가 커졌다.",
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
    payload = response.json()
    assert re.fullmatch(r"[0-9a-f]{64}", payload["duplicate_key"])
    assert payload["stock_code"] == "005930"
    assert payload["news_disclosure_type"] == "NEWS"
    assert payload["original_title"] == "삼성전자 2분기 영업이익 증가"
    assert "Samsung Electronics" in payload["translated_title"]
    assert "operating profit" in payload["translated_title"]
    assert payload["summary"]
    assert payload["translated_summary"]
    assert payload["sentiment"] == "POSITIVE"
    assert payload["importance"] in {"MEDIUM", "HIGH"}
    assert "EARNINGS" in payload["event_tags"]
    assert payload["event_tag"] in payload["event_tags"]
    assert payload["is_watchlist_target"] is True
    assert payload["translation_provider"] == "local-financial-glossary"
    assert payload["translation_model_version"] == "local-financial-glossary-v1"
    assert payload["data_source"] == "Naver/OpenDART/NLP/PapagoDeepLAdapter"


def test_tax_refund_status_contract_computes_case_01_advance_payment() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/tax/refund-status",
        json={
            "investor_id": "HK_USER_1234",
            "tax_residency_country": "HK",
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
    payload = response.json()
    assert payload["investor_id"] == "HK_USER_1234"
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
    assert payload["tax_model_version"] == "hk-treaty-refund-case-engine-v1"
    assert payload["document_model_version"] == "ocr-fraud-risk-gate-v1"
