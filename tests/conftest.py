import urllib.error

import pytest

from hannah_montana_ai.services.korean_translation_generator import (
    QwenHttpKoreanTranslationClient,
)


@pytest.fixture(autouse=True)
def block_unmocked_qwen_calls(
    monkeypatch: pytest.MonkeyPatch,
    request: pytest.FixtureRequest,
) -> None:
    if request.node.name == "test_http_client_calls_openai_compatible_qwen_endpoint":
        return

    def unavailable(
        _self: QwenHttpKoreanTranslationClient,
        _messages: list[dict[str, str]],
        _max_tokens: int,
    ) -> str:
        raise urllib.error.URLError("Qwen must be explicitly mocked in unit tests")

    monkeypatch.setattr(QwenHttpKoreanTranslationClient, "generate", unavailable)
