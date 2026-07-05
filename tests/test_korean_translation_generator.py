import json

from fastapi.testclient import TestClient

from hannah_montana_ai.api import routes
from hannah_montana_ai.core.config import Settings, get_settings
from hannah_montana_ai.domain.schemas import FinancialGlossaryTerm
from hannah_montana_ai.main import app
from hannah_montana_ai.services.korean_translation_generator import (
    KoreanTranslationContext,
    KoreanTranslationGenerator,
    MlxQwenKoreanTranslationClient,
    OpenAiCompatibleKoreanTranslationClient,
)


class FakeTranslationClient:
    def __init__(self, output: str) -> None:
        self.output = output
        self.calls: list[list[dict[str, str]]] = []

    def generate(self, messages: list[dict[str, str]], max_tokens: int) -> str:
        self.calls.append(messages)
        return self.output


def json_translation(value: str) -> str:
    return '{"translation":"' + value + '"}'


def test_korean_translation_local_llm_settings_use_direct_qwen3_mlx_client() -> None:
    settings = Settings(korean_translation_generation_mode="local_llm")

    generator = KoreanTranslationGenerator.from_settings(settings)

    assert generator._enabled is True
    assert isinstance(generator._client, MlxQwenKoreanTranslationClient)
    assert generator._model_name == "local-llm:mlx-community/Qwen3-0.6B-4bit"


def test_korean_translation_local_llm_settings_with_endpoint_use_openai_compatible_client() -> None:
    settings = Settings(
        korean_translation_generation_mode="local_llm",
        korean_translation_llm_endpoint="http://127.0.0.1:18081",
        korean_translation_llm_model="qwen3-translation-sidecar",
    )

    generator = KoreanTranslationGenerator.from_settings(settings)

    assert generator._enabled is True
    assert isinstance(generator._client, OpenAiCompatibleKoreanTranslationClient)
    assert generator._model_name == "local-llm:qwen3-translation-sidecar"


def test_korean_translation_qwen_output_returns_complete_english_translation() -> None:
    client = FakeTranslationClient(
        json_translation(
            "Samsung Electronics disclosed a KRW 14.58 trillion treasury-share "
            "cancellation. The company said the decision is intended to strengthen "
            "shareholder returns and capital efficiency."
        )
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text=(
                "삼성전자는 14조5800억원 규모 자사주 소각을 결정했다고 공시했다. "
                "회사는 주주환원 정책 강화와 자본 효율성 제고가 이번 결정의 목적이라고 설명했다."
            ),
            source_type="DISCLOSURE",
        )
    )

    assert result.status == "TRANSLATED"
    assert result.provider == "local-open-source-qwen3-translation"
    assert "Samsung Electronics disclosed" in result.translated_text
    assert result.quality_flags == []
    assert client.calls


def test_korean_translation_rejects_hangul_or_summary_output() -> None:
    client = FakeTranslationClient('{"translation":"삼성전자가 shareholder return을 강화했다."}')
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="삼성전자는 자사주 소각을 결정했다고 공시했다.",
            source_type="DISCLOSURE",
        )
    )

    assert result.translated_text == ""
    assert result.status == "SOURCE_LANGUAGE_FALLBACK"
    assert "HANGUL_REMAINS" in result.quality_flags


def test_korean_translation_preserves_localism_surface_for_glossary() -> None:
    client = FakeTranslationClient(
        '{"translation":"A retail investor net bought Samsung Electronics, SK Hynix '
        'shares, citing their sector leader stock status."}'
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="개미가 대장주 삼전닉스를 순매수했다.",
            glossary_terms=[
                FinancialGlossaryTerm(
                    source_term="개미",
                    normalized_term="개미",
                    english_term="retail investor",
                    category="market_slang",
                ),
                FinancialGlossaryTerm(
                    source_term="대장주",
                    normalized_term="대장주",
                    english_term="sector leader stock",
                    category="market_slang",
                ),
                FinancialGlossaryTerm(
                    source_term="삼전닉스",
                    normalized_term="삼전닉스",
                    english_term="Samsung Electronics and SK hynix basket",
                    category="market_slang",
                ),
            ],
        )
    )

    assert result.status == "TRANSLATED"
    assert (
        result.translated_text
        == "Ants net bought Samjeon Nix shares, citing their bellwether stock status."
    )
    assert result.quality_flags == []


