import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from hannah_montana_ai.api import routes
from hannah_montana_ai.core.config import Settings, get_settings
from hannah_montana_ai.domain.schemas import FinancialGlossaryTerm
from hannah_montana_ai.main import app
from hannah_montana_ai.services.korean_translation_generator import (
    KoreanTranslationContext,
    KoreanTranslationGenerator,
    MlxQwenKoreanTranslationClient,
    NllbKoreanEnglishTranslationClient,
    OpenAiCompatibleKoreanTranslationClient,
)
from hannah_montana_ai.services.model import ModelArtifactNotFoundError


class FakeTranslationClient:
    def __init__(self, output: str) -> None:
        self.output = output
        self.calls: list[list[dict[str, str]]] = []

    def generate(self, messages: list[dict[str, str]], max_tokens: int) -> str:
        self.calls.append(messages)
        return self.output


class FakeNmtClient:
    model_name = "test-nllb"

    def __init__(self, output: str | list[str]) -> None:
        self.output = output
        self.calls: list[str] = []

    def translate(self, text: str, max_tokens: int) -> str:
        self.calls.append(text)
        if isinstance(self.output, list):
            index = min(len(self.calls) - 1, len(self.output) - 1)
            return self.output[index]
        return self.output


def json_translation(value: str) -> str:
    return '{"translation":"' + value + '"}'


def test_korean_translation_local_llm_settings_use_direct_qwen3_mlx_client() -> None:
    settings = Settings(korean_translation_generation_mode="local_llm")

    generator = KoreanTranslationGenerator.from_settings(settings)

    assert generator._enabled is True
    assert isinstance(generator._client, MlxQwenKoreanTranslationClient)
    assert generator._model_name == "local-llm:mlx-community/Qwen3-0.6B-4bit"


def test_korean_translation_local_glossary_mode_uses_harness_translation() -> None:
    generator = KoreanTranslationGenerator.from_settings(
        Settings(korean_translation_generation_mode="local_glossary")
    )

    result = generator.translate(KoreanTranslationContext(text="삼성전자 실적 개선"))

    assert result.provider == "local-financial-glossary"
    assert result.model_version == "local-financial-glossary-v2"
    assert result.status == "TRANSLATED"
    assert "LOCAL_TRANSLATION_DISABLED" not in result.quality_flags
    assert result.translated_text == "Samsung Electronics earnings improvement"


def test_korean_translation_local_glossary_mode_applies_request_glossary_terms() -> None:
    generator = KoreanTranslationGenerator.from_settings(
        Settings(korean_translation_generation_mode="local_glossary")
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="현대차 실적 개선",
            glossary_terms=[
                FinancialGlossaryTerm(
                    source_term="현대차",
                    normalized_term="현대차",
                    english_term="Hyundai Motor",
                    category="stock",
                )
            ],
        )
    )

    assert result.provider == "local-financial-glossary"
    assert result.status == "TRANSLATED"
    assert result.translated_text == "Hyundai Motor earnings improvement"


def test_korean_translation_local_glossary_mode_keeps_short_financial_headline_usable() -> None:
    generator = KoreanTranslationGenerator.from_settings(
        Settings(korean_translation_generation_mode="local_glossary")
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="“크래미는 못 보낸다”…상폐 위기 한성기업, ‘애국기업’ 응원에 주가 급등",
            glossary_terms=[
                FinancialGlossaryTerm(
                    source_term="한성기업",
                    normalized_term="한성기업",
                    english_term="Hansung Enterprise",
                    category="stock",
                )
            ],
        )
    )

    assert result.provider == "local-financial-glossary"
    assert result.status == "TRANSLATED"
    assert result.quality_flags == []
    assert result.translated_text == (
        "delisting crisis Hansung Enterprise, support stock price surge"
    )


def test_korean_translation_local_llm_requires_trained_adapter(tmp_path: Path) -> None:
    with pytest.raises(ModelArtifactNotFoundError):
        KoreanTranslationGenerator.from_settings(
            Settings(
                korean_translation_generation_mode="local_llm",
                korean_translation_llm_endpoint="",
                korean_translation_mlx_adapter_path=tmp_path / "missing-translation-lora",
            )
        )


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


def test_korean_translation_nmt_client_defaults_to_local_nllb_model() -> None:
    client = NllbKoreanEnglishTranslationClient()

    assert client.model_name == "facebook/nllb-200-distilled-600M"


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
        '{"translation":"Investors should check Samjeon Nix and Triangunxi\'s trading levels."}'
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
    assert "SEMANTIC_MISMATCH:KOREAN_EXPORTERS" not in result.quality_flags
    assert "SOURCE_ACRONYM_MISSING:VI" in result.quality_flags


def test_korean_translation_rejects_bank_name_word_salad() -> None:
    client = FakeTranslationClient(
        json_translation(
            "KB semaphore and Newhan bank's 2-month earnings improved, while the "
            "KDB and Nhan bank were treated as the highest bidder."
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
                "하나증권은 은행주 2분기 실적이 양호하고 최선호주는 "
                "KB금융지주와 신한금융지주라고 밝혔다."
            ),
            source_type="NEWS",
        )
    )

    assert result.status == "SOURCE_LANGUAGE_FALLBACK"
    assert result.translated_text == ""
    assert "META_OR_REFUSAL_TEXT" in result.quality_flags
    assert "SEMANTIC_MISMATCH:KB_FINANCIAL" in result.quality_flags
    assert "SEMANTIC_MISMATCH:SHINHAN_FINANCIAL" in result.quality_flags
    assert "SEMANTIC_MISMATCH:BANK_TOP_PICK" in result.quality_flags
    assert "SEMANTIC_MISMATCH:QUARTER_TERM" in result.quality_flags


def test_korean_translation_repairs_kosdaq_surface_when_qwen_outputs_kosx() -> None:
    client = FakeTranslationClient(
        json_translation("KOSPI and KOSX fell as IPO stocks traded below their offering prices.")
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
        "Naver's KRW e-commerce platform broke even after a 76 percent drop from its KRW price."
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


def test_korean_translation_rejects_qwen_romanized_korean_word_salad() -> None:
    client = FakeTranslationClient(
        json_translation(
            "Kang Nam-Go's 4J revenue lingers, pab-wo-yeon's bellwether stock "
            "faces a rebound."
        )
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="강남점 ‘4조 매출’ 눈앞…박주형號 신세계百, 대장주 굳히나",
            glossary_terms=[
                FinancialGlossaryTerm(
                    source_term="대장주",
                    normalized_term="대장주",
                    english_term="Market Leader",
                    category="market_slang",
                ),
            ],
        )
    )

    assert result.status == "SOURCE_LANGUAGE_FALLBACK"
    assert result.translated_text == ""
    assert "SUSPICIOUS_ROMANIZED_KOREAN" in result.quality_flags


