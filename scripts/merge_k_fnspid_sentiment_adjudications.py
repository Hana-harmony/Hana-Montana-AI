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
        ADJUDICATION_PACKET_KIND,
        ADJUDICATOR_ROLE,
        CONTEXT_ISOLATION,
        NONEXPOSURE_VALUE,
        VERIFIED_STATUS,
        artifact_record,
        assert_independent_receipts,
        signed_payload,
        validate_review_receipt,
        write_json_exclusive,
    )
except ModuleNotFoundError:  # pragma: no cover - 직접 script 실행 경로
    from k_fnspid_sentiment_review_provenance import (  # type: ignore[import-not-found,no-redef]
        ADJUDICATION_PACKET_KIND,
        ADJUDICATOR_ROLE,
        CONTEXT_ISOLATION,
        NONEXPOSURE_VALUE,
        VERIFIED_STATUS,
        artifact_record,
        assert_independent_receipts,
        signed_payload,
        validate_review_receipt,
        write_json_exclusive,
    )

SCHEMA_VERSION = "k-fnspid-sentiment-adjudication-provenance/v1"
DECISION_FIELDS = frozenset(
    {
        "item_id",
        "final_sentiment",
        "adjudication_note",
        "adjudicator_id",
        "adjudicated_at",
        "adjudication_status",
    }
)
LABELS = frozenset({"POSITIVE", "NEUTRAL", "NEGATIVE", "UNRESOLVED"})


def merge_adjudication_parts(
    *,
    packet_path: Path,
    part_paths: list[Path],
    receipt_paths: list[Path],
    codebook_path: Path,
    prompt_path: Path,
    output_path: Path,
    provenance_output_path: Path,
) -> dict[str, Any]:
    if not part_paths or len(part_paths) != len(receipt_paths):
        raise ValueError("adjudication part와 receipt 수가 같고 비어 있지 않아야 합니다.")
    packet_rows = _read_jsonl(packet_path)
    packet_ids = [_item_id(row, "adjudication packet") for row in packet_rows]
    if len(packet_ids) != len(set(packet_ids)):
        raise ValueError("adjudication packet item_id가 중복됩니다.")

    receipts: list[dict[str, Any]] = []
    combined: dict[str, dict[str, Any]] = {}
    part_chain: list[dict[str, Any]] = []
    for part_path, receipt_path in zip(part_paths, receipt_paths, strict=True):
        part_rows = _read_jsonl(part_path)
        for row in part_rows:
            _validate_decision(row)
            item_id = _item_id(row, "adjudication decision")
            if item_id in combined:
                raise ValueError("adjudication part 사이 item_id가 중복됩니다.")
            combined[item_id] = row
        receipt = validate_review_receipt(
            receipt_path,
            packet_path=packet_path,
            decision_path=part_path,
            codebook_path=codebook_path,
            prompt_path=prompt_path,
            expected_packet_kind=ADJUDICATION_PACKET_KIND,
            expected_role=ADJUDICATOR_ROLE,
        )
        receipts.append(receipt)
        part_chain.append(
            {
                "decision": artifact_record(part_path, sample_count=len(part_rows)),
                "receipt": artifact_record(receipt_path),
                "receipt_payload_sha256": receipt["receipt_payload_sha256"],
                "reviewer": receipt["reviewer"],
                "run": receipt["run"],
                "input_scope": receipt["input_scope"],
            }
        )
    assert_independent_receipts(receipts)
    if set(combined) != set(packet_ids):
        raise ValueError("adjudication part item 집합이 불일치 packet과 다릅니다.")
    ordered = [combined[item_id] for item_id in packet_ids]
    _write_jsonl_exclusive(output_path, ordered)
    manifest = signed_payload(
        {
            "schema_version": SCHEMA_VERSION,
            "status": VERIFIED_STATUS,
            "role": ADJUDICATOR_ROLE,
            "artifacts": {
                "adjudication_packet": artifact_record(
                    packet_path, sample_count=len(packet_rows)
                ),
                "merged_decision": artifact_record(output_path, sample_count=len(ordered)),
                "codebook": artifact_record(codebook_path),
                "prompt": artifact_record(prompt_path),
            },
            "part_chain": part_chain,
            "participant_receipt_payload_sha256": [
                receipt["receipt_payload_sha256"] for receipt in receipts
            ],
            "blindness": {
                "candidate_prediction_visibility": NONEXPOSURE_VALUE,
                "teacher_prediction_visibility": NONEXPOSURE_VALUE,
                "market_outcome_visibility": NONEXPOSURE_VALUE,
                "reviewer_decision_visibility": NONEXPOSURE_VALUE,
            },
            "context_isolation_commitment": CONTEXT_ISOLATION,
            "exact_item_set": True,
            "item_order_preserved": True,
            "sample_count": len(ordered),
            "adjudicator_count": len(receipts),
            "label_distribution": dict(
                sorted(Counter(str(row["final_sentiment"]) for row in ordered).items())
            ),
        },
        signature_field="adjudication_manifest_payload_sha256",
    )
    write_json_exclusive(provenance_output_path, manifest)
    return {
        "sample_count": len(ordered),
        "adjudicator_count": len(receipts),
        "output_path": str(output_path),
        "provenance_output_path": str(provenance_output_path),
        "provenance_status": VERIFIED_STATUS,
    }


def _validate_decision(row: dict[str, Any]) -> None:
    sentiment = row.get("final_sentiment")
    expected_status = "UNRESOLVED" if sentiment == "UNRESOLVED" else "CODEX_ADJUDICATED"
    if (
        set(row) != DECISION_FIELDS
        or sentiment not in LABELS
        or row.get("adjudication_status") != expected_status
        or not str(row.get("adjudication_note", "")).strip()
        or not str(row.get("adjudicator_id", "")).strip()
        or not str(row.get("adjudicated_at", "")).strip()
    ):
        raise ValueError("adjudication decision 스키마가 올바르지 않습니다.")


def _item_id(row: dict[str, Any], label: str) -> str:
    value = row.get("item_id")
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} item_id가 없습니다.")
    return value.strip()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
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
    if not rows:
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
        os.link(temporary, path, follow_symlinks=False)
    except FileExistsError as error:
        raise ValueError(f"JSONL 출력이 이미 존재합니다: {path}") from error
    finally:
        temporary.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="분할 blind adjudication을 receipt와 병합한다.")
    parser.add_argument("--packet-path", type=Path, required=True)
    parser.add_argument("--part-path", type=Path, action="append", required=True)
    parser.add_argument("--receipt-path", type=Path, action="append", required=True)
    parser.add_argument("--codebook-path", type=Path, required=True)
    parser.add_argument("--prompt-path", type=Path, required=True)
    parser.add_argument("--output-path", type=Path, required=True)
    parser.add_argument("--provenance-output-path", type=Path, required=True)
    args = parser.parse_args()
    result = merge_adjudication_parts(
        packet_path=args.packet_path,
        part_paths=args.part_path,
        receipt_paths=args.receipt_path,
        codebook_path=args.codebook_path,
        prompt_path=args.prompt_path,
        output_path=args.output_path,
        provenance_output_path=args.provenance_output_path,
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
