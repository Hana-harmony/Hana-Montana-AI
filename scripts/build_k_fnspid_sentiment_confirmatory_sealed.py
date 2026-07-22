from __future__ import annotations

import argparse
import json
import math
from collections.abc import Iterable
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

import pyarrow.parquet as parquet

from hannah_montana_ai.training.sentiment_protocol import (
    LABEL_ORDER,
    assert_sentiment_groups_disjoint,
)

from build_k_fnspid_sentiment_dataset import (  # isort: skip
    CODEBOOK_VERSION,
    DEFAULT_DATASET_DIR,
    PROJECT_ROOT,
    Candidate,
    _review_payload,
    _sha256,
    load_candidates,
)
from build_k_fnspid_sentiment_prevalence_sealed import (  # isort: skip
    IdentityCollection,
    SamplingDesign,
    SamplingUnit,
    _encode_jsonl,
    _flatten_selected,
    _identity_set_digest,
    _load_identity_collection,
    _path_report,
    _preflight_new_outputs,
    _protected_collection_report,
    _stratum_report,
    _unit_identity_set_digest,
    _write_new_json,
    _write_new_jsonl,
    build_sampling_design,
)

FRAME_START = "2026-04-01"
EXPECTED_SNAPSHOT_MAX_EFFECTIVE_TRADE_DATE = "2026-07-13"
SAMPLE_PER_STRATUM = 200
SAMPLING_SEED = "k-fnspid-confirmatory-sealed-v1:2026-07-15"
WEAK_STRATUM_VERSION = "k-fnspid-confirmatory-weak-stratum/v1"
NEWS_PARTITION = "CONFIRMATORY_SEALED_TEST_REVIEW"
DISCLOSURE_PARTITION = "DISCLOSURE_CONFIRMATORY_SEALED_TEST_REVIEW"
DEFAULT_NEWS_OUTPUT_PATH = PROJECT_ROOT / "data/gold/confirmatory_sealed_test_review.jsonl"
DEFAULT_DISCLOSURE_OUTPUT_PATH = (
    PROJECT_ROOT / "data/gold/disclosure_confirmatory_sealed_test_review.jsonl"
)
DEFAULT_REPORT_PATH = (
    PROJECT_ROOT / "reports/k-fnspid-sentiment-confirmatory-sealed-sampling-design-v2.json"
)
SOURCE_TYPES = ("NEWS", "DISCLOSURE")
FORBIDDEN_RESERVATION_FIELDS = frozenset(
    {
        "sentiment",
        "sampling_stratum",
        "weak_label",
        "weak_sentiment",
        "rule_confidence",
        "inclusion_probability",
        "analysis_weight",
        "design_weight",
    }
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="후보 학습 전에 K-FNSPID 확증용 무라벨 봉인 reservation을 생성한다."
    )
    parser.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET_DIR)
    parser.add_argument("--news-output-path", type=Path, default=DEFAULT_NEWS_OUTPUT_PATH)
    parser.add_argument(
        "--disclosure-output-path",
        type=Path,
        default=DEFAULT_DISCLOSURE_OUTPUT_PATH,
    )
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()

    output_paths = (args.news_output_path, args.disclosure_output_path, args.report_path)
    _preflight_new_outputs(output_paths)
    snapshot = inspect_snapshot_cutoff(args.dataset_dir)
    _assert_locked_snapshot_cutoff(snapshot)

    protected = load_confirmatory_protected_identity_collections(
        project_root=PROJECT_ROOT,
        excluded_paths=frozenset(
            {args.news_output_path.resolve(), args.disclosure_output_path.resolve()}
        ),
    )
    protected_keys = frozenset(
        key for collection in protected.values() for key in collection.group_keys
    )
    candidates, source_audit = load_candidates(
        args.dataset_dir,
        [],
        source_types=set(SOURCE_TYPES),
    )
    frame_end = str(snapshot["observed_max_effective_trade_date"])
    design = build_sampling_design(
        candidates,
        protected_keys,
        seed=SAMPLING_SEED,
        sample_per_stratum=SAMPLE_PER_STRATUM,
        frame_start=FRAME_START,
        frame_end=frame_end,
        news_partition=NEWS_PARTITION,
        disclosure_partition=DISCLOSURE_PARTITION,
    )

    news_units = _flatten_selected(design.selected["NEWS"], output_seed=SAMPLING_SEED)
    disclosure_units = _flatten_selected(
        design.selected["DISCLOSURE"],
        output_seed=SAMPLING_SEED,
    )
    news_payloads = [blind_review_payload(unit.candidate, NEWS_PARTITION) for unit in news_units]
    disclosure_payloads = [
        blind_review_payload(unit.candidate, DISCLOSURE_PARTITION) for unit in disclosure_units
    ]
    _assert_exact_allocation(design)
    _assert_reservation_disjointness(design, protected)
    assert_blind_reservation(news_payloads, expected_partition=NEWS_PARTITION)
    assert_blind_reservation(
        disclosure_payloads,
        expected_partition=DISCLOSURE_PARTITION,
    )

    news_output_commitment = reservation_output_commitment(
        args.news_output_path,
        news_payloads,
    )
    disclosure_output_commitment = reservation_output_commitment(
        args.disclosure_output_path,
        disclosure_payloads,
    )
    generated_at = datetime.now(UTC)
    report = build_confirmatory_sampling_report(
        design=design,
        protected=protected,
        source_audit=source_audit,
        snapshot=snapshot,
        news_output_path=args.news_output_path,
        disclosure_output_path=args.disclosure_output_path,
        generated_at=generated_at,
        news_output_commitment=news_output_commitment,
        disclosure_output_commitment=disclosure_output_commitment,
    )
    _write_new_jsonl(args.news_output_path, news_payloads)
    _write_new_jsonl(args.disclosure_output_path, disclosure_payloads)
    if _path_report(args.news_output_path) != news_output_commitment:
        raise RuntimeError("NEWS 봉인 reservation 기록 후 commitment가 달라졌습니다.")
    if _path_report(args.disclosure_output_path) != disclosure_output_commitment:
        raise RuntimeError("DISCLOSURE 봉인 reservation 기록 후 commitment가 달라졌습니다.")
    _write_new_json(args.report_path, report)
    print(json.dumps(report, ensure_ascii=False))