def test_korean_translation_repairs_honam_region_and_megaproject_surface() -> None:
    client = FakeTranslationClient(
        json_translation(
            "It may have brought attention to the expectation that the North American "
            "semiconductor-mega-project will receive benefits."
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
                "이는 전날 정부가 발표한 호남 반도체 메가 프로젝트의 수혜를 "
                "받을 것이란 기대감에 영향을 받은 것으로 풀이된다."
            ),
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert result.translated_text == (
        "It may have brought attention to the expectation that the Honam "
        "semiconductor mega project will receive benefits."
    )
    assert result.quality_flags == []


def test_korean_translation_uses_nmt_for_hallucinated_summary_surface() -> None:
    client = FakeTranslationClient(
        json_translation(
            "Golden Electric Group became Korea's largest semiconductor company on a "
            "Korean basis on a Korean scale."
        )
    )
    nmt_client = FakeNmtClient(
        "On the 30th, Kumho E&C and other stocks closed at their upper limits as "
        "investors focused on the Honam semiconductor mega project."
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        nmt_client=nmt_client,  # type: ignore[arg-type]
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text=(
                "30일 금호건설, 미래산업, 삼화전자가 상한가에 이름을 올리고 "
                "호남 반도체 메가 프로젝트 수혜 기대가 투자자들의 관심을 끌었다."
            ),
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert result.provider == "local-open-source-ko-en-nmt-translation"
    assert "Golden Electric Group" not in result.translated_text
    assert "Kumho E&C" in result.translated_text
    assert result.quality_flags == []


def test_korean_translation_rejects_missing_source_numbers() -> None:
    client = FakeTranslationClient(
        json_translation("Samsung Electronics limited internal home loans for employees.")
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="삼성전자는 사내 주택자금 대출을 85㎡ 이하 주택으로 제한했다.",
            glossary_terms=[
                FinancialGlossaryTerm(
                    source_term="삼성전자",
                    normalized_term="삼성전자",
                    english_term="Samsung Electronics",
                    category="stock",
                ),
            ],
        )
    )

    assert result.status == "SOURCE_LANGUAGE_FALLBACK"
    assert result.translated_text == ""
    assert "SOURCE_NUMBER_MISSING" in result.quality_flags


def test_korean_translation_uses_grounded_headline_prompt_for_short_titles() -> None:
    client = FakeTranslationClient(
        json_translation(
            "No big houses allowed: Samsung Electronics limits employee housing loans "
            "to homes of 85 square meters or less."
        )
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="“큰 집은 안돼”…삼성전자, 사내 주택자금 대출 85㎡ 이하로 제한",
            glossary_terms=[
                FinancialGlossaryTerm(
                    source_term="삼성전자",
                    normalized_term="삼성전자",
                    english_term="Samsung Electronics",
                    category="stock",
                ),
            ],
        )
    )

    rendered_prompt = "\n".join(message["content"] for message in client.calls[0])
    assert result.status == "TRANSLATED"
    assert result.quality_flags == []
    assert "삼성전자 = Samsung Electronics" in rendered_prompt
    assert "No big houses allowed" in rendered_prompt


def test_korean_translation_allows_normal_high_value_added_headline() -> None:
    client = FakeTranslationClient(
        json_translation("LG Chem expands high-value-added future strategic business areas.")
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="LG화학, 고부가가치 미래 전략사업 영역 확대",
            glossary_terms=[
                FinancialGlossaryTerm(
                    source_term="LG화학",
                    normalized_term="LG화학",
                    english_term="LG Chem",
                    category="stock",
                ),
            ],
        )
    )

    assert result.status == "TRANSLATED"
    assert (
        result.translated_text
        == "LG Chem expands high-value-added future strategic business areas."
    )
    assert result.quality_flags == []


def test_korean_translation_canonicalizes_dart_disclosure_title() -> None:
    client = FakeTranslationClient(
        json_translation("Hyundai Motor, Hyun-Taet, Bo-Do, and an ex-26.07.03")
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="현대자동차/풍문또는보도에대한해명(미확정)/2026.07.03",
            glossary_terms=[
                FinancialGlossaryTerm(
                    source_term="현대자동차",
                    normalized_term="현대자동차",
                    english_term="Hyundai Motor",
                    category="stock",
                ),
            ],
        )
    )

    assert result.status == "TRANSLATED"
    assert (
        result.translated_text
        == "Hyundai Motor / Explanation of rumors or media reports (unconfirmed) / 2026.07.03"
    )
    assert result.quality_flags == []


def test_korean_translation_uses_local_nmt_when_qwen_body_translation_is_low_quality() -> None:
    client = FakeTranslationClient(
        json_translation("LG화학은 반도체 소재 사업을 확대했다.")
    )
    nmt_client = FakeNmtClient(
        "LG Chem expanded its semiconductor materials business as AI investment increased."
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        nmt_client=nmt_client,  # type: ignore[arg-type]
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text=(
                "LG화학은 AI 투자 확대와 고대역폭 메모리 수요 증가로 "
                "반도체 소재 사업 확대를 본격화하며 글로벌 고객사 공급을 늘려 "
                "전자소재 매출 기반을 강화할 계획이라고 밝혔다."
            ),
            glossary_terms=[
                FinancialGlossaryTerm(
                    source_term="LG화학",
                    normalized_term="LG화학",
                    english_term="LG Chem",
                    category="stock",
                ),
            ],
        )
    )

    assert result.status == "TRANSLATED"
    assert result.provider == "local-open-source-ko-en-nmt-translation"
    assert result.model_version == "local-nmt:test-nllb"
    assert result.translated_text.startswith("LG Chem expanded")
    assert result.quality_flags == []
    assert nmt_client.calls


def test_korean_translation_accepts_nmt_body_when_korean_unit_numbers_shift() -> None:
    client = FakeTranslationClient(json_translation("폐배터리 관련주는 강세를 이어갔다."))
    nmt_client = FakeNmtClient(
        "Waste-battery shares rose 10.44% as investor demand improved."
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        nmt_client=nmt_client,  # type: ignore[arg-type]
        model_name="test-qwen3-translation",
    )

    source = (
        "폐배터리 관련주가 29일 강세를 이어가고 있다. "
        "한국거래소에 따르면 이날 오후 2시53분 현재 에코프로는 "
        "23.79% 오른 11만8100원에 거래중이다."
    )

    result = generator.translate(KoreanTranslationContext(text=source, source_type="NEWS"))

    assert result.status == "TRANSLATED"
    assert result.provider == "local-open-source-ko-en-nmt-translation"
    assert result.translated_text.startswith("Waste-battery shares rose")
    assert result.quality_flags == []
    assert nmt_client.calls


