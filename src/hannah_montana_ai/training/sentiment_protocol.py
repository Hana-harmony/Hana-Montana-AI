from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict, deque
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from hannah_montana_ai.training.dataset import load_labeled_alerts, resolve_jsonl_paths

LABEL_ORDER = ("NEGATIVE", "NEUTRAL", "POSITIVE")
_NON_ALNUM = re.compile(r"[^0-9a-z가-힣]+")
_TRACKING_QUERY_NAMES = frozenset(
    {
        "_ga",
        "_gl",
        "dclid",
        "fbclid",
        "gclid",
        "igshid",
        "mc_cid",
        "mc_eid",
        "msclkid",
        "ref",
        "referrer",
        "sid",
        "sid1",
        "sid2",
        "yclid",
    }
)
_TRACKING_QUERY_PREFIXES = ("utm_",)
ProvenanceGroupKey = tuple[str, str]


@dataclass(frozen=True, slots=True)
class SentimentProvenance:
    canonical_url: str
    normalized_text: str
    content_hash: str
    event_cluster_id: str

    @property
    def row_key(self) -> tuple[str, str, str, str]:
        return (
            self.canonical_url,
            self.normalized_text,
            self.content_hash,
            self.event_cluster_id,
        )

    @property
    def group_keys(self) -> frozenset[ProvenanceGroupKey]:
        values = {
            "canonical_url": self.canonical_url,
            "normalized_text": self.normalized_text,
            "content_hash": self.content_hash,
            "event_cluster_id": self.event_cluster_id,
        }
        return frozenset((name, value) for name, value in values.items() if value)


def canonical_sentiment_url(value: str) -> str:
    raw = unicodedata.normalize("NFKC", value).strip()
    if not raw:
        return ""
    try:
        parsed = urlsplit(raw)
        port = parsed.port
    except ValueError:
        return raw
    if not parsed.scheme or not parsed.hostname:
        return raw

    scheme = parsed.scheme.casefold()
    hostname = parsed.hostname.casefold().rstrip(".")
    if ":" in hostname and not hostname.startswith("["):
        hostname = f"[{hostname}]"
    default_port = (scheme == "http" and port == 80) or (scheme == "https" and port == 443)
    netloc = hostname if port is None or default_port else f"{hostname}:{port}"
    path = parsed.path or "/"
    if path != "/":
        path = path.rstrip("/")
    query = [
        (name, query_value)
        for name, query_value in parse_qsl(parsed.query, keep_blank_values=True)
        if not _is_tracking_query_parameter(name)
    ]
    query.sort(key=lambda item: (item[0].casefold(), item[1]))
    return urlunsplit((scheme, netloc, path, urlencode(query, doseq=True), ""))


def _is_tracking_query_parameter(name: str) -> bool:
    normalized = name.casefold()
    return normalized in _TRACKING_QUERY_NAMES or normalized.startswith(_TRACKING_QUERY_PREFIXES)


def sentiment_provenance(row: Mapping[str, Any]) -> SentimentProvenance:
    source_url = row.get("canonical_url") or row.get("source_url") or row.get("original_url")
    return SentimentProvenance(
        canonical_url=canonical_sentiment_url(str(source_url or "")),
        normalized_text=normalized_sentiment_text(str(row.get("text") or "")),
        content_hash=_normalized_identity(row.get("content_hash")),
        event_cluster_id=_normalized_identity(row.get("event_cluster_id")),
    )


def _normalized_identity(value: Any) -> str:
    return unicodedata.normalize("NFKC", str(value or "")).strip().casefold()


