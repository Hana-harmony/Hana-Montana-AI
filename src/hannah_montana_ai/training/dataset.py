import json
from dataclasses import dataclass
from pathlib import Path

from hannah_montana_ai.domain.schemas import Importance, Sentiment, SourceType


@dataclass(frozen=True)
class LabeledAlert:
    text: str
    tags: list[str]
    sentiment: Sentiment
    importance: Importance
    source_type: SourceType = "NEWS"
    stock_code: str | None = None
    stock_name: str | None = None


def load_labeled_alerts(path: Path) -> list[LabeledAlert]:
    samples: list[LabeledAlert] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        samples.append(
            LabeledAlert(
                text=payload["text"],
                tags=payload["tags"],
                sentiment=payload["sentiment"],
                importance=payload["importance"],
                source_type=payload.get("source_type", "NEWS"),
                stock_code=payload.get("stock_code"),
                stock_name=payload.get("stock_name"),
            )
        )
    return samples