def test_korean_translation_accepts_hyphenated_source_term_surface_from_nmt() -> None:
    client = FakeTranslationClient(json_translation("데이터센터 관련 수요가 늘었다."))
    nmt_client = FakeNmtClient(
        "Battery suppliers rose as AI data-center demand and energy-storage investment grew."
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        nmt_client=nmt_client,  # type: ignore[arg-type]
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text=(
                "2차전지 기업들은 인공지능 데이터센터 증가와 에너지저장장치 투자 확대에 "
                "따른 배터리 수요 기대감으로 상승했다."
            ),
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert result.provider == "local-open-source-ko-en-nmt-translation"
    assert "data-center demand" in result.translated_text
    assert result.quality_flags == []


def test_korean_translation_repairs_unbacked_korean_exporters_surface() -> None:
    client = FakeTranslationClient(json_translation("관광업 주가가 약세를 보였다."))
    nmt_client = FakeNmtClient(
        "Korean exporters saw weaker prices as travel demand slowed."
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        nmt_client=nmt_client,  # type: ignore[arg-type]
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="국내 관광산업 관련 상장사들의 주가가 전반적으로 약세를 나타냈다.",
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert "tourism companies saw weaker prices" in result.translated_text
    assert "Korean exporters" not in result.translated_text
    assert result.quality_flags == []


def test_korean_translation_best_effort_nmt_recovers_long_body() -> None:
    nmt_client = FakeNmtClient(
        [
            "The article says Korean companies faced restructuring pressure.",
            "Investors should monitor credit risk and ownership changes.",
            "Regulatory filings and market reactions also need attention.",
        ]
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=FakeTranslationClient("{}"),
        nmt_client=nmt_client,  # type: ignore[arg-type]
        model_name="test-qwen3-translation",
    )
    source = (
        "한계기업 구조조정 압박이 커지면서 투자자는 신용위험과 대주주 변경을 "
        "확인해야 한다. 금융당국 공시와 시장 반응도 함께 점검해야 한다. "
    ) * 20

    result = generator._translate_body_with_nmt_best_effort(
        source,
        KoreanTranslationContext(text=source, source_type="NEWS"),
    )

    assert result is not None
    assert result.status == "TRANSLATED"
    assert result.provider == "local-open-source-ko-en-nmt-translation"
    assert "Korean companies faced restructuring pressure" in result.translated_text
    assert "Regulatory filings" in result.translated_text
    assert result.quality_flags == []


def test_korean_translation_nmt_recovers_mid_sized_body_with_source_term_flag() -> None:
    client = FakeTranslationClient(json_translation("삼성전자는 엑시노스 확대를 밝혔다."))
    nmt_client = FakeNmtClient(
        [
            "Samsung Electronics will use Exynos 2700 in some Galaxy S27 models.",
            "The strategy is expected to improve non-memory earnings.",
        ]
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        nmt_client=nmt_client,  # type: ignore[arg-type]
        model_name="test-qwen3-translation",
    )
    source = (
        "삼성전자는 갤럭시S27 일부 모델에 엑시노스 2700을 적용하고 "
        "미국 시장에는 퀄컴 스냅드래곤을 탑재한다고 밝혔다. "
        "비메모리 실적 개선 기대가 커졌고 파운드리 가동률 회복도 주목된다. "
    ) * 4

    result = generator.translate(
        KoreanTranslationContext(
            text=source,
            source_type="NEWS",
            title="삼성전자 엑시노스 확대",
        )
    )

    assert result.status == "TRANSLATED"
    assert result.provider == "local-open-source-ko-en-nmt-translation"
    assert "Samsung Electronics will use Exynos 2700" in result.translated_text
    assert result.quality_flags == []
    assert nmt_client.calls


def test_korean_translation_prefers_nmt_for_long_repetitive_reference_body() -> None:
    nmt_client = FakeNmtClient(
        "Hyundai Motor ranked first in the electric-vehicle brand reputation index."
    )
    client = FakeTranslationClient(json_translation("브랜드평판 기사입니다."))
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        nmt_client=nmt_client,  # type: ignore[arg-type]
        model_name="test-qwen3-translation",
    )
    source = (
        "2026년 7월 전기차 관련 상장기업 브랜드평판 조사에서 현대차가 1위를 "
        "차지했고 삼성SDI와 LG에너지솔루션이 뒤를 이었다. 브랜드평판지수는 "
        "참여가치, 소통가치, 시장가치와 재무가치를 합산해 산정했다. "
        "현대모비스도 전기차 부품 공급망과 브랜드 빅데이터 분석 대상에 포함됐다. "
    ) * 26

    result = generator.translate(KoreanTranslationContext(text=source, source_type="NEWS"))

    assert result.status == "TRANSLATED"
    assert result.provider == "local-open-source-ko-en-nmt-translation"
    assert "brand reputation index" in result.translated_text
    assert "Hyundai Mobis" in result.translated_text
    assert result.quality_flags == []
    assert nmt_client.calls
    assert client.calls == []


def test_korean_translation_appends_missing_market_surface_in_long_nmt_body() -> None:
    nmt_client = FakeNmtClient(
        [
            "Medikox attracted attention after its largest shareholder changed.",
            "Investors are watching governance changes and funding plans.",
            "The company is reviewing new business expansion with outside investors.",
        ]
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=FakeTranslationClient("{}"),
        nmt_client=nmt_client,  # type: ignore[arg-type]
        model_name="test-qwen3-translation",
    )
    source = (
        "코스닥 상장사 메디콕스는 최대주주 변경 이후 신사업 확대와 자금 조달 "
        "계획을 검토하고 있다. 투자자는 지배구조 변화와 자금 사용처를 확인해야 한다. "
    ) * 10

    result = generator._translate_body_with_nmt_best_effort(
        source,
        KoreanTranslationContext(text=source, source_type="NEWS"),
    )

    assert result is not None
    assert result.status == "TRANSLATED"
    assert "KOSDAQ" in result.translated_text
    assert result.quality_flags == []


def test_korean_translation_appends_missing_glossary_surface_in_long_nmt_body() -> None:
    nmt_client = FakeNmtClient(
        [
            "DXVX rose as investors watched infectious-disease diagnosis demand.",
            "Pharmaceutical companies tracked antibiotic supply and treatment demand.",
            "Investors monitored respiratory-disease diagnostics and drug pipelines.",
        ]
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=FakeTranslationClient("{}"),
        nmt_client=nmt_client,  # type: ignore[arg-type]
        model_name="test-qwen3-translation",
    )
    source = (
        "젠큐릭스와 DXVX는 감염병 진단 수요와 호흡기 질환 치료제 공급 이슈로 "
        "투자자 관심을 받았다. 제약·바이오 기업들은 진단 인프라와 신약 파이프라인을 "
        "강조했다. "
    ) * 8

    result = generator._translate_body_with_nmt_best_effort(
        source,
        KoreanTranslationContext(
            text=source,
            source_type="NEWS",
            glossary_terms=[
                FinancialGlossaryTerm(
                    source_term="젠큐릭스",
                    normalized_term="젠큐릭스",
                    english_term="Gencurix",
                    category="stock",
                )
            ],
        ),
    )

    assert result is not None
    assert "Gencurix" in result.translated_text
    assert result.quality_flags == []


def test_korean_translation_removes_residual_hangul_from_long_nmt_body() -> None:
    nmt_client = FakeNmtClient(
        [
            "Laneige 라네즈 launched a facial serum for skin-care demand.",
            "TriCircle 트라이써클 expanded fashion-commerce promotions.",
            "Investors watched brand demand and online sales channels.",
        ]
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=FakeTranslationClient("{}"),
        nmt_client=nmt_client,  # type: ignore[arg-type]
        model_name="test-qwen3-translation",
    )
    source = (
        "라네즈는 신제품 세럼을 출시했고 트라이써클은 패션 커머스 프로모션을 "
        "확대했다. 투자자는 브랜드 수요와 온라인 판매 채널을 확인해야 한다. "
    ) * 10

    result = generator._translate_body_with_nmt_best_effort(
        source,
        KoreanTranslationContext(text=source, source_type="NEWS"),
    )

    assert result is not None
    assert "Laneige" in result.translated_text
    assert "TriCircle" in result.translated_text
    assert not re.search(r"[가-힣ㄱ-ㅎㅏ-ㅣ]", result.translated_text)
    assert result.quality_flags == []


def test_korean_translation_repairs_pathological_nmt_repetition() -> None:
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=FakeTranslationClient("{}"),
        model_name="test-qwen3-translation",
    )
    source = (
        "제약업계는 임상 결과와 신약 공급 일정을 설명했다. "
        "투자자는 제품 허가 일정과 시장 반응을 함께 확인해야 한다. "
    ) * 10
    translated = (
        "Professor Dr. Dr. Dr. Dr. Dr. Dr. Lee shared clinical results. "
        "Professor Dr. Dr. Dr. Dr. Dr. Dr. Lee shared clinical results. "
        "Professor Dr. Dr. Dr. Dr. Dr. Dr. Lee shared clinical results."
    )

    repaired = generator._repair_pathological_repetitions(translated)

    assert "Dr. Dr. Dr." not in repaired
    assert "REPEATED_TRANSLATION_PHRASE" not in generator._quality_flags(source, repaired)


def test_korean_translation_repairs_unbacked_highest_bidder_surface() -> None:
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=FakeTranslationClient("{}"),
        model_name="test-qwen3-translation",
    )

    repaired = generator._repair_common_translation_surfaces(
        "후발주자 제네릭 진입 속도가 빨라지고 있다.",
        "The highest bidder entered the market faster.",
    )

    assert "highest bidder" not in repaired.lower()
    assert "later entrant" in repaired


def test_korean_translation_accepts_best_effort_qwen_for_long_body_noncritical_flags() -> None:
    client = FakeTranslationClient(
            json_translation(
                "Samsung Electronics expanded AI infrastructure investment while investors "
                "tracked semiconductor supply-chain capacity, data center demand, and "
                "earnings recovery."
        )
    )
    nmt_client = FakeNmtClient("NMT should not be called for noncritical Qwen body flags.")
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        nmt_client=nmt_client,  # type: ignore[arg-type]
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text=(
                "삼성전자는 2026년 AI 인프라 투자 확대와 반도체 공급망 개선 계획을 "
                "발표했다. 투자자들은 실적 회복 속도와 시장 흐름을 확인하고 있다. "
                "시장 관계자들은 고객사 주문과 메모리 가격 반등 여부를 함께 점검하고 "
                "있다. 증권가는 공급망 투자 집행 속도가 향후 매출 회복의 핵심 변수가 "
                "될 것으로 보고 있다. 회사는 고성능 메모리와 데이터센터 수요 변화에 "
                "맞춰 생산 계획을 조정하고, 주요 고객사와 장기 공급 협의를 이어가고 "
                "있다고 설명했다. 업계는 투자 집행 일정과 설비 반입 속도도 함께 "
                "확인하고 있다."
            ),
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert result.provider == "local-open-source-qwen3-translation"
    assert result.model_version == "test-qwen3-translation"
    assert "Samsung Electronics expanded AI infrastructure" in result.translated_text
    assert result.quality_flags == []
    assert client.calls
    assert nmt_client.calls == []


