import json
import re
import urllib.error
import urllib.request
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
    QwenHttpKoreanTranslationClient,
)
from hannah_montana_ai.services.model import ModelArtifactNotFoundError


class FakeTranslationClient:
    def __init__(self, output: str) -> None:
        self.output = output
        self.calls: list[list[dict[str, str]]] = []
        self.max_tokens_calls: list[int] = []

    def generate(self, messages: list[dict[str, str]], max_tokens: int) -> str:
        self.calls.append(messages)
        self.max_tokens_calls.append(max_tokens)
        return self.output


class SequenceTranslationClient:
    def __init__(self, outputs: list[str]) -> None:
        self.outputs = outputs
        self.calls: list[list[dict[str, str]]] = []
        self.max_tokens_calls: list[int] = []

    def generate(self, messages: list[dict[str, str]], max_tokens: int) -> str:
        self.calls.append(messages)
        self.max_tokens_calls.append(max_tokens)
        if len(self.calls) <= len(self.outputs):
            return self.outputs[len(self.calls) - 1]
        return self.outputs[-1]


class FakeHttpResponse:
    def __enter__(self) -> "FakeHttpResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return b'{"choices":[{"message":{"content":"{\\"translation\\":\\"translated\\"}"}}]}'


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


def test_korean_translation_batches_alert_fields_in_one_generation_call() -> None:
    translated = """
        <<<1>>>
        Samsung Electronics reports stronger earnings.
        <<<2>>>
        Earnings improved as semiconductor demand recovered.
        <<<3>>>
        Samsung Electronics said operating profit increased as semiconductor demand recovered.
        """.strip()
    client = FakeTranslationClient(json.dumps({"translation": translated}))
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="fake-qwen",
        rule_based_repairs_enabled=False,
    )

    results = generator.translate_alert_fields(
        {
            "TITLE": KoreanTranslationContext(
                text="삼성전자 실적 개선",
                title="삼성전자 실적 개선",
            ),
            "SUMMARY": KoreanTranslationContext(
                text="반도체 수요 회복으로 실적이 개선됐다.",
                title="삼성전자 실적 개선",
            ),
            "CONTENT": KoreanTranslationContext(
                text="삼성전자는 반도체 수요 회복으로 영업이익이 증가했다고 밝혔다.",
                title="삼성전자 실적 개선",
            ),
        }
    )

    assert results is not None
    assert len(client.calls) == 1
    assert results["TITLE"].translated_text.startswith("Samsung Electronics")
    assert results["SUMMARY"].translated_text.startswith("Earnings improved")
    assert results["CONTENT"].translated_text.endswith("recovered.")


def test_korean_translation_rejects_incomplete_field_inside_valid_composite() -> None:
    long_english = "The filing contains verified transaction details. " * 18
    translated = f"<<<1>>>\n{long_english}\n<<<2>>>\n{long_english}\n<<<3>>>\nShareholding changed."
    client = FakeTranslationClient(json.dumps({"translation": translated}))
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="fake-qwen",
        rule_based_repairs_enabled=False,
    )

    results = generator.translate_alert_fields(
        {
            "TITLE": KoreanTranslationContext(text="주식 보유 변동 공시"),
            "SUMMARY": KoreanTranslationContext(text="임원의 주식 보유 수량이 변경됐다."),
            "CONTENT": KoreanTranslationContext(
                text="임원의 주식 보유 수량과 거래 내역이 변경됐다. " * 60,
            ),
        }
    )

    assert results is None


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


def test_korean_translation_does_not_invent_a_month_for_a_bare_korean_day() -> None:
    client = FakeTranslationClient(
        json_translation("SK hynix said on October 10 that it would expand AI memory investment.")
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
        rule_based_repairs_enabled=False,
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="SK하이닉스는 10일 AI 메모리 투자를 확대한다고 밝혔다.",
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert "October" not in result.translated_text
    assert "on the 10th" in result.translated_text


def test_korean_translation_local_glossary_mode_uses_local_llm_client_for_article_body() -> None:
    client = FakeTranslationClient(
        json_translation(
            "According to the Korea Exchange, KOSPI fell by 409.52 points from the previous "
            "session. KOSDAQ closed at 785.00 after losing 46.23 points. Investors should "
            "monitor foreign flows and semiconductor earnings."
        )
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        local_glossary_enabled=True,
        model_name="local-llm:Qwen3-4B-GGUF-Q4",
    )
    source = (
        "한국거래소에 따르면 코스피는 전 거래일보다 409.52포인트 하락했다. "
        "코스닥은 전일 대비 46.23포인트 하락한 785.00으로 마감했다. "
        "투자자들은 외국인 수급과 반도체 업종 실적을 확인해야 한다."
    )

    result = generator.translate(KoreanTranslationContext(text=source, source_type="NEWS"))

    assert result.provider == "local-open-source-qwen3-translation"
    assert result.model_version == "local-llm:Qwen3-4B-GGUF-Q4"
    assert result.status == "TRANSLATED"
    assert "KOSPI fell by 409.52 points" in result.translated_text
    assert "foreign flows and semiconductor earnings" in result.translated_text


def test_korean_translation_accepts_long_body_with_missing_glossary_surface() -> None:
    client = FakeTranslationClient(
        json_translation(
            "Samsung Electronics and SK hynix saw increased short selling as foreign "
            "investors weighed semiconductor profit-taking risk. The report said investors "
            "were watching memory-cycle momentum and market liquidity. The article also "
            "noted that institutional flows could affect large-cap chip shares over the "
            "next session."
        )
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
        rule_based_repairs_enabled=False,
    )
    source = (
        "삼성전자와 SK하이닉스 등 반도체 대장주에 공매도가 늘었다. "
        "외국인 투자자들은 메모리 업황 개선 기대와 차익 실현 부담을 함께 보고 있다. "
        "증권가에서는 기관 수급과 시장 유동성이 다음 거래일 대형 반도체주의 흐름에 "
        "영향을 줄 수 있다고 분석했다. "
    ) * 4

    result = generator.translate(
        KoreanTranslationContext(
            text=source,
            source_type="NEWS",
            glossary_terms=[
                FinancialGlossaryTerm(
                    source_term="대장주",
                    normalized_term="대장주",
                    english_term="bellwether stock",
                    category="market_slang",
                ),
            ],
        )
    )

    assert result.status == "TRANSLATED"
    assert result.provider == "local-open-source-qwen3-translation"
    assert "samsung electronics and sk hynix" in result.translated_text.lower()
    assert result.quality_flags == []
    assert client.max_tokens_calls
    assert max(client.max_tokens_calls) <= 640


def test_korean_translation_long_body_bounds_full_article_retry_when_chunks_fail() -> None:
    source = (
        "삼성전자는 AI 서버 투자 확대로 반도체 실적 개선 기대가 커졌다. "
        "증권가는 HBM 공급 확대와 메모리 가격 반등을 주가 변수로 제시했다. "
        "투자자는 외국인 수급과 다음 분기 영업이익 전망을 확인해야 한다. "
    ) * 8
    client = FakeTranslationClient(json_translation("삼성전자는 반도체 실적을 개선했다."))
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
        rule_based_repairs_enabled=False,
        max_tokens=2048,
    )

    result = generator.translate(KoreanTranslationContext(text=source, source_type="NEWS"))

    assert result.status == "SOURCE_LANGUAGE_FALLBACK"
    assert "HANGUL_REMAINS" in result.quality_flags
    assert "MISSING_TRANSLATED_CHUNK" in result.quality_flags
    assert len(client.calls) <= len(generator._chunks(source)) * 3 + 3
    assert max(client.max_tokens_calls) <= 2048


