from pathlib import Path

from hannah_montana_ai.domain.schemas import AlertAnalysisRequest
from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.training.stock_universe import load_stock_universe


def test_stock_mapping_uses_aliases_and_preserves_text_order() -> None:
    request = AlertAnalysisRequest.model_validate(
        {
            "source_type": "NEWS",
            "title": "SK hynix와 Samsung Elec 반도체 업황 개선",
            "original_url": "https://example.com/news/alias",
            "stock_universe": [
                {
                    "stock_code": "005930",
                    "stock_name": "삼성전자",
                    "stock_name_en": "Samsung Electronics",
                    "aliases": ["Samsung Elec"],
                },
                {
                    "stock_code": "000660",
                    "stock_name": "SK하이닉스",
                    "stock_name_en": "SK hynix",
                    "aliases": ["하이닉스"],
                },
            ],
        }
    )

    response = AlertAnalyzer().analyze(request)

    assert response.stock_code == "000660"
    assert response.related_stocks == ["000660", "005930"]


def test_internal_stock_universe_matches_every_stock_code() -> None:
    analyzer = AlertAnalyzer()
    entries = load_stock_universe(Path("data/reference/korea_stock_universe.csv"))

    misses = [
        stock.stock_code
        for stock in entries
        if analyzer._match_primary_stock(
            f"{stock.stock_code} 주요사항보고서",
            analyzer._stock_universe_for_request([]),
        )
        is None
    ]

    assert len(entries) >= 3_000
    assert misses == []


def test_request_stock_candidates_take_primary_mapping_priority() -> None:
    request = AlertAnalysisRequest.model_validate(
        {
            "source_type": "NEWS",
            "title": "삼성전자 이슈 이후 위험기업 공급계약 체결",
            "original_url": "https://example.com/news/request-priority",
            "stock_universe": [
                {
                    "stock_code": "123456",
                    "stock_name": "위험기업",
                    "stock_name_en": "Risk Company",
                }
            ],
        }
    )

    response = AlertAnalyzer().analyze(request)

    assert response.stock_code == "123456"
    assert response.related_stocks[0] == "005930"
    assert "123456" in response.related_stocks


def test_duplicate_key_ignores_spacing_case_and_punctuation() -> None:
    analyzer = AlertAnalyzer()
    first = analyzer._duplicate_key("NEWS", "Samsung Elec, 실적 개선!", "005930")
    second = analyzer._duplicate_key("NEWS", "samsung-elec 실적   개선", "005930")

    assert first == second


def test_duplicate_key_ignores_common_news_label_and_tail_noise() -> None:
    analyzer = AlertAnalyzer()
    first = analyzer._duplicate_key(
        "NEWS",
        "[속보] 삼성전자, 2분기 잠정실적 개선(종합) - 연합뉴스",
        "005930",
    )
    second = analyzer._duplicate_key("news", "삼성전자 2분기 잠정 실적 개선", "005930")

    assert first == second


def test_duplicate_key_keeps_source_type_and_stock_boundaries() -> None:
    analyzer = AlertAnalyzer()
    news = analyzer._duplicate_key("NEWS", "삼성전자 2분기 잠정실적 개선", "005930")
    disclosure = analyzer._duplicate_key("DISCLOSURE", "삼성전자 2분기 잠정실적 개선", "005930")
    different_stock = analyzer._duplicate_key("NEWS", "삼성전자 2분기 잠정실적 개선", "000660")

    assert news != disclosure
    assert news != different_stock
