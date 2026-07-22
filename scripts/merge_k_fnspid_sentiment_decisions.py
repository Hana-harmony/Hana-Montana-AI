from __future__ import annotations

import argparse
import json
import os
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, cast

try:
    from scripts.k_fnspid_sentiment_review_provenance import (
        CONTEXT_ISOLATION,
        NONEXPOSURE_VALUE,
        REVIEW_PACKET_KIND,
        REVIEW_ROLE,
        STAGE_MANIFEST_SCHEMA,
        VERIFIED_STATUS,
        LegacyUnverifiedError,
        artifact_record,
        assert_independent_receipts,
        signed_payload,
        validate_review_receipt,
        write_json_exclusive,
    )
except ModuleNotFoundError:  # pragma: no cover - 직접 script 실행 경로
    from k_fnspid_sentiment_review_provenance import (  # type: ignore[import-not-found,no-redef]
        CONTEXT_ISOLATION,
        NONEXPOSURE_VALUE,
        REVIEW_PACKET_KIND,
        REVIEW_ROLE,
        STAGE_MANIFEST_SCHEMA,
        VERIFIED_STATUS,
        LegacyUnverifiedError,
        artifact_record,
        assert_independent_receipts,
        signed_payload,
        validate_review_receipt,
        write_json_exclusive,
    )

LABELS = frozenset({"POSITIVE", "NEUTRAL", "NEGATIVE"})
REQUIRED_FIELDS = frozenset(
    {
        "item_id",
        "final_sentiment",
        "review_note",
        "reviewer_id",
        "reviewed_at",
        "review_status",
    }
)


def merge_decisions(
    review_path: Path,
    part_paths: list[Path],
    output_path: Path,
    *,
    receipt_paths: list[Path] | None = None,
    codebook_path: Path | None = None,
    prompt_path: Path | None = None,
    provenance_output_path: Path | None = None,
) -> dict[str, Any]:
    if not part_paths:
        raise ValueError("결정 part 파일이 하나 이상 필요합니다.")
    if (
        receipt_paths is None
        or codebook_path is None
        or prompt_path is None
        or provenance_output_path is None
    ):
        raise LegacyUnverifiedError(
            "LEGACY_UNVERIFIED: reviewer receipt·codebook·prompt·stage provenance가 "
            "없습니다. 예측 비노출 상태로 재검수해야 합니다."
        )
    if len(receipt_paths) != len(part_paths):
        raise ValueError("decision part와 reviewer receipt 수가 다릅니다.")
    for path in (output_path, provenance_output_path):
        if path.exists() or path.is_symlink():
            raise ValueError(f"출력이 이미 존재하거나 symlink입니다: {path}")
    review_rows = _read_jsonl(review_path)
    review_ids = [_review_item_id(row) for row in review_rows]
    if len(review_ids) != len(set(review_ids)):
        raise ValueError("review item_id가 중복되었습니다.")

    receipts: list[dict[str, Any]] = []
    decisions: dict[str, dict[str, Any]] = {}
    for part_path, receipt_path in zip(part_paths, receipt_paths, strict=True):
        receipt = validate_review_receipt(
            receipt_path,
            packet_path=review_path,
            decision_path=part_path,
            codebook_path=codebook_path,
            prompt_path=prompt_path,
            expected_packet_kind=REVIEW_PACKET_KIND,
            expected_role=REVIEW_ROLE,
        )
        receipts.append(receipt)
        for row in _read_jsonl(part_path):
            if set(row) != REQUIRED_FIELDS:
                raise ValueError(f"결정 스키마가 올바르지 않습니다: {part_path}")
            item_id = str(row["item_id"])
            if item_id in decisions:
                raise ValueError(f"결정 item_id가 중복되었습니다: {item_id}")
            if (
                row["final_sentiment"] not in LABELS
                or row["review_status"] != "CODEX_REVIEW_APPROVED"
                or not str(row["review_note"]).strip()
                or not str(row["reviewer_id"]).strip()
                or not str(row["reviewed_at"]).strip()
            ):
                raise ValueError(f"승인되지 않은 결정이 있습니다: {item_id}")
            decisions[item_id] = row
    assert_independent_receipts(receipts)
    if set(decisions) != set(review_ids):
        missing = len(set(review_ids) - set(decisions))
        unexpected = len(set(decisions) - set(review_ids))
        raise ValueError(
            f"review와 결정 집합이 다릅니다: missing={missing}, unexpected={unexpected}"
        )

    ordered = [decisions[item_id] for item_id in review_ids]
    _atomic_write_jsonl(output_path, ordered)
    part_chain: list[dict[str, Any]] = []
    for part_path, receipt_path, receipt in zip(
        part_paths, receipt_paths, receipts, strict=True
    ):
        part_chain.append(
            {
                "decision": artifact_record(
                    part_path,
                    sample_count=len(_read_jsonl(part_path)),
                ),
                "receipt": artifact_record(receipt_path),
                "receipt_payload_sha256": receipt["receipt_payload_sha256"],
                "reviewer": receipt["reviewer"],
                "run": receipt["run"],
                "input_scope": receipt["input_scope"],
            }
        )
    manifest = signed_payload(
        {
            "schema_version": STAGE_MANIFEST_SCHEMA,
            "status": VERIFIED_STATUS,
            "role": REVIEW_ROLE,
            "protocol": "receipt-bound-independent-codex-review-stage/v1",
            "artifacts": {
                "review_packet": artifact_record(review_path, sample_count=len(review_rows)),
                "codebook": artifact_record(codebook_path),
                "prompt": artifact_record(prompt_path),
                "merged_decision": artifact_record(output_path, sample_count=len(ordered)),
            },
            "part_chain": part_chain,
            "blindness": {
                "candidate_prediction_visibility": NONEXPOSURE_VALUE,
                "teacher_prediction_visibility": NONEXPOSURE_VALUE,
                "market_outcome_visibility": NONEXPOSURE_VALUE,
            },
            "context_isolation_commitment": CONTEXT_ISOLATION,
            "exact_item_set": True,
            "item_order_preserved": True,
        },
        signature_field="stage_manifest_payload_sha256",
    )
    write_json_exclusive(provenance_output_path, manifest)
    return {
        "sample_count": len(ordered),
        "reviewer_count": len({str(row["reviewer_id"]) for row in ordered}),
        "label_distribution": dict(
            sorted(Counter(str(row["final_sentiment"]) for row in ordered).items())
        ),
        "output_path": str(output_path),
        "provenance_output_path": str(provenance_output_path),
        "provenance_status": VERIFIED_STATUS,
    }


