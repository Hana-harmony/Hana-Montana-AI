from pathlib import Path

from fastapi.testclient import TestClient

from hannah_montana_ai.domain.schemas import KoreanFinancialTermExplainRequest
from hannah_montana_ai.main import app
from hannah_montana_ai.services.korean_financial_terms import (
    KoreanFinancialTermExplanationService,
    load_financial_term_entries,
    term_cache_key,
)

SEED_PATH = Path("data/reference/korean_financial_terms_seed.json")


def _service() -> KoreanFinancialTermExplanationService:
    return KoreanFinancialTermExplanationService(
        seed_path=SEED_PATH,
        model_version="test-dictionary-v3",
    )


def test_api_returns_canonical_ant_surface() -> None:
    response = TestClient(app).post(
        "/api/v1/korean-financial-terms/explain",
        json={
            "term": "개미",
            "title": "개미, 삼성전자 순매수 확대",
            "context": "개미가 삼성전자를 순매수했다.",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["normalized_term"] == "개미"
    assert payload["english_term"] == "Ant"
    assert payload["source"] == "DICTIONARY"
    assert payload["display_mode"] == "EXPLANATION"


def test_api_returns_canonical_daejangju_surface() -> None:
    response = _service().explain(KoreanFinancialTermExplainRequest(term="대장주"))

    assert response.english_term == "Daejangju"
    assert response.source == "DICTIONARY"


def test_localisms_use_romanization_and_direct_terms_use_translation() -> None:
    expected = {
        "따상": "Ttasang",
        "따따블": "Ttattable",
        "품절주": "Pumjeolju",
        "쩜상": "Jjeomsang",
        "작전주": "Jakjeonju",
        "물타기": "averaging down",
        "손절": "cutting losses",
    }

    for term, english_term in expected.items():
        response = _service().explain(KoreanFinancialTermExplainRequest(term=term))
        assert response.english_term == english_term
        assert response.source == "DICTIONARY"


def test_distinct_ant_localisms_do_not_collapse_into_generic_ant() -> None:
    donghak = _service().explain(KoreanFinancialTermExplainRequest(term="동학개미"))
    seohak = _service().explain(KoreanFinancialTermExplainRequest(term="서학개미"))

    assert donghak.english_term == "Donghak Ant"
    assert seohak.english_term == "Seohak Ant"


def test_expanded_dictionary_has_no_duplicate_normalized_terms() -> None:
    entries = load_financial_term_entries(SEED_PATH)
    normalized_terms = [entry.normalized_term for entry in entries]

    assert len(entries) >= 30
    assert len(normalized_terms) == len(set(normalized_terms))


def test_alias_maps_to_seed_entry() -> None:
    response = _service().explain(KoreanFinancialTermExplainRequest(term="공모가 4배"))

    assert response.normalized_term == "따따블"
    assert response.english_term == "Ttattable"


def test_explicit_english_localism_is_dictionary_backed() -> None:
    response = _service().explain(KoreanFinancialTermExplainRequest(term="Ants"))

    assert response.normalized_term == "개미"
    assert response.english_term == "Ant"
    assert 'The term "Ants" refers to' in response.explanation


def test_generic_english_term_is_not_treated_as_korean_glossary() -> None:
    response = _service().explain(KoreanFinancialTermExplainRequest(term="earnings"))

    assert response.display_mode == "TEXT_ONLY"
    assert response.english_term == ""
    assert response.quality_flags == ["NON_KOREAN_GLOSSARY_TERM_IGNORED"]


def test_unknown_korean_term_requires_review_without_llm() -> None:
    response = _service().explain(
        KoreanFinancialTermExplainRequest(
            term="양자컴퓨팅밈주",
            title="양자컴퓨팅밈주가 급등했다",
            context="온라인 수급과 함께 언급됐다.",
        )
    )

    assert response.source == "UNVERIFIED_CONTEXT"
    assert response.display_mode == "REVIEW_REQUIRED"
    assert response.cacheable is False


def test_cache_key_is_stable_and_context_sensitive() -> None:
    assert term_cache_key("개미", "en", "문맥") == term_cache_key("개미", "en", "문맥")
    assert term_cache_key("개미", "en", "문맥") != term_cache_key("개미", "en", "다른 문맥")


def test_openapi_exposes_financial_term_contract() -> None:
    response = TestClient(app).get("/openapi.json")

    assert response.status_code == 200
    assert "/api/v1/korean-financial-terms/explain" in response.json()["paths"]