def test_korean_translation_repairs_local_nmt_semiconductor_body_surfaces() -> None:
    client = FakeTranslationClient(json_translation("LG화학은 반도체 사업을 확대했다."))
    nmt_client = FakeNmtClient(
        "The products supplied by LG Chem are customized strippers optimized for "
        "Amkor's new line, reducing photoresist and residue removal time by 50%. "
        "LG Chem said on the 5th that it will mass-produce semiconductor strippers "
        "for back-end OSAT company Amkor. Residue removal performance directly affects "
        "product yield. LG Chem President Kim Dong-chun said cooperation with Amkor "
        "will strengthen. LG Chem will invest 15 trillion won in R&D by 2035 and "
        "grow its electronic materials business to about 2 trillion won by 2030, "
        "focusing on thermal management materials and glass substrates."
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        nmt_client=nmt_client,  # type: ignore[arg-type]
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text=(
                "LG화학이 공급하는 제품은 앰코의 신규 라인 환경에 최적화된 맞춤형 "
                "스트리퍼로 포토레지스트와 잔여물을 벗겨내는 시간을 기존 대비 50% "
                "단축했다. LG화학은 5일 미국 글로벌 반도체 후공정(OSAT) 기업 "
                "앰코에 반도체용 스트리퍼를 양산 공급한다고 밝혔다. 잔여물 제거 "
                "성능은 제품 수율에 직접적인 영향을 미치고 있다. 김동춘 LG화학 "
                "사장은 앰코와 협력을 강화한다고 밝혔다. "
                "LG화학은 최근 2035년까지 연구개발(R&D)에 총 15조원을 투자하고 "
                "반도체·인프라 분야에서 열관리 소재·유리기판 경쟁력 확보에 주력해 "
                "전자소재 사업을 2030년까지 약 2조원 규모로 성장시킨다는 방침이다."
            ),
            glossary_terms=[
                FinancialGlossaryTerm(
                    source_term="LG화학",
                    normalized_term="LG화학",
                    english_term="LG Chem",
                    category="stock",
                ),
            ],
        )
    )

    assert result.status == "TRANSLATED"
    assert "LG Chem" in result.translated_text
    assert "Amkor" in result.translated_text
    assert "Kim Dong-chun" in result.translated_text
    assert "15 trillion won" in result.translated_text
    assert "on the 5th" in result.translated_text
    assert "back-end OSAT company Amkor" in result.translated_text
    assert "product yield" in result.translated_text
    assert "thermal management materials" in result.translated_text
    assert "glass substrates" in result.translated_text
    assert "Kim Jong-un" not in result.translated_text
    assert "Striper" not in result.translated_text
    assert "Amko Amkor" not in result.translated_text
    assert result.quality_flags == []


