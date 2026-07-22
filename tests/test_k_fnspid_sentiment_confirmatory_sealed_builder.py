from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pyarrow as pa
import pyarrow.parquet as parquet
import pytest

from hannah_montana_ai.training.sentiment_protocol import (
    assert_sentiment_groups_disjoint,
    sentiment_provenance,
)


def _script_module(name: str, path: Path) -> ModuleType:
    scripts_path = str(Path("scripts").resolve())
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _module() -> ModuleType:
    return _script_module(
        "build_k_fnspid_sentiment_confirmatory_sealed",
        Path("scripts/build_k_fnspid_sentiment_confirmatory_sealed.py"),
    )


def _candidate(
    module: ModuleType,
    document_id: str,
    source_type: str,
    stratum: str,
    *,
    content_hash: str | None = None,
    event_cluster_id: str | None = None,
) -> Any:
    return module.Candidate(
        document_id=document_id,
        source_type=source_type,
        title=f"{document_id} 대상 기업의 객관적 금융 사건",
        snippet=f"{document_id} 사건의 확인된 사실을 설명한다.",
        source_url=f"https://example.com/{document_id}",
        content_hash=content_hash or f"hash-{document_id}",
        published_at_kst="2026-06-01T09:00:00+09:00",
        effective_trade_date="2026-06-01",
        event_cluster_id=event_cluster_id or f"event-{document_id}",
        stock_code=f"{abs(hash(document_id)) % 1_000_000:06d}",
        stock_name="테스트기업",
        sampling_stratum=stratum,
        rule_confidence=0.9,
    )


def _build_design(
    module: ModuleType,
    candidates: list[Any],
    *,
    protected_keys: frozenset[tuple[str, str]] = frozenset(),
    sample_per_stratum: int,
) -> Any:
    return module.build_sampling_design(
        candidates,
        protected_keys,
        seed=module.SAMPLING_SEED,
        sample_per_stratum=sample_per_stratum,
        frame_start=module.FRAME_START,
        frame_end=module.EXPECTED_SNAPSHOT_MAX_EFFECTIVE_TRADE_DATE,
        news_partition=module.NEWS_PARTITION,
        disclosure_partition=module.DISCLOSURE_PARTITION,
    )


def _selected_ids(design: Any) -> dict[str, dict[str, list[str]]]:
    return {
        source: {
            label: [unit.candidate.document_id for unit in units] for label, units in strata.items()
        }
        for source, strata in design.selected.items()
    }


def test_locked_contract_constants_and_exact_deterministic_allocation() -> None:
    module = _module()
    candidates = [
        _candidate(module, f"{source}-{label}-{index:03d}", source, label)
        for source in ("NEWS", "DISCLOSURE")
        for label in module.LABEL_ORDER
        for index in range(205)
    ]

    forward = _build_design(module, candidates, sample_per_stratum=200)
    reverse = _build_design(module, list(reversed(candidates)), sample_per_stratum=200)

    assert module.SAMPLING_SEED == "k-fnspid-confirmatory-sealed-v1:2026-07-15"
    assert module.NEWS_PARTITION == "CONFIRMATORY_SEALED_TEST_REVIEW"
    assert module.DISCLOSURE_PARTITION == "DISCLOSURE_CONFIRMATORY_SEALED_TEST_REVIEW"
    assert module.DEFAULT_NEWS_OUTPUT_PATH.name == "confirmatory_sealed_test_review.jsonl"
    assert (
        module.DEFAULT_DISCLOSURE_OUTPUT_PATH.name
        == "disclosure_confirmatory_sealed_test_review.jsonl"
    )
    assert _selected_ids(forward) == _selected_ids(reverse)
    for source in ("NEWS", "DISCLOSURE"):
        assert all(len(forward.selected[source][label]) == 200 for label in module.LABEL_ORDER)