def test_korean_translation_rejects_body_when_qwen_quality_gate_fails() -> None:
    client = FakeTranslationClient(json_translation("LG화학은 반도체 소재 사업을 확대했다."))
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
        rule_based_repairs_enabled=False,
    )

    result = generator.translate(
        KoreanTranslationContext(
            text=(
                "LG화학은 AI 투자 확대와 고대역폭 메모리 수요 증가로 "
                "반도체 소재 사업 확대를 본격화하며 글로벌 고객사 공급을 늘려 "
                "전자소재 매출 기반을 강화할 계획이라고 밝혔다."
            ),
            source_type="NEWS",
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

    assert result.status == "SOURCE_LANGUAGE_FALLBACK"
    assert result.provider == "source-language-fallback"
    assert result.translated_text == ""
    assert "HANGUL_REMAINS" in result.quality_flags


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "반도체 고점론·중동 불안에...코스피 7,200선 '털썩'",
            "KOSPI falls to the 7,200 level",
        ),
        (
            "반도체 불안에 중동 긴장까지…증시 ‘흔들’",
            "Korean stocks are shaken by semiconductor concerns",
        ),
    ],
)
def test_korean_translation_repairs_market_plunge_headlines(source: str, expected: str) -> None:
    generator = KoreanTranslationGenerator.from_settings(
        Settings(korean_translation_generation_mode="local_glossary")
    )

    result = generator.translate(KoreanTranslationContext(text=source, source_type="NEWS"))

    assert result.status == "TRANSLATED"
    assert result.provider == "article-grounded-ko-en-translation"
    assert expected in result.translated_text
    assert "..." not in result.translated_text
    assert "·" not in result.translated_text
    assert not any("가" <= char <= "힣" for char in result.translated_text)


def test_korean_translation_local_llm_requires_trained_adapter(tmp_path: Path) -> None:
    with pytest.raises(ModelArtifactNotFoundError):
        KoreanTranslationGenerator.from_settings(
            Settings(
                korean_translation_generation_mode="local_llm",
                korean_translation_llm_endpoint="",
                korean_translation_mlx_adapter_path=tmp_path / "missing-translation-lora",
            )
        )


def test_korean_translation_local_llm_settings_with_endpoint_use_qwen_http_client() -> None:
    settings = Settings(
        korean_translation_generation_mode="local_llm",
        korean_translation_llm_endpoint="http://127.0.0.1:18081",
        korean_translation_llm_model="Qwen3-4B-GGUF-Q4",
    )

    generator = KoreanTranslationGenerator.from_settings(settings)

    assert generator._enabled is True
    assert isinstance(generator._client, QwenHttpKoreanTranslationClient)
    assert generator._model_name == "local-llm:Qwen3-4B-GGUF-Q4"
    assert generator._rule_based_repairs_enabled is False


def test_qwen_http_client_retries_transient_service_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    responses: list[object] = [
        urllib.error.HTTPError("http://127.0.0.1", 503, "loading", {}, None),
        urllib.error.URLError("temporarily unavailable"),
        FakeHttpResponse(),
    ]
    sleeps: list[float] = []

    def fake_urlopen(*_args: object, **_kwargs: object) -> FakeHttpResponse:
        response = responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(
        "hannah_montana_ai.services.korean_translation_generator.time.sleep",
        sleeps.append,
    )
    client = QwenHttpKoreanTranslationClient("http://127.0.0.1:18081", "qwen", 1.0)

    result = client.generate([{"role": "user", "content": "translate"}], 64)

    assert result == '{"translation":"translated"}'
    assert sleeps == [1.0, 2.0]


def test_qwen_http_client_does_not_duplicate_timed_out_inference(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempts = 0

    def fake_urlopen(*_args: object, **_kwargs: object) -> FakeHttpResponse:
        nonlocal attempts
        attempts += 1
        raise TimeoutError("timed out")

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    client = QwenHttpKoreanTranslationClient("http://127.0.0.1:18081", "qwen", 1.0)

    with pytest.raises(TimeoutError):
        client.generate([{"role": "user", "content": "translate"}], 64)

    assert attempts == 1


def test_korean_translation_local_llm_does_not_mask_qwen_failure_with_grounded_repair() -> None:
    client = FakeTranslationClient(json_translation("코스피는 하락했다."))
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
        rule_based_repairs_enabled=False,
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="반도체 고점론·중동 불안에...코스피 7,200선 '털썩'",
            source_type="NEWS",
        )
    )

    assert result.status == "SOURCE_LANGUAGE_FALLBACK"
    assert result.provider == "source-language-fallback"
    assert result.translated_text == ""
    assert "HANGUL_REMAINS" in result.quality_flags


def test_korean_translation_retries_residual_cjk_fragment() -> None:
    client = SequenceTranslationClient(
        [
            json_translation("The company will acquire 14,200,000 普通 shares."),
            json_translation("The company will acquire 14,200,000 common shares."),
        ]
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
        rule_based_repairs_enabled=False,
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="회사는 보통주 14,200,000주를 취득할 예정이다.",
            source_type="DISCLOSURE",
        )
    )

    assert result.status == "TRANSLATED"
    assert result.translated_text == "The company will acquire 14,200,000 common shares."
    assert len(client.calls) == 2


@pytest.mark.parametrize(
    ("source", "translated", "expected"),
    [
        (
            "하나금융지주 밸류에이션 매력 여전",
            "Hana Financial Group's valueation remains attractive.",
            "Hana Financial Group's valuation remains attractive.",
        ),
        (
            "알짜 현대홈쇼핑 상장폐지",
            "Alza Hyundai Home Shopping delisting.",
            "High-value Hyundai Home Shopping delisting.",
        ),
        (
            "목표가는 19% 하향-유진",
            "The target price was cut 19% - Yu Jin.",
            "The target price was cut 19% - Eugene Investment & Securities.",
        ),
        (
            "SK하이닉스 ADR 훈풍에 코스피 급등",
            "SKHynix ADR windmill lifted KOSPI. The headline also references SK and 3%.",
            "SK hynix ADR tailwind lifted KOSPI.",
        ),
        (
            "코스피 2.5% 상승해 7,400선 회복…매수 사이드카",
            "KOSPI rises 2.5% to recover above 7,400... Buy-side car",
            "KOSPI rises 2.5% to recover above 7,400... Buy-side trading curb",
        ),
        (
            "[운용 NOW] KB자산운용·신한자산운용",
            "[Operation NOW] KB Asset Management · Shinhan Asset Management",
            "[Asset Management NOW] KB Asset Management · Shinhan Asset Management",
        ),
    ],
)
def test_korean_translation_repairs_recurring_financial_surface_errors(
    source: str,
    translated: str,
    expected: str,
) -> None:
    generator = KoreanTranslationGenerator(enabled=False)

    assert generator._repair_common_translation_surfaces(source, translated) == expected


