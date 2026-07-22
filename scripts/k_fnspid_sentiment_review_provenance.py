from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from collections import Counter
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, cast
from uuid import UUID

RECEIPT_SCHEMA = "k-fnspid-sentiment-review-receipt/v1"
STAGE_MANIFEST_SCHEMA = "k-fnspid-sentiment-review-stage-manifest/v1"
MERGE_MANIFEST_SCHEMA = "k-fnspid-sentiment-dual-review-provenance/v1"
ADJUDICATION_MANIFEST_SCHEMA = "k-fnspid-sentiment-adjudication-provenance/v1"
VERIFIED_STATUS = "VERIFIED_BLIND_PROVENANCE"
LEGACY_STATUS = "LEGACY_UNVERIFIED"
REVIEW_PACKET_KIND = "BLIND_REVIEW_SOURCE"
ADJUDICATION_PACKET_KIND = "BLIND_ADJUDICATION_DISAGREEMENTS"
REVIEW_ROLE = "REVIEWER"
ADJUDICATOR_ROLE = "ADJUDICATOR"
NONEXPOSURE_VALUE = "NOT_PROVIDED_TO_REVIEW_CONTEXT"
CONTEXT_ISOLATION = "FRESH_CONTEXT_WITHOUT_PRIOR_REVIEW_OR_MODEL_OUTPUT"
MAX_ARTIFACT_BYTES = 512 * 1024 * 1024
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")
CONTROL_CHARACTER_PATTERN = re.compile(r"[\x00-\x1f\x7f]")

# 이 필드는 검수 입력에 존재하는 것만으로도 모델 또는 약지도 결과 노출 가능성이 있다.
FORBIDDEN_REVIEW_INPUT_KEYS = frozenset(
    {
        "sentiment",
        "final_sentiment",
        "label",
        "labels",
        "label_evidence",
        "prediction",
        "predictions",
        "predicted_sentiment",
        "candidate_prediction",
        "candidate_predictions",
        "candidate_probabilities",
        "teacher_sentiment",
        "teacher_prediction",
        "teacher_predictions",
        "teacher_confidence",
        "teacher_rationale",
        "logit",
        "logits",
        "probability",
        "probabilities",
        "score",
        "scores",
        "future_return",
        "market_return",
        "abnormal_return",
        "price_reaction",
    }
)
FORBIDDEN_PREFIXES = ("candidate_", "teacher_", "model_output_")


class LegacyUnverifiedError(ValueError):
    """과거 산출물에 검증 가능한 receipt가 없음을 명시한다."""


def canonical_sha256(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256(_read_bytes(path, "artifact")).hexdigest()


def artifact_record(path: Path, *, sample_count: int | None = None) -> dict[str, object]:
    raw = _read_bytes(path, "artifact")
    record: dict[str, object] = {
        "path": str(path),
        "bytes": len(raw),
        "sha256": sha256(raw).hexdigest(),
    }
    if sample_count is not None:
        record["sample_count"] = sample_count
    return record


def read_jsonl(path: Path, *, allow_empty: bool = False) -> list[dict[str, Any]]:
    raw = _read_bytes(path, "JSONL")
    try:
        lines = raw.decode("utf-8").splitlines()
    except UnicodeDecodeError as error:
        raise ValueError(f"JSONL은 UTF-8이어야 합니다: {path}") from error
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"JSONL {line_number}행이 올바르지 않습니다: {path}") from error
        if not isinstance(value, dict):
            raise ValueError(f"JSONL {line_number}행은 객체여야 합니다: {path}")
        rows.append(cast(dict[str, Any], value))
    if not rows and not allow_empty:
        raise ValueError(f"JSONL이 비었습니다: {path}")
    return rows


def read_json(path: Path) -> dict[str, Any]:
    raw = _read_bytes(path, "JSON")
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError(f"JSON이 올바르지 않습니다: {path}") from error
    if not isinstance(value, dict):
        raise ValueError(f"JSON 최상위는 객체여야 합니다: {path}")
    return cast(dict[str, Any], value)


def write_json_exclusive(path: Path, payload: dict[str, Any]) -> None:
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    _write_exclusive(path, encoded)


def receipt_payload_sha256(payload: dict[str, Any]) -> str:
    unsigned = {key: value for key, value in payload.items() if key != "receipt_payload_sha256"}
    return canonical_sha256(unsigned)


def signed_payload(payload: dict[str, Any], *, signature_field: str) -> dict[str, Any]:
    if signature_field in payload:
        raise ValueError(f"서명 필드가 이미 존재합니다: {signature_field}")
    signed = dict(payload)
    signed[signature_field] = canonical_sha256(payload)
    return signed


def validate_signed_payload(
    payload: dict[str, Any],
    *,
    schema: str,
    signature_field: str,
    label: str,
) -> None:
    if payload.get("schema_version") != schema or payload.get("status") != VERIFIED_STATUS:
        raise LegacyUnverifiedError(
            f"{LEGACY_STATUS}: {label}에 검증 가능한 v1 provenance가 없습니다. "
            "예측 비노출 상태로 재검수해야 합니다."
        )
    signature = payload.get(signature_field)
    unsigned = {key: value for key, value in payload.items() if key != signature_field}
    if not isinstance(signature, str) or signature != canonical_sha256(unsigned):
        raise ValueError(f"{label} 자체 해시가 다릅니다.")


