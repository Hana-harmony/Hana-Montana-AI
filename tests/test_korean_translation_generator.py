import json
import urllib.request

import pytest

from hannah_montana_ai.core.config import Settings
from hannah_montana_ai.domain.schemas import FinancialGlossaryTerm
from hannah_montana_ai.services.analyzer import _contains_glossary_surface
from hannah_montana_ai.services.korean_translation_generator import (
    KoreanTranslationContext,
    KoreanTranslationGenerator,
    OpenAIResponsesTranslationClient,
    QwenAlertSummaryContext,
    QwenAlertSummaryError,
    QwenHttpKoreanTranslationClient,
)


class FakeTranslationClient:
    def __init__(self, output: str) -> None:
        self.output = output
        self.calls: list[list[dict[str, str]]] = []

    def generate(self, messages: list[dict[str, str]], max_tokens: int) -> str:
        assert max_tokens > 0
        self.calls.append(messages)
        return self.output


class FakeHttpResponse:
    def __enter__(self) -> "FakeHttpResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return b'{"choices":[{"message":{"content":"{\\"translation\\":\\"translated\\"}"}}]}'


class FakeOpenAIHttpResponse:
    def __enter__(self) -> "FakeOpenAIHttpResponse":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def read(self) -> bytes:
        return (
            b'{"output":[{"type":"message","content":'
            b'[{"type":"output_text","text":"{\\"translation\\":\\"translated\\"}"}]}]}'
        )


def _term(source: str, normalized: str, english: str) -> FinancialGlossaryTerm:
    return FinancialGlossaryTerm(
        source_term=source,
        normalized_term=normalized,
        english_term=english,
        category="market_slang",
    )


def test_settings_factory_always_uses_qwen_4b_http() -> None:
    generator = KoreanTranslationGenerator.from_settings(
        Settings(korean_translation_llm_endpoint="http://127.0.0.1:18081")
    )

    assert isinstance(generator._client, QwenHttpKoreanTranslationClient)
    assert generator._model_name == "local-llm:Qwen3-4B-GGUF-Q4"
    assert generator._rule_based_repairs_enabled is False
    dictionary_terms = {
        (term.normalized_term, term.english_term)
        for term in generator._dictionary_glossary_terms
    }
    assert ("개미", "Ant") in dictionary_terms
    assert ("대장주", "Daejangju") in dictionary_terms


def test_dictionary_contract_repairs_qwen_localism_paraphrases() -> None:
    generator = KoreanTranslationGenerator.from_settings(
        Settings(korean_translation_llm_endpoint="http://127.0.0.1:18081")
    )
    client = FakeTranslationClient(
        json.dumps({"translation": "Insects are buying semiconductor blue chips."})
    )
    generator._client = client

    result = generator.translate(
        KoreanTranslationContext(text="개미가 반도체 대장주를 사고 있다.")
    )

    assert result.status == "TRANSLATED"
    assert result.translated_text == "Ant are buying semiconductor Daejangju."
    assert result.quality_flags == []
    prompt = json.loads(client.calls[0][1]["content"])
    glossary = {
        (term["normalized_term"], term["english_term"])
        for term in prompt["glossary"]
    }
    assert ("개미", "Ant") in glossary
    assert ("대장주", "Daejangju") in glossary


def test_settings_factory_requires_endpoint() -> None:
    try:
        KoreanTranslationGenerator.from_settings(Settings(korean_translation_llm_endpoint=""))
    except ValueError as error:
        assert "ENDPOINT" in str(error)
    else:
        raise AssertionError("empty Qwen endpoint must fail")


def test_http_client_calls_openai_compatible_qwen_endpoint(monkeypatch: object) -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(request: urllib.request.Request, timeout: float) -> FakeHttpResponse:
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        assert isinstance(request.data, bytes)
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return FakeHttpResponse()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)  # type: ignore[attr-defined]
    client = QwenHttpKoreanTranslationClient(
        endpoint="http://127.0.0.1:18081",
        model="Qwen3-4B-GGUF-Q4",
        timeout_seconds=30,
    )

    assert client.generate([{"role": "user", "content": "번역"}], 256)
    assert captured["url"] == "http://127.0.0.1:18081/v1/chat/completions"
    assert captured["body"]["model"] == "Qwen3-4B-GGUF-Q4"  # type: ignore[index]


