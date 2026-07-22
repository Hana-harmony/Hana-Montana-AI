from __future__ import annotations

import importlib.util
import json
import os
import subprocess  # nosec B404 - 고정된 로컬 검증 스크립트만 실행한다.
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

SCRIPT = Path("scripts/train_kf_deberta_sentiment_v6_ablation.py")


def _subprocess_environment() -> dict[str, str]:
    """격리 실행 환경에서도 OpenMP가 공유 메모리를 요구하지 않게 고정한다."""
    return {**os.environ, "KMP_USE_SHM": "0", "OMP_NUM_THREADS": "1"}


@pytest.fixture(scope="module")
def module() -> ModuleType:
    scripts = str(Path("scripts").resolve())
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    name = "train_kf_deberta_sentiment_v6_ablation"
    existing = sys.modules.get(name)
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    assert spec is not None and spec.loader is not None
    loaded = importlib.util.module_from_spec(spec)
    sys.modules[name] = loaded
    spec.loader.exec_module(loaded)
    return loaded


@pytest.fixture(scope="module")
def validation_reports() -> dict[str, dict[str, Any]]:
    reports: dict[str, dict[str, Any]] = {}
    for mode in ("NO_K", "NEWS_ONLY", "DISCLOSURE_ONLY", "FULL", "ZERO_K_EXPOSURE"):
        completed = subprocess.run(  # noqa: S603  # nosec B603
            [
                sys.executable,
                str(SCRIPT),
                "--mode",
                mode,
                "--seed",
                "17",
                "--validate-only",
            ],
            check=True,
            capture_output=True,
            env=_subprocess_environment(),
            text=True,
            timeout=120,
        )
        reports[mode] = json.loads(completed.stdout)
    return reports


def test_runner_uses_v6_modeling_for_every_data_mode(module: ModuleType) -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert tuple(mode.value for mode in module.AblationMode) == (
        "NO_K",
        "NEWS_ONLY",
        "DISCLOSURE_ONLY",
        "FULL",
    )
    assert "v6.train_stage(" in source
    assert "v6.fit_calibration(" in source
    assert "AutoModelForSequenceClassification" not in source
    assert "SentimentTrainer" not in source
    assert module.MODEL_SEEDS == (17, 42, 73)


def test_recipe_commitment_excludes_only_model_seed(module: ModuleType) -> None:
    commitments = []
    for mode in module.AblationMode:
        for seed in module.MODEL_SEEDS:
            args = module.parser().parse_args(
                ["--mode", mode.value, "--seed", str(seed), "--validate-only"]
            )
            commitments.append(module._recipe_commitment(args))

    assert len(set(commitments)) == 1
    assert len(commitments[0]) == 64


def test_compute_matched_schedule_cannot_be_overridden(module: ModuleType) -> None:
    args = module.parser().parse_args(["--mode", "NO_K", "--seed", "17", "--stage1-epochs", "3"])

    with pytest.raises(SystemExit, match="4114/452"):
        module._validate_compute_matched_schedule(args)


def test_stage1_stable_cycle_is_permutation_invariant(module: ModuleType) -> None:
    rows = [
        {
            "text": f"공개 문장 {index}",
            "label": label,
            "source_type": "NEWS",
            "sample_weight": 1.0,
            "dataset": "PUBLIC_TRAIN",
        }
        for index, label in enumerate(module.v6.LABEL_ORDER)
    ]

    first = module._stage1_compute_matched_exposures(rows)
    reversed_plan = module._stage1_compute_matched_exposures(list(reversed(rows)))

    assert first.audit == reversed_plan.audit
    assert first.audit["target_exposure_count_per_epoch"] == 32_907
    assert first.audit["minimum_exposures_per_unique_row"] == 10_969
    assert first.audit["maximum_exposures_per_unique_row"] == 10_969
    assert (
        first.audit["exposure_sequence_commitment"]
        == reversed_plan.audit["exposure_sequence_commitment"]
    )