def review_item_id(row: dict[str, Any]) -> str:
    for field in ("review_key", "annotation_id", "item_id"):
        value = row.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    document_id = str(row.get("document_id", "")).strip()
    target = str(
        row.get("target_security") or row.get("stock_code") or "UNSPECIFIED"
    ).strip()
    if not document_id:
        raise ValueError("review packet에 item_id 원천이 없습니다.")
    return f"{document_id}::{target}"


def audit_blind_packet(rows: list[dict[str, Any]], *, packet_kind: str) -> None:
    if packet_kind not in {REVIEW_PACKET_KIND, ADJUDICATION_PACKET_KIND}:
        raise ValueError("packet_kind가 올바르지 않습니다.")
    for line_number, row in enumerate(rows, start=1):
        if packet_kind == REVIEW_PACKET_KIND:
            for field in ("final_sentiment", "reviewer_id", "reviewed_at", "review_note"):
                if row.get(field) not in {None, ""}:
                    raise ValueError(
                        f"blind review packet {line_number}행의 {field}가 비어 있지 않습니다."
                    )
        _audit_mapping(row, packet_kind=packet_kind, context=f"packet[{line_number}]")


def input_scope(
    rows: list[dict[str, Any]],
    *,
    packet_kind: str,
    row_start: int,
    row_end: int,
    selected_item_ids: list[str] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if row_start < 1 or row_end < row_start or row_end > len(rows):
        raise ValueError("receipt 입력 row 범위가 packet을 벗어났습니다.")
    bounded = rows[row_start - 1 : row_end]
    if selected_item_ids is None:
        selected = bounded
    else:
        if not selected_item_ids or len(selected_item_ids) != len(set(selected_item_ids)):
            raise ValueError("receipt selected_item_ids가 비었거나 중복됩니다.")
        bounded_by_id = {
            review_item_id(row)
            if packet_kind == REVIEW_PACKET_KIND
            else _required_item_id(row): row
            for row in bounded
        }
        if any(item_id not in bounded_by_id for item_id in selected_item_ids):
            raise ValueError("receipt selected_item_ids가 지정한 row 경계를 벗어났습니다.")
        packet_order = [
            review_item_id(row)
            if packet_kind == REVIEW_PACKET_KIND
            else _required_item_id(row)
            for row in bounded
        ]
        expected_order = [item_id for item_id in packet_order if item_id in selected_item_ids]
        if selected_item_ids != expected_order:
            raise ValueError("receipt selected_item_ids가 packet 순서를 보존하지 않습니다.")
        if selected_item_ids[0] != packet_order[0] or selected_item_ids[-1] != packet_order[-1]:
            raise ValueError("receipt row 경계는 selected_item_ids의 실제 경계와 같아야 합니다.")
        selected = [bounded_by_id[item_id] for item_id in selected_item_ids]
    ids = [
        review_item_id(row) if packet_kind == REVIEW_PACKET_KIND else _required_item_id(row)
        for row in selected
    ]
    if len(ids) != len(set(ids)):
        raise ValueError("receipt 입력 범위의 item_id가 중복됩니다.")
    field_sets = [sorted(str(key) for key in row) for row in selected]
    source_types = Counter(str(row.get("source_type", "UNSPECIFIED")) for row in selected)
    profile: dict[str, Any] = {
        "row_start_inclusive": row_start,
        "row_end_inclusive": row_end,
        "item_count": len(ids),
        "first_item_id": ids[0],
        "last_item_id": ids[-1],
        "item_id_order_sha256": canonical_sha256(ids),
        "item_id_set_sha256": canonical_sha256(sorted(ids)),
        "input_field_sets_sha256": canonical_sha256(field_sets),
        "source_type_distribution": dict(sorted(source_types.items())),
    }
    if selected_item_ids is not None:
        profile["selected_item_ids"] = ids
    return selected, profile


def create_review_receipt(
    *,
    packet_path: Path,
    decision_path: Path,
    codebook_path: Path,
    prompt_path: Path,
    output_path: Path,
    packet_kind: str,
    role: str,
    reviewer_id: str,
    reviewer_model: str,
    reviewer_model_version: str,
    independent_run_id: str,
    context_id: str,
    row_start: int,
    row_end: int,
    run_started_at: str,
    run_completed_at: str,
    selected_item_ids: list[str] | None = None,
) -> dict[str, Any]:
    if role not in {REVIEW_ROLE, ADJUDICATOR_ROLE}:
        raise ValueError("review role이 올바르지 않습니다.")
    if (role == REVIEW_ROLE) != (packet_kind == REVIEW_PACKET_KIND):
        raise ValueError("review role과 packet_kind 조합이 올바르지 않습니다.")
    for value, field in (
        (reviewer_id, "reviewer_id"),
        (reviewer_model, "reviewer_model"),
        (reviewer_model_version, "reviewer_model_version"),
    ):
        _required_text(value, field)
    _uuid4(independent_run_id, "independent_run_id")
    _uuid4(context_id, "context_id")
    if independent_run_id == context_id:
        raise ValueError("run ID와 context ID는 달라야 합니다.")
    started = _aware_datetime(run_started_at, "run_started_at")
    completed = _aware_datetime(run_completed_at, "run_completed_at")
    if completed <= started:
        raise ValueError("review run 종료 시각은 시작 이후여야 합니다.")

    packet_rows = read_jsonl(packet_path)
    audit_blind_packet(packet_rows, packet_kind=packet_kind)
    selected_rows, scope = input_scope(
        packet_rows,
        packet_kind=packet_kind,
        row_start=row_start,
        row_end=row_end,
        selected_item_ids=selected_item_ids,
    )
    expected_ids = [
        review_item_id(row) if packet_kind == REVIEW_PACKET_KIND else _required_item_id(row)
        for row in selected_rows
    ]
    decision_rows = read_jsonl(decision_path, allow_empty=False)
    decision_ids = [_required_item_id(row) for row in decision_rows]
    if decision_ids != expected_ids:
        raise ValueError("receipt decision item_id 순서나 범위가 packet 입력과 다릅니다.")
    timestamp_field = "reviewed_at" if role == REVIEW_ROLE else "adjudicated_at"
    identity_field = "reviewer_id" if role == REVIEW_ROLE else "adjudicator_id"
    for index, row in enumerate(decision_rows, start=1):
        if row.get(identity_field) != reviewer_id:
            raise ValueError(f"decision {index}행의 {identity_field}가 receipt와 다릅니다.")
        decision_time = _aware_datetime(str(row.get(timestamp_field, "")), timestamp_field)
        if not started <= decision_time <= completed:
            raise ValueError(f"decision {index}행 시각이 review run 범위 밖입니다.")

    blindness = {
        "candidate_prediction_visibility": NONEXPOSURE_VALUE,
        "teacher_prediction_visibility": NONEXPOSURE_VALUE,
        "market_outcome_visibility": NONEXPOSURE_VALUE,
        "packet_forbidden_fields_audited": True,
    }
    if role == ADJUDICATOR_ROLE:
        blindness["reviewer_decision_visibility"] = NONEXPOSURE_VALUE
    payload: dict[str, Any] = {
        "schema_version": RECEIPT_SCHEMA,
        "status": VERIFIED_STATUS,
        "role": role,
        "packet_kind": packet_kind,
        "reviewer": {
            "reviewer_id": reviewer_id,
            "reviewer_type": "CODEX_AI",
            "model_name": reviewer_model,
            "model_version": reviewer_model_version,
        },
        "run": {
            "independent_run_id": independent_run_id,
            "context_id": context_id,
            "context_parent_id": None,
            "context_isolation_commitment": CONTEXT_ISOLATION,
            "started_at": run_started_at,
            "completed_at": run_completed_at,
        },
        "blindness": blindness,
        "input_scope": scope,
        "artifacts": {
            "packet": artifact_record(packet_path, sample_count=len(packet_rows)),
            "decision": artifact_record(decision_path, sample_count=len(decision_rows)),
            "codebook": artifact_record(codebook_path),
            "prompt": artifact_record(prompt_path),
        },
    }
    payload["receipt_payload_sha256"] = receipt_payload_sha256(payload)
    write_json_exclusive(output_path, payload)
    return payload


def validate_review_receipt(
    receipt_path: Path,
    *,
    packet_path: Path,
    decision_path: Path,
    codebook_path: Path,
    prompt_path: Path,
    expected_packet_kind: str,
    expected_role: str,
) -> dict[str, Any]:
    if not receipt_path.exists():
        raise LegacyUnverifiedError(
            f"{LEGACY_STATUS}: review receipt가 없습니다. 예측 비노출 상태로 재검수해야 합니다."
        )
    receipt = read_json(receipt_path)
    validate_signed_payload(
        receipt,
        schema=RECEIPT_SCHEMA,
        signature_field="receipt_payload_sha256",
        label="review receipt",
    )
    if receipt.get("role") != expected_role or receipt.get("packet_kind") != expected_packet_kind:
        raise ValueError("review receipt role또는 packet_kind가 다릅니다.")
    reviewer = _mapping(receipt.get("reviewer"), "reviewer")
    run = _mapping(receipt.get("run"), "run")
    blindness = _mapping(receipt.get("blindness"), "blindness")
    for field in ("reviewer_id", "model_name", "model_version"):
        _required_text(str(reviewer.get(field, "")), f"reviewer.{field}")
    if reviewer.get("reviewer_type") != "CODEX_AI":
        raise ValueError("review receipt reviewer_type이 다릅니다.")
    _uuid4(str(run.get("independent_run_id", "")), "independent_run_id")
    _uuid4(str(run.get("context_id", "")), "context_id")
    if (
        run.get("independent_run_id") == run.get("context_id")
        or run.get("context_parent_id") is not None
        or run.get("context_isolation_commitment") != CONTEXT_ISOLATION
    ):
        raise ValueError("review context 독립성 commitment가 올바르지 않습니다.")
    started = _aware_datetime(str(run.get("started_at", "")), "run.started_at")
    completed = _aware_datetime(str(run.get("completed_at", "")), "run.completed_at")
    if completed <= started:
        raise ValueError("review receipt 시각 범위가 올바르지 않습니다.")
    if (
        blindness.get("candidate_prediction_visibility") != NONEXPOSURE_VALUE
        or blindness.get("teacher_prediction_visibility") != NONEXPOSURE_VALUE
        or blindness.get("market_outcome_visibility") != NONEXPOSURE_VALUE
        or blindness.get("packet_forbidden_fields_audited") is not True
    ):
        raise ValueError("review receipt 비노출 commitment가 완전하지 않습니다.")
    if (
        expected_role == ADJUDICATOR_ROLE
        and blindness.get("reviewer_decision_visibility") != NONEXPOSURE_VALUE
    ):
        raise ValueError("adjudication receipt reviewer decision 비노출 commitment가 없습니다.")

    packet_rows = read_jsonl(packet_path)
    audit_blind_packet(packet_rows, packet_kind=expected_packet_kind)
    decision_rows = read_jsonl(decision_path)
    scope = _mapping(receipt.get("input_scope"), "input_scope")
    row_start = _positive_int(scope.get("row_start_inclusive"), "row_start_inclusive")
    row_end = _positive_int(scope.get("row_end_inclusive"), "row_end_inclusive")
    selected_item_ids_value = scope.get("selected_item_ids")
    selected_item_ids: list[str] | None
    if selected_item_ids_value is None:
        selected_item_ids = None
    elif isinstance(selected_item_ids_value, list) and all(
        isinstance(item_id, str) and item_id for item_id in selected_item_ids_value
    ):
        selected_item_ids = selected_item_ids_value
    else:
        raise ValueError("review receipt selected_item_ids 스키마가 올바르지 않습니다.")
    selected_rows, expected_scope = input_scope(
        packet_rows,
        packet_kind=expected_packet_kind,
        row_start=row_start,
        row_end=row_end,
        selected_item_ids=selected_item_ids,
    )
    if scope != expected_scope:
        raise ValueError("review receipt input_scope가 packet 실제 범위와 다릅니다.")
    expected_ids = [
        review_item_id(row)
        if expected_packet_kind == REVIEW_PACKET_KIND
        else _required_item_id(row)
        for row in selected_rows
    ]
    if [_required_item_id(row) for row in decision_rows] != expected_ids:
        raise ValueError("review receipt와 decision item_id 범위가 다릅니다.")
    artifacts = _mapping(receipt.get("artifacts"), "artifacts")
    for name, path, count in (
        ("packet", packet_path, len(packet_rows)),
        ("decision", decision_path, len(decision_rows)),
        ("codebook", codebook_path, None),
        ("prompt", prompt_path, None),
    ):
        _validate_artifact_record(artifacts.get(name), path, sample_count=count, label=name)
    return receipt


def assert_independent_receipts(receipts: list[dict[str, Any]]) -> None:
    reviewer_ids: list[str] = []
    run_ids: list[str] = []
    context_ids: list[str] = []
    for receipt in receipts:
        reviewer = _mapping(receipt.get("reviewer"), "reviewer")
        run = _mapping(receipt.get("run"), "run")
        reviewer_ids.append(str(reviewer["reviewer_id"]))
        run_ids.append(str(run["independent_run_id"]))
        context_ids.append(str(run["context_id"]))
    for values, label in (
        (reviewer_ids, "reviewer_id"),
        (run_ids, "independent_run_id"),
        (context_ids, "context_id"),
    ):
        if len(values) != len(set(values)):
            raise ValueError(f"독립 검수 receipt의 {label}가 중복됩니다.")


def validate_manifest_artifact(
    manifest: dict[str, Any],
    *,
    field: str,
    path: Path,
    sample_count: int | None,
) -> None:
    artifacts = _mapping(manifest.get("artifacts"), "manifest.artifacts")
    _validate_artifact_record(artifacts.get(field), path, sample_count=sample_count, label=field)


def validate_dual_review_manifest(
    manifest_path: Path,
    *,
    review_path: Path,
    decision_path: Path,
    codebook_path: Path,
    prompt_path: Path,
) -> dict[str, Any]:
    if not manifest_path.exists():
        raise LegacyUnverifiedError(
            f"{LEGACY_STATUS}: dual-review provenance manifest가 없습니다. "
            "예측 비노출 상태로 재검수해야 합니다."
        )
    manifest = read_json(manifest_path)
    validate_signed_payload(
        manifest,
        schema=MERGE_MANIFEST_SCHEMA,
        signature_field="merge_manifest_payload_sha256",
        label="dual-review provenance manifest",
    )
    if (
        manifest.get("context_isolation_commitment") != CONTEXT_ISOLATION
        or manifest.get("exact_item_set") is not True
    ):
        raise ValueError("dual-review manifest 독립성 계약이 올바르지 않습니다.")
    blindness = _mapping(manifest.get("blindness"), "manifest.blindness")
    if any(
        blindness.get(field) != NONEXPOSURE_VALUE
        for field in (
            "candidate_prediction_visibility",
            "teacher_prediction_visibility",
            "market_outcome_visibility",
        )
    ):
        raise ValueError("dual-review manifest 비노출 commitment가 완전하지 않습니다.")
    review_rows = read_jsonl(review_path)
    decision_rows = read_jsonl(decision_path)
    validate_manifest_artifact(
        manifest,
        field="review_packet",
        path=review_path,
        sample_count=len(review_rows),
    )
    validate_manifest_artifact(
        manifest,
        field="merged_decision",
        path=decision_path,
        sample_count=len(decision_rows),
    )
    validate_manifest_artifact(manifest, field="codebook", path=codebook_path, sample_count=None)
    validate_manifest_artifact(manifest, field="prompt", path=prompt_path, sample_count=None)

    artifacts = _mapping(manifest.get("artifacts"), "manifest.artifacts")
    receipts: list[dict[str, Any]] = []
    stage_decision_maps: dict[str, dict[str, dict[str, Any]]] = {}
    expected_stage_hashes = _mapping(
        manifest.get("stage_manifest_payload_sha256"),
        "stage_manifest_payload_sha256",
    )
    for stage_name in ("stage_1", "stage_2"):
        stage_manifest_record = _mapping(
            artifacts.get(f"{stage_name}_manifest"),
            f"{stage_name}_manifest",
        )
        stage_decision_record = _mapping(
            artifacts.get(f"{stage_name}_decision"),
            f"{stage_name}_decision",
        )
        stage_manifest_path = _record_path(stage_manifest_record, f"{stage_name}_manifest")
        stage_decision_path = _record_path(stage_decision_record, f"{stage_name}_decision")
        stage_decisions = read_jsonl(stage_decision_path)
        stage_decision_maps[stage_name] = {
            _required_item_id(row): row for row in stage_decisions
        }
        if len(stage_decision_maps[stage_name]) != len(stage_decisions):
            raise ValueError(f"{stage_name} merged decision item_id가 중복됩니다.")
        _validate_artifact_record(
            stage_manifest_record,
            stage_manifest_path,
            sample_count=None,
            label=f"{stage_name}_manifest",
        )
        _validate_artifact_record(
            stage_decision_record,
            stage_decision_path,
            sample_count=len(stage_decisions),
            label=f"{stage_name}_decision",
        )
        stage_manifest = read_json(stage_manifest_path)
        validate_signed_payload(
            stage_manifest,
            schema=STAGE_MANIFEST_SCHEMA,
            signature_field="stage_manifest_payload_sha256",
            label=f"{stage_name} manifest",
        )
        if (
            expected_stage_hashes.get(stage_name)
            != stage_manifest.get("stage_manifest_payload_sha256")
        ):
            raise ValueError(f"{stage_name} manifest 해시가 dual-review chain과 다릅니다.")
        validate_manifest_artifact(
            stage_manifest,
            field="review_packet",
            path=review_path,
            sample_count=len(review_rows),
        )
        validate_manifest_artifact(
            stage_manifest,
            field="merged_decision",
            path=stage_decision_path,
            sample_count=len(stage_decisions),
        )
        validate_manifest_artifact(
            stage_manifest,
            field="codebook",
            path=codebook_path,
            sample_count=None,
        )
        validate_manifest_artifact(
            stage_manifest,
            field="prompt",
            path=prompt_path,
            sample_count=None,
        )
        part_chain = stage_manifest.get("part_chain")
        if not isinstance(part_chain, list) or not part_chain:
            raise ValueError(f"{stage_name} part_chain이 비었습니다.")
        combined: dict[str, dict[str, Any]] = {}
        for raw_part in part_chain:
            part = _mapping(raw_part, f"{stage_name}.part")
            part_record = _mapping(part.get("decision"), "part.decision")
            receipt_record = _mapping(part.get("receipt"), "part.receipt")
            part_path = _record_path(part_record, "part.decision")
            receipt_path = _record_path(receipt_record, "part.receipt")
            part_rows = read_jsonl(part_path)
            _validate_artifact_record(
                part_record,
                part_path,
                sample_count=len(part_rows),
                label="part.decision",
            )
            _validate_artifact_record(
                receipt_record,
                receipt_path,
                sample_count=None,
                label="part.receipt",
            )
            receipt = validate_review_receipt(
                receipt_path,
                packet_path=review_path,
                decision_path=part_path,
                codebook_path=codebook_path,
                prompt_path=prompt_path,
                expected_packet_kind=REVIEW_PACKET_KIND,
                expected_role=REVIEW_ROLE,
            )
            if part.get("receipt_payload_sha256") != receipt["receipt_payload_sha256"]:
                raise ValueError("stage part receipt 해시가 다릅니다.")
            receipts.append(receipt)
            for row in part_rows:
                item_id = _required_item_id(row)
                if item_id in combined:
                    raise ValueError("stage part item_id가 중복됩니다.")
                combined[item_id] = row
        if [combined.get(_required_item_id(row)) for row in stage_decisions] != stage_decisions:
            raise ValueError(f"{stage_name} part와 merged decision이 다릅니다.")

    disagreement_count = manifest.get("disagreement_count")
    if isinstance(disagreement_count, bool) or not isinstance(disagreement_count, int):
        raise ValueError("dual-review disagreement_count가 정수가 아닙니다.")
    adjudication_by_id: dict[str, dict[str, Any]] = {}
    if disagreement_count > 0:
        packet_record = _mapping(artifacts.get("adjudication_packet"), "adjudication_packet")
        decision_record = _mapping(
            artifacts.get("adjudication_decision"), "adjudication_decision"
        )
        packet_path = _record_path(packet_record, "adjudication_packet")
        adjudication_path = _record_path(decision_record, "adjudication_decision")
        adjudication_rows = read_jsonl(adjudication_path)
        adjudication_by_id = {
            _required_item_id(row): row for row in adjudication_rows
        }
        if len(adjudication_by_id) != len(adjudication_rows):
            raise ValueError("adjudication decision item_id가 중복됩니다.")
        _validate_artifact_record(
            packet_record,
            packet_path,
            sample_count=disagreement_count,
            label="adjudication_packet",
        )
        _validate_artifact_record(
            decision_record,
            adjudication_path,
            sample_count=len(adjudication_rows),
            label="adjudication_decision",
        )
        manifest_record_raw = artifacts.get("adjudication_manifest")
        if manifest_record_raw is not None:
            manifest_record = _mapping(
                manifest_record_raw,
                "adjudication_manifest",
            )
            adjudication_manifest_path = _record_path(
                manifest_record,
                "adjudication_manifest",
            )
            _validate_artifact_record(
                manifest_record,
                adjudication_manifest_path,
                sample_count=None,
                label="adjudication_manifest",
            )
            _, adjudication_receipts = validate_adjudication_manifest(
                adjudication_manifest_path,
                packet_path=packet_path,
                decision_path=adjudication_path,
                codebook_path=codebook_path,
                prompt_path=prompt_path,
            )
            receipts.extend(adjudication_receipts)
        else:
            receipt_record = _mapping(
                artifacts.get("adjudication_receipt"), "adjudication_receipt"
            )
            receipt_path = _record_path(receipt_record, "adjudication_receipt")
            _validate_artifact_record(
                receipt_record,
                receipt_path,
                sample_count=None,
                label="adjudication_receipt",
            )
            receipts.append(
                validate_review_receipt(
                    receipt_path,
                    packet_path=packet_path,
                    decision_path=adjudication_path,
                    codebook_path=codebook_path,
                    prompt_path=prompt_path,
                    expected_packet_kind=ADJUDICATION_PACKET_KIND,
                    expected_role=ADJUDICATOR_ROLE,
                )
            )
    final_by_id = {_required_item_id(row): row for row in decision_rows}
    if len(final_by_id) != len(decision_rows):
        raise ValueError("dual-review merged decision item_id가 중복됩니다.")
    expected_ids = set(final_by_id)
    if any(set(stage_decision_maps[name]) != expected_ids for name in ("stage_1", "stage_2")):
        raise ValueError("review stage와 dual-review merged decision item 집합이 다릅니다.")
    actual_disagreements = 0
    for item_id, final in final_by_id.items():
        left = stage_decision_maps["stage_1"][item_id]
        right = stage_decision_maps["stage_2"][item_id]
        if final.get("reviewer_1") != _reviewer_provenance_from_stage(left):
            raise ValueError(f"{item_id} reviewer_1 provenance가 stage decision과 다릅니다.")
        if final.get("reviewer_2") != _reviewer_provenance_from_stage(right):
            raise ValueError(f"{item_id} reviewer_2 provenance가 stage decision과 다릅니다.")
        agreement = left.get("final_sentiment") == right.get("final_sentiment")
        if agreement:
            if (
                final.get("inter_reviewer_agreement") is not True
                or final.get("decision_path") != "INDEPENDENT_REVIEWER_AGREEMENT"
                or final.get("final_sentiment") != left.get("final_sentiment")
                or final.get("adjudication") is not None
            ):
                raise ValueError(f"{item_id} agreement merge가 stage decision과 다릅니다.")
        else:
            actual_disagreements += 1
            adjudication = adjudication_by_id.get(item_id)
            if adjudication is None or final.get("adjudication") != adjudication:
                raise ValueError(f"{item_id} adjudication merge가 receipt chain과 다릅니다.")
            expected_path = (
                "UNRESOLVED_EXCLUDED"
                if adjudication.get("final_sentiment") == "UNRESOLVED"
                else "ADJUDICATED"
            )
            if (
                final.get("inter_reviewer_agreement") is not False
                or final.get("decision_path") != expected_path
                or final.get("final_sentiment") != adjudication.get("final_sentiment")
            ):
                raise ValueError(f"{item_id} disagreement merge가 adjudication과 다릅니다.")
    if actual_disagreements != disagreement_count or set(adjudication_by_id) != {
        item_id
        for item_id in expected_ids
        if stage_decision_maps["stage_1"][item_id].get("final_sentiment")
        != stage_decision_maps["stage_2"][item_id].get("final_sentiment")
    }:
        raise ValueError("dual-review disagreement 집합이 manifest와 다릅니다.")
    assert_independent_receipts(receipts)
    committed_receipts = manifest.get("participant_receipt_payload_sha256")
    actual_receipts = [receipt["receipt_payload_sha256"] for receipt in receipts]
    if committed_receipts != actual_receipts:
        raise ValueError("dual-review participant receipt 체인이 다릅니다.")
    return manifest


def validate_adjudication_manifest(
    manifest_path: Path,
    *,
    packet_path: Path,
    decision_path: Path,
    codebook_path: Path,
    prompt_path: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not manifest_path.exists():
        raise LegacyUnverifiedError(
            f"{LEGACY_STATUS}: adjudication provenance manifest가 없습니다."
        )
    manifest = read_json(manifest_path)
    validate_signed_payload(
        manifest,
        schema=ADJUDICATION_MANIFEST_SCHEMA,
        signature_field="adjudication_manifest_payload_sha256",
        label="adjudication provenance manifest",
    )
    if (
        manifest.get("role") != ADJUDICATOR_ROLE
        or manifest.get("context_isolation_commitment") != CONTEXT_ISOLATION
        or manifest.get("exact_item_set") is not True
        or manifest.get("item_order_preserved") is not True
    ):
        raise ValueError("adjudication manifest 독립성 계약이 올바르지 않습니다.")
    blindness = _mapping(manifest.get("blindness"), "adjudication.blindness")
    if any(
        blindness.get(field) != NONEXPOSURE_VALUE
        for field in (
            "candidate_prediction_visibility",
            "teacher_prediction_visibility",
            "market_outcome_visibility",
            "reviewer_decision_visibility",
        )
    ):
        raise ValueError("adjudication manifest 비노출 commitment가 완전하지 않습니다.")
    packet_rows = read_jsonl(packet_path)
    decision_rows = read_jsonl(decision_path)
    validate_manifest_artifact(
        manifest,
        field="adjudication_packet",
        path=packet_path,
        sample_count=len(packet_rows),
    )
    validate_manifest_artifact(
        manifest,
        field="merged_decision",
        path=decision_path,
        sample_count=len(decision_rows),
    )
    validate_manifest_artifact(manifest, field="codebook", path=codebook_path, sample_count=None)
    validate_manifest_artifact(manifest, field="prompt", path=prompt_path, sample_count=None)
    packet_ids = [_required_item_id(row) for row in packet_rows]
    decision_ids = [_required_item_id(row) for row in decision_rows]
    if (
        len(packet_ids) != len(set(packet_ids))
        or len(decision_ids) != len(set(decision_ids))
        or packet_ids != decision_ids
        or manifest.get("sample_count") != len(packet_ids)
    ):
        raise ValueError("adjudication packet·decision item 집합/순서가 다릅니다.")
    part_chain = manifest.get("part_chain")
    if not isinstance(part_chain, list) or not part_chain:
        raise ValueError("adjudication manifest part_chain이 비었습니다.")
    receipts: list[dict[str, Any]] = []
    combined: dict[str, dict[str, Any]] = {}
    for raw_part in part_chain:
        part = _mapping(raw_part, "adjudication.part")
        decision_record = _mapping(part.get("decision"), "adjudication.part.decision")
        receipt_record = _mapping(part.get("receipt"), "adjudication.part.receipt")
        part_path = _record_path(decision_record, "adjudication.part.decision")
        receipt_path = _record_path(receipt_record, "adjudication.part.receipt")
        part_rows = read_jsonl(part_path)
        _validate_artifact_record(
            decision_record,
            part_path,
            sample_count=len(part_rows),
            label="adjudication part decision",
        )
        _validate_artifact_record(
            receipt_record,
            receipt_path,
            sample_count=None,
            label="adjudication part receipt",
        )
        receipt = validate_review_receipt(
            receipt_path,
            packet_path=packet_path,
            decision_path=part_path,
            codebook_path=codebook_path,
            prompt_path=prompt_path,
            expected_packet_kind=ADJUDICATION_PACKET_KIND,
            expected_role=ADJUDICATOR_ROLE,
        )
        if (
            part.get("receipt_payload_sha256") != receipt["receipt_payload_sha256"]
            or part.get("reviewer") != receipt["reviewer"]
            or part.get("run") != receipt["run"]
            or part.get("input_scope") != receipt["input_scope"]
        ):
            raise ValueError("adjudication part receipt chain이 다릅니다.")
        receipts.append(receipt)
        for row in part_rows:
            item_id = _required_item_id(row)
            if item_id in combined:
                raise ValueError("adjudication part item_id가 중복됩니다.")
            combined[item_id] = row
    assert_independent_receipts(receipts)
    if [combined.get(item_id) for item_id in decision_ids] != decision_rows:
        raise ValueError("adjudication part와 merged decision이 다릅니다.")
    committed = manifest.get("participant_receipt_payload_sha256")
    if committed != [receipt["receipt_payload_sha256"] for receipt in receipts]:
        raise ValueError("adjudication participant receipt chain이 다릅니다.")
    return manifest, receipts


def _reviewer_provenance_from_stage(row: dict[str, Any]) -> dict[str, Any]:
    sentiment = str(row.get("final_sentiment", ""))
    return {
        "stage_1": "NEUTRAL" if sentiment == "NEUTRAL" else "DIRECTIONAL",
        "stage_2": sentiment if sentiment != "NEUTRAL" else "NOT_APPLICABLE",
        "final_sentiment": sentiment,
        "label_evidence": row.get("review_note"),
        "decision_path": "NEUTRAL_DIRECTIONAL_THEN_POLARITY",
        "reviewer_id": row.get("reviewer_id"),
        "reviewed_at": row.get("reviewed_at"),
        "reviewer_type": "CODEX_AI",
        "model_blind": True,
        "market_blind": True,
    }


def _audit_mapping(value: object, *, packet_kind: str, context: str) -> None:
    if isinstance(value, dict):
        for raw_key, child in value.items():
            key = str(raw_key).lower()
            forbidden = key in FORBIDDEN_REVIEW_INPUT_KEYS or key.startswith(FORBIDDEN_PREFIXES)
            if key == "final_sentiment" and (child is None or child == ""):
                forbidden = False
            if forbidden:
                raise ValueError(f"blind packet에 금지 필드가 있습니다: {context}.{key}")
            _audit_mapping(child, packet_kind=packet_kind, context=f"{context}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _audit_mapping(child, packet_kind=packet_kind, context=f"{context}[{index}]")


def _validate_artifact_record(
    value: object,
    path: Path,
    *,
    sample_count: int | None,
    label: str,
) -> None:
    record = _mapping(value, label)
    actual = artifact_record(path, sample_count=sample_count)
    for field in ("bytes", "sha256"):
        if record.get(field) != actual[field]:
            raise ValueError(f"{label} artifact가 receipt 이후 변경되었습니다.")
    if sample_count is not None and record.get("sample_count") != sample_count:
        raise ValueError(f"{label} sample_count가 receipt와 다릅니다.")
    digest = record.get("sha256")
    if not isinstance(digest, str) or SHA256_PATTERN.fullmatch(digest) is None:
        raise ValueError(f"{label} SHA-256이 올바르지 않습니다.")


def _record_path(record: dict[str, Any], label: str) -> Path:
    raw = record.get("path")
    if not isinstance(raw, str) or not raw:
        raise ValueError(f"{label}.path가 비었습니다.")
    return Path(raw)


def _mapping(value: object, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field}는 JSON 객체여야 합니다.")
    return cast(dict[str, Any], value)


def _required_item_id(row: dict[str, Any]) -> str:
    value = row.get("item_id")
    if not isinstance(value, str) or not value.strip():
        raise ValueError("decision에 item_id가 없습니다.")
    return value.strip()


def _required_text(value: str, field: str) -> str:
    if (
        not value
        or value != value.strip()
        or len(value) > 256
        or CONTROL_CHARACTER_PATTERN.search(value)
    ):
        raise ValueError(f"{field}가 올바르지 않습니다.")
    return value


def _positive_int(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{field}는 양의 정수여야 합니다.")
    return value


def _uuid4(value: str, field: str) -> UUID:
    try:
        parsed = UUID(value)
    except ValueError as error:
        raise ValueError(f"{field}는 UUIDv4여야 합니다.") from error
    if parsed.version != 4 or str(parsed) != value.lower():
        raise ValueError(f"{field}는 canonical UUIDv4여야 합니다.")
    return parsed


def _aware_datetime(value: str, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{field}는 ISO-8601 시간이어야 합니다.") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field}에는 시간대가 필요합니다.")
    return parsed


def _read_bytes(path: Path, label: str) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{label} 파일이 없거나 symlink입니다: {path}")
    raw = path.read_bytes()
    if not raw or len(raw) > MAX_ARTIFACT_BYTES:
        raise ValueError(f"{label} 파일이 비었거나 크기 제한을 넘습니다: {path}")
    return raw


def _write_exclusive(path: Path, payload: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise ValueError(f"출력이 이미 존재하거나 symlink입니다: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as file:
            os.chmod(temporary, 0o600)
            file.write(payload)
            file.flush()
            os.fsync(file.fileno())
        try:
            os.link(temporary, path, follow_symlinks=False)
        except FileExistsError as error:
            raise ValueError(f"출력이 이미 존재합니다: {path}") from error
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="예측 비노출 Codex Gold 검수 run의 불변 receipt를 생성한다."
    )
    parser.add_argument("--packet-path", type=Path, required=True)
    parser.add_argument("--decision-path", type=Path, required=True)
    parser.add_argument("--codebook-path", type=Path, required=True)
    parser.add_argument("--prompt-path", type=Path, required=True)
    parser.add_argument("--output-path", type=Path, required=True)
    parser.add_argument(
        "--packet-kind",
        choices=(REVIEW_PACKET_KIND, ADJUDICATION_PACKET_KIND),
        required=True,
    )
    parser.add_argument("--role", choices=(REVIEW_ROLE, ADJUDICATOR_ROLE), required=True)
    parser.add_argument("--reviewer-id", required=True)
    parser.add_argument("--reviewer-model", required=True)
    parser.add_argument("--reviewer-model-version", required=True)
    parser.add_argument("--independent-run-id", required=True)
    parser.add_argument("--context-id", required=True)
    parser.add_argument("--row-start", type=int, required=True)
    parser.add_argument("--row-end", type=int, required=True)
    parser.add_argument("--run-started-at", required=True)
    parser.add_argument("--run-completed-at", required=True)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    receipt = create_review_receipt(
        packet_path=args.packet_path,
        decision_path=args.decision_path,
        codebook_path=args.codebook_path,
        prompt_path=args.prompt_path,
        output_path=args.output_path,
        packet_kind=args.packet_kind,
        role=args.role,
        reviewer_id=args.reviewer_id,
        reviewer_model=args.reviewer_model,
        reviewer_model_version=args.reviewer_model_version,
        independent_run_id=args.independent_run_id,
        context_id=args.context_id,
        row_start=args.row_start,
        row_end=args.row_end,
        run_started_at=args.run_started_at,
        run_completed_at=args.run_completed_at,
    )
    print(json.dumps(receipt, ensure_ascii=False))


if __name__ == "__main__":
    main()
