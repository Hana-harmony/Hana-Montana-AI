from hannah_montana_ai.domain.schemas import AlertAnalysisRequest
from hannah_montana_ai.services.analyzer import AlertAnalyzer


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


def test_duplicate_key_ignores_spacing_case_and_punctuation() -> None:
    analyzer = AlertAnalyzer()
    first = analyzer._duplicate_key("NEWS", "Samsung Elec, 실적 개선!", "005930")
    second = analyzer._duplicate_key("NEWS", "samsung-elec 실적   개선", "005930")

    assert first == second