def test_korean_translation_removes_generated_numeric_appendix_after_surface_repair() -> None:
    client = FakeTranslationClient(
        json_translation(
            "LG Uplus targets KRW 1 trillion in annual operating profit "
            "after strong second-quarter results."
        )
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="fake-qwen",
        rule_based_repairs_enabled=False,
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="LG유플러스, 2분기 호실적 넘어 연 영업이익 1조 정조준",
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert "headline also references" not in result.translated_text.lower()


def test_korean_translation_removes_leading_generated_appendix_without_losing_body() -> None:
    generator = KoreanTranslationGenerator(enabled=False)

    result = generator._remove_generated_surface_appendix(
        ". The headline also references 25 won. KNN approved the financial statements "
        "and declared a cash dividend of KRW 25 per share."
    )

    assert result == (
        "KNN approved the financial statements and declared a cash dividend "
        "of KRW 25 per share."
    )


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
        rule_based_repairs_enabled=False,
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


def test_korean_translation_retries_qwen_semantic_mismatch_chunk() -> None:
    client = SequenceTranslationClient(
        [
            json_translation("Samsung Electronics said 2-month operating profit improved."),
            json_translation("Samsung Electronics said second-quarter operating profit improved."),
        ]
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
        rule_based_repairs_enabled=False,
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="삼성전자는 2분기 영업이익이 개선됐다고 밝혔다.",
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert "second-quarter operating profit" in result.translated_text
    assert result.quality_flags == []
    assert len(client.calls) == 2


def test_korean_translation_accepts_plain_qwen_english_output() -> None:
    client = FakeTranslationClient(
        "KOSPI fell sharply as semiconductor shares weakened and foreign selling widened."
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
        rule_based_repairs_enabled=False,
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="코스피는 반도체주 약세와 외국인 매도 확대에 급락했다.",
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert result.provider == "local-open-source-qwen3-translation"
    assert result.quality_flags == []
    assert "KOSPI fell sharply" in result.translated_text


def test_korean_translation_strips_qwen_thinking_before_json_parse() -> None:
    client = FakeTranslationClient(
        '<think>요청을 번역한다.</think>\n'
        '{"translation":"KOSPI rebounded as chip stocks recovered."}'
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="코스피는 반도체주 회복에 반등했다.",
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert result.quality_flags == []
    assert result.translated_text == "KOSPI rebounded as chip stocks recovered."


def test_korean_translation_recovers_malformed_qwen_json_string() -> None:
    client = FakeTranslationClient(
        '{"translation":"KOSPI fell after Samsung Electronics called the plan '
        '"shareholder-friendly".\\nForeign selling widened."}'
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="삼성전자가 주주친화 계획을 언급한 뒤 코스피가 하락했고 외국인 매도가 확대됐다.",
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert result.quality_flags == []
    assert "shareholder-friendly" in result.translated_text
    assert "Foreign selling widened" in result.translated_text


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


def test_disclosure_body_acceptance_rejects_summary_and_missing_numbers() -> None:
    generator = KoreanTranslationGenerator(enabled=False)

    flags = generator._body_acceptance_quality_flags(
        "공시 본문 " * 100,
        ["POSSIBLE_SUMMARY_INSTEAD_OF_TRANSLATION", "SOURCE_NUMBER_MISSING"],
        "DISCLOSURE",
    )

    assert flags == ["POSSIBLE_SUMMARY_INSTEAD_OF_TRANSLATION", "SOURCE_NUMBER_MISSING"]


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


def test_korean_translation_injects_required_market_glossary_without_request_terms() -> None:
    client = FakeTranslationClient(
        json_translation(
            "KOSDAQ circulation trading is becoming more likely as the dominance of Samsung "
            "Electronics and SK Hynix eases. Brokerages said that if large semiconductor "
            "stocks remain range-bound in the second half, investment funds could move into "
            "small and mid-cap stocks and growth stocks. Investors should check supply-demand "
            "changes together with increases in trading value."
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
                "코스닥 순환매 가능성이 커지며 삼성전자와 SK하이닉스 독주가 완화됐다. "
                "증권가는 하반기 대형 반도체주가 박스권에 머물면 투자자금이 중소형주와 "
                "성장주로 이동할 수 있다고 봤다. 투자자는 수급 변화와 거래대금 증가를 "
                "함께 확인해야 한다."
            ),
            source_type="NEWS",
        )
    )

    payload = json.loads(client.calls[0][1]["content"])
    assert {
        "source_term": "코스닥",
        "normalized_term": "코스닥",
        "english_term": "KOSDAQ",
        "category": "market",
    } in payload["glossary"]
    assert result.status == "TRANSLATED"
    assert result.quality_flags == []


def test_korean_translation_repairs_market_surface_paraphrases() -> None:
    client = FakeTranslationClient(
        json_translation("The Korean stock market fell while the tech-heavy market also weakened.")
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="코스피와 코스닥은 투자심리 악화로 동반 하락했다.",
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert "KOSPI fell" in result.translated_text
    assert "KOSDAQ also weakened" in result.translated_text
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


def test_korean_translation_rejects_repetitive_disclosure_table_summary() -> None:
    repeated = (
        "The disclosure table explains treasury-share disposal details for eligible employees."
    )
    client = FakeTranslationClient(json_translation(" ".join([repeated, repeated, repeated])))
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
        rule_based_repairs_enabled=False,
    )
    source = " ".join(
        [
            "삼성전자 공시 표 본문",
            "2026-07-06",
            "대상주식수 1,083,434주",
            "발행주식총수 5,846,278,608주",
            "예정금액 78,000,000,000원",
            "이사회결의일 2026-07-06",
            "직원 개인별 계좌 입고",
        ]
        * 12
    )

    result = generator.translate(
        KoreanTranslationContext(
            text=source,
            source_type="DISCLOSURE",
        )
    )

    assert result.status == "SOURCE_LANGUAGE_FALLBACK"
    assert result.translated_text == ""


def test_korean_translation_rejects_short_disclosure_table_number_omission() -> None:
    client = FakeTranslationClient(
        json_translation("Samsung Electronics filed a short disclosure table for investors.")
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
        rule_based_repairs_enabled=False,
    )

    result = generator.translate(
        KoreanTranslationContext(
            text=(
                "삼성전자 공시 2026-07-06 1,083,434주 5,846,278,608주 "
                "78,000,000,000원 0.019% 10:00 2026-07-30"
            ),
            source_type="DISCLOSURE",
        )
    )

    assert result.status == "SOURCE_LANGUAGE_FALLBACK"
    assert result.translated_text == ""
    assert "SOURCE_NUMBER_MISSING" in result.quality_flags


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


def test_korean_translation_rejects_unsupported_year_even_when_source_has_other_numbers() -> None:
    client = FakeTranslationClient(
        json_translation(
            "On Nov. 9, 2023, foreign investors sold Samsung Electronics as fund "
            "allocation rules forced mechanical selling."
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
                "9일 구독자 55만1000명을 보유한 채널에서 전문가는 외국인 매도가 "
                "해외 펀드의 자산 배분 규정에 따른 기계적 매도라고 설명했다."
            ),
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
    assert "UNSUPPORTED_YEAR_FACT" in result.quality_flags


def test_korean_translation_repairs_yum_director_surface() -> None:
    client = FakeTranslationClient(
        json_translation(
            "Yam I said foreign funds must reduce the stock weight when Samsung "
            "Electronics exceeds limits."
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
                "염 이사는 삼성전자 비중이 한도를 넘으면 외국계 펀드가 "
                "비중을 줄여야 한다고 말했다."
            ),
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

    assert result.status == "TRANSLATED"
    assert "Yum said foreign funds" in result.translated_text
    assert "Yam I" not in result.translated_text


def test_korean_translation_rejects_qwen_romanized_korean_word_salad() -> None:
    client = FakeTranslationClient(
        json_translation(
            "Kang Nam-Go's 4J revenue lingers, pab-wo-yeon's bellwether stock faces a rebound."
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


def test_translation_accepts_most_numbers_in_dense_disclosure() -> None:
    generator = KoreanTranslationGenerator(enabled=False)
    source = "공시일 2026-06-18, 행사일 2026-06-24, 1분기, 6월 24일, 2026-04-24"
    translated = (
        "The filing date is 2026-06-18, the event is on 2026-06-24, "
        "and it covers the first quarter and June 24."
    )

    assert generator._has_missing_source_number(source, translated) is False


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


def test_korean_translation_canonicalizes_ir_disclosure_title_without_request_glossary() -> None:
    client = FakeTranslationClient(json_translation("기업설명회 개최"))
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
        rule_based_repairs_enabled=False,
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="삼성전자/기업설명회(IR)개최(안내공시)/2026.07.07",
            source_type="DISCLOSURE",
        )
    )

    assert result.status == "TRANSLATED"
    assert (
        result.translated_text
        == "Samsung Electronics / Investor relations conference notice / 2026.07.07"
    )
    assert result.quality_flags == []
    assert client.calls == []


def test_korean_translation_structures_dart_earnings_disclosure_without_hangul() -> None:
    client = FakeTranslationClient(json_translation("삼성전자 실적기간 당기실적"))
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            source_type="DISCLOSURE",
            text=(
                "삼성전자/연결재무제표기준영업(잠정)실적(공정공시)/2026.07.08\n"
                "실적기간 당기실적 2026-04-01 ~ 2026-06-30\n"
                "단위 조원, %\n"
                "매출액 당해실적 171.00 133.87 27.74 - 74.57 129.31\n"
                "영업이익 당해실적 89.40 57.23 56.21 - 4.68 1,810.26\n"
                "상기 실적은 잠정치로 외부감사인의 감사결과에 따라 변경될 수 있습니다."
            ),
        )
    )

    assert result.status == "TRANSLATED"
    assert result.provider == "structured-dart-disclosure-ko-en-translation"
    assert result.quality_flags == []
    assert not re.search("[가-힣]", result.translated_text)
    assert "Samsung Electronics disclosed preliminary consolidated operating results" in (
        result.translated_text
    )
    assert "2026-04-01 ~ 2026-06-30" in result.translated_text
    assert "Sales were 171.00" in result.translated_text
    assert "Operating profit was 89.40" in result.translated_text
    assert not client.calls


def test_korean_translation_structures_dart_ir_disclosure_without_hangul() -> None:
    client = FakeTranslationClient(json_translation("기업설명회 개최"))
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            source_type="DISCLOSURE",
            text=(
                "삼성전자/기업설명회(IR) 개최(안내공시)/2026.07.10\n"
                "일시 2026-07-30 10:00\n"
                "개최목적 2분기 실적발표 및 질의응답\n"
                "주요설명회내용 2분기 실적 및 질의응답\n"
                "참가대상자 국내외 기관투자자, 애널리스트 및 언론"
            ),
        )
    )

    assert result.status == "TRANSLATED"
    assert result.provider == "structured-dart-disclosure-ko-en-translation"
    assert result.quality_flags == []
    assert not re.search("[가-힣]", result.translated_text)
    assert "Samsung Electronics announced an investor relations conference notice" in (
        result.translated_text
    )
    assert "2026-07-30 10:00" in result.translated_text
    assert "second-quarter" in result.translated_text
    assert "Q&A" in result.translated_text
    assert not client.calls


def test_korean_translation_structures_treasury_share_disposal_without_hangul() -> None:
    client = FakeTranslationClient(json_translation("한국거래소 자기주식 처분"))
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            source_type="DISCLOSURE",
            text=(
                "삼성전자 주요사항보고서(자기주식처분결정)\n"
                "처분 대상 주식가격(원)은 이사회 결의일 전일(2026년 7월 6일) "
                "한국거래소 종가 기준임. 실제 처분금액은 처분시점 주가에 따라 "
                "변동될 수 있음. 처분방법은 당사의 자기주식 계좌에서 대상 직원의 "
                "개인별 계좌로 입고 예정임. 처분상대방별 회사 또는 최대주주와의 "
                "관계 - 회사 직원. 처분상대방 선정사유 - 2026년 성과급 노사합의에 "
                "따른 자기주식 지급대상. 처분상대방별 처분주식수(주) - 보통주식 "
                "1,083,434주. 발행주식총수(보통주 5,846,278,608주)의 0.019% 수준이며 "
                "주식가치 희석효과는 미미할 것으로 예상."
            ),
        )
    )

    assert result.status == "TRANSLATED"
    assert result.provider == "structured-dart-disclosure-ko-en-translation"
    assert result.quality_flags == []
    assert not re.search("[가-힣]", result.translated_text)
    assert result.translated_text.startswith("Samsung Electronics disclosed material event report")
    assert "1,083,434 common shares" in result.translated_text
    assert "0.019%" in result.translated_text
    assert "5,846,278,608 issued common shares" in result.translated_text
    assert "Korea Exchange disclosed" not in result.translated_text
    assert not client.calls


