from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from hannah_montana_ai.services.sentiment_artifact_contract import (
    MODEL_FAMILY,
    TRAINING_SCHEMA_VERSION,
)
from hannah_montana_ai.training.sentiment_evaluation_plan import (
    canonical_statistical_analysis_plan,
)
from hannah_montana_ai.training.sentiment_v6_evaluation_contract import (
    CONFIRMATORY_BASELINES,
    LEGACY_V5_NO_K_MODEL_NAME,
    V6_CANDIDATE_MODEL_NAME,
    _validate_no_k_fixed_budget,
    canonical_candidate_matching_contract,
    canonical_v6_statistical_analysis_plan,
    validate_v6_confirmatory_baseline_commitments,
    validate_v6_statistical_analysis_plan,
)


def _no_k_stage_report() -> dict[str, object]:
    provenance = {
        "residual_optimizer_membership": {
            "NEWS_TARGETED": False,
            "DISCLOSURE_TARGETED": False,
        },
        "inactive_residual_bitwise_preserved": True,
        "inactive_residual_exact_zero_before": True,
        "inactive_residual_exact_zero_after": True,
        "inactive_residual_state_sha256_before": "d" * 64,
        "inactive_residual_state_sha256_after": "d" * 64,
    }
    return {
        "stages": {
            "stage1": {
                "optimizer_steps": 4_114,
                "planned_optimizer_steps": 4_114,
                "history": [{"epoch": 1}, {"epoch": 2}],
                "active_parameter_provenance": provenance,
            },
            "stage2": {
                "optimizer_steps": 452,
                "planned_optimizer_steps": 452,
                "history": [{"epoch": index} for index in range(1, 5)],
                "active_parameter_provenance": provenance,
            },
            "executed_optimizer_steps_total": 4_566,
            "planned_optimizer_steps_total": 4_566,
            "fixed_full_epoch_budget": True,
        }
    }


def _no_k_arguments() -> dict[str, object]:
    return {
        "stage1_epochs": 2,
        "stage2_epochs": 4,
        "batch_size": 8,
        "gradient_accumulation_steps": 2,
    }


def _no_k_candidate_schedule() -> dict[str, object]:
    return {
        **_no_k_arguments(),
        "stage1_optimizer_steps": 4_114,
        "stage2_optimizer_steps": 452,
        "executed_optimizer_steps_total": 4_566,
        "planned_optimizer_steps_total": 4_566,
    }


def _candidate_report() -> dict[str, object]:
    return {
        "schema_version": TRAINING_SCHEMA_VERSION,
        "max_length": 256,
        "public_test_opened": False,
        "confirmatory_labels_opened": False,
        "candidate_selection": {
            "public_test_used": False,
            "confirmatory_used": False,
            "independent_generalization_evidence": False,
        },
        "training_arguments": {
            "data_selection_seed": 20_260_715,
            "stage1_epochs": 2,
            "stage2_epochs": 4,
            "batch_size": 8,
            "eval_batch_size": 16,
            "gradient_accumulation_steps": 2,
            "gradient_checkpointing": False,
        },
        "stage_selection": {
            "stage1": {
                "optimizer_steps": 120,
                "planned_optimizer_steps": 120,
                "history": [{"epoch": 1}, {"epoch": 2}],
            },
            "stage2": {
                "optimizer_steps": 40,
                "planned_optimizer_steps": 40,
                "history": [
                    {"epoch": 1},
                    {"epoch": 2},
                    {"epoch": 3},
                    {"epoch": 4},
                ],
            },
            "executed_optimizer_steps_total": 160,
            "planned_optimizer_steps_total": 160,
            "fixed_full_epoch_budget": True,
        },
        "prepared_partition_commitments": {
            "TRAIN": {"sha256": "a" * 64},
            "CHECKPOINT": {"sha256": "b" * 64},
        },
        "input_artifacts": {"public_train": {"sha256": "c" * 64}},
    }


def test_v6_sap_is_exactly_eight_v6_candidate_hypotheses() -> None:
    plan = validate_v6_statistical_analysis_plan(
        canonical_v6_statistical_analysis_plan()
    )
    hypotheses = plan["holm_hypotheses"]
    assert len(hypotheses) == 8
    assert {row["candidate_model"] for row in hypotheses} == {
        V6_CANDIDATE_MODEL_NAME
    }
    assert {row["baseline_model"] for row in hypotheses} == set(
        CONFIRMATORY_BASELINES
    )
    assert LEGACY_V5_NO_K_MODEL_NAME not in {
        row["baseline_model"] for row in hypotheses
    }


def test_v6_sap_rejects_v5_plan() -> None:
    with pytest.raises(ValueError, match="v6 statistical_analysis_plan"):
        validate_v6_statistical_analysis_plan(canonical_statistical_analysis_plan())


def test_candidate_matching_contract_locks_real_update_count() -> None:
    contract = canonical_candidate_matching_contract(_candidate_report())
    assert contract["candidate_model_family"] == MODEL_FAMILY
    assert contract["update_schedule"]["executed_optimizer_steps_total"] == 160

    altered = deepcopy(_candidate_report())
    altered["stage_selection"]["executed_optimizer_steps_total"] = 159
    with pytest.raises(ValueError, match="고정 full-epoch optimizer step"):
        canonical_candidate_matching_contract(altered)


def test_no_k_budget_requires_candidate_matched_stage2_and_zero_residuals() -> None:
    report = _no_k_stage_report()
    _validate_no_k_fixed_budget(
        report,
        _no_k_arguments(),
        _no_k_candidate_schedule(),
    )

    altered = deepcopy(report)
    altered["stages"]["stage2"]["optimizer_steps"] = 0
    altered["stages"]["stage2"]["planned_optimizer_steps"] = 0
    altered["stages"]["stage2"]["history"] = []
    with pytest.raises(ValueError, match="stage2"):
        _validate_no_k_fixed_budget(
            altered,
            _no_k_arguments(),
            _no_k_candidate_schedule(),
        )

    altered = deepcopy(report)
    altered["stages"]["stage1"]["active_parameter_provenance"][
        "residual_optimizer_membership"
    ]["NEWS_TARGETED"] = True
    with pytest.raises(ValueError, match="exact-zero residual"):
        _validate_no_k_fixed_budget(
            altered,
            _no_k_arguments(),
            _no_k_candidate_schedule(),
        )


def test_v6_baseline_contract_rejects_v5_payload_before_file_access(
    tmp_path: Path,
) -> None:
    legacy = {
        "schema_version": "sentiment-confirmatory-baseline-commitments/v1",
        "confirmatory_labels_used": False,
        "public_test_labels_used": False,
        "baselines": {},
    }
    with pytest.raises(ValueError, match="v6 baseline lock 계약"):
        validate_v6_confirmatory_baseline_commitments(
            legacy,
            tmp_path,
            candidate_training_report=_candidate_report(),
        )
