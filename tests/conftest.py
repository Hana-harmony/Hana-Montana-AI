import json

import pytest

from hannah_montana_ai.services.korean_translation_generator import (
    QwenHttpKoreanTranslationClient,
)


@pytest.fixture(autouse=True)
def mock_qwen_http_provider(
    monkeypatch: pytest.MonkeyPatch,
    request: pytest.FixtureRequest,
) -> None:
    if request.node.name == "test_http_client_calls_openai_compatible_qwen_endpoint":
        return

    def generate(
        _self: QwenHttpKoreanTranslationClient,
        messages: list[dict[str, str]],
        _max_tokens: int,
    ) -> str:
        payload = json.loads(messages[1]["content"])
        task = payload.get("task", "")
        if task.startswith("Extract grounded facts"):
            return json.dumps({"evidence": ["The source reports a financial event."]})
        if task.startswith("Create a grounded English financial alert"):
            return json.dumps({
                "translated_title": "Financial event update",
                "what": "The source reports a financial event.",
                "why": "The source states the event background.",
                "impact": "The event is relevant to investors monitoring the company.",
            })
        return json.dumps({"translation": "The complete source reports a financial event."})

    monkeypatch.setattr(QwenHttpKoreanTranslationClient, "generate", generate)