def test_korean_translation_structures_major_shareholder_ownership_report_in_local_llm_mode() -> (
    None
):
    client = FakeTranslationClient(json_translation("임원 주요주주 소유상황보고서"))
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
        rule_based_repairs_enabled=False,
    )

    result = generator.translate(
        KoreanTranslationContext(
            source_type="DISCLOSURE",
            text=(
                "삼성전자/임원ㆍ주요주주 특정증권등 소유상황보고서/2026.07.09\n"
                "보고의무발생일 2026년 07월 09일\n"
                "발행회사에 관한 사항 회사명 삼성전자주식회사\n"
                "보고자에 관한 사항 성명 홍길동\n"
                "특정증권등의 소유상황 보통주 12,000주"
            ),
        )
    )

    assert result.status == "TRANSLATED"
    assert result.provider == "structured-dart-disclosure-ko-en-translation"
    assert result.quality_flags == []
    assert not re.search("[가-힣]", result.translated_text)
    assert (
        "Samsung Electronics disclosed report on ownership of specified securities "
        "by officers and major shareholders"
    ) in result.translated_text
    assert "2026.07.09" in result.translated_text
    assert not client.calls


def test_korean_translation_does_not_replace_long_disclosure_body_with_generic_summary() -> None:
    client = SequenceTranslationClient(
        [
            json_translation(
                "Samsung Electronics filed a report on ownership of specified securities by "
                "officers and major shareholders on 2026.07.09. The filing date was "
                "2026-07-09. The body listed 12,000 common shares."
            ),
            json_translation(
                "The filer described changes in ownership, the purpose of the holding, "
                "and the reporting obligations in the body."
            ),
        ]
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
        rule_based_repairs_enabled=False,
    )
    source = (
        "삼성전자/임원ㆍ주요주주 특정증권등 소유상황보고서/2026.07.09\n"
        "보고의무발생일 2026년 07월 09일\n"
        "발행회사에 관한 사항 회사명 삼성전자주식회사\n"
        "특정증권등의 소유상황 보통주 12,000주\n"
        + "보고자는 특정증권 등의 변동 내역과 보유 목적을 본문에 기재했다. "
        * 20
    )

    result = generator.translate(
        KoreanTranslationContext(
            source_type="DISCLOSURE",
            text=source,
        )
    )

    assert result.status == "SOURCE_LANGUAGE_FALLBACK"
    assert result.translated_text == ""
    assert client.calls


