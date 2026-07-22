from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path, PurePosixPath
from typing import Any

from hannah_montana_ai.services.kr_finbert_sc_raw_reference import (
    RawReferenceArtifactError,
    validate_raw_reference_artifact,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    CANDIDATE_MODEL as V6_CANDIDATE_MODEL_NAME,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    EXPECTED_HEAD_ARCHITECTURE as V6_EXPECTED_HEAD_ARCHITECTURE,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    MODEL_FAMILY as V6_MODEL_FAMILY,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    RUNTIME_LOADER_SCHEMA_VERSION as V6_RUNTIME_SCHEMA_VERSION,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    TRAINING_SCHEMA_VERSION as V6_TRAINING_SCHEMA_VERSION,
)
from hannah_montana_ai.training.sentiment_baseline_commitments import (
    canonical_json_sha256,
    directory_commitment,
    file_commitment,
    validate_directory_commitment,
    validate_file_commitment,
)
from hannah_montana_ai.training.sentiment_v6_baseline_commitment import (
    BASELINE_MODEL_NAME as V6_FAIR_BASELINE_MODEL_NAME,
)

__all__ = [
    "CONFIRMATORY_BASELINES",
    "CONFIRMATORY_SOURCES",
    "V6_CANDIDATE_MODEL_NAME",
    "V6_FAIR_BASELINE_MODEL_NAME",
    "V6_NO_K_ABLATION_MODEL_NAME",
    "build_v6_confirmatory_baseline_commitments",
    "canonical_v6_statistical_analysis_plan",
    "v6_baseline_paths",
    "validate_v6_confirmatory_baseline_commitments",
    "validate_v6_evaluation_runtime_parameters",
    "validate_v6_statistical_analysis_plan",
]
from hannah_montana_ai.training.sentiment_v6_baseline_commitment import (
    build_v6_kr_finbert_sc_baseline_commitment,
    validate_v6_kr_finbert_sc_baseline_commitment,
)

SAP_SCHEMA_VERSION = "k-fnspid-sentiment-statistical-analysis-plan/v3"
BASELINE_SCHEMA_VERSION = "sentiment-v6-confirmatory-baseline-commitments/v2"
CANDIDATE_MATCH_SCHEMA_VERSION = "sentiment-v6-candidate-matching-contract/v2"
NO_K_SELECTION_SCHEMA_VERSION = (
    "k-fnspid-compute-matched-sentiment-ablation-selection/v3"
)
NO_K_TRAINING_SCHEMA_VERSION = (
    "k-fnspid-compute-matched-sentiment-ablation-training/v3"
)
NO_K_WINNER_SCHEMA_VERSION = (
    "k-fnspid-compute-matched-sentiment-ablation-winner/v3"
)
NO_K_ARTIFACT_SCHEMA_VERSION = (
    "kf-deberta-compute-matched-sentiment-ablation-artifact/v3"
)

RAW_REFERENCE_MODEL_NAME = "kr_finbert_sc_raw_off_the_shelf"
PRE_K_FNSPID_MODEL_NAME = "pre_k_fnspid_kf_deberta"
V6_NO_K_ABLATION_MODEL_NAME = "kf_deberta_shared_residual_v6_no_k"
TFIDF_BASELINE_MODEL_NAME = "hana_tfidf_logistic"
QWEN_TEACHER_MODEL_NAME = "qwen3_4b_blind_teacher"
LEGACY_V5_NO_K_MODEL_NAME = "kf_deberta_no_k_ablation"

FAMILYWISE_ALPHA = 0.05
CONFIDENCE_LEVEL = 0.95
PRACTICAL_SUPERIORITY_MARGIN = 0.02
DEFAULT_BOOTSTRAP_SAMPLES = 2_000
DEFAULT_BOOTSTRAP_SEED = 20_260_715
EVALUATION_BATCH_SIZE = 16
REQUIRED_SEEDS = (17, 42, 73)
CONFIRMATORY_SOURCES = ("NEWS", "DISCLOSURE")
CONFIRMATORY_BASELINES = (
    RAW_REFERENCE_MODEL_NAME,
    PRE_K_FNSPID_MODEL_NAME,
    V6_FAIR_BASELINE_MODEL_NAME,
    V6_NO_K_ABLATION_MODEL_NAME,
)
REQUIRED_BASELINE_KEYS = frozenset(
    {
        RAW_REFERENCE_MODEL_NAME,
        TFIDF_BASELINE_MODEL_NAME,
        PRE_K_FNSPID_MODEL_NAME,
        V6_FAIR_BASELINE_MODEL_NAME,
        V6_NO_K_ABLATION_MODEL_NAME,
    }
)
NO_K_ARTIFACT_ROLE = "RESEARCH_ABLATION_NOT_DEPLOYABLE"
NO_K_FINAL_HOLM_ROLE = "NO_K_TRAIN_ROWS_WITH_SHARED_K_DEV"
NO_K_ESTIMAND_ID = "K_TRAINING_ROW_INTERVENTION_CONDITIONAL_ON_SHARED_K_DEVELOPMENT"
NO_K_STAGE1_UNIQUE_ROWS = 7_413
NO_K_STAGE1_EXPOSURES_PER_EPOCH = 32_907
NO_K_STAGE2_REFINEMENT_ROWS = 1_794
NO_K_PUBLIC_CONTROL_PER_LABEL = 598
LEGACY_V5_ROLE = "HISTORICAL_AUDIT_ONLY_NON_GATING"