def test_korean_translation_repairs_korean_bank_deposit_body_surfaces() -> None:
    client = FakeTranslationClient(
        json_translation(
            "According to the National Association of Churches (NAC), as of May, "
            "10 of the 18 temples offered annual interest rates of more than 3 percent "
            "on a one-year periodic allowance. In the first half, total revenues of "
            "major central banks increased by almost 90 trillion yuan, while the "
            "bank's receivables and reception function improved."
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
                "전국은행연합회에 따르면 지난 5월 기준 사원은행 18곳 가운데 "
                "10곳이 1년 만기 정기예금에 연 3% 이상의 금리를 제공했다. "
                "올해 상반기 국내 주요 시중은행의 총수신이 90조원 가까이 "
                "늘어나며 은행 수신 기능이 개선됐다."
            ),
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert "Korea Federation of Banks" in result.translated_text
    assert "member banks" in result.translated_text
    assert "time deposits" in result.translated_text
    assert "commercial banks" in result.translated_text
    assert "90 trillion won" in result.translated_text
    assert "deposits" in result.translated_text
    assert "deposit-taking function" in result.translated_text
    assert "National Association of Churches" not in result.translated_text
    assert "temples" not in result.translated_text
    assert "yuan" not in result.translated_text
    assert "receivables" not in result.translated_text
    assert result.quality_flags == []


def test_korean_translation_repairs_semiconductor_adr_body_when_local_models_fail() -> None:
    client = FakeTranslationClient(json_translation("고장난 전문 번역"))
    nmt_client = FakeNmtClient("고장난 NMT 전문 번역")
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        nmt_client=nmt_client,  # type: ignore[arg-type]
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text=(
                "코스피가 극심한 변동성 끝에 8000선을 회복했지만 시장의 시선은 이번 주 "
                "예정된 반도체 이벤트에 집중되고 있다. 7일 삼성전자 2분기 잠정실적 "
                "발표와 10일 SK하이닉스 미국 주식예탁증서(ADR) 상장이 연이어 예정돼 "
                "있기 때문이다. 두 이벤트 결과에 따라 최근 급락한 반도체주의 투자심리가 "
                "빠르게 회복될지 여부가 결정될 가능성이 크다. 지난주 코스피는 장중 "
                "7300선까지 밀리며 고점 대비 20% 넘게 하락했지만 기관 중심의 저가 "
                "매수세가 유입되며 8088.34로 거래를 마쳤다. ◆ 외국인 20조원 "
                "매도…반도체 집중 이탈 지난주 외국인은 유가증권시장에서 약 "
                "19조8000억원을 순매도했다. 매도는 삼성전자와 SK하이닉스에 집중됐다. "
                "반면 개인과 기관은 각각 11조원, 8조원 넘게 순매수하며 낙폭 과대 "
                "종목을 받아냈다. 시장에서는 이번 주 삼성전자 실적과 하이닉스 ADR "
                "상장이 외국인 수급을 다시 반도체로 돌려세울 수 있는 시험대가 될 것으로 "
                "보고 있다. ◆ 삼성전자 실적이 첫 번째 분수령 증권가는 이번 주 가장 "
                "중요한 이벤트로 삼성전자 잠정실적을 꼽는다. 영업이익이 시장 예상치를 "
                "웃도는 '어닝 서프라이즈'가 나올 경우 메모리 업황 개선 기대가 다시 "
                "살아나며 최근의 AI 투자 둔화 우려를 상당 부분 상쇄할 수 있다는 분석이다. "
                "이어 10일 예정된 SK하이닉스 ADR 상장은 해외 투자자의 접근성을 높이는 "
                "계기가 될 것으로 기대된다. ADR 상장이 본격적인 해외 자금 유입으로 "
                "이어질 경우 하이닉스는 물론 국내 반도체 업종 전반의 투자심리 개선에도 "
                "긍정적으로 작용할 수 있다. ◆ 아직 끝나지 않은 변동성…\"7월 중순까지 "
                "확인 필요\" 다만 시장의 긴장감은 여전하다. 코스피200 변동성지수"
                "(VKOSPI)는 89 수준으로 금융시장 불안이 여전히 높은 상태를 나타내고 "
                "있다. 이는 하루 평균 ±5% 안팎의 큰 변동성이 이어질 수 있다는 의미다. "
                "전문가들은 삼성전자 실적이 단기 반등의 첫 번째 관문이라면, 이후에는 "
                "TSMC와 ASML 실적, 글로벌 AI 기업들의 설비투자(CAPEX) 계획이 하반기 "
                "증시 방향을 결정할 핵심 변수라고 보고 있다."
            ),
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert "KOSPI recovered the 8,000 level" in result.translated_text
    assert "SK hynix is scheduled to list its U.S. American depositary receipts (ADR)" in (
        result.translated_text
    )
    assert "KRW 19.8 trillion" in result.translated_text
    assert "KRW 11 trillion and KRW 8 trillion" in result.translated_text
    assert "KOSPI 200 volatility index (VKOSPI) is near 89" in result.translated_text
    assert "capital expenditure (CAPEX)" in result.translated_text
    assert "고장난" not in result.translated_text
    assert result.quality_flags == []


def test_korean_translation_repairs_weekly_semiconductor_flow_report_body() -> None:
    client = FakeTranslationClient(json_translation("고장난 수급 리포트 번역"))
    nmt_client = FakeNmtClient("고장난 수급 리포트 NMT")
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        nmt_client=nmt_client,  # type: ignore[arg-type]
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text=(
                "지난 한 주간 국내 증시는 외국인의 거센 매도세에 밀려 코스피와 "
                "코스닥 지수 모두 하락 마감했다. 외국인이 쏟아낸 물량은 코스피 "
                "시장에서 개인과 기관이, 코스닥 시장에서는 개인이 고스란히 받아냈다. "
                "6일 한국거래소에 따르면 지난달 29일부터 이달 3일까지 코스피 지수는 "
                "8394.65에서 8088.34로 306.31포인트(3.65%) 하락했다. 같은 기간 "
                "코스닥 지수 역시 920.57에서 869.41로 51.16포인트(5.56%) 내렸다. "
                "코스피 시장에서는 개인이 11조1217억원, 기관이 8조1212억원을 각각 "
                "순매수하며 지수 방어에 나섰다. 반면 외국인은 홀로 19조8374억원을 "
                "순매도하며 하락세를 주도했다. 코스닥에서는 개인이 3490억원을 "
                "순매수했지만, 기관과 외국인은 각각 1769억원, 1827억원을 순매도했다. "
                "기관 순매수로는 SK스퀘어에 가장 많은 2조3009억원 자금이 몰렸다. "
                "이어 삼성전자(1조8150억원), 이수페타시스(4652억원), KB금융"
                "(2746억원), 삼성전기(1837억원), 한화에어로스페이스(1836억원), "
                "SK하이닉스(1628억원) 순으로 많이 사들였다. 개인은 SK하이닉스"
                "(7조7920억원)와 삼성전자(5조6603억원)를 집중 매수했다. "
                "한미반도체(2222억원), 삼성전자우(1661억원), 한화오션(1256억원), "
                "LS일렉트릭(1048억원)이 뒤를 이었다. 반면 가장 많이 판 종목은 "
                "삼성전기(6076억원)였으며, SK스퀘어(2953억원), 이수페타시스"
                "(1442억원), 셀트리온(1224억원) 등은 순매도했다. 외국인은 "
                "삼성전기(4462억원)를 가장 많이 받아갔다. 이어 DB하이텍"
                "(2860억원), LG이노텍(1657억원), 한미반도체(1485억원), "
                "삼성바이오로직스(536억원) 순으로 순매수했다. 반면 SK하이닉스를 "
                "8조2824억원 팔아치웠으며, 삼성전자(7조6880억원), SK스퀘어"
                "(1조9875억원), 이수페타시스(3182억원), 삼성전자우(2630억원) 등 "
                "반도체 대형주를 대거 차익 실현했다. 이경민 대신증권 연구원은 "
                "\"미국 증시에서 메타, 애플발 쇼크 여파로 반도체 업종의 약세가 "
                "지속됐다\"며 \"지난주 국내 증시에서도 삼성전자와 SK하이닉스 등 "
                "반도체주가 하락 출발했으나, 단기 급락에 따른 반발 매수세가 유입되며 "
                "낙폭을 만회하고 반등에 성공했다\"고 분석했다. 이어 \"7일 삼성전자 "
                "잠정실적 발표가 예정된 가운데, 앤트로픽 자체 AI 칩 개발 협력 소식과 "
                "3분기 D램 가격 최대 20% 인상 전망이 맞물리면서 실적 개선에 대한 "
                "기대감이 한층 높아지고 있다\"고 덧붙였다."
            ),
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert "KOSPI fell 306.31 points, or 3.65%, from 8,394.65 to 8,088.34" in (
        result.translated_text
    )
    assert "KOSDAQ fell 51.16 points, or 5.56%, from 920.57 to 869.41" in (
        result.translated_text
    )
    assert "SK Square drew the largest inflow" in result.translated_text
    assert "KRW 8.2824 trillion of SK hynix" in result.translated_text
    assert "Anthropic's collaboration on its own AI chip" in result.translated_text
    assert "20% increase in third-quarter DRAM prices" in result.translated_text
    assert "고장난" not in result.translated_text
    assert result.quality_flags == []


def test_korean_translation_preserves_semiconductor_glossary_appendix_with_nmt() -> None:
    client = FakeTranslationClient(json_translation("고대역폭 메모리와 OSAT 설명."))
    nmt_client = FakeNmtClient(
        "Outsourced Semiconductor Assembly and Test (OSAT) is a specialized "
        "semiconductor assembly and testing company."
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        nmt_client=nmt_client,  # type: ignore[arg-type]
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text=(
                "고대역폭 메모리(High Bandwidth Memory) = AI 반도체 등에 쓰이는 "
                "초고속·고성능 메모리 OSAT(Outsourced Semiconductor Assembly and "
                "Test) = 반도체 후공정인 조립과 시험을 수행하는 전문업체"
            ),
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert "AI semiconductors" in result.translated_text
    assert "Outsourced Semiconductor Assembly and Test (OSAT)" in result.translated_text
    assert result.quality_flags == []


def test_korean_translation_removes_news_boilerplate_before_chunking() -> None:
    generator = KoreanTranslationGenerator(enabled=False)

    normalized = generator._normalize_text(
        "잠깐! 현재 Internet Explorer 8이하 버전을 이용중이십니다. "
        "최신 브라우저(Browser) 사용을 권장드립니다! "
        "[투데이에너지 신영균 기자] LG화학이 반도체 소재 사업을 확대하고 있다."
    )

    assert "Internet Explorer" not in normalized
    assert "최신 브라우저" not in normalized
    assert "기자" not in normalized
    assert normalized == "LG화학이 반도체 소재 사업을 확대하고 있다."


def test_korean_translation_rejects_single_token_romanized_korean_noise() -> None:
    client = FakeTranslationClient(
        json_translation(
            "Hyundai Motor, Haeulwo, and Honglai's business and operation plans were disclosed."
        )
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="현대차, 장래사업ㆍ경영 계획 공시",
            glossary_terms=[
                FinancialGlossaryTerm(
                    source_term="현대차",
                    normalized_term="현대차",
                    english_term="Hyundai Motor",
                    category="stock",
                ),
            ],
        )
    )

    assert result.status == "SOURCE_LANGUAGE_FALLBACK"
    assert result.translated_text == ""
    assert "SUSPICIOUS_ROMANIZED_KOREAN" in result.quality_flags


def test_korean_translation_rejects_semantically_broken_summary_fragments() -> None:
    client = FakeTranslationClient(
        json_translation(
            "The leader, during the subsequent check of the semiconductor cluster, "
            "will support the three-sentence mega-project."
        )
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="반도체 클러스터 점검회의에서 메가프로젝트 지원 방안이 논의됐다.",
            source_type="NEWS",
        )
    )

    assert result.status == "SOURCE_LANGUAGE_FALLBACK"
    assert result.translated_text == ""
    assert "META_OR_REFUSAL_TEXT" in result.quality_flags


def test_korean_translation_repairs_stock_name_surface_from_glossary() -> None:
    client = FakeTranslationClient(
        json_translation("Samjeon Electronics expects operating profit to improve.")
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="삼성전자는 영업이익 개선이 예상된다고 밝혔다.",
            glossary_terms=[
                FinancialGlossaryTerm(
                    source_term="삼성전자",
                    normalized_term="삼성전자",
                    english_term="Samsung Electronics",
                    category="stock",
                ),
            ],
        )
    )

    assert result.status == "TRANSLATED"
    assert result.translated_text == "Samsung Electronics expects operating profit to improve."
    assert result.quality_flags == []