def inspect_snapshot_cutoff(dataset_dir: Path) -> dict[str, Any]:
    documents_path = dataset_dir / "documents.parquet"
    if documents_path.is_symlink() or not documents_path.is_file():
        raise FileNotFoundError(f"v4 documents parquet이 올바르지 않습니다: {documents_path}")
    table = parquet.read_table(
        documents_path,
        columns=["source_type", "effective_trade_date"],
    )
    dates_by_source: dict[str, list[str]] = {source: [] for source in SOURCE_TYPES}
    invalid_date_count = 0
    for batch in table.to_batches(max_chunksize=100_000):
        payload = batch.to_pydict()
        for raw_source, raw_date in zip(
            payload["source_type"],
            payload["effective_trade_date"],
            strict=True,
        ):
            source = str(raw_source or "").strip().upper()
            if source not in dates_by_source:
                continue
            value = str(raw_date or "").strip()
            try:
                normalized = datetime.strptime(value, "%Y-%m-%d").date().isoformat()
            except ValueError:
                invalid_date_count += 1
                continue
            dates_by_source[source].append(normalized)
    if invalid_date_count:
        raise ValueError(f"NEWS/DISCLOSURE effective_trade_date 형식 오류: {invalid_date_count}건")
    if any(not dates for dates in dates_by_source.values()):
        raise ValueError("NEWS/DISCLOSURE snapshot 날짜가 비어 있습니다.")
    observed_max = max(max(dates) for dates in dates_by_source.values())
    return {
        "documents_path": str(documents_path.resolve()),
        "documents_bytes": documents_path.stat().st_size,
        "documents_sha256": _sha256(documents_path),
        "observed_max_effective_trade_date": observed_max,
        "source_date_bounds": {
            source: {
                "row_count_with_effective_trade_date": len(dates),
                "min_effective_trade_date": min(dates),
                "max_effective_trade_date": max(dates),
            }
            for source, dates in dates_by_source.items()
        },
    }