def test_no_k_validate_only_has_real_fixed_partitions(
    module: ModuleType,
    validation_reports: dict[str, dict[str, Any]],
) -> None:
    report = validation_reports["NO_K"]

    assert report["status"] == "VALIDATED_WITHOUT_TRAINING"
    assert report["partition_count"]["TRAIN"] == 7_413
    assert report["partition_count"]["STAGE1_EXPOSURES_PER_EPOCH"] == 32_907
    assert report["partition_count"]["K_GOLD_REFINEMENT"] == 0
    assert report["partition_count"]["GOLD_REFINEMENT"] == 1_794
    assert report["stage2_data_intervention"]["status"] == module.STAGE2_TRAINED
    assert report["compute_matching"]["stage1"]["source_unique_row_count"] == 7_413
    assert report["compute_matching"]["stage1"]["minimum_exposures_per_unique_row"] == 4
    assert report["compute_matching"]["stage1"]["maximum_exposures_per_unique_row"] == 5
    assert report["compute_matching"]["stage2"]["public_control_label_distribution"] == {
        "NEGATIVE": 598,
        "NEUTRAL": 598,
        "POSITIVE": 598,
    }
    assert report["compute_matching"]["stage2"]["no_k_training_exposure"] is True
    assert (
        report["compute_matching"]["optimizer_step_contract"]["candidate_steps_exactly_matched"]
        is True
    )
    assert report["final_holm_baseline_contract"]["no_k_role"] == (
        "NO_K_TRAIN_ROWS_WITH_SHARED_K_DEV"
    )
    assert report["estimand_contract"]["common_k_development_labels_used"] is True
    assert report["partition_roles"]["SELECTION"] == ("ADAPTIVE_DEVELOPMENT_SELECTION")
    assert report["public_test_opened"] is False
    assert report["confirmatory_labels_opened"] is False


def test_zero_k_exposure_is_public_only_validation_diagnostic(
    validation_reports: dict[str, dict[str, Any]],
) -> None:
    report = validation_reports["ZERO_K_EXPOSURE"]

    assert report["holm_eligible"] is False
    assert report["training_implemented"] is False
    assert report["k_training_inputs_opened"] is False
    assert report["k_development_inputs_opened"] is False
    assert report["development_contract"]["source"] == "PUBLIC_VALIDATION_ONLY"
    assert report["development_contract"]["k_development_rows"] == 0
    assert report["separation_from_holm"]["holm_no_k_role"] == ("NO_K_TRAIN_ROWS_WITH_SHARED_K_DEV")


def test_zero_k_exposure_rejects_training_execution() -> None:
    completed = subprocess.run(  # noqa: S603  # nosec B603
        [sys.executable, str(SCRIPT), "--mode", "ZERO_K_EXPOSURE", "--seed", "17"],
        check=False,
        capture_output=True,
        env=_subprocess_environment(),
        text=True,
        timeout=30,
    )

    assert completed.returncode != 0
    assert "validation-only" in completed.stderr


def test_all_holm_modes_are_exactly_compute_matched(
    module: ModuleType,
    validation_reports: dict[str, dict[str, Any]],
) -> None:
    expected = {
        "NO_K": (7_413, 4, 5, 0, 1_794),
        "NEWS_ONLY": (28_107, 1, 2, 1_194, 600),
        "DISCLOSURE_ONLY": (12_213, 2, 3, 600, 1_194),
        "FULL": (32_907, 1, 1, 1_794, 0),
    }
    for mode, (
        unique_rows,
        minimum_exposure,
        maximum_exposure,
        k_gold_rows,
        public_control_rows,
    ) in expected.items():
        report = validation_reports[mode]
        stage1 = report["compute_matching"]["stage1"]
        stage2 = report["compute_matching"]["stage2"]
        steps = report["compute_matching"]["optimizer_step_contract"]
        assert stage1["source_unique_row_count"] == unique_rows
        assert stage1["target_exposure_count_per_epoch"] == 32_907
        assert stage1["minimum_exposures_per_unique_row"] == minimum_exposure
        assert stage1["maximum_exposures_per_unique_row"] == maximum_exposure
        assert stage1["exposure_rows_commitment"]["row_count"] == 32_907
        assert stage2["row_count"] == 1_794
        assert stage2["eligible_k_gold_row_count"] == k_gold_rows
        assert stage2["public_control_row_count"] == public_control_rows
        assert stage2["public_control_label_distribution"] == {
            label: public_control_rows // 3 for label in module.v6.LABEL_ORDER
        }
        assert stage2["rows_commitment"]["row_count"] == 1_794
        assert steps["stage1"]["optimizer_steps"] == 4_114
        assert steps["stage2"]["optimizer_steps"] == 452
        assert steps["candidate_steps_exactly_matched"] is True
        assert report["estimand_contract"] == module._estimand_contract()
        assert report["statistical_analysis_plan"]["zero_k_exposure_holm_eligible"] is False