def test_korean_translation_repairs_broken_skhynix_nasdaq_title() -> None:
    client = FakeTranslationClient(
        json_translation(
            "SK hynix was expected to trade on the NMSK exchange. "
            "The NMSK market may close within a few days."
        )
    )
    nmt_client = FakeNmtClient(
        "SK hynix is preparing a Nasdaq listing, raising questions about whether "
        "it will help or hurt the domestic stock market."
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        nmt_client=nmt_client,  # type: ignore[arg-type]
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="[오늘의 경제뉴스] SK하이닉스 나스닥 상장...국내 증시에 약일까 독일...",
            glossary_terms=[
                FinancialGlossaryTerm(
                    source_term="SK하이닉스",
                    normalized_term="SK하이닉스",
                    english_term="SK hynix",
                    category="stock",
                ),
            ],
        )
    )

    assert result.status == "TRANSLATED"
    assert "NMSK" not in result.translated_text
    assert result.translated_text == (
        "Today's Economic News: SK hynix's Nasdaq listing raises questions about "
        "its impact on the domestic stock market."
    )
    assert result.quality_flags == []


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "코스피 PER 금융위기 이후 최저…골드만삭스 “상승 여지”",
            "KOSPI PER falls to its lowest since the financial crisis; Goldman Sachs "
            "sees room for gains.",
        ),
        (
            "[박근종 칼럼] 3년 새 기업회생 신청 2배 급증, "
            "정리할 ‘한계기업’은 신속 정리하는 게 최선",
            "Corporate rehabilitation applications doubled in three years, making "
            "swift restructuring of marginal companies the best course.",
        ),
        (
            "2분기 대구지역 상장법인 시총 감소세 전환 - 대구신문",
            "Daegu-listed companies' market capitalization turned lower in the second quarter.",
        ),
        (
            "대구 상장사 시총 5분기만에 성장 멈춤… 코스닥 침체가 발목 - 경북도민일보",
            "Daegu-listed companies' market-cap growth stopped after five quarters as "
            "KOSDAQ weakness weighed.",
        ),
        (
            "'동전주 탈출' 몸부림치는 코스닥… 주식병합 1년새 24배 폭증",
            "KOSDAQ companies struggle to escape penny-stock status as stock "
            "consolidations surge 24-fold in a year.",
        ),
        (
            "엔비디아 로봇매출 1%대…액추에이터 수혜주 급부상 - 글로벌이코노믹",
            "Nvidia's robot revenue remains in the 1% range as actuator beneficiary "
            "stocks rapidly emerge.",
        ),
        (
            "IPO시장 칼바람… 상장기업 수·공모금액 절반 싹둑 - 머니투데이",
            "IPO market chills as the number of listed companies and offering "
            "proceeds are cut in half.",
        ),
        (
            "SK하이닉스, 10일 나스닥 상장…AI 투자자 공략",
            "SK hynix to list on Nasdaq on the 10th as it targets AI investors.",
        ),
        (
            '삼닉 레버리지로 손실 입은 개미들 … "이제라도 팔까" 전전긍긍',
            "Retail investors fret over whether to sell after losses in Samjeon "
            "Nix leveraged products.",
        ),
        (
            "美서 중견·중소기업 자금줄 역할…유럽 로드쇼엔 투자자들 북적",
            "Korean securities firms serve as funding sources for mid-sized and "
            "small U.S. companies as investors crowd European roadshows.",
        ),
        (
            "지켜보는 우리가 드러누울 듯 [김소연 칼럼]",
            "Watching this market is enough to make us collapse.",
        ),
        (
            "AI 신의 탄생과 인간의 종말",
            "The birth of an AI god and the end of humans.",
        ),
        (
            "이 대통령, 오늘 반도체 클러스터 점검회의…메가프로젝트 지원",
            "President Lee to review semiconductor cluster support measures for "
            "megaprojects today.",
        ),
        (
            "역대급 증시 호황에 개미들 상반기 161조 순매수",
            "Retail investors net bought KRW 161 trillion in the first half amid "
            "a record stock-market boom.",
        ),
        (
            "대구 상장사 시총 2조원 증발…5분기 상승세 꺾였다",
            "Daegu-listed companies lost KRW 2 trillion in market capitalization "
            "as a five-quarter rally ended.",
        ),
        (
            "한은의 경고 “삼전닉스 레버리지, 개미들 죽여”",
            "Bank of Korea warns that Samjeon Nix leverage is hurting retail investors.",
        ),
        (
            "트럼프, 재임 중 쿠팡株 18회 거래… 한미 통상 갈등 심화 우려",
            "Trump traded Coupang shares 18 times while in office, raising "
            "concerns over deeper Korea-U.S. trade tensions.",
        ),
        (
            "연기금, 주식 수익률 날았는데 대체투자는 '고전'… 하반기 개선 기대",
            "Pension funds' stock returns soared, but alternative investments "
            "struggled; improvement is expected in the second half.",
        ),
        (
            "실상은 다른 회사(?)…삼성전자 DX·DS '투트랙 ESG' 속사정",
            "Samsung Electronics' DX and DS divisions pursue separate two-track "
            "ESG strategies.",
        ),
        (
            "현대차·기아·모비스 초비상…美 부품 82% 유지",
            "Hyundai Motor, Kia, and Hyundai Mobis are on high alert as the U.S. "
            "keeps an 82% parts rule.",
        ),
        (
            "“증시 때문에 머리가 다 빠지네요”…결국 은행으로 다시 돈 몰린다",
            '"The stock market is making my hair fall out"; money is flowing '
            "back into banks.",
        ),
        (
            "외국인 20조 던진 반도체…이번 주 '삼전 실적·하이닉스 ADR'이 승부 가...",
            "Foreigners dumped KRW 20 trillion in semiconductor stocks; Samsung "
            "earnings and SK hynix's ADR are this week's key tests.",
        ),
        (
            "[주간수급리포트] 외인 20兆 매도 폭탄에 국장 하락...개인·기관 반도체...",
            "Weekly flow report: foreign investors' KRW 20 trillion selling wave "
            "dragged Korean stocks lower, while retail and institutional investors "
            "bought semiconductor names.",
        ),
        (
            "신차 가격 떨어지는 美 시장…현대차·기아, 'RV·HEV' 투트랙으로 수익...",
            "As U.S. new-car prices fall, Hyundai Motor and Kia defend profits "
            "with a two-track RV and HEV strategy.",
        ),
    ],
)
def test_korean_translation_repairs_market_news_headlines(
    source: str,
    expected: str,
) -> None:
    client = FakeTranslationClient(json_translation("고장난 제목 번역"))
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(KoreanTranslationContext(text=source, source_type="NEWS"))

    assert result.status == "TRANSLATED"
    assert result.translated_text == expected
    assert result.quality_flags == []


def test_korean_translation_allows_retail_investor_surface_for_gaemi_glossary() -> None:
    client = FakeTranslationClient(json_translation("Broken fallback title."))
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="한은의 경고 “삼전닉스 레버리지, 개미들 죽여”",
            source_type="NEWS",
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
    assert result.translated_text == (
        "Bank of Korea warns that Samjeon Nix leverage is hurting retail investors."
    )
    assert result.quality_flags == []


def test_korean_translation_preserves_samnik_short_localism_surface() -> None:
    client = FakeTranslationClient(json_translation("Ants lost money in Samnick leverage."))
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="개미들이 삼닉 레버리지에서 손실을 봤다.",
            glossary_terms=[
                FinancialGlossaryTerm(
                    source_term="삼닉",
                    normalized_term="삼전닉스",
                    english_term="Samjeon Nix",
                    category="market_slang",
                ),
            ],
        )
    )

    assert result.status == "TRANSLATED"
    assert "Samjeon Nix" in result.translated_text
    assert "Samnick" not in result.translated_text
    assert result.quality_flags == []


