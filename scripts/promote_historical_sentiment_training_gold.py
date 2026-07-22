from __future__ import annotations

import argparse
import json
import os
import tempfile
from collections import Counter
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, cast

from hannah_montana_ai.training.sentiment_protocol import (
    assert_sentiment_groups_disjoint,
    sentiment_provenance,
)

try:
    from scripts.k_fnspid_sentiment_review_provenance import (
        LEGACY_STATUS,
        LegacyUnverifiedError,
        validate_dual_review_manifest,
    )
    from scripts.k_fnspid_sentiment_review_provenance import (
        artifact_record as review_artifact_record,
    )
except ModuleNotFoundError:  # pragma: no cover - 직접 script 실행 경로
    from k_fnspid_sentiment_review_provenance import (  # type: ignore[import-not-found,no-redef]
        LEGACY_STATUS,
        LegacyUnverifiedError,
        validate_dual_review_manifest,
    )
    from k_fnspid_sentiment_review_provenance import (  # type: ignore[no-redef]
        artifact_record as review_artifact_record,
    )

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REVIEW_SCHEMA = "k-fnspid-sentiment-review-row/v1"
DECISION_SCHEMA = "k-fnspid-sentiment-dual-review-decision/v1"
OUTPUT_SCHEMA = "k-fnspid-sentiment-auxiliary-training-gold/v2"
REPORT_SCHEMA = "k-fnspid-sentiment-training-reclassification/v2"
PRIMARY_OUTPUT_SCHEMA = "k-fnspid-sentiment-codex-gold/v1"
DEVELOPMENT_REPORT_SCHEMA = "k-fnspid-sentiment-development-promotion/v1"
TRAINING_ROLE = "TRAINING_ONLY_NOT_EVALUATION_OR_CLAIM_EVIDENCE"
DEVELOPMENT_ROLE = "DEVELOPMENT_MODEL_SELECTION_NOT_CLAIM_EVIDENCE"
LABELS = frozenset({"NEGATIVE", "NEUTRAL", "POSITIVE"})
UNRESOLVED_LABEL = "UNRESOLVED"
CODEBOOK_VERSION = "k-fnspid-sentiment-codebook/v1"
DECISION_FIELDS = frozenset(
    {
        "schema_version",
        "item_id",
        "reviewer_1",
        "reviewer_2",
        "independent_reviewer_count",
        "inter_reviewer_agreement",
        "decision_path",
        "adjudication",
        "final_sentiment",
        "review_note",
        "reviewer_id",
        "reviewed_at",
        "review_status",
        "reviewer_type",
        "model_blind",
        "market_blind",
    }
)
REVIEWER_FIELDS = frozenset(
    {
        "stage_1",
        "stage_2",
        "final_sentiment",
        "label_evidence",
        "decision_path",
        "reviewer_id",
        "reviewed_at",
        "reviewer_type",
        "model_blind",
        "market_blind",
    }
)
ADJUDICATION_FIELDS = frozenset(
    {
        "item_id",
        "final_sentiment",
        "adjudication_note",
        "adjudicator_id",
        "adjudicated_at",
        "adjudication_status",
    }
)
FORBIDDEN_RESERVATION_LABEL_FIELDS = frozenset(
    {
        "sentiment",
        "label",
        "teacher_sentiment",
        "candidate_prediction",
        "predicted_sentiment",
        "prediction",
        "logits",
        "probabilities",
    }
)
DEFAULT_CONFIRMATORY_PATHS = (
    PROJECT_ROOT / "data/gold/confirmatory_sealed_test_review.jsonl",
    PROJECT_ROOT / "data/gold/disclosure_confirmatory_sealed_test_review.jsonl",
)
DEFAULT_SAMPLING_DESIGN = (
    PROJECT_ROOT / "reports/k-fnspid-sentiment-confirmatory-sealed-sampling-design-v2.json"
)
DEFAULT_CODEBOOK_PATH = PROJECT_ROOT / "docs/datasets/k-fnspid-sentiment-codebook.md"
DEFAULT_REVIEW_PROMPT_PATH = (
    PROJECT_ROOT / "docs/datasets/k-fnspid-sentiment-review-prompt-v1.md"
)