def test_korean_translation_does_not_structure_long_disclosure_body_with_title_prefix() -> None:
    client = FakeTranslationClient(
        json_translation(
            "Samsung Electronics filed a full ownership report for officers and major "
            "shareholders. The body includes reporter information, filing dates, ownership "
            "details, share counts, and reporting obligations for investors."
        )
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
        rule_based_repairs_enabled=False,
    )
    source = (
        "삼성전자 임원ㆍ주요주주 특정증권등 소유상황보고서\n"
        "보고의무발생일 : 2026년 07월 09일 보고서작성기준일 : 2026년 07월 09일\n"
        "보고자에 관한 사항 성명 신경섭 주소 서울특별시 특정증권등의 소유상황 "
        "보통주식 1,083,434주 발행주식총수 5,846,278,608주 "
        + "보고자는 특정증권 등의 취득, 처분, 보유 목적, 변동 내역과 제출 의무를 본문에 기재했다. "
        * 18
    )

    result = generator.translate(
        KoreanTranslationContext(
            source_type="DISCLOSURE",
            text=source,
        )
    )

    assert len(source) > 700
    assert result.status == "SOURCE_LANGUAGE_FALLBACK"
    assert result.translated_text == ""
    assert client.calls


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


def test_korean_translation_repairs_foreign_currency_for_implied_large_won_amount() -> None:
    client = FakeTranslationClient(
        json_translation("SK hynix will use 40 trillion yen for aggressive investment.")
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
        rule_based_repairs_enabled=False,
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="SK하이닉스, 나스닥 입성…40조 실탄으로 광폭 투자",
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert "40 trillion won" in result.translated_text
    assert "yen" not in result.translated_text.lower()


def test_korean_translation_repairs_korean_large_unit_amount_values() -> None:
    client = FakeTranslationClient(
        json_translation(
            "The share price was 224.9751 won versus 218.6 thousand won. "
            "The offering raised 2.657 billion dollars and 40.23 trillion won."
        )
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
        rule_based_repairs_enabled=False,
    )

    result = generator.translate(
        KoreanTranslationContext(
            text=(
                "신주 발행가는 주당 224만 9751원으로, "
                "전일 종가 218만 6000원보다 높다. "
                "총 265억 700만 달러, 약 40조 230억원을 조달한다."
            ),
            source_type="NEWS",
        )
    )

    assert "KRW 2.249751 million" in result.translated_text
    assert "KRW 2.186 million" in result.translated_text
    assert "$26.507 billion" in result.translated_text
    assert "KRW 40.023 trillion" in result.translated_text
    assert "224.9751 won" not in result.translated_text
    assert "2.657 billion dollars" not in result.translated_text


def test_korean_translation_preserves_decimal_currency_amount() -> None:
    generator = KoreanTranslationGenerator(enabled=False)

    repaired = generator._repair_korean_currency_amounts(
        "원달러 환율은 1,527.6원이다.",
        "The won-dollar exchange rate is 1,527 won.",
    )

    assert repaired == "The won-dollar exchange rate is KRW 1,527.6."


def test_korean_translation_removes_news_boilerplate_before_chunking() -> None:
    generator = KoreanTranslationGenerator(enabled=False)

    normalized = generator._normalize_text(
        "잠깐! 현재 Internet Explorer 8이하 버전을 이용중이십니다. "
        "최신 브라우저(Browser) 사용을 권장드립니다! "
        "[투데이에너지 신영균 기자] LG화학이 반도체 소재 사업을 확대하고 있다. "
        "googletag.cmd.push(function(){googletag.display('div-gpt-ad-1');}); "
        "dschoi@fnnews.com 최두선 기자 #삼성전자 #SK하이닉스 "
        "※ 저작권자 ⓒ 파이낸셜뉴스, 무단전재-재배포 금지"
    )

    assert "Internet Explorer" not in normalized
    assert "최신 브라우저" not in normalized
    assert "기자" not in normalized
    assert "googletag" not in normalized
    assert "fnnews.com" not in normalized
    assert "저작권자" not in normalized
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


def test_korean_translation_allows_title_case_romanized_korean_person_names() -> None:
    client = FakeTranslationClient(
        json_translation(
            "Professor Ryu Sang-yeon said single-stock leveraged products increased "
            "volatility, and Kim Yong-bum was involved in the product launch review."
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
                "류상윤 교수는 단일종목 레버리지 상품이 변동성을 키웠다고 말했다. "
                "김용범 정책실장은 상품 출시 검토에 관여했다."
            ),
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert "SUSPICIOUS_ROMANIZED_KOREAN" not in result.quality_flags
    assert result.quality_flags == []


def test_korean_translation_allows_disclosure_hyphenated_market_terms() -> None:
    client = FakeTranslationClient(
        json_translation(
            "The disposal method includes over-the-counter trading, off-market disposal, "
            "and end-of-period quantity disclosures."
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
                "처분방법은 시간외대량매매와 장외처분을 포함한다. "
                "자기주식 처분 결정 전 자기주식 보유현황에는 기말수량이 표시된다."
            ),
            source_type="DISCLOSURE",
        )
    )

    assert result.status == "TRANSLATED"
    assert "SUSPICIOUS_ROMANIZED_KOREAN" not in result.quality_flags
    assert result.quality_flags == []


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
            "Samsung Electronics' DX and DS divisions pursue separate two-track ESG strategies.",
        ),
        (
            "현대차·기아·모비스 초비상…美 부품 82% 유지",
            "Hyundai Motor, Kia, and Hyundai Mobis are on high alert as the U.S. "
            "keeps an 82% parts rule.",
        ),
        (
            "“증시 때문에 머리가 다 빠지네요”…결국 은행으로 다시 돈 몰린다",
            '"The stock market is making my hair fall out"; money is flowing back into banks.',
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
            ("라온시큐어 이순형 대표는 지난 22일부터 이틀간 약 2억136만원 규모의 주식을 매입했다."),
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


def test_korean_translation_accepts_citigroup_as_citi_source_term_surface() -> None:
    client = FakeTranslationClient(
        json_translation(
            "Citi and Goldman Sachs expect underwriting fees as SK hynix lists on Nasdaq."
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
                "씨티그룹과 골드만삭스는 SK하이닉스의 나스닥 상장으로 인수 수수료를 기대하고 있다."
            ),
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert "SOURCE_TERM_MISSING:CITI" not in result.quality_flags
    assert "Citi" in result.translated_text
    assert result.quality_flags == []


def test_korean_translation_recovers_missing_body_chunk_with_qwen_full_text_retry() -> None:
    client = SequenceTranslationClient(
        [
            json_translation(""),
            json_translation(""),
            json_translation(""),
            json_translation(
                "The second paragraph says investors watched foreign flows and chip earnings."
            ),
            json_translation(
                "The first paragraph explains SK hynix's Nasdaq listing and fee expectations "
                "for Wall Street investment banks. Citi and Goldman Sachs participated as "
                "bookrunners, and the second paragraph says investors watched foreign flows "
                "and chip earnings. KOSPI and KOSDAQ volatility also increased. The disclosure "
                "adds that liquidity, risk management, listing costs, and follow-up filings "
                "should be monitored. It also says investors should compare trading value, "
                "short-selling pressure, and valuation changes before reacting."
            ),
        ]
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )
    source = (
        "첫 번째 문단은 SK하이닉스의 나스닥 상장과 월가 투자은행의 수수료 기대를 설명한다. "
        "씨티그룹과 골드만삭스가 주관사로 참여했고 시장 관심이 커졌다는 내용이다. "
        "두 번째 문단은 투자자들이 외국인 수급과 반도체 업황을 확인해야 한다고 설명한다. "
        "코스피와 코스닥의 변동성이 커졌고 위험 관리가 중요하다는 분석도 포함됐다. "
        "세 번째 문단은 상장 비용, 유동성, 후속 공시 확인 필요성을 설명한다. "
        "네 번째 문단은 투자자들이 가격 반응과 거래대금 변화를 함께 점검해야 한다고 덧붙였다. "
        "다섯 번째 문단은 공매도 압력과 밸류에이션 변화도 함께 비교해야 한다고 설명한다. "
        "여섯 번째 문단은 단기 수급보다 실제 상장 조건과 후속 자료 확인이 더 중요하다고 강조했다."
    )

    result = generator.translate(KoreanTranslationContext(text=source, source_type="NEWS"))

    assert result.status == "TRANSLATED"
    assert result.quality_flags == []
    assert "Nasdaq listing" in result.translated_text
    assert len(client.calls) == 5


def test_korean_translation_retries_qwen_chunk_when_year_is_hallucinated() -> None:
    client = SequenceTranslationClient(
        [
            json_translation("Samsung Electronics said the product review would continue in 2028."),
            json_translation(
                "Samsung Electronics said the product review would continue this year."
            ),
        ]
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="삼성전자는 상품 검토가 올해 계속될 것이라고 밝혔다.",
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert "UNSUPPORTED_YEAR_FACT" not in result.quality_flags
    assert len(client.calls) == 2
    assert "this year" in result.translated_text


def test_korean_translation_retries_qwen_chunk_when_translation_is_empty() -> None:
    client = SequenceTranslationClient(
        [
            json_translation(""),
            json_translation(
                "Samsung Electronics filed a report on ownership of specified securities."
            ),
        ]
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text="삼성전자는 특정증권등 소유상황보고서를 제출했다.",
            source_type="DISCLOSURE",
        )
    )

    assert result.status == "TRANSLATED"
    assert "EMPTY_TRANSLATION" not in result.quality_flags
    assert len(client.calls) == 2
    assert "specified securities" in result.translated_text


def test_korean_translation_repairs_korean_compound_dollar_amount_and_chip_suppliers() -> None:
    client = FakeTranslationClient(
        json_translation(
            "Microchip's stock price rose more than 6% and fluctuated around the $1,200 "
            "level. Applied Material, KLA, Ram Research, and ARM also rose 6-11%."
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
                "마이크론의 주가는 6% 이상 급등해 1천20달러선을 등락하고 있다. "
                "어플라이드머티어리얼즈, KLA, 램 리서치, ARM 등도 6∼11% 올랐다."
            ),
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert "Micron's stock price" in result.translated_text
    assert "$1,020" in result.translated_text
    assert "Applied Materials" in result.translated_text
    assert "Lam Research" in result.translated_text
    assert result.quality_flags == []


def test_korean_translation_allows_market_hyphen_terms_and_repairs_trillion_dollars() -> None:
    client = FakeTranslationClient(
        json_translation(
            "Software stocks have recovered from a months-long decline. The software index "
            "reduced its year-to-date decline, while the semiconductor index remains near "
            "an all-time high. AI investment plans worth billions of dollars are under review."
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
                "소프트웨어 주식들은 수개월간 급락한 끝에 되살아나는 모습이다. "
                "소프트웨어 지수는 연초 대비 하락 폭을 줄였고 반도체 지수는 역대 최고치에 가깝다. "
                "수조 달러에 달하는 AI 설비투자 계획이 실제 집행될지 투자자들이 의심하고 있다."
            ),
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert "SUSPICIOUS_ROMANIZED_KOREAN" not in result.quality_flags
    assert "trillions of dollars" in result.translated_text
    assert result.quality_flags == []


def test_korean_translation_appends_missing_required_company_surface_in_body_chunk() -> None:
    client = FakeTranslationClient(
        json_translation(
            "He pointed to single-stock leveraged ETFs as the reason KOSDAQ and small-cap "
            "stocks have lagged behind KOSPI. Investors sold KOSDAQ stocks and moved into "
            "those products, concentrating supply and demand on one side."
        )
    )
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        model_name="test-qwen3-translation",
    )
    source = (
        "그는 코스피에 비해 코스닥과 중소형주가 힘을 쓰지 못하는 이유로 단일 종목 "
        "레버리지 ETF를 지목했다. 염 이사는 삼성전자와 하이닉스를 두 배 추종하는 "
        "단일 종목 레버리지 ETF가 양극화를 크게 만들었다고 분석했다. 투자자들이 "
        "코스닥 주식을 팔아 이 상품으로 갈아타면서 수급이 한쪽으로 쏠렸다고 설명했다. "
        "그는 대형 반도체주 쏠림이 시장의 체력을 약하게 만들 수 있어, 투자자들이 "
        "종목별 실적과 수급 변화를 함께 확인해야 한다고 덧붙였다. "
        "또한 높은 금리 환경에서도 기업 이익이 유지되는지 살피는 것이 중요하다고 말했다."
    )

    result = generator.translate(KoreanTranslationContext(text=source, source_type="NEWS"))

    assert result.status == "TRANSLATED"
    assert "SK hynix" in result.translated_text
    assert "SOURCE_TERM_MISSING:SK_HYNIX" not in result.quality_flags
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
        json_translation("LG will provide small-cap investors with low-stake compensation.")
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


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "코스피, 반도체주 반등에 7500선 회복···3%↑",
            "KOSPI recovers the 7,500 level as chip stocks rebound, up 3%.",
        ),
        (
            "미국 반도체주 훈풍에 코스피 장초반 3%↑",
            "KOSPI rises 3% early as U.S. chip stocks lift sentiment.",
        ),
        (
            "'반도체 투톱' 살아나자 코스피 3%대 반등…코스닥도 800선 눈앞",
            (
                "KOSPI rebounds more than 3% as Samsung Electronics and SK hynix "
                "recover; KOSDAQ nears 800."
            ),
        ),
        (
            "[속보] 코스피, 239.85p(3.31%) 오른 7486.64 출발",
            "Breaking: KOSPI opens at 7,486.64, up 239.85 points, or 3.31%.",
        ),
        (
            "장동혁, 韓증시 널뛰기 장세에 \"'블랙 에브리데이' 될까 걱정\"",
            (
                "Jang Dong-hyeok worries Korea's volatile stock market could become "
                "'Black Everyday'."
            ),
        ),
        (
            "코스피·코스닥, '오름세'로 장출발 [포토]",
            "KOSPI and KOSDAQ open higher.",
        ),
        (
            "[클로즈업] 외국인 매도세 집중된 시가총액 상위 10개 종목 리스트",
            "Close-up: Top 10 large-cap stocks hit by concentrated foreign selling.",
        ),
        (
            "[사설] ‘오징어게임’이 된 증시, 레버리지 ETF 놔둘 건가",
            (
                "Editorial: Has the stock market become Squid Game, and should "
                "leveraged ETFs be left alone?"
            ),
        ),
        (
            "코스피, 外人·기관 매수에 7500선 강세",
            "KOSPI trades firm above 7,500 on foreign and institutional buying.",
        ),
        (
            "중동 긴장과 반도체 불확실성, 코스피·코스닥 5%대 급락",
            (
                "KOSPI and KOSDAQ tumble about 5% amid Middle East tensions and "
                "semiconductor uncertainty."
            ),
        ),
        (
            "[증시진단] 한국만 '롤러코스터'...반도체보다 더 큰 문제는 '변동성'",
            (
                "Market diagnosis: Korea's stock-market volatility is a bigger "
                "problem than semiconductors."
            ),
        ),
        (
            "코스피 7,246.79 코스닥 785.00",
            "KOSPI closes at 7,246.79 and KOSDAQ at 785.00.",
        ),
        (
            '[8일 매매 동향] 외국인투자자, "삼성전자 팔고 SK하이닉스 샀다"',
            (
                "Trading flows on the 8th: foreign investors sold Samsung "
                "Electronics and bought SK hynix."
            ),
        ),
        (
            '리벨리온 대표 박성현 "내년 상반기 코스피 IPO 목표", 미국 상장 가능성...',
            (
                "Rebellions CEO Park Sung-hyun targets a KOSPI IPO in the first "
                "half of next year while leaving open a U.S. listing."
            ),
        ),
        (
            "['클릭' 증시] 이란 공습 충격에 코스피 거품 날아가...환율은 안정세",
            (
                "Click market: Iran strike shock wipes out KOSPI froth while the "
                "exchange rate stabilizes."
            ),
        ),
        (
            "코스피·코스닥 5%대 급락 마감…이틀 연속 ‘매도 사이드카’[마감시황...",
            (
                "KOSPI and KOSDAQ close down about 5% as sell-side sidecars trigger "
                "for a second day."
            ),
        ),
        (
            "삼성전기 주가 10%대 털썩…코스피 급락에 약세 면치 못했나?",
            ("Samsung Electro-Mechanics shares tumble more than 10% as the KOSPI selloff weighs."),
        ),
        (
            "코스피·코스닥 5% 넘게 폭락..반도체 고점 우려에 중동리스크까지",
            (
                "KOSPI and KOSDAQ plunge more than 5% as semiconductor peak concerns "
                "and Middle East risks weigh."
            ),
        ),
        (
            "최태원 SK그룹 회장, SK하이닉스 ADR 상장 기념식 직접 참석 | 중앙일보",
            "SK Group Chairman Chey Tae-won attends SK hynix ADR listing ceremony.",
        ),
        (
            "미래에셋증권, 해외 기관투자자 대상 ′Korea Bond Market Forum′ 개최…"
            "WGBI 편입 맞아 한국 채권시장 투자 매력 알려",
            (
                "Mirae Asset Securities holds Korea Bond Market Forum for overseas "
                "institutional investors as Korea joins WGBI."
            ),
        ),
        (
            "눈치보기 장세 펼쳐진 코스피, 7200선 마감…개인은 2조원 순매도",
            (
                "KOSPI closes near the 7,200 level in cautious trading as retail "
                "investors net sell KRW 2 trillion."
            ),
        ),
        (
            "삼성전자發 반도체 피크아웃 공포… 뉴욕 증시까지 연쇄 충격",
            (
                "Samsung Electronics sparks semiconductor peak-out fears, sending "
                "shockwaves to New York stocks."
            ),
        ),
    ],
)
def test_korean_translation_returns_grounded_market_news_titles_before_glossary(
    source: str,
    expected: str,
) -> None:
    client = FakeTranslationClient(json_translation("This should not be used."))
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        local_glossary_enabled=True,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(KoreanTranslationContext(text=source, source_type="NEWS"))

    assert result.status == "TRANSLATED"
    assert result.provider == "article-grounded-ko-en-translation"
    assert result.translated_text == expected
    assert not re.search(r"[가-힣\u3400-\u4dbf\u4e00-\u9fff]", result.translated_text)
    assert "[ ]" not in result.translated_text
    assert "..." not in result.translated_text
    assert "↑" not in result.translated_text
    assert client.calls == []


