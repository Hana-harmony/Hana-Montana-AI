from __future__ import annotations

import importlib.util
import sys
from dataclasses import replace
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

from hannah_montana_ai.training.sentiment_protocol import (
    assert_sentiment_groups_disjoint,
    sentiment_provenance,
)


def _module() -> ModuleType:
    scripts_path = str(Path("scripts").resolve())
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    path = Path("scripts/build_k_fnspid_sentiment_prevalence_sealed.py")
    spec = importlib.util.spec_from_file_location(
        "build_k_fnspid_sentiment_prevalence_sealed",
        path,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _candidate(
    module: ModuleType,
    document_id: str,
    source_type: str,
    stratum: str,
    *,
    stock_code: str = "000001",
    content_hash: str | None = None,
    event_cluster_id: str | None = None,
) -> Any:
    return module.Candidate(
        document_id=document_id,
        source_type=source_type,
        title=f"{document_id} 기업의 주요 금융 사건 발표",
        snippet=f"{document_id} 관련 객관적 사실을 설명한다.",
        source_url=f"https://example.com/{document_id}",
        content_hash=content_hash or f"hash-{document_id}",
        published_at_kst="2026-05-04T09:00:00+09:00",
        effective_trade_date="2026-05-04",
        event_cluster_id=event_cluster_id or f"event-{document_id}",
        stock_code=stock_code,
        stock_name="테스트기업",
        sampling_stratum=stratum,
        rule_confidence=0.9,
    )


def _selected_document_ids(design: Any) -> dict[str, dict[str, list[str]]]:
    return {
        source_type: {
            label: [unit.candidate.document_id for unit in units]
            for label, units in by_label.items()
        }
        for source_type, by_label in design.selected.items()
    }


def _frame_document_ids(design: Any) -> dict[str, dict[str, list[str]]]:
    return {
        source_type: {
            label: [unit.candidate.document_id for unit in units]
            for label, units in by_label.items()
        }
        for source_type, by_label in design.frames.items()
    }


def test_sampling_is_deterministic_independent_of_input_order() -> None:
    module = _module()
    candidates = [
        _candidate(module, f"{source}-{label}-{index}", source, label)
        for source in ("NEWS", "DISCLOSURE")
        for label in module.LABEL_ORDER
        for index in range(6)
    ]

    forward = module.build_sampling_design(
        candidates,
        frozenset(),
        seed="fixed-test-seed",
        sample_per_stratum=3,
    )
    reverse = module.build_sampling_design(
        list(reversed(candidates)),
        frozenset(),
        seed="fixed-test-seed",
        sample_per_stratum=3,
    )

    assert _selected_document_ids(forward) == _selected_document_ids(reverse)
    assert _frame_document_ids(forward) == _frame_document_ids(reverse)


def test_equal_probability_hash_rank_has_no_stock_cap() -> None:
    module = _module()
    seed = "equal-probability-seed"
    candidates = [
        _candidate(
            module,
            f"{source}-{label}-{index:02d}",
            source,
            label,
            stock_code="005930",
        )
        for source in ("NEWS", "DISCLOSURE")
        for label in module.LABEL_ORDER
        for index in range(10)
    ]

    design = module.build_sampling_design(
        candidates,
        frozenset(),
        seed=seed,
        sample_per_stratum=3,
    )

    for label in module.LABEL_ORDER:
        frame = design.frames["NEWS"][label]
        expected = sorted(
            frame,
            key=lambda unit: (
                module._stable_digest(
                    unit.candidate.document_id,
                    f"{seed}:{module.NEWS_PARTITION}:{label}",
                ),
                unit.identity_sha256,
            ),
        )[:3]
        assert design.selected["NEWS"][label] == tuple(expected)
        assert {unit.candidate.stock_code for unit in expected} == {"005930"}


def test_stratum_report_contains_exact_probability_and_analysis_weight() -> None:
    module = _module()
    candidates = [
        _candidate(module, f"{source}-{label}-{index}", source, label)
        for source in ("NEWS", "DISCLOSURE")
        for label in module.LABEL_ORDER
        for index in range(10)
    ]
    design = module.build_sampling_design(
        candidates,
        frozenset(),
        seed="weight-seed",
        sample_per_stratum=3,
    )

    report = module._stratum_report(
        design.frames["NEWS"]["NEGATIVE"],
        design.selected["NEWS"]["NEGATIVE"],
    )

    assert report["frame_N_h"] == 10
    assert report["sample_n_h"] == 3
    assert report["inclusion_probability"] == pytest.approx(0.3)
    assert report["inclusion_probability_exact"] == "3/10"
    assert report["analysis_weight"] == pytest.approx(10 / 3)
    assert report["analysis_weight_exact"] == "10/3"


def test_disclosure_adverse_auxiliary_is_sampling_only() -> None:
    module = _module()
    candidate = _candidate(
        module,
        "disclosure-dilution",
        "DISCLOSURE",
        "NEUTRAL",
    )
    candidate = replace(
        candidate,
        title="주요사항보고서(유상증자결정) 공시 제출",
    )

    assert candidate.sampling_stratum == "NEUTRAL"
    assert module._prevalence_sampling_stratum(candidate) == "NEGATIVE"
    payload = module._review_payload(candidate, module.DISCLOSURE_PARTITION)
    assert "sampling_stratum" not in payload
    assert "sentiment" not in payload
    assert payload["final_sentiment"] == ""


def test_protected_closure_and_cross_source_selection_are_disjoint() -> None:
    module = _module()
    protected_row = {
        "text": "기존 보호 사건",
        "source_url": "https://protected.example.com/event",
        "content_hash": "protected-hash",
        "event_cluster_id": "protected-event",
    }
    protected_keys = sentiment_provenance(protected_row).group_keys
    candidates = [
        _candidate(module, "news-negative", "NEWS", "NEGATIVE"),
        _candidate(module, "news-neutral", "NEWS", "NEUTRAL"),
        _candidate(
            module,
            "news-cross-positive",
            "NEWS",
            "POSITIVE",
            event_cluster_id="cross-source-event",
        ),
        _candidate(module, "disclosure-negative", "DISCLOSURE", "NEGATIVE"),
        _candidate(module, "disclosure-neutral", "DISCLOSURE", "NEUTRAL"),
        _candidate(
            module,
            "disclosure-cross-positive",
            "DISCLOSURE",
            "POSITIVE",
            event_cluster_id="cross-source-event",
        ),
        _candidate(
            module,
            "disclosure-positive-alternative",
            "DISCLOSURE",
            "POSITIVE",
        ),
        _candidate(
            module,
            "protected-direct",
            "NEWS",
            "NEUTRAL",
            content_hash="protected-hash",
            event_cluster_id="protected-bridge",
        ),
        _candidate(
            module,
            "protected-transitive",
            "NEWS",
            "NEUTRAL",
            event_cluster_id="protected-bridge",
        ),
    ]

    design = module.build_sampling_design(
        candidates,
        protected_keys,
        seed="disjoint-seed",
        sample_per_stratum=1,
    )
    frame_ids = {
        unit.candidate.document_id
        for source_frames in design.frames.values()
        for units in source_frames.values()
        for unit in units
    }
    selected_ids = _selected_document_ids(design)

    assert "protected-direct" not in frame_ids
    assert "protected-transitive" not in frame_ids
    assert selected_ids["NEWS"]["POSITIVE"] == ["news-cross-positive"]
    assert selected_ids["DISCLOSURE"]["POSITIVE"] == [
        "disclosure-positive-alternative"
    ]
    assert design.component_audit[
        "disclosure_unit_count_excluded_by_news_selection"
    ] == 1
    assert_sentiment_groups_disjoint(
        {
            "NEWS": [
                unit.candidate.group_row()
                for units in design.selected["NEWS"].values()
                for unit in units
            ],
            "DISCLOSURE": [
                unit.candidate.group_row()
                for units in design.selected["DISCLOSURE"].values()
                for unit in units
            ],
            "PROTECTED": [protected_row],
        }
    )


def test_immutable_writer_rejects_existing_file_and_symlink(tmp_path: Path) -> None:
    module = _module()
    existing = tmp_path / "existing.jsonl"
    existing.write_text("protected\n", encoding="utf-8")
    symlink = tmp_path / "symlink.jsonl"
    symlink.symlink_to(tmp_path / "missing-target.jsonl")

    with pytest.raises(FileExistsError):
        module._write_new_file_atomic(existing, b"replacement\n")
    with pytest.raises(FileExistsError):
        module._write_new_file_atomic(symlink, b"replacement\n")

    assert existing.read_text(encoding="utf-8") == "protected\n"
    assert symlink.is_symlink()
