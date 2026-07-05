import json
from pathlib import Path

from fastapi.testclient import TestClient

from hannah_montana_ai.core.config import Settings
from hannah_montana_ai.domain.schemas import (
    FinancialTermEvidence,
    KoreanFinancialTermExplainRequest,
)
from hannah_montana_ai.main import app
from hannah_montana_ai.services.korean_financial_terms import (
    GeneratedTermExplanation,
    KoreanFinancialTermExplanationService,
    LocalQwenTermExplanationProvider,
    MlxQwenTermExplanationClient,
    build_term_provider_from_settings,
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


def test_financial_term_explain_api_ignores_generic_english_display_term() -> None:
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
    assert payload["normalized_term"] == "retail investors"
    assert payload["english_term"] == ""
    assert payload["source"] == "INTERNAL_CONTEXT_RAG"
    assert payload["display_mode"] == "TEXT_ONLY"
    assert payload["quality_flags"] == ["NON_KOREAN_GLOSSARY_TERM_IGNORED"]
    assert "not a Korean local-market glossary term" in payload["explanation"]


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
            term="양자컴퓨팅밈주",
            title="양자컴퓨팅밈주가 급등했다",
            context="양자컴퓨팅밈주라는 표현이 온라인 수급과 함께 언급됐다.",
        )
    )

    assert response.source == "UNVERIFIED_CONTEXT"
    assert response.display_mode == "REVIEW_REQUIRED"
    assert response.cacheable is False
    assert "definitive" in response.explanation


def test_common_theme_stock_terms_are_dictionary_backed_without_web_provider() -> None:
    service = KoreanFinancialTermExplanationService(
        seed_path=Path("data/reference/korean_financial_terms_seed.json"),
        model_version="test-term-rag",
    )

    response = service.explain(
        KoreanFinancialTermExplainRequest(
            term="초전도체주",
            title="초전도체주 테마성 급등",
            context="초전도체주가 테마성 수급으로 급등했다는 보도가 나왔다.",
            allow_web_search=False,
        )
    )

    assert response.source == "DICTIONARY"
    assert response.display_mode == "EXPLANATION"
    assert response.cacheable is True
    assert response.english_term == "superconductor-themed stock"
    assert "does not prove" in response.explanation


def test_samjeon_nix_is_dictionary_backed_korean_market_slang() -> None:
    service = KoreanFinancialTermExplanationService(
        seed_path=Path("data/reference/korean_financial_terms_seed.json"),
        model_version="test-term-rag",
    )

    response = service.explain(
        KoreanFinancialTermExplainRequest(
            term="Samjeon Nix",
            title='"Samjeon Nix" returns are enviable',
            context="The translated article uses Samjeon Nix for Samsung Electronics and SK hynix.",
        )
    )

    assert response.source == "DICTIONARY"
    assert response.normalized_term == "삼전닉스"
    assert response.english_term == "Samsung Electronics and SK hynix basket"
    assert "Samsung Electronics and SK hynix" in response.explanation
    assert "literal translation" in response.explanation


def test_local_qwen_term_provider_promotes_unknown_korean_term() -> None:
    service = KoreanFinancialTermExplanationService(
        seed_path=Path("data/reference/korean_financial_terms_seed.json"),
        model_version="test-term-qwen3",
        provider=LocalQwenTermExplanationProvider(
            model_name="Qwen3-0.6B-test",
            max_tokens=320,
            client=_FakeTermGenerationClient(
                {
                    "english_term": "aerospace-themed stock",
                    "category": "theme_stock",
                    "definition": (
                        '"우주항공주" means a Korean stock grouped under the aerospace '
                        "investment theme."
                    ),
                    "explanation": (
                        '"우주항공주" is used when articles link stocks to satellites, '
                        "launch systems, defense aerospace, or space policy. In this article, "
                        "the term is grounded by references to policy expectations and satellite "
                        "investment."
                    ),
                    "example": "우주항공주 강세 means aerospace-themed stocks rallied.",
                    "confidence_score": 0.86,
                }
            ),
        ),
    )

    response = service.explain(
        KoreanFinancialTermExplainRequest(
            term="우주항공주",
            title="우주항공주 강세",
            context="우주항공주가 정부 정책 기대감과 위성 투자 확대로 강세를 보였다.",
        )
    )

    assert response.source == "LOCAL_OPEN_SOURCE_LLM_RAG"
    assert response.display_mode == "EXPLANATION"
    assert response.cacheable is True
    assert response.english_term == "aerospace-themed stock"
    assert "LOCAL_QWEN_RAG" in response.quality_flags


