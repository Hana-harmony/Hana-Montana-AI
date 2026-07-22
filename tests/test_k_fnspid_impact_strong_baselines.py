from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

import pytest

from scripts import evaluate_k_fnspid_impact_strong_baselines as evaluator
from scripts import verify_k_fnspid_impact_baseline_artifact as verifier
from scripts.train_k_fnspid_transformer import (
    MODEL_PRESETS,
    _validate_comparison_initial_adapter,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_strong_baseline_revisions_and_roles_are_locked() -> None:
    kr_finbert = MODEL_PRESETS["KR_FINBERT_SC"]
    klue_large = MODEL_PRESETS["KLUE_ROBERTA_LARGE"]

    assert kr_finbert.comparison_only is True
    assert kr_finbert.local_files_only is True
    assert kr_finbert.ignore_mismatched_sizes is True
    assert kr_finbert.lora_target_modules == ("query", "key", "value")
    assert klue_large.comparison_only is True
    assert klue_large.local_files_only is False
    assert klue_large.lora_target_modules == ("query", "key", "value")
    assert len(kr_finbert.revision) == 40
    assert len(klue_large.revision) == 40


def test_kr_finbert_safe_reference_matches_preset_revision() -> None:
    preset = MODEL_PRESETS["KR_FINBERT_SC"]
    root = PROJECT_ROOT / preset.model_id
    manifest = json.loads(
        (root / "raw_reference_manifest.json").read_text(encoding="utf-8")
    )

    assert manifest["base_model"] == "snunlp/KR-FinBert-SC"
    assert manifest["base_model_revision"] == preset.revision
    assert manifest["files_sha256"]["model.safetensors"] == (
        preset.model_safetensors_sha256
    )
    assert manifest["inference_contract"]["safe_serialization_only"] is True
    assert (root / "model.safetensors").is_file()


def test_comparison_presets_cannot_share_deployment_identity() -> None:
    deployment = MODEL_PRESETS["HANA_KF_DEBERTA"]
    for name in ("KR_FINBERT_SC", "KLUE_ROBERTA_LARGE"):
        comparison = MODEL_PRESETS[name]
        assert comparison.comparison_only is True
        assert comparison.model_id != deployment.model_id
        assert comparison.revision != deployment.revision


def test_strong_baseline_artifact_verifier_rejects_tampering(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(verifier, "PROJECT_ROOT", tmp_path)
    dataset = tmp_path / "data/k_fnspid/v4"
    artifact = tmp_path / "artifacts/impact/kr-finbert/news/seed17"
    predictions = tmp_path / "reports/predictions.jsonl"
    dataset.mkdir(parents=True)
    artifact.mkdir(parents=True)
    predictions.parent.mkdir(parents=True)
    manifest_path = dataset / "manifest.json"
    manifest_path.write_text('{"version":"v4"}\n', encoding="utf-8")
    adapter = artifact / "adapter_model.safetensors"
    adapter.write_bytes(b"verified-adapter")
    for name in (
        "adapter_config.json",
        "tokenizer.json",
        "tokenizer_config.json",
    ):
        (artifact / name).write_text("{}\n", encoding="utf-8")
    predictions.write_text('{"document_id":"1"}\n', encoding="utf-8")

    preset = MODEL_PRESETS["KR_FINBERT_SC"]
    report = {
        "schema_version": verifier.EXPECTED_SCHEMA,
        "model_preset": "KR_FINBERT_SC",
        "base_model": preset.model_id,
        "base_model_revision": preset.revision,
        "base_model_safetensors_sha256": preset.model_safetensors_sha256,
        "comparison_only": True,
        "source_type": None,
        "seed": 17,
        "max_length": 256,
        "training_hyperparameters": {
            "evaluation_only": False,
            "epochs_requested": 3,
            "effective_batch_size": 32,
            "learning_rate": 0.0002,
            "gradient_checkpointing": False,
            "lora": {
                "rank": 16,
                "alpha": 32,
                "dropout": 0.1,
                "initial_adapter_path": None,
            },
        },
        "training_objective": {
            "focal_gamma": 1.5,
            "ordinal_loss_weight": 0.30,
            "label_smoothing": 0.02,
        },
        "deployment_gate": {"decision": "RESEARCH_BASELINE_ONLY"},
        "dataset_dir": "data/k_fnspid/v4",
        "dataset_manifest": {"sha256": sha256(manifest_path.read_bytes()).hexdigest()},
        "artifact_dir": "artifacts/impact/kr-finbert/news/seed17",
        "artifact_files": {
            path.name: {
                "bytes": path.stat().st_size,
                "sha256": sha256(path.read_bytes()).hexdigest(),
            }
            for path in artifact.iterdir()
        },
        "test_predictions": {
            "path": "reports/predictions.jsonl",
            "bytes": predictions.stat().st_size,
            "sha256": sha256(predictions.read_bytes()).hexdigest(),
        },
    }

    verifier.validate_report(
        report,
        model_preset="KR_FINBERT_SC",
        source_type="SHARED",
        seed=17,
    )
    adapter.write_bytes(b"tampered")
    with pytest.raises(ValueError, match="크기가 다릅니다|SHA-256이 다릅니다"):
        verifier.validate_report(
            report,
            model_preset="KR_FINBERT_SC",
            source_type="SHARED",
            seed=17,
        )


def test_source_recipe_reuses_shared_adapter_in_same_artifact_namespace() -> None:
    report = {
        "artifact_dir": (
            "artifacts/impact/strong-baselines/kr-finbert_sc/news/seed73"
        ),
        "max_length": 256,
        "training_hyperparameters": {
            "evaluation_only": True,
            "epochs_requested": 3,
            "effective_batch_size": 64,
            "learning_rate": 0.0002,
            "gradient_checkpointing": False,
            "lora": {
                "rank": 16,
                "alpha": 32,
                "dropout": 0.1,
                "initial_adapter_path": (
                    "artifacts/impact/strong-baselines/kr-finbert_sc/shared/seed42"
                ),
            },
        },
        "training_objective": {
            "focal_gamma": 1.5,
            "ordinal_loss_weight": 0.30,
            "label_smoothing": 0.02,
        },
    }

    verifier._validate_recipe(
        report,
        model_preset="KR_FINBERT_SC",
        source_type="NEWS",
    )

    report["training_hyperparameters"]["lora"]["initial_adapter_path"] = (
        "artifacts/impact/strong-baselines/kr-finbert-sc/shared/seed42"
    )
    with pytest.raises(ValueError, match="LoRA recipe"):
        verifier._validate_recipe(
            report,
            model_preset="KR_FINBERT_SC",
            source_type="NEWS",
        )


def test_holm_gate_controls_four_comparison_family() -> None:
    raw_values = (0.01, 0.04, 0.03, 0.20)
    comparisons = [
        {
            "evaluation": {
                "mcnemar_exact": {"p_value": raw},
                "clustered_bootstrap": {
                    "macro_f1_difference": {"low": 0.001, "high": 0.01},
                    "quadratic_kappa_difference": {"low": 0.0, "high": 0.02},
                },
            }
        }
        for raw in raw_values
    ]

    evaluator._apply_holm_mcnemar(comparisons)

    adjusted = [item["holm_adjusted_mcnemar_p_value"] for item in comparisons]
    assert adjusted == pytest.approx([0.04, 0.09, 0.09, 0.20])
    assert comparisons[0]["strong_baseline_superiority_gate"]["passed"] is True
    assert all(
        item["strong_baseline_superiority_gate"]["passed"] is False
        for item in comparisons[1:]
    )


def test_baseline_storage_slug_matches_locked_runner_namespace() -> None:
    assert evaluator._baseline_model_slug("KR_FINBERT_SC") == "kr-finbert_sc"
    assert (
        evaluator._baseline_model_slug("KLUE_ROBERTA_LARGE")
        == "klue-roberta_large"
    )


def test_baseline_aggregate_rejects_wrong_model_revision(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(evaluator, "PROJECT_ROOT", tmp_path)
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    preset = MODEL_PRESETS["KR_FINBERT_SC"]
    report_paths: list[str] = []
    report_hashes: dict[str, str] = {}
    for seed in (17, 42, 73):
        display_path = f"reports/seed{seed}.json"
        path = tmp_path / display_path
        payload = {
            "schema_version": "k-fnspid-impact-strong-baseline-training/v1",
            "model_preset": "KR_FINBERT_SC",
            "base_model": preset.model_id,
            "base_model_revision": "0" * 40 if seed == 42 else preset.revision,
            "base_model_safetensors_sha256": preset.model_safetensors_sha256,
            "source_type": "NEWS",
            "seed": seed,
            "comparison_only": True,
        }
        path.write_text(json.dumps(payload), encoding="utf-8")
        report_paths.append(display_path)
        report_hashes[display_path] = sha256(path.read_bytes()).hexdigest()
    aggregate = {
        "schema_version": "k-fnspid-transformer-multiseed/v2",
        "source_type": "NEWS",
        "run_count": 3,
        "seeds": [17, 42, 73],
        "selection_protocol": "validation macro F1 only; TEST is excluded from selection",
        "selected_seed_by_validation": 42,
        "report_paths": report_paths,
        "report_sha256": report_hashes,
        "runs": [{"seed": seed} for seed in (17, 42, 73)],
    }

    with pytest.raises(ValueError, match="base_model_revision"):
        evaluator._validate_baseline_aggregate(
            aggregate,
            model_preset="KR_FINBERT_SC",
            source="NEWS",
        )


def test_source_transfer_requires_verified_shared_seed42(
    tmp_path: Path,
) -> None:
    preset = MODEL_PRESETS["KR_FINBERT_SC"]
    adapter = tmp_path / "shared-seed42"
    adapter.mkdir()
    weights = adapter / "adapter_model.safetensors"
    weights.write_bytes(b"news-seed42")
    metadata = {
        "schema_version": "k-fnspid-transformer-artifact/v1",
        "model_preset": "KR_FINBERT_SC",
        "base_model": preset.model_id,
        "base_model_revision": preset.revision,
        "comparison_only": True,
        "source_type": None,
        "seed": 42,
        "artifact_files": {
            weights.name: {
                "bytes": weights.stat().st_size,
                "sha256": sha256(weights.read_bytes()).hexdigest(),
            }
        },
    }
    (adapter / "hannah_metadata.json").write_text(
        json.dumps(metadata),
        encoding="utf-8",
    )

    _validate_comparison_initial_adapter(
        adapter,
        model_preset="KR_FINBERT_SC",
        preset=preset,
    )
    weights.write_bytes(b"tampered")
    with pytest.raises(SystemExit, match="크기가 다릅니다|SHA-256이 다릅니다"):
        _validate_comparison_initial_adapter(
            adapter,
            model_preset="KR_FINBERT_SC",
            preset=preset,
        )