def test_protected_transitive_closure_and_cross_source_selection_are_disjoint() -> None:
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
            event_cluster_id="cross-event",
        ),
        _candidate(module, "disclosure-negative", "DISCLOSURE", "NEGATIVE"),
        _candidate(module, "disclosure-neutral", "DISCLOSURE", "NEUTRAL"),
        _candidate(
            module,
            "disclosure-cross-positive",
            "DISCLOSURE",
            "POSITIVE",
            event_cluster_id="cross-event",
        ),
        _candidate(module, "disclosure-positive-alt", "DISCLOSURE", "POSITIVE"),
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

    design = _build_design(
        module,
        candidates,
        protected_keys=protected_keys,
        sample_per_stratum=1,
    )
    frame_ids = {
        unit.candidate.document_id
        for source_frames in design.frames.values()
        for units in source_frames.values()
        for unit in units
    }

    assert "protected-direct" not in frame_ids
    assert "protected-transitive" not in frame_ids
    assert _selected_ids(design)["NEWS"]["POSITIVE"] == ["news-cross-positive"]
    assert _selected_ids(design)["DISCLOSURE"]["POSITIVE"] == ["disclosure-positive-alt"]
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


def test_snapshot_cutoff_is_observed_from_parquet_and_locked(tmp_path: Path) -> None:
    module = _module()
    dataset_dir = tmp_path / "v4"
    dataset_dir.mkdir()
    parquet.write_table(
        pa.table(
            {
                "source_type": ["NEWS", "NEWS", "DISCLOSURE", "DISCLOSURE", "OTHER"],
                "effective_trade_date": [
                    "2026-07-13",
                    "2026-04-01",
                    "2026-07-12",
                    "2026-05-01",
                    "2099-01-01",
                ],
            }
        ),
        dataset_dir / "documents.parquet",
    )

    snapshot = module.inspect_snapshot_cutoff(dataset_dir)

    assert snapshot["observed_max_effective_trade_date"] == "2026-07-13"
    assert snapshot["source_date_bounds"]["NEWS"]["max_effective_trade_date"] == "2026-07-13"
    module._assert_locked_snapshot_cutoff(snapshot)
    with pytest.raises(RuntimeError):
        module._assert_locked_snapshot_cutoff({"observed_max_effective_trade_date": "2026-07-14"})


def test_write_once_blind_payload_has_no_annotation_result(tmp_path: Path) -> None:
    module = _module()
    candidate = _candidate(module, "blind-row", "NEWS", "POSITIVE")
    payload = module.blind_review_payload(candidate, module.NEWS_PARTITION)
    output_path = tmp_path / "reservation.jsonl"

    assert not (module.FORBIDDEN_RESERVATION_FIELDS & payload.keys())
    assert {
        field: payload[field]
        for field in ("final_sentiment", "reviewer_id", "reviewed_at", "review_note")
    } == {
        "final_sentiment": "",
        "reviewer_id": "",
        "reviewed_at": "",
        "review_note": "",
    }
    module._write_new_jsonl(output_path, [payload])
    with pytest.raises(FileExistsError):
        module._write_new_jsonl(output_path, [payload])
    assert json.loads(output_path.read_text(encoding="utf-8"))["document_id"] == "blind-row"


