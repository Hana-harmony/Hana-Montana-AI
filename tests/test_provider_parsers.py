import pytest

from hannah_montana_ai.api.routes import get_analyzer
from hannah_montana_ai.domain.schemas import TaxRefundStatusRequest
from hannah_montana_ai.services.feature_contracts import (
    IntelligenceEventService,
    StockOrderStatusService,
    TaxRefundStatusService,
)
from hannah_montana_ai.services.provider_parsers import (
    ProviderParseError,
    build_intelligence_event_request,
    build_omnilens_websocket_event,
    build_stock_order_status_request,
    parse_kis_master_csv,
    parse_kis_realtime_packet,
    parse_krx_foreign_holding_row,
    parse_naver_news_row,
    parse_opendart_disclosure_row,
    parse_tax_document_rows,
    parse_tax_transaction_rows,
)


def test_provider_parsers_build_stock_order_model_input_from_kis_and_krx_rows() -> None:
    master = parse_kis_master_csv(
        "종목코드,종목명,영문명,시장구분,발행주식수,전일종가,상한가,하한가\n"
        "005930,삼성전자,Samsung Electronics,KOSPI,\"100,000,000\",65000,84500,45500\n"
    )[0]
    quote = parse_kis_realtime_packet("005930|84500|Y|N|단일가")
    foreign_holding = parse_krx_foreign_holding_row(
        {
            "종목코드": "005930",
            "외국인보유수량": "39,900,000",
            "외국인보유율": "39.90",
            "한도소진율": "99.75",
            "외국인한도수량": "40,000,000",
        }
    )

    request = build_stock_order_status_request(
        master=master,
        quote=quote,
        foreign_holding=foreign_holding,
        foreign_limit_rate=40.0,
        intraday_foreign_net_buy_quantity=50_000,
        local_currency="HKD",
        local_fx_rate=0.0058,
    )
    response = StockOrderStatusService().build_response(request)

    assert response.stock_code == "005930"
    assert response.foreign_ownership_rate == 39.9
    assert response.foreign_limit_exhaustion_rate == 99.75
    assert response.fx_predicted_rate_min == 39.91
    assert response.fx_predicted_rate_max == 39.99
    assert response.vi_activation_status == "Y"
    assert response.price_limit_status == "UPPER"
    assert response.immediate_execution_available is False


def test_provider_parser_rejects_mismatched_stock_codes() -> None:
    master = parse_kis_master_csv(
        "stock_code,stock_name,stock_name_en,market,issued_shares,previous_close_price,upper_limit_price,lower_limit_price\n"
        "005930,삼성전자,Samsung Electronics,KOSPI,100000000,65000,84500,45500\n"
    )[0]
    quote = parse_kis_realtime_packet(
        {
            "stock_code": "000660",
            "current_price": "120000",
            "dynamic_vi_activated": "N",
            "static_vi_activated": "N",
            "trading_session_status": "REGULAR",
        }
    )
    foreign_holding = parse_krx_foreign_holding_row(
        {
            "stock_code": "005930",
            "foreign_owned_quantity": "39900000",
            "foreign_ownership_rate": "39.90",
            "foreign_limit_exhaustion_rate": "99.75",
        }
    )

    with pytest.raises(ProviderParseError):
        build_stock_order_status_request(
            master=master,
            quote=quote,
            foreign_holding=foreign_holding,
        )


def test_tax_provider_parsers_build_tax_refund_model_inputs() -> None:
    documents = parse_tax_document_rows(
        [
            {
                "서류유형": "RESIDENCE_CERTIFICATE",
                "파일명": "cert_res_2024.pdf",
                "검증상태": "완료",
                "OCR신뢰도": "0.94",
                "위변조위험도": "0.03",
            },
            {
                "서류유형": "TREATY_APPLICATION",
                "파일명": "treaty_application.jpg",
                "검증상태": "VERIFIED",
                "OCR신뢰도": "0.91",
                "위변조위험도": "0.04",
            },
        ]
    )
    transactions = parse_tax_transaction_rows(
        [
            {
                "거래유형": "DIVIDEND",
                "총배당금": "1,000,000",
                "기납부원천세": "220,000",
                "장내거래여부": "Y",
                "지분율": "0.2",
            },
            {
                "거래유형": "SELL",
                "총매도지급액": "3,000,000",
                "양도차익": "1,136,364",
                "기납부원천세": "220,000",
                "장내거래여부": "Y",
                "지분율": "0.2",
            },
        ]
    )

    response = TaxRefundStatusService().build_response(
        TaxRefundStatusRequest(
            investor_id="HK_USER_1234",
            tax_residency_country="HK",
            tax_year="2023-2024",
            documents=documents,
            transactions=transactions,
            instant_payout_requested=True,
            instant_payout_fee_rate=3.0,
        )
    )

    assert response.tax_case_type == "CASE_01"
    assert response.eligible_refund_amount == 320_000
    assert response.instant_payout_amount == 310_400


def test_naver_news_provider_parser_builds_intelligence_event_packet() -> None:
    get_analyzer.cache_clear()
    record = parse_naver_news_row(
        {
            "title": "삼성전자 2분기 영업이익 증가",
            "description": "반도체 수요 회복으로 실적 개선 기대가 커졌다.",
            "originallink": "https://news.example.com/article/005930-earnings",
            "pubDate": "Wed, 17 Jun 2026 09:00:00 +0900",
            "provider": "naver-news",
            "stock_code": "005930",
            "stock_name": "삼성전자",
            "stock_name_en": "Samsung Electronics",
            "aliases": "삼전",
        }
    )

    request = build_intelligence_event_request(record)
    response = IntelligenceEventService(get_analyzer()).build_response(request)
    websocket_event = build_omnilens_websocket_event(
        response,
        partner_id="HK_BROKER",
    )

    assert record.source_type == "NEWS"
    assert len(record.duplicate_key) == 64
    assert request.stock_universe[0].stock_code == "005930"
    assert response.stock_code == "005930"
    assert "Samsung Electronics" in response.translated_title
    assert "EARNINGS" in response.event_tags
    assert websocket_event["channel"] == "stock:005930"
    assert websocket_event["partner_id"] == "HK_BROKER"
    assert websocket_event["alert_id"] == response.alert_id
    assert websocket_event["data_source"] == "Naver/OpenDART/NLP/PapagoDeepLAdapter"


def test_opendart_provider_parser_builds_disclosure_event_request() -> None:
    get_analyzer.cache_clear()
    record = parse_opendart_disclosure_row(
        {
            "rcept_no": "20260617000001",
            "corp_name": "한화시스템",
            "stock_code": "272210",
            "stock_name": "한화시스템",
            "stock_name_en": "Hanwha Systems",
            "report_nm": "단일판매ㆍ공급계약체결",
            "rcept_dt": "20260617",
        }
    )

    request = build_intelligence_event_request(record)
    response = IntelligenceEventService(get_analyzer()).build_response(request)

    assert record.source_type == "DISCLOSURE"
    assert record.provider_event_id == "20260617000001"
    assert record.original_url.endswith("rcpNo=20260617000001")
    assert request.provider == "opendart"
    assert response.news_disclosure_type == "DISCLOSURE"
    assert response.stock_code == "272210"
    assert "CONTRACT" in response.event_tags


def test_intelligence_provider_parser_rejects_invalid_url() -> None:
    with pytest.raises(ProviderParseError):
        parse_naver_news_row(
            {
                "title": "삼성전자 영업이익 증가",
                "description": "실적 개선 기대",
                "originallink": "javascript:alert(1)",
                "stock_code": "005930",
                "stock_name": "삼성전자",
            }
        )