def _assert_locked_snapshot_cutoff(snapshot: dict[str, Any]) -> None:
    observed = snapshot.get("observed_max_effective_trade_date")
    if observed != EXPECTED_SNAPSHOT_MAX_EFFECTIVE_TRADE_DATE:
        raise RuntimeError(
            "확증 표본 모집단 snapshot이 사전 고정값과 다릅니다: "
            f"{observed!r} != {EXPECTED_SNAPSHOT_MAX_EFFECTIVE_TRADE_DATE!r}"
        )


def discover_protected_paths(
    project_root: Path,
    *,
    excluded_paths: frozenset[Path] = frozenset(),
) -> dict[str, tuple[Path, ...]]:
    excluded = {path.resolve() for path in excluded_paths}

    def collect(root: Path, pattern: str = "*.jsonl") -> tuple[Path, ...]:
        return tuple(path for path in sorted(root.rglob(pattern)) if path.resolve() not in excluded)

    training_paths = collect(project_root / "data/training")
    silver_paths = tuple(path for path in training_paths if "silver" in path.name.casefold())
    silver_set = set(silver_paths)
    return {
        "curation_review_train_dev_test_prevalence_components": collect(
            project_root / "data/curation"
        ),
        "silver_sets": silver_paths,
        "other_training_sets": tuple(path for path in training_paths if path not in silver_set),
        "evaluation_sets": collect(project_root / "data/evaluation"),
        "existing_gold_sets": collect(project_root / "data/gold"),
    }


def load_confirmatory_protected_identity_collections(
    *,
    project_root: Path,
    excluded_paths: frozenset[Path] = frozenset(),
) -> dict[str, IdentityCollection]:
    return {
        category: _load_identity_collection(paths)
        for category, paths in discover_protected_paths(
            project_root,
            excluded_paths=excluded_paths,
        ).items()
    }


def blind_review_payload(candidate: Candidate, partition: str) -> dict[str, Any]:
    payload = _review_payload(candidate, partition)
    assert_blind_reservation([payload], expected_partition=partition)
    return payload


def reservation_output_commitment(
    path: Path,
    rows: list[dict[str, Any]],
) -> dict[str, str | int]:
    encoded = _encode_jsonl(rows)
    try:
        display_path = str(path.resolve().relative_to(PROJECT_ROOT.resolve()))
    except ValueError:
        display_path = str(path.resolve())
    return {
        "path": display_path,
        "bytes": len(encoded),
        "sha256": sha256(encoded).hexdigest(),
    }


def assert_blind_reservation(
    rows: list[dict[str, Any]],
    *,
    expected_partition: str,
) -> None:
    for index, row in enumerate(rows, start=1):
        exposed = FORBIDDEN_RESERVATION_FIELDS & row.keys()
        if exposed:
            raise ValueError(f"봉인 reservation에 금지 필드가 있습니다: {index}:{sorted(exposed)}")
        if (
            row.get("partition") != expected_partition
            or row.get("review_status") != "NEEDS_BLIND_REVIEW"
            or row.get("final_sentiment") != ""
            or row.get("reviewer_id") != ""
            or row.get("reviewed_at") != ""
            or row.get("review_note") != ""
        ):
            raise ValueError(f"봉인 reservation 행이 blind 계약을 위반했습니다: {index}")


def _assert_exact_allocation(design: SamplingDesign) -> None:
    for source_type in SOURCE_TYPES:
        for label in LABEL_ORDER:
            selected_count = len(design.selected[source_type][label])
            if selected_count != SAMPLE_PER_STRATUM:
                raise RuntimeError(
                    f"{source_type}/{label} 표본 수 오류: {selected_count}/{SAMPLE_PER_STRATUM}"
                )


def _assert_reservation_disjointness(
    design: SamplingDesign,
    protected: dict[str, IdentityCollection],
) -> None:
    protected_rows = [row for collection in protected.values() for row in collection.rows]
    news_rows = [
        unit.candidate.group_row() for units in design.selected["NEWS"].values() for unit in units
    ]
    disclosure_rows = [
        unit.candidate.group_row()
        for units in design.selected["DISCLOSURE"].values()
        for unit in units
    ]
    assert_sentiment_groups_disjoint(
        {
            NEWS_PARTITION: news_rows,
            DISCLOSURE_PARTITION: disclosure_rows,
            "ALL_EXISTING_PROVENANCE_COMPONENTS": protected_rows,
        }
    )