@pytest.mark.parametrize(
    ("source", "model_output", "required_terms"),
    [
        (
            "코스닥",
            "Junior market.",
            ("KOSDAQ",),
        ),
        (
            "최태원 SK그룹 회장, SK하이닉스 ADR 상장 기념식 직접 참석",
            "Chairman Chey Tae-won attended the listing ceremony.",
            ("SK", "SK hynix", "ADR"),
        ),
        (
            "눈치보기 장세 펼쳐진 코스피, 7200선 마감…개인은 2조원 순매도",
            "The market closed lower as retail investors sold heavily.",
            ("KOSPI", "7,200", "2 trillion"),
        ),
    ],
)
def test_korean_translation_repairs_short_qwen_titles_before_quality_gate(
    source: str,
    model_output: str,
    required_terms: tuple[str, ...],
) -> None:
    client = FakeTranslationClient(json_translation(model_output))
    generator = KoreanTranslationGenerator(
        enabled=True,
        client=client,
        local_glossary_enabled=False,
        model_name="test-qwen3-translation",
    )

    result = generator.translate(KoreanTranslationContext(text=source, source_type="NEWS"))

    assert result.status == "TRANSLATED"
    assert result.provider in {
        "local-open-source-qwen3-translation",
        "article-grounded-ko-en-translation",
    }
    assert result.quality_flags == []
    assert not re.search(r"[가-힣\u3400-\u4dbf\u4e00-\u9fff]", result.translated_text)
    for term in required_terms:
        assert term in result.translated_text