def test_openai_client_uses_responses_api_without_persistence(monkeypatch: object) -> None:
    captured: dict[str, object] = {}

    def fake_urlopen(request: urllib.request.Request, timeout: float) -> FakeOpenAIHttpResponse:
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["headers"] = dict(request.header_items())
        assert isinstance(request.data, bytes)
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return FakeOpenAIHttpResponse()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)  # type: ignore[attr-defined]
    client = OpenAIResponsesTranslationClient(
        endpoint="https://api.openai.com",
        api_key="test-secret",
        model="gpt-5.6-luna",
        timeout_seconds=30,
    )

    result = client.generate([{"role": "user", "content": "번역"}], 256)

    assert json.loads(result)["translation"] == "translated"
    assert captured["url"] == "https://api.openai.com/v1/responses"
    assert captured["headers"]["Authorization"] == "Bearer test-secret"  # type: ignore[index]
    assert captured["body"]["model"] == "gpt-5.6-luna"  # type: ignore[index]
    assert captured["body"]["reasoning"] == {"effort": "low"}  # type: ignore[index]
    assert captured["body"]["store"] is False  # type: ignore[index]
    assert captured["body"]["text"]["format"] == {"type": "json_object"}  # type: ignore[index]


def test_openai_settings_factory_marks_initial_backfill_provider() -> None:
    generator = KoreanTranslationGenerator.from_openai_settings(
        Settings(openai_api_key="test-secret")
    )

    assert isinstance(generator._client, OpenAIResponsesTranslationClient)
    assert generator._model_name == "openai:gpt-5.6-luna"
    assert generator._provider_name == "openai-initial-backfill"


def test_qwen_generates_grounded_alert_title_and_what_why_impact() -> None:
    client = FakeTranslationClient(json.dumps({
        "translated_title": "Samsung Electronics expects stronger earnings",
        "what": "Samsung Electronics expects operating profit to improve.",
        "why": "The source cites recovering HBM demand.",
        "impact": "The update is relevant to investors monitoring semiconductor earnings.",
    }))
    generator = KoreanTranslationGenerator(
        client=client,
        model_name="fake-qwen",
        rule_based_repairs_enabled=False,
    )
    result = generator.generate_alert_summary(_summary_context())

    assert len(client.calls) == 1
    assert result.translated_title.startswith("Samsung Electronics")
    assert result.summary_lines.why == "The source cites recovering HBM demand."
    assert result.provider == "local-open-source-qwen3-translation"


def test_qwen_summary_quality_failure_does_not_return_a_fallback() -> None:
    client = FakeTranslationClient(json.dumps({
        "translated_title": "Samsung Electronics expects 999% growth",
        "what": "Samsung Electronics expects 999% growth.",
        "why": "The source cites recovering HBM demand.",
        "impact": "The update is relevant to investors.",
    }))
    generator = KoreanTranslationGenerator(
        client=client,
        model_name="fake-qwen",
        rule_based_repairs_enabled=False,
    )

    with pytest.raises(QwenAlertSummaryError, match="UNSUPPORTED_NUMERIC_FACT"):
        generator.generate_alert_summary(_summary_context())

    assert len(client.calls) == 2


@pytest.mark.parametrize(
    ("invalid_what", "expected_flag"),
    [
        ("Earnings improved.", "FRAGMENTARY_SUMMARY_LINE"),
        ("005930 reported stronger quarterly operating profit.", "STOCK_CODE_SUMMARY_SUBJECT"),
        ("...Samsung Electronics reported stronger operating profit.", "ELLIPSIS_REMAINS"),
    ],
)
def test_qwen_summary_matches_api_complete_sentence_contract(
    invalid_what: str,
    expected_flag: str,
) -> None:
    client = FakeTranslationClient(json.dumps({
        "translated_title": "Samsung Electronics expects stronger earnings",
        "what": invalid_what,
        "why": "The source cites recovering HBM demand.",
        "impact": "The update matters to investors monitoring semiconductor earnings.",
    }))
    generator = KoreanTranslationGenerator(
        client=client,
        model_name="fake-qwen",
        rule_based_repairs_enabled=False,
    )

    with pytest.raises(QwenAlertSummaryError, match=expected_flag):
        generator.generate_alert_summary(_summary_context())

    assert len(client.calls) == 2


def test_qwen_summary_normalizes_missing_terminal_punctuation() -> None:
    client = FakeTranslationClient(json.dumps({
        "translated_title": "Samsung Electronics expects stronger earnings",
        "what": "Samsung Electronics expects stronger earnings",
        "why": "The source cites recovering HBM demand",
        "impact": "The update matters to semiconductor investors",
    }))
    generator = KoreanTranslationGenerator(
        client=client,
        model_name="fake-qwen",
        rule_based_repairs_enabled=False,
    )

    result = generator.generate_alert_summary(_summary_context())

    assert result.summary_lines.what.endswith(".")
    assert result.summary_lines.why.endswith(".")
    assert result.summary_lines.impact.endswith(".")
    assert len(client.calls) == 1