def test_correct_order_is_reservation_train_lock_then_annotation(tmp_path: Path) -> None:
    builder = _module()
    trainer = _script_module(
        "confirmatory_order_trainer",
        Path("scripts/train_kf_deberta_sentiment_v2.py"),
    )
    locker = _script_module(
        "confirmatory_order_locker",
        Path("scripts/lock_kf_deberta_sentiment_candidate.py"),
    )
    locker.__dict__["PROJECT_ROOT"] = tmp_path
    reservation_path = tmp_path / "data/gold/confirmatory_sealed_test_review.jsonl"
    report_path = tmp_path / "reports/k-fnspid-sentiment-confirmatory-sealed-sampling-design.json"
    reservation_rows = [
        builder.blind_review_payload(
            _candidate(builder, f"order-{index:03d}", "NEWS", "NEUTRAL"),
            builder.NEWS_PARTITION,
        )
        for index in range(600)
    ]
    builder._write_new_jsonl(reservation_path, reservation_rows)
    builder._write_new_json(
        report_path,
        {
            "report_role": "UNLABELED_CONFIRMATORY_RESERVATION",
            "labels_available_at_reservation": False,
            "candidate_predictions_available": False,
        },
    )

    identity_only_rows = trainer._load_sealed_reservation_rows(
        reservation_path,
        builder.NEWS_PARTITION,
        "NEWS",
    )
    assert len(identity_only_rows) == 600
    assert all("label" not in row and "final_sentiment" not in row for row in identity_only_rows)

    training_report = {
        "input_artifacts": {
            "news_confirmatory_reservation": {
                "path": str(reservation_path.relative_to(tmp_path)),
                "bytes": reservation_path.stat().st_size,
                "sha256": locker.file_sha256(reservation_path),
            }
        }
    }
    reservation_commitment, identity_keys = locker._sealed_reservation_commitment(
        training_report,
        artifact_name="news_confirmatory_reservation",
        expected_partition=builder.NEWS_PARTITION,
        expected_source="NEWS",
    )
    report_commitment = locker._regular_file_commitment(report_path)
    reservation_sha_before_annotation = locker.file_sha256(reservation_path)
    assert reservation_commitment["sample_count"] == 600
    assert identity_keys
    assert report_commitment["sha256"] == locker.file_sha256(report_path)

    annotation_path = tmp_path / "data/annotations/confirmatory_news_decisions.jsonl"
    builder._write_new_jsonl(
        annotation_path,
        [
            {
                "item_id": f"{row['document_id']}::{row['stock_code']}",
                "final_sentiment": "NEUTRAL",
            }
            for row in reservation_rows
        ],
    )
    assert annotation_path.is_file()
    assert locker.file_sha256(reservation_path) == reservation_sha_before_annotation
    assert all(row["final_sentiment"] == "" for row in reservation_rows)