def promote_historical_training_gold(
    *,
    review_path: Path,
    decisions_path: Path,
    output_path: Path,
    report_path: Path,
    expected_partition: str,
    expected_source: str,
    confirmatory_paths: tuple[Path, Path] = DEFAULT_CONFIRMATORY_PATHS,
    sampling_design_path: Path = DEFAULT_SAMPLING_DESIGN,
    review_provenance_path: Path | None = None,
    codebook_path: Path = DEFAULT_CODEBOOK_PATH,
    review_prompt_path: Path = DEFAULT_REVIEW_PROMPT_PATH,
    purpose: str = "TRAINING",
) -> dict[str, Any]:
    if review_provenance_path is None:
        raise LegacyUnverifiedError(
            f"{LEGACY_STATUS}: historical Gold에 receipt-bound dual-review provenance가 "
            "없습니다. 예측 비노출 상태로 재검수해야 합니다."
        )
    source = expected_source.upper()
    normalized_purpose = purpose.upper()
    if (
        source not in {"NEWS", "DISCLOSURE"}
        or not expected_partition.strip()
        or normalized_purpose not in {"TRAINING", "PRIMARY_TRAINING", "DEVELOPMENT"}
    ):
        raise ValueError("Partition or source type is invalid.")
    for path in (output_path, report_path):
        if path.exists() or path.is_symlink():
            raise ValueError(f"Output already exists: {path}")
    paths = (
        review_path,
        decisions_path,
        output_path,
        report_path,
        *confirmatory_paths,
        sampling_design_path,
    )
    if len(paths) != len({path.resolve() for path in paths}):
        raise ValueError("All input and output paths must be distinct.")

    review_rows = _read_jsonl(review_path)
    decision_rows = _read_jsonl(decisions_path)
    news_confirmatory = _read_jsonl(confirmatory_paths[0])
    disclosure_confirmatory = _read_jsonl(confirmatory_paths[1])
    sampling_design = _read_json(sampling_design_path)
    reviews, review_order = _validated_reviews(
        review_rows,
        expected_partition=expected_partition,
        expected_source=source,
    )
    decisions = _validated_decisions(decision_rows, set(review_order))
    review_provenance = validate_dual_review_manifest(
        review_provenance_path,
        review_path=review_path,
        decision_path=decisions_path,
        codebook_path=codebook_path,
        prompt_path=review_prompt_path,
    )
    _validate_confirmatory(news_confirmatory, "CONFIRMATORY_SEALED_TEST_REVIEW", "NEWS")
    _validate_confirmatory(
        disclosure_confirmatory,
        "DISCLOSURE_CONFIRMATORY_SEALED_TEST_REVIEW",
        "DISCLOSURE",
    )
    if (
        sampling_design.get("schema_version")
        != "k-fnspid-sentiment-confirmatory-sealed-sampling-design/v2"
        or sampling_design.get("report_role") != "UNLABELED_CONFIRMATORY_RESERVATION"
        or sampling_design.get("labels_available_at_reservation") is not False
        or sampling_design.get("candidate_predictions_available") is not False
    ):
        raise ValueError("Confirmatory sampling design contract is invalid.")
    _validate_sampling_commitments(
        sampling_design,
        review_path=review_path,
        confirmatory_paths=confirmatory_paths,
        confirmatory_rows=(news_confirmatory, disclosure_confirmatory),
    )
    assert_sentiment_groups_disjoint(
        {
            "AUXILIARY_TRAINING_SOURCE": [reviews[item_id] for item_id in review_order],
            "NEWS_CONFIRMATORY": news_confirmatory,
            "DISCLOSURE_CONFIRMATORY": disclosure_confirmatory,
        }
    )

    promoted_at_value = datetime.now(UTC)
    sampling_generated_at = _aware_datetime(
        sampling_design.get("generated_at"), "sampling_design.generated_at"
    )
    if sampling_generated_at >= promoted_at_value:
        raise ValueError("Confirmatory reservation must predate training reclassification.")
    promoted_at = promoted_at_value.isoformat()
    eligible_order = [
        item_id for item_id in review_order if decisions[item_id]["final_sentiment"] in LABELS
    ]
    unresolved_order = [
        item_id
        for item_id in review_order
        if decisions[item_id]["final_sentiment"] == UNRESOLVED_LABEL
    ]
    if len(eligible_order) + len(unresolved_order) != len(review_order) or not eligible_order:
        raise ValueError("Dual-review decisions do not define an eligible Gold subset.")
    gold_rows = [
        _gold_row(
            reviews[item_id],
            decisions[item_id],
            promoted_at=promoted_at,
            original_partition=expected_partition,
            purpose=normalized_purpose,
        )
        for item_id in eligible_order
    ]
    output_bytes = _jsonl_bytes(gold_rows)
    output_sha256 = sha256(output_bytes).hexdigest()
    report = {
        "schema_version": (
            DEVELOPMENT_REPORT_SCHEMA
            if normalized_purpose == "DEVELOPMENT"
            else REPORT_SCHEMA
        ),
        "generated_at": promoted_at,
        "reclassification": {
            "previous_role": "REPEATEDLY_EXPOSED_DIAGNOSTIC_NOT_CLAIM_EVIDENCE",
            "new_role": (
                DEVELOPMENT_ROLE
                if normalized_purpose == "DEVELOPMENT"
                else (
                    "PRIMARY_TRAINING_NOT_EVALUATION_OR_CLAIM_EVIDENCE"
                    if normalized_purpose == "PRIMARY_TRAINING"
                    else TRAINING_ROLE
                )
            ),
            "confirmatory_created_before_reclassification": True,
            "eligible_for_confirmatory_metrics": False,
            "eligible_for_superiority_claims": False,
            "eligible_for_model_selection": normalized_purpose == "DEVELOPMENT",
            "eligible_for_evaluation": normalized_purpose == "DEVELOPMENT",
        },
        "source": {
            "partition": expected_partition,
            "source_type": source,
            "review_sample_count": len(review_order),
            "sample_count": len(gold_rows),
            "excluded_unresolved_count": len(unresolved_order),
            "label_distribution": dict(
                sorted(Counter(str(row["sentiment"]) for row in gold_rows).items())
            ),
            "agreement_count": sum(
                bool(decisions[item_id]["inter_reviewer_agreement"]) for item_id in review_order
            ),
            "adjudicated_count": sum(
                decisions[item_id]["decision_path"] == "ADJUDICATED" for item_id in review_order
            ),
        },
        "lineage": {
            "review": _artifact_record(review_path),
            "dual_decisions": _artifact_record(decisions_path),
            "dual_review_provenance": review_artifact_record(review_provenance_path),
            "review_codebook": review_artifact_record(codebook_path),
            "review_prompt": review_artifact_record(review_prompt_path),
            "confirmatory_reservations": {
                "NEWS": _artifact_record(confirmatory_paths[0]),
                "DISCLOSURE": _artifact_record(confirmatory_paths[1]),
            },
            "confirmatory_sampling_design": _artifact_record(sampling_design_path),
            "output": {
                "path": _display_path(output_path),
                "bytes": len(output_bytes),
                "sha256": output_sha256,
            },
        },
        "integrity": {
            "exact_item_set": True,
            "independent_dual_review_required": True,
            "review_provenance_status": review_provenance["status"],
            "review_provenance_manifest_sha256": review_provenance[
                "merge_manifest_payload_sha256"
            ],
            "review_receipt_chain_exact": True,
            "candidate_predictions_not_provided_to_review_context": True,
            "teacher_predictions_not_provided_to_review_context": True,
            "review_context_ids_independent": True,
            "model_blind": True,
            "market_blind": True,
            "confirmatory_group_overlap_count": 0,
            "confirmatory_sampling_commitments_verified": True,
            "source_review_protected_at_confirmatory_reservation": True,
            "promotion_after_confirmatory_reservation": True,
            "write_once": True,
            "unresolved_rows_excluded": True,
        },
    }
    _atomic_write(output_path, output_bytes)
    _atomic_write(
        report_path,
        (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(),
    )
    return report


def _validated_reviews(
    rows: list[dict[str, Any]], *, expected_partition: str, expected_source: str
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    by_id: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for line_number, row in enumerate(rows, start=1):
        item_id = _item_id(row)
        if (
            row.get("schema_version") != REVIEW_SCHEMA
            or row.get("dataset_version") != "K-FNSPID-v4"
            or row.get("codebook_version") != CODEBOOK_VERSION
            or row.get("partition") != expected_partition
            or row.get("source_type") != expected_source
            or row.get("review_status") != "NEEDS_BLIND_REVIEW"
            or row.get("final_sentiment") not in {"", None}
            or FORBIDDEN_RESERVATION_LABEL_FIELDS.intersection(row)
            or any(
                row.get(field) not in {"", None}
                for field in ("reviewer_id", "reviewed_at", "review_note")
            )
            or any(
                not str(row.get(field, "")).strip()
                for field in (
                    "document_id",
                    "stock_code",
                    "stock_name",
                    "text",
                    "source_url",
                    "content_hash",
                    "event_cluster_id",
                    "published_at_kst",
                    "effective_trade_date",
                )
            )
            or item_id in by_id
        ):
            raise ValueError(f"Review row contract violation: {line_number}")
        _aware_datetime(row.get("published_at_kst"), "published_at_kst")
        by_id[item_id] = row
        order.append(item_id)
    if not order:
        raise ValueError("No review rows are available for reclassification.")
    _validate_internal_provenance(rows, "AUXILIARY_TRAINING_SOURCE")
    return by_id, order


def _validated_decisions(
    rows: list[dict[str, Any]], expected_ids: set[str]
) -> dict[str, dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for line_number, row in enumerate(rows, start=1):
        item_id = str(row.get("item_id", "")).strip()
        left = row.get("reviewer_1")
        right = row.get("reviewer_2")
        final_sentiment = row.get("final_sentiment")
        unresolved = final_sentiment == UNRESOLVED_LABEL
        if (
            set(row) != DECISION_FIELDS
            or row.get("schema_version") != DECISION_SCHEMA
            or final_sentiment not in LABELS | {UNRESOLVED_LABEL}
            or row.get("review_status")
            != ("UNRESOLVED" if unresolved else "CODEX_REVIEW_APPROVED")
            or row.get("independent_reviewer_count") != 2
            or not isinstance(row.get("inter_reviewer_agreement"), bool)
            or row.get("reviewer_type") != "INDEPENDENT_CODEX_AI"
            or row.get("model_blind") is not True
            or row.get("market_blind") is not True
            or row.get("decision_path")
            not in {
                "INDEPENDENT_REVIEWER_AGREEMENT",
                "ADJUDICATED",
                "UNRESOLVED_EXCLUDED",
            }
            or not isinstance(left, dict)
            or not isinstance(right, dict)
            or item_id in by_id
        ):
            raise ValueError(f"Dual-review decision contract violation: {line_number}")
        left_time = _validated_reviewer(left, "reviewer_1")
        right_time = _validated_reviewer(right, "reviewer_2")
        if left["reviewer_id"] == right["reviewer_id"]:
            raise ValueError(f"Dual-review decision contract violation: {line_number}")
        decision_time = _aware_datetime(row.get("reviewed_at"), "reviewed_at")
        if (
            not str(row.get("reviewer_id", "")).strip()
            or not str(row.get("review_note", "")).strip()
        ):
            raise ValueError(f"Dual-review decision contract violation: {line_number}")
        terminal_time = max(left_time, right_time)
        if row["decision_path"] == "INDEPENDENT_REVIEWER_AGREEMENT":
            if (
                unresolved
                or row.get("inter_reviewer_agreement") is not True
                or left.get("final_sentiment") != row["final_sentiment"]
                or right.get("final_sentiment") != row["final_sentiment"]
                or row.get("adjudication") is not None
            ):
                raise ValueError(f"Contradictory agreement decision: {item_id}")
        else:
            adjudication = row.get("adjudication")
            expected_path = "UNRESOLVED_EXCLUDED" if unresolved else "ADJUDICATED"
            expected_status = "UNRESOLVED" if unresolved else "CODEX_ADJUDICATED"
            if (
                row.get("inter_reviewer_agreement") is not False
                or not isinstance(adjudication, dict)
                or left.get("final_sentiment") == right.get("final_sentiment")
                or row.get("decision_path") != expected_path
                or adjudication.get("final_sentiment") != row["final_sentiment"]
                or adjudication.get("adjudication_status") != expected_status
            ):
                raise ValueError(f"Contradictory adjudication decision: {item_id}")
            if set(adjudication) != ADJUDICATION_FIELDS or adjudication.get("item_id") != item_id:
                raise ValueError(f"Contradictory adjudication decision: {item_id}")
            adjudicator_id = str(adjudication.get("adjudicator_id", "")).strip()
            if (
                not adjudicator_id
                or adjudicator_id in {left["reviewer_id"], right["reviewer_id"]}
                or not str(adjudication.get("adjudication_note", "")).strip()
                or row.get("reviewer_id") != adjudicator_id
                or row.get("review_note") != adjudication.get("adjudication_note")
            ):
                raise ValueError(f"Adjudicator independence violation: {item_id}")
            adjudicated_at = _aware_datetime(adjudication.get("adjudicated_at"), "adjudicated_at")
            if adjudicated_at < terminal_time:
                raise ValueError(f"Adjudication predates independent reviews: {item_id}")
            terminal_time = adjudicated_at
        if decision_time != terminal_time:
            raise ValueError(f"Decision timestamp is not the terminal review time: {item_id}")
        by_id[item_id] = row
    if set(by_id) != expected_ids:
        raise ValueError("Review and dual-review decision item sets differ.")
    return by_id


def _validate_confirmatory(rows: list[dict[str, Any]], partition: str, source: str) -> None:
    if len(rows) < 500 or any(
        row.get("schema_version") != REVIEW_SCHEMA
        or row.get("dataset_version") != "K-FNSPID-v4"
        or row.get("codebook_version") != CODEBOOK_VERSION
        or row.get("partition") != partition
        or row.get("source_type") != source
        or row.get("review_status") != "NEEDS_BLIND_REVIEW"
        or row.get("final_sentiment") not in {"", None}
        or any(
            row.get(field) not in {"", None}
            for field in ("reviewer_id", "reviewed_at", "review_note")
        )
        or FORBIDDEN_RESERVATION_LABEL_FIELDS.intersection(row)
        or not str(row.get("text", "")).strip()
        or not str(row.get("content_hash", "")).strip()
        or not str(row.get("event_cluster_id", "")).strip()
        for row in rows
    ):
        raise ValueError(f"Confirmatory reservation contract violation: {source}")
    item_ids = [_item_id(row) for row in rows]
    if len(item_ids) != len(set(item_ids)):
        raise ValueError(f"Confirmatory reservation item_id duplication: {source}")
    _validate_internal_provenance(rows, f"{source}_CONFIRMATORY")


def _validated_reviewer(value: dict[str, Any], field: str) -> datetime:
    final_sentiment = value.get("final_sentiment")
    if (
        set(value) != REVIEWER_FIELDS
        or final_sentiment not in LABELS
        or value.get("reviewer_type") != "CODEX_AI"
        or value.get("model_blind") is not True
        or value.get("market_blind") is not True
        or value.get("stage_1") != ("NEUTRAL" if final_sentiment == "NEUTRAL" else "DIRECTIONAL")
        or value.get("stage_2")
        != (final_sentiment if final_sentiment != "NEUTRAL" else "NOT_APPLICABLE")
        or value.get("decision_path") != "NEUTRAL_DIRECTIONAL_THEN_POLARITY"
        or not str(value.get("reviewer_id", "")).strip()
        or not str(value.get("label_evidence", "")).strip()
    ):
        raise ValueError(f"Invalid independent reviewer provenance: {field}")
    return _aware_datetime(value.get("reviewed_at"), f"{field}.reviewed_at")


def _validate_internal_provenance(rows: list[dict[str, Any]], label: str) -> None:
    seen: dict[tuple[str, str], int] = {}
    for index, row in enumerate(rows, start=1):
        for key in sentiment_provenance(row).group_keys:
            previous = seen.get(key)
            if previous is not None:
                raise ValueError(
                    f"{label} internal provenance duplication: rows {previous}, {index}"
                )
            seen[key] = index


def _validate_sampling_commitments(
    sampling_design: dict[str, Any],
    *,
    review_path: Path,
    confirmatory_paths: tuple[Path, Path],
    confirmatory_rows: tuple[list[dict[str, Any]], list[dict[str, Any]]],
) -> None:
    partitions = sampling_design.get("partitions")
    commitments = sampling_design.get("write_once_commitments")
    expected = (
        ("CONFIRMATORY_SEALED_TEST_REVIEW", "NEWS", confirmatory_paths[0], confirmatory_rows[0]),
        (
            "DISCLOSURE_CONFIRMATORY_SEALED_TEST_REVIEW",
            "DISCLOSURE",
            confirmatory_paths[1],
            confirmatory_rows[1],
        ),
    )
    if not isinstance(partitions, dict) or not isinstance(commitments, dict):
        raise ValueError("Confirmatory sampling commitments are missing.")
    for partition, source, path, rows in expected:
        details = partitions.get(partition)
        committed = commitments.get(partition)
        artifact = _artifact_record(path)
        if (
            not isinstance(details, dict)
            or details.get("source_type") != source
            or details.get("sample_count") != len(rows)
            or details.get("output") != artifact
            or committed != artifact
        ):
            raise ValueError(f"Confirmatory sampling artifact commitment mismatch: {source}")

    protected = sampling_design.get("protected_identity_sets")
    categories = protected.get("categories") if isinstance(protected, dict) else None
    review_artifact = _artifact_record(review_path)
    records = []
    if isinstance(categories, dict):
        for category in categories.values():
            if isinstance(category, dict) and isinstance(category.get("paths"), list):
                records.extend(category["paths"])
    if review_artifact not in records:
        raise ValueError("Historical review was not protected when confirmatory data was reserved.")


def _gold_row(
    source: dict[str, Any],
    decision: dict[str, Any],
    *,
    promoted_at: str,
    original_partition: str,
    purpose: str,
) -> dict[str, Any]:
    source_hash = _canonical_sha256(source)
    decision_hash = _canonical_sha256(decision)
    row = {
        **source,
        "schema_version": (
            OUTPUT_SCHEMA if purpose == "TRAINING" else PRIMARY_OUTPUT_SCHEMA
        ),
        "partition": (
            "AUXILIARY_TRAINING_GOLD" if purpose == "TRAINING" else original_partition
        ),
        "source_partition": original_partition,
        "item_id": _item_id(source),
        "sentiment": decision["final_sentiment"],
        "final_sentiment": decision["final_sentiment"],
        "label_quality": "INDEPENDENT_DUAL_CODEX_GOLD",
        "review_status": "CODEX_REVIEW_APPROVED",
        "reviewer_id": decision["reviewer_id"],
        "reviewed_at": decision["reviewed_at"],
        "review_note": decision["review_note"],
        "independent_reviewer_count": 2,
        "inter_reviewer_agreement": decision["inter_reviewer_agreement"],
        "decision_path": decision["decision_path"],
        "reviewer_1": decision["reviewer_1"],
        "reviewer_2": decision["reviewer_2"],
        "adjudication": decision["adjudication"],
        "model_blind": True,
        "market_blind": True,
        "promoted_at": promoted_at,
        "training_role": (
            TRAINING_ROLE
            if purpose == "TRAINING"
            else (
                "PRIMARY_TRAINING_NOT_EVALUATION_OR_CLAIM_EVIDENCE"
                if purpose == "PRIMARY_TRAINING"
                else "NOT_TRAINING_DATA"
            )
        ),
        "source_record_sha256": source_hash,
        "dual_decision_sha256": decision_hash,
    }
    provenance = {
        "item_id": row["item_id"],
        "source_record_sha256": source_hash,
        "dual_decision_sha256": decision_hash,
        "training_role": row["training_role"],
    }
    if purpose != "TRAINING":
        row["evaluation_role"] = (
            "NOT_EVALUATION_OR_CLAIM_EVIDENCE"
            if purpose == "PRIMARY_TRAINING"
            else DEVELOPMENT_ROLE
        )
        provenance["evaluation_role"] = row["evaluation_role"]
    row["promotion_provenance_sha256"] = _canonical_sha256(provenance)
    return row


def _item_id(row: dict[str, Any]) -> str:
    document_id = str(row.get("document_id", "")).strip()
    stock_code = str(row.get("stock_code", "")).strip()
    if not document_id or not stock_code:
        raise ValueError("Review row document_id or stock_code is missing.")
    return f"{document_id}::{stock_code}"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    _require_regular(path)
    result: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"JSONL row must be an object at line {line_number}: {path}")
            result.append(cast(dict[str, Any], value))
    return result


def _read_json(path: Path) -> dict[str, Any]:
    _require_regular(path)
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Top-level JSON value must be an object: {path}")
    return cast(dict[str, Any], value)


def _require_regular(path: Path) -> None:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"Input is not a regular file: {path}")


def _aware_datetime(value: object, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exception:
        raise ValueError(f"{field} is not an ISO-8601 timestamp.") from exception
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must include a timezone.")
    return parsed


def _canonical_sha256(value: dict[str, Any]) -> str:
    return sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_record(path: Path) -> dict[str, int | str]:
    return {"path": _display_path(path), "bytes": path.stat().st_size, "sha256": _file_sha256(path)}


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(resolved)


def _jsonl_bytes(rows: list[dict[str, Any]]) -> bytes:
    return "".join(
        json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    ).encode()


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as file:
            file.write(content)
            file.flush()
            os.fsync(file.fileno())
        os.chmod(temporary, 0o600)
        try:
            os.link(temporary, path, follow_symlinks=False)
        except FileExistsError as exception:
            raise ValueError(f"Output appeared during validation: {path}") from exception
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Promote receipt-bound dual-reviewed Gold for training or development."
    )
    parser.add_argument("--review-path", type=Path, required=True)
    parser.add_argument("--decisions-path", type=Path, required=True)
    parser.add_argument("--output-path", type=Path, required=True)
    parser.add_argument("--report-path", type=Path, required=True)
    parser.add_argument("--expected-partition", required=True)
    parser.add_argument("--expected-source", choices=("NEWS", "DISCLOSURE"), required=True)
    parser.add_argument(
        "--purpose",
        choices=("TRAINING", "PRIMARY_TRAINING", "DEVELOPMENT"),
        default="TRAINING",
    )
    parser.add_argument("--review-provenance-path", type=Path, required=True)
    parser.add_argument("--codebook-path", type=Path, default=DEFAULT_CODEBOOK_PATH)
    parser.add_argument(
        "--review-prompt-path",
        type=Path,
        default=DEFAULT_REVIEW_PROMPT_PATH,
    )
    args = parser.parse_args()
    report = promote_historical_training_gold(
        review_path=args.review_path,
        decisions_path=args.decisions_path,
        output_path=args.output_path,
        report_path=args.report_path,
        expected_partition=args.expected_partition,
        expected_source=args.expected_source,
        review_provenance_path=args.review_provenance_path,
        codebook_path=args.codebook_path,
        review_prompt_path=args.review_prompt_path,
        purpose=args.purpose,
    )
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
