from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.k_fnspid_sentiment_review_provenance import (
    ADJUDICATION_PACKET_KIND,
    ADJUDICATOR_ROLE,
    create_review_receipt,
    validate_adjudication_manifest,
)
from scripts.merge_k_fnspid_sentiment_adjudications import merge_adjudication_parts
from tests.sentiment_review_provenance_fixture import write_jsonl

CODEBOOK = Path("docs/datasets/k-fnspid-sentiment-codebook.md")
PROMPT = Path("docs/datasets/k-fnspid-sentiment-review-prompt-v1.md")


def _packet(item_id: str, index: int) -> dict[str, object]:
    return {
        "schema_version": "k-fnspid-sentiment-adjudication-packet/v1",
        "item_id": item_id,
        "source_record": {
            "document_id": f"doc-{index}",
            "stock_code": f"{index:06d}",
            "review_status": "NEEDS_BLIND_REVIEW",
            "final_sentiment": "",
            "reviewer_id": "",
            "reviewed_at": "",
            "review_note": "",
            "text": f"대상 기업 사건 {index}",
        },
        "adjudication_status": "NEEDS_BLIND_ADJUDICATION",
        "stage_1_manifest_sha256": "a" * 64,
        "stage_2_manifest_sha256": "b" * 64,
    }


def _decision(item_id: str, reviewer: str, label: str) -> dict[str, object]:
    return {
        "item_id": item_id,
        "final_sentiment": label,
        "adjudication_note": f"{label} 독립 판정",
        "adjudicator_id": reviewer,
        "adjudicated_at": "2026-07-17T00:00:00+00:00",
        "adjudication_status": "CODEX_ADJUDICATED",
    }


def test_split_adjudicators_merge_with_independent_receipt_chain(tmp_path: Path) -> None:
    packet = tmp_path / "packet.jsonl"
    parts = [tmp_path / "part-1.jsonl", tmp_path / "part-2.jsonl"]
    receipts = [tmp_path / "receipt-1.json", tmp_path / "receipt-2.json"]
    output = tmp_path / "merged.jsonl"
    manifest = tmp_path / "manifest.json"
    packet_rows = [_packet("doc-1::000001", 1), _packet("doc-2::000002", 2)]
    write_jsonl(packet, packet_rows)
    write_jsonl(parts[0], [_decision("doc-1::000001", "adjudicator-1", "POSITIVE")])
    write_jsonl(parts[1], [_decision("doc-2::000002", "adjudicator-2", "NEGATIVE")])
    for index in range(2):
        create_review_receipt(
            packet_path=packet,
            decision_path=parts[index],
            codebook_path=CODEBOOK,
            prompt_path=PROMPT,
            output_path=receipts[index],
            packet_kind=ADJUDICATION_PACKET_KIND,
            role=ADJUDICATOR_ROLE,
            reviewer_id=f"adjudicator-{index + 1}",
            reviewer_model="GPT-5",
            reviewer_model_version="test",
            independent_run_id=f"{index + 1}0000000-0000-4000-8000-000000000001",
            context_id=f"{index + 3}0000000-0000-4000-8000-000000000001",
            row_start=index + 1,
            row_end=index + 1,
            run_started_at="2026-07-16T23:59:59+00:00",
            run_completed_at="2026-07-17T00:00:01+00:00",
        )
        receipt = json.loads(receipts[index].read_text(encoding="utf-8"))
        assert receipt["blindness"]["reviewer_decision_visibility"] == (
            "NOT_PROVIDED_TO_REVIEW_CONTEXT"
        )

    result = merge_adjudication_parts(
        packet_path=packet,
        part_paths=parts,
        receipt_paths=receipts,
        codebook_path=CODEBOOK,
        prompt_path=PROMPT,
        output_path=output,
        provenance_output_path=manifest,
    )
    assert result["sample_count"] == 2
    _, validated_receipts = validate_adjudication_manifest(
        manifest,
        packet_path=packet,
        decision_path=output,
        codebook_path=CODEBOOK,
        prompt_path=PROMPT,
    )
    assert len(validated_receipts) == 2

    rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
    rows[0]["final_sentiment"] = "NEGATIVE"
    write_jsonl(output, rows)
    with pytest.raises(ValueError, match="artifact"):
        validate_adjudication_manifest(
            manifest,
            packet_path=packet,
            decision_path=output,
            codebook_path=CODEBOOK,
            prompt_path=PROMPT,
        )