def build_confirmatory_sampling_report(
    *,
    design: SamplingDesign,
    protected: dict[str, IdentityCollection],
    source_audit: dict[str, Any],
    snapshot: dict[str, Any],
    news_output_path: Path,
    disclosure_output_path: Path,
    generated_at: datetime,
    news_output_commitment: dict[str, str | int] | None = None,
    disclosure_output_commitment: dict[str, str | int] | None = None,
) -> dict[str, Any]:
    protected_keys = frozenset(
        key for collection in protected.values() for key in collection.group_keys
    )
    frame_end = str(snapshot["observed_max_effective_trade_date"])
    resolved_news_commitment = news_output_commitment or _path_report(news_output_path)
    resolved_disclosure_commitment = disclosure_output_commitment or _path_report(
        disclosure_output_path
    )
    return {
        "schema_version": "k-fnspid-sentiment-confirmatory-sealed-sampling-design/v2",
        "generated_at": generated_at.astimezone(UTC).isoformat(),
        "dataset_version": "K-FNSPID-v4",
        "codebook_version": CODEBOOK_VERSION,
        "report_role": "UNLABELED_CONFIRMATORY_RESERVATION",
        "labels_available_at_reservation": False,
        "candidate_predictions_available": False,
        "reservation_state_at_generation": {
            "labels_available_at_reservation": False,
            "candidate_predictions_available": False,
            "annotation_allowed_before_candidate_lock": False,
            "annotation_result_fields": {
                "final_sentiment": "",
                "reviewer_id": "",
                "reviewed_at": "",
                "review_note": "",
            },
            "workflow_status_field": "NEEDS_BLIND_REVIEW",
            "required_order": [
                "BUILD_UNLABELED_RESERVATION",
                "TRAIN_WITH_IDENTITY_ONLY_OVERLAP_PURGE",
                "LOCK_CANDIDATE_AND_COMMIT_RESERVATION_REPORT",
                "ANNOTATE_SEPARATE_DECISION_ARTIFACT",
            ],
        },
        "estimand_and_frame": {
            "primary_estimands": (
                "K-FNSPID-v4 snapshot의 적격 canonical 문서-증권 유한 모집단에서 "
                "출처별 후보·고정 기준선의 설계가중 plug-in Macro-F1과 "
                "후보-minus-기준선 paired contrast"
            ),
            "descriptive_secondary_estimand": (
                "사후 Gold label로 기술하는 출처별 모집단 감성 비율"
            ),
            "sampling_strata_role": (
                "Gold 감성이 아닌 사전 고정 weak-rule auxiliary strata"
            ),
            "eligible_unit": (
                "품질 계약과 단일 PRIMARY 대상 조건을 만족하고 기존 provenance "
                "구성요소와 겹치지 않는 canonical document-security unit"
            ),
            "effective_trade_date_start": FRAME_START,
            "effective_trade_date_end_inclusive": frame_end,
            "snapshot_max_effective_trade_date_observed_at_generation": frame_end,
            "future_dates_after_snapshot_claimed": False,
            "source_types": list(SOURCE_TYPES),
            "snapshot": snapshot,
        },
        "sampling_design": {
            "method": "stratified_equal_allocation_without_replacement_by_seeded_sha256_rank/v1",
            "seed": SAMPLING_SEED,
            "hash_function": "SHA-256",
            "strata": list(LABEL_ORDER),
            "weak_rule_stratum": {
                "version": WEAK_STRATUM_VERSION,
                "gold_label_role": "none; sampling auxiliary only",
                "review_packet_exposure": "omitted",
            },
            "sample_per_stratum": SAMPLE_PER_STRATUM,
            "sampling_unit": (
                "canonical representative of a transitive provenance component "
                "within the locked snapshot date/source frame"
            ),
            "source_selection_order": ["NEWS", "DISCLOSURE"],
            "cross_source_rule": (
                "NEWS-selected provenance components are removed from the DISCLOSURE "
                "frame before DISCLOSURE ranking"
            ),
            "equal_probability_contract": (
                "Within each final source/weak stratum, all N_h units receive one "
                "predeclared seeded SHA-256 rank and the first n_h units are selected; "
                "pi_h=f_h=n_h/N_h and design_weight_h=N_h/n_h."
            ),
            "finite_population_correction_contract": (
                "Evaluator must use reported N_h, n_h and f_h. The SRSWOR variance "
                "multiplier is 1-f_h=(N_h-n_h)/N_h, with its square root applied to "
                "standard errors."
            ),
        },
        "protected_identity_sets": {
            "combined": {
                "group_key_count": len(protected_keys),
                "identity_set_sha256": _identity_set_digest(protected_keys),
            },
            "categories": {
                category: _protected_collection_report(collection)
                for category, collection in protected.items()
            },
            "identity_overlap_allowed": False,
            "transitive_component_closure": True,
        },
        "candidate_source_audit": source_audit,
        "component_audit": design.component_audit,
        "write_once_commitments": {
            "policy": "create-exclusive immutable outputs; overwrite and symlink refused",
            NEWS_PARTITION: resolved_news_commitment,
            DISCLOSURE_PARTITION: resolved_disclosure_commitment,
        },
        "partitions": {
            NEWS_PARTITION: _confirmatory_partition_report(
                source_type="NEWS",
                output_path=news_output_path,
                frames=design.frames["NEWS"],
                selected=design.selected["NEWS"],
                output_commitment=resolved_news_commitment,
            ),
            DISCLOSURE_PARTITION: _confirmatory_partition_report(
                source_type="DISCLOSURE",
                output_path=disclosure_output_path,
                frames=design.frames["DISCLOSURE"],
                selected=design.selected["DISCLOSURE"],
                output_commitment=resolved_disclosure_commitment,
            ),
        },
    }


