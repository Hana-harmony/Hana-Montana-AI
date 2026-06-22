import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from hannah_montana_ai.domain.schemas import Importance, Sentiment, SourceType

JSONL_SHARD_MANIFEST_SCHEMA_VERSION = "jsonl-shard-manifest/v1"


@dataclass(frozen=True)
class LabeledAlert:
    text: str
    tags: list[str]
    sentiment: Sentiment
    importance: Importance
    source_type: SourceType = "NEWS"
    stock_code: str | None = None
    stock_name: str | None = None
    stock_aliases: list[str] = field(default_factory=list)
    source_review_status: str = ""
    reviewer_id: str = ""
    title: str = ""
    snippet: str = ""
    full_content: str = ""
    content_availability: str = "SUMMARY_ONLY"
    source_license_policy: str = ""
    source_url: str = ""
    content_hash: str = ""

    @property
    def model_text(self) -> str:
        parts = [
            self.title or self.text,
            self.snippet,
            self.full_content,
        ]
        return " ".join(part.strip() for part in parts if part and part.strip())

    @property
    def dedupe_text(self) -> str:
        return self.model_text or self.text


def load_labeled_alerts(path: Path) -> list[LabeledAlert]:
    samples: list[LabeledAlert] = []
    for payload in load_jsonl_payloads(path):
        samples.append(
            LabeledAlert(
                text=payload["text"],
                tags=payload["tags"],
                sentiment=payload["sentiment"],
                importance=payload["importance"],
                source_type=payload.get("source_type", "NEWS"),
                stock_code=payload.get("stock_code"),
                stock_name=payload.get("stock_name"),
                stock_aliases=payload.get("stock_aliases", []),
                source_review_status=payload.get("source_review_status", ""),
                reviewer_id=payload.get("reviewer_id", ""),
                title=payload.get("title", ""),
                snippet=payload.get("snippet", ""),
                full_content=payload.get("full_content", payload.get("content", "")),
                content_availability=payload.get("content_availability", "SUMMARY_ONLY"),
                source_license_policy=payload.get("source_license_policy", ""),
                source_url=payload.get("source_url", payload.get("original_url", "")),
                content_hash=payload.get("content_hash", ""),
            )
        )
    return samples


def load_jsonl_payloads(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for jsonl_path in resolve_jsonl_paths(path):
        with jsonl_path.open(encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    rows.append(json.loads(line))
    return rows


def resolve_jsonl_paths(path: Path) -> list[Path]:
    if not path.exists():
        return []
    first_line = ""
    with path.open(encoding="utf-8") as file:
        first_line = file.readline().strip()
    if not first_line:
        return [path]
    try:
        payload = json.loads(first_line)
    except json.JSONDecodeError:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return [path]
    shard_paths = payload.get("dataset_shards") if isinstance(payload, dict) else None
    if not isinstance(shard_paths, list):
        return [path]
    return [
        (path.parent / shard_path).resolve()
        for shard_path in shard_paths
        if isinstance(shard_path, str)
    ]
