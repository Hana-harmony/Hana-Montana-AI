from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, date, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, cast

from hannah_montana_ai.training.sentiment_git_attestation import (
    validate_candidate_git_attestation,
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
DEFAULT_REVIEW_PATH = PROJECT_ROOT / "data/curation/k_fnspid_sentiment/train_review.jsonl"
DEFAULT_TEACHER_PATH = PROJECT_ROOT / "data/curation/k_fnspid_sentiment/train_qwen_silver.jsonl"
DEFAULT_DECISIONS_PATH = (
    PROJECT_ROOT / "data/curation/k_fnspid_sentiment/train_codex_decisions.jsonl"
)
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "data/training/k_fnspid_sentiment_codex_gold.jsonl"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "reports/k-fnspid-sentiment-gold-promotion-report.json"
DEFAULT_CODEBOOK_PATH = PROJECT_ROOT / "docs/datasets/k-fnspid-sentiment-codebook.md"
DEFAULT_REVIEW_PROMPT_PATH = (
    PROJECT_ROOT / "docs/datasets/k-fnspid-sentiment-review-prompt-v1.md"
)
DEFAULT_GIT_ATTESTATION_PATH = (
    PROJECT_ROOT / "reports/sentiment-candidate-git-attestation.json"
)

REVIEW_SCHEMA_VERSION = "k-fnspid-sentiment-review-row/v1"
TEACHER_SCHEMA_VERSION = "k-fnspid-sentiment-teacher-silver/v1"
GOLD_SCHEMA_VERSION = "k-fnspid-sentiment-codex-gold/v1"
REPORT_SCHEMA_VERSION = "k-fnspid-sentiment-gold-promotion-report/v1"
SUPPORTED_CANDIDATE_LOCK_SCHEMAS = frozenset(
    {"sentiment-candidate-lock/v1", "sentiment-candidate-lock/v2"}
)
CODEBOOK_VERSION = "k-fnspid-sentiment-codebook/v1"
PROMPT_VERSION = "k-fnspid-sentiment-qwen-silver-v2"
OPERATIONAL_RULES_SHA256 = "13263e52e948678a16573db80f3b050e52ddc2cfdc35a6ffd71a6a9e437fc3a1"
TEACHER_PROVIDER = "local-open-source-qwen3"
TEACHER_ENDPOINT_SCOPE = "literal-loopback-only"
TEACHER_SAMPLING_SEED = 20260715
GOLD_REVIEWER_VISIBILITY = "PROHIBITED"
CANDIDATE_PREDICTION_VISIBILITY = "NOT_PROVIDED_TO_TEACHER_CONTEXT"
APPROVED_STATUS = "CODEX_REVIEW_APPROVED"
SENTIMENT_LABELS = frozenset({"POSITIVE", "NEUTRAL", "NEGATIVE"})
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
STAGE_PROVENANCE_FIELDS = frozenset(
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
TEACHER_INPUT_FIELDS = frozenset(
    {"item_id", "source_type", "target_security", "input_scope", "text"}
)
TRUNCATION_MARKER = "\n[...teacher input truncated...]\n"
CONTROL_CHARACTER_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
MAX_INPUT_BYTES = 512 * 1024 * 1024
MAX_CODEBOOK_BYTES = 1024 * 1024


@dataclass(frozen=True, slots=True)
class PromotionSummary:
    sample_count: int
    agreement_count: int
    disagreement_count: int
    output_path: str
    output_sha256: str
    report_path: str

    def as_dict(self) -> dict[str, object]:
        return {
            "sample_count": self.sample_count,
            "agreement_count": self.agreement_count,
            "disagreement_count": self.disagreement_count,
            "output_path": self.output_path,
            "output_sha256": self.output_sha256,
            "report_path": self.report_path,
        }


@dataclass(frozen=True, slots=True)
class JsonlArtifact:
    path: Path
    rows: tuple[dict[str, Any], ...]
    sha256: str


@dataclass(frozen=True, slots=True)
class CandidateManifestCommitment:
    sha256: str
    locked_at: datetime | None
    annotation_not_before: datetime | None
    git_attestation_sha256: str
    git_commit_sha: str


def promote_gold(
    *,
    review_path: Path,
    teacher_path: Path,
    decisions_path: Path,
    output_path: Path,
    report_path: Path,
    codebook_path: Path = DEFAULT_CODEBOOK_PATH,
    review_provenance_path: Path | None = None,
    review_prompt_path: Path = DEFAULT_REVIEW_PROMPT_PATH,
    candidate_lock_path: Path | None = None,
    candidate_git_attestation_path: Path | None = None,
    project_root: Path = PROJECT_ROOT,
) -> PromotionSummary:
    if review_provenance_path is None:
        raise LegacyUnverifiedError(
            f"{LEGACY_STATUS}: dual-review receipt provenance가 없습니다. "
            "예측 비노출 상태로 재검수한 뒤에만 Gold로 승격할 수 있습니다."
        )
    review_artifact = _read_jsonl_artifact(review_path, "원본 review")
    teacher_artifact = _read_jsonl_artifact(teacher_path, "Qwen teacher silver")
    decision_artifact = _read_jsonl_artifact(decisions_path, "Codex decisions")
    codebook_resolved, codebook_sha256 = _load_codebook(codebook_path)
    review_prompt_resolved, review_prompt_sha256 = _load_codebook(review_prompt_path)
    output_resolved = _resolve_output_path(output_path, "Gold 출력")
    report_resolved = _resolve_output_path(report_path, "승격 보고서")
    for label, path in (("Gold 출력", output_resolved), ("승격 보고서", report_resolved)):
        if path.exists() or path.is_symlink():
            raise ValueError(f"{label}이 이미 존재하여 다시 승격할 수 없습니다: {path}")
    _validate_distinct_paths(
        review_artifact.path,
        teacher_artifact.path,
        decision_artifact.path,
        output_resolved,
        report_resolved,
    )

    review_by_id, review_order = _validate_review_rows(review_artifact.rows)
    partition = str(review_artifact.rows[0]["partition"])
    source_types = {str(row["source_type"]) for row in review_artifact.rows}
    source_type = next(iter(source_types)) if len(source_types) == 1 else "MULTI_SOURCE"
    candidate_commitment = _candidate_manifest_commitment(
        partition,
        source_type,
        review_artifact,
        candidate_lock_path,
        candidate_git_attestation_path,
        project_root=project_root,
    )
    teacher_by_id = _validate_teacher_rows(
        teacher_artifact.rows,
        review_by_id,
        codebook_path=codebook_resolved,
        codebook_sha256=codebook_sha256,
    )
    decision_by_id = _validate_decision_rows(decision_artifact.rows)
    if candidate_commitment.annotation_not_before is not None:
        _validate_post_lock_annotations(
            teacher_by_id,
            decision_by_id,
            candidate_commitment.annotation_not_before,
        )
    candidate_manifest_sha256 = candidate_commitment.sha256
    expected_ids = set(review_by_id)
    _assert_exact_item_set("Qwen teacher silver", set(teacher_by_id), expected_ids)
    _assert_exact_item_set("Codex decisions", set(decision_by_id), expected_ids)
    review_provenance = validate_dual_review_manifest(
        review_provenance_path,
        review_path=review_artifact.path,
        decision_path=decision_artifact.path,
        codebook_path=codebook_resolved,
        prompt_path=review_prompt_resolved,
    )

    promoted_at = datetime.now(UTC).isoformat()
    gold_rows = [
        _build_gold_row(
            review_by_id[item_id],
            teacher_by_id[item_id],
            decision_by_id[item_id],
            promoted_at=promoted_at,
            candidate_manifest_sha256=candidate_manifest_sha256,
            candidate_git_attestation_sha256=candidate_commitment.git_attestation_sha256,
            candidate_git_commit_sha=candidate_commitment.git_commit_sha,
        )
        for item_id in review_order
        if decision_by_id[item_id]["final_sentiment"] in SENTIMENT_LABELS
    ]
    if not gold_rows:
        raise ValueError("UNRESOLVED 제외 후 Gold 행이 없습니다.")
    output_bytes = _encode_jsonl(gold_rows)
    output_sha256 = sha256(output_bytes).hexdigest()
    report = _build_report(
        review_artifact=review_artifact,
        teacher_artifact=teacher_artifact,
        decision_artifact=decision_artifact,
        output_path=output_resolved,
        output_sha256=output_sha256,
        codebook_path=codebook_resolved,
        codebook_sha256=codebook_sha256,
        review_by_id=review_by_id,
        teacher_by_id=teacher_by_id,
        decision_by_id=decision_by_id,
        review_order=review_order,
        gold_rows=gold_rows,
        candidate_manifest_sha256=candidate_manifest_sha256,
        candidate_git_attestation_sha256=candidate_commitment.git_attestation_sha256,
        candidate_git_commit_sha=candidate_commitment.git_commit_sha,
        review_provenance_path=review_provenance_path,
        review_provenance=review_provenance,
        review_prompt_path=review_prompt_resolved,
        review_prompt_sha256=review_prompt_sha256,
    )
    report_bytes = (json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )

    # 검증이 모두 끝난 뒤에만 Gold와 보고서를 교체한다.
    _atomic_write_bytes(output_resolved, output_bytes)
    _atomic_write_bytes(report_resolved, report_bytes)
    agreement_count = sum(bool(row["teacher_agreement"]) for row in gold_rows)
    return PromotionSummary(
        sample_count=len(gold_rows),
        agreement_count=agreement_count,
        disagreement_count=len(gold_rows) - agreement_count,
        output_path=_display_path(output_resolved),
        output_sha256=output_sha256,
        report_path=_display_path(report_resolved),
    )


def _validate_review_rows(
    rows: tuple[dict[str, Any], ...],
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    by_id: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for line_number, row in enumerate(rows, start=1):
        context = f"원본 review {line_number}행"
        if row.get("schema_version") != REVIEW_SCHEMA_VERSION:
            raise ValueError(f"{context} schema_version이 올바르지 않습니다.")
        if row.get("codebook_version") != CODEBOOK_VERSION:
            raise ValueError(f"{context} codebook_version이 올바르지 않습니다.")
        if row.get("review_status") != "NEEDS_BLIND_REVIEW":
            raise ValueError(f"{context}는 검수 전 원본이 아닙니다.")
        for field in ("final_sentiment", "reviewer_id", "reviewed_at", "review_note"):
            if row.get(field) not in {"", None}:
                raise ValueError(f"{context}의 {field}는 원본에서 비어 있어야 합니다.")
        source_type = _required_string(row.get("source_type"), f"{context}.source_type")
        if source_type not in {"NEWS", "DISCLOSURE"}:
            raise ValueError(f"{context}.source_type이 올바르지 않습니다.")
        for field in (
            "dataset_version",
            "partition",
            "document_id",
            "stock_code",
            "stock_name",
            "text",
            "source_url",
            "content_hash",
            "event_cluster_id",
        ):
            _required_string(row.get(field), f"{context}.{field}")
        _parse_aware_datetime(row.get("published_at_kst"), f"{context}.published_at_kst")
        _parse_iso_date(row.get("effective_trade_date"), f"{context}.effective_trade_date")
        source_sha256 = _canonical_sha256(row)
        item_id = _resolve_item_id(row, source_sha256)
        if item_id in by_id:
            raise ValueError(f"원본 review에 중복 item_id가 있습니다: {item_id}")
        by_id[item_id] = row
        order.append(item_id)
    _require_single_value(rows, "dataset_version", "원본 review")
    _require_single_value(rows, "partition", "원본 review")
    return by_id, order


def _validate_teacher_rows(
    rows: tuple[dict[str, Any], ...],
    review_by_id: dict[str, dict[str, Any]],
    *,
    codebook_path: Path,
    codebook_sha256: str,
) -> dict[str, dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    expected_codebook_path = _display_path(codebook_path)
    fixed_provenance: dict[str, object] = {
        "schema_version": TEACHER_SCHEMA_VERSION,
        "label_quality": "SILVER",
        "review_status": "needs_codex_review",
        "needs_codex_review": True,
        "teacher_provider": TEACHER_PROVIDER,
        "teacher_endpoint_scope": TEACHER_ENDPOINT_SCOPE,
        "prompt_version": PROMPT_VERSION,
        "operational_rules_sha256": OPERATIONAL_RULES_SHA256,
        "sampling_seed": TEACHER_SAMPLING_SEED,
        "codebook_path": expected_codebook_path,
        "codebook_sha256": codebook_sha256,
        "gold_reviewer_visibility": GOLD_REVIEWER_VISIBILITY,
        "candidate_prediction_visibility": CANDIDATE_PREDICTION_VISIBILITY,
        "model_blind": True,
        "market_blind": True,
    }
    for line_number, row in enumerate(rows, start=1):
        context = f"Qwen teacher silver {line_number}행"
        item_id = _required_string(row.get("item_id"), f"{context}.item_id")
        if item_id in by_id:
            raise ValueError(f"Qwen teacher silver에 중복 item_id가 있습니다: {item_id}")
        for field, expected in fixed_provenance.items():
            if row.get(field) != expected:
                raise ValueError(f"{context}.{field} provenance가 올바르지 않습니다.")
        source_record = row.get("source_record")
        if not isinstance(source_record, dict):
            raise ValueError(f"{context}.source_record가 JSON 객체가 아닙니다.")
        expected_source = review_by_id.get(item_id)
        if expected_source is None:
            raise ValueError(f"{context} item_id가 원본 review에 없습니다: {item_id}")
        if source_record != expected_source:
            raise ValueError(f"{context}.source_record가 원본 review와 다릅니다.")
        source_sha256 = _canonical_sha256(source_record)
        if row.get("source_record_sha256") != source_sha256:
            raise ValueError(f"{context}.source_record_sha256이 원본과 다릅니다.")
        teacher_input = row.get("teacher_input")
        if not isinstance(teacher_input, dict) or set(teacher_input) != TEACHER_INPUT_FIELDS:
            raise ValueError(f"{context}.teacher_input 스키마가 올바르지 않습니다.")
        if row.get("teacher_input_sha256") != _canonical_sha256(teacher_input):
            raise ValueError(f"{context}.teacher_input_sha256이 입력과 다릅니다.")
        truncated = row.get("teacher_input_truncated")
        if not isinstance(truncated, bool):
            raise ValueError(f"{context}.teacher_input_truncated가 bool이 아닙니다.")
        _validate_teacher_input(
            teacher_input,
            expected_source,
            item_id=item_id,
            truncated=truncated,
            context=context,
        )
        sentiment = row.get("sentiment")
        if sentiment not in SENTIMENT_LABELS:
            raise ValueError(f"{context}.sentiment가 올바르지 않습니다.")
        confidence = row.get("confidence")
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
            raise ValueError(f"{context}.confidence가 숫자가 아닙니다.")
        if not 0.0 <= float(confidence) <= 1.0:
            raise ValueError(f"{context}.confidence가 범위를 벗어났습니다.")
        _required_string(row.get("rationale"), f"{context}.rationale", max_length=1_000)
        _required_string(
            row.get("teacher_model_requested"),
            f"{context}.teacher_model_requested",
        )
        _required_string(
            row.get("teacher_model_served"),
            f"{context}.teacher_model_served",
        )
        _parse_aware_datetime(row.get("generated_at_utc"), f"{context}.generated_at_utc")
        by_id[item_id] = row
    for field in (
        "teacher_model_requested",
        "teacher_model_served",
        "teacher_provider",
        "prompt_version",
        "codebook_path",
        "codebook_sha256",
        "operational_rules_sha256",
    ):
        _require_single_value(rows, field, "Qwen teacher silver")
    return by_id


def _validate_teacher_input(
    teacher_input: dict[str, Any],
    source_record: dict[str, Any],
    *,
    item_id: str,
    truncated: bool,
    context: str,
) -> None:
    source_type = str(source_record["source_type"])
    expected_text, expected_scope = _resolve_teacher_text(source_record, context)
    expected_metadata: dict[str, object] = {
        "item_id": item_id,
        "source_type": source_type,
        "target_security": _resolve_target_security(source_record),
        "input_scope": expected_scope,
    }
    if any(teacher_input.get(field) != expected for field, expected in expected_metadata.items()):
        raise ValueError(f"{context}.teacher_input provenance가 원본 review와 다릅니다.")
    teacher_text = teacher_input.get("text")
    if not isinstance(teacher_text, str) or not teacher_text:
        raise ValueError(f"{context}.teacher_input.text가 비어 있습니다.")
    if not truncated and teacher_text != expected_text:
        raise ValueError(f"{context}.teacher_input.text가 원본 review와 다릅니다.")
    if truncated:
        parts = teacher_text.split(TRUNCATION_MARKER)
        if (
            len(parts) != 2
            or not parts[0]
            or not parts[1]
            or not expected_text.startswith(parts[0])
            or not expected_text.endswith(parts[1])
            or len(teacher_text) >= len(expected_text)
        ):
            raise ValueError(f"{context}.teacher_input.text 절단 provenance가 올바르지 않습니다.")


def _validate_decision_rows(
    rows: tuple[dict[str, Any], ...],
) -> dict[str, dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for line_number, row in enumerate(rows, start=1):
        context = f"Codex decisions {line_number}행"
        if set(row) != DECISION_FIELDS:
            raise ValueError(f"{context} 스키마가 올바르지 않습니다.")
        item_id = _required_string(row.get("item_id"), f"{context}.item_id")
        if item_id in by_id:
            raise ValueError(f"Codex decisions에 중복 item_id가 있습니다: {item_id}")
        if row.get("schema_version") != "k-fnspid-sentiment-dual-review-decision/v1":
            raise ValueError(f"{context}.schema_version이 올바르지 않습니다.")
        final_sentiment = row.get("final_sentiment")
        if final_sentiment not in SENTIMENT_LABELS | {"UNRESOLVED"}:
            raise ValueError(f"{context}.final_sentiment가 올바르지 않습니다.")
        expected_status = "UNRESOLVED" if final_sentiment == "UNRESOLVED" else APPROVED_STATUS
        if row.get("review_status") != expected_status:
            raise ValueError(f"{context}.review_status가 승인 상태가 아닙니다.")
        if (
            row.get("independent_reviewer_count") != 2
            or not isinstance(row.get("inter_reviewer_agreement"), bool)
            or row.get("reviewer_type") != "INDEPENDENT_CODEX_AI"
            or row.get("model_blind") is not True
            or row.get("market_blind") is not True
        ):
            raise ValueError(f"{context}의 독립 검수 provenance가 올바르지 않습니다.")
        reviewer_1 = _validate_reviewer_provenance(row.get("reviewer_1"), f"{context}.reviewer_1")
        reviewer_2 = _validate_reviewer_provenance(row.get("reviewer_2"), f"{context}.reviewer_2")
        if reviewer_1["reviewer_id"] == reviewer_2["reviewer_id"]:
            raise ValueError(f"{context}의 독립 검수자 ID가 같습니다.")
        agreement = bool(row["inter_reviewer_agreement"])
        adjudication = row.get("adjudication")
        if agreement:
            if (
                reviewer_1["final_sentiment"] != reviewer_2["final_sentiment"]
                or final_sentiment != reviewer_1["final_sentiment"]
                or row.get("decision_path") != "INDEPENDENT_REVIEWER_AGREEMENT"
                or adjudication is not None
            ):
                raise ValueError(f"{context}의 일치 판정 경로가 올바르지 않습니다.")
        else:
            _validate_adjudication(
                adjudication, item_id, final_sentiment, f"{context}.adjudication"
            )
            expected_path = (
                "UNRESOLVED_EXCLUDED" if final_sentiment == "UNRESOLVED" else "ADJUDICATED"
            )
            if (
                reviewer_1["final_sentiment"] == reviewer_2["final_sentiment"]
                or row.get("decision_path") != expected_path
            ):
                raise ValueError(f"{context}의 adjudication 경로가 올바르지 않습니다.")
        _required_string(row.get("reviewer_id"), f"{context}.reviewer_id", max_length=128)
        _required_string(row.get("review_note"), f"{context}.review_note", max_length=2_000)
        _parse_aware_datetime(row.get("reviewed_at"), f"{context}.reviewed_at")
        by_id[item_id] = row
    return by_id


def _validate_reviewer_provenance(value: object, context: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != STAGE_PROVENANCE_FIELDS:
        raise ValueError(f"{context} 스키마가 올바르지 않습니다.")
    if (
        value.get("final_sentiment") not in SENTIMENT_LABELS
        or value.get("reviewer_type") != "CODEX_AI"
        or value.get("model_blind") is not True
        or value.get("market_blind") is not True
    ):
        raise ValueError(f"{context} provenance가 올바르지 않습니다.")
    final_sentiment = str(value["final_sentiment"])
    if (
        value.get("stage_1") != ("NEUTRAL" if final_sentiment == "NEUTRAL" else "DIRECTIONAL")
        or value.get("stage_2")
        != (final_sentiment if final_sentiment != "NEUTRAL" else "NOT_APPLICABLE")
        or value.get("decision_path") != "NEUTRAL_DIRECTIONAL_THEN_POLARITY"
    ):
        raise ValueError(f"{context}의 2단계 판정 경로가 올바르지 않습니다.")
    _required_string(value.get("label_evidence"), f"{context}.label_evidence", max_length=2_000)
    _required_string(value.get("reviewer_id"), f"{context}.reviewer_id", max_length=128)
    _parse_aware_datetime(value.get("reviewed_at"), f"{context}.reviewed_at")
    return value


def _validate_adjudication(
    value: object,
    item_id: str,
    final_sentiment: object,
    context: str,
) -> None:
    if not isinstance(value, dict) or set(value) != ADJUDICATION_FIELDS:
        raise ValueError(f"{context} 스키마가 올바르지 않습니다.")
    expected_status = "UNRESOLVED" if final_sentiment == "UNRESOLVED" else "CODEX_ADJUDICATED"
    if (
        value.get("item_id") != item_id
        or value.get("final_sentiment") != final_sentiment
        or value.get("adjudication_status") != expected_status
    ):
        raise ValueError(f"{context} 판정이 최종 결정과 다릅니다.")
    _required_string(
        value.get("adjudication_note"), f"{context}.adjudication_note", max_length=2_000
    )
    _required_string(value.get("adjudicator_id"), f"{context}.adjudicator_id", max_length=128)
    _parse_aware_datetime(value.get("adjudicated_at"), f"{context}.adjudicated_at")


def _build_gold_row(
    source: dict[str, Any],
    teacher: dict[str, Any],
    decision: dict[str, Any],
    *,
    promoted_at: str,
    candidate_manifest_sha256: str,
    candidate_git_attestation_sha256: str,
    candidate_git_commit_sha: str,
) -> dict[str, Any]:
    text, _ = _resolve_teacher_text(source, "Gold source")
    full_content = _first_string(source, "full_content", "full_text", "content")
    final_sentiment = str(decision["final_sentiment"])
    teacher_sentiment = str(teacher["sentiment"])
    source_sha256 = str(teacher["source_record_sha256"])
    teacher_sha256 = _canonical_sha256(teacher)
    decision_sha256 = _canonical_sha256(decision)
    return {
        "schema_version": GOLD_SCHEMA_VERSION,
        "dataset_version": source["dataset_version"],
        "partition": source["partition"],
        "item_id": teacher["item_id"],
        "text": text,
        "tags": [],
        "sentiment": final_sentiment,
        "importance": "MEDIUM",
        "source_type": source["source_type"],
        "stock_code": source["stock_code"],
        "stock_name": source["stock_name"],
        "stock_aliases": source.get("stock_aliases", []),
        "title": source.get("title", ""),
        "snippet": source.get("snippet", ""),
        "full_content": full_content,
        "content_availability": source.get(
            "content_availability",
            "FULL_TEXT" if full_content else "SUMMARY_ONLY",
        ),
        "source_license_policy": source.get("source_license_policy", ""),
        "source_url": source["source_url"],
        "canonical_url": source.get("canonical_url", ""),
        "content_hash": source["content_hash"],
        "provider": source.get("provider", ""),
        "published_at": source.get("published_at", source["published_at_kst"]),
        "published_at_kst": source["published_at_kst"],
        "published_precision": source.get("published_precision", ""),
        "market_session": source.get("market_session", ""),
        "effective_trade_date": source["effective_trade_date"],
        "document_id": source["document_id"],
        "event_cluster_id": source["event_cluster_id"],
        "label_quality": "GOLD",
        "source_review_status": APPROVED_STATUS,
        "review_status": APPROVED_STATUS,
        "needs_codex_review": False,
        "reviewer_id": decision["reviewer_id"],
        "reviewed_at": decision["reviewed_at"],
        "promoted_at": promoted_at,
        "review_note": decision["review_note"],
        "annotation_protocol": source["codebook_version"],
        "candidate_manifest_sha256": candidate_manifest_sha256,
        "candidate_git_attestation_sha256": candidate_git_attestation_sha256,
        "candidate_git_commit_sha": candidate_git_commit_sha,
        "independent_reviewer_count": decision["independent_reviewer_count"],
        "inter_reviewer_agreement": decision["inter_reviewer_agreement"],
        "decision_path": decision["decision_path"],
        "stage_1": "NEUTRAL" if final_sentiment == "NEUTRAL" else "DIRECTIONAL",
        "stage_2": (final_sentiment if final_sentiment != "NEUTRAL" else "NOT_APPLICABLE"),
        "reviewer_1": decision["reviewer_1"],
        "reviewer_2": decision["reviewer_2"],
        "adjudication": decision["adjudication"],
        "reviewer_type": decision["reviewer_type"],
        "codebook_version": source["codebook_version"],
        "codebook_sha256": teacher["codebook_sha256"],
        "teacher_sentiment": teacher_sentiment,
        "teacher_confidence": float(teacher["confidence"]),
        "teacher_rationale": teacher["rationale"],
        "teacher_provider": teacher["teacher_provider"],
        "teacher_model_requested": teacher["teacher_model_requested"],
        "teacher_model_served": teacher["teacher_model_served"],
        "teacher_generated_at_utc": teacher["generated_at_utc"],
        "teacher_prompt_version": teacher["prompt_version"],
        "teacher_agreement": teacher_sentiment == final_sentiment,
        "model_blind": teacher["model_blind"],
        "market_blind": teacher["market_blind"],
        "source_record_sha256": source_sha256,
        "teacher_silver_row_sha256": teacher_sha256,
        "codex_decision_sha256": decision_sha256,
        "promotion_provenance_sha256": _canonical_sha256(
            {
                "item_id": teacher["item_id"],
                "source_record_sha256": source_sha256,
                "teacher_silver_row_sha256": teacher_sha256,
                "codex_decision_sha256": decision_sha256,
            }
        ),
    }


def _build_report(
    *,
    review_artifact: JsonlArtifact,
    teacher_artifact: JsonlArtifact,
    decision_artifact: JsonlArtifact,
    output_path: Path,
    output_sha256: str,
    codebook_path: Path,
    codebook_sha256: str,
    review_by_id: dict[str, dict[str, Any]],
    teacher_by_id: dict[str, dict[str, Any]],
    decision_by_id: dict[str, dict[str, Any]],
    review_order: list[str],
    gold_rows: list[dict[str, Any]],
    candidate_manifest_sha256: str,
    candidate_git_attestation_sha256: str,
    candidate_git_commit_sha: str,
    review_provenance_path: Path,
    review_provenance: dict[str, Any],
    review_prompt_path: Path,
    review_prompt_sha256: str,
) -> dict[str, Any]:
    sample_count = len(gold_rows)
    agreements = [row for row in gold_rows if bool(row["teacher_agreement"])]
    disagreements = [row for row in gold_rows if not bool(row["teacher_agreement"])]
    published_values = [
        _parse_aware_datetime(row["published_at_kst"], "published_at_kst")
        for row in review_by_id.values()
    ]
    effective_values = [
        _parse_iso_date(row["effective_trade_date"], "effective_trade_date")
        for row in review_by_id.values()
    ]
    provider_distribution = Counter(
        str(row.get("provider") or "UNKNOWN") for row in review_by_id.values()
    )
    transition_distribution = Counter(
        f"{row['teacher_sentiment']}->{row['sentiment']}" for row in disagreements
    )
    independent_agreements = [
        row for row in decision_by_id.values() if row["inter_reviewer_agreement"] is True
    ]
    unresolved = [row for row in decision_by_id.values() if row["final_sentiment"] == "UNRESOLVED"]
    item_set = sorted(review_by_id)
    source_record_hashes = sorted(
        (
            {
                "item_id": item_id,
                "source_record_sha256": str(teacher_by_id[item_id]["source_record_sha256"]),
            }
            for item_id in review_order
        ),
        key=lambda row: str(row["item_id"]),
    )
    teacher_generated = sorted(
        _parse_aware_datetime(row["generated_at_utc"], "generated_at_utc")
        for row in teacher_by_id.values()
    )
    provenance = {
        "review": {
            "schema_version": REVIEW_SCHEMA_VERSION,
            "dataset_version": _require_single_value(
                review_artifact.rows, "dataset_version", "원본 review"
            ),
            "partition": _require_single_value(review_artifact.rows, "partition", "원본 review"),
            "codebook_version": CODEBOOK_VERSION,
        },
        "teacher": {
            "schema_version": TEACHER_SCHEMA_VERSION,
            "provider": TEACHER_PROVIDER,
            "model_requested": _require_single_value(
                teacher_artifact.rows,
                "teacher_model_requested",
                "Qwen teacher silver",
            ),
            "model_served": _require_single_value(
                teacher_artifact.rows,
                "teacher_model_served",
                "Qwen teacher silver",
            ),
            "prompt_version": PROMPT_VERSION,
            "operational_rules_sha256": OPERATIONAL_RULES_SHA256,
            "sampling_seed": TEACHER_SAMPLING_SEED,
            "codebook_path": _display_path(codebook_path),
            "codebook_sha256": codebook_sha256,
            "model_blind": True,
            "market_blind": True,
            "gold_reviewer_visibility": GOLD_REVIEWER_VISIBILITY,
            "candidate_prediction_visibility": CANDIDATE_PREDICTION_VISIBILITY,
            "generated_at_utc_min": teacher_generated[0].isoformat(),
            "generated_at_utc_max": teacher_generated[-1].isoformat(),
        },
        "codex_review": {
            "required_status": APPROVED_STATUS,
            "protocol": "receipt-bound-two-independent-codex-reviewers-plus-adjudication/v1",
            "minimum_independent_reviewers": 2,
            "reviewer_distribution": dict(
                sorted(Counter(str(row["reviewer_id"]) for row in decision_by_id.values()).items())
            ),
            "teacher_is_advisory_only": True,
            "automatic_teacher_gold_promotion": False,
            "unresolved_excluded_from_gold": True,
            "candidate_manifest_sha256": candidate_manifest_sha256,
            "candidate_git_attestation_sha256": candidate_git_attestation_sha256,
            "candidate_git_commit_sha": candidate_git_commit_sha,
            "review_provenance_status": review_provenance["status"],
            "review_provenance_manifest_sha256": review_provenance[
                "merge_manifest_payload_sha256"
            ],
            "review_prompt_path": _display_path(review_prompt_path),
            "review_prompt_sha256": review_prompt_sha256,
        },
    }
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "status": "pass",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "sample_count": sample_count,
        "reviewed_item_count": len(review_order),
        "unresolved_excluded_count": len(unresolved),
        "artifacts": {
            "review_input": _display_path(review_artifact.path),
            "teacher_silver_input": _display_path(teacher_artifact.path),
            "codex_decisions_input": _display_path(decision_artifact.path),
            "review_provenance_input": _display_path(review_provenance_path),
            "review_prompt_input": _display_path(review_prompt_path),
            "gold_output": _display_path(output_path),
        },
        "file_sha256": {
            "review_input": review_artifact.sha256,
            "teacher_silver_input": teacher_artifact.sha256,
            "codex_decisions_input": decision_artifact.sha256,
            "review_provenance_input": review_artifact_record(review_provenance_path)["sha256"],
            "review_prompt_input": review_prompt_sha256,
            "gold_output": output_sha256,
        },
        "integrity": {
            "review_teacher_item_sets_exact": True,
            "review_decision_item_sets_exact": True,
            "source_records_exact": True,
            "source_record_hashes_exact": True,
            "teacher_input_hashes_exact": True,
            "codebook_file_hash_exact": True,
            "review_receipt_chain_exact": True,
            "review_prompt_hash_exact": True,
            "candidate_predictions_not_provided_to_review_context": True,
            "teacher_predictions_not_provided_to_review_context": True,
            "review_context_ids_independent": True,
            "item_id_set_sha256": _canonical_sha256(item_set),
            "source_record_set_sha256": _canonical_sha256(source_record_hashes),
            "provenance_sha256": _canonical_sha256(provenance),
        },
        "provenance": provenance,
        "label_distribution": dict(
            sorted(Counter(str(row["sentiment"]) for row in gold_rows).items())
        ),
        "qwen_final_agreement": {
            "agreement_count": len(agreements),
            "disagreement_count": len(disagreements),
            "agreement_rate": round(len(agreements) / sample_count, 6),
            "agreement_percentage": round(len(agreements) * 100.0 / sample_count, 2),
            "transition_distribution": dict(sorted(transition_distribution.items())),
            "disagreements": [
                {
                    "item_id": row["item_id"],
                    "teacher_sentiment": row["teacher_sentiment"],
                    "final_sentiment": row["sentiment"],
                    "reviewer_id": row["reviewer_id"],
                    "reviewed_at": row["reviewed_at"],
                    "review_note": row["review_note"],
                }
                for row in disagreements
            ],
        },
        "independent_reviewer_agreement": {
            "agreement_count": len(independent_agreements),
            "disagreement_count": len(review_order) - len(independent_agreements),
            "agreement_rate": round(len(independent_agreements) / len(review_order), 6),
            "adjudicated_count": len(review_order) - len(independent_agreements) - len(unresolved),
            "unresolved_count": len(unresolved),
        },
        "coverage": {
            "source_type_count": len({str(row["source_type"]) for row in gold_rows}),
            "source_type_distribution": dict(
                sorted(Counter(str(row["source_type"]) for row in gold_rows).items())
            ),
            "provider_count": len(provider_distribution),
            "provider_distribution": dict(sorted(provider_distribution.items())),
            "published_at_kst_min": min(published_values).isoformat(),
            "published_at_kst_max": max(published_values).isoformat(),
            "effective_trade_date_min": min(effective_values).isoformat(),
            "effective_trade_date_max": max(effective_values).isoformat(),
            "year_distribution": dict(
                sorted(Counter(value.year for value in effective_values).items())
            ),
            "stock_count": len({str(row["stock_code"]) for row in gold_rows}),
            "event_count": len({str(row["event_cluster_id"]) for row in gold_rows}),
            "document_count": len({str(row["document_id"]) for row in gold_rows}),
            "partition_distribution": dict(
                sorted(Counter(str(row["partition"]) for row in gold_rows).items())
            ),
        },
        "promotion_policy": (
            "Qwen teacher SILVER는 참고 신호로만 보존하며, 모든 행에 유효한 "
            "CODEX_REVIEW_APPROVED 결정을 요구한다."
        ),
    }


def _read_jsonl_artifact(path: Path, label: str) -> JsonlArtifact:
    expanded = path.expanduser()
    if expanded.is_symlink():
        raise ValueError(f"{label} JSONL symlink는 허용하지 않습니다: {path}")
    try:
        resolved = expanded.resolve(strict=True)
    except FileNotFoundError as error:
        raise FileNotFoundError(f"{label} JSONL 파일이 없습니다: {path}") from error
    if not resolved.is_file():
        raise ValueError(f"{label} 입력은 파일이어야 합니다: {resolved}")
    raw = resolved.read_bytes()
    if not raw or len(raw) > MAX_INPUT_BYTES:
        raise ValueError(f"{label} JSONL이 비어 있거나 크기 제한을 초과했습니다.")
    try:
        lines = raw.decode("utf-8").splitlines()
    except UnicodeDecodeError as error:
        raise ValueError(f"{label} JSONL은 UTF-8이어야 합니다.") from error
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"{resolved}:{line_number} JSON이 올바르지 않습니다.") from error
        if not isinstance(payload, dict):
            raise ValueError(f"{resolved}:{line_number} JSON 객체가 필요합니다.")
        rows.append(cast(dict[str, Any], payload))
    if not rows:
        raise ValueError(f"{label} JSONL에 유효한 행이 없습니다.")
    return JsonlArtifact(path=resolved, rows=tuple(rows), sha256=sha256(raw).hexdigest())


def _candidate_manifest_commitment(
    partition: str,
    source_type: str,
    review_artifact: JsonlArtifact,
    candidate_lock_path: Path | None,
    candidate_git_attestation_path: Path | None,
    *,
    project_root: Path,
) -> CandidateManifestCommitment:
    sealed = "SEALED" in partition
    if candidate_lock_path is None:
        if sealed:
            raise ValueError("봉인 Gold 승격에는 candidate lock manifest가 필요합니다.")
        return CandidateManifestCommitment(
            sha256="NOT_APPLICABLE_PRE_LOCK_DEVELOPMENT",
            locked_at=None,
            annotation_not_before=None,
            git_attestation_sha256="NOT_APPLICABLE_PRE_LOCK_DEVELOPMENT",
            git_commit_sha="NOT_APPLICABLE_PRE_LOCK_DEVELOPMENT",
        )
    if candidate_lock_path.is_symlink() or not candidate_lock_path.is_file():
        raise ValueError("candidate lock manifest가 없거나 symlink입니다.")
    raw = candidate_lock_path.read_bytes()
    payload = json.loads(raw)
    if (
        not isinstance(payload, dict)
        or payload.get("schema_version") not in SUPPORTED_CANDIDATE_LOCK_SCHEMAS
        or payload.get("selection_only") is not True
        or payload.get("public_test_evaluated_before_lock") is not False
        or payload.get("operational_sealed_gold_evaluated_before_lock") is not False
        or payload.get("external_git_commitment_required") is not True
    ):
        raise ValueError("candidate lock manifest 계약이 올바르지 않습니다.")
    locked_at = _parse_aware_datetime(payload.get("locked_at"), "candidate_lock.locked_at")
    if locked_at > datetime.now(UTC):
        raise ValueError("candidate lock 시각이 미래입니다.")
    if sealed and candidate_git_attestation_path is None:
        raise ValueError("봉인 Gold 승격에는 candidate Git attestation이 필요합니다.")
    if candidate_git_attestation_path is None:
        return CandidateManifestCommitment(
            sha256=sha256(raw).hexdigest(),
            locked_at=locked_at,
            annotation_not_before=locked_at,
            git_attestation_sha256="NOT_APPLICABLE_NON_SEALED_PARTITION",
            git_commit_sha="NOT_APPLICABLE_NON_SEALED_PARTITION",
        )
    attestation = validate_candidate_git_attestation(
        candidate_git_attestation_path,
        candidate_lock_path,
        project_root=project_root,
    )
    manifest_sha256 = sha256(raw).hexdigest()
    if attestation["candidate_lock_sha256"] != manifest_sha256:
        raise ValueError("Git attestation과 candidate lock manifest hash가 다릅니다.")
    _validate_sealed_review_commitment(
        payload,
        review_artifact,
        partition=partition,
        source_type=source_type,
        project_root=project_root,
    )
    committer_time = _parse_aware_datetime(
        attestation["committer_time_iso"],
        "candidate_git_attestation.committer_time_iso",
    )
    return CandidateManifestCommitment(
        sha256=manifest_sha256,
        locked_at=locked_at,
        annotation_not_before=max(locked_at, committer_time),
        git_attestation_sha256=str(attestation["sha256"]),
        git_commit_sha=str(attestation["commit_sha"]),
    )


def _validate_sealed_review_commitment(
    lock: dict[str, Any],
    review_artifact: JsonlArtifact,
    *,
    partition: str,
    source_type: str,
    project_root: Path,
) -> None:
    reservations = lock.get("sealed_reservations")
    if source_type not in {"NEWS", "DISCLOSURE"} or not isinstance(reservations, dict):
        raise ValueError("봉인 review source_type 또는 reservation 계약이 올바르지 않습니다.")
    reservation = reservations.get(source_type)
    if not isinstance(reservation, dict):
        raise ValueError(f"candidate lock에 {source_type} reservation이 없습니다.")
    raw_path = reservation.get("path")
    if not isinstance(raw_path, str) or not raw_path:
        raise ValueError("candidate lock reservation 경로가 올바르지 않습니다.")
    expected_path = (project_root / raw_path).resolve()
    try:
        expected_path.relative_to(project_root.resolve())
    except ValueError as error:
        raise ValueError("candidate lock reservation 경로가 project root 밖입니다.") from error
    if (
        reservation.get("source_type") != source_type
        or reservation.get("partition") != partition
        or expected_path != review_artifact.path
        or reservation.get("sha256") != review_artifact.sha256
        or reservation.get("bytes") != review_artifact.path.stat().st_size
        or reservation.get("sample_count") != len(review_artifact.rows)
    ):
        raise ValueError("봉인 review가 candidate lock reservation commitment와 다릅니다.")


def _validate_post_lock_annotations(
    teachers: dict[str, dict[str, Any]],
    decisions: dict[str, dict[str, Any]],
    locked_at: datetime,
) -> None:
    """후보 고정 전에 생성된 판정이 봉인 Gold로 유입되지 않도록 차단한다."""
    for item_id, teacher in teachers.items():
        generated_at = _parse_aware_datetime(
            teacher.get("generated_at_utc"), f"{item_id}.generated_at_utc"
        )
        if generated_at < locked_at:
            raise ValueError(
                "봉인 Gold teacher 판정 시각이 candidate lock보다 빠릅니다: "
                f"{item_id}.generated_at_utc"
            )
    for item_id, decision in decisions.items():
        timestamps = {
            "reviewer_1.reviewed_at": decision["reviewer_1"]["reviewed_at"],
            "reviewer_2.reviewed_at": decision["reviewer_2"]["reviewed_at"],
            "reviewed_at": decision["reviewed_at"],
        }
        adjudication = decision.get("adjudication")
        if isinstance(adjudication, dict):
            timestamps["adjudication.adjudicated_at"] = adjudication["adjudicated_at"]
        for field, value in timestamps.items():
            reviewed_at = _parse_aware_datetime(value, f"{item_id}.{field}")
            if reviewed_at < locked_at:
                raise ValueError(
                    f"봉인 Gold 판정 시각이 candidate lock보다 빠릅니다: {item_id}.{field}"
                )


def _load_codebook(path: Path) -> tuple[Path, str]:
    expanded = path.expanduser()
    if expanded.is_symlink():
        raise ValueError(f"코드북 symlink는 허용하지 않습니다: {path}")
    try:
        resolved = expanded.resolve(strict=True)
    except FileNotFoundError as error:
        raise FileNotFoundError(f"코드북 파일이 없습니다: {path}") from error
    raw = resolved.read_bytes()
    if not raw or len(raw) > MAX_CODEBOOK_BYTES:
        raise ValueError("코드북이 비어 있거나 크기 제한을 초과했습니다.")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("코드북은 UTF-8이어야 합니다.") from error
    if any(label not in text for label in SENTIMENT_LABELS):
        raise ValueError("코드북에 필수 감성 라벨이 없습니다.")
    return resolved, sha256(raw).hexdigest()


def _validate_distinct_paths(*paths: Path) -> None:
    if len(set(paths)) != len(paths):
        raise ValueError("입력·Gold 출력·보고서 경로는 모두 달라야 합니다.")


def _resolve_output_path(path: Path, label: str) -> Path:
    expanded = path.expanduser()
    if expanded.is_symlink():
        raise ValueError(f"{label} symlink는 허용하지 않습니다: {path}")
    return expanded.resolve()


def _assert_exact_item_set(label: str, actual: set[str], expected: set[str]) -> None:
    if actual == expected:
        return
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    raise ValueError(
        f"{label} item_id 집합이 원본 review와 다릅니다. "
        f"missing={missing[:10]}, unexpected={unexpected[:10]}"
    )


def _require_single_value(
    rows: tuple[dict[str, Any], ...],
    field: str,
    context: str,
) -> object:
    values = {_hashable_value(row.get(field)) for row in rows}
    if len(values) != 1:
        raise ValueError(f"{context}.{field} provenance가 행마다 다릅니다.")
    value = next(iter(values))
    if value in {None, ""}:
        raise ValueError(f"{context}.{field} provenance가 비어 있습니다.")
    return value


def _hashable_value(value: object) -> object:
    if isinstance(value, (dict, list)):
        return _canonical_sha256(value)
    return value


def _required_string(value: object, field: str, *, max_length: int = 8_192) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError(f"{field}는 공백 없는 문자열이어야 합니다.")
    if len(value) > max_length or CONTROL_CHARACTER_PATTERN.search(value):
        raise ValueError(f"{field} 길이 또는 제어문자가 올바르지 않습니다.")
    return value


def _parse_aware_datetime(value: object, field: str) -> datetime:
    raw = _required_string(value, field, max_length=64)
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{field}는 ISO 8601 날짜·시간이어야 합니다.") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field}에는 시간대가 필요합니다.")
    return parsed


def _parse_iso_date(value: object, field: str) -> date:
    raw = _required_string(value, field, max_length=10)
    try:
        parsed = date.fromisoformat(raw)
    except ValueError as error:
        raise ValueError(f"{field}는 YYYY-MM-DD 날짜여야 합니다.") from error
    if parsed.isoformat() != raw:
        raise ValueError(f"{field}는 YYYY-MM-DD 날짜여야 합니다.")
    return parsed


def _resolve_item_id(row: dict[str, Any], source_sha256: str) -> str:
    for key in ("review_key", "annotation_id", "item_id"):
        value = row.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    document_id = row.get("document_id")
    target = row.get("target_security") or row.get("stock_code")
    if isinstance(document_id, str) and document_id.strip():
        target_value = target.strip() if isinstance(target, str) else "UNSPECIFIED"
        return f"{document_id.strip()}::{target_value}"
    content_hash = row.get("content_hash")
    if isinstance(content_hash, str) and content_hash.strip():
        target_value = target.strip() if isinstance(target, str) else "UNSPECIFIED"
        return f"{content_hash.strip()}::{target_value}"
    return source_sha256


def _resolve_teacher_text(row: dict[str, Any], context: str) -> tuple[str, str]:
    explicit_text = row.get("text")
    if isinstance(explicit_text, str) and explicit_text.strip():
        scope = row.get("input_scope")
        return explicit_text.strip(), str(scope).strip() if scope else "TEXT"
    parts: list[str] = []
    scopes: list[str] = []
    for key in ("title", "full_text", "snippet", "content"):
        value = row.get(key)
        if isinstance(value, str) and value.strip() and value.strip() not in parts:
            parts.append(value.strip())
            scopes.append(key.upper())
    if not parts:
        raise ValueError(f"{context}에 라벨링할 text가 없습니다.")
    return "\n".join(parts), "_".join(scopes)


def _resolve_target_security(row: dict[str, Any]) -> dict[str, str]:
    target = row.get("target_security")
    if isinstance(target, str) and target.strip():
        return {"identifier": target.strip()}
    if isinstance(target, dict):
        identifier = target.get("identifier") or target.get("stock_code")
        name = target.get("name") or target.get("stock_name")
        return {
            "identifier": str(identifier).strip() if identifier else "UNSPECIFIED",
            "name": str(name).strip() if name else "",
        }
    stock_code = row.get("stock_code")
    stock_name = row.get("stock_name")
    return {
        "identifier": str(stock_code).strip() if stock_code else "UNSPECIFIED",
        "name": str(stock_name).strip() if stock_name else "",
    }


def _first_string(row: dict[str, Any], *fields: str) -> str:
    for field in fields:
        value = row.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _canonical_sha256(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _encode_jsonl(rows: list[dict[str, Any]]) -> bytes:
    return "".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows
    ).encode("utf-8")


def _atomic_write_bytes(path: Path, payload: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise ValueError(f"출력이 이미 존재하거나 symlink입니다: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            os.chmod(temporary_path, 0o600)
            temporary.write(payload)
            temporary.flush()
            os.fsync(temporary.fileno())
        if path.exists() or path.is_symlink():
            raise ValueError(f"출력이 이미 존재하거나 symlink입니다: {path}")
        os.replace(temporary_path, path)
        temporary_path = None
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(PROJECT_ROOT.resolve()))
    except ValueError:
        return str(resolved)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Qwen SILVER와 독립 Codex 결정을 검증해 K-FNSPID 감성 Gold를 만든다."
    )
    parser.add_argument("--review-path", type=Path, default=DEFAULT_REVIEW_PATH)
    parser.add_argument("--teacher-path", type=Path, default=DEFAULT_TEACHER_PATH)
    parser.add_argument("--decisions-path", type=Path, default=DEFAULT_DECISIONS_PATH)
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--codebook-path", type=Path, default=DEFAULT_CODEBOOK_PATH)
    parser.add_argument("--review-provenance-path", type=Path, required=True)
    parser.add_argument(
        "--review-prompt-path",
        type=Path,
        default=DEFAULT_REVIEW_PROMPT_PATH,
    )
    parser.add_argument("--candidate-lock-path", type=Path)
    parser.add_argument(
        "--candidate-git-attestation-path",
        type=Path,
        default=DEFAULT_GIT_ATTESTATION_PATH,
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    summary = promote_gold(
        review_path=args.review_path,
        teacher_path=args.teacher_path,
        decisions_path=args.decisions_path,
        output_path=args.output_path,
        report_path=args.report_path,
        codebook_path=args.codebook_path,
        review_provenance_path=args.review_provenance_path,
        review_prompt_path=args.review_prompt_path,
        candidate_lock_path=args.candidate_lock_path,
        candidate_git_attestation_path=args.candidate_git_attestation_path,
    )
    print(json.dumps(summary.as_dict(), ensure_ascii=False))


if __name__ == "__main__":
    main()