def canonical_v6_statistical_analysis_plan() -> dict[str, Any]:
    hypotheses = [
        {
            "hypothesis_id": f"{source.casefold()}_v6_candidate_gt_{baseline}",
            "source_type": source,
            "candidate_model": V6_CANDIDATE_MODEL_NAME,
            "baseline_model": baseline,
            "metric": "sampling_design_weighted_plugin_macro_f1",
            "contrast": "candidate_minus_baseline",
            "null_hypothesis": "difference=0",
            "alternative_hypothesis": "difference!=0",
            "claim_direction": "candidate>baseline",
        }
        for source in CONFIRMATORY_SOURCES
        for baseline in CONFIRMATORY_BASELINES
    ]
    return {
        "schema_version": SAP_SCHEMA_VERSION,
        "candidate_pipeline": "source-hierarchical-v6",
        "frozen_before_public_test_or_sealed_gold": True,
        "familywise_alpha": FAMILYWISE_ALPHA,
        "multiple_comparison_correction": "holm_bonferroni/v1",
        "family_hypothesis_count": 8,
        "primary_metric": "sampling_design_weighted_plugin_macro_f1",
        "primary_metric_definition": {
            "class_order": ["NEGATIVE", "NEUTRAL", "POSITIVE"],
            "class_average": "unweighted_arithmetic_mean_over_three_class_plugin_f1",
            "zero_denominator_rule": "metric_component_equals_zero",
            "variance_estimator": "paired_stratified_delete_1_jackknife_srswor_fpc/v1",
        },
        "estimand_and_finite_frame": {
            "frame": (
                "K-FNSPID-v4 2026-04-01..2026-07-13 eligible canonical "
                "document-security units"
            ),
            "primary_estimands": (
                "source-specific design-weighted plug-in Macro-F1 and paired "
                "candidate-minus-named-baseline contrasts"
            ),
            "sampling_strata": "prelocked weak-rule auxiliary strata, not Gold labels",
            "long_horizon_or_external_population_claim_allowed": False,
        },
        "evaluation_batch_size": EVALUATION_BATCH_SIZE,
        "confirmatory_inference_backend": {
            "device": "cpu",
            "evaluator_batch_size": EVALUATION_BATCH_SIZE,
            "packaged_runtime_batch_size": 1,
            "parity_input": "unlabeled_confirmatory_reservation_only",
            "exact_threshold_label_agreement_required": True,
            "calibrated_probability_max_abs_error_tolerance": 1e-6,
            "base_encoder_safetensors_manifest_must_match": True,
        },
        "holm_hypotheses": hypotheses,
        "paired_design_inference": {
            "estimator": "candidate_minus_baseline",
            "variance_method": "paired_stratified_delete_1_jackknife_srswor_fpc/v1",
            "finite_population_correction": True,
            "sampling_unit": "event_cluster_id",
            "confidence_level": CONFIDENCE_LEVEL,
            "p_value_method": "two_sided_normal_from_design_jackknife_standard_error/v1",
            "inference_scope": "asymptotic_design_based_approximation",
            "zero_standard_error_policy": "p_value_one_fail_closed",
            "superiority_rule": {
                "observed_difference_must_be_positive": True,
                "confidence_interval_lower_bound_must_be_positive": True,
                "holm_adjusted_p_value_must_be_below_alpha": True,
            },
            "practical_superiority_rule": {
                "metric": "absolute_macro_f1_difference",
                "minimum_difference": PRACTICAL_SUPERIORITY_MARGIN,
                "confidence_interval_lower_bound_must_reach_minimum": True,
                "required_for_large_or_material_superiority_wording": True,
                "affects_statistical_superiority_flag": False,
            },
        },
        "bootstrap": {
            "samples": DEFAULT_BOOTSTRAP_SAMPLES,
            "base_seed": DEFAULT_BOOTSTRAP_SEED,
            "confidence_level": CONFIDENCE_LEVEL,
            "role": "secondary_interval_and_randomization_diagnostics",
        },
        "model_names": {
            "candidate": V6_CANDIDATE_MODEL_NAME,
            "raw_reference": RAW_REFERENCE_MODEL_NAME,
            "pre_k_fnspid_baseline": PRE_K_FNSPID_MODEL_NAME,
            "same_data_schedule_fair_baseline": V6_FAIR_BASELINE_MODEL_NAME,
            "same_structure_no_k_baseline": V6_NO_K_ABLATION_MODEL_NAME,
        },
        "raw_reference_contract": {
            "display_name": (
                "raw KR-FinBERT-SC, first-256-token, no target conditioning"
            ),
            "generic_kr_finbert_superiority_claim_allowed": False,
            "immutable_local_artifact_and_tokenizer_commitment_required": True,
        },
        "baseline_roles": {
            V6_FAIR_BASELINE_MODEL_NAME: {
                "required_contract": (
                    "same prepared rows, partitions, optimizer-step schedule, hierarchical "
                    "task, calibration, and seed-selection protocol"
                ),
                "required_model_seeds": list(REQUIRED_SEEDS),
                "included_in_holm_family": True,
            },
            V6_NO_K_ABLATION_MODEL_NAME: {
                "required_model_family": V6_MODEL_FAMILY,
                "required_model_seeds": list(REQUIRED_SEEDS),
                "required_winner_role": NO_K_FINAL_HOLM_ROLE,
                "included_in_holm_family": True,
            },
            LEGACY_V5_NO_K_MODEL_NAME: {
                "role": LEGACY_V5_ROLE,
                "included_in_holm_family": False,
                "affects_deployment_gate": False,
            },
        },
        "excluded_confirmatory_models": {
            QWEN_TEACHER_MODEL_NAME: {
                "role": "blind_teacher_diagnostic_only",
                "included_in_holm_family": False,
                "affects_deployment_gate": False,
            },
            LEGACY_V5_NO_K_MODEL_NAME: {
                "role": LEGACY_V5_ROLE,
                "included_in_holm_family": False,
                "affects_deployment_gate": False,
            },
        },
        "claim_scope": {
            "global_sota_claim_allowed": False,
            "allowed_claim": "locked_v6_candidate_vs_named_locked_baselines_only",
            "large_or_material_wording_requires_practical_margin": True,
            "excluded_claim": (
                "global_or_all_korean_finance_benchmark_sota; generic KR-FinBERT-SC "
                "superiority; long-horizon temporal generalization; K-FNSPID-only "
                "causal effect"
            ),
        },
    }


def validate_v6_statistical_analysis_plan(value: object) -> dict[str, Any]:
    expected = canonical_v6_statistical_analysis_plan()
    if not isinstance(value, Mapping) or _canonical_json(value) != _canonical_json(expected):
        raise ValueError("v6 statistical_analysis_plan이 고정된 확증 평가 계약과 다릅니다.")
    hypotheses = expected["holm_hypotheses"]
    if (
        len(hypotheses) != 8
        or len({row["hypothesis_id"] for row in hypotheses}) != 8
        or any(row["candidate_model"] != V6_CANDIDATE_MODEL_NAME for row in hypotheses)
    ):
        raise ValueError("v6 Holm 가설군이 정확한 8개 v6 후보 비교가 아닙니다.")
    return expected