def _confirmatory_partition_report(
    *,
    source_type: str,
    output_path: Path,
    frames: dict[str, tuple[SamplingUnit, ...]],
    selected: dict[str, tuple[SamplingUnit, ...]],
    output_commitment: dict[str, str | int] | None = None,
) -> dict[str, Any]:
    selected_units = _flatten_selected(selected, output_seed=SAMPLING_SEED)
    return {
        "source_type": source_type,
        "sample_count": len(selected_units),
        "output": output_commitment or _path_report(output_path),
        "frame_sampling_unit_identity_set_sha256": _unit_identity_set_digest(
            unit for units in frames.values() for unit in units
        ),
        "selected_sampling_unit_identity_set_sha256": _unit_identity_set_digest(selected_units),
        "strata": {
            label: _confirmatory_stratum_report(frames[label], selected[label])
            for label in LABEL_ORDER
        },
    }


def _confirmatory_stratum_report(
    frame: tuple[SamplingUnit, ...],
    selected: tuple[SamplingUnit, ...],
) -> dict[str, Any]:
    report = _stratum_report(frame, selected)
    population = int(report["frame_N_h"])
    sample = int(report["sample_n_h"])
    sampling_fraction = sample / population
    variance_multiplier = (population - sample) / population
    report.update(
        {
            "sampling_fraction": sampling_fraction,
            "sampling_fraction_exact": f"{sample}/{population}",
            "design_weight": population / sample,
            "design_weight_exact": f"{population}/{sample}",
            "finite_population_correction": {
                "inputs": {
                    "population_N_h": population,
                    "sample_n_h": sample,
                    "sampling_fraction_f_h": sampling_fraction,
                    "sampling_fraction_exact": f"{sample}/{population}",
                },
                "variance_multiplier": variance_multiplier,
                "variance_multiplier_exact": f"{population - sample}/{population}",
                "standard_error_multiplier": math.sqrt(variance_multiplier),
            },
        }
    )
    return report


def selected_identity_digest(units: Iterable[SamplingUnit]) -> str:
    return _unit_identity_set_digest(units)


if __name__ == "__main__":
    main()
