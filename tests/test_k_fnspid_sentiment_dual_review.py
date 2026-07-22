from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest


def _module() -> ModuleType:
    path = Path("scripts/adjudicate_k_fnspid_sentiment_reviews.py")
    spec = importlib.util.spec_from_file_location("adjudicate_sentiment_reviews", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def _decision(item_id: str, label: str, reviewer: str) -> dict[str, object]:
    return {
        "item_id": item_id,
        "final_sentiment": label,
        "review_note": f"{label} 근거",
        "reviewer_id": reviewer,
        "reviewed_at": "2026-07-15T00:00:00+00:00",
        "review_status": "CODEX_REVIEW_APPROVED",
    }


def test_legacy_dual_review_without_receipts_is_fail_closed(tmp_path: Path) -> None:
    module = _module()
    review = tmp_path / "review.jsonl"
    stage_1 = tmp_path / "stage1.jsonl"
    stage_2 = tmp_path / "stage2.jsonl"
    packet = tmp_path / "packet.jsonl"
    adjudication = tmp_path / "adjudication.jsonl"
    output = tmp_path / "final.jsonl"
    _write(
        review,
        [
            {
                "document_id": "a",
                "stock_code": "1",
                "review_status": "NEEDS_BLIND_REVIEW",
                "text": "호재",
            },
            {
                "document_id": "b",
                "stock_code": "2",
                "review_status": "NEEDS_BLIND_REVIEW",
                "text": "혼합",
            },
        ],
    )
    _write(
        stage_1,
        [_decision("a::1", "POSITIVE", "r1"), _decision("b::2", "NEUTRAL", "r1")],
    )
    _write(
        stage_2,
        [_decision("a::1", "POSITIVE", "r2"), _decision("b::2", "NEGATIVE", "r2")],
    )

    with pytest.raises(ValueError, match="LEGACY_UNVERIFIED"):
        module.create_adjudication_packet(review, stage_1, stage_2, packet)
    assert not adjudication.exists()
    assert not output.exists()


def test_dual_review_rejects_same_reviewer(tmp_path: Path) -> None:
    module = _module()
    review = tmp_path / "review.jsonl"
    stage_1 = tmp_path / "stage1.jsonl"
    stage_2 = tmp_path / "stage2.jsonl"
    _write(
        review,
        [{"document_id": "a", "stock_code": "1", "review_status": "NEEDS_BLIND_REVIEW"}],
    )
    _write(stage_1, [_decision("a::1", "POSITIVE", "same")])
    _write(stage_2, [_decision("a::1", "POSITIVE", "same")])

    with pytest.raises(ValueError, match="LEGACY_UNVERIFIED"):
        module.create_adjudication_packet(
            review, stage_1, stage_2, tmp_path / "packet.jsonl"
        )


def test_latest_review_timestamp_compares_instants_not_iso_strings() -> None:
    module = _module()

    assert module._latest_review_timestamp(
        "2026-07-17T00:14:19+09:00",
        "2026-07-16T15:46:09.516474Z",
    ) == "2026-07-16T15:46:09.516474Z"