def purge_sentiment_group_overlap(
    training_rows: list[dict[str, Any]],
    protected_rows: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """보호 행과 연결된 provenance 그룹 전체를 학습 데이터에서 제거한다."""
    provenance = [sentiment_provenance(row) for row in training_rows]
    key_to_indices: dict[ProvenanceGroupKey, list[int]] = defaultdict(list)
    for index, item in enumerate(provenance):
        for key in item.group_keys:
            key_to_indices[key].append(index)

    protected_keys = {key for row in protected_rows for key in sentiment_provenance(row).group_keys}
    queue = deque(sorted(protected_keys))
    contaminated_keys = set(protected_keys)
    removed_indices: set[int] = set()
    trigger_counts: Counter[str] = Counter()
    propagated_count = 0
    while queue:
        key = queue.popleft()
        for index in key_to_indices.get(key, ()):
            if index in removed_indices:
                continue
            removed_indices.add(index)
            trigger_counts[key[0]] += 1
            if key not in protected_keys:
                propagated_count += 1
            for connected_key in sorted(provenance[index].group_keys):
                if connected_key not in contaminated_keys:
                    contaminated_keys.add(connected_key)
                    queue.append(connected_key)

    cleaned = [row for index, row in enumerate(training_rows) if index not in removed_indices]
    return cleaned, {
        "input_count": len(training_rows),
        "output_count": len(cleaned),
        "removed_count": len(removed_indices),
        "propagated_removed_count": propagated_count,
        "protected_group_key_count": len(protected_keys),
        "contaminated_group_key_count": len(contaminated_keys),
        "removed_by_trigger_key": {
            name: trigger_counts[name]
            for name in (
                "canonical_url",
                "normalized_text",
                "content_hash",
                "event_cluster_id",
            )
        },
    }


def assert_sentiment_groups_disjoint(
    partitions: Mapping[str, Sequence[Mapping[str, Any]]],
) -> None:
    keys = {
        name: {key for row in rows for key in sentiment_provenance(row).group_keys}
        for name, rows in partitions.items()
    }
    names = sorted(keys)
    for index, left in enumerate(names):
        for right in names[index + 1 :]:
            overlap = keys[left] & keys[right]
            if overlap:
                counts = Counter(name for name, _ in overlap)
                summary = ", ".join(f"{name}={counts[name]}" for name in sorted(counts))
                raise ValueError(f"{left}-{right} provenance 그룹 중복: {summary}")


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

    validation_before = len(cleaned["VALIDATION"])
    cleaned["VALIDATION"], validation_overlap_audit = purge_sentiment_group_overlap(
        cleaned["VALIDATION"], cleaned["TEST"]
    )
    train_before = len(cleaned["TRAIN"])
    cleaned["TRAIN"], train_overlap_audit = purge_sentiment_group_overlap(
        cleaned["TRAIN"], [*cleaned["TEST"], *cleaned["VALIDATION"]]
    )
    audit = {
        "normalization": "NFKC-casefold-alphanumeric/v1",
        "holdout_priority": ["TEST", "VALIDATION", "TRAIN"],
        "internal": internal,
        "cross_partition_removed": {
            "TRAIN": train_before - len(cleaned["TRAIN"]),
            "VALIDATION": validation_before - len(cleaned["VALIDATION"]),
            "TEST": 0,
        },
        "group_overlap": {
            "TRAIN": train_overlap_audit,
            "VALIDATION": validation_overlap_audit,
        },
        "final_count": {name: len(rows) for name, rows in cleaned.items()},
    }
    assert_disjoint_partitions(cleaned)
    return cleaned, audit


def assert_disjoint_partitions(partitions: dict[str, list[dict[str, str]]]) -> None:
    assert_sentiment_groups_disjoint(partitions)


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


def stratified_hash_three_way_split(
    rows: list[dict[str, str]],
    *,
    checkpoint_name: str,
    calibration_name: str,
    selection_name: str,
    minimum_per_label: int,
) -> dict[str, list[dict[str, str]]]:
    """라벨별 해시 정렬로 50/25/25 그룹 분할을 만든다."""
    names = (checkpoint_name, calibration_name, selection_name)
    if len(set(names)) != len(names) or minimum_per_label < 1:
        raise ValueError("3-way 분할 이름 또는 최소 라벨 수가 올바르지 않습니다.")
    result: dict[str, list[dict[str, str]]] = {name: [] for name in names}
    for label in LABEL_ORDER:
        bucket = [row for row in rows if row["label"] == label]
        bucket.sort(
            key=lambda row: sha256(
                json.dumps(
                    {
                        "normalized_text": normalized_sentiment_text(row["text"]),
                        "provenance": sentiment_provenance(row).row_key,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).digest()
        )
        checkpoint_count = len(bucket) // 2
        remaining = len(bucket) - checkpoint_count
        calibration_count = remaining // 2
        selection_count = remaining - calibration_count
        counts = (checkpoint_count, calibration_count, selection_count)
        if min(counts, default=0) < minimum_per_label:
            raise ValueError(
                f"{label} 3-way 분할 후 최소 {minimum_per_label}건을 보장할 수 없습니다: "
                f"{dict(zip(names, counts, strict=True))}"
            )
        calibration_end = checkpoint_count + calibration_count
        result[checkpoint_name].extend(bucket[:checkpoint_count])
        result[calibration_name].extend(bucket[checkpoint_count:calibration_end])
        result[selection_name].extend(bucket[calibration_end:])
    for values in result.values():
        values.sort(key=lambda row: normalized_sentiment_text(row["text"]))
    assert_sentiment_groups_disjoint(result)
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