def test_report_reconstructs_frames_weights_fpc_and_output_commitments(
    tmp_path: Path,
) -> None:
    module = _module()
    candidates = [
        _candidate(module, f"{source}-{label}-{index}", source, label)
        for source in ("NEWS", "DISCLOSURE")
        for label in module.LABEL_ORDER
        for index in range(5)
    ]
    design = _build_design(module, candidates, sample_per_stratum=2)
    news_units = module._flatten_selected(
        design.selected["NEWS"],
        output_seed=module.SAMPLING_SEED,
    )
    disclosure_units = module._flatten_selected(
        design.selected["DISCLOSURE"],
        output_seed=module.SAMPLING_SEED,
    )
    news_path = tmp_path / "news.jsonl"
    disclosure_path = tmp_path / "disclosure.jsonl"
    news_rows = [
        module.blind_review_payload(unit.candidate, module.NEWS_PARTITION) for unit in news_units
    ]
    disclosure_rows = [
        module.blind_review_payload(unit.candidate, module.DISCLOSURE_PARTITION)
        for unit in disclosure_units
    ]
    news_commitment = module.reservation_output_commitment(news_path, news_rows)
    disclosure_commitment = module.reservation_output_commitment(
        disclosure_path,
        disclosure_rows,
    )
    module._write_new_jsonl(news_path, news_rows)
    module._write_new_jsonl(disclosure_path, disclosure_rows)
    empty = module.IdentityCollection(
        paths=(),
        rows=(),
        group_keys=frozenset(),
        row_count=0,
        rows_without_identity=0,
    )

    report = module.build_confirmatory_sampling_report(
        design=design,
        protected={"empty": empty},
        source_audit={"eligible_candidates": len(candidates)},
        snapshot={
            "observed_max_effective_trade_date": "2026-07-13",
            "source_date_bounds": {},
        },
        news_output_path=news_path,
        disclosure_output_path=disclosure_path,
        generated_at=module.datetime(2026, 7, 15, 1, tzinfo=module.UTC),
        news_output_commitment=news_commitment,
        disclosure_output_commitment=disclosure_commitment,
    )

    for partition, units, path in (
        (module.NEWS_PARTITION, news_units, news_path),
        (module.DISCLOSURE_PARTITION, disclosure_units, disclosure_path),
    ):
        partition_report = report["partitions"][partition]
        assert partition_report["sample_count"] == 6
        assert partition_report["output"]["sha256"] == module._sha256(path)
        assert partition_report[
            "selected_sampling_unit_identity_set_sha256"
        ] == module.selected_identity_digest(units)
        for label in module.LABEL_ORDER:
            stratum = partition_report["strata"][label]
            assert stratum["frame_N_h"] == 5
            assert stratum["sample_n_h"] == 2
            assert stratum["inclusion_probability_exact"] == "2/5"
            assert stratum["design_weight_exact"] == "5/2"
            assert stratum["finite_population_correction"]["inputs"] == {
                "population_N_h": 5,
                "sample_n_h": 2,
                "sampling_fraction_f_h": pytest.approx(0.4),
                "sampling_fraction_exact": "2/5",
            }
            assert stratum["finite_population_correction"]["variance_multiplier"] == pytest.approx(
                3 / 5
            )
            assert stratum["finite_population_correction"][
                "standard_error_multiplier"
            ] == pytest.approx(math.sqrt(3 / 5))

    reconstructed_news_ids = {
        json.loads(line)["document_id"] for line in news_path.read_text().splitlines()
    }
    assert reconstructed_news_ids == {unit.candidate.document_id for unit in news_units}
    assert report["estimand_and_frame"]["effective_trade_date_end_inclusive"] == "2026-07-13"
    assert report["estimand_and_frame"]["sampling_strata_role"] == (
        "Gold 감성이 아닌 사전 고정 weak-rule auxiliary strata"
    )
    assert report["estimand_and_frame"]["future_dates_after_snapshot_claimed"] is False
    assert report["report_role"] == "UNLABELED_CONFIRMATORY_RESERVATION"
    assert report["labels_available_at_reservation"] is False
    assert report["candidate_predictions_available"] is False
    assert report["write_once_commitments"][module.NEWS_PARTITION] == news_commitment


def test_protected_path_discovery_includes_all_provenance_components(
    tmp_path: Path,
) -> None:
    module = _module()
    paths = [
        tmp_path / "data/curation/k_fnspid_sentiment/train_review.jsonl",
        tmp_path / "data/curation/k_fnspid_sentiment/prevalence_packet.jsonl",
        tmp_path / "data/training/k_fnspid_sentiment_silver.jsonl",
        tmp_path / "data/training/other_train.jsonl",
        tmp_path / "data/evaluation/test_gold.jsonl",
        tmp_path / "data/gold/existing_gold.jsonl",
    ]
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}\n", encoding="utf-8")
    excluded = tmp_path / "data/gold/confirmatory_sealed_test_review.jsonl"
    excluded.write_text("{}\n", encoding="utf-8")

    discovered = module.discover_protected_paths(
        tmp_path,
        excluded_paths=frozenset({excluded}),
    )

    assert paths[0] in discovered["curation_review_train_dev_test_prevalence_components"]
    assert paths[1] in discovered["curation_review_train_dev_test_prevalence_components"]
    assert discovered["silver_sets"] == (paths[2],)
    assert discovered["other_training_sets"] == (paths[3],)
    assert discovered["evaluation_sets"] == (paths[4],)
    assert discovered["existing_gold_sets"] == (paths[5],)
    assert excluded not in discovered["existing_gold_sets"]
