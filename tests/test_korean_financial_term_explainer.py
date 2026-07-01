from pathlib import Path

from fastapi.testclient import TestClient

from hannah_montana_ai.domain.schemas import (
    FinancialTermEvidence,
    KoreanFinancialTermExplainRequest,
)
from hannah_montana_ai.main import app
from hannah_montana_ai.services.korean_financial_terms import (
    GeneratedTermExplanation,
    KoreanFinancialTermExplanationService,
)


def test_financial_term_explain_api_returns_dictionary_hit_for_retail_slang() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/korean-financial-terms/explain",
        json={
            "term": "개미",
            "title": "개미, 삼성전자 순매수 확대",
            "context": "개미가 삼성전자를 순매수했다는 보도가 나왔다.",
            "article_id": "news-1",
            "article_url": "https://example.com/news/1",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["normalized_term"] == "개미"
    assert payload["english_term"] == "retail investor"
    assert payload["source"] == "DICTIONARY"
    assert payload["display_mode"] == "EXPLANATION"
    assert payload["cacheable"] is True
    assert payload["confidence_level"] == "HIGH"
    assert "retail investors" in payload["explanation"]
    assert payload["evidence"]


def test_financial_term_explain_api_maps_alias_to_seed_term() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/korean-financial-terms/explain",
        json={
            "term": "공모가 4배",
            "title": "새내기주가 공모가 4배에 도전",
            "context": "시장에서는 공모가 4배 상승을 따따블로 부른다.",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["normalized_term"] == "따따블"
    assert payload["english_term"] == "IPO quadruple jump"
    assert payload["source"] == "DICTIONARY"


def test_financial_term_explain_api_maps_translated_english_term_to_seed_term() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/korean-financial-terms/explain",
        json={
            "term": "retail investors",
            "title": "Samsung retail investors digest disclosure update",
            "context": (
                "Foreign investors often see retail investors and bellwether stock "
                "in translated Korean market news."
            ),
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["term"] == "retail investors"
    assert payload["normalized_term"] == "개미"
    assert payload["english_term"] == "retail investor"
    assert payload["source"] == "DICTIONARY"
    assert payload["display_mode"] == "EXPLANATION"
    assert 'The term "retail investors" refers to' in payload["explanation"]
    assert "개미" not in payload["explanation"]
    assert "개미" not in payload["example"]


def test_financial_term_explain_api_maps_literal_ant_translation_to_seed_term() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/korean-financial-terms/explain",
        json={
            "term": "Ants",
            "title": "Ants net bought Samsung Electronics",
            "context": (
                "In translated Korean market news, Ants can appear as a literal "
                "translation of a local investor slang term."
            ),
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["term"] == "Ants"
    assert payload["normalized_term"] == "개미"
    assert payload["english_term"] == "retail investor"
    assert payload["source"] == "DICTIONARY"
    assert 'The term "Ants" refers to' in payload["explanation"]
    assert "개미" not in payload["explanation"]


def test_unknown_financial_term_requires_review_without_web_provider() -> None:
    service = KoreanFinancialTermExplanationService(
        seed_path=Path("data/reference/korean_financial_terms_seed.json"),
        model_version="test-term-rag",
    )

    response = service.explain(
        KoreanFinancialTermExplainRequest(
            term="초전도체주",
            title="초전도체주가 급등했다",
            context="초전도체주가 테마성 수급으로 급등했다는 보도가 나왔다.",
        )
    )

    assert response.source == "UNVERIFIED_CONTEXT"
    assert response.display_mode == "REVIEW_REQUIRED"
    assert response.cacheable is False
    assert "definitive" in response.explanation


def test_web_search_provider_can_promote_unknown_term_to_cacheable_explanation() -> None:
    service = KoreanFinancialTermExplanationService(
        seed_path=Path("data/reference/korean_financial_terms_seed.json"),
        model_version="test-term-rag",
        provider=_FakeTermProvider(),
    )

    response = service.explain(
        KoreanFinancialTermExplainRequest(
            term="로봇주",
            title="로봇주 강세",
            context="로봇주가 정부 정책 기대감과 자동화 투자 확대로 강세를 보였다.",
            allow_web_search=True,
        )
    )

    assert response.source == "OPENAI_WEB_SEARCH_RAG"
    assert response.display_mode == "EXPLANATION"
    assert response.cacheable is True
    assert response.english_term == "robotics-themed stock"
    assert response.evidence[0].source_type == "article_context"
    assert response.evidence[1].source_type == "web_search"


def test_openapi_docs_expose_korean_financial_term_contract() -> None:
    client = TestClient(app)
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/v1/korean-financial-terms/explain" in response.json()["paths"]


class _FakeTermProvider:
    def generate(
        self,
        request: KoreanFinancialTermExplainRequest,
        context_evidence: tuple[FinancialTermEvidence, ...],
    ) -> GeneratedTermExplanation:
        return GeneratedTermExplanation(
            english_term="robotics-themed stock",
            category="theme_stock",
            definition="A Korean stock grouped by investors under the robotics investment theme.",
            explanation=(
                "\"로봇주\" means a robotics-themed stock in Korean market news. "
                "It is usually used for companies expected to benefit from automation, robotics, "
                "or related government and corporate investment themes."
            ),
            example="로봇주 강세 means robotics-themed stocks rallied.",
            confidence_score=0.86,
            evidence=(
                *context_evidence,
                FinancialTermEvidence(
                    title="Robotics theme explanation",
                    snippet="Market reports use 로봇주 for robotics-themed stocks.",
                    url="https://example.com/robot-theme",
                    source_type="web_search",
                ),
            ),
            source="OPENAI_WEB_SEARCH_RAG",
        )