def validate_v6_evaluation_runtime_parameters(
    plan: object,
    *,
    batch_size: int,
    bootstrap_samples: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    validated = validate_v6_statistical_analysis_plan(plan)
    bootstrap = _mapping(validated["bootstrap"], "v6 bootstrap")
    if (
        isinstance(batch_size, bool)
        or batch_size != validated["evaluation_batch_size"]
        or isinstance(bootstrap_samples, bool)
        or bootstrap_samples != bootstrap["samples"]
        or isinstance(bootstrap_seed, bool)
        or bootstrap_seed != bootstrap["base_seed"]
    ):
        raise ValueError("평가 CLI 인자가 잠긴 v6 statistical_analysis_plan과 다릅니다.")
    return validated


def canonical_candidate_matching_contract(training_report: object) -> dict[str, Any]:
    report = _mapping(training_report, "v6 candidate training report")
    selection = _mapping(report.get("candidate_selection"), "v6 candidate selection")
    arguments = _mapping(report.get("training_arguments"), "v6 training arguments")
    stages = _mapping(report.get("stage_selection"), "v6 stage selection")
    stage1 = _mapping(stages.get("stage1"), "v6 stage1")
    stage2 = _mapping(stages.get("stage2"), "v6 stage2")
    prepared = _mapping(
        report.get("prepared_partition_commitments"),
        "v6 prepared partition commitments",
    )
    input_artifacts = _mapping(report.get("input_artifacts"), "v6 input artifacts")
    if (
        report.get("schema_version") != V6_TRAINING_SCHEMA_VERSION
        or report.get("public_test_opened") is not False
        or report.get("confirmatory_labels_opened") is not False
        or selection.get("public_test_used") is not False
        or selection.get("confirmatory_used") is not False
        or selection.get("independent_generalization_evidence") is not False
    ):
        raise ValueError("v6 candidate가 봉인 전 matching 계약을 위반했습니다.")
    stage1_optimizer_steps = _integer(
        stage1.get("optimizer_steps"), "stage1 optimizer steps", minimum=1
    )
    stage1_planned_optimizer_steps = _integer(
        stage1.get("planned_optimizer_steps"),
        "stage1 planned optimizer steps",
        minimum=1,
    )
    stage2_optimizer_steps = _integer(
        stage2.get("optimizer_steps"), "stage2 optimizer steps", minimum=1
    )
    stage2_planned_optimizer_steps = _integer(
        stage2.get("planned_optimizer_steps"),
        "stage2 planned optimizer steps",
        minimum=1,
    )
    update_schedule = {
        "data_selection_seed": _integer(
            arguments.get("data_selection_seed"), "data selection seed", minimum=0
        ),
        "max_length": _integer(report.get("max_length"), "max length", minimum=16),
        "stage1_epochs": _integer(arguments.get("stage1_epochs"), "stage1 epochs", minimum=1),
        "stage2_epochs": _integer(arguments.get("stage2_epochs"), "stage2 epochs", minimum=1),
        "batch_size": _integer(arguments.get("batch_size"), "batch size", minimum=1),
        "gradient_accumulation_steps": _integer(
            arguments.get("gradient_accumulation_steps"),
            "gradient accumulation steps",
            minimum=1,
        ),
        "gradient_checkpointing": _boolean(
            arguments.get("gradient_checkpointing"), "gradient checkpointing"
        ),
        "eval_batch_size": _integer(
            arguments.get("eval_batch_size"), "eval batch size", minimum=1
        ),
        "optimizer": "AdamW",
        "scheduler": "cosine-with-8pct-warmup",
        "checkpoint_and_stopping_rule": (
            "fixed-full-epoch; best-in-stage-checkpoint-selected"
        ),
        "stage1_optimizer_steps": stage1_optimizer_steps,
        "stage1_planned_optimizer_steps": stage1_planned_optimizer_steps,
        "stage2_optimizer_steps": stage2_optimizer_steps,
        "stage2_planned_optimizer_steps": stage2_planned_optimizer_steps,
        "executed_optimizer_steps_total": _integer(
            stages.get("executed_optimizer_steps_total"),
            "executed optimizer steps",
            minimum=2,
        ),
        "planned_optimizer_steps_total": _integer(
            stages.get("planned_optimizer_steps_total"),
            "planned optimizer steps",
            minimum=2,
        ),
        "fixed_full_epoch_budget": stages.get("fixed_full_epoch_budget"),
    }
    stage1_history = stage1.get("history")
    stage2_history = stage2.get("history")
    executed_total = stage1_optimizer_steps + stage2_optimizer_steps
    planned_total = stage1_planned_optimizer_steps + stage2_planned_optimizer_steps
    if (
        update_schedule["fixed_full_epoch_budget"] is not True
        or update_schedule["stage1_optimizer_steps"]
        != update_schedule["stage1_planned_optimizer_steps"]
        or update_schedule["stage2_optimizer_steps"]
        != update_schedule["stage2_planned_optimizer_steps"]
        or update_schedule["executed_optimizer_steps_total"] != executed_total
        or update_schedule["planned_optimizer_steps_total"] != planned_total
        or executed_total != planned_total
        or not isinstance(stage1_history, list)
        or len(stage1_history) != update_schedule["stage1_epochs"]
        or not isinstance(stage2_history, list)
        or len(stage2_history) != update_schedule["stage2_epochs"]
    ):
        raise ValueError("v6 candidate 고정 full-epoch optimizer step 계약이 다릅니다.")
    return {
        "schema_version": CANDIDATE_MATCH_SCHEMA_VERSION,
        "candidate_model_family": V6_MODEL_FAMILY,
        "candidate_training_schema": V6_TRAINING_SCHEMA_VERSION,
        "prepared_partition_commitments": prepared,
        "prepared_partition_commitments_sha256": canonical_json_sha256(prepared),
        "input_artifacts_sha256": canonical_json_sha256(input_artifacts),
        "update_schedule": update_schedule,
        "update_schedule_sha256": canonical_json_sha256(update_schedule),
    }


def build_v6_confirmatory_baseline_commitments(
    *,
    project_root: Path,
    candidate_training_report: object,
    raw_reference_artifact: Path,
    tfidf_model: Path,
    pre_k_artifact: Path,
    pre_k_training_report: Path,
    fair_artifact_root: Path,
    fair_selection_report: Path,
    no_k_selection_report: Path,
    no_k_winner_manifest: Path,
) -> dict[str, Any]:
    root = project_root.resolve(strict=True)
    candidate_contract = canonical_candidate_matching_contract(candidate_training_report)
    fair = build_v6_kr_finbert_sc_baseline_commitment(
        project_root=root,
        selection_report=fair_selection_report,
    )
    fair_winner = root / _safe_relative_path(
        _mapping(fair.get("winner_artifact"), "v6 fair winner").get("path"),
        "v6 fair winner",
    )
    expected_fair_winner = (
        fair_artifact_root / f"seed{fair['selected_seed']}"
    ).resolve(strict=True)
    if fair_winner.resolve(strict=True) != expected_fair_winner:
        raise ValueError("v6 fair winner artifact가 지정 artifact root와 다릅니다.")
    no_k = _build_seeded_commitment(
        root=root,
        artifact_root=None,
        selection_path=no_k_selection_report,
        winner_manifest_path=no_k_winner_manifest,
        selection_schema=NO_K_SELECTION_SCHEMA_VERSION,
        label="v6 no-K baseline",
    )
    raw_reference = _raw_reference_commitment(raw_reference_artifact, root)
    payload = {
        "schema_version": BASELINE_SCHEMA_VERSION,
        "candidate_matching_contract": candidate_contract,
        "confirmatory_labels_used": False,
        "public_test_labels_used": False,
        "baselines": {
            RAW_REFERENCE_MODEL_NAME: raw_reference,
            TFIDF_BASELINE_MODEL_NAME: {"artifact": file_commitment(tfidf_model, root)},
            PRE_K_FNSPID_MODEL_NAME: {
                "training_report": file_commitment(pre_k_training_report, root),
                "winner_artifact": directory_commitment(pre_k_artifact, root),
            },
            V6_FAIR_BASELINE_MODEL_NAME: fair,
            V6_NO_K_ABLATION_MODEL_NAME: no_k,
        },
        "excluded_historical_baselines": _excluded_historical_baselines(),
    }
    return validate_v6_confirmatory_baseline_commitments(
        payload,
        root,
        candidate_training_report=candidate_training_report,
    )


def validate_v6_confirmatory_baseline_commitments(
    value: object,
    project_root: Path,
    *,
    candidate_training_report: object,
) -> dict[str, Any]:
    root = project_root.resolve(strict=True)
    payload = _mapping(value, "v6 baseline commitments")
    baselines = _mapping(payload.get("baselines"), "v6 baselines")
    candidate_contract = canonical_candidate_matching_contract(candidate_training_report)
    if (
        set(payload)
        != {
            "schema_version",
            "candidate_matching_contract",
            "confirmatory_labels_used",
            "public_test_labels_used",
            "baselines",
            "excluded_historical_baselines",
        }
        or payload.get("schema_version") != BASELINE_SCHEMA_VERSION
        or payload.get("candidate_matching_contract") != candidate_contract
        or payload.get("confirmatory_labels_used") is not False
        or payload.get("public_test_labels_used") is not False
        or set(baselines) != REQUIRED_BASELINE_KEYS
        or payload.get("excluded_historical_baselines")
        != _excluded_historical_baselines()
    ):
        raise ValueError("v6 baseline lock 계약이 완전하지 않습니다.")
    tfidf = _mapping(baselines[TFIDF_BASELINE_MODEL_NAME], "v6 TF-IDF baseline")
    raw_reference = _mapping(
        baselines[RAW_REFERENCE_MODEL_NAME], "v6 raw KR-FinBERT-SC baseline"
    )
    pre_k = _mapping(baselines[PRE_K_FNSPID_MODEL_NAME], "v6 pre-K baseline")
    if set(tfidf) != {"artifact"} or set(pre_k) != {
        "training_report",
        "winner_artifact",
    }:
        raise ValueError("v6 진단 baseline commitment 구성이 다릅니다.")
    normalized = {
        RAW_REFERENCE_MODEL_NAME: _validate_raw_reference_commitment(
            raw_reference, root
        ),
        TFIDF_BASELINE_MODEL_NAME: {
            "artifact": validate_file_commitment(
                tfidf["artifact"], root, "v6 TF-IDF artifact"
            )
        },
        PRE_K_FNSPID_MODEL_NAME: {
            "training_report": validate_file_commitment(
                pre_k["training_report"], root, "v6 pre-K report"
            ),
            "winner_artifact": validate_directory_commitment(
                pre_k["winner_artifact"], root, "v6 pre-K artifact"
            ),
        },
        V6_FAIR_BASELINE_MODEL_NAME: _validate_external_fair_commitment(
            baselines[V6_FAIR_BASELINE_MODEL_NAME], root, candidate_contract
        ),
        V6_NO_K_ABLATION_MODEL_NAME: _validate_no_k_commitment(
            baselines[V6_NO_K_ABLATION_MODEL_NAME],
            root,
            candidate_training_report,
        ),
    }
    return {
        "schema_version": BASELINE_SCHEMA_VERSION,
        "candidate_matching_contract": candidate_contract,
        "confirmatory_labels_used": False,
        "public_test_labels_used": False,
        "baselines": normalized,
        "excluded_historical_baselines": _excluded_historical_baselines(),
    }


def v6_baseline_paths(value: object, project_root: Path) -> dict[str, Path]:
    payload = _mapping(value, "v6 baseline commitments")
    baselines = _mapping(payload.get("baselines"), "v6 baselines")
    root = project_root.resolve(strict=True)

    def resolve(record: object, label: str) -> Path:
        raw = _mapping(record, label).get("path")
        path = (root / _safe_relative_path(raw, label)).resolve(strict=True)
        path.relative_to(root)
        return path

    tfidf = _mapping(baselines[TFIDF_BASELINE_MODEL_NAME], "TF-IDF")
    raw_reference = _mapping(baselines[RAW_REFERENCE_MODEL_NAME], "raw KR-FinBERT-SC")
    pre_k = _mapping(baselines[PRE_K_FNSPID_MODEL_NAME], "pre-K")
    fair = _mapping(baselines[V6_FAIR_BASELINE_MODEL_NAME], "v6 fair")
    no_k = _mapping(baselines[V6_NO_K_ABLATION_MODEL_NAME], "v6 no-K")
    return {
        "raw_reference_artifact": resolve(
            raw_reference["artifact"], "raw KR-FinBERT-SC artifact"
        ),
        "tfidf_model": resolve(tfidf["artifact"], "TF-IDF artifact"),
        "pre_k_artifact": resolve(pre_k["winner_artifact"], "pre-K artifact"),
        "pre_k_training_report": resolve(pre_k["training_report"], "pre-K report"),
        "fair_selection_report": resolve(
            fair["selection_report"], "v6 fair selection"
        ),
        "fair_winner_artifact": resolve(
            fair["winner_artifact"], "v6 fair artifact"
        ),
        "no_k_winner_artifact": resolve(
            no_k["winner_artifact"], "v6 no-K artifact"
        ),
    }


def _raw_reference_commitment(path: Path, root: Path) -> dict[str, Any]:
    try:
        contract = validate_raw_reference_artifact(path)
    except RawReferenceArtifactError as exception:
        raise ValueError(str(exception)) from exception
    if contract.artifact_dir != path.resolve(strict=True):
        raise ValueError("raw KR-FinBERT-SC artifact 경로가 canonical하지 않습니다.")
    return {
        "artifact": directory_commitment(contract.artifact_dir, root),
        "manifest_sha256": contract.manifest_sha256,
        "inference_contract": {
            "max_length": contract.max_length,
            "truncation": "first_tokens",
            "target_conditioning": False,
            "local_files_only": True,
        },
    }


def _validate_raw_reference_commitment(
    value: object,
    root: Path,
) -> dict[str, Any]:
    record = _mapping(value, "raw KR-FinBERT-SC commitment")
    if set(record) != {"artifact", "manifest_sha256", "inference_contract"}:
        raise ValueError("raw KR-FinBERT-SC commitment 필드가 다릅니다.")
    artifact = validate_directory_commitment(
        record["artifact"], root, "raw KR-FinBERT-SC artifact"
    )
    artifact_path = root / _safe_relative_path(
        artifact.get("path"), "raw KR-FinBERT-SC artifact"
    )
    expected = _raw_reference_commitment(artifact_path, root)
    if record != expected:
        raise ValueError("raw KR-FinBERT-SC commitment가 실제 pinned artifact와 다릅니다.")
    return expected


def _excluded_historical_baselines() -> dict[str, Any]:
    return {
        LEGACY_V5_NO_K_MODEL_NAME: {
            "role": LEGACY_V5_ROLE,
            "included_in_holm_family": False,
            "affects_deployment_gate": False,
        }
    }


def _build_seeded_commitment(
    *,
    root: Path,
    artifact_root: Path | None,
    selection_path: Path,
    winner_manifest_path: Path | None,
    selection_schema: str,
    label: str,
) -> dict[str, Any]:
    selection_record = file_commitment(selection_path, root)
    selection = _load_json(selection_path, label)
    if selection.get("schema_version") != selection_schema:
        raise ValueError(f"{label} selection schema가 다릅니다.")
    seed_results = _mapping(selection.get("seed_results"), f"{label} seed results")
    reports: dict[str, dict[str, int | str]] = {}
    for seed in REQUIRED_SEEDS:
        result = _mapping(seed_results.get(str(seed)), f"{label} seed{seed}")
        report_record = _mapping(result.get("training_report"), f"{label} seed report")
        report_path = root / _safe_relative_path(report_record.get("path"), label)
        reports[str(seed)] = file_commitment(report_path, root)
    winner = _mapping(selection.get("winner"), f"{label} winner")
    selected_seed = _required_seed(winner.get("selected_seed"), f"{label} winner seed")
    winner_record: dict[str, int | str] | None = None
    if winner_manifest_path is not None:
        winner_record = file_commitment(winner_manifest_path, root)
        if _load_json(winner_manifest_path, f"{label} winner manifest") != winner:
            raise ValueError(f"{label} winner manifest와 selection winner가 다릅니다.")
    artifact_path = root / _safe_relative_path(
        winner.get("artifact_directory"), f"{label} artifact"
    )
    if artifact_root is not None:
        expected = (artifact_root / f"seed{selected_seed}").resolve(strict=True)
        if artifact_path.resolve(strict=True) != expected:
            raise ValueError(f"{label} winner artifact 경로가 seed 선택과 다릅니다.")
    commitment: dict[str, Any] = {
        "selection_report": selection_record,
        "seed_reports": reports,
        "selected_seed": selected_seed,
        "winner_artifact": directory_commitment(artifact_path, root),
    }
    if winner_record is not None:
        commitment["winner_manifest"] = winner_record
    return commitment


def _validate_external_fair_commitment(
    value: object,
    root: Path,
    candidate_contract: dict[str, Any],
) -> dict[str, Any]:
    fair = validate_v6_kr_finbert_sc_baseline_commitment(value, project_root=root)
    if fair.get("baseline_model_name") != V6_FAIR_BASELINE_MODEL_NAME:
        raise ValueError("v6 fair baseline 모델명이 SAP 계약과 다릅니다.")
    seed_runs = _mapping(fair.get("seed_runs"), "v6 fair seed runs")
    if set(seed_runs) != {str(seed) for seed in REQUIRED_SEEDS}:
        raise ValueError("v6 fair baseline은 정확히 3개 고정 seed가 필요합니다.")
    for seed in REQUIRED_SEEDS:
        run = _mapping(seed_runs[str(seed)], f"v6 fair seed{seed}")
        _validate_external_fair_matching_contract(
            run.get("candidate_matching_contract"),
            candidate_contract,
            seed=seed,
        )
    return fair


def _validate_external_fair_matching_contract(
    value: object,
    candidate: dict[str, Any],
    *,
    seed: int,
) -> None:
    fair = _mapping(value, f"v6 fair seed{seed} candidate matching")
    schedule = _mapping(fair.get("configured_schedule"), "v6 fair configured schedule")
    planned = _mapping(fair.get("planned_optimizer_steps"), "v6 fair planned steps")
    executed = _mapping(fair.get("executed_optimizer_steps"), "v6 fair executed steps")
    semantics = _mapping(fair.get("matching_semantics"), "v6 fair matching semantics")
    candidate_schedule = _mapping(candidate.get("update_schedule"), "v6 candidate schedule")
    expected_schedule = {
        key: candidate_schedule[key]
        for key in (
            "stage1_epochs",
            "stage2_epochs",
            "batch_size",
            "eval_batch_size",
            "gradient_accumulation_steps",
            "gradient_checkpointing",
            "optimizer",
            "scheduler",
            "checkpoint_and_stopping_rule",
        )
    }
    expected_steps = {
        "stage1": candidate_schedule["stage1_optimizer_steps"],
        "stage2": candidate_schedule["stage2_optimizer_steps"],
        "total": candidate_schedule["executed_optimizer_steps_total"],
    }
    if (
        fair.get("schema_version")
        != "kr-finbert-sc-v6-candidate-matching-contract/v1"
        or fair.get("candidate_trainer") != "scripts/train_kf_deberta_sentiment_v6.py"
        or fair.get("prepared_partition_commitments")
        != candidate["prepared_partition_commitments"]
        or fair.get("input_artifacts_sha256") != candidate["input_artifacts_sha256"]
        or schedule != expected_schedule
        or planned != expected_steps
        or executed != expected_steps
        or semantics.get("same_raw_source_rows") is not True
        or semantics.get("same_group_disjoint_partitions") is not True
        or semantics.get("same_data_selection_seed") is not True
        or semantics.get("same_model_seed_set") is not True
        or semantics.get("same_target_aware_input") is not True
        or semantics.get("same_source_hierarchical_task_loss_calibration_selection")
        is not True
        or semantics.get("same_schedule_implementation_and_configured_rule") is not True
        or semantics.get("planned_equals_executed_optimizer_steps") is not True
    ):
        raise ValueError(
            f"v6 fair seed{seed}가 candidate 동일 data/split/update schedule과 다릅니다."
        )


def _validate_no_k_commitment(
    value: object,
    root: Path,
    candidate_training_report: object,
) -> dict[str, Any]:
    record = _validate_seeded_record(value, root, "v6 no-K baseline", winner_required=True)
    selection = record.pop("_selection")
    reports = record.pop("_reports")
    declared_runtime = record.pop("_declared_runtime")
    winner = _mapping(selection.get("winner"), "v6 no-K winner")
    winner_path = root / record["winner_manifest"]["path"]
    if _load_json(winner_path, "v6 no-K winner manifest") != winner:
        raise ValueError("v6 no-K winner manifest와 selection winner가 다릅니다.")
    if (
        selection.get("schema_version") != NO_K_SELECTION_SCHEMA_VERSION
        or selection.get("artifact_role") != NO_K_ARTIFACT_ROLE
        or selection.get("model_family") != V6_MODEL_FAMILY
        or selection.get("ablation_mode") != "NO_K"
        or selection.get("fixed_model_seeds") != list(REQUIRED_SEEDS)
        or selection.get("final_holm_no_k_role") != NO_K_FINAL_HOLM_ROLE
        or selection.get("legacy_v5_no_k_final_holm_eligible") is not False
        or selection.get("independent_generalization_evidence") is not False
        or selection.get("deployment_eligible") is not False
        or winner.get("schema_version") != NO_K_WINNER_SCHEMA_VERSION
        or winner.get("selected_seed") != record["selected_seed"]
        or winner.get("final_holm_no_k_role") != NO_K_FINAL_HOLM_ROLE
        or winner.get("legacy_v5_no_k_final_holm_eligible") is not False
        or winner.get("zero_k_exposure_holm_eligible") is not False
        or winner.get("independent_generalization_evidence") is not False
        or winner.get("deployment_eligible") is not False
        or not _valid_no_k_estimand(selection.get("estimand_contract"))
        or not _valid_no_k_estimand(winner.get("estimand_contract"))
        or not _valid_no_k_statistical_plan(selection.get("statistical_analysis_plan"))
        or not _valid_no_k_statistical_plan(winner.get("statistical_analysis_plan"))
    ):
        raise ValueError("v6 no-K 3-seed winner 계약이 다릅니다.")
    candidate = _mapping(candidate_training_report, "v6 candidate report")
    candidate_protected = dict(
        _mapping(candidate.get("prepared_partition_commitments"), "v6 candidate partitions")
    )
    candidate_protected.pop("TRAIN", None)
    candidate_structure = _source_hierarchical_structure(candidate.get("architecture"))
    candidate_arguments = _mapping(candidate.get("training_arguments"), "v6 candidate args")
    candidate_schedule = _mapping(
        canonical_candidate_matching_contract(candidate).get("update_schedule"),
        "v6 candidate update schedule",
    )
    runtimes: dict[int, dict[str, Any]] = {}
    for seed in REQUIRED_SEEDS:
        report = reports[str(seed)]
        report_partitions = dict(
            _mapping(report.get("prepared_partition_commitments"), "v6 no-K partitions")
        )
        report_partitions.pop("TRAIN", None)
        arguments = _mapping(report.get("training_arguments"), "v6 no-K arguments")
        test = _mapping(report.get("test"), "v6 no-K test")
        if (
            report.get("schema_version") != NO_K_TRAINING_SCHEMA_VERSION
            or report.get("artifact_role") != NO_K_ARTIFACT_ROLE
            or report.get("model_family") != V6_MODEL_FAMILY
            or report.get("ablation_mode") != "NO_K"
            or report.get("seed") != seed
            or report.get("public_test_opened") is not False
            or report.get("confirmatory_labels_opened") is not False
            or test.get("sample_count") != 0
            or report_partitions != candidate_protected
            or _source_hierarchical_structure(report.get("architecture"))
            != candidate_structure
            or report.get("base_source_kind") != candidate.get("base_source_kind")
            or report.get("base_source") != candidate.get("base_source")
            or not _same_no_k_training_schedule(arguments, candidate_arguments, candidate)
            or not _valid_no_k_estimand(report.get("estimand_contract"))
            or not _valid_no_k_statistical_plan(report.get("statistical_analysis_plan"))
            or not _valid_no_k_holm_contract(report.get("final_holm_baseline_contract"))
        ):
            raise ValueError(f"v6 no-K seed{seed}가 동일 구조·보호 분할 계약과 다릅니다.")
        _validate_no_k_compute_matching(report)
        _validate_no_k_fixed_budget(report, arguments, candidate_schedule)
        seed_runtime = _validate_no_k_runtime(report.get("runtime_loader_contract"))
        if seed_runtime["base_source"] != candidate.get("base_source"):
            raise ValueError("v6 no-K runtime base가 v6 candidate와 다릅니다.")
        runtimes[seed] = seed_runtime
    runtime = runtimes[record["selected_seed"]]
    selected_report = reports[str(record["selected_seed"])]
    artifact_path = root / record["winner_artifact"]["path"]
    metadata = _load_json(artifact_path / "hannah_metadata.json", "v6 no-K metadata")
    if (
        selected_report.get("artifact_directory") != record["winner_artifact"]["path"]
        or winner.get("artifact_directory") != record["winner_artifact"]["path"]
        or winner.get("artifact_files") != record["winner_artifact"]["files"]
        or metadata.get("schema_version") != NO_K_ARTIFACT_SCHEMA_VERSION
        or metadata.get("artifact_role") != NO_K_ARTIFACT_ROLE
        or metadata.get("model_family") != V6_MODEL_FAMILY
        or metadata.get("ablation_mode") != "NO_K"
        or metadata.get("seed") != record["selected_seed"]
        or metadata.get("runtime_loader_contract") != runtime
        or metadata.get("compute_matching") != selected_report.get("compute_matching")
        or not _valid_no_k_estimand(metadata.get("estimand_contract"))
        or not _valid_no_k_statistical_plan(metadata.get("statistical_analysis_plan"))
        or metadata.get("stage2_status") != "TRAINED_COMPUTE_MATCHED_REFINEMENT_CONTROL"
    ):
        raise ValueError("v6 no-K winner artifact 연결이 다릅니다.")
    if declared_runtime is not None and declared_runtime != runtime:
        raise ValueError("잠긴 v6 no-K runtime 계약이 실제 report와 다릅니다.")
    record["runtime_loader_contract"] = runtime
    return record


def _validate_seeded_record(
    value: object,
    root: Path,
    label: str,
    *,
    winner_required: bool,
) -> dict[str, Any]:
    raw = _mapping(value, label)
    required = {"selection_report", "seed_reports", "selected_seed", "winner_artifact"}
    if winner_required:
        required.add("winner_manifest")
    allowed_with_runtime = required | {"runtime_loader_contract"}
    if frozenset(raw) not in {frozenset(required), frozenset(allowed_with_runtime)}:
        raise ValueError(f"{label} commitment 필드가 다릅니다.")
    selection_record = validate_file_commitment(
        raw["selection_report"], root, f"{label} selection"
    )
    selection = _load_json(
        root / _commitment_relative_path(selection_record, f"{label} selection"),
        f"{label} selection",
    )
    selected_seed = _required_seed(raw.get("selected_seed"), f"{label} selected seed")
    declared_reports = _mapping(raw.get("seed_reports"), f"{label} reports")
    if set(declared_reports) != {str(seed) for seed in REQUIRED_SEEDS}:
        raise ValueError(f"{label}는 정확히 3개 고정 seed report가 필요합니다.")
    normalized_reports: dict[str, dict[str, int | str]] = {}
    reports: dict[str, dict[str, Any]] = {}
    seed_results = _mapping(selection.get("seed_results"), f"{label} seed results")
    for seed in REQUIRED_SEEDS:
        seed_text = str(seed)
        commitment = validate_file_commitment(
            declared_reports[seed_text], root, f"{label} seed{seed} report"
        )
        linked = _mapping(
            _mapping(seed_results.get(seed_text), f"{label} seed{seed}").get(
                "training_report"
            ),
            f"{label} linked report",
        )
        if linked != commitment:
            raise ValueError(f"{label} seed{seed} report link가 commitment와 다릅니다.")
        normalized_reports[seed_text] = commitment
        reports[seed_text] = _load_json(
            root / _commitment_relative_path(commitment, f"{label} seed{seed} report"),
            f"{label} seed{seed} report",
        )
    normalized: dict[str, Any] = {
        "selection_report": selection_record,
        "seed_reports": normalized_reports,
        "selected_seed": selected_seed,
        "winner_artifact": validate_directory_commitment(
            raw["winner_artifact"], root, f"{label} artifact"
        ),
        "_selection": selection,
        "_reports": reports,
        "_declared_runtime": raw.get("runtime_loader_contract"),
    }
    if winner_required:
        normalized["winner_manifest"] = validate_file_commitment(
            raw["winner_manifest"], root, f"{label} winner manifest"
        )
    return normalized


def _validate_no_k_runtime(value: object) -> dict[str, Any]:
    runtime = _mapping(value, "v6 no-K runtime")
    if (
        runtime.get("schema_version") != V6_RUNTIME_SCHEMA_VERSION
        or runtime.get("unknown_domain_behavior") != "FAIL_CLOSED"
        or runtime.get("domain_required") is not True
        or runtime.get("input_feature_version") != "source-target-prefix-head-tail/v2"
        or runtime.get("head_architecture") != V6_EXPECTED_HEAD_ARCHITECTURE
        or not isinstance(runtime.get("calibration"), Mapping)
    ):
        raise ValueError("v6 no-K shared-residual runtime 계약이 다릅니다.")
    _integer(runtime.get("max_length"), "v6 no-K max length", minimum=16)
    return runtime


def _valid_no_k_estimand(value: object) -> bool:
    if not isinstance(value, Mapping):
        return False
    return (
        value.get("estimand_id") == NO_K_ESTIMAND_ID
        and value.get("holm_no_k_role") == NO_K_FINAL_HOLM_ROLE
        and value.get("intervention") == "K_FNSPID_TRAINING_ROWS_BY_SOURCE"
        and value.get("conditioned_on")
        == "COMMON_K_DEVELOPMENT_CHECKPOINT_CALIBRATION_AND_ADAPTIVE_SELECTION"
        and value.get("common_k_development_labels_used") is True
        and value.get("does_not_estimate_zero_k_exposure") is True
        and value.get("zero_k_exposure_is_separate_exploratory_diagnostic") is True
    )


def _valid_no_k_statistical_plan(value: object) -> bool:
    if not isinstance(value, Mapping):
        return False
    return (
        value.get("schema_version") == "k-fnspid-compute-matched-ablation-sap/v1"
        and value.get("holm_family_modes")
        == ["NO_K", "NEWS_ONLY", "DISCLOSURE_ONLY", "FULL"]
        and value.get("holm_reference") == "NO_K"
        and value.get("holm_no_k_role") == NO_K_FINAL_HOLM_ROLE
        and value.get("estimand_id") == NO_K_ESTIMAND_ID
        and value.get("matched_unit") == "MODEL_SEED"
        and value.get("fixed_model_seeds") == list(REQUIRED_SEEDS)
        and value.get("candidate_compute_matched") is True
        and value.get("common_k_development_conditioning") is True
        and value.get("zero_k_exposure_holm_eligible") is False
        and value.get("independent_generalization_evidence") is False
    )


def _valid_no_k_holm_contract(value: object) -> bool:
    if not isinstance(value, Mapping):
        return False
    return (
        value.get("no_k_role") == NO_K_FINAL_HOLM_ROLE
        and value.get("estimand_id") == NO_K_ESTIMAND_ID
        and value.get("required_model_family") == V6_MODEL_FAMILY
        and value.get("required_seed_runs") == list(REQUIRED_SEEDS)
        and value.get("legacy_v5_no_k_role")
        == "LEGACY_DIAGNOSTIC_ONLY_NOT_FINAL_HOLM_ELIGIBLE"
        and value.get("legacy_v5_no_k_final_holm_eligible") is False
        and value.get("zero_k_exposure_holm_eligible") is False
    )


def _validate_no_k_compute_matching(report: dict[str, Any]) -> None:
    compute = _mapping(report.get("compute_matching"), "v6 no-K compute matching")
    stage1 = _mapping(compute.get("stage1"), "v6 no-K compute stage1")
    stage2 = _mapping(compute.get("stage2"), "v6 no-K compute stage2")
    steps = _mapping(
        compute.get("optimizer_step_contract"),
        "v6 no-K optimizer step contract",
    )
    stage1_steps = _mapping(steps.get("stage1"), "v6 no-K stage1 step contract")
    stage2_steps = _mapping(steps.get("stage2"), "v6 no-K stage2 step contract")
    stage2_labels = _mapping(
        stage2.get("public_control_label_distribution"),
        "v6 no-K public control labels",
    )
    stage2_intervention = _mapping(
        report.get("stage2_data_intervention"),
        "v6 no-K stage2 intervention",
    )
    partitions = _mapping(report.get("partition_count"), "v6 no-K partition count")
    if (
        compute.get("schema_version") != "k-fnspid-compute-matched-training-plan/v1"
        or stage1.get("source_unique_row_count") != NO_K_STAGE1_UNIQUE_ROWS
        or stage1.get("target_exposure_count_per_epoch")
        != NO_K_STAGE1_EXPOSURES_PER_EPOCH
        or stage1.get("minimum_exposures_per_unique_row") != 4
        or stage1.get("maximum_exposures_per_unique_row") != 5
        or stage1.get("all_source_rows_exposed") is not True
        or _mapping(
            stage1.get("exposure_rows_commitment"),
            "v6 no-K exposure commitment",
        ).get("row_count")
        != NO_K_STAGE1_EXPOSURES_PER_EPOCH
        or stage2.get("row_count") != NO_K_STAGE2_REFINEMENT_ROWS
        or stage2.get("eligible_k_gold_row_count") != 0
        or stage2.get("public_control_row_count") != NO_K_STAGE2_REFINEMENT_ROWS
        or stage2.get("no_k_training_exposure") is not True
        or stage2_labels
        != {
            label: NO_K_PUBLIC_CONTROL_PER_LABEL
            for label in ("NEGATIVE", "NEUTRAL", "POSITIVE")
        }
        or steps.get("candidate_steps_exactly_matched") is not True
        or stage1_steps.get("optimizer_steps") != 4_114
        or stage2_steps.get("optimizer_steps") != 452
        or partitions.get("TRAIN") != NO_K_STAGE1_UNIQUE_ROWS
        or partitions.get("STAGE1_EXPOSURES_PER_EPOCH")
        != NO_K_STAGE1_EXPOSURES_PER_EPOCH
        or partitions.get("K_GOLD_REFINEMENT") != 0
        or partitions.get("GOLD_REFINEMENT") != NO_K_STAGE2_REFINEMENT_ROWS
        or stage2_intervention.get("status")
        != "TRAINED_COMPUTE_MATCHED_REFINEMENT_CONTROL"
        or stage2_intervention.get("stage2_skipped") is not False
        or stage2_intervention.get("eligible_k_gold_rows") != 0
        or stage2_intervention.get("public_control_rows")
        != NO_K_STAGE2_REFINEMENT_ROWS
        or stage2_intervention.get("total_refinement_rows")
        != NO_K_STAGE2_REFINEMENT_ROWS
        or stage2_intervention.get("candidate_optimizer_steps_matched") is not True
    ):
        raise ValueError("v6 no-K compute-matched 데이터·노출·step 계약이 다릅니다.")


def _source_hierarchical_structure(value: object) -> dict[str, Any]:
    architecture = _mapping(value, "source-hierarchical architecture")
    normalized = {
        "encoder": architecture.get("encoder"),
        "lora_layers": architecture.get("lora_layers"),
        "lora_target_modules": architecture.get("lora_target_modules"),
        "lora_rank": architecture.get("lora_rank"),
        "lora_alpha": architecture.get("lora_alpha"),
        "head_architecture": architecture.get("head_architecture"),
        "head_outputs": architecture.get("head_outputs"),
        "composition": architecture.get(
            "composition", architecture.get("three_class_composition")
        ),
        "checkpoint_primary": architecture.get("checkpoint_primary"),
        "calibration": architecture.get("calibration"),
    }
    if any(item is None for item in normalized.values()):
        raise ValueError("source-hierarchical architecture 핵심 필드가 없습니다.")
    return normalized


def _same_no_k_training_schedule(
    no_k: dict[str, Any],
    candidate: dict[str, Any],
    candidate_report: dict[str, Any],
) -> bool:
    expected = {
        "data_selection_seed": candidate.get("data_selection_seed"),
        "max_length": candidate_report.get("max_length"),
        "stage1_epochs": candidate.get("stage1_epochs"),
        "stage2_epochs": candidate.get("stage2_epochs"),
        "batch_size": candidate.get("batch_size"),
        "eval_batch_size": candidate.get("eval_batch_size"),
        "gradient_accumulation_steps": candidate.get("gradient_accumulation_steps"),
        "stage1_learning_rate": candidate.get("stage1_learning_rate"),
        "stage2_learning_rate": candidate.get("stage2_learning_rate"),
        "weight_decay": candidate.get("weight_decay"),
        "rdrop_alpha": candidate.get("rdrop_alpha"),
        "gradient_checkpointing": candidate.get("gradient_checkpointing"),
    }
    return all(no_k.get(key) == item for key, item in expected.items())


def _validate_no_k_fixed_budget(
    report: dict[str, Any],
    arguments: dict[str, Any],
    candidate_schedule: dict[str, Any],
) -> None:
    stages = _mapping(report.get("stages"), "v6 no-K stages")
    stage1 = _mapping(stages.get("stage1"), "v6 no-K stage1")
    stage2 = _mapping(stages.get("stage2"), "v6 no-K stage2")
    expected_stage1 = _integer(
        candidate_schedule.get("stage1_optimizer_steps"),
        "v6 candidate stage1 steps",
        minimum=1,
    )
    expected_stage2 = _integer(
        candidate_schedule.get("stage2_optimizer_steps"),
        "v6 candidate stage2 steps",
        minimum=1,
    )

    def validate_stage(
        stage: dict[str, Any],
        *,
        label: str,
        expected_steps: int,
        expected_epochs: object,
    ) -> int:
        executed = _integer(
            stage.get("optimizer_steps"), f"v6 no-K {label} steps", minimum=1
        )
        planned = _integer(
            stage.get("planned_optimizer_steps"),
            f"v6 no-K planned {label} steps",
            minimum=1,
        )
        history = stage.get("history")
        provenance = _mapping(
            stage.get("active_parameter_provenance"),
            f"v6 no-K {label} parameter provenance",
        )
        membership = {
            "NEWS_TARGETED": False,
            "DISCLOSURE_TARGETED": False,
        }
        if (
            executed != expected_steps
            or planned != expected_steps
            or not isinstance(history, list)
            or len(history) != expected_epochs
            or provenance.get("residual_optimizer_membership") != membership
            or provenance.get("inactive_residual_bitwise_preserved") is not True
            or provenance.get("inactive_residual_exact_zero_before") is not True
            or provenance.get("inactive_residual_exact_zero_after") is not True
            or provenance.get("inactive_residual_state_sha256_before")
            != provenance.get("inactive_residual_state_sha256_after")
        ):
            raise ValueError(
                f"v6 no-K {label} update·exact-zero residual 계약이 다릅니다."
            )
        return executed

    stage1_steps = validate_stage(
        stage1,
        label="stage1",
        expected_steps=expected_stage1,
        expected_epochs=arguments.get("stage1_epochs"),
    )
    stage2_steps = validate_stage(
        stage2,
        label="stage2",
        expected_steps=expected_stage2,
        expected_epochs=arguments.get("stage2_epochs"),
    )
    total_steps = stage1_steps + stage2_steps
    if (
        stages.get("fixed_full_epoch_budget") is not True
        or arguments.get("stage1_epochs")
        != candidate_schedule.get("stage1_epochs")
        or arguments.get("stage2_epochs")
        != candidate_schedule.get("stage2_epochs")
        or arguments.get("batch_size") != candidate_schedule.get("batch_size")
        or arguments.get("gradient_accumulation_steps")
        != candidate_schedule.get("gradient_accumulation_steps")
        or stages.get("executed_optimizer_steps_total") != total_steps
        or stages.get("planned_optimizer_steps_total") != total_steps
        or total_steps
        != candidate_schedule.get("executed_optimizer_steps_total")
        or total_steps != candidate_schedule.get("planned_optimizer_steps_total")
    ):
        raise ValueError("v6 no-K 고정 full-epoch update budget 계약이 다릅니다.")


def _load_json(path: Path, label: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{label}는 symlink가 아닌 일반 파일이어야 합니다.")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exception:
        raise ValueError(f"{label} JSON을 읽을 수 없습니다.") from exception
    return _mapping(value, label)


def _mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping) or not all(isinstance(key, str) for key in value):
        raise ValueError(f"{label}는 JSON 객체여야 합니다.")
    return dict(value)


def _required_seed(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value not in REQUIRED_SEEDS:
        raise ValueError(f"{label}는 고정 seed {list(REQUIRED_SEEDS)} 중 하나여야 합니다.")
    return value


def _integer(value: object, label: str, *, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{label} 정수 값이 올바르지 않습니다.")
    return value


def _boolean(value: object, label: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{label} boolean 값이 올바르지 않습니다.")
    return value


def _safe_relative_path(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} 경로가 없습니다.")
    pure = PurePosixPath(value)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise ValueError(f"{label} 상대 경로가 올바르지 않습니다.")
    return Path(*pure.parts)


def _commitment_relative_path(
    commitment: Mapping[str, int | str], label: str
) -> Path:
    return _safe_relative_path(commitment.get("path"), label)


def _canonical_json(value: object) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    except (TypeError, ValueError) as exception:
        raise ValueError("v6 확증 계약이 canonical JSON이 아닙니다.") from exception