@pytest.mark.parametrize(
    "invalid_title",
    [
        "Kia grants treasury shares...union objects",
        "Kia grants treasury shares…union objects",
        "Kia grants treasury shares···union objects",
    ],
)
def test_qwen_title_rejects_every_api_ellipsis_form(invalid_title: str) -> None:
    client = FakeTranslationClient(json.dumps({
        "translated_title": invalid_title,
        "what": "Kia granted treasury shares only to executives.",
        "why": "The source cites an employee-payment exception clause.",
        "impact": "The decision prompted objections from the labor union.",
    }))
    generator = KoreanTranslationGenerator(
        client=client,
        model_name="fake-qwen",
        rule_based_repairs_enabled=False,
    )

    with pytest.raises(QwenAlertSummaryError, match="ELLIPSIS_REMAINS"):
        generator.generate_alert_summary(_summary_context())

    assert len(client.calls) == 2
    assert client.calls[1][-2]["role"] == "assistant"
    assert json.loads(client.calls[1][-2]["content"])["translated_title"] == invalid_title
    assert "Replace every ellipsis" in client.calls[1][-1]["content"]


def _summary_context() -> QwenAlertSummaryContext:
    return QwenAlertSummaryContext(
        title="삼성전자 HBM 실적 개선 전망",
        content="삼성전자는 HBM 수요 회복으로 영업이익 증가를 전망했다.",
        source_type="NEWS",
        importance="HIGH",
        sentiment="POSITIVE",
        event_tags=["EARNINGS"],
        stock_code="005930",
        stock_name="삼성전자",
        stock_name_en="Samsung Electronics",
        market_impact_importance="MEDIUM",
    )


def test_long_body_retry_count_is_bounded() -> None:
    source = "삼성전자는 반도체 투자 계획과 공급망 현황을 상세히 설명했다. " * 30
    client = FakeTranslationClient(json.dumps({"translation": "번역 실패"}))
    generator = KoreanTranslationGenerator(
        client=client,
        model_name="fake-qwen",
        max_concurrency=2,
        rule_based_repairs_enabled=False,
    )

    result = generator.translate(KoreanTranslationContext(text=source))

    assert result.status == "SOURCE_LANGUAGE_FALLBACK"
    assert len(generator._chunks(source)) == 2
    assert len(client.calls) == 4


def test_ant_surface_is_not_rewritten_to_retail_investor() -> None:
    generator = KoreanTranslationGenerator()
    glossary = [_term("개미", "개미", "Ant")]

    translated = generator._apply_glossary_surfaces("Retail investors were net buyers.", glossary)

    assert translated == "Ant were net buyers."
    assert generator._glossary_quality_flags(translated, glossary) == []


def test_plural_ant_surface_is_normalized_to_canonical_ant() -> None:
    generator = KoreanTranslationGenerator()
    glossary = [_term("개미", "개미", "Ant")]

    assert generator._apply_glossary_surfaces("Ants were net buyers.", glossary) == (
        "Ant were net buyers."
    )


def test_daejangju_surface_preserves_romanization() -> None:
    generator = KoreanTranslationGenerator()
    glossary = [_term("대장주", "대장주", "Daejangju")]

    translated = generator._apply_glossary_surfaces("The sector leader stock rallied.", glossary)

    assert translated == "Daejangju rallied."
    assert generator._glossary_quality_flags(translated, glossary) == []


def test_missing_localism_surface_is_rejected() -> None:
    generator = KoreanTranslationGenerator()
    glossary = [_term("개미", "개미", "Ant")]

    assert generator._glossary_quality_flags("Investors were net buyers.", glossary) == [
        "GLOSSARY_TERM_MISSING:개미"
    ]


def test_english_glossary_alias_requires_a_whole_token() -> None:
    generator = KoreanTranslationGenerator()

    assert _contains_glossary_surface("A market participant bought shares.", "ant") is False
    assert generator._contains_source_term("A market participant bought shares.", "ant") is False
    assert _contains_glossary_surface("An Ant bought shares.", "ant") is True
    assert generator._contains_source_term("An Ant bought shares.", "ant") is True


def test_empty_source_returns_source_language_fallback() -> None:
    result = KoreanTranslationGenerator().translate(KoreanTranslationContext(text="   "))

    assert result.status == "SOURCE_LANGUAGE_FALLBACK"
    assert "EMPTY_SOURCE" in result.quality_flags


def test_translation_parser_accepts_qwen_thinking_wrapper() -> None:
    generator = KoreanTranslationGenerator()

    assert generator._parse_translation(
        '<think>reasoning</think>{"translation":"Samsung Electronics rose."}'
    ) == "Samsung Electronics rose."


def test_translation_parser_rejects_missing_translation_field() -> None:
    generator = KoreanTranslationGenerator()

    with pytest.raises(ValueError, match="translation is missing"):
        generator._parse_translation('{"summary":"wrong field"}')
