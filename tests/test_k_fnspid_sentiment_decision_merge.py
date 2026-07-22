from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest


def _module() -> ModuleType:
    path = Path("scripts/merge_k_fnspid_sentiment_decisions.py")
    spec = importlib.util.spec_from_file_location("merge_sentiment_decisions", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def _decision(item_id: str, label: str) -> dict[str, object]:
    return {
        "item_id": item_id,
        "final_sentiment": label,
        "review_note": "근거",
        "reviewer_id": "codex-blind",
        "reviewed_at": "2026-07-15T00:00:00+00:00",
        "review_status": "CODEX_REVIEW_APPROVED",
    }


def test_merge_without_receipts_is_legacy_unverified(tmp_path: Path) -> None:
    module = _module()
    review = tmp_path / "review.jsonl"
    left = tmp_path / "left.jsonl"
    right = tmp_path / "right.jsonl"
    output = tmp_path / "merged.jsonl"
    _write(
        review,
        [
            {"document_id": "a", "stock_code": "1"},
            {"document_id": "b", "stock_code": "2"},
        ],
    )
    _write(left, [_decision("b::2", "NEUTRAL")])
    _write(right, [_decision("a::1", "POSITIVE")])

    with pytest.raises(ValueError, match="LEGACY_UNVERIFIED"):
        module.merge_decisions(review, [left, right], output)
    assert not output.exists()


def test_merge_rejects_missing_or_duplicate_decision(tmp_path: Path) -> None:
    module = _module()
    review = tmp_path / "review.jsonl"
    part = tmp_path / "part.jsonl"
    _write(
        review,
        [
            {"document_id": "a", "stock_code": "1"},
            {"document_id": "b", "stock_code": "2"},
        ],
    )
    _write(part, [_decision("a::1", "POSITIVE")])

    with pytest.raises(ValueError, match="LEGACY_UNVERIFIED"):
        module.merge_decisions(review, [part], tmp_path / "output.jsonl")

    _write(part, [_decision("a::1", "POSITIVE"), _decision("a::1", "POSITIVE")])
    with pytest.raises(ValueError, match="LEGACY_UNVERIFIED"):
        module.merge_decisions(review, [part], tmp_path / "output.jsonl")