def _review_item_id(row: dict[str, Any]) -> str:
    for field in ("review_key", "annotation_id", "item_id"):
        value = row.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    document_id = str(row.get("document_id", "")).strip()
    stock_code = str(row.get("stock_code", "")).strip()
    if not document_id or not stock_code:
        raise ValueError("review 행에 item_id 원천 필드가 없습니다.")
    return f"{document_id}::{stock_code}"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"JSONL 파일이 없거나 symlink입니다: {path}")
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"JSONL {line_number}행은 객체여야 합니다: {path}")
            rows.append(cast(dict[str, Any], value))
    return rows


def _atomic_write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    if path.exists() or path.is_symlink():
        raise ValueError(f"결정 병합 출력이 이미 존재하거나 symlink입니다: {path}")
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
        if path.exists() or path.is_symlink():
            raise ValueError(f"결정 병합 출력이 이미 존재하거나 symlink입니다: {path}")
        try:
            os.link(temporary, path, follow_symlinks=False)
        except FileExistsError as error:
            raise ValueError(
                f"결정 병합 출력이 이미 존재하거나 symlink입니다: {path}"
            ) from error
        temporary.unlink()
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if temporary.exists():
            temporary.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="분할 blind 감성 검수 결정을 원본 순서로 병합한다."
    )
    parser.add_argument("--review-path", type=Path, required=True)
    parser.add_argument("--part-path", type=Path, action="append", required=True)
    parser.add_argument("--receipt-path", type=Path, action="append", required=True)
    parser.add_argument("--codebook-path", type=Path, required=True)
    parser.add_argument("--prompt-path", type=Path, required=True)
    parser.add_argument("--output-path", type=Path, required=True)
    parser.add_argument("--provenance-output-path", type=Path, required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            merge_decisions(
                args.review_path,
                args.part_path,
                args.output_path,
                receipt_paths=args.receipt_path,
                codebook_path=args.codebook_path,
                prompt_path=args.prompt_path,
                provenance_output_path=args.provenance_output_path,
            ),
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
