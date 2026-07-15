from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from hashlib import sha256
from pathlib import Path
from typing import Any

from hannah_montana_ai.training.dataset import load_labeled_alerts, resolve_jsonl_paths

LABEL_ORDER = ("NEGATIVE", "NEUTRAL", "POSITIVE")
_NON_ALNUM = re.compile(r"[^0-9a-z가-힣]+")


def normalized_sentiment_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text).casefold()
    return _NON_ALNUM.sub("", normalized)


def conflict_safe_deduplicate(
    rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, int]]:
    by_text: dict[str, dict[str, str]] = {}
    conflicts: set[str] = set()
    empty_count = 0
    for row in rows:
        key = normalized_sentiment_text(row["text"])
        if not key:
            empty_count += 1
            continue
        previous = by_text.get(key)
        if previous is not None and previous["label"] != row["label"]:
            conflicts.add(key)
            continue
        by_text.setdefault(key, row)
    result = [row for key, row in by_text.items() if key not in conflicts]
    return result, {
        "input_count": len(rows),
        "output_count": len(result),
        "duplicate_count": len(rows) - len(by_text) - empty_count,
        "conflicting_text_count": len(conflicts),
        "empty_normalized_text_count": empty_count,
    }


def decontaminate_public_partitions(
    partitions: dict[str, list[dict[str, str]]],
) -> tuple[dict[str, list[dict[str, str]]], dict[str, Any]]:
    """TEST를 보존하고 하위 우선순위 파티션의 중복을 제거한다."""
    required = {"TRAIN", "VALIDATION", "TEST"}
    if set(partitions) != required:
        raise ValueError(f"감성 파티션은 {sorted(required)}이 필요합니다.")
    cleaned: dict[str, list[dict[str, str]]] = {}
    internal: dict[str, dict[str, int]] = {}
    for name in ("TRAIN", "VALIDATION", "TEST"):
        cleaned[name], internal[name] = conflict_safe_deduplicate(partitions[name])

    test_keys = {normalized_sentiment_text(row["text"]) for row in cleaned["TEST"]}
    validation_before = len(cleaned["VALIDATION"])
    cleaned["VALIDATION"] = [
        row
        for row in cleaned["VALIDATION"]
        if normalized_sentiment_text(row["text"]) not in test_keys
    ]
    validation_keys = {normalized_sentiment_text(row["text"]) for row in cleaned["VALIDATION"]}
    train_before = len(cleaned["TRAIN"])
    holdout_keys = test_keys | validation_keys
    cleaned["TRAIN"] = [
        row
        for row in cleaned["TRAIN"]
        if normalized_sentiment_text(row["text"]) not in holdout_keys
    ]
    audit = {
        "normalization": "NFKC-casefold-alphanumeric/v1",
        "holdout_priority": ["TEST", "VALIDATION", "TRAIN"],
        "internal": internal,
        "cross_partition_removed": {
            "TRAIN": train_before - len(cleaned["TRAIN"]),
            "VALIDATION": validation_before - len(cleaned["VALIDATION"]),
            "TEST": 0,
        },
        "final_count": {name: len(rows) for name, rows in cleaned.items()},
    }
    assert_disjoint_partitions(cleaned)
    return cleaned, audit


def assert_disjoint_partitions(partitions: dict[str, list[dict[str, str]]]) -> None:
    keys = {
        name: {normalized_sentiment_text(row["text"]) for row in rows}
        for name, rows in partitions.items()
    }
    names = sorted(keys)
    for index, left in enumerate(names):
        for right in names[index + 1 :]:
            overlap = keys[left] & keys[right]
            if overlap:
                raise ValueError(f"{left}-{right} 정규화 문장 중복 {len(overlap)}건")


def stratified_hash_split(
    rows: list[dict[str, str]],
    *,
    left_name: str,
    right_name: str,
) -> dict[str, list[dict[str, str]]]:
    """라벨별 해시 정렬로 재현 가능한 1:1 분할을 만든다."""
    result: dict[str, list[dict[str, str]]] = {left_name: [], right_name: []}
    for label in LABEL_ORDER:
        bucket = [row for row in rows if row["label"] == label]
        bucket.sort(
            key=lambda row: sha256(normalized_sentiment_text(row["text"]).encode()).digest()
        )
        midpoint = (len(bucket) + 1) // 2
        result[left_name].extend(bucket[:midpoint])
        result[right_name].extend(bucket[midpoint:])
    for values in result.values():
        values.sort(key=lambda row: normalized_sentiment_text(row["text"]))
    return result


def label_distribution(rows: list[dict[str, str]]) -> dict[str, int]:
    counts = Counter(row["label"] for row in rows)
    return {label: counts[label] for label in LABEL_ORDER}


def load_disclosure_domain_partitions(
    dataset_path: Path,
    evaluation_paths: tuple[Path, ...],
) -> tuple[dict[str, list[dict[str, str]]], dict[str, Any]]:
    holdout_samples = [sample for path in evaluation_paths for sample in load_labeled_alerts(path)]
    holdout_urls = {sample.source_url for sample in holdout_samples if sample.source_url}
    holdout_texts = {normalized_sentiment_text(sample.text) for sample in holdout_samples}
    candidates: list[dict[str, str]] = []
    excluded_url_count = 0
    excluded_text_count = 0
    for shard_path in resolve_jsonl_paths(dataset_path):
        with shard_path.open(encoding="utf-8") as file:
            for line in file:
                if not line.strip():
                    continue
                payload = json.loads(line)
                if (
                    payload.get("source_type") != "DISCLOSURE"
                    or payload.get("sentiment") not in LABEL_ORDER
                    or not payload.get("text")
                ):
                    continue
                if payload.get("source_url") in holdout_urls:
                    excluded_url_count += 1
                    continue
                if normalized_sentiment_text(str(payload["text"])) in holdout_texts:
                    excluded_text_count += 1
                    continue
                candidates.append(
                    {
                        "text": str(payload["text"]),
                        "label": str(payload["sentiment"]),
                        "published_at": str(payload.get("published_at", "")),
                        "source_type": "DISCLOSURE",
                    }
                )
    deduplicated, duplicate_audit = conflict_safe_deduplicate(candidates)
    historical = [row for row in deduplicated if row.get("published_at", "")[:4] != "2026"]
    future = [row for row in deduplicated if row.get("published_at", "")[:4] == "2026"]
    future_split = stratified_hash_split(
        future,
        left_name="CALIBRATION",
        right_name="SELECTION",
    )
    partitions = {"TRAIN": historical, **future_split}
    return partitions, {
        "normalization": "NFKC-casefold-alphanumeric/v1",
        "temporal_train_max_year": "2025",
        "calibration_selection_year": "2026",
        "excluded_gold_url_count": excluded_url_count,
        "excluded_gold_normalized_text_count": excluded_text_count,
        "deduplication": duplicate_audit,
    }
