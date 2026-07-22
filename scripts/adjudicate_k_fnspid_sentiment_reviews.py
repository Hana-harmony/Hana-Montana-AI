from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, cast

try:
    from scripts.k_fnspid_sentiment_review_provenance import (
        ADJUDICATION_PACKET_KIND,
        ADJUDICATOR_ROLE,
        CONTEXT_ISOLATION,
        MERGE_MANIFEST_SCHEMA,
        NONEXPOSURE_VALUE,
        REVIEW_PACKET_KIND,
        REVIEW_ROLE,
        STAGE_MANIFEST_SCHEMA,
        VERIFIED_STATUS,
        LegacyUnverifiedError,
        artifact_record,
        assert_independent_receipts,
        read_json,
        signed_payload,
        validate_adjudication_manifest,
        validate_manifest_artifact,
        validate_review_receipt,
        validate_signed_payload,
        write_json_exclusive,
    )
except ModuleNotFoundError:  # pragma: no cover - 직접 script 실행 경로
    from k_fnspid_sentiment_review_provenance import (  # type: ignore[import-not-found,no-redef]
        ADJUDICATION_PACKET_KIND,
        ADJUDICATOR_ROLE,
        CONTEXT_ISOLATION,
        MERGE_MANIFEST_SCHEMA,
        NONEXPOSURE_VALUE,
        REVIEW_PACKET_KIND,
        REVIEW_ROLE,
        STAGE_MANIFEST_SCHEMA,
        VERIFIED_STATUS,
        LegacyUnverifiedError,
        artifact_record,
        assert_independent_receipts,
        read_json,
        signed_payload,
        validate_adjudication_manifest,
        validate_manifest_artifact,
        validate_review_receipt,
        validate_signed_payload,
        write_json_exclusive,
    )

