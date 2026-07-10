import json
import urllib.request

import pytest

from hannah_montana_ai.core.config import Settings
from hannah_montana_ai.domain.schemas import FinancialGlossaryTerm
from hannah_montana_ai.services.korean_translation_generator import (
    KoreanTranslationContext,
    KoreanTranslationGenerator,
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


def test_alert_fields_use_one_qwen_generation_call() -> None:
    translated = """<<<1>>>
Samsung Electronics reports stronger earnings.
<<<2>>>
Earnings improved as semiconductor demand recovered.
<<<3>>>
Samsung Electronics said operating profit increased as semiconductor demand recovered."""
    client = FakeTranslationClient(json.dumps({"translation": translated}))
    generator = KoreanTranslationGenerator(
        client=client,
        model_name="fake-qwen",
        rule_based_repairs_enabled=False,
    )
    results = generator.translate_alert_fields(
        {
            "TITLE": KoreanTranslationContext(text="삼성전자 실적 개선"),
            "SUMMARY": KoreanTranslationContext(text="반도체 수요 회복으로 실적이 개선됐다."),
            "CONTENT": KoreanTranslationContext(
                text="삼성전자는 반도체 수요 회복으로 영업이익이 증가했다고 밝혔다."
            ),
        }
    )

    assert results is not None
    assert len(client.calls) == 1
    assert results["TITLE"].translated_text.startswith("Samsung Electronics")


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