def test_korean_translation_repairs_qwen_large_cap_mistranslation_for_bellwether() -> None:
    client = FakeTranslationClient(
        '{"translation":"Ants net bought Samjeon Nix, lifting attention on the '
        'semiconductor and large-cap stocks."}'
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="개미가 삼전닉스를 순매수하며 반도체 대장주에 대한 관심이 커졌다.",
            glossary_terms=[
                FinancialGlossaryTerm(
                    source_term="개미",
                    normalized_term="개미",
                    english_term="retail investor",
                    category="market_slang",
                ),
                FinancialGlossaryTerm(
                    source_term="삼전닉스",
                    normalized_term="삼전닉스",
                    english_term="Samsung Electronics and SK hynix basket",
                    category="market_slang",
                ),
                FinancialGlossaryTerm(
                    source_term="대장주",
                    normalized_term="대장주",
                    english_term="sector leader stock",
                    category="market_slang",
                ),
            ],
        )
    )

    assert result.status == "TRANSLATED"
    assert (
        result.translated_text
        == "Ants net bought Samjeon Nix, lifting attention on the semiconductor and "
        "bellwether stock."
    )
    assert result.quality_flags == []


def test_korean_translation_ignores_glossary_terms_absent_from_chunk() -> None:
    client = FakeTranslationClient('{"translation":"Ants, Samjeon Nix net bought."}')
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="개미, 삼전닉스 순매수",
            glossary_terms=[
                FinancialGlossaryTerm(
                    source_term="개미",
                    normalized_term="개미",
                    english_term="retail investors",
                    category="market_slang",
                ),
                FinancialGlossaryTerm(
                    source_term="대장주",
                    normalized_term="대장주",
                    english_term="bellwether stock",
                    category="market_slang",
                ),
                FinancialGlossaryTerm(
                    source_term="삼전닉스",
                    normalized_term="삼전닉스",
                    english_term="Samjeon Nix",
                    category="market_slang",
                ),
            ],
        )
    )

    payload = json.loads(client.calls[0][1]["content"])

    assert result.status == "TRANSLATED"
    assert result.translated_text == "Ants net bought Samjeon Nix."
    assert result.quality_flags == []
    assert [term["normalized_term"] for term in payload["glossary"]] == ["개미", "삼전닉스"]


def test_korean_translation_canonicalizes_preferred_localism_case() -> None:
    client = FakeTranslationClient('{"translation":"ants, samjeon nix net bought."}')
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="개미, 삼전닉스 순매수",
            glossary_terms=[
                FinancialGlossaryTerm(
                    source_term="개미",
                    normalized_term="개미",
                    english_term="retail investors",
                    category="market_slang",
                ),
                FinancialGlossaryTerm(
                    source_term="삼전닉스",
                    normalized_term="삼전닉스",
                    english_term="Samjeon Nix",
                    category="market_slang",
                ),
            ],
        )
    )

    assert result.status == "TRANSLATED"
    assert result.translated_text == "Ants net bought Samjeon Nix."
    assert result.quality_flags == []


def test_korean_translation_repairs_qwen_gaemi_romanization() -> None:
    client = FakeTranslationClient(
        "{\"translation\":\"Investors should check Samjeon Nix and Triangunxi's trading "
        'levels."}'
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="투자자는 개미, 삼전닉스 순매수가 수급에 미치는 영향을 확인해야 합니다.",
            glossary_terms=[
                FinancialGlossaryTerm(
                    source_term="개미",
                    normalized_term="개미",
                    english_term="retail investors",
                    category="market_slang",
                ),
                FinancialGlossaryTerm(
                    source_term="삼전닉스",
                    normalized_term="삼전닉스",
                    english_term="Samjeon Nix",
                    category="market_slang",
                ),
            ],
        )
    )

    assert result.status == "TRANSLATED"
    assert result.translated_text == "Investors should check Samjeon Nix and Ants' trading levels."
    assert result.quality_flags == []


def test_korean_translation_repairs_qwen_country_investor_mistranslation() -> None:
    client = FakeTranslationClient(
        '{"translation":"Samjeon Nix rose as country-investor net buying increased."}'
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="개미가 삼전닉스를 순매수했다.",
            glossary_terms=[
                FinancialGlossaryTerm(
                    source_term="개미",
                    normalized_term="개미",
                    english_term="retail investors",
                    category="market_slang",
                ),
                FinancialGlossaryTerm(
                    source_term="삼전닉스",
                    normalized_term="삼전닉스",
                    english_term="Samjeon Nix",
                    category="market_slang",
                ),
            ],
        )
    )

    assert result.status == "TRANSLATED"
    assert result.translated_text == "Ants net bought Samjeon Nix."
    assert result.quality_flags == []


def test_korean_translation_repairs_terse_localism_when_qwen_leaves_hangul() -> None:
    client = FakeTranslationClient('{"translation":"개미, 삼전닉스는 순매수를 공시했다."}')
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="개미, 삼전닉스 순매수",
            glossary_terms=[
                FinancialGlossaryTerm(
                    source_term="개미",
                    normalized_term="개미",
                    english_term="retail investors",
                    category="market_slang",
                ),
                FinancialGlossaryTerm(
                    source_term="삼전닉스",
                    normalized_term="삼전닉스",
                    english_term="Samjeon Nix",
                    category="market_slang",
                ),
            ],
        )
    )

    assert result.status == "TRANSLATED"
    assert result.translated_text == "Ants net bought Samjeon Nix."
    assert result.quality_flags == []


