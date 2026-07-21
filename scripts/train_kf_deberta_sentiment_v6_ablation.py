from __future__ import annotations

import argparse
import json
import math
import os
import platform
import shutil
import sys
import uuid
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, cast

import numpy as np
import torch
from transformers import AutoTokenizer

from hannah_montana_ai.training.sentiment_gold_provenance import (
    gold_provenance_paths,
    validate_all_gold_provenance,
)
from hannah_montana_ai.training.sentiment_protocol import (
    assert_sentiment_groups_disjoint,
    decontaminate_public_partitions,
    sentiment_provenance,
    stratified_hash_three_way_split,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts import train_kf_deberta_sentiment_v2 as v5  # noqa: E402
from scripts import train_kf_deberta_sentiment_v6 as v6  # noqa: E402

sys.modules.setdefault("train_kf_deberta_sentiment_v2", v5)

from scripts import train_k_fnspid_sentiment_ablation as data_contract  # noqa: E402
from scripts.train_k_fnspid_sentiment_ablation import (  # noqa: E402
    AblationMode,
    AblationPaths,
)

MODEL_SEEDS = (17, 42, 73)
SCHEMA_VERSION = "k-fnspid-compute-matched-sentiment-ablation-training/v3"
SELECTION_SCHEMA_VERSION = "k-fnspid-compute-matched-sentiment-ablation-selection/v3"
WINNER_SCHEMA_VERSION = "k-fnspid-compute-matched-sentiment-ablation-winner/v3"
MATRIX_SCHEMA_VERSION = "k-fnspid-compute-matched-sentiment-ablation-matrix/v3"
FULL_REUSE_SCHEMA_VERSION = "kf-deberta-v6-full-ablation-artifact-reuse/v1"
FULL_REUSE_STATUS = "VERIFIED_EXACT_ARTIFACT_REFERENCE_ARM"
ARTIFACT_SCHEMA_VERSION = "kf-deberta-compute-matched-sentiment-ablation-artifact/v3"
ARTIFACT_ROLE = "RESEARCH_ABLATION_NOT_DEPLOYABLE"
MODEL_FAMILY = v6.MODEL_FAMILY
FINAL_HOLM_NO_K_ROLE = "NO_K_TRAIN_ROWS_WITH_SHARED_K_DEV"
LEGACY_V5_NO_K_ROLE = "LEGACY_DIAGNOSTIC_ONLY_NOT_FINAL_HOLM_ELIGIBLE"
ZERO_K_EXPOSURE_MODE = "ZERO_K_EXPOSURE"
STAGE2_TRAINED = "TRAINED_COMPUTE_MATCHED_REFINEMENT_CONTROL"
CANDIDATE_STAGE1_ROW_EXPOSURES = 32_907
CANDIDATE_STAGE2_REFINEMENT_ROWS = 1_794
CANDIDATE_STAGE1_EPOCHS = 2
CANDIDATE_STAGE2_EPOCHS = 4
CANDIDATE_BATCH_SIZE = 8
CANDIDATE_GRADIENT_ACCUMULATION_STEPS = 2
CANDIDATE_STAGE1_OPTIMIZER_STEPS = 4_114
CANDIDATE_STAGE2_OPTIMIZER_STEPS = 452
PUBLIC_CONTROL_PER_LABEL = {
    AblationMode.NO_K: 598,
    AblationMode.NEWS_ONLY: 200,
    AblationMode.DISCLOSURE_ONLY: 398,
    AblationMode.FULL: 0,
}
EXPECTED_K_GOLD_ROWS = {
    AblationMode.NO_K: 0,
    AblationMode.NEWS_ONLY: 1_194,
    AblationMode.DISCLOSURE_ONLY: 600,
    AblationMode.FULL: 1_794,
}
ESTIMAND_ID = "K_TRAINING_ROW_INTERVENTION_CONDITIONAL_ON_SHARED_K_DEVELOPMENT"


@dataclass(frozen=True)
class ComputeMatchedStage:
    rows: list[dict[str, Any]]
    audit: dict[str, Any]


def parser() -> argparse.ArgumentParser:
    value = v6.parser()
    value.description = "v6 동일 구조로 K-FNSPID 데이터 개입 ablation을 수행한다."
    value.add_argument(
        "--mode",
        choices=(*tuple(mode.value for mode in AblationMode), ZERO_K_EXPOSURE_MODE),
    )
    value.add_argument("--aggregate", action="store_true")
    value.add_argument("--aggregate-matrix", action="store_true")
    value.add_argument("--report-dir", type=Path)
    value.add_argument("--artifact-root", type=Path)
    value.add_argument("--selection-report-path", type=Path)
    value.add_argument("--winner-manifest-path", type=Path)
    value.add_argument("--matrix-report-path", type=Path)
    value.add_argument("--reuse-full-candidate", action="store_true")
    value.add_argument("--candidate-report-path", type=Path)
    value.add_argument("--candidate-artifact-dir", type=Path)
    value.set_defaults(output_dir=None, report_path=None)
    return value


def _mode_slug(mode: AblationMode) -> str:
    return mode.value.casefold().replace("_", "-")


def _default_paths(mode: AblationMode, seed: int) -> tuple[Path, Path]:
    slug = _mode_slug(mode)
    output = PROJECT_ROOT / f"artifacts/sentiment/v6-ablations/{slug}/seed{seed}"
    report = (
        PROJECT_ROOT / f"reports/ablations/v6/{slug}/kf-deberta-sentiment-v6-{slug}-seed{seed}.json"
    )
    return output, report


def _default_candidate_paths(seed: int) -> tuple[Path, Path]:
    return (
        PROJECT_ROOT / f"artifacts/sentiment/v6-candidates/seed{seed}",
        PROJECT_ROOT / f"reports/candidates/kf-deberta-sentiment-v6-seed{seed}.json",
    )


def _ablation_paths(args: argparse.Namespace) -> Any:
    return AblationPaths(
        dataset_dir=args.dataset_dir,
        news_silver=args.silver_path,
        disclosure_silver=args.disclosure_silver_path,
        main_news_gold=args.train_gold_path,
        news_auxiliary_gold=args.news_auxiliary_gold_path,
        disclosure_auxiliary_gold=args.disclosure_auxiliary_gold_path,
        news_auxiliary_report=args.news_auxiliary_report_path,
        disclosure_auxiliary_report=args.disclosure_auxiliary_report_path,
        news_development_gold=args.development_gold_path,
        disclosure_development_gold=args.disclosure_development_gold_path,
        news_reservation=args.news_sealed_review_path,
        disclosure_reservation=args.disclosure_sealed_review_path,
        sampling_design=args.sampling_design_report,
    )


def _architecture_contract() -> dict[str, Any]:
    return {
        "schema_version": "compute-matched-shared-residual-kf-deberta-ablation-recipe/v3",
        "encoder": "shared-kf-deberta",
        "lora_layers": list(v6.LORA_LAYERS),
        "lora_target_modules": list(v6.LORA_TARGET_MODULES),
        "lora_rank": v6.LORA_RANK,
        "lora_alpha": v6.LORA_ALPHA,
        "lora_dropout": v6.LORA_DROPOUT,
        "head_architecture": v6.EXPECTED_HEAD_ARCHITECTURE,
        "source_domains": list(v6.DOMAIN_ORDER),
        "head_outputs": ["neutral_vs_directional", "negative_vs_positive"],
        "composition": "normalized-hierarchical-log-probabilities/v1",
        "loss": v6.LOSS_CONTRACT_VERSION,
        "checkpoint_primary": "weakest-source-domain-macro-f1",
        "calibration": "calibration-only-sequential-temperature-neutral-threshold-shrunk/v1",
        "stage2": "compute-matched-k-gold-plus-public-control-heads-only/v3",
        "compute_matching": {
            "stage1_row_exposures_per_epoch": CANDIDATE_STAGE1_ROW_EXPOSURES,
            "stage2_refinement_rows": CANDIDATE_STAGE2_REFINEMENT_ROWS,
            "stage1_optimizer_steps": CANDIDATE_STAGE1_OPTIMIZER_STEPS,
            "stage2_optimizer_steps": CANDIDATE_STAGE2_OPTIMIZER_STEPS,
            "stable_order": "SHA256(item_sha256||group_sha256)",
            "public_control_source": "PUBLIC_TRAIN_ONLY",
        },
        "estimand": ESTIMAND_ID,
    }


def _training_arguments(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "model_seed": args.seed,
        "data_selection_seed": v5.DATA_SELECTION_SEED,
        "max_length": args.max_length,
        "stage1_epochs": args.stage1_epochs,
        "stage2_epochs": args.stage2_epochs,
        "batch_size": args.batch_size,
        "eval_batch_size": args.eval_batch_size,
        "gradient_accumulation_steps": args.gradient_accumulation_steps,
        "stage1_learning_rate": args.stage1_learning_rate,
        "stage2_learning_rate": args.stage2_learning_rate,
        "weight_decay": args.weight_decay,
        "rdrop_alpha": args.rdrop_alpha,
        "gradient_checkpointing": args.gradient_checkpointing,
    }


def _recipe_commitment(args: argparse.Namespace) -> str:
    arguments = _training_arguments(args)
    arguments.pop("model_seed")
    canonical = json.dumps(
        {"architecture": _architecture_contract(), "training_arguments": arguments},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(canonical).hexdigest()


def _canonical_sha256(value: object) -> str:
    return sha256(
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def _row_identity(row: dict[str, Any]) -> dict[str, str]:
    provenance = sentiment_provenance(row)
    item_sha256 = str(v5._rows_commitment([row], include_label=True)["sha256"])
    group_sha256 = _canonical_sha256(
        {
            "canonical_url": provenance.canonical_url,
            "normalized_text": provenance.normalized_text,
            "content_hash": provenance.content_hash,
            "event_cluster_id": provenance.event_cluster_id,
        }
    )
    return {
        "item_sha256": item_sha256,
        "group_sha256": group_sha256,
        "ordering_sha256": sha256(f"{item_sha256}:{group_sha256}".encode("ascii")).hexdigest(),
    }


def _stable_rows(
    rows: list[dict[str, Any]],
    *,
    require_unique: bool,
) -> list[tuple[dict[str, Any], dict[str, str]]]:
    identified = [(row, _row_identity(row)) for row in rows]
    item_ids = [identity["item_sha256"] for _, identity in identified]
    if require_unique and len(set(item_ids)) != len(item_ids):
        raise RuntimeError("compute-matched source에 중복 item commitment가 있습니다.")
    return sorted(
        identified,
        key=lambda entry: (
            entry[1]["ordering_sha256"],
            entry[1]["item_sha256"],
            entry[1]["group_sha256"],
        ),
    )


def _sequence_commitment(
    identified: list[tuple[dict[str, Any], dict[str, str]]],
) -> dict[str, int | str]:
    sequence = [
        {
            "position": position,
            **identity,
        }
        for position, (_, identity) in enumerate(identified)
    ]
    return {"row_count": len(sequence), "sha256": _canonical_sha256(sequence)}


def _stage1_compute_matched_exposures(
    unique_rows: list[dict[str, Any]],
) -> ComputeMatchedStage:
    if not unique_rows or len(unique_rows) > CANDIDATE_STAGE1_ROW_EXPOSURES:
        raise RuntimeError("Stage 1 고유 행 수가 compute-matched 노출 예산과 맞지 않습니다.")
    ordered = _stable_rows(unique_rows, require_unique=True)
    exposure_identified = [
        ordered[index % len(ordered)] for index in range(CANDIDATE_STAGE1_ROW_EXPOSURES)
    ]
    exposure_rows = [dict(row) for row, _ in exposure_identified]
    frequency = Counter(identity["item_sha256"] for _, identity in exposure_identified)
    frequency_records = [
        {"item_sha256": item_sha256, "exposure_count": frequency[item_sha256]}
        for item_sha256 in sorted(frequency)
    ]
    counts = list(frequency.values())
    unique_commitment = v5._rows_commitment(unique_rows, include_label=True)
    exposure_commitment = v5._rows_commitment(exposure_rows, include_label=True)
    audit = {
        "schema_version": "stable-hash-cyclic-stage1-exposure/v1",
        "source_unique_rows_commitment": unique_commitment,
        "source_unique_row_count": len(unique_rows),
        "stable_unique_order_commitment": _sequence_commitment(ordered),
        "stable_order": "SHA256(item_sha256||group_sha256)",
        "cycling": "ROUND_ROBIN_OVER_STABLE_UNIQUE_ORDER",
        "target_exposure_count_per_epoch": CANDIDATE_STAGE1_ROW_EXPOSURES,
        "exposure_rows_commitment": exposure_commitment,
        "exposure_sequence_commitment": _sequence_commitment(exposure_identified),
        "exposure_frequency_sha256": _canonical_sha256(frequency_records),
        "minimum_exposures_per_unique_row": min(counts),
        "maximum_exposures_per_unique_row": max(counts),
        "all_source_rows_exposed": len(frequency) == len(unique_rows),
    }
    if (
        exposure_commitment["row_count"] != CANDIDATE_STAGE1_ROW_EXPOSURES
        or not audit["all_source_rows_exposed"]
        or max(counts) - min(counts) > 1
    ):
        raise RuntimeError("Stage 1 compute-matched 순환 노출 계약이 일치하지 않습니다.")
    return ComputeMatchedStage(rows=exposure_rows, audit=audit)


def _selected_public_controls(
    public_rows: list[dict[str, Any]],
    *,
    per_label: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    selected_source_rows: list[dict[str, Any]] = []
    selected_training_rows: list[dict[str, Any]] = []
    label_sequences: dict[str, dict[str, int | str]] = {}
    for label in v6.LABEL_ORDER:
        candidates = _stable_rows(
            [row for row in public_rows if str(row.get("label", "")) == label],
            require_unique=True,
        )
        if len(candidates) < per_label:
            raise RuntimeError(f"PUBLIC_TRAIN {label} refinement control이 부족합니다.")
        chosen = candidates[:per_label]
        label_sequences[label] = _sequence_commitment(chosen)
        for rank, (row, identity) in enumerate(chosen):
            selected_source_rows.append(row)
            selected_training_rows.append(
                {
                    **row,
                    "dataset": "PUBLIC_REFINEMENT_CONTROL",
                    "compute_match_control_rank": rank,
                    "compute_match_source_item_sha256": identity["item_sha256"],
                    "compute_match_source_group_sha256": identity["group_sha256"],
                }
            )
    return selected_training_rows, {
        "selection": "FIRST_N_PER_LABEL_BY_STABLE_ITEM_GROUP_SHA",
        "requested_per_label": {label: per_label for label in v6.LABEL_ORDER},
        "selected_per_label": v5._label_distribution(selected_training_rows),
        "public_source_pool_commitment": v5._rows_commitment(
            public_rows,
            include_label=True,
        ),
        "selected_source_rows_commitment": v5._rows_commitment(
            selected_source_rows,
            include_label=True,
        ),
        "selected_training_rows_commitment": v5._rows_commitment(
            selected_training_rows,
            include_label=True,
        ),
        "label_sequence_commitments": label_sequences,
    }


def _stage2_compute_matched_refinement(
    prepared: Any,
    gold_rows: list[dict[str, Any]],
) -> ComputeMatchedStage:
    mode = prepared.mode
    expected_gold = EXPECTED_K_GOLD_ROWS[mode]
    if len(gold_rows) != expected_gold:
        raise RuntimeError(
            f"{mode.value} K Gold 행 수가 고정 refinement 계약과 다릅니다: "
            f"expected={expected_gold}, actual={len(gold_rows)}"
        )
    public_rows = [
        row for row in prepared.train_rows if str(row.get("dataset", "")) == "PUBLIC_TRAIN"
    ]
    if len(public_rows) != 7_413 or any(
        v5._target_security(row) or str(row.get("source_type", "")).upper() != "NEWS"
        for row in public_rows
    ):
        raise RuntimeError("공개 refinement control source 계약이 다릅니다.")
    controls, control_audit = _selected_public_controls(
        public_rows,
        per_label=PUBLIC_CONTROL_PER_LABEL[mode],
    )
    identified = _stable_rows(
        [*map(dict, gold_rows), *controls],
        require_unique=True,
    )
    rows = [dict(row) for row, _ in identified]
    domain_label_counts: dict[str, dict[str, int]] = {}
    for row in rows:
        domain = v6.strict_source_domain(
            str(row.get("source_type", "")),
            v5._target_security(row),
        )
        domain_label_counts.setdefault(
            domain,
            {label: 0 for label in v6.LABEL_ORDER},
        )[str(row["label"])] += 1
    if len(rows) != CANDIDATE_STAGE2_REFINEMENT_ROWS or any(
        count < 1 for counts in domain_label_counts.values() for count in counts.values()
    ):
        raise RuntimeError("Stage 2 compute-matched refinement 행 계약이 다릅니다.")
    if mode is AblationMode.NO_K and any(
        str(row.get("dataset", "")).startswith("K_FNSPID") for row in rows
    ):
        raise RuntimeError("NO_K Stage 2에 K-FNSPID 행이 포함되었습니다.")
    audit = {
        "schema_version": "compute-matched-stage2-refinement-control/v1",
        "mode": mode.value,
        "row_count": len(rows),
        "rows_commitment": v5._rows_commitment(rows, include_label=True),
        "row_sequence_commitment": _sequence_commitment(identified),
        "eligible_k_gold_row_count": len(gold_rows),
        "eligible_k_gold_rows_commitment": v5._rows_commitment(
            gold_rows,
            include_label=True,
        ),
        "eligible_k_gold_label_distribution": v5._label_distribution(gold_rows),
        "public_control_row_count": len(controls),
        "public_control_label_distribution": v5._label_distribution(controls),
        "public_control": control_audit,
        "training_label_distribution": v5._label_distribution(rows),
        "training_dataset_distribution": dict(
            sorted(Counter(str(row.get("dataset", "")) for row in rows).items())
        ),
        "domain_label_counts": domain_label_counts,
        "k_training_rows_used": len(gold_rows),
        "no_k_training_exposure": len(gold_rows) == 0,
    }
    return ComputeMatchedStage(rows=rows, audit=audit)


def _compute_matched_stages(
    prepared: Any,
    gold_rows: list[dict[str, Any]],
) -> tuple[ComputeMatchedStage, ComputeMatchedStage]:
    stage1 = _stage1_compute_matched_exposures(prepared.train_rows)
    if (
        stage1.audit["source_unique_rows_commitment"]
        != (prepared.prepared_partition_commitments["TRAIN"])
    ):
        raise RuntimeError("고유 TRAIN commitment와 Stage 1 source commitment가 다릅니다.")
    stage2 = _stage2_compute_matched_refinement(prepared, gold_rows)
    return stage1, stage2


def _expected_optimizer_steps(row_count: int, epochs: int, args: argparse.Namespace) -> int:
    batches = math.ceil(row_count / int(args.batch_size))
    return math.ceil(batches / int(args.gradient_accumulation_steps)) * epochs


def _validate_compute_matched_schedule(args: argparse.Namespace) -> None:
    if (
        args.stage1_epochs != CANDIDATE_STAGE1_EPOCHS
        or args.stage2_epochs != CANDIDATE_STAGE2_EPOCHS
        or args.batch_size != CANDIDATE_BATCH_SIZE
        or args.gradient_accumulation_steps != CANDIDATE_GRADIENT_ACCUMULATION_STEPS
        or _expected_optimizer_steps(
            CANDIDATE_STAGE1_ROW_EXPOSURES,
            args.stage1_epochs,
            args,
        )
        != CANDIDATE_STAGE1_OPTIMIZER_STEPS
        or _expected_optimizer_steps(
            CANDIDATE_STAGE2_REFINEMENT_ROWS,
            args.stage2_epochs,
            args,
        )
        != CANDIDATE_STAGE2_OPTIMIZER_STEPS
    ):
        raise SystemExit("ablation schedule은 candidate와 동일한 4114/452 step으로 고정됩니다.")


def _optimizer_step_contract(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "schema_version": "candidate-compute-matched-optimizer-steps/v1",
        "stage1": {
            "row_exposures_per_epoch": CANDIDATE_STAGE1_ROW_EXPOSURES,
            "epochs": args.stage1_epochs,
            "optimizer_steps": CANDIDATE_STAGE1_OPTIMIZER_STEPS,
        },
        "stage2": {
            "refinement_rows": CANDIDATE_STAGE2_REFINEMENT_ROWS,
            "epochs": args.stage2_epochs,
            "optimizer_steps": CANDIDATE_STAGE2_OPTIMIZER_STEPS,
        },
        "batch_size": args.batch_size,
        "gradient_accumulation_steps": args.gradient_accumulation_steps,
        "candidate_steps_exactly_matched": True,
    }


def _estimand_contract() -> dict[str, Any]:
    return {
        "estimand_id": ESTIMAND_ID,
        "holm_no_k_role": FINAL_HOLM_NO_K_ROLE,
        "intervention": "K_FNSPID_TRAINING_ROWS_BY_SOURCE",
        "conditioned_on": ("COMMON_K_DEVELOPMENT_CHECKPOINT_CALIBRATION_AND_ADAPTIVE_SELECTION"),
        "common_k_development_labels_used": True,
        "interpretation": (
            "K training-row intervention conditional on common K development selection"
        ),
        "does_not_estimate_zero_k_exposure": True,
        "zero_k_exposure_is_separate_exploratory_diagnostic": True,
    }


def _statistical_analysis_plan_contract() -> dict[str, Any]:
    return {
        "schema_version": "k-fnspid-compute-matched-ablation-sap/v1",
        "holm_family_modes": [mode.value for mode in AblationMode],
        "holm_reference": AblationMode.NO_K.value,
        "holm_no_k_role": FINAL_HOLM_NO_K_ROLE,
        "estimand_id": ESTIMAND_ID,
        "matched_unit": "MODEL_SEED",
        "fixed_model_seeds": list(MODEL_SEEDS),
        "primary_metric": "WEAKEST_SOURCE_DOMAIN_MACRO_F1",
        "secondary_metric": "OVERALL_MACRO_F1",
        "candidate_compute_matched": True,
        "common_k_development_conditioning": True,
        "zero_k_exposure_mode": ZERO_K_EXPOSURE_MODE,
        "zero_k_exposure_holm_eligible": False,
        "independent_generalization_evidence": False,
    }


def _prepare_zero_k_public_only(paths: AblationPaths) -> Any:
    public = decontaminate_public_partitions(
        {
            "TRAIN": v5._load_public_rows(paths.dataset_dir / "ratings_train.csv"),
            "VALIDATION": v5._load_public_rows(paths.dataset_dir / "ratings_val.csv"),
            "TEST": [],
        }
    )[0]
    development = stratified_hash_three_way_split(
        public["VALIDATION"],
        checkpoint_name="CHECKPOINT",
        calibration_name="CALIBRATION",
        selection_name="SELECTION",
        minimum_per_label=v5.MIN_DEVELOPMENT_LABEL_COUNT,
    )
    train_rows = [
        {
            **row,
            "source_type": "NEWS",
            "sample_weight": 1.0,
            "dataset": "PUBLIC_TRAIN",
        }
        for row in public["TRAIN"]
    ]
    checkpoint_rows = [
        {**row, "source_type": "NEWS", "dataset": "PUBLIC_CHECKPOINT"}
        for row in development["CHECKPOINT"]
    ]
    calibration_rows = [
        {**row, "source_type": "NEWS", "dataset": "PUBLIC_CALIBRATION"}
        for row in development["CALIBRATION"]
    ]
    selection_rows = [
        {**row, "source_type": "NEWS", "dataset": "PUBLIC_SELECTION"}
        for row in development["SELECTION"]
    ]
    assert_sentiment_groups_disjoint(
        {
            "TRAIN": train_rows,
            "CHECKPOINT": checkpoint_rows,
            "CALIBRATION": calibration_rows,
            "SELECTION": selection_rows,
        }
    )
    commitments = v5._prepared_partition_commitments(
        train_rows=train_rows,
        checkpoint_rows=checkpoint_rows,
        calibration_rows=calibration_rows,
        selection_rows=selection_rows,
        news_reservation=[],
        disclosure_reservation=[],
    )
    return data_contract.PreparedAblation(
        mode=AblationMode.NO_K,
        train_rows=train_rows,
        checkpoint_rows=checkpoint_rows,
        calibration_rows=calibration_rows,
        selection_rows=selection_rows,
        news_reservation=[],
        disclosure_reservation=[],
        target_swap_rows=[],
        prepared_partition_commitments=commitments,
        public_audit={"status": "PUBLIC_ONLY_ZERO_K_EXPOSURE"},
        news_silver_audit={"status": "NOT_OPENED"},
        disclosure_silver_audit={"status": "NOT_OPENED"},
        final_overlap_audit={"status": "PUBLIC_PARTITIONS_DISJOINT"},
        raw_source_counts={
            "PUBLIC_TRAIN": len(train_rows),
            "K_FNSPID_CODEX_GOLD": 0,
            "K_FNSPID_NEWS_AUXILIARY_CODEX_GOLD": 0,
            "K_FNSPID_DISCLOSURE_AUXILIARY_CODEX_GOLD": 0,
            "K_FNSPID_RULE_SILVER": 0,
            "K_FNSPID_DISCLOSURE_RULE_SILVER": 0,
        },
    )


def _zero_k_exposure_validation(
    paths: AblationPaths,
    args: argparse.Namespace,
    recipe_records: dict[str, Any],
) -> dict[str, Any]:
    public_paths = {
        "public_train": paths.dataset_dir / "ratings_train.csv",
        "public_validation": paths.dataset_dir / "ratings_val.csv",
    }
    for name, path in public_paths.items():
        v6.assert_training_path_allowed(path, name)
        v5._require_regular_input(path, name)
    prepared = _prepare_zero_k_public_only(paths)
    gold_rows = _validate_prepared(prepared)
    stage1, stage2 = _compute_matched_stages(prepared, gold_rows)
    base_source = v6.resolve_base_source(args.base_source, verify_pinned=False)
    return {
        "schema_version": "zero-k-exposure-exploratory-diagnostic/v1",
        "status": "VALIDATED_WITHOUT_TRAINING",
        "ablation_mode": ZERO_K_EXPOSURE_MODE,
        "exploratory_diagnostic": True,
        "holm_eligible": False,
        "training_implemented": False,
        "public_test_opened": False,
        "k_training_inputs_opened": False,
        "k_development_inputs_opened": False,
        "input_artifacts": {
            name: v5._input_artifact_record(path) for name, path in public_paths.items()
        },
        "recipe_artifacts": recipe_records,
        "prepared_partition_commitments": prepared.prepared_partition_commitments,
        "partition_count": {
            "TRAIN_UNIQUE": len(prepared.train_rows),
            "STAGE1_EXPOSURES_PER_EPOCH": len(stage1.rows),
            "CHECKPOINT": len(prepared.checkpoint_rows),
            "CALIBRATION": len(prepared.calibration_rows),
            "SELECTION": len(prepared.selection_rows),
            "STAGE2_PUBLIC_CONTROL": len(stage2.rows),
        },
        "development_contract": {
            "source": "PUBLIC_VALIDATION_ONLY",
            "k_development_rows": 0,
            "source_domains": ["NEWS_UNTARGETED"],
            "comparable_to_holm_estimand": False,
        },
        "compute_matching": {
            "stage1": stage1.audit,
            "stage2": stage2.audit,
            "optimizer_step_contract": _optimizer_step_contract(args),
        },
        "statistical_analysis_plan": _statistical_analysis_plan_contract(),
        "residual_contract": {
            "NEWS_TARGETED": "EXCLUDED_FROM_OPTIMIZER_AND_EXACT_ZERO",
            "DISCLOSURE_TARGETED": "EXCLUDED_FROM_OPTIMIZER_AND_EXACT_ZERO",
        },
        "separation_from_holm": {
            "holm_estimand_id": ESTIMAND_ID,
            "holm_no_k_role": FINAL_HOLM_NO_K_ROLE,
            "reason": (
                "Holm comparison conditions on shared K development; this diagnostic does not."
            ),
        },
        "base_source_kind": base_source.kind,
        "base_source": base_source.provenance,
    }


def _recipe_paths() -> dict[str, Path]:
    return {
        "v6_ablation_runner": Path(__file__).resolve(),
        "v6_trainer": Path(v6.__file__).resolve(),
        "ablation_data_contract": Path(data_contract.__file__).resolve(),
        "v5_data_contract": Path(v5.__file__).resolve(),
        "sentiment_input": PROJECT_ROOT / "src/hannah_montana_ai/services/sentiment_input.py",
        "sentiment_protocol": PROJECT_ROOT / "src/hannah_montana_ai/training/sentiment_protocol.py",
        "pyproject": PROJECT_ROOT / "pyproject.toml",
        "uv_lock": PROJECT_ROOT / "uv.lock",
    }


def _records(paths: dict[str, Path]) -> dict[str, dict[str, int | str]]:
    return {
        name: v6._regular_file_record(path, PROJECT_ROOT) for name, path in sorted(paths.items())
    }


def _assert_records_unchanged(
    expected: dict[str, dict[str, int | str]],
    paths: dict[str, Path],
) -> None:
    if _records(paths) != expected:
        raise RuntimeError("ablation 실행 중 학습 code/dependency가 변경되었습니다.")


def _validate_prepared(prepared: Any) -> list[dict[str, Any]]:
    if prepared.mode is AblationMode.FULL and (
        prepared.prepared_partition_commitments != v6.EXPECTED_FULL_COMMITMENTS
    ):
        raise RuntimeError("FULL ablation이 v6 고정 학습 분할과 다릅니다.")
    for row in [
        *prepared.train_rows,
        *prepared.checkpoint_rows,
        *prepared.calibration_rows,
        *prepared.selection_rows,
    ]:
        v6.strict_source_domain(
            str(row.get("source_type", "")),
            v5._target_security(row),
        )
    gold_rows = [
        row
        for row in prepared.train_rows
        if v6.GOLD_DATASET_MARKER in str(row.get("dataset", ""))
        and "SILVER" not in str(row.get("dataset", ""))
    ]
    if prepared.mode is AblationMode.NO_K and gold_rows:
        raise RuntimeError("NO_K ablation에 Gold refinement 행이 포함되었습니다.")
    if prepared.mode is not AblationMode.NO_K and not gold_rows:
        raise RuntimeError("K-FNSPID ablation에 적합한 Gold refinement 행이 없습니다.")
    return gold_rows


def _stage2_intervention_contract(
    prepared: Any,
    stage2: ComputeMatchedStage,
) -> dict[str, Any]:
    audit = stage2.audit
    return {
        "status": STAGE2_TRAINED,
        "eligible_k_gold_rows": audit["eligible_k_gold_row_count"],
        "public_control_rows": audit["public_control_row_count"],
        "total_refinement_rows": audit["row_count"],
        "public_control_per_label": PUBLIC_CONTROL_PER_LABEL[prepared.mode],
        "stage2_skipped": False,
        "candidate_optimizer_steps_matched": True,
        "interpretation": (
            "Removed K-FNSPID Gold rows are replaced by deterministic PUBLIC_TRAIN "
            "refinement controls so every mode executes the same Stage 2 row/update budget."
        ),
    }


def _protocol_record(
    prepared: Any,
    gold_rows: list[dict[str, Any]],
    stage1: ComputeMatchedStage,
    stage2: ComputeMatchedStage,
    args: argparse.Namespace,
    input_records: dict[str, Any],
    recipe_records: dict[str, Any],
    base_source: Any,
    gold_provenance: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    source_distribution = dict(
        sorted(Counter(str(row.get("dataset", "")) for row in prepared.train_rows).items())
    )
    return {
        "status": "VALIDATED_WITHOUT_TRAINING" if args.validate_only else "READY_TO_TRAIN",
        "schema_version": SCHEMA_VERSION,
        "artifact_role": ARTIFACT_ROLE,
        "model_family": MODEL_FAMILY,
        "ablation_mode": prepared.mode.value,
        "fixed_model_seeds": list(MODEL_SEEDS),
        "seed": args.seed,
        "public_test_opened": False,
        "confirmatory_labels_opened": False,
        "prepared_partition_commitments": prepared.prepared_partition_commitments,
        "partition_count": {
            "TRAIN": len(prepared.train_rows),
            "STAGE1_EXPOSURES_PER_EPOCH": len(stage1.rows),
            "CHECKPOINT": len(prepared.checkpoint_rows),
            "CALIBRATION": len(prepared.calibration_rows),
            "SELECTION": len(prepared.selection_rows),
            "K_GOLD_REFINEMENT": len(gold_rows),
            "GOLD_REFINEMENT": len(stage2.rows),
        },
        "training_source_distribution": source_distribution,
        "training_label_distribution": v5._label_distribution(prepared.train_rows),
        "target_swap_count": len(prepared.target_swap_rows),
        "source_selection_provenance": data_contract._source_selection_provenance(prepared),
        "architecture": _architecture_contract(),
        "training_arguments": _training_arguments(args),
        "recipe_commitment_sha256": _recipe_commitment(args),
        "input_artifacts": input_records,
        "verified_gold_provenance": gold_provenance,
        "recipe_artifacts": recipe_records,
        "base_source_kind": base_source.kind,
        "base_source": base_source.provenance,
        "compute_matching": {
            "schema_version": "k-fnspid-compute-matched-training-plan/v1",
            "stage1": stage1.audit,
            "stage2": stage2.audit,
            "optimizer_step_contract": _optimizer_step_contract(args),
        },
        "estimand_contract": _estimand_contract(),
        "statistical_analysis_plan": _statistical_analysis_plan_contract(),
        "stage2_data_intervention": _stage2_intervention_contract(prepared, stage2),
        "partition_roles": {
            "SELECTION": v6.ADAPTIVE_SELECTION_ROLE,
            "CONFIRMATORY": "ONLY_INDEPENDENT_GENERALIZATION_EVIDENCE_AFTER_LOCK",
            "K_DEVELOPMENT": "SHARED_CONDITIONING_SET_NOT_TRAINING_INTERVENTION",
        },
        "final_holm_baseline_contract": {
            "no_k_role": FINAL_HOLM_NO_K_ROLE,
            "estimand_id": ESTIMAND_ID,
            "required_model_family": MODEL_FAMILY,
            "required_seed_runs": list(MODEL_SEEDS),
            "legacy_v5_no_k_role": LEGACY_V5_NO_K_ROLE,
            "legacy_v5_no_k_final_holm_eligible": False,
            "zero_k_exposure_holm_eligible": False,
        },
        "dapt_verifier_contract": v6.DAPT_VERIFIER_CONTRACT,
        "test": {"sample_count": 0, "status": "SEALED_AND_NOT_LOADED"},
    }


def _stage_record(result: Any) -> dict[str, Any]:
    return {
        "stage": result.stage,
        "best_epoch": result.best_epoch,
        "checkpoint_score": list(result.checkpoint_score),
        "checkpoint_metrics": result.checkpoint_metrics,
        "history": result.history,
        "optimizer_steps": result.optimizer_steps,
        "planned_optimizer_steps": result.planned_optimizer_steps,
        "best_optimizer_step": result.best_optimizer_step,
        "wall_seconds": result.wall_seconds,
        "objective_provenance": result.objective_provenance,
        "active_parameter_provenance": result.active_parameter_provenance,
    }


def _runtime_contract(
    base_source: Any,
    calibration: dict[str, Any],
    max_length: int,
) -> dict[str, Any]:
    return {
        "schema_version": v6.RUNTIME_LOADER_SCHEMA_VERSION,
        "base_source": base_source.provenance,
        "adapter_path": "adapter",
        "heads_path": v6.HEAD_ARTIFACT_FILENAME,
        "tokenizer_source": "artifact-root",
        "domain_order": list(v6.DOMAIN_ORDER),
        "domain_required": True,
        "unknown_domain_behavior": "FAIL_CLOSED",
        "pooling": "last_hidden_state_cls",
        "head_tensor_contract": v6.EXPECTED_HEAD_TENSOR_CONTRACT,
        "head_architecture": v6.EXPECTED_HEAD_ARCHITECTURE,
        "composition": {
            "NEGATIVE": "log_sigmoid(boundary)+log_softmax(direction)[0]",
            "NEUTRAL": "log_sigmoid(-boundary)",
            "POSITIVE": "log_sigmoid(boundary)+log_softmax(direction)[1]",
        },
        "calibration": calibration,
        "input_feature_version": "source-target-prefix-head-tail/v2",
        "max_length": max_length,
    }


def _validate_compute_matched_stage_results(
    mode: AblationMode,
    stage1: Any,
    stage2: Any,
) -> None:
    if (
        stage1.optimizer_steps != CANDIDATE_STAGE1_OPTIMIZER_STEPS
        or stage1.planned_optimizer_steps != CANDIDATE_STAGE1_OPTIMIZER_STEPS
        or stage2.optimizer_steps != CANDIDATE_STAGE2_OPTIMIZER_STEPS
        or stage2.planned_optimizer_steps != CANDIDATE_STAGE2_OPTIMIZER_STEPS
    ):
        raise RuntimeError("ablation optimizer step이 candidate 4114/452와 다릅니다.")
    expected_membership = {
        "NEWS_TARGETED": mode in {AblationMode.NEWS_ONLY, AblationMode.FULL},
        "DISCLOSURE_TARGETED": mode in {AblationMode.DISCLOSURE_ONLY, AblationMode.FULL},
    }
    for result in (stage1, stage2):
        provenance = result.active_parameter_provenance
        if provenance.get("residual_optimizer_membership") != expected_membership:
            raise RuntimeError("ablation residual optimizer membership이 mode와 다릅니다.")
        if not all(expected_membership.values()) and (
            provenance.get("inactive_residual_bitwise_preserved") is not True
            or provenance.get("inactive_residual_exact_zero_before") is not True
            or provenance.get("inactive_residual_exact_zero_after") is not True
            or provenance.get("inactive_residual_state_sha256_before")
            != provenance.get("inactive_residual_state_sha256_after")
        ):
            raise RuntimeError("제거 source residual의 exact-zero bitwise 보존이 실패했습니다.")


def train_ablation(
    prepared: Any,
    gold_rows: list[dict[str, Any]],
    stage1_plan: ComputeMatchedStage,
    stage2_plan: ComputeMatchedStage,
    args: argparse.Namespace,
    protocol: dict[str, Any],
    execution_snapshot: dict[str, Any],
    recipe_records: dict[str, Any],
    input_paths: dict[str, Path],
    output_dir: Path,
    report_path: Path,
) -> dict[str, Any]:
    if stage2_plan.audit.get("eligible_k_gold_row_count") != len(gold_rows):
        raise RuntimeError("Stage 2 plan과 K Gold 입력 commitment가 다릅니다.")
    base_source = v6.assert_execution_snapshot_unchanged(
        execution_snapshot,
        input_paths,
        args.base_source,
    )
    tokenizer = AutoTokenizer.from_pretrained(
        v5.BASE_MODEL,
        revision=v5.BASE_MODEL_REVISION,
        trust_remote_code=False,
    )
    model = cast(
        Any,
        v6.build_model(base_source, gradient_checkpointing=args.gradient_checkpointing),
    )
    device = v6._device(args.device)
    model.to(device)
    collator = v6.DomainCollator(tokenizer)
    datasets = {
        "TRAIN": v6.DomainEncodedDataset(stage1_plan.rows, tokenizer, args.max_length),
        "REFINEMENT": v6.DomainEncodedDataset(stage2_plan.rows, tokenizer, args.max_length),
        "CHECKPOINT": v6.DomainEncodedDataset(prepared.checkpoint_rows, tokenizer, args.max_length),
        "CALIBRATION": v6.DomainEncodedDataset(
            prepared.calibration_rows, tokenizer, args.max_length
        ),
        "SELECTION": v6.DomainEncodedDataset(prepared.selection_rows, tokenizer, args.max_length),
    }
    trainable_names = {
        name for name, parameter in model.named_parameters() if parameter.requires_grad
    }
    checkpoint_root = args.checkpoint_root or (
        output_dir.parent / f".{output_dir.name}-training-checkpoints"
    )
    if checkpoint_root.is_symlink():
        raise RuntimeError("ablation checkpoint root는 symlink일 수 없습니다.")
    checkpoint_context_sha256 = v6._stage_checkpoint_context_sha256(
        {
            "execution_material": execution_snapshot["material"],
            "protocol": protocol,
            "seed": args.seed,
            "max_length": args.max_length,
            "stage1_epochs": args.stage1_epochs,
            "stage2_epochs": args.stage2_epochs,
            "batch_size": args.batch_size,
            "eval_batch_size": args.eval_batch_size,
            "gradient_accumulation_steps": args.gradient_accumulation_steps,
            "stage1_learning_rate": args.stage1_learning_rate,
            "stage2_learning_rate": args.stage2_learning_rate,
            "weight_decay": args.weight_decay,
            "rdrop_alpha": args.rdrop_alpha,
            "gradient_checkpointing": bool(args.gradient_checkpointing),
        }
    )
    audit = v6.TrainingInterruptionAudit()
    audit.install()
    stage1 = v6.train_stage(
        model,
        datasets["TRAIN"],
        datasets["CHECKPOINT"],
        collator,
        stage="STAGE1_COMPUTE_MATCHED_EXPOSURE",
        epochs=args.stage1_epochs,
        learning_rate=args.stage1_learning_rate,
        weight_decay=args.weight_decay,
        batch_size=args.batch_size,
        eval_batch_size=args.eval_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        rdrop_alpha=args.rdrop_alpha,
        seed=args.seed,
        device=device,
        state_names=trainable_names,
        interruption_audit=audit,
        checkpoint_directory=checkpoint_root / "stage1",
        checkpoint_context_sha256=checkpoint_context_sha256,
    )
    selected_stage = stage1
    for parameter in model.encoder.parameters():
        parameter.requires_grad = False
    stage2_names = {name for name, parameter in model.named_parameters() if parameter.requires_grad}
    stage2 = v6.train_stage(
        model,
        datasets["REFINEMENT"],
        datasets["CHECKPOINT"],
        collator,
        stage="STAGE2_COMPUTE_MATCHED_REFINEMENT",
        epochs=args.stage2_epochs,
        learning_rate=args.stage2_learning_rate,
        weight_decay=args.weight_decay,
        batch_size=args.batch_size,
        eval_batch_size=args.eval_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        rdrop_alpha=args.rdrop_alpha,
        seed=args.seed + 1_003,
        device=device,
        state_names=stage2_names,
        interruption_audit=audit,
        checkpoint_directory=checkpoint_root / "stage2",
        checkpoint_context_sha256=checkpoint_context_sha256,
    )
    _validate_compute_matched_stage_results(prepared.mode, stage1, stage2)
    selected_stage = stage2
    if stage1.checkpoint_score >= stage2.checkpoint_score:
        v6._restore_state(model, stage1.state)
        selected_stage = stage1

    calibration_logits, calibration_labels, calibration_domains = v6.predict(
        model,
        datasets["CALIBRATION"],
        collator,
        batch_size=args.eval_batch_size,
        device=device,
    )
    calibration = v6.fit_calibration(
        calibration_logits,
        calibration_labels,
        calibration_domains,
    )
    calibration_predictions = v6.calibrated_predictions(
        calibration_logits,
        calibration_domains,
        calibration,
    )
    calibration_metrics = v6.metrics_by_domain(
        calibration_labels,
        calibration_predictions,
        calibration_domains,
    )
    selection_logits, selection_labels, selection_domains = v6.predict(
        model,
        datasets["SELECTION"],
        collator,
        batch_size=args.eval_batch_size,
        device=device,
    )
    selection_predictions = v6.calibrated_predictions(
        selection_logits,
        selection_domains,
        calibration,
    )
    selection_metrics = v6.metrics_by_domain(
        selection_labels,
        selection_predictions,
        selection_domains,
    )
    weakest, overall = v6.weakest_source_score(selection_metrics)
    audit.mark_progress()
    audit.close()
    interruption_provenance = audit.report()

    final_base = v6.assert_execution_snapshot_unchanged(
        execution_snapshot,
        input_paths,
        args.base_source,
    )
    _assert_records_unchanged(recipe_records, _recipe_paths())
    if final_base.provenance != base_source.provenance:
        raise RuntimeError("ablation 저장 직전 base-source가 변경되었습니다.")
    version = (
        "hana-montana-kf-deberta-k-fnspid-sentiment-v6-ablation-"
        f"{_mode_slug(prepared.mode)}-seed{args.seed}-"
        f"{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    )
    runtime = _runtime_contract(base_source, calibration, args.max_length)
    metadata = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "artifact_role": ARTIFACT_ROLE,
        "model_family": MODEL_FAMILY,
        "version": version,
        "ablation_mode": prepared.mode.value,
        "seed": args.seed,
        "base_model": v5.BASE_MODEL,
        "base_model_revision": v5.BASE_MODEL_REVISION,
        "base_source_kind": base_source.kind,
        "label_order": list(v6.LABEL_ORDER),
        "runtime_loader_contract": runtime,
        "prepared_partition_commitments": prepared.prepared_partition_commitments,
        "compute_matching": protocol["compute_matching"],
        "estimand_contract": protocol["estimand_contract"],
        "statistical_analysis_plan": protocol["statistical_analysis_plan"],
        "selected_stage": selected_stage.stage,
        "stage2_status": STAGE2_TRAINED,
        "trained_at": datetime.now(UTC).isoformat(),
    }
    model.to(torch.device("cpu"))
    artifact_files = v6.save_artifact(model, tokenizer, output_dir, metadata)
    try:
        production_cpu_roundtrip = v6.verify_production_cpu_roundtrip(
            model=model,
            tokenizer=tokenizer,
            artifact_dir=output_dir,
            base_source=base_source,
            calibration=calibration,
            canary_rows=prepared.selection_rows,
            max_length=args.max_length,
            validate_deployable_artifact=False,
        )
    except Exception:
        # 현재 실행이 생성한 parity 실패 연구 후보도 즉시 폐기한다.
        shutil.rmtree(output_dir)
        raise
    selected_global_step = stage1.best_optimizer_step
    executed_steps = stage1.optimizer_steps + stage2.optimizer_steps
    if selected_stage is stage2:
        selected_global_step += stage2.best_optimizer_step
    report = {
        **protocol,
        **metadata,
        "schema_version": SCHEMA_VERSION,
        "status": "TRAINING_COMPLETE_RESEARCH_ONLY",
        "artifact_directory": _display_path(output_dir),
        "artifact_files": artifact_files,
        "execution_snapshot": execution_snapshot,
        "training_environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "torch": torch.__version__,
            "numpy": np.__version__,
            "device": str(device),
            "bitwise_deterministic_guaranteed": False,
        },
        "restart_safe_stage_checkpointing": {
            "schema_version": v6.STAGE_CHECKPOINT_SCHEMA_VERSION,
            "checkpoint_root": str(checkpoint_root),
            "context_sha256": checkpoint_context_sha256,
            "interval": "END_OF_EPOCH",
            "atomic_directory_publish": True,
            "safe_tensor_serialization_only": True,
            "automatic_latest_resume": True,
        },
        "stages": {
            "stage1": _stage_record(stage1),
            "stage2": _stage_record(stage2),
            "executed_optimizer_steps_total": executed_steps,
            "planned_optimizer_steps_total": (
                stage1.planned_optimizer_steps + stage2.planned_optimizer_steps
            ),
            "fixed_full_epoch_budget": True,
            "selected_checkpoint_lineage_global_step": selected_global_step,
        },
        "calibration": {
            "fit_partition": "CALIBRATION_ONLY",
            "parameters": calibration,
            "metrics": calibration_metrics,
            "adaptive_selection_used_for_fit": False,
        },
        "candidate_selection": {
            "fit_partition": v6.ADAPTIVE_SELECTION_ROLE,
            "legacy_commitment_partition_name": "SELECTION",
            "weakest_source_domain_macro_f1": weakest,
            "overall_macro_f1": overall,
            "metrics": selection_metrics,
            "independent_generalization_evidence": False,
            "confirmatory_is_only_independent_generalization_evidence": True,
        },
        "selection_score": {
            "weakest_source_domain_macro_f1": weakest,
            "overall_macro_f1": overall,
        },
        "interruption_provenance": interruption_provenance,
        "production_cpu_roundtrip": production_cpu_roundtrip,
        "public_test_opened": False,
        "confirmatory_labels_opened": False,
        "test": {"sample_count": 0, "status": "SEALED_AND_NOT_LOADED"},
    }
    _write_json_exclusive_atomic(report_path, report)
    return report


def _display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return str(resolved)


def _regular_file_record(path: Path) -> dict[str, int | str]:
    """집계 manifest의 프로젝트 내부 파일 경로를 이식 가능한 상대경로로 기록한다."""
    record = v6._regular_file_record(path)
    record["path"] = _display_path(path)
    return record


def _read_json_object(path: Path, label: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise RuntimeError(f"{label}은 symlink가 아닌 일반 JSON 파일이어야 합니다.")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} JSON object 계약이 다릅니다.")
    return value


def _verified_artifact_manifest(directory: Path) -> dict[str, dict[str, int | str]]:
    if directory.is_symlink() or not directory.is_dir():
        raise RuntimeError("ablation artifact directory 계약이 다릅니다.")
    manifest_path = directory / "manifest.json"
    manifest = _read_json_object(manifest_path, "artifact manifest")
    records = manifest.get("artifact_files")
    if (
        manifest.get("schema_version") != v6.ARTIFACT_MANIFEST_SCHEMA_VERSION
        or manifest.get("status") != "ATOMIC_COMPLETE"
        or manifest.get("safe_serialization_only") is not True
        or manifest.get("symlinks_allowed") is not False
        or manifest.get("overwrite_allowed") is not False
        or not isinstance(records, dict)
    ):
        raise RuntimeError("ablation artifact manifest 계약이 다릅니다.")
    actual_files: set[str] = set()
    for path in directory.rglob("*"):
        if path.is_symlink():
            raise RuntimeError("ablation artifact에 symlink가 있습니다.")
        if path.is_file():
            actual_files.add(path.relative_to(directory).as_posix())
    if actual_files != {*records, "manifest.json"}:
        raise RuntimeError("ablation artifact 파일 목록이 manifest와 다릅니다.")
    for relative, record in records.items():
        path = directory / relative
        if (
            not isinstance(relative, str)
            or not isinstance(record, dict)
            or path.is_symlink()
            or not path.is_file()
            or record.get("bytes") != path.stat().st_size
            or record.get("sha256") != v6._sha256_file(path)
        ):
            raise RuntimeError(f"ablation artifact hash가 다릅니다: {relative}")
    return cast(dict[str, dict[str, int | str]], records)


def _candidate_architecture_contract() -> dict[str, Any]:
    return {
        "encoder": "shared-kf-deberta",
        "lora_layers": list(v6.LORA_LAYERS),
        "lora_target_modules": list(v6.LORA_TARGET_MODULES),
        "lora_rank": v6.LORA_RANK,
        "lora_alpha": v6.LORA_ALPHA,
        "head_architecture": v6.EXPECTED_HEAD_ARCHITECTURE,
        "source_domains": list(v6.DOMAIN_ORDER),
        "head_outputs": ["neutral_vs_directional", "negative_vs_positive"],
        "three_class_composition": "normalized-hierarchical-log-probabilities/v1",
        "loss": v6.LOSS_CONTRACT_VERSION,
        "checkpoint_primary": "weakest-source-domain-macro-f1",
        "calibration": "calibration-only-sequential-temperature-neutral-threshold-shrunk/v1",
        "adaptive_development_selection_primary": "weakest-source-domain-macro-f1",
    }


def _candidate_training_arguments(report: dict[str, Any]) -> dict[str, Any]:
    arguments = report.get("training_arguments")
    if not isinstance(arguments, dict):
        raise RuntimeError("FULL 후보 training arguments가 없습니다.")
    normalized = dict(arguments)
    normalized["model_seed"] = normalized.pop("seed", None)
    normalized["max_length"] = report.get("max_length")
    return normalized


def _candidate_input_artifacts(report: dict[str, Any]) -> dict[str, Any]:
    records = report.get("input_artifacts")
    if not isinstance(records, dict):
        raise RuntimeError("FULL 후보 input artifact 기록이 없습니다.")
    normalized = dict(records)
    train_gold = normalized.pop("train_gold", None)
    if train_gold is None or "main_news_gold" in normalized:
        raise RuntimeError("FULL 후보 Gold 입력 별칭 계약이 다릅니다.")
    normalized["main_news_gold"] = train_gold
    return normalized


def _candidate_stages(report: dict[str, Any]) -> dict[str, Any]:
    selection = report.get("stage_selection")
    if not isinstance(selection, dict):
        raise RuntimeError("FULL 후보 stage selection이 없습니다.")
    stage1 = selection.get("stage1")
    stage2 = selection.get("stage2")
    if not isinstance(stage1, dict) or not isinstance(stage2, dict):
        raise RuntimeError("FULL 후보 stage 기록이 없습니다.")
    stages = {
        "stage1": dict(stage1),
        "stage2": dict(stage2),
        "executed_optimizer_steps_total": selection.get("executed_optimizer_steps_total"),
        "planned_optimizer_steps_total": selection.get("planned_optimizer_steps_total"),
        "fixed_full_epoch_budget": selection.get("fixed_full_epoch_budget"),
        "selected_checkpoint_lineage_global_step": selection.get(
            "selected_checkpoint_lineage_global_step"
        ),
    }
    return stages


def _full_candidate_identity_projection(
    report: dict[str, Any],
    records: dict[str, dict[str, int | str]],
) -> dict[str, Any]:
    return {
        "schema_version": report.get("schema_version"),
        "model_family": report.get("model_family"),
        "seed": report.get("seed"),
        "selected_stage": report.get("selected_stage"),
        "training_arguments": report.get("training_arguments"),
        "architecture": report.get("architecture"),
        "prepared_partition_commitments": report.get("prepared_partition_commitments"),
        "input_artifacts": report.get("input_artifacts"),
        "training_code": report.get("training_code"),
        "dependency_artifacts": report.get("dependency_artifacts"),
        "base_source_kind": report.get("base_source_kind"),
        "base_source": report.get("base_source"),
        "stage_selection": report.get("stage_selection"),
        "calibration": report.get("calibration"),
        "candidate_selection": report.get("candidate_selection"),
        "production_cpu_roundtrip": report.get("production_cpu_roundtrip"),
        "artifact_files": records,
    }


def _validate_full_candidate_source(
    report: dict[str, Any],
    *,
    seed: int,
    artifact_dir: Path,
    comparison_contract: dict[str, Any],
) -> tuple[dict[str, dict[str, int | str]], dict[str, Any]]:
    selection = report.get("candidate_selection")
    roundtrip = report.get("production_cpu_roundtrip")
    stages = _candidate_stages(report)
    if (
        report.get("schema_version") != v6.TRAINING_SCHEMA_VERSION
        or report.get("model_family") != MODEL_FAMILY
        or report.get("seed") != seed
        or report.get("architecture") != _candidate_architecture_contract()
        or report.get("prepared_partition_commitments")
        != comparison_contract.get("prepared_partition_commitments")
        or _candidate_input_artifacts(report) != comparison_contract.get("input_artifacts")
        or report.get("base_source_kind") != comparison_contract.get("base_source_kind")
        or report.get("base_source") != comparison_contract.get("base_source")
        or _candidate_training_arguments(report)
        != comparison_contract.get("training_arguments")
        or report.get("public_test_opened") is not False
        or report.get("confirmatory_labels_opened") is not False
        or report.get("test", {}).get("sample_count") != 0
        or not isinstance(selection, dict)
        or selection.get("fit_partition") != v6.ADAPTIVE_SELECTION_ROLE
        or selection.get("independent_generalization_evidence") is not False
        or selection.get("confirmatory_is_only_independent_generalization_evidence") is not True
        or not isinstance(roundtrip, dict)
        or roundtrip.get("status") != "PASS"
        or roundtrip.get("device") != "cpu"
        or roundtrip.get("logits_max_abs_error") != 0.0
        or roundtrip.get("probability_max_abs_error") != 0.0
        or roundtrip.get("exact_final_threshold_label_agreement") is not True
    ):
        raise RuntimeError("FULL 후보의 데이터·모델·평가 계약이 다릅니다.")
    if report.get("selected_stage") not in {
        "STAGE1_DOMAIN_BALANCED_FULL",
        "STAGE2_GOLD_CLEAN_HEADS_ONLY",
    }:
        raise RuntimeError("FULL 후보 selected stage 계약이 다릅니다.")
    synthetic = {
        "stages": stages,
        "training_arguments": comparison_contract["training_arguments"],
    }
    _validate_fixed_stage_budget(synthetic, AblationMode.FULL)
    records = _verified_artifact_manifest(artifact_dir)
    if report.get("artifact_files") != records:
        raise RuntimeError("FULL 후보 report와 artifact manifest가 일치하지 않습니다.")
    metadata = _read_json_object(artifact_dir / "hannah_metadata.json", "FULL 후보 metadata")
    if (
        metadata.get("schema_version") != v6.ARTIFACT_SCHEMA_VERSION
        or metadata.get("base_source_kind") != report.get("base_source_kind")
        or metadata.get("prepared_partition_commitments")
        != report.get("prepared_partition_commitments")
        or metadata.get("selected_stage") != report.get("selected_stage")
        or metadata.get("runtime_loader_contract") != report.get("runtime_loader_contract")
    ):
        raise RuntimeError("FULL 후보 artifact metadata 계약이 다릅니다.")
    return records, stages


def _path_from_record(record: Any, label: str) -> Path:
    if not isinstance(record, dict) or not isinstance(record.get("path"), str):
        raise RuntimeError(f"{label} 경로 계약이 다릅니다.")
    path = Path(record["path"])
    return path if path.is_absolute() else PROJECT_ROOT / path


def _full_reuse_contract(
    *,
    source_report_path: Path,
    source_artifact_dir: Path,
    source_report: dict[str, Any],
    records: dict[str, dict[str, int | str]],
    seed: int,
) -> dict[str, Any]:
    identity = _full_candidate_identity_projection(source_report, records)
    return {
        "schema_version": FULL_REUSE_SCHEMA_VERSION,
        "status": FULL_REUSE_STATUS,
        "ablation_mode": AblationMode.FULL.value,
        "seed": seed,
        "source_candidate_report": v6._regular_file_record(source_report_path),
        "source_candidate_artifact_directory": _display_path(source_artifact_dir),
        "source_candidate_manifest": v6._regular_file_record(
            source_artifact_dir / "manifest.json"
        ),
        "source_candidate_artifact_files": records,
        "source_candidate_identity_sha256": _canonical_sha256(identity),
        "reuse_semantics": "LOCKED_FULL_ARM_EXACT_ARTIFACT_REFERENCE_NO_COPY_NO_RETRAIN",
        "artifact_bytes_reused_without_copy": sum(
            int(record["bytes"]) for record in records.values()
        ),
        "training_compute_avoided": True,
        "comparison_contract": {
            "same_model_family": True,
            "same_seed": True,
            "same_data_partition_commitments": True,
            "same_input_artifact_hashes": True,
            "same_base_source_hashes": True,
            "same_architecture_and_hyperparameters": True,
            "same_stage_optimizer_step_budget": True,
            "source_artifact_manifest_sha256_verified": True,
            "candidate_native_minibatch_sequence_retained": True,
            "stable_order_plan_reexecuted": False,
        },
    }


def build_full_reuse_receipt(
    *,
    protocol: dict[str, Any],
    source_report_path: Path,
    source_artifact_dir: Path,
    report_path: Path,
    seed: int,
) -> dict[str, Any]:
    source_report = _read_json_object(source_report_path, "FULL 후보 report")
    records, stages = _validate_full_candidate_source(
        source_report,
        seed=seed,
        artifact_dir=source_artifact_dir,
        comparison_contract=protocol,
    )
    reuse = _full_reuse_contract(
        source_report_path=source_report_path,
        source_artifact_dir=source_artifact_dir,
        source_report=source_report,
        records=records,
        seed=seed,
    )
    source_selection = cast(dict[str, Any], source_report["candidate_selection"])
    compute_matching = dict(cast(dict[str, Any], protocol["compute_matching"]))
    compute_matching["full_reference_execution"] = {
        "status": FULL_REUSE_STATUS,
        "candidate_native_minibatch_sequence_retained": True,
        "stable_order_plan_reexecuted": False,
        "interpretation": (
            "행 집합·노출 수·optimizer step은 동일하며 FULL은 고정 후보의 실제 순서를 유지한다."
        ),
    }
    receipt = {
        **protocol,
        "schema_version": SCHEMA_VERSION,
        "status": FULL_REUSE_STATUS,
        "artifact_directory": _display_path(source_artifact_dir),
        "artifact_files": records,
        "artifact_reuse": reuse,
        "compute_matching": compute_matching,
        "selected_stage": source_report["selected_stage"],
        "stages": stages,
        "calibration": source_report["calibration"],
        "candidate_selection": {
            "fit_partition": v6.ADAPTIVE_SELECTION_ROLE,
            "legacy_commitment_partition_name": "SELECTION",
            "weakest_source_domain_macro_f1": source_selection["primary_value"],
            "overall_macro_f1": source_selection["secondary_overall_macro_f1"],
            "metrics": source_selection["metrics"],
            "independent_generalization_evidence": False,
            "confirmatory_is_only_independent_generalization_evidence": True,
        },
        "selection_score": {
            "weakest_source_domain_macro_f1": source_selection["primary_value"],
            "overall_macro_f1": source_selection["secondary_overall_macro_f1"],
        },
        "production_cpu_roundtrip": source_report["production_cpu_roundtrip"],
    }
    _write_json_exclusive_atomic(report_path, receipt)
    return receipt


def _validate_candidate_report(
    report: dict[str, Any],
    *,
    mode: AblationMode,
    seed: int,
    artifact_dir: Path,
) -> tuple[float, float]:
    if "artifact_reuse" in report:
        return _validate_full_reuse_receipt(report, mode=mode, seed=seed)
    test = report.get("test")
    selection = report.get("candidate_selection")
    stage2 = report.get("stage2_data_intervention")
    score = report.get("selection_score")
    holm_contract = report.get("final_holm_baseline_contract")
    estimand = report.get("estimand_contract")
    if (
        report.get("schema_version") != SCHEMA_VERSION
        or report.get("status") != "TRAINING_COMPLETE_RESEARCH_ONLY"
        or report.get("artifact_role") != ARTIFACT_ROLE
        or report.get("model_family") != MODEL_FAMILY
        or report.get("ablation_mode") != mode.value
        or report.get("seed") != seed
        or report.get("public_test_opened") is not False
        or report.get("confirmatory_labels_opened") is not False
        or not isinstance(test, dict)
        or test.get("sample_count") != 0
        or not isinstance(selection, dict)
        or selection.get("fit_partition") != v6.ADAPTIVE_SELECTION_ROLE
        or selection.get("independent_generalization_evidence") is not False
        or selection.get("confirmatory_is_only_independent_generalization_evidence") is not True
        or not isinstance(stage2, dict)
        or not isinstance(score, dict)
        or holm_contract
        != {
            "no_k_role": FINAL_HOLM_NO_K_ROLE,
            "estimand_id": ESTIMAND_ID,
            "required_model_family": MODEL_FAMILY,
            "required_seed_runs": list(MODEL_SEEDS),
            "legacy_v5_no_k_role": LEGACY_V5_NO_K_ROLE,
            "legacy_v5_no_k_final_holm_eligible": False,
            "zero_k_exposure_holm_eligible": False,
        }
        or estimand != _estimand_contract()
        or report.get("statistical_analysis_plan") != _statistical_analysis_plan_contract()
        or report.get("artifact_directory") != _display_path(artifact_dir)
    ):
        raise RuntimeError(f"{mode.value} seed{seed} report 계약이 다릅니다.")
    if (
        stage2.get("status") != STAGE2_TRAINED
        or stage2.get("stage2_skipped") is not False
        or stage2.get("total_refinement_rows") != CANDIDATE_STAGE2_REFINEMENT_ROWS
        or stage2.get("candidate_optimizer_steps_matched") is not True
    ):
        raise RuntimeError(f"{mode.value} Stage 2 데이터 개입 계약이 다릅니다.")
    _validate_compute_matching_report(report, mode)
    _validate_fixed_stage_budget(report, mode)
    weakest = score.get("weakest_source_domain_macro_f1")
    overall = score.get("overall_macro_f1")
    if (
        isinstance(weakest, bool)
        or not isinstance(weakest, (int, float))
        or not 0.0 <= float(weakest) <= 1.0
        or isinstance(overall, bool)
        or not isinstance(overall, (int, float))
        or not 0.0 <= float(overall) <= 1.0
    ):
        raise RuntimeError("ablation selection score 계약이 다릅니다.")
    records = _verified_artifact_manifest(artifact_dir)
    if report.get("artifact_files") != records:
        raise RuntimeError("ablation report와 artifact manifest가 일치하지 않습니다.")
    metadata = _read_json_object(artifact_dir / "hannah_metadata.json", "artifact metadata")
    if (
        metadata.get("schema_version") != ARTIFACT_SCHEMA_VERSION
        or metadata.get("artifact_role") != ARTIFACT_ROLE
        or metadata.get("model_family") != MODEL_FAMILY
        or metadata.get("ablation_mode") != mode.value
        or metadata.get("seed") != seed
        or metadata.get("compute_matching") != report.get("compute_matching")
        or metadata.get("estimand_contract") != _estimand_contract()
        or metadata.get("statistical_analysis_plan") != _statistical_analysis_plan_contract()
    ):
        raise RuntimeError("ablation artifact metadata 계약이 다릅니다.")
    return float(weakest), float(overall)


def _validate_full_reuse_receipt(
    report: dict[str, Any],
    *,
    mode: AblationMode,
    seed: int,
) -> tuple[float, float]:
    reuse = report.get("artifact_reuse")
    selection = report.get("candidate_selection")
    score = report.get("selection_score")
    stage2 = report.get("stage2_data_intervention")
    if (
        mode is not AblationMode.FULL
        or not isinstance(reuse, dict)
        or reuse.get("schema_version") != FULL_REUSE_SCHEMA_VERSION
        or reuse.get("status") != FULL_REUSE_STATUS
        or report.get("schema_version") != SCHEMA_VERSION
        or report.get("status") != FULL_REUSE_STATUS
        or report.get("artifact_role") != ARTIFACT_ROLE
        or report.get("model_family") != MODEL_FAMILY
        or report.get("ablation_mode") != AblationMode.FULL.value
        or report.get("seed") != seed
        or report.get("public_test_opened") is not False
        or report.get("confirmatory_labels_opened") is not False
        or report.get("test", {}).get("sample_count") != 0
        or not isinstance(selection, dict)
        or selection.get("fit_partition") != v6.ADAPTIVE_SELECTION_ROLE
        or selection.get("independent_generalization_evidence") is not False
        or selection.get("confirmatory_is_only_independent_generalization_evidence") is not True
        or not isinstance(stage2, dict)
        or stage2.get("status") != STAGE2_TRAINED
        or stage2.get("stage2_skipped") is not False
        or stage2.get("total_refinement_rows") != CANDIDATE_STAGE2_REFINEMENT_ROWS
        or stage2.get("candidate_optimizer_steps_matched") is not True
        or report.get("estimand_contract") != _estimand_contract()
        or report.get("statistical_analysis_plan") != _statistical_analysis_plan_contract()
    ):
        raise RuntimeError(f"FULL seed{seed} artifact 재사용 영수증 계약이 다릅니다.")
    source_report_path = _path_from_record(reuse.get("source_candidate_report"), "FULL 후보 report")
    if reuse.get("source_candidate_report") != v6._regular_file_record(source_report_path):
        raise RuntimeError("FULL 후보 report hash가 재사용 영수증과 다릅니다.")
    source_artifact_value = reuse.get("source_candidate_artifact_directory")
    if not isinstance(source_artifact_value, str):
        raise RuntimeError("FULL 후보 artifact 경로 계약이 다릅니다.")
    source_artifact_dir = Path(source_artifact_value)
    if not source_artifact_dir.is_absolute():
        source_artifact_dir = PROJECT_ROOT / source_artifact_dir
    source_report = _read_json_object(source_report_path, "FULL 후보 report")
    records, _ = _validate_full_candidate_source(
        source_report,
        seed=seed,
        artifact_dir=source_artifact_dir,
        comparison_contract=report,
    )
    expected_reuse = _full_reuse_contract(
        source_report_path=source_report_path,
        source_artifact_dir=source_artifact_dir,
        source_report=source_report,
        records=records,
        seed=seed,
    )
    if reuse != expected_reuse:
        raise RuntimeError("FULL 후보 artifact 재사용 hash 계약이 다릅니다.")
    if (
        report.get("artifact_directory") != _display_path(source_artifact_dir)
        or report.get("artifact_files") != records
    ):
        raise RuntimeError("FULL 재사용 report와 원본 artifact가 일치하지 않습니다.")
    _validate_compute_matching_report(report, AblationMode.FULL)
    _validate_fixed_stage_budget(report, AblationMode.FULL)
    if not isinstance(score, dict):
        raise RuntimeError("FULL 재사용 selection score가 없습니다.")
    weakest = score.get("weakest_source_domain_macro_f1")
    overall = score.get("overall_macro_f1")
    if (
        isinstance(weakest, bool)
        or not isinstance(weakest, (int, float))
        or not 0.0 <= float(weakest) <= 1.0
        or isinstance(overall, bool)
        or not isinstance(overall, (int, float))
        or not 0.0 <= float(overall) <= 1.0
    ):
        raise RuntimeError("FULL 재사용 selection score 계약이 다릅니다.")
    source_selection = cast(dict[str, Any], source_report["candidate_selection"])
    if (
        float(weakest) != float(source_selection.get("primary_value"))
        or float(overall) != float(source_selection.get("secondary_overall_macro_f1"))
    ):
        raise RuntimeError("FULL 재사용 score가 후보 report와 다릅니다.")
    return float(weakest), float(overall)


def _effective_artifact_directory(report: dict[str, Any], fallback: Path) -> Path:
    if "artifact_reuse" not in report:
        return fallback
    value = cast(dict[str, Any], report["artifact_reuse"]).get(
        "source_candidate_artifact_directory"
    )
    if not isinstance(value, str):
        raise RuntimeError("재사용 artifact 경로가 없습니다.")
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def _validate_compute_matching_report(report: dict[str, Any], mode: AblationMode) -> None:
    compute_matching = report.get("compute_matching")
    if not isinstance(compute_matching, dict):
        raise RuntimeError("compute-matching provenance가 없습니다.")
    stage1 = compute_matching.get("stage1")
    stage2 = compute_matching.get("stage2")
    step_contract = compute_matching.get("optimizer_step_contract")
    expected_unique = {
        AblationMode.NO_K: 7_413,
        AblationMode.NEWS_ONLY: 28_107,
        AblationMode.DISCLOSURE_ONLY: 12_213,
        AblationMode.FULL: 32_907,
    }[mode]
    expected_min = CANDIDATE_STAGE1_ROW_EXPOSURES // expected_unique
    expected_max = math.ceil(CANDIDATE_STAGE1_ROW_EXPOSURES / expected_unique)
    expected_control = PUBLIC_CONTROL_PER_LABEL[mode] * len(v6.LABEL_ORDER)
    if (
        not isinstance(stage1, dict)
        or not isinstance(stage2, dict)
        or not isinstance(step_contract, dict)
        or stage1.get("source_unique_row_count") != expected_unique
        or stage1.get("target_exposure_count_per_epoch") != CANDIDATE_STAGE1_ROW_EXPOSURES
        or stage1.get("minimum_exposures_per_unique_row") != expected_min
        or stage1.get("maximum_exposures_per_unique_row") != expected_max
        or stage1.get("all_source_rows_exposed") is not True
        or stage2.get("row_count") != CANDIDATE_STAGE2_REFINEMENT_ROWS
        or stage2.get("eligible_k_gold_row_count") != EXPECTED_K_GOLD_ROWS[mode]
        or stage2.get("public_control_row_count") != expected_control
        or stage2.get("no_k_training_exposure") != (mode is AblationMode.NO_K)
        or step_contract.get("candidate_steps_exactly_matched") is not True
        or step_contract.get("stage1", {}).get("optimizer_steps")
        != CANDIDATE_STAGE1_OPTIMIZER_STEPS
        or step_contract.get("stage2", {}).get("optimizer_steps")
        != CANDIDATE_STAGE2_OPTIMIZER_STEPS
    ):
        raise RuntimeError("compute-matched 행·노출·step 계약이 다릅니다.")


def _validate_fixed_stage_budget(report: dict[str, Any], mode: AblationMode) -> None:
    stages = report.get("stages")
    arguments = report.get("training_arguments")
    if not isinstance(stages, dict) or not isinstance(arguments, dict):
        raise RuntimeError("ablation 고정 update budget 계약이 없습니다.")
    stage1 = stages.get("stage1")
    stage2 = stages.get("stage2")
    if not isinstance(stage1, dict) or not isinstance(stage2, dict):
        raise RuntimeError("ablation stage update budget 계약이 없습니다.")

    def stage_budget(stage: dict[str, Any], epochs: int, expected: int) -> int:
        executed = stage.get("optimizer_steps")
        planned = stage.get("planned_optimizer_steps")
        history = stage.get("history")
        if (
            isinstance(executed, bool)
            or not isinstance(executed, int)
            or isinstance(planned, bool)
            or not isinstance(planned, int)
            or executed != expected
            or planned != expected
            or not isinstance(history, list)
            or len(history) != epochs
        ):
            raise RuntimeError("ablation stage planned/executed update budget이 다릅니다.")
        return executed

    stage1_steps = stage_budget(
        stage1,
        int(arguments.get("stage1_epochs", 0)),
        CANDIDATE_STAGE1_OPTIMIZER_STEPS,
    )
    stage2_steps = stage_budget(
        stage2,
        int(arguments.get("stage2_epochs", 0)),
        CANDIDATE_STAGE2_OPTIMIZER_STEPS,
    )
    if (
        arguments.get("stage1_epochs") != CANDIDATE_STAGE1_EPOCHS
        or arguments.get("stage2_epochs") != CANDIDATE_STAGE2_EPOCHS
        or arguments.get("batch_size") != CANDIDATE_BATCH_SIZE
        or arguments.get("gradient_accumulation_steps") != CANDIDATE_GRADIENT_ACCUMULATION_STEPS
        or stages.get("fixed_full_epoch_budget") is not True
        or stages.get("executed_optimizer_steps_total") != stage1_steps + stage2_steps
        or stages.get("planned_optimizer_steps_total") != stage1_steps + stage2_steps
    ):
        raise RuntimeError("ablation 고정 full-epoch update 총계가 다릅니다.")

    expected_membership = {
        "NEWS_TARGETED": mode in {AblationMode.NEWS_ONLY, AblationMode.FULL},
        "DISCLOSURE_TARGETED": mode in {AblationMode.DISCLOSURE_ONLY, AblationMode.FULL},
    }
    for stage in (stage1, stage2):
        provenance = stage.get("active_parameter_provenance")
        if (
            not isinstance(provenance, dict)
            or provenance.get("residual_optimizer_membership") != expected_membership
        ):
            raise RuntimeError("ablation residual optimizer report가 mode와 다릅니다.")
        if not all(expected_membership.values()) and (
            provenance.get("inactive_residual_bitwise_preserved") is not True
            or provenance.get("inactive_residual_exact_zero_before") is not True
            or provenance.get("inactive_residual_exact_zero_after") is not True
            or provenance.get("inactive_residual_state_sha256_before")
            != provenance.get("inactive_residual_state_sha256_after")
        ):
            raise RuntimeError("ablation residual exact-zero report가 없습니다.")


def _cross_seed_projection(report: dict[str, Any]) -> dict[str, Any]:
    arguments = dict(cast(dict[str, Any], report["training_arguments"]))
    arguments.pop("model_seed", None)
    return {
        "prepared_partition_commitments": report.get("prepared_partition_commitments"),
        "input_artifacts": report.get("input_artifacts"),
        "architecture": report.get("architecture"),
        "training_arguments": arguments,
        "recipe_commitment_sha256": report.get("recipe_commitment_sha256"),
        "base_source_kind": report.get("base_source_kind"),
        "base_source": report.get("base_source"),
        "compute_matching": report.get("compute_matching"),
        "estimand_contract": report.get("estimand_contract"),
        "statistical_analysis_plan": report.get("statistical_analysis_plan"),
        "stage2_data_intervention": report.get("stage2_data_intervention"),
    }


def _write_json_exclusive_atomic(path: Path, value: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise RuntimeError(f"출력이 이미 존재합니다: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.parent / f".{path.name}.tmp-{uuid.uuid4().hex}"
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as file:
            file.write(payload)
            file.flush()
            os.fsync(file.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def aggregate_mode_runs(
    *,
    mode: AblationMode,
    report_dir: Path,
    artifact_root: Path,
    selection_report_path: Path,
    winner_manifest_path: Path,
    validate_only: bool,
) -> dict[str, Any]:
    slug = _mode_slug(mode)
    reports: dict[int, dict[str, Any]] = {}
    scores: dict[int, tuple[float, float]] = {}
    report_paths: dict[int, Path] = {}
    for seed in MODEL_SEEDS:
        report_path = report_dir / f"kf-deberta-sentiment-v6-{slug}-seed{seed}.json"
        artifact_dir = artifact_root / f"seed{seed}"
        report = _read_json_object(report_path, f"{mode.value} seed{seed} report")
        scores[seed] = _validate_candidate_report(
            report,
            mode=mode,
            seed=seed,
            artifact_dir=artifact_dir,
        )
        reports[seed] = report
        report_paths[seed] = report_path
    baseline = _cross_seed_projection(reports[MODEL_SEEDS[0]])
    if any(_cross_seed_projection(reports[seed]) != baseline for seed in MODEL_SEEDS[1:]):
        raise RuntimeError("3개 seed의 data·recipe·base commitment가 다릅니다.")
    selected_seed = sorted(
        MODEL_SEEDS,
        key=lambda seed: (-scores[seed][0], -scores[seed][1], seed),
    )[0]
    selected_artifact = _effective_artifact_directory(
        reports[selected_seed],
        artifact_root / f"seed{selected_seed}",
    )
    winner = {
        "schema_version": WINNER_SCHEMA_VERSION,
        "artifact_role": ARTIFACT_ROLE,
        "model_family": MODEL_FAMILY,
        "ablation_mode": mode.value,
        "selected_seed": selected_seed,
        "selection_rule": (
            "highest adaptive weakest-source macro-F1, then overall macro-F1, then lower seed"
        ),
        "selection_score": {
            "weakest_source_domain_macro_f1": scores[selected_seed][0],
            "overall_macro_f1": scores[selected_seed][1],
        },
        "selected_training_report": _regular_file_record(report_paths[selected_seed]),
        "artifact_directory": _display_path(selected_artifact),
        "artifact_files": v6._artifact_records(selected_artifact),
        "prepared_partition_commitments": reports[selected_seed]["prepared_partition_commitments"],
        "compute_matching": reports[selected_seed]["compute_matching"],
        "estimand_contract": _estimand_contract(),
        "statistical_analysis_plan": _statistical_analysis_plan_contract(),
        "independent_generalization_evidence": False,
        "confirmatory_is_only_independent_generalization_evidence": True,
        "final_holm_no_k_role": (
            FINAL_HOLM_NO_K_ROLE if mode is AblationMode.NO_K else "NOT_NO_K_BASELINE"
        ),
        "legacy_v5_no_k_final_holm_eligible": False,
        "zero_k_exposure_holm_eligible": False,
        "deployment_eligible": False,
    }
    selection = {
        "schema_version": SELECTION_SCHEMA_VERSION,
        "artifact_role": ARTIFACT_ROLE,
        "model_family": MODEL_FAMILY,
        "ablation_mode": mode.value,
        "fixed_model_seeds": list(MODEL_SEEDS),
        "seed_results": {
            str(seed): {
                "weakest_source_domain_macro_f1": scores[seed][0],
                "overall_macro_f1": scores[seed][1],
                "training_report": _regular_file_record(report_paths[seed]),
            }
            for seed in MODEL_SEEDS
        },
        "winner": winner,
        "adaptive_development_selection": True,
        "independent_generalization_evidence": False,
        "estimand_contract": _estimand_contract(),
        "statistical_analysis_plan": _statistical_analysis_plan_contract(),
        "final_holm_no_k_role": (
            FINAL_HOLM_NO_K_ROLE if mode is AblationMode.NO_K else "NOT_NO_K_BASELINE"
        ),
        "legacy_v5_no_k_final_holm_eligible": False,
        "zero_k_exposure_holm_eligible": False,
        "deployment_eligible": False,
    }
    if not validate_only:
        _write_json_exclusive_atomic(winner_manifest_path, winner)
        _write_json_exclusive_atomic(selection_report_path, selection)
    return {
        "status": "VALIDATED_WITHOUT_WRITE" if validate_only else "AGGREGATION_WRITTEN",
        "mode": mode.value,
        "selected_seed": selected_seed,
        "selection_report_path": _display_path(selection_report_path),
        "winner_manifest_path": _display_path(winner_manifest_path),
    }


def _cross_mode_projection(report: dict[str, Any]) -> dict[str, Any]:
    commitments = dict(cast(dict[str, Any], report["prepared_partition_commitments"]))
    commitments.pop("TRAIN", None)
    arguments = dict(cast(dict[str, Any], report["training_arguments"]))
    arguments.pop("model_seed", None)
    return {
        "protected_partition_commitments": commitments,
        "input_artifacts": report.get("input_artifacts"),
        "architecture": report.get("architecture"),
        "training_arguments": arguments,
        "recipe_commitment_sha256": report.get("recipe_commitment_sha256"),
        "base_source_kind": report.get("base_source_kind"),
        "base_source": report.get("base_source"),
        "optimizer_step_contract": cast(dict[str, Any], report["compute_matching"]).get(
            "optimizer_step_contract"
        ),
        "estimand_contract": report.get("estimand_contract"),
        "statistical_analysis_plan": report.get("statistical_analysis_plan"),
    }


def aggregate_ablation_matrix(
    *,
    report_root: Path,
    artifact_root: Path,
    matrix_report_path: Path,
    validate_only: bool,
) -> dict[str, Any]:
    reports_by_mode: dict[AblationMode, dict[int, dict[str, Any]]] = {}
    scores_by_mode: dict[AblationMode, dict[int, tuple[float, float]]] = {}
    report_records: dict[str, dict[str, dict[str, int | str]]] = {}
    for mode in AblationMode:
        slug = _mode_slug(mode)
        reports: dict[int, dict[str, Any]] = {}
        scores: dict[int, tuple[float, float]] = {}
        records: dict[str, dict[str, int | str]] = {}
        for seed in MODEL_SEEDS:
            report_path = report_root / slug / f"kf-deberta-sentiment-v6-{slug}-seed{seed}.json"
            artifact_dir = artifact_root / slug / f"seed{seed}"
            report = _read_json_object(report_path, f"{mode.value} seed{seed} report")
            scores[seed] = _validate_candidate_report(
                report,
                mode=mode,
                seed=seed,
                artifact_dir=artifact_dir,
            )
            reports[seed] = report
            records[str(seed)] = v6._regular_file_record(report_path)
        baseline = _cross_seed_projection(reports[MODEL_SEEDS[0]])
        if any(_cross_seed_projection(reports[seed]) != baseline for seed in MODEL_SEEDS[1:]):
            raise RuntimeError(f"{mode.value} 3개 seed commitment가 다릅니다.")
        reports_by_mode[mode] = reports
        scores_by_mode[mode] = scores
        report_records[mode.value] = records

    baseline_mode = _cross_mode_projection(reports_by_mode[AblationMode.NO_K][MODEL_SEEDS[0]])
    for mode in AblationMode:
        for seed in MODEL_SEEDS:
            if _cross_mode_projection(reports_by_mode[mode][seed]) != baseline_mode:
                raise RuntimeError(
                    "4개 data mode의 보호 holdout·model recipe·base commitment가 다릅니다."
                )

    mode_aggregates: dict[str, Any] = {}
    for mode in AblationMode:
        weakest = np.asarray(
            [scores_by_mode[mode][seed][0] for seed in MODEL_SEEDS],
            dtype=np.float64,
        )
        overall = np.asarray(
            [scores_by_mode[mode][seed][1] for seed in MODEL_SEEDS],
            dtype=np.float64,
        )
        mode_aggregates[mode.value] = {
            "stage2_data_intervention": reports_by_mode[mode][MODEL_SEEDS[0]][
                "stage2_data_intervention"
            ],
            "train_commitment": reports_by_mode[mode][MODEL_SEEDS[0]][
                "prepared_partition_commitments"
            ]["TRAIN"],
            "stage1_compute_matching": reports_by_mode[mode][MODEL_SEEDS[0]]["compute_matching"][
                "stage1"
            ],
            "stage2_compute_matching": reports_by_mode[mode][MODEL_SEEDS[0]]["compute_matching"][
                "stage2"
            ],
            "weakest_source_domain_macro_f1": {
                "mean": float(weakest.mean()),
                "sample_std": float(weakest.std(ddof=1)),
                "minimum": float(weakest.min()),
            },
            "overall_macro_f1": {
                "mean": float(overall.mean()),
                "sample_std": float(overall.std(ddof=1)),
                "minimum": float(overall.min()),
            },
        }

    contrasts: dict[str, Any] = {}
    no_k_scores = scores_by_mode[AblationMode.NO_K]
    for mode in (
        AblationMode.NEWS_ONLY,
        AblationMode.DISCLOSURE_ONLY,
        AblationMode.FULL,
    ):
        weakest_deltas = [
            scores_by_mode[mode][seed][0] - no_k_scores[seed][0] for seed in MODEL_SEEDS
        ]
        overall_deltas = [
            scores_by_mode[mode][seed][1] - no_k_scores[seed][1] for seed in MODEL_SEEDS
        ]
        contrasts[mode.value] = {
            "reference": AblationMode.NO_K.value,
            "matched_seed_weakest_domain_macro_f1_delta": {
                str(seed): weakest_deltas[index] for index, seed in enumerate(MODEL_SEEDS)
            },
            "matched_seed_overall_macro_f1_delta": {
                str(seed): overall_deltas[index] for index, seed in enumerate(MODEL_SEEDS)
            },
            "mean_weakest_domain_macro_f1_delta": float(np.mean(weakest_deltas)),
            "mean_overall_macro_f1_delta": float(np.mean(overall_deltas)),
        }

    matrix = {
        "schema_version": MATRIX_SCHEMA_VERSION,
        "artifact_role": ARTIFACT_ROLE,
        "model_family": MODEL_FAMILY,
        "status": "COMPLETE_ADAPTIVE_DEVELOPMENT_MATRIX",
        "modes": [mode.value for mode in AblationMode],
        "fixed_model_seeds": list(MODEL_SEEDS),
        "aggregation_unit": "matched_model_seed",
        "mode_aggregates": mode_aggregates,
        "paired_contrasts_vs_no_k": contrasts,
        "training_reports": report_records,
        "compute_matching_interpretation": (
            "Every mode executes 32,907 Stage 1 row exposures per epoch and a 1,794-row "
            "Stage 2; removed K Gold is replaced by deterministic PUBLIC_TRAIN controls."
        ),
        "estimand_contract": _estimand_contract(),
        "statistical_analysis_plan": _statistical_analysis_plan_contract(),
        "selection_partition_role": v6.ADAPTIVE_SELECTION_ROLE,
        "independent_generalization_evidence": False,
        "confirmatory_is_only_independent_generalization_evidence": True,
        "final_holm_baseline_contract": {
            "no_k_role": FINAL_HOLM_NO_K_ROLE,
            "estimand_id": ESTIMAND_ID,
            "required_model_family": MODEL_FAMILY,
            "required_seed_runs": list(MODEL_SEEDS),
            "legacy_v5_no_k_role": LEGACY_V5_NO_K_ROLE,
            "legacy_v5_no_k_final_holm_eligible": False,
            "zero_k_exposure_holm_eligible": False,
        },
        "deployment_eligible": False,
    }
    if not validate_only:
        _write_json_exclusive_atomic(matrix_report_path, matrix)
    return {
        "status": "VALIDATED_WITHOUT_WRITE" if validate_only else "MATRIX_WRITTEN",
        "matrix_report_path": _display_path(matrix_report_path),
        "modes": matrix["modes"],
        "fixed_model_seeds": matrix["fixed_model_seeds"],
    }


def main() -> None:
    args = parser().parse_args()
    v6.validate_arguments(args)
    _validate_compute_matched_schedule(args)
    if args.aggregate and args.aggregate_matrix:
        raise SystemExit("--aggregate와 --aggregate-matrix는 동시에 사용할 수 없습니다.")
    if args.reuse_full_candidate and (
        args.aggregate or args.aggregate_matrix or args.validate_only
    ):
        raise SystemExit("FULL 후보 재사용은 개별 FULL 영수증 생성에만 사용할 수 있습니다.")
    if args.aggregate_matrix:
        report_root = args.report_dir or PROJECT_ROOT / "reports/ablations/v6"
        artifact_root = args.artifact_root or PROJECT_ROOT / "artifacts/sentiment/v6-ablations"
        matrix_path = args.matrix_report_path or report_root / "matrix.json"
        result = aggregate_ablation_matrix(
            report_root=report_root,
            artifact_root=artifact_root,
            matrix_report_path=matrix_path,
            validate_only=args.validate_only,
        )
        print(json.dumps(result, ensure_ascii=False))
        return
    if args.mode is None:
        raise SystemExit("개별 학습/집계에는 --mode가 필요합니다.")
    if args.seed not in MODEL_SEEDS:
        raise SystemExit(f"ablation seed는 {MODEL_SEEDS}로 고정됩니다.")
    if args.mode == ZERO_K_EXPOSURE_MODE:
        if not args.validate_only or args.aggregate or args.aggregate_matrix:
            raise SystemExit("ZERO_K_EXPOSURE는 validation-only 탐색 진단으로만 허용됩니다.")
        paths = _ablation_paths(args)
        recipe_records = _records(_recipe_paths())
        print(
            json.dumps(
                _zero_k_exposure_validation(paths, args, recipe_records),
                ensure_ascii=False,
            )
        )
        return
    mode = AblationMode(args.mode)
    slug = _mode_slug(mode)
    if args.reuse_full_candidate and mode is not AblationMode.FULL:
        raise SystemExit("--reuse-full-candidate는 FULL mode에만 허용됩니다.")
    reuse_full_candidate = args.reuse_full_candidate or (
        mode is AblationMode.FULL
        and not args.aggregate
        and not args.aggregate_matrix
        and not args.validate_only
    )
    if args.aggregate:
        report_dir = args.report_dir or PROJECT_ROOT / f"reports/ablations/v6/{slug}"
        artifact_root = args.artifact_root or PROJECT_ROOT / (
            f"artifacts/sentiment/v6-ablations/{slug}"
        )
        selection_path = args.selection_report_path or report_dir / "selection.json"
        winner_path = args.winner_manifest_path or report_dir / "winner-manifest.json"
        result = aggregate_mode_runs(
            mode=mode,
            report_dir=report_dir,
            artifact_root=artifact_root,
            selection_report_path=selection_path,
            winner_manifest_path=winner_path,
            validate_only=args.validate_only,
        )
        print(json.dumps(result, ensure_ascii=False))
        return

    default_output, default_report = _default_paths(mode, args.seed)
    output_dir = args.output_dir or default_output
    report_path = args.report_path or default_report
    if reuse_full_candidate:
        if args.output_dir is not None:
            raise SystemExit("FULL artifact 재사용 시 새 --output-dir를 지정할 수 없습니다.")
        if report_path.exists() or report_path.is_symlink():
            raise SystemExit(f"ablation report 출력이 이미 존재합니다: {report_path}")
        candidate_artifact, candidate_report = _default_candidate_paths(args.seed)
        candidate_artifact = args.candidate_artifact_dir or candidate_artifact
        candidate_report = args.candidate_report_path or candidate_report
        paths = _ablation_paths(args)
        input_paths = data_contract.input_paths(paths)
        input_paths.update(gold_provenance_paths(args))
        for name, path in input_paths.items():
            v6.assert_training_path_allowed(path, name)
            v5._require_regular_input(path, name)
        gold_provenance = validate_all_gold_provenance(args)
        prepared = data_contract.prepare_ablation_data(mode, paths)
        gold_rows = _validate_prepared(prepared)
        stage1_plan, stage2_plan = _compute_matched_stages(prepared, gold_rows)
        base_source = v6.resolve_base_source(args.base_source, verify_pinned=True)
        protocol = _protocol_record(
            prepared,
            gold_rows,
            stage1_plan,
            stage2_plan,
            args,
            {name: v5._input_artifact_record(path) for name, path in input_paths.items()},
            _records(_recipe_paths()),
            base_source,
            gold_provenance,
        )
        receipt = build_full_reuse_receipt(
            protocol=protocol,
            source_report_path=candidate_report,
            source_artifact_dir=candidate_artifact,
            report_path=report_path,
            seed=args.seed,
        )
        print(json.dumps(receipt, ensure_ascii=False))
        return
    if output_dir.exists() or output_dir.is_symlink():
        raise SystemExit(f"ablation artifact 출력이 이미 존재합니다: {output_dir}")
    if report_path.exists() or report_path.is_symlink():
        raise SystemExit(f"ablation report 출력이 이미 존재합니다: {report_path}")

    paths = _ablation_paths(args)
    input_paths = data_contract.input_paths(paths)
    input_paths.update(gold_provenance_paths(args))
    for name, path in input_paths.items():
        v6.assert_training_path_allowed(path, name)
        v5._require_regular_input(path, name)
    gold_provenance = validate_all_gold_provenance(args)
    recipe_records = _records(_recipe_paths())
    if args.validate_only:
        prepared = data_contract.prepare_ablation_data(mode, paths)
        gold_rows = _validate_prepared(prepared)
        stage1_plan, stage2_plan = _compute_matched_stages(prepared, gold_rows)
        base_source = v6.resolve_base_source(args.base_source, verify_pinned=False)
        protocol = _protocol_record(
            prepared,
            gold_rows,
            stage1_plan,
            stage2_plan,
            args,
            {name: v5._input_artifact_record(path) for name, path in input_paths.items()},
            recipe_records,
            base_source,
            gold_provenance,
        )
        print(json.dumps(protocol, ensure_ascii=False))
        return

    v6._set_seed(args.seed)
    base_source = v6.resolve_base_source(args.base_source, verify_pinned=True)
    execution_snapshot = v6.capture_execution_snapshot(input_paths, base_source)
    prepared = data_contract.prepare_ablation_data(mode, paths)
    gold_rows = _validate_prepared(prepared)
    stage1_plan, stage2_plan = _compute_matched_stages(prepared, gold_rows)
    base_source = v6.assert_execution_snapshot_unchanged(
        execution_snapshot,
        input_paths,
        args.base_source,
    )
    _assert_records_unchanged(recipe_records, _recipe_paths())
    protocol = _protocol_record(
        prepared,
        gold_rows,
        stage1_plan,
        stage2_plan,
        args,
        execution_snapshot["material"]["input_artifacts"],
        recipe_records,
        base_source,
        gold_provenance,
    )
    report = train_ablation(
        prepared,
        gold_rows,
        stage1_plan,
        stage2_plan,
        args,
        protocol,
        execution_snapshot,
        recipe_records,
        input_paths,
        output_dir,
        report_path,
    )
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
