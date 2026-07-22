from __future__ import annotations

import argparse
import html
import json
import re
from collections import Counter, defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

import pyarrow.parquet as parquet

from hannah_montana_ai.services.sentiment_input import sentiment_document_text
from hannah_montana_ai.training.dataset import load_labeled_alerts
from hannah_montana_ai.training.sentiment_protocol import (
    assert_sentiment_groups_disjoint,
    canonical_sentiment_url,
    sentiment_provenance,
)
from hannah_montana_ai.training.sentiment_sampling import weak_sentiment_label

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_DIR = PROJECT_ROOT / "data/k_fnspid/v4"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data/curation/k_fnspid_sentiment"
DEFAULT_SILVER_PATH = PROJECT_ROOT / "data/training/k_fnspid_sentiment_silver.jsonl"
DEFAULT_DISCLOSURE_SILVER_PATH = (
    PROJECT_ROOT / "data/training/k_fnspid_disclosure_sentiment_silver.jsonl"
)
DEFAULT_REPORT_PATH = PROJECT_ROOT / "reports/k-fnspid-sentiment-dataset-report.json"
CODEBOOK_VERSION = "k-fnspid-sentiment-codebook/v1"
LABEL_ORDER = ("NEGATIVE", "NEUTRAL", "POSITIVE")
REVIEW_PARTITIONS = {
    "TRAIN_REVIEW": ("2022-01-01", "2024-12-31", 200),
    "DEVELOPMENT_REVIEW": ("2025-01-01", "2025-12-31", 150),
    "SEALED_TEST_REVIEW": ("2026-04-01", "2026-12-31", 200),
}
DISCLOSURE_REVIEW_PARTITIONS = {
    "DISCLOSURE_DEVELOPMENT_REVIEW": (
        "2025-01-01",
        "2025-12-31",
        {"NEGATIVE": 50, "NEUTRAL": 250, "POSITIVE": 150},
    ),
    "DISCLOSURE_SEALED_TEST_REVIEW": ("2026-04-01", "2026-12-31", 200),
}
PROTECTED_PATHS = (
    PROJECT_ROOT / "data/training/financial_alert_real_news_gold.jsonl",
    PROJECT_ROOT / "data/training/financial_alert_stock_review_gold.jsonl",
    PROJECT_ROOT / "data/evaluation/financial_alert_eval.jsonl",
    PROJECT_ROOT / "data/evaluation/financial_alert_real_disclosure_gold.jsonl",
    PROJECT_ROOT / "data/evaluation/financial_alert_real_news_gold.jsonl",
    PROJECT_ROOT / "data/evaluation/financial_alert_stock_review_gold.jsonl",
)
LOW_QUALITY_TITLE = re.compile(r"(?:오늘의\s*운세|로또|날씨|포토|부고|인사\]|인사$)")


