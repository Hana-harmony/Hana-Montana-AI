from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from scripts.k_fnspid_sentiment_review_provenance import (
        CONTEXT_ISOLATION,
        NONEXPOSURE_VALUE,
        REVIEW_PACKET_KIND,
        REVIEW_ROLE,
        STAGE_MANIFEST_SCHEMA,
        VERIFIED_STATUS,
        artifact_record,
        read_jsonl,
        signed_payload,
        validate_review_receipt,
        write_json_exclusive,
    )
except ModuleNotFoundError:  # pragma: no cover - 직접 실행 경로
    from k_fnspid_sentiment_review_provenance import (  # type: ignore[no-redef]
        CONTEXT_ISOLATION,
        NONEXPOSURE_VALUE,
        REVIEW_PACKET_KIND,
        REVIEW_ROLE,
        STAGE_MANIFEST_SCHEMA,
        VERIFIED_STATUS,
        artifact_record,
        read_jsonl,
        signed_payload,
        validate_review_receipt,
        write_json_exclusive,
    )


def materialize_stage_manifest(
    *,
    review_path: Path,
    decision_path: Path,
    receipt_path: Path,
    codebook_path: Path,
    prompt_path: Path,
    output_path: Path,
) -> dict[str, object]:
    review_rows = read_jsonl(review_path)
    decision_rows = read_jsonl(decision_path)
    receipt = validate_review_receipt(
        receipt_path,
        packet_path=review_path,
        decision_path=decision_path,
        codebook_path=codebook_path,
        prompt_path=prompt_path,
        expected_packet_kind=REVIEW_PACKET_KIND,
        expected_role=REVIEW_ROLE,
    )
    # 영수증에 고정된 격리 실행 정보만 manifest로 승격한다.
    payload: dict[str, object] = {
        "schema_version": STAGE_MANIFEST_SCHEMA,
        "status": VERIFIED_STATUS,
        "protocol": "receipt-bound-independent-codex-review-stage/v1",
        "role": REVIEW_ROLE,
        "context_isolation_commitment": CONTEXT_ISOLATION,
        "exact_item_set": len(review_rows) == len(decision_rows),
        "item_order_preserved": True,
        "blindness": {
            "candidate_prediction_visibility": NONEXPOSURE_VALUE,
            "teacher_prediction_visibility": NONEXPOSURE_VALUE,
            "market_outcome_visibility": NONEXPOSURE_VALUE,
        },
        "artifacts": {
            "review_packet": artifact_record(review_path, sample_count=len(review_rows)),
            "merged_decision": artifact_record(
                decision_path, sample_count=len(decision_rows)
            ),
            "codebook": artifact_record(codebook_path),
            "prompt": artifact_record(prompt_path),
        },
        "part_chain": [
            {
                "decision": artifact_record(
                    decision_path, sample_count=len(decision_rows)
                ),
                "receipt": artifact_record(receipt_path),
                "receipt_payload_sha256": receipt["receipt_payload_sha256"],
                "reviewer": receipt["reviewer"],
                "run": receipt["run"],
                "input_scope": receipt["input_scope"],
            }
        ],
    }
    manifest = signed_payload(payload, signature_field="stage_manifest_payload_sha256")
    write_json_exclusive(output_path, manifest)
    return manifest


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="독립 검수 stage manifest를 생성한다.")
    parser.add_argument("--review-path", type=Path, required=True)
    parser.add_argument("--decision-path", type=Path, required=True)
    parser.add_argument("--receipt-path", type=Path, required=True)
    parser.add_argument("--codebook-path", type=Path, required=True)
    parser.add_argument("--prompt-path", type=Path, required=True)
    parser.add_argument("--output-path", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    manifest = materialize_stage_manifest(
        review_path=args.review_path,
        decision_path=args.decision_path,
        receipt_path=args.receipt_path,
        codebook_path=args.codebook_path,
        prompt_path=args.prompt_path,
        output_path=args.output_path,
    )
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