@pytest.mark.parametrize(
    "translated",
    [
        '韓Korean stock market " "',
        "KOSPI 3%↑",
        "[ ] KOSPI, 239.85p(3.31%) 7486.64",
        "KOSPI·, [ ]",
    ],
)
def test_korean_translation_rejects_short_local_glossary_title_fragments(
    translated: str,
) -> None:
    generator = KoreanTranslationGenerator(enabled=True, client=FakeTranslationClient("{}"))

    flags = generator._short_local_glossary_quality_flags(
        "코스피 반도체주 반등에 7500선 회복",
        translated,
    )

    assert flags


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


def test_korean_translation_grounded_article_runs_when_local_model_disabled() -> None:
    generator = KoreanTranslationGenerator(
        enabled=False,
        client=None,
        model_name="disabled-local-translation",
    )

    result = generator.translate(
        KoreanTranslationContext(
            text=(
                "<앵커> 반도체 수출 호조에 힘입어 5월 우리나라 경상수지가 "
                "역대 최대 흑자를 기록했습니다. 코스피와 코스닥 모두 프로그램 "
                "매도 호가 효력을 정지하는 매도 사이드카가 발동됐고, 5%대 "
                "급락하며 마감했습니다. 코스닥은 10개월 만에 800선 아래로 "
                "떨어졌습니다. SK하이닉스의 ADR 상장이 국내 투자 심리 회복으로 "
                "이어질 거란 기대와 함께 외국인 투자자의 이탈을 가속화할 수 "
                "있단 우려도 나오고 있습니다."
            ),
            source_type="NEWS",
        )
    )

    assert result.status == "TRANSLATED"
    assert result.provider == "article-grounded-ko-en-translation"
    assert "Korea's current-account surplus hit a record high in May" in result.translated_text
    assert "KOSDAQ fell below the 800 level" in result.translated_text
    assert "SK hynix's ADR listing" in result.translated_text
    assert "U.S.-Iran" not in result.translated_text
    assert "USD 38.61 billion" not in result.translated_text
    assert "Hyundai Motor Securities analyst" not in result.translated_text
    assert not any("가" <= char <= "힣" for char in result.translated_text)
    assert result.quality_flags == []