@dataclass(frozen=True, slots=True)
class Candidate:
    document_id: str
    source_type: str
    title: str
    snippet: str
    source_url: str
    content_hash: str
    published_at_kst: str
    effective_trade_date: str
    event_cluster_id: str
    stock_code: str
    stock_name: str
    sampling_stratum: str
    rule_confidence: float

    @property
    def text(self) -> str:
        return sentiment_document_text(self.title, self.snippet)

    def group_row(self) -> dict[str, str]:
        return {
            "text": self.text,
            "canonical_url": canonical_sentiment_url(self.source_url),
            "content_hash": self.content_hash,
            "event_cluster_id": self.event_cluster_id,
        }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="K-FNSPID 뉴스 감성 실버 학습셋과 독립 검수 패킷을 생성한다."
    )
    parser.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--silver-path", type=Path, default=DEFAULT_SILVER_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--silver-per-label", type=int, default=10_000)
    parser.add_argument("--seed", type=str, default="20260715")
    args = parser.parse_args()

    protected_rows = _load_protected_rows(PROTECTED_PATHS)
    news_candidates, news_source_audit = load_candidates(
        args.dataset_dir, protected_rows, source_types={"NEWS"}
    )
    review = select_review_partitions(news_candidates, args.seed)
    news_reserved_rows = [candidate.group_row() for rows in review.values() for candidate in rows]
    silver = select_silver_rows(
        news_candidates,
        protected_rows + news_reserved_rows,
        args.silver_per_label,
        args.seed,
        source_type="NEWS",
    )
    assert_sentiment_groups_disjoint(
        {
            **{
                name: [candidate.group_row() for candidate in rows] for name, rows in review.items()
            },
            "SILVER_TRAIN": silver,
            "LEGACY_PROTECTED": protected_rows,
        }
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_paths: dict[str, Path] = {}
    for partition, rows in review.items():
        output_path = args.output_dir / f"{partition.casefold()}.jsonl"
        _write_jsonl_atomic(output_path, [_review_payload(row, partition) for row in rows])
        output_paths[partition] = output_path
    args.silver_path.parent.mkdir(parents=True, exist_ok=True)
    _write_jsonl_atomic(args.silver_path, silver)

    generated_at = datetime.now(UTC).isoformat()
    report = {
        "schema_version": "k-fnspid-sentiment-dataset-report/v1",
        "generated_at": generated_at,
        "dataset_version": "K-FNSPID-v4",
        "codebook_version": CODEBOOK_VERSION,
        "sampling_seed": args.seed,
        "source_audit": news_source_audit,
        "independence_contract": {
            "group_keys": [
                "canonical_url",
                "normalized_text",
                "content_hash",
                "event_cluster_id",
            ],
            "legacy_gold_role": "contaminated_regression_diagnostic_only",
            "sealed_test_policy": "candidate_hash_locked_before_first_label_evaluation",
        },
        "partitions": {
            **{
                name: {
                    **_file_report(path, [_review_payload(row, name) for row in review[name]]),
                    "blind_sampling_distribution": dict(
                        sorted(Counter(row.sampling_stratum for row in review[name]).items())
                    ),
                }
                for name, path in output_paths.items()
            },
            "SILVER_TRAIN": _file_report(args.silver_path, silver),
        },
    }
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    _write_json_atomic(args.report_path, report)
    print(json.dumps(report, ensure_ascii=False))


def load_candidates(
    dataset_dir: Path,
    protected_rows: list[dict[str, str]],
    *,
    source_types: set[str] | None = None,
) -> tuple[list[Candidate], dict[str, Any]]:
    allowed_source_types = source_types or {"NEWS", "DISCLOSURE"}
    primary_entities = _load_primary_entities(dataset_dir / "document_entities.parquet")
    protected_keys = {key for row in protected_rows for key in sentiment_provenance(row).group_keys}
    documents = parquet.read_table(
        dataset_dir / "documents.parquet",
        columns=[
            "document_id",
            "source_type",
            "title",
            "snippet",
            "source_url",
            "content_hash",
            "published_at_kst",
            "effective_trade_date",
            "event_cluster_id",
        ],
    )
    counters: Counter[str] = Counter()
    result: list[Candidate] = []
    seen_documents: set[str] = set()
    for batch in documents.to_batches(max_chunksize=50_000):
        payload = batch.to_pydict()
        for index, source_type in enumerate(payload["source_type"]):
            counters["input_documents"] += 1
            if source_type not in allowed_source_types:
                continue
            document_id = str(payload["document_id"][index] or "")
            entity = primary_entities.get(document_id)
            if entity is None or document_id in seen_documents:
                counters["excluded_without_unique_primary_entity"] += 1
                continue
            title = _clean_text(payload["title"][index])
            snippet = _clean_text(payload["snippet"][index])
            source_url = str(payload["source_url"][index] or "").strip()
            event_cluster_id = str(payload["event_cluster_id"][index] or "").strip()
            if not _eligible_title(title) or not source_url or not event_cluster_id:
                counters["excluded_quality_contract"] += 1
                continue
            sampling_stratum, confidence = weak_sentiment_label(
                f"{title} {snippet}", str(source_type)
            )
            candidate = Candidate(
                document_id=document_id,
                source_type=str(source_type),
                title=title,
                snippet=snippet[:800],
                source_url=source_url,
                content_hash=str(payload["content_hash"][index] or "").strip(),
                published_at_kst=str(payload["published_at_kst"][index] or "").strip(),
                effective_trade_date=str(payload["effective_trade_date"][index] or "").strip(),
                event_cluster_id=event_cluster_id,
                stock_code=entity[0],
                stock_name=entity[1],
                sampling_stratum=sampling_stratum,
                rule_confidence=confidence,
            )
            if sentiment_provenance(candidate.group_row()).group_keys & protected_keys:
                counters["excluded_legacy_protected_group"] += 1
                continue
            result.append(candidate)
            seen_documents.add(document_id)
            counters[f"candidate_{str(source_type).casefold()}_{sampling_stratum.casefold()}"] += 1
    counters["eligible_candidates"] = len(result)
    counters["unique_primary_entities"] = len({row.stock_code for row in result})
    return result, dict(sorted(counters.items()))


def _load_primary_entities(path: Path) -> dict[str, tuple[str, str]]:
    table = parquet.read_table(
        path,
        columns=["document_id", "stock_code", "stock_name", "relation"],
    )
    candidates: defaultdict[str, list[tuple[str, str]]] = defaultdict(list)
    for batch in table.to_batches(max_chunksize=100_000):
        payload = batch.to_pydict()
        for index, relation in enumerate(payload["relation"]):
            if relation == "PRIMARY":
                candidates[str(payload["document_id"][index])].append(
                    (
                        str(payload["stock_code"][index]),
                        str(payload["stock_name"][index]),
                    )
                )
    return {
        document_id: values[0]
        for document_id, values in candidates.items()
        if len(set(values)) == 1
    }


def select_review_partitions(
    candidates: list[Candidate],
    seed: str,
    *,
    partition_specs: Mapping[str, tuple[str, str, int | Mapping[str, int]]] = REVIEW_PARTITIONS,
    source_type: str = "NEWS",
) -> dict[str, list[Candidate]]:
    selected: dict[str, list[Candidate]] = {}
    used_group_keys: set[tuple[str, str]] = set()
    for partition, (start, end, requested_counts) in partition_specs.items():
        rows: list[Candidate] = []
        for label in LABEL_ORDER:
            per_label = (
                requested_counts[label]
                if isinstance(requested_counts, Mapping)
                else requested_counts
            )
            bucket = [
                candidate
                for candidate in candidates
                if candidate.sampling_stratum == label
                and candidate.source_type == source_type
                and start <= candidate.effective_trade_date <= end
            ]
            chosen = _diverse_select(
                bucket,
                per_label,
                f"{seed}:{partition}:{label}",
                used_group_keys,
                stock_cap=4,
            )
            if len(chosen) != per_label:
                raise RuntimeError(f"{partition} {label} 표본 부족: {len(chosen)}/{per_label}")
            rows.extend(chosen)
            for candidate in chosen:
                used_group_keys.update(sentiment_provenance(candidate.group_row()).group_keys)
        rows.sort(key=lambda row: _stable_digest(row.document_id, f"{seed}:{partition}"))
        selected[partition] = rows
    return selected


def select_silver_rows(
    candidates: list[Candidate],
    protected_rows: list[dict[str, str]],
    per_label: int,
    seed: str,
    *,
    source_type: str,
) -> list[dict[str, Any]]:
    protected_keys = {key for row in protected_rows for key in sentiment_provenance(row).group_keys}
    selected: list[Candidate] = []
    for label in LABEL_ORDER:
        minimum_confidence = (
            0.84 if label == "NEUTRAL" else (0.80 if source_type == "DISCLOSURE" else 0.92)
        )
        bucket = [
            candidate
            for candidate in candidates
            if candidate.sampling_stratum == label
            and candidate.source_type == source_type
            and candidate.effective_trade_date <= "2024-12-31"
            and candidate.rule_confidence >= minimum_confidence
            and not (sentiment_provenance(candidate.group_row()).group_keys & protected_keys)
        ]
        chosen = _diverse_select(
            bucket,
            per_label,
            f"{seed}:silver:{label}",
            protected_keys,
            stock_cap=40,
        )
        if len(chosen) != per_label:
            raise RuntimeError(f"SILVER {label} 표본 부족: {len(chosen)}/{per_label}")
        selected.extend(chosen)
        for candidate in chosen:
            protected_keys.update(sentiment_provenance(candidate.group_row()).group_keys)
    selected.sort(key=lambda row: _stable_digest(row.document_id, f"{seed}:silver"))
    return [_silver_payload(candidate) for candidate in selected]


def _diverse_select(
    candidates: list[Candidate],
    limit: int,
    seed: str,
    excluded_keys: set[tuple[str, str]],
    *,
    stock_cap: int,
) -> list[Candidate]:
    stock_counts: Counter[str] = Counter()
    selected: list[Candidate] = []
    for candidate in sorted(candidates, key=lambda row: _stable_digest(row.document_id, seed)):
        keys = sentiment_provenance(candidate.group_row()).group_keys
        if keys & excluded_keys or stock_counts[candidate.stock_code] >= stock_cap:
            continue
        selected.append(candidate)
        stock_counts[candidate.stock_code] += 1
        excluded_keys.update(keys)
        if len(selected) == limit:
            return selected
    return selected


def _review_payload(candidate: Candidate, partition: str) -> dict[str, Any]:
    return {
        "schema_version": "k-fnspid-sentiment-review-row/v1",
        "dataset_version": "K-FNSPID-v4",
        "partition": partition,
        "document_id": candidate.document_id,
        "source_type": candidate.source_type,
        "stock_code": candidate.stock_code,
        "stock_name": candidate.stock_name,
        "title": candidate.title,
        "snippet": candidate.snippet,
        "text": candidate.text,
        "source_url": candidate.source_url,
        "canonical_url": canonical_sentiment_url(candidate.source_url),
        "content_hash": candidate.content_hash,
        "published_at_kst": candidate.published_at_kst,
        "effective_trade_date": candidate.effective_trade_date,
        "event_cluster_id": candidate.event_cluster_id,
        "codebook_version": CODEBOOK_VERSION,
        "review_status": "NEEDS_BLIND_REVIEW",
        "final_sentiment": "",
        "reviewer_id": "",
        "reviewed_at": "",
        "review_note": "",
    }


def _silver_payload(candidate: Candidate) -> dict[str, Any]:
    return {
        "schema_version": "k-fnspid-sentiment-silver-row/v1",
        "dataset_version": "K-FNSPID-v4",
        "document_id": candidate.document_id,
        "source_type": candidate.source_type,
        "stock_code": candidate.stock_code,
        "stock_name": candidate.stock_name,
        "title": candidate.title,
        "snippet": candidate.snippet,
        "text": candidate.text,
        "sentiment": candidate.sampling_stratum,
        "source_url": candidate.source_url,
        "canonical_url": canonical_sentiment_url(candidate.source_url),
        "content_hash": candidate.content_hash,
        "published_at_kst": candidate.published_at_kst,
        "effective_trade_date": candidate.effective_trade_date,
        "event_cluster_id": candidate.event_cluster_id,
        "label_provenance": "STRICT_RULE_SILVER_V1",
        "label_confidence": candidate.rule_confidence,
        "sample_weight": round(0.35 * candidate.rule_confidence, 6),
        "review_status": "UNREVIEWED_SILVER",
        "codebook_version": CODEBOOK_VERSION,
    }


def _load_protected_rows(paths: tuple[Path, ...]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in paths:
        if not path.exists():
            continue
        for sample in load_labeled_alerts(path):
            rows.append(
                {
                    "text": sample.text,
                    "source_url": sample.source_url,
                    "content_hash": sample.content_hash,
                    "event_cluster_id": sample.event_cluster_id,
                }
            )
    return rows


def _eligible_title(title: str) -> bool:
    return 12 <= len(title) <= 260 and not LOW_QUALITY_TITLE.search(title)


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", html.unescape(str(value or ""))).strip()


def _stable_digest(value: str, seed: str) -> bytes:
    return sha256(f"{seed}:{value}".encode()).digest()


def _write_jsonl_atomic(path: Path, rows: list[dict[str, Any]]) -> None:
    temporary = path.with_suffix(f"{path.suffix}.tmp")
    with temporary.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    temporary.replace(path)


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(f"{path.suffix}.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _file_report(path: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    distribution = Counter(str(row["sentiment"]) for row in rows if row.get("sentiment"))
    return {
        "path": str(path.relative_to(PROJECT_ROOT)),
        "sample_count": len(rows),
        "label_distribution": dict(sorted(distribution.items())),
        "stock_count": len({str(row.get("stock_code")) for row in rows}),
        "event_cluster_count": len({str(row.get("event_cluster_id")) for row in rows}),
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    main()
