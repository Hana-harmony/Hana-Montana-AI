from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path
from typing import Any

from scripts.adjudicate_k_fnspid_sentiment_reviews import (
    create_adjudication_packet,
    merge_dual_reviews,
)
from scripts.k_fnspid_sentiment_review_provenance import (
    ADJUDICATION_PACKET_KIND,
    ADJUDICATOR_ROLE,
    REVIEW_PACKET_KIND,
    REVIEW_ROLE,
    create_review_receipt,
)
from scripts.merge_k_fnspid_sentiment_decisions import merge_decisions

CODEBOOK_PATH = Path("docs/datasets/k-fnspid-sentiment-codebook.md")
PROMPT_PATH = Path("docs/datasets/k-fnspid-sentiment-review-prompt-v1.md")
RUN_IDS = (
    "10000000-0000-4000-8000-000000000001",
    "20000000-0000-4000-8000-000000000002",
    "30000000-0000-4000-8000-000000000003",
)
CONTEXT_IDS = (
    "40000000-0000-4000-8000-000000000004",
    "50000000-0000-4000-8000-000000000005",
    "60000000-0000-4000-8000-000000000006",
)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def build_verified_dual_review_provenance(
    *,
    root: Path,
    review_path: Path,
    final_decisions: list[dict[str, Any]],
    final_decisions_path: Path,
) -> Path:
    stage_paths = (root / "stage-1.jsonl", root / "stage-2.jsonl")
    stage_receipts = (root / "stage-1-receipt.json", root / "stage-2-receipt.json")
    stage_outputs = (root / "stage-1-complete.jsonl", root / "stage-2-complete.jsonl")
    stage_manifests = (root / "stage-1-manifest.json", root / "stage-2-manifest.json")
    review_count = len(read_jsonl(review_path))
    if review_count != len(final_decisions):
        raise ValueError("test fixture review와 decision 수가 다릅니다.")

    for stage_index in range(2):
        reviewer_key = f"reviewer_{stage_index + 1}"
        stage_rows = [
            {
                "item_id": decision["item_id"],
                "final_sentiment": decision[reviewer_key]["final_sentiment"],
                "review_note": decision[reviewer_key]["label_evidence"],
                "reviewer_id": decision[reviewer_key]["reviewer_id"],
                "reviewed_at": decision[reviewer_key]["reviewed_at"],
                "review_status": "CODEX_REVIEW_APPROVED",
            }
            for decision in final_decisions
        ]
        reviewer_ids = {str(row["reviewer_id"]) for row in stage_rows}
        if len(reviewer_ids) != 1:
            raise ValueError("test fixture는 stage당 하나의 reviewer run만 지원합니다.")
        write_jsonl(stage_paths[stage_index], stage_rows)
        started, completed = _run_bounds(
            [str(row["reviewed_at"]) for row in stage_rows]
        )
        create_review_receipt(
            packet_path=review_path,
            decision_path=stage_paths[stage_index],
            codebook_path=CODEBOOK_PATH,
            prompt_path=PROMPT_PATH,
            output_path=stage_receipts[stage_index],
            packet_kind=REVIEW_PACKET_KIND,
            role=REVIEW_ROLE,
            reviewer_id=next(iter(reviewer_ids)),
            reviewer_model="GPT-5",
            reviewer_model_version="test-fixture-2026-07-16",
            independent_run_id=RUN_IDS[stage_index],
            context_id=CONTEXT_IDS[stage_index],
            row_start=1,
            row_end=review_count,
            run_started_at=started,
            run_completed_at=completed,
        )
        merge_decisions(
            review_path,
            [stage_paths[stage_index]],
            stage_outputs[stage_index],
            receipt_paths=[stage_receipts[stage_index]],
            codebook_path=CODEBOOK_PATH,
            prompt_path=PROMPT_PATH,
            provenance_output_path=stage_manifests[stage_index],
        )

    adjudication_packet = root / "adjudication-packet.jsonl"
    create_adjudication_packet(
        review_path,
        stage_outputs[0],
        stage_outputs[1],
        adjudication_packet,
        stage_1_provenance_path=stage_manifests[0],
        stage_2_provenance_path=stage_manifests[1],
        codebook_path=CODEBOOK_PATH,
        prompt_path=PROMPT_PATH,
    )
    adjudication_rows = [
        decision["adjudication"]
        for decision in final_decisions
        if decision["reviewer_1"]["final_sentiment"]
        != decision["reviewer_2"]["final_sentiment"]
    ]
    adjudication_path = root / "adjudication.jsonl"
    write_jsonl(adjudication_path, adjudication_rows)
    adjudication_receipt: Path | None = None
    if adjudication_rows:
        adjudicator_ids = {str(row["adjudicator_id"]) for row in adjudication_rows}
        if len(adjudicator_ids) != 1:
            raise ValueError("test fixture는 하나의 adjudicator run만 지원합니다.")
        adjudication_receipt = root / "adjudication-receipt.json"
        started, completed = _run_bounds(
            [str(row["adjudicated_at"]) for row in adjudication_rows]
        )
        create_review_receipt(
            packet_path=adjudication_packet,
            decision_path=adjudication_path,
            codebook_path=CODEBOOK_PATH,
            prompt_path=PROMPT_PATH,
            output_path=adjudication_receipt,
            packet_kind=ADJUDICATION_PACKET_KIND,
            role=ADJUDICATOR_ROLE,
            reviewer_id=next(iter(adjudicator_ids)),
            reviewer_model="GPT-5",
            reviewer_model_version="test-fixture-2026-07-16",
            independent_run_id=RUN_IDS[2],
            context_id=CONTEXT_IDS[2],
            row_start=1,
            row_end=len(adjudication_rows),
            run_started_at=started,
            run_completed_at=completed,
        )

    final_decisions_path.unlink(missing_ok=True)
    provenance_path = root / "dual-review-provenance.json"
    provenance_path.unlink(missing_ok=True)
    merge_dual_reviews(
        review_path,
        stage_outputs[0],
        stage_outputs[1],
        adjudication_path,
        final_decisions_path,
        stage_1_provenance_path=stage_manifests[0],
        stage_2_provenance_path=stage_manifests[1],
        adjudication_packet_path=(adjudication_packet if adjudication_rows else None),
        adjudication_receipt_path=adjudication_receipt,
        codebook_path=CODEBOOK_PATH,
        prompt_path=PROMPT_PATH,
        provenance_output_path=provenance_path,
    )
    return provenance_path


def _run_bounds(values: list[str]) -> tuple[str, str]:
    from datetime import datetime

    parsed = [datetime.fromisoformat(value.replace("Z", "+00:00")) for value in values]
    return (
        (min(parsed) - timedelta(seconds=1)).isoformat(),
        (max(parsed) + timedelta(seconds=1)).isoformat(),
    )