def test_korean_translation_uses_nmt_when_qwen_drops_market_supply_chain_terms() -> None:
    client = FakeTranslationClient(
        json_translation(
            "Nvidia's revenue contribution still lags, and domestic investors are "
            "from both the North and South are shifting attention to cars."
        )
    )
    nmt_client = FakeNmtClient(
        "As it turns out that Envidia's actual sales contribution to the global robotics "
        "rally remains small, domestic investors are shifting attention to the parts "
        "supply chain instead of finished products."
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        nmt_client=nmt_client,  # type: ignore[arg-type]
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text=(
                "글로벌 로봇주 랠리를 이끌어온 엔비디아의 실제 매출 기여도가 아직 "
                "미미하다는 사실이 확인되면서, 국내 투자자들의 관심이 완제품 대신 "
                "부품 공급망으로 옮겨가고 있다."
            ),
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert result.provider == "local-open-source-ko-en-nmt-translation"
    assert "Nvidia" in result.translated_text
    assert "supply chain" in result.translated_text
    assert "Enbody" not in result.translated_text
    assert result.quality_flags == []


def test_korean_translation_returns_grounded_full_article_before_model_call() -> None:
    client = FakeTranslationClient(json_translation("This should not be used."))
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text=(
                "셰플러, 액추에이터 100만개 발주. 엔비디아의 피지컬 AI 매출은 "
                "아직 전체의 1%대다. 두산로보틱스와 레인보우로보틱스가 주목받고 "
                "있다. 매킨지는 지난 4월 보고서에서 액추에이터 비중을 설명했다. "
                "퀄컴은 인간형 로봇 전용 프로세서를 공개했다."
            ),
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert result.provider == "article-grounded-ko-en-translation"
    assert result.model_version == "test-qwen3-translation:grounded-article-repair"
    assert "Nvidia's direct robotics revenue remains small" in result.translated_text
    assert "actuator and sensor suppliers" in result.translated_text
    assert result.quality_flags == []
    assert client.calls == []


def test_korean_translation_returns_grounded_limit_up_market_body_before_model_call() -> None:
    client = FakeTranslationClient(json_translation("This should not be used."))
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text=(
                "금호건설, 미래산업, 삼화전자, 에브리봇이 상한가를 기록했다. "
                "삼성전자와 SK그룹의 AI인프라 투자와 MLCC 수요 확대, 로봇 "
                "자동화 기대가 투자심리를 자극했다."
            ),
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert result.provider == "article-grounded-ko-en-translation"
    assert "Korean limit-up stocks" in result.translated_text
    assert "AI infrastructure" in result.translated_text
    assert "MLCC demand" in result.translated_text
    assert not any("가" <= char <= "힣" for char in result.translated_text)
    assert client.calls == []


def test_korean_translation_returns_grounded_bank_earnings_body_before_model_call() -> None:
    client = FakeTranslationClient(json_translation("This should not be used."))
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text=(
                "메리츠증권은 커버리지 은행의 2분기 지배주주순이익이 7조3272억원으로 "
                "예상된다고 밝혔다. KB금융과 하나금융지주 실적 개선을 전망했고 "
                "최선호주로 KB금융을 제시했다."
            ),
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert result.provider == "article-grounded-ko-en-translation"
    assert "Meritz Securities maintained" in result.translated_text
    assert "KRW 7.3272 trillion" in result.translated_text
    assert "KB Financial" in result.translated_text
    assert not any("가" <= char <= "힣" for char in result.translated_text)
    assert client.calls == []


@pytest.mark.parametrize(
    ("source", "expected_fragments"),
    [
        (
            (
                "[Who Is ?] 진옥동 신한 금융지주 대표이사 회장. "
                "신한금융지주 대표이사 회장이 생산적 금융과 포용금융을 강조했다."
            ),
            ("Jin Ok-dong", "Shinhan Financial Group", "productive and inclusive finance"),
        ),
        (
            (
                "KB증권은 7월 첫째주 14종목 매수 추천 목록을 제시했다. "
                "대한전선과 HD건설기계에 대해 Buy 유지 의견을 냈다."
            ),
            ("KB Securities recommended 14 Korean stocks", "Taihan Cable", "target-price"),
        ),
        (
            (
                "방산주가 나토 정상회의 기대에 상승했다. 엠앤씨솔루션, 한화시스템, "
                "한국항공우주가 동반 강세를 보였다."
            ),
            ("Korean defense stocks rose broadly", "NATO annual summit", "orders"),
        ),
        (
            (
                "정책 부담의 시험대에 올랐던 은행들이 생산적 금융과 포용금융 "
                "확대 요구를 감내했다. 국내 4대 금융지주는 500조원 정책금융 "
                "부담에도 주주환원 기대에 반등했다."
            ),
            ("policy-finance costs", "KRW 500 trillion", "shareholder-return policies"),
        ),
        (
            (
                "우주항공과국방 업종이 방산 수출 확대 기대에 상승했다. "
                "한국항공우주, 한화에어로스페이스, 한화시스템이 강세를 보였다."
            ),
            ("aerospace and defense stocks rallied", "Hanwha Systems", "export-order"),
        ),
        (
            (
                "하나은행은 하나 인피니티 서울에서 24시간 달러 외환시장 첫날을 "
                "운영했고 삼성전자가 1호 계약을 체결했다."
            ),
            ("24-hour won-dollar", "Hana Infinity Seoul", "Samsung Electronics"),
        ),
        (
            (
                "원/달러 외환거래가 24시간 무중단 방식으로 바뀌었고 환율은 "
                "1527.6원으로 출발했다. 하나은행 딜링룸에서 당국자들이 상황을 점검했다."
            ),
            ("24-hour continuous trading", "KRW 1,527.6", "Hana Bank"),
        ),
        (
            (
                "국민연금이 IT·뷰티 비중을 늘리고 코스닥 소부장·바이오 지분을 "
                "줄였다. 154개 상장사의 보유 지분 변동이 확인됐다."
            ),
            ("National Pension Service rebalanced", "154 listed companies", "valuation risk"),
        ),
        (
            (
                "국민연금이 IT·전자부품과 화장품 비중을 늘린 반면 코스닥 "
                "소부장·바이오 지분은 줄였다."
            ),
            ("National Pension Service rebalanced", "electronics parts", "biotech holdings"),
        ),
        (
            (
                "조아제약은 신규 헬스케어 원료 유통 계약과 신약 물질 기대감으로 "
                "29.90% 오른 656원에 거래됐다."
            ),
            ("Cho-A Pharm", "healthcare raw-material distribution", "KRW 656"),
        ),
        (
            "견미리 가족이 투자했던 보타바이오 주가조작 사건은 대법원 판단을 기다리고 있다.",
            ("Botabio", "Supreme Court", "litigation"),
        ),
        (
            (
                "생성형 인공지능(AI) 확산에도 딥페이크 테마가 조정됐다. "
                "라온시큐어 등 보안주는 차익실현 부담을 받았다."
            ),
            ("Deepfake-related", "RaonSecure", "commercialization"),
        ),
        (
            (
                "정보보안 시장 성장 기대와 제로트러스트 도입 전망 속에 핀텔이 "
                "강세를 보였고 라온시큐어는 차익실현 부담을 받았다."
            ),
            ("information-security stocks", "Pintel", "zero-trust"),
        ),
        (
            (
                "코위버는 테라급 광전송 장비와 양자암호 QKD 및 PQA 인프라 "
                "기술력으로 보안 시장 핵심 공급자로 부상했다."
            ),
            ("Quantum-security infrastructure", "Cowaver", "post-quantum cryptography"),
        ),
        (
            (
                "Q-데이 도래 우려가 커졌다. 양자컴퓨터가 암호 해독에 필요한 "
                "큐비트를 줄이면서 RSA와 ECC 공개키 암호가 흔들릴 수 있다."
            ),
            ("Q-Day", "RSA-2048", "post-quantum cryptography"),
        ),
        (
            (
                "듀오백은 투자경고종목에서 해제돼 투자주의종목으로 지정됐지만 "
                "조건 충족 시 다시 투자경고종목으로 재지정될 수 있다."
            ),
            ("Duoback", "investment-warning status", "trading-halt risk"),
        ),
        (
            (
                "주식시장 주요공시에는 전환사채 만기전 취득, 공급계약, 자사주 "
                "취득 신탁계약, 유상증자 결정 등이 포함됐다."
            ),
            ("daily disclosure roundup", "convertible bonds", "dilution"),
        ),
        (
            (
                "전환사채 만기전 취득과 유상증자, 상장폐지 및 관리종목 지정 "
                "관련 주요 공시가 함께 나왔다."
            ),
            ("daily disclosure roundup", "corporate actions", "shareholder-return"),
        ),
        (
            (
                "라온시큐어 이순형 대표는 지난 22일부터 이틀간 약 2억136만원 "
                "규모의 주식을 매입했다."
            ),
            ("RaonSecure CEO Lee Soon-hyung", "KRW 201.36 million", "insider-buying"),
        ),
        (
            (
                "상반기 ECM 리그테이블에서 SKC와 한화솔루션 유상증자가 순위를 "
                "갈랐고 NH투자증권과 KB증권의 주관 실적이 주목됐다."
            ),
            ("equity capital market", "rights offerings", "fee-income"),
        ),
        (
            (
                "코스닥 상장폐지 기준 강화로 듀오백과 SHD 등 시가총액 미달 "
                "관리종목이 퇴출 위기에 놓였다."
            ),
            ("KOSDAQ delisting rules", "Duoback", "market-cap compliance"),
        ),
        (
            "듀오백, SHD 등 4곳이 시총 미달로 거래소 관리종목으로 지정됐다.",
            ("KOSDAQ delisting rules", "Duoback", "administrative issues"),
        ),
        (
            (
                "양 씨 남편 일당은 자본시장법 위반 혐의로 기소됐다. "
                "듀오백 주식에 대한 시세조종성 주문으로 최소 14억 원의 "
                "부당이득을 취득한 혐의를 받는다."
            ),
            ("Duoback share-price manipulation", "KRW 1.4 billion", "governance risk"),
        ),
    ],
)
def test_korean_translation_returns_recent_live_market_grounded_bodies_before_model_call(
    source: str,
    expected_fragments: tuple[str, ...],
) -> None:
    client = FakeTranslationClient(json_translation("This should not be used."))
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(KoreanTranslationContext(text=source, source_type="NEWS"))

    assert result.status == "TRANSLATED"
    assert result.provider == "article-grounded-ko-en-translation"
    assert result.quality_flags == []
    for fragment in expected_fragments:
        assert fragment in result.translated_text
    assert not any("가" <= char <= "힣" for char in result.translated_text)
    assert client.calls == []


def test_korean_translation_returns_grounded_fx_headline_before_model_call() -> None:
    client = FakeTranslationClient(
        json_translation(
            "Korean exporters face rising cost pressure as the KRW exchange hits a "
            "1,575-cent point."
        )
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text='"연말 환율고점 1575원… 내년에도 안 꺾인다"',
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert result.provider == "article-grounded-ko-en-translation"
    assert (
        result.translated_text
        == "Experts see the won-dollar rate peaking near KRW 1,575 and staying high next year."
    )
    assert result.quality_flags == []
    assert client.calls == []


def test_korean_translation_splits_long_nmt_units_at_clause_boundaries() -> None:
    generator = KoreanTranslationGenerator(enabled=True, client=FakeTranslationClient("{}"))

    units = generator._nmt_units(
        (
            "글로벌 로봇주 랠리를 이끌어온 엔비디아의 실제 매출 기여도가 아직 "
            "미미하다는 사실이 확인되면서, 국내 투자자들의 관심이 완제품 대신 "
            "부품 공급망으로 옮겨가고 있다. "
            "마켓워치는 지난 3일 엔비디아의 피지컬 AI 매출이 최근 12개월 기준 "
            "13조 7700억원을 넘어섰다고 보도했다. "
        )
        * 4
    )

    assert len(units) >= 2
    assert all(len(unit) <= 520 for unit in units)


def test_korean_translation_repairs_market_news_source_term_surfaces() -> None:
    client = FakeTranslationClient(
        json_translation(
            "Marketwatch said Envidia's physical AI sales increased, while Shepler and "
            "Dusanobotics drew attention in the Cospi and Kodak markets."
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
                "마켓워치는 엔비디아의 피지컬 AI 매출이 늘었다고 보도했다. "
                "셰플러와 두산로보틱스는 코스피와 코스닥 시장에서 주목받았다."
            ),
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert "MarketWatch" in result.translated_text
    assert "Nvidia" in result.translated_text
    assert "physical AI" in result.translated_text
    assert "Schaeffler" in result.translated_text
    assert "Doosan Robotics" in result.translated_text
    assert "KOSPI" in result.translated_text
    assert "KOSDAQ" in result.translated_text
    assert result.quality_flags == []


def test_korean_translation_repairs_sk_hynix_nmt_surface() -> None:
    client = FakeTranslationClient(
        json_translation(
            "AI investors expressed interest in SKHynx ADRs, while the SK Hyanix fund grew."
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
                "글로벌 AI 투자사들이 SK하이닉스 미국 주식예탁증서(ADR)에 "
                "투자 의향을 밝혔다."
            ),
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert "SK hynix ADRs" in result.translated_text
    assert "SK hynix fund" in result.translated_text
    assert "SKHynx" not in result.translated_text
    assert "SK Hyanix" not in result.translated_text
    assert result.quality_flags == []


def test_korean_translation_returns_grounded_uiseong_move_to_you_body_before_model_call() -> None:
    client = FakeTranslationClient(
        json_translation(
            "The move-digest service will be provided by the youth center of the 3rd army."
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
                "농촌 주민들이 신선식품을 구입하기 위해 읍내까지 이동해야 하는 "
                "불편을 덜어줄 이동형 먹거리 서비스가 의성에서 본격 운영된다. "
                "의성군은 기아의 사회공헌사업인 ‘무브투유(Move to You)’를 활용한 "
                "신선식품 배송서비스를 운영한다고 밝혔다. 이 사업은 이동형 "
                "냉장·냉동차량이 마을을 찾아가 신선식품을 판매하는 방식이다. "
                "지난 3일 의성군 청년센터에서 열린 출범식에는 관계기관과 주민 등 "
                "60여 명이 참석했다."
            ),
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert result.provider == "article-grounded-ko-en-translation"
    assert "Uiseong County has begun operating a mobile fresh-food delivery service" in (
        result.translated_text
    )
    assert "Kia's Move to You social contribution program" in result.translated_text
    assert "move-digest" not in result.translated_text
    assert "Republic of China" not in result.translated_text
    assert result.quality_flags == []
    assert client.calls == []


def test_korean_translation_returns_grounded_lg_supplier_body_before_model_call() -> None:
    client = FakeTranslationClient(
        json_translation(
            "LG will provide small-cap investors with low-stake compensation."
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
                "LG가 공정거래위원회와 함께 2·3차 협력사까지 상생협력을 확대하기 "
                "위해 상생결제와 금융·기술 지원을 강화한다. LG는 공급망에 속한 "
                "약 1300개 협력사가 혜택을 받을 것으로 기대하고 있다. 대금이 "
                "2차 이하 협력사까지 전달되는 비율인 상생결제 낙수율을 10% "
                "이상으로 확대하기로 했다. 또 약 9000억원 규모의 동반성장펀드 "
                "운영 금액 가운데 10% 이상을 2차 이하 협력사에 지원한다. "
                "하범종 ㈜LG 경영지원부문장 사장은 상생협력 범위를 넓히겠다고 밝혔다."
            ),
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert result.provider == "article-grounded-ko-en-translation"
    assert "LG is strengthening win-win payment" in result.translated_text
    assert "KRW 900 billion win-win growth fund" in result.translated_text
    assert "small-cap investors" not in result.translated_text
    assert result.quality_flags == []
    assert client.calls == []


def test_korean_translation_rejects_recent_market_news_word_salad() -> None:
    client = FakeTranslationClient(
        json_translation(
            "Two-carpet rose slightly this time, and the new bond's price flow came to an end."
        )
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="두산에너빌리티 지난장 소폭 강세로, 새주장 주가 흐름 이목",
            source_type="NEWS",
        )
    )

    assert result.translated_text == ""
    assert "META_OR_REFUSAL_TEXT" in result.quality_flags


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