def _compute_matching_fixture(module: ModuleType, mode: Any) -> dict[str, Any]:
    unique = {
        module.AblationMode.NO_K: 7_413,
        module.AblationMode.NEWS_ONLY: 28_107,
        module.AblationMode.DISCLOSURE_ONLY: 12_213,
        module.AblationMode.FULL: 32_907,
    }[mode]
    controls = module.PUBLIC_CONTROL_PER_LABEL[mode] * 3
    return {
        "schema_version": "k-fnspid-compute-matched-training-plan/v1",
        "stage1": {
            "source_unique_row_count": unique,
            "target_exposure_count_per_epoch": 32_907,
            "minimum_exposures_per_unique_row": 32_907 // unique,
            "maximum_exposures_per_unique_row": -(-32_907 // unique),
            "all_source_rows_exposed": True,
        },
        "stage2": {
            "row_count": 1_794,
            "eligible_k_gold_row_count": module.EXPECTED_K_GOLD_ROWS[mode],
            "public_control_row_count": controls,
            "no_k_training_exposure": mode is module.AblationMode.NO_K,
        },
        "optimizer_step_contract": {
            "candidate_steps_exactly_matched": True,
            "stage1": {"optimizer_steps": 4_114},
            "stage2": {"optimizer_steps": 452},
        },
    }


def _residual_provenance(module: ModuleType, mode: Any) -> dict[str, Any]:
    membership = {
        "NEWS_TARGETED": mode in {module.AblationMode.NEWS_ONLY, module.AblationMode.FULL},
        "DISCLOSURE_TARGETED": mode
        in {module.AblationMode.DISCLOSURE_ONLY, module.AblationMode.FULL},
    }
    return {
        "residual_optimizer_membership": membership,
        "inactive_residual_bitwise_preserved": True,
        "inactive_residual_exact_zero_before": True,
        "inactive_residual_exact_zero_after": True,
        "inactive_residual_state_sha256_before": "d" * 64,
        "inactive_residual_state_sha256_after": "d" * 64,
    }


def _write_candidate(
    module: ModuleType,
    root: Path,
    report_dir: Path,
    *,
    mode: Any,
    seed: int,
    weakest: float,
    overall: float,
) -> None:
    compute_matching = _compute_matching_fixture(module, mode)
    artifact = root / f"seed{seed}"
    (artifact / "adapter").mkdir(parents=True)
    for relative in (
        "adapter/adapter_config.json",
        "adapter/adapter_model.safetensors",
        module.v6.HEAD_ARTIFACT_FILENAME,
        "tokenizer.json",
        "tokenizer_config.json",
    ):
        path = artifact / relative
        path.write_text(f"seed={seed};path={relative}\n", encoding="utf-8")
    metadata = {
        "schema_version": module.ARTIFACT_SCHEMA_VERSION,
        "artifact_role": module.ARTIFACT_ROLE,
        "model_family": module.MODEL_FAMILY,
        "ablation_mode": mode.value,
        "seed": seed,
        "compute_matching": compute_matching,
        "estimand_contract": module._estimand_contract(),
        "statistical_analysis_plan": module._statistical_analysis_plan_contract(),
    }
    (artifact / "hannah_metadata.json").write_text(
        json.dumps(metadata),
        encoding="utf-8",
    )
    records = module.v6._artifact_records(artifact)
    manifest = {
        "schema_version": module.v6.ARTIFACT_MANIFEST_SCHEMA_VERSION,
        "status": "ATOMIC_COMPLETE",
        "artifact_files": records,
        "safe_serialization_only": True,
        "symlinks_allowed": False,
        "overwrite_allowed": False,
    }
    (artifact / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    report = {
        "schema_version": module.SCHEMA_VERSION,
        "status": "TRAINING_COMPLETE_RESEARCH_ONLY",
        "artifact_role": module.ARTIFACT_ROLE,
        "model_family": module.MODEL_FAMILY,
        "ablation_mode": mode.value,
        "seed": seed,
        "public_test_opened": False,
        "confirmatory_labels_opened": False,
        "test": {"sample_count": 0, "status": "SEALED_AND_NOT_LOADED"},
        "candidate_selection": {
            "fit_partition": module.v6.ADAPTIVE_SELECTION_ROLE,
            "independent_generalization_evidence": False,
            "confirmatory_is_only_independent_generalization_evidence": True,
        },
        "stage2_data_intervention": {
            "status": module.STAGE2_TRAINED,
            "stage2_skipped": False,
            "total_refinement_rows": 1_794,
            "candidate_optimizer_steps_matched": True,
        },
        "selection_score": {
            "weakest_source_domain_macro_f1": weakest,
            "overall_macro_f1": overall,
        },
        "artifact_directory": module._display_path(artifact),
        "artifact_files": records,
        "prepared_partition_commitments": {"TRAIN": {"row_count": 10, "sha256": "a" * 64}},
        "input_artifacts": {"train": {"bytes": 1, "sha256": "b" * 64}},
        "architecture": {"same": True},
        "training_arguments": {
            "model_seed": seed,
            "batch_size": 8,
            "stage1_epochs": 2,
            "stage2_epochs": 4,
            "gradient_accumulation_steps": 2,
        },
        "compute_matching": compute_matching,
        "estimand_contract": module._estimand_contract(),
        "statistical_analysis_plan": module._statistical_analysis_plan_contract(),
        "stages": {
            "stage1": {
                "optimizer_steps": 4_114,
                "planned_optimizer_steps": 4_114,
                "history": [{"epoch": 1}, {"epoch": 2}],
                "active_parameter_provenance": _residual_provenance(module, mode),
            },
            "stage2": {
                "optimizer_steps": 452,
                "planned_optimizer_steps": 452,
                "history": [
                    {"epoch": 1},
                    {"epoch": 2},
                    {"epoch": 3},
                    {"epoch": 4},
                ],
                "active_parameter_provenance": _residual_provenance(module, mode),
            },
            "executed_optimizer_steps_total": 4_566,
            "planned_optimizer_steps_total": 4_566,
            "fixed_full_epoch_budget": True,
        },
        "recipe_commitment_sha256": "c" * 64,
        "base_source_kind": "PINNED_RAW",
        "base_source": {"revision": "fixed"},
        "final_holm_baseline_contract": {
            "no_k_role": module.FINAL_HOLM_NO_K_ROLE,
            "estimand_id": module.ESTIMAND_ID,
            "required_model_family": module.MODEL_FAMILY,
            "required_seed_runs": list(module.MODEL_SEEDS),
            "legacy_v5_no_k_role": module.LEGACY_V5_NO_K_ROLE,
            "legacy_v5_no_k_final_holm_eligible": False,
            "zero_k_exposure_holm_eligible": False,
        },
    }
    slug = module._mode_slug(mode)
    (report_dir / f"kf-deberta-sentiment-v6-{slug}-seed{seed}.json").write_text(
        json.dumps(report),
        encoding="utf-8",
    )


def _write_full_source_candidate(
    module: ModuleType,
    root: Path,
    *,
    protocol: dict[str, Any],
    seed: int,
) -> tuple[Path, Path]:
    artifact = root / "candidate-artifact"
    (artifact / "adapter").mkdir(parents=True)
    for relative in (
        "adapter/adapter_config.json",
        "adapter/adapter_model.safetensors",
        module.v6.HEAD_ARTIFACT_FILENAME,
        "tokenizer.json",
        "tokenizer_config.json",
    ):
        path = artifact / relative
        path.write_text(f"seed={seed};path={relative}\n", encoding="utf-8")
    runtime = {"schema_version": module.v6.RUNTIME_LOADER_SCHEMA_VERSION}
    metadata = {
        "schema_version": module.v6.ARTIFACT_SCHEMA_VERSION,
        "base_source_kind": protocol["base_source_kind"],
        "prepared_partition_commitments": protocol["prepared_partition_commitments"],
        "selected_stage": "STAGE2_GOLD_CLEAN_HEADS_ONLY",
        "runtime_loader_contract": runtime,
    }
    (artifact / "hannah_metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    records = module.v6._artifact_records(artifact)
    manifest = {
        "schema_version": module.v6.ARTIFACT_MANIFEST_SCHEMA_VERSION,
        "status": "ATOMIC_COMPLETE",
        "artifact_files": records,
        "safe_serialization_only": True,
        "symlinks_allowed": False,
        "overwrite_allowed": False,
    }
    (artifact / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    arguments = dict(protocol["training_arguments"])
    arguments["seed"] = arguments.pop("model_seed")
    max_length = arguments.pop("max_length")
    stages = {
        "stage1": {
            "optimizer_steps": 4_114,
            "planned_optimizer_steps": 4_114,
            "history": [{"epoch": 1}, {"epoch": 2}],
            "active_parameter_provenance": _residual_provenance(
                module, module.AblationMode.FULL
            ),
        },
        "stage2": {
            "optimizer_steps": 452,
            "planned_optimizer_steps": 452,
            "history": [{"epoch": index} for index in range(1, 5)],
            "active_parameter_provenance": _residual_provenance(
                module, module.AblationMode.FULL
            ),
        },
        "executed_optimizer_steps_total": 4_566,
        "planned_optimizer_steps_total": 4_566,
        "fixed_full_epoch_budget": True,
        "selected_checkpoint_lineage_global_step": 2_509,
    }
    candidate = {
        "schema_version": module.v6.TRAINING_SCHEMA_VERSION,
        "model_family": module.MODEL_FAMILY,
        "seed": seed,
        "max_length": max_length,
        "selected_stage": "STAGE2_GOLD_CLEAN_HEADS_ONLY",
        "architecture": module._candidate_architecture_contract(),
        "training_arguments": arguments,
        "prepared_partition_commitments": protocol["prepared_partition_commitments"],
        "input_artifacts": {
            "train_gold": protocol["input_artifacts"]["main_news_gold"]
        },
        "base_source_kind": protocol["base_source_kind"],
        "base_source": protocol["base_source"],
        "stage_selection": stages,
        "calibration": {"fit_partition": "CALIBRATION_ONLY"},
        "candidate_selection": {
            "fit_partition": module.v6.ADAPTIVE_SELECTION_ROLE,
            "primary_value": 0.64,
            "secondary_overall_macro_f1": 0.86,
            "metrics": {"OVERALL": {"macro_f1": 0.86}},
            "independent_generalization_evidence": False,
            "confirmatory_is_only_independent_generalization_evidence": True,
        },
        "production_cpu_roundtrip": {
            "status": "PASS",
            "device": "cpu",
            "logits_max_abs_error": 0.0,
            "probability_max_abs_error": 0.0,
            "exact_final_threshold_label_agreement": True,
        },
        "runtime_loader_contract": runtime,
        "training_code": {"v6_trainer": {"sha256": "e" * 64}},
        "dependency_artifacts": {},
        "artifact_files": records,
        "public_test_opened": False,
        "confirmatory_labels_opened": False,
        "test": {"sample_count": 0},
    }
    report = root / "candidate-report.json"
    report.write_text(json.dumps(candidate), encoding="utf-8")
    return artifact, report


def _full_reuse_fixture(
    module: ModuleType,
    tmp_path: Path,
    *,
    seed: int = 17,
) -> tuple[dict[str, Any], Path, Path, Path]:
    ablation_reports = tmp_path / "ablation-reports"
    ablation_artifacts = tmp_path / "ablation-artifacts"
    ablation_reports.mkdir()
    _write_candidate(
        module,
        ablation_artifacts,
        ablation_reports,
        mode=module.AblationMode.FULL,
        seed=seed,
        weakest=0.64,
        overall=0.86,
    )
    protocol_path = (
        ablation_reports / f"kf-deberta-sentiment-v6-full-seed{seed}.json"
    )
    protocol = json.loads(protocol_path.read_text(encoding="utf-8"))
    protocol["input_artifacts"] = {
        "main_news_gold": {"bytes": 7, "sha256": "b" * 64}
    }
    protocol["training_arguments"] = {
        "model_seed": seed,
        "data_selection_seed": 20260715,
        "max_length": 256,
        "stage1_epochs": 2,
        "stage2_epochs": 4,
        "batch_size": 8,
        "eval_batch_size": 16,
        "gradient_accumulation_steps": 2,
        "stage1_learning_rate": 0.00008,
        "stage2_learning_rate": 0.0004,
        "weight_decay": 0.01,
        "rdrop_alpha": 0.25,
        "gradient_checkpointing": True,
    }
    source_artifact, source_report = _write_full_source_candidate(
        module,
        tmp_path / "source",
        protocol=protocol,
        seed=seed,
    )
    receipt_path = tmp_path / "receipt.json"
    receipt = module.build_full_reuse_receipt(
        protocol=protocol,
        source_report_path=source_report,
        source_artifact_dir=source_artifact,
        report_path=receipt_path,
        seed=seed,
    )
    return receipt, receipt_path, source_report, source_artifact


def test_full_reuse_receipt_verifies_exact_source_without_duplicate_artifact(
    module: ModuleType,
    tmp_path: Path,
) -> None:
    receipt, receipt_path, _, source_artifact = _full_reuse_fixture(module, tmp_path)

    score = module._validate_candidate_report(
        receipt,
        mode=module.AblationMode.FULL,
        seed=17,
        artifact_dir=tmp_path / "unused-ablation-artifact",
    )

    assert score == pytest.approx((0.64, 0.86))
    assert receipt_path.is_file()
    assert not (tmp_path / "unused-ablation-artifact").exists()
    assert module._effective_artifact_directory(
        receipt, tmp_path / "unused"
    ).resolve() == source_artifact.resolve()
    assert receipt["artifact_reuse"]["training_compute_avoided"] is True
    assert (
        receipt["artifact_reuse"]["comparison_contract"][
            "stable_order_plan_reexecuted"
        ]
        is False
    )


def test_full_reuse_receipt_fails_closed_after_source_artifact_tamper(
    module: ModuleType,
    tmp_path: Path,
) -> None:
    receipt, _, _, source_artifact = _full_reuse_fixture(module, tmp_path)
    (source_artifact / "tokenizer_config.json").write_text("tampered\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="hash"):
        module._validate_candidate_report(
            receipt,
            mode=module.AblationMode.FULL,
            seed=17,
            artifact_dir=tmp_path / "unused",
        )


def test_full_reuse_receipt_fails_closed_after_source_report_tamper(
    module: ModuleType,
    tmp_path: Path,
) -> None:
    receipt, _, source_report, _ = _full_reuse_fixture(module, tmp_path)
    candidate = json.loads(source_report.read_text(encoding="utf-8"))
    candidate["seed"] = 42
    source_report.write_text(json.dumps(candidate), encoding="utf-8")

    with pytest.raises(RuntimeError, match="report hash"):
        module._validate_candidate_report(
            receipt,
            mode=module.AblationMode.FULL,
            seed=17,
            artifact_dir=tmp_path / "unused",
        )


def test_three_seed_aggregate_ranks_weakest_domain_then_overall(
    module: ModuleType,
    tmp_path: Path,
) -> None:
    mode = module.AblationMode.NO_K
    reports = tmp_path / "reports"
    artifacts = tmp_path / "artifacts"
    reports.mkdir()
    # seed 42는 overall이 높지만 weakest-domain이 낮아 선택되면 안 된다.
    for seed, weakest, overall in (
        (17, 0.62, 0.70),
        (42, 0.61, 0.90),
        (73, 0.62, 0.72),
    ):
        _write_candidate(
            module,
            artifacts,
            reports,
            mode=mode,
            seed=seed,
            weakest=weakest,
            overall=overall,
        )
    selection_path = tmp_path / "aggregate/selection.json"
    winner_path = tmp_path / "aggregate/winner.json"

    result = module.aggregate_mode_runs(
        mode=mode,
        report_dir=reports,
        artifact_root=artifacts,
        selection_report_path=selection_path,
        winner_manifest_path=winner_path,
        validate_only=False,
    )

    assert result["status"] == "AGGREGATION_WRITTEN"
    assert result["selected_seed"] == 73
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    winner = json.loads(winner_path.read_text(encoding="utf-8"))
    assert selection["fixed_model_seeds"] == [17, 42, 73]
    assert selection["independent_generalization_evidence"] is False
    assert winner["selected_seed"] == 73
    assert winner["deployment_eligible"] is False
    assert winner["final_holm_no_k_role"] == module.FINAL_HOLM_NO_K_ROLE
    assert winner["legacy_v5_no_k_final_holm_eligible"] is False


def test_aggregate_file_record_uses_project_relative_path(module: ModuleType) -> None:
    record = module._regular_file_record(SCRIPT)

    assert record["path"] == SCRIPT.as_posix()


def test_aggregate_fails_closed_when_stage2_contract_is_tampered(
    module: ModuleType,
    tmp_path: Path,
) -> None:
    mode = module.AblationMode.NO_K
    reports = tmp_path / "reports"
    artifacts = tmp_path / "artifacts"
    reports.mkdir()
    for seed in module.MODEL_SEEDS:
        _write_candidate(
            module,
            artifacts,
            reports,
            mode=mode,
            seed=seed,
            weakest=0.6,
            overall=0.7,
        )
    path = reports / "kf-deberta-sentiment-v6-no-k-seed42.json"
    report = json.loads(path.read_text(encoding="utf-8"))
    report["stage2_data_intervention"]["status"] = "SKIPPED_NO_ELIGIBLE_GOLD"
    path.write_text(json.dumps(report), encoding="utf-8")

    with pytest.raises(RuntimeError, match="Stage 2"):
        module.aggregate_mode_runs(
            mode=mode,
            report_dir=reports,
            artifact_root=artifacts,
            selection_report_path=tmp_path / "selection.json",
            winner_manifest_path=tmp_path / "winner.json",
            validate_only=True,
        )


def test_matrix_aggregate_uses_all_four_modes_and_matched_seed_deltas(
    module: ModuleType,
    tmp_path: Path,
) -> None:
    report_root = tmp_path / "reports"
    artifact_root = tmp_path / "artifacts"
    offsets = {
        module.AblationMode.NO_K: 0.00,
        module.AblationMode.NEWS_ONLY: 0.04,
        module.AblationMode.DISCLOSURE_ONLY: 0.02,
        module.AblationMode.FULL: 0.08,
    }
    for mode, offset in offsets.items():
        slug = module._mode_slug(mode)
        mode_reports = report_root / slug
        mode_artifacts = artifact_root / slug
        mode_reports.mkdir(parents=True)
        for seed, base_score in zip(module.MODEL_SEEDS, (0.50, 0.52, 0.54), strict=True):
            _write_candidate(
                module,
                mode_artifacts,
                mode_reports,
                mode=mode,
                seed=seed,
                weakest=base_score + offset,
                overall=base_score + 0.10 + offset,
            )
    matrix_path = tmp_path / "matrix/result.json"

    result = module.aggregate_ablation_matrix(
        report_root=report_root,
        artifact_root=artifact_root,
        matrix_report_path=matrix_path,
        validate_only=False,
    )

    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    assert result["status"] == "MATRIX_WRITTEN"
    assert matrix["modes"] == [
        "NO_K",
        "NEWS_ONLY",
        "DISCLOSURE_ONLY",
        "FULL",
    ]
    assert matrix["fixed_model_seeds"] == [17, 42, 73]
    assert matrix["aggregation_unit"] == "matched_model_seed"
    assert matrix["paired_contrasts_vs_no_k"]["FULL"][
        "mean_weakest_domain_macro_f1_delta"
    ] == pytest.approx(0.08)
    assert (
        matrix["mode_aggregates"]["NO_K"]["stage2_data_intervention"]["status"]
        == module.STAGE2_TRAINED
    )
    assert (
        matrix["mode_aggregates"]["NO_K"]["stage1_compute_matching"][
            "target_exposure_count_per_epoch"
        ]
        == 32_907
    )
    assert (
        matrix["mode_aggregates"]["NO_K"]["stage2_compute_matching"]["public_control_row_count"]
        == 1_794
    )
    assert matrix["estimand_contract"]["estimand_id"] == module.ESTIMAND_ID
    assert matrix["independent_generalization_evidence"] is False
    assert matrix["final_holm_baseline_contract"] == {
        "no_k_role": module.FINAL_HOLM_NO_K_ROLE,
        "estimand_id": module.ESTIMAND_ID,
        "required_model_family": module.MODEL_FAMILY,
        "required_seed_runs": [17, 42, 73],
        "legacy_v5_no_k_role": module.LEGACY_V5_NO_K_ROLE,
        "legacy_v5_no_k_final_holm_eligible": False,
        "zero_k_exposure_holm_eligible": False,
    }
