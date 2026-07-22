from __future__ import annotations

import json
from pathlib import Path

import pytest

from hannah_montana_ai.training.sentiment_gold_provenance import (
    GoldProvenanceInput,
    validate_gold_provenance,
)
from tests.sentiment_review_provenance_fixture import (
    build_verified_dual_review_provenance,
    write_jsonl,
)


def _review() -> dict[str, object]:
    return {
        "schema_version": "k-fnspid-sentiment-review-row/v1",
        "dataset_version": "K-FNSPID-v4",
        "codebook_version": "k-fnspid-sentiment-codebook/v1",
        "partition": "TRAIN_REVIEW",
        "document_id": "news-1",
        "source_type": "NEWS",
        "stock_code": "000001",
        "stock_name": "test",
        "text": "대상 기업이 신규 공급 계약을 체결했다.",
        "source_url": "https://example.test/1",
        "canonical_url": "https://example.test/1",
        "content_hash": "hash-1",
        "event_cluster_id": "cluster-1",
        "published_at_kst": "2026-03-01T09:00:00+09:00",
        "effective_trade_date": "2026-03-02",
        "review_status": "NEEDS_BLIND_REVIEW",
        "final_sentiment": "",
        "reviewer_id": "",
        "reviewed_at": "",
        "review_note": "",
    }


def _reviewer(reviewer_id: str) -> dict[str, object]:
    return {
        "stage_1": "DIRECTIONAL",
        "stage_2": "POSITIVE",
        "final_sentiment": "POSITIVE",
        "label_evidence": "대상 기업의 신규 공급 계약",
        "decision_path": "NEUTRAL_DIRECTIONAL_THEN_POLARITY",
        "reviewer_id": reviewer_id,
        "reviewed_at": "2026-07-17T00:00:00+00:00",
        "reviewer_type": "CODEX_AI",
        "model_blind": True,
        "market_blind": True,
    }


def _decision() -> dict[str, object]:
    return {
        "schema_version": "k-fnspid-sentiment-dual-review-decision/v1",
        "item_id": "news-1::000001",
        "reviewer_1": _reviewer("reviewer-1"),
        "reviewer_2": _reviewer("reviewer-2"),
        "independent_reviewer_count": 2,
        "inter_reviewer_agreement": True,
        "decision_path": "INDEPENDENT_REVIEWER_AGREEMENT",
        "adjudication": None,
        "final_sentiment": "POSITIVE",
        "review_note": "independent agreement",
        "reviewer_id": "reviewer-1+reviewer-2",
        "reviewed_at": "2026-07-17T00:00:00+00:00",
        "review_status": "CODEX_REVIEW_APPROVED",
        "reviewer_type": "INDEPENDENT_CODEX_AI",
        "model_blind": True,
        "market_blind": True,
    }


def _fixture(tmp_path: Path) -> GoldProvenanceInput:
    review_path = tmp_path / "review.jsonl"
    decision_path = tmp_path / "final.jsonl"
    gold_path = tmp_path / "gold.jsonl"
    write_jsonl(review_path, [_review()])
    decision = _decision()
    manifest_path = build_verified_dual_review_provenance(
        root=tmp_path,
        review_path=review_path,
        final_decisions=[decision],
        final_decisions_path=decision_path,
    )
    write_jsonl(
        gold_path,
        [
            {
                "item_id": decision["item_id"],
                "sentiment": decision["final_sentiment"],
                "review_status": "CODEX_REVIEW_APPROVED",
                "model_blind": True,
                "market_blind": True,
                "independent_reviewer_count": 2,
                "inter_reviewer_agreement": True,
                "decision_path": "INDEPENDENT_REVIEWER_AGREEMENT",
            }
        ],
    )
    return GoldProvenanceInput("fixture", gold_path, manifest_path)


def test_verified_gold_is_bound_to_dual_review_receipt_chain(tmp_path: Path) -> None:
    contract = _fixture(tmp_path)
    result = validate_gold_provenance(contract)
    assert result["status"] == "VERIFIED_BLIND_PROVENANCE"
    assert result["gold_row_count"] == 1


def test_gold_label_tamper_and_missing_manifest_fail_closed(tmp_path: Path) -> None:
    contract = _fixture(tmp_path)
    rows = [json.loads(line) for line in contract.gold_path.read_text().splitlines()]
    rows[0]["sentiment"] = "NEGATIVE"
    write_jsonl(contract.gold_path, rows)
    with pytest.raises(ValueError, match="dual-review decision"):
        validate_gold_provenance(contract)

    with pytest.raises(ValueError, match="dual-review manifest"):
        validate_gold_provenance(
            GoldProvenanceInput("fixture", contract.gold_path, tmp_path / "missing.json")
        )