def test_local_qwen_term_provider_rejects_generic_english_finance_word() -> None:
    provider = LocalQwenTermExplanationProvider(
        model_name="Qwen3-0.6B-test",
        max_tokens=320,
        client=_FakeTermGenerationClient(
            {
                "english_term": "earnings",
                "category": "metric",
                "definition": '"earnings" means company profit.',
                "explanation": (
                    '"earnings" is a generic finance word in English. It should not be '
                    "treated as a Korean local-market glossary term."
                ),
                "example": "earnings improved means profit improved.",
                "confidence_score": 0.9,
            }
        ),
    )

    result = provider.generate(
        KoreanFinancialTermExplainRequest(
            term="earnings",
            title="Samsung earnings improve",
            context="earnings improved after chip demand recovered.",
        ),
        (
            FinancialTermEvidence(
                title="Samsung earnings improve",
                snippet="earnings improved after chip demand recovered.",
                source_type="article_context",
            ),
        ),
    )

    assert result is None


def test_generic_english_finance_words_are_text_only_not_glossary_explanations() -> None:
    service = KoreanFinancialTermExplanationService(
        seed_path=Path("data/reference/korean_financial_terms_seed.json"),
        model_version="test-term-rag",
    )

    for term in ("earnings", "Foreign investors"):
        response = service.explain(
            KoreanFinancialTermExplainRequest(
                term=term,
                title=f"{term} mentioned in a translated article",
                context=f"{term} was present in the translated article text.",
            )
        )

        assert response.display_mode == "TEXT_ONLY"
        assert response.source == "INTERNAL_CONTEXT_RAG"
        assert response.english_term == ""
        assert response.quality_flags == ["NON_KOREAN_GLOSSARY_TERM_IGNORED"]


def test_korean_financial_term_local_llm_settings_use_direct_qwen3_mlx_client() -> None:
    provider = build_term_provider_from_settings(
        Settings(
            korean_financial_term_generation_mode="local_llm",
            korean_financial_term_llm_endpoint="",
            korean_financial_term_mlx_model="mlx-community/Qwen3-0.6B-4bit",
            korean_financial_term_mlx_adapter_path=Path(
                "src/hannah_montana_ai/model_store/korean_term_qwen3_explainer_lora"
            ),
        )
    )

    assert isinstance(provider, LocalQwenTermExplanationProvider)
    assert isinstance(provider._client, MlxQwenTermExplanationClient)


def test_web_search_provider_can_promote_unknown_term_to_cacheable_explanation() -> None:
    service = KoreanFinancialTermExplanationService(
        seed_path=Path("data/reference/korean_financial_terms_seed.json"),
        model_version="test-term-rag",
        provider=_FakeTermProvider(),
    )

    response = service.explain(
        KoreanFinancialTermExplainRequest(
            term="우주항공주",
            title="우주항공주 강세",
            context="우주항공주가 정부 정책 기대감과 위성 투자 확대로 강세를 보였다.",
            allow_web_search=True,
        )
    )

    assert response.source == "OPENAI_WEB_SEARCH_RAG"
    assert response.display_mode == "EXPLANATION"
    assert response.cacheable is True
    assert response.english_term == "aerospace-themed stock"
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
            english_term="aerospace-themed stock",
            category="theme_stock",
            definition="A Korean stock grouped by investors under the aerospace investment theme.",
            explanation=(
                '"우주항공주" means an aerospace-themed stock in Korean market news. '
                "It is usually used for companies expected to benefit from satellites, launch "
                "systems, defense aerospace, or related policy themes."
            ),
            example="우주항공주 강세 means aerospace-themed stocks rallied.",
            confidence_score=0.86,
            evidence=(
                *context_evidence,
                FinancialTermEvidence(
                    title="Aerospace theme explanation",
                    snippet="Market reports use 우주항공주 for aerospace-themed stocks.",
                    url="https://example.com/aerospace-theme",
                    source_type="web_search",
                ),
            ),
            source="OPENAI_WEB_SEARCH_RAG",
        )


class _FakeTermGenerationClient:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def generate(self, messages: list[dict[str, str]], max_tokens: int) -> str:
        assert messages
        assert max_tokens > 0
        return json.dumps(self._payload, ensure_ascii=False)