LABELS = frozenset({"POSITIVE", "NEUTRAL", "NEGATIVE"})
STAGE_FIELDS = frozenset(
    {
        "item_id",
        "final_sentiment",
        "review_note",
        "reviewer_id",
        "reviewed_at",
        "review_status",
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


def create_adjudication_packet(
    review_path: Path,
    stage_1_path: Path,
    stage_2_path: Path,
    output_path: Path,
    *,
    stage_1_provenance_path: Path | None = None,
    stage_2_provenance_path: Path | None = None,
    codebook_path: Path | None = None,
    prompt_path: Path | None = None,
) -> dict[str, Any]:
    if (
        stage_1_provenance_path is None
        or stage_2_provenance_path is None
        or codebook_path is None
        or prompt_path is None
    ):
        raise LegacyUnverifiedError(
            "LEGACY_UNVERIFIED: 두 검수 stage의 receipt-bound provenance가 없습니다. "
            "예측 비노출 상태로 재검수해야 합니다."
        )
    review_rows, review_ids = _review_rows(review_path)
    stage_1 = _stage_decisions(stage_1_path, review_ids)
    stage_2 = _stage_decisions(stage_2_path, review_ids)
    stage_1_manifest, stage_1_receipts = _validated_stage_manifest(
        stage_1_provenance_path,
        review_path=review_path,
        decision_path=stage_1_path,
        codebook_path=codebook_path,
        prompt_path=prompt_path,
    )
    stage_2_manifest, stage_2_receipts = _validated_stage_manifest(
        stage_2_provenance_path,
        review_path=review_path,
        decision_path=stage_2_path,
        codebook_path=codebook_path,
        prompt_path=prompt_path,
    )
    assert_independent_receipts([*stage_1_receipts, *stage_2_receipts])
    disagreements: list[dict[str, Any]] = []
    for source_record, item_id in zip(review_rows, review_ids, strict=True):
        left = stage_1[item_id]
        right = stage_2[item_id]
        _assert_independent_reviewers(left, right, item_id)
        if left["final_sentiment"] == right["final_sentiment"]:
            continue
        disagreements.append(
            {
                "schema_version": "k-fnspid-sentiment-adjudication-packet/v1",
                "item_id": item_id,
                "source_record": source_record,
                "adjudication_status": "NEEDS_BLIND_ADJUDICATION",
                "stage_1_manifest_sha256": stage_1_manifest[
                    "stage_manifest_payload_sha256"
                ],
                "stage_2_manifest_sha256": stage_2_manifest[
                    "stage_manifest_payload_sha256"
                ],
            }
        )
    if disagreements:
        _write_jsonl_exclusive(output_path, disagreements)
    elif output_path.exists() or output_path.is_symlink():
        raise ValueError(f"adjudication packet 출력이 이미 존재합니다: {output_path}")
    else:
        _write_jsonl_exclusive(output_path, [])
    return {
        "sample_count": len(review_ids),
        "agreement_count": len(review_ids) - len(disagreements),
        "disagreement_count": len(disagreements),
        "output_path": str(output_path),
        "provenance_status": VERIFIED_STATUS,
    }


def merge_dual_reviews(
    review_path: Path,
    stage_1_path: Path,
    stage_2_path: Path,
    adjudication_path: Path,
    output_path: Path,
    *,
    stage_1_provenance_path: Path | None = None,
    stage_2_provenance_path: Path | None = None,
    adjudication_packet_path: Path | None = None,
    adjudication_receipt_path: Path | None = None,
    adjudication_provenance_path: Path | None = None,
    codebook_path: Path | None = None,
    prompt_path: Path | None = None,
    provenance_output_path: Path | None = None,
) -> dict[str, Any]:
    if (
        stage_1_provenance_path is None
        or stage_2_provenance_path is None
        or codebook_path is None
        or prompt_path is None
        or provenance_output_path is None
    ):
        raise LegacyUnverifiedError(
            "LEGACY_UNVERIFIED: dual review provenance 체인이 없습니다. "
            "예측 비노출 상태로 재검수해야 합니다."
        )
    if provenance_output_path.exists() or provenance_output_path.is_symlink():
        raise ValueError(f"provenance 출력이 이미 존재합니다: {provenance_output_path}")
    _, review_ids = _review_rows(review_path)
    stage_1 = _stage_decisions(stage_1_path, review_ids)
    stage_2 = _stage_decisions(stage_2_path, review_ids)
    stage_1_manifest, stage_1_receipts = _validated_stage_manifest(
        stage_1_provenance_path,
        review_path=review_path,
        decision_path=stage_1_path,
        codebook_path=codebook_path,
        prompt_path=prompt_path,
    )
    stage_2_manifest, stage_2_receipts = _validated_stage_manifest(
        stage_2_provenance_path,
        review_path=review_path,
        decision_path=stage_2_path,
        codebook_path=codebook_path,
        prompt_path=prompt_path,
    )
    disagreement_ids = {
        item_id
        for item_id in review_ids
        if stage_1[item_id]["final_sentiment"]
        != stage_2[item_id]["final_sentiment"]
    }
    adjudications = _adjudications(adjudication_path, disagreement_ids)
    receipts = [*stage_1_receipts, *stage_2_receipts]
    if disagreement_ids:
        if adjudication_packet_path is None or (
            adjudication_receipt_path is None and adjudication_provenance_path is None
        ):
            raise LegacyUnverifiedError(
                "LEGACY_UNVERIFIED: 불일치 adjudication receipt가 없습니다. "
                "새 context에서 재검수해야 합니다."
            )
        if adjudication_provenance_path is not None:
            _, adjudication_receipts = validate_adjudication_manifest(
                adjudication_provenance_path,
                packet_path=adjudication_packet_path,
                decision_path=adjudication_path,
                codebook_path=codebook_path,
                prompt_path=prompt_path,
            )
            receipts.extend(adjudication_receipts)
        else:
            assert adjudication_receipt_path is not None
            receipts.append(
                validate_review_receipt(
                    adjudication_receipt_path,
                    packet_path=adjudication_packet_path,
                    decision_path=adjudication_path,
                    codebook_path=codebook_path,
                    prompt_path=prompt_path,
                    expected_packet_kind=ADJUDICATION_PACKET_KIND,
                    expected_role=ADJUDICATOR_ROLE,
                )
            )
    assert_independent_receipts(receipts)
    merged: list[dict[str, Any]] = []
    unresolved_count = 0
    for item_id in review_ids:
        left = stage_1[item_id]
        right = stage_2[item_id]
        _assert_independent_reviewers(left, right, item_id)
        agreement = left["final_sentiment"] == right["final_sentiment"]
        if agreement:
            final_sentiment = str(left["final_sentiment"])
            adjudication: dict[str, Any] | None = None
            decision_path = "INDEPENDENT_REVIEWER_AGREEMENT"
            reviewer_id = f"{left['reviewer_id']}+{right['reviewer_id']}"
            reviewed_at = _latest_review_timestamp(
                str(left["reviewed_at"]), str(right["reviewed_at"])
            )
            review_note = (
                f"독립 검수 일치: {left['review_note']} / {right['review_note']}"
            )
        else:
            adjudication = adjudications[item_id]
            final_sentiment = str(adjudication["final_sentiment"])
            decision_path = (
                "ADJUDICATED" if final_sentiment in LABELS else "UNRESOLVED_EXCLUDED"
            )
            reviewer_id = str(adjudication["adjudicator_id"])
            reviewed_at = str(adjudication["adjudicated_at"])
            review_note = str(adjudication["adjudication_note"])
        unresolved = final_sentiment == "UNRESOLVED"
        unresolved_count += int(unresolved)
        merged.append(
            {
                "schema_version": "k-fnspid-sentiment-dual-review-decision/v1",
                "item_id": item_id,
                "reviewer_1": _reviewer_provenance(left),
                "reviewer_2": _reviewer_provenance(right),
                "independent_reviewer_count": 2,
                "inter_reviewer_agreement": agreement,
                "decision_path": decision_path,
                "adjudication": adjudication,
                "final_sentiment": final_sentiment,
                "review_note": review_note,
                "reviewer_id": reviewer_id,
                "reviewed_at": reviewed_at,
                "review_status": (
                    "UNRESOLVED" if unresolved else "CODEX_REVIEW_APPROVED"
                ),
                "reviewer_type": "INDEPENDENT_CODEX_AI",
                "model_blind": True,
                "market_blind": True,
            }
        )
    _write_jsonl_exclusive(output_path, merged)
    artifacts: dict[str, Any] = {
        "review_packet": artifact_record(review_path, sample_count=len(review_ids)),
        "stage_1_decision": artifact_record(stage_1_path, sample_count=len(stage_1)),
        "stage_2_decision": artifact_record(stage_2_path, sample_count=len(stage_2)),
        "stage_1_manifest": artifact_record(stage_1_provenance_path),
        "stage_2_manifest": artifact_record(stage_2_provenance_path),
        "adjudication_decision": _artifact_record_allow_empty(
            adjudication_path, sample_count=len(adjudications)
        ),
        "codebook": artifact_record(codebook_path),
        "prompt": artifact_record(prompt_path),
        "merged_decision": artifact_record(output_path, sample_count=len(merged)),
    }
    if disagreement_ids:
        if adjudication_packet_path is None:
            raise ValueError("adjudication provenance 경로가 완전하지 않습니다.")
        artifacts["adjudication_packet"] = artifact_record(
            adjudication_packet_path, sample_count=len(disagreement_ids)
        )
        if adjudication_provenance_path is not None:
            artifacts["adjudication_manifest"] = artifact_record(
                adjudication_provenance_path
            )
        else:
            assert adjudication_receipt_path is not None
            artifacts["adjudication_receipt"] = artifact_record(
                adjudication_receipt_path
            )
    manifest = signed_payload(
        {
            "schema_version": MERGE_MANIFEST_SCHEMA,
            "status": VERIFIED_STATUS,
            "protocol": "receipt-bound-two-independent-codex-reviewers-plus-adjudication/v1",
            "artifacts": artifacts,
            "stage_manifest_payload_sha256": {
                "stage_1": stage_1_manifest["stage_manifest_payload_sha256"],
                "stage_2": stage_2_manifest["stage_manifest_payload_sha256"],
            },
            "participant_receipt_payload_sha256": [
                receipt["receipt_payload_sha256"] for receipt in receipts
            ],
            "blindness": {
                "candidate_prediction_visibility": NONEXPOSURE_VALUE,
                "teacher_prediction_visibility": NONEXPOSURE_VALUE,
                "market_outcome_visibility": NONEXPOSURE_VALUE,
            },
            "context_isolation_commitment": CONTEXT_ISOLATION,
            "reviewed_item_count": len(review_ids),
            "disagreement_count": len(disagreement_ids),
            "unresolved_count": unresolved_count,
            "exact_item_set": True,
        },
        signature_field="merge_manifest_payload_sha256",
    )
    write_json_exclusive(provenance_output_path, manifest)
    return {
        "sample_count": len(merged),
        "agreement_count": len(merged) - len(disagreement_ids),
        "disagreement_count": len(disagreement_ids),
        "adjudicated_count": len(disagreement_ids) - unresolved_count,
        "unresolved_count": unresolved_count,
        "output_path": str(output_path),
        "provenance_output_path": str(provenance_output_path),
        "provenance_status": VERIFIED_STATUS,
    }


def _validated_stage_manifest(
    manifest_path: Path,
    *,
    review_path: Path,
    decision_path: Path,
    codebook_path: Path,
    prompt_path: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not manifest_path.exists():
        raise LegacyUnverifiedError(
            "LEGACY_UNVERIFIED: review stage manifest가 없습니다. 재검수해야 합니다."
        )
    manifest = read_json(manifest_path)
    validate_signed_payload(
        manifest,
        schema=STAGE_MANIFEST_SCHEMA,
        signature_field="stage_manifest_payload_sha256",
        label="review stage manifest",
    )
    if (
        manifest.get("role") != REVIEW_ROLE
        or manifest.get("context_isolation_commitment") != CONTEXT_ISOLATION
        or manifest.get("exact_item_set") is not True
        or manifest.get("item_order_preserved") is not True
    ):
        raise ValueError("review stage manifest 독립성 계약이 올바르지 않습니다.")
    blindness = manifest.get("blindness")
    if not isinstance(blindness, dict) or any(
        blindness.get(field) != NONEXPOSURE_VALUE
        for field in (
            "candidate_prediction_visibility",
            "teacher_prediction_visibility",
            "market_outcome_visibility",
        )
    ):
        raise ValueError("review stage manifest 비노출 commitment가 잘못되었습니다.")
    review_rows = _read_jsonl(review_path, allow_empty=False)
    decision_rows = _read_jsonl(decision_path, allow_empty=False)
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

    part_chain = manifest.get("part_chain")
    if not isinstance(part_chain, list) or not part_chain:
        raise ValueError("review stage manifest part_chain이 비었습니다.")
    receipts: list[dict[str, Any]] = []
    combined: dict[str, dict[str, Any]] = {}
    for index, raw_part in enumerate(part_chain, start=1):
        if not isinstance(raw_part, dict):
            raise ValueError(f"review stage part_chain {index}행이 객체가 아닙니다.")
        decision_record = _required_artifact_record(raw_part.get("decision"), "decision")
        receipt_record = _required_artifact_record(raw_part.get("receipt"), "receipt")
        part_path = Path(str(decision_record["path"]))
        receipt_path = Path(str(receipt_record["path"]))
        part_rows = _read_jsonl(part_path, allow_empty=False)
        _validate_embedded_artifact_record(
            decision_record,
            part_path,
            sample_count=len(part_rows),
            label="stage decision part",
        )
        _validate_embedded_artifact_record(
            receipt_record,
            receipt_path,
            sample_count=None,
            label="stage reviewer receipt",
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
        if raw_part.get("receipt_payload_sha256") != receipt["receipt_payload_sha256"]:
            raise ValueError("stage manifest의 reviewer receipt 해시가 다릅니다.")
        if raw_part.get("reviewer") != receipt["reviewer"] or raw_part.get("run") != receipt["run"]:
            raise ValueError("stage manifest의 reviewer run provenance가 다릅니다.")
        if raw_part.get("input_scope") != receipt["input_scope"]:
            raise ValueError("stage manifest의 input_scope가 reviewer receipt와 다릅니다.")
        receipts.append(receipt)
        for row in part_rows:
            item_id = str(row.get("item_id", ""))
            if not item_id or item_id in combined:
                raise ValueError("stage decision part item_id가 비었거나 중복됩니다.")
            combined[item_id] = row
    assert_independent_receipts(receipts)
    ordered = [combined.get(str(row.get("item_id", ""))) for row in decision_rows]
    if any(row is None for row in ordered) or ordered != decision_rows or len(combined) != len(
        decision_rows
    ):
        raise ValueError("stage part와 merged decision 내용이 다릅니다.")
    return manifest, receipts


def _artifact_record_allow_empty(path: Path, *, sample_count: int) -> dict[str, object]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"artifact가 없거나 symlink입니다: {path}")
    raw = path.read_bytes()
    return {
        "path": str(path),
        "bytes": len(raw),
        "sha256": sha256(raw).hexdigest(),
        "sample_count": sample_count,
    }


def _required_artifact_record(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} artifact record가 객체가 아닙니다.")
    path = value.get("path")
    if not isinstance(path, str) or not path:
        raise ValueError(f"{label} artifact path가 비었습니다.")
    return cast(dict[str, Any], value)


def _validate_embedded_artifact_record(
    record: dict[str, Any],
    path: Path,
    *,
    sample_count: int | None,
    label: str,
) -> None:
    actual = artifact_record(path, sample_count=sample_count)
    if record.get("bytes") != actual["bytes"] or record.get("sha256") != actual["sha256"]:
        raise ValueError(f"{label}가 manifest 생성 이후 변경되었습니다.")
    if sample_count is not None and record.get("sample_count") != sample_count:
        raise ValueError(f"{label} sample_count가 manifest와 다릅니다.")


def _review_rows(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    rows = _read_jsonl(path, allow_empty=False)
    item_ids: list[str] = []
    for row in rows:
        item_id = _review_item_id(row)
        if row.get("review_status") != "NEEDS_BLIND_REVIEW" or item_id in item_ids:
            raise ValueError("review packet 원본 또는 item_id가 올바르지 않습니다.")
        item_ids.append(item_id)
    return rows, item_ids


def _review_item_id(row: dict[str, Any]) -> str:
    for field in ("review_key", "annotation_id", "item_id"):
        value = row.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    document_id = str(row.get("document_id", "")).strip()
    target = str(row.get("target_security") or row.get("stock_code") or "UNSPECIFIED").strip()
    if not document_id:
        raise ValueError("review packet에 document_id가 없습니다.")
    return f"{document_id}::{target}"


def _stage_decisions(path: Path, review_ids: list[str]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in _read_jsonl(path, allow_empty=False):
        if set(row) != STAGE_FIELDS:
            raise ValueError(f"독립 검수 decision 스키마가 올바르지 않습니다: {path}")
        item_id = str(row["item_id"])
        if (
            item_id in result
            or row["final_sentiment"] not in LABELS
            or row["review_status"] != "CODEX_REVIEW_APPROVED"
            or not str(row["review_note"]).strip()
            or not str(row["reviewer_id"]).strip()
        ):
            raise ValueError(f"독립 검수 decision이 올바르지 않습니다: {item_id}")
        _aware_datetime(row["reviewed_at"], "reviewed_at")
        result[item_id] = row
    if set(result) != set(review_ids):
        raise ValueError("독립 검수 decision item_id 집합이 review packet과 다릅니다.")
    return result


def _adjudications(
    path: Path,
    disagreement_ids: set[str],
) -> dict[str, dict[str, Any]]:
    rows = _read_jsonl(path, allow_empty=True)
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        if set(row) != ADJUDICATION_FIELDS:
            raise ValueError("adjudication decision 스키마가 올바르지 않습니다.")
        item_id = str(row["item_id"])
        final_sentiment = row["final_sentiment"]
        expected_status = (
            "UNRESOLVED" if final_sentiment == "UNRESOLVED" else "CODEX_ADJUDICATED"
        )
        if (
            item_id in result
            or final_sentiment not in LABELS | {"UNRESOLVED"}
            or row["adjudication_status"] != expected_status
            or not str(row["adjudication_note"]).strip()
            or not str(row["adjudicator_id"]).strip()
        ):
            raise ValueError(f"adjudication decision이 올바르지 않습니다: {item_id}")
        _aware_datetime(row["adjudicated_at"], "adjudicated_at")
        result[item_id] = row
    if set(result) != disagreement_ids:
        raise ValueError("adjudication item_id 집합이 불일치 항목과 다릅니다.")
    return result


def _assert_independent_reviewers(
    left: dict[str, Any], right: dict[str, Any], item_id: str
) -> None:
    if left["reviewer_id"] == right["reviewer_id"]:
        raise ValueError(f"독립 검수자 ID가 같습니다: {item_id}")


def _reviewer_provenance(row: dict[str, Any]) -> dict[str, Any]:
    sentiment = str(row["final_sentiment"])
    return {
        "stage_1": "NEUTRAL" if sentiment == "NEUTRAL" else "DIRECTIONAL",
        "stage_2": sentiment if sentiment != "NEUTRAL" else "NOT_APPLICABLE",
        "final_sentiment": sentiment,
        "label_evidence": row["review_note"],
        "decision_path": "NEUTRAL_DIRECTIONAL_THEN_POLARITY",
        "reviewer_id": row["reviewer_id"],
        "reviewed_at": row["reviewed_at"],
        "reviewer_type": "CODEX_AI",
        "model_blind": True,
        "market_blind": True,
    }


def _aware_datetime(value: object, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exception:
        raise ValueError(f"{field}가 ISO-8601 형식이 아닙니다.") from exception
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field}에는 시간대가 필요합니다.")
    return parsed


def _latest_review_timestamp(left: str, right: str) -> str:
    left_time = _aware_datetime(left, "reviewed_at")
    right_time = _aware_datetime(right, "reviewed_at")
    return left if left_time >= right_time else right


def _read_jsonl(path: Path, *, allow_empty: bool) -> list[dict[str, Any]]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"JSONL 파일이 없거나 symlink입니다: {path}")
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"JSONL {line_number}행은 객체여야 합니다: {path}")
        rows.append(cast(dict[str, Any], value))
    if not rows and not allow_empty:
        raise ValueError(f"JSONL 파일이 비었습니다: {path}")
    return rows


def _write_jsonl_exclusive(path: Path, rows: list[dict[str, Any]]) -> None:
    if path.exists() or path.is_symlink():
        raise ValueError(f"JSONL 출력이 이미 존재하거나 symlink입니다: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as file:
            for row in rows:
                file.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
            file.flush()
            os.fsync(file.fileno())
        os.chmod(temporary, 0o600)
        try:
            os.link(temporary, path, follow_symlinks=False)
        except FileExistsError as exception:
            raise ValueError(f"JSONL 출력이 이미 존재합니다: {path}") from exception
    finally:
        temporary.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="2단계 독립 감성 검수와 adjudication을 처리한다.")
    parser.add_argument("--mode", choices=("packet", "merge"), required=True)
    parser.add_argument("--review-path", type=Path, required=True)
    parser.add_argument("--stage-1-path", type=Path, required=True)
    parser.add_argument("--stage-2-path", type=Path, required=True)
    parser.add_argument("--stage-1-provenance-path", type=Path, required=True)
    parser.add_argument("--stage-2-provenance-path", type=Path, required=True)
    parser.add_argument("--codebook-path", type=Path, required=True)
    parser.add_argument("--prompt-path", type=Path, required=True)
    parser.add_argument("--adjudication-path", type=Path)
    parser.add_argument("--adjudication-packet-path", type=Path)
    parser.add_argument("--adjudication-receipt-path", type=Path)
    parser.add_argument("--adjudication-provenance-path", type=Path)
    parser.add_argument("--output-path", type=Path, required=True)
    parser.add_argument("--provenance-output-path", type=Path)
    args = parser.parse_args()
    if args.mode == "packet":
        result = create_adjudication_packet(
            args.review_path,
            args.stage_1_path,
            args.stage_2_path,
            args.output_path,
            stage_1_provenance_path=args.stage_1_provenance_path,
            stage_2_provenance_path=args.stage_2_provenance_path,
            codebook_path=args.codebook_path,
            prompt_path=args.prompt_path,
        )
    else:
        if args.adjudication_path is None or args.provenance_output_path is None:
            raise SystemExit(
                "merge mode에는 --adjudication-path와 --provenance-output-path가 필요합니다."
            )
        result = merge_dual_reviews(
            args.review_path,
            args.stage_1_path,
            args.stage_2_path,
            args.adjudication_path,
            args.output_path,
            stage_1_provenance_path=args.stage_1_provenance_path,
            stage_2_provenance_path=args.stage_2_provenance_path,
            adjudication_packet_path=args.adjudication_packet_path,
            adjudication_receipt_path=args.adjudication_receipt_path,
            adjudication_provenance_path=args.adjudication_provenance_path,
            codebook_path=args.codebook_path,
            prompt_path=args.prompt_path,
            provenance_output_path=args.provenance_output_path,
        )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