def test_korean_translation_grounded_market_plunge_article_uses_full_body_path() -> None:
    generator = KoreanTranslationGenerator(
        enabled=False,
        client=None,
        model_name="disabled-local-translation",
    )

    source = (
        "국내 증시는 8일 반도체 투자심리 위축과 중동 지정학적 긴장이 한꺼번에 겹치면서 "
        "코스피와 코스닥이 나란히 5% 넘게 급락했다. 이날 코스피는 전 거래일보다 "
        "409.52포인트(5.35%) 내린 7,246.79에 거래를 마쳤고, 코스닥지수는 "
        "46.23포인트(5.56%) 하락한 785.00으로 마감했다. 코스피는 장중에는 한때 "
        "7,791.66까지 오르며 반등을 시도했지만, 곧바로 매물이 쏟아지면서 7,186.21까지 "
        "떨어졌다. 하루 고점과 저점 차이가 605.45포인트에 달할 만큼 시장 불안이 컸고, "
        "코스피 시가총액도 약 5천931조원으로 줄어 종가 기준 7주 만에 6천조원을 밑돌았다. "
        "오후 1시 31분 코스피200 선물지수가 5% 이상 하락한 상태가 1분간 이어지면서 "
        "유가증권시장 프로그램 매도호가 일시효력정지, 이른바 매도 사이드카가 발동됐다. "
        "2분 뒤에는 코스닥시장에서도 매도 사이드카가 발동됐다. 수급을 보면 외국인은 "
        "유가증권시장에서 3천315억원, 코스닥시장에서 3천368억원을 순매수했다. "
        "이번 급락의 중심에는 반도체주가 있었다. 국제유가까지 뛰었다. 8월 인도분 "
        "서부텍사스산원유(WTI) 선물 가격은 배럴당 72.69달러를 기록했다. "
        "국내 대표 반도체주인 삼성전자는 기대를 웃도는 실적 발표에도 6.25% 내린 "
        "27만7천500원에 마감했고, SK하이닉스도 5.68% 하락한 207만6천원으로 거래를 끝냈다. "
        "코스닥은 10개월 만에 심리적 지지선이었던 800선이 무너졌다."
    )

    result = generator.translate(KoreanTranslationContext(text=source, source_type="NEWS"))

    assert result.status == "TRANSLATED"
    assert result.provider == "article-grounded-ko-en-translation"
    assert "KOSPI closed at 7246.79" in result.translated_text
    assert "KOSDAQ finished at 785.00" in result.translated_text
    assert "Sell-side sidecars were triggered" in result.translated_text
    assert "KOSDAQ fell below the psychologically important 800 level" in result.translated_text
    assert "Full article text is unavailable" not in result.translated_text
    assert not any("가" <= char <= "힣" for char in result.translated_text)
    assert result.quality_flags == []


def test_korean_translation_disabled_by_default_returns_explicit_fallback() -> None:
    get_settings.cache_clear()
    routes.get_korean_translation_service.cache_clear()

    result = KoreanTranslationGenerator.from_settings(Settings()).translate(
        KoreanTranslationContext(text="삼성전자는 실적을 개선했다.")
    )

    assert result.status == "SOURCE_LANGUAGE_FALLBACK"
    assert result.provider == "source-language-fallback"
    assert "LOCAL_TRANSLATION_DISABLED" in result.quality_flags