def test_korean_translation_rejects_prompt_leakage_and_missing_market_terms() -> None:
    client = FakeTranslationClient(
        json_translation(
            "Korean exporters net a higher price for US dollars. The company's "
            "assigned task is to return only compact JSON with key translation."
        )
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="‘쏠림과 변동’의 코스피… 1조 클럽은 줄고 VI는 역대 최대",
            source_type="NEWS",
        )
    )

    assert result.status == "SOURCE_LANGUAGE_FALLBACK"
    assert result.translated_text == ""
    assert "META_OR_REFUSAL_TEXT" in result.quality_flags
    assert "MARKET_TERM_MISSING:KOSPI" in result.quality_flags
    assert "SEMANTIC_MISMATCH:KOREAN_EXPORTERS" in result.quality_flags
    assert "SOURCE_ACRONYM_MISSING:VI" in result.quality_flags


def test_korean_translation_repairs_kosdaq_surface_when_qwen_outputs_kosx() -> None:
    client = FakeTranslationClient(
        json_translation(
            "KOSPI and KOSX fell as IPO stocks traded below their offering prices."
        )
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="코스피와 코스닥은 IPO 종목이 공모가를 밑돌면서 하락했다.",
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert result.translated_text == (
        "KOSPI and KOSDAQ fell as IPO stocks traded below their offering prices."
    )
    assert result.quality_flags == []


def test_korean_translation_rejects_repeated_long_phrase() -> None:
    repeated = (
        "Naver's KRW e-commerce platform broke even after a 76 percent drop "
        "from its KRW price."
    )
    client = FakeTranslationClient(json_translation(" ".join([repeated, repeated, repeated])))
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text=(
                "상반기 증시 랠리에도 기업공개 시장의 체감 온도는 낮았다. "
                "올해 신규 상장 기업 다수가 공모가를 밑돌았다. "
                "투자심리 회복이 지연되면서 새내기주 부진이 이어졌다."
            ),
            source_type="NEWS",
        )
    )

    assert result.status == "SOURCE_LANGUAGE_FALLBACK"
    assert result.translated_text == ""
    assert "REPEATED_TRANSLATION_PHRASE" in result.quality_flags


def test_korean_translation_rejects_unsupported_numeric_fact_and_uppercase_word_salad() -> None:
    client = FakeTranslationClient(
        json_translation(
            "SANILSE HONDA KOREAN NEXUS REACHIMENT increased revenue by 15% in Q1 2024."
        )
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="삼성전자 실적 개선",
            glossary_terms=[
                FinancialGlossaryTerm(
                    source_term="삼성전자",
                    normalized_term="삼성전자",
                    english_term="Samsung Electronics",
                    category="company",
                ),
            ],
        )
    )

    assert result.status == "SOURCE_LANGUAGE_FALLBACK"
    assert result.translated_text == ""
    assert "UNSUPPORTED_NUMERIC_FACT" in result.quality_flags
    assert "UPPERCASE_WORD_SALAD" in result.quality_flags


def test_korean_translation_api_uses_configured_generator(monkeypatch) -> None:
    client = FakeTranslationClient('{"translation":"Samsung Electronics improved earnings."}')
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    routes.get_korean_translation_service.cache_clear()
    monkeypatch.setattr(routes, "get_korean_translation_service", lambda: generator)
    api_client = TestClient(app)

    response = api_client.post(
        "/api/v1/translation/ko-en",
        json={
            "text": "삼성전자는 실적을 개선했다.",
            "source_type": "NEWS",
            "title": "삼성전자 실적 개선",
        },
    )

    assert response.status_code == 200
    payload = response.json()["data"]
    assert payload["provider"] == "local-open-source-qwen3-translation"
    assert payload["model_version"] == "test-qwen3-translation"
    assert payload["translated_text"] == "Samsung Electronics improved earnings."


def test_korean_translation_disabled_by_default_returns_explicit_fallback() -> None:
    get_settings.cache_clear()
    routes.get_korean_translation_service.cache_clear()

    result = KoreanTranslationGenerator.from_settings(Settings()).translate(
        KoreanTranslationContext(text="삼성전자는 실적을 개선했다.")
    )

    assert result.status == "SOURCE_LANGUAGE_FALLBACK"
    assert result.provider == "source-language-fallback"
    assert "LOCAL_TRANSLATION_DISABLED" in result.quality_flags
