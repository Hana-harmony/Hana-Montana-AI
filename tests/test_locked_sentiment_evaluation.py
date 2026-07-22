from __future__ import annotations

import importlib.util
import json
import sys
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

from hannah_montana_ai.services.sentiment_runtime_parity import (
    base_encoder_evidence,
    build_cpu_serving_parity_evidence,
    build_runtime_parity_lock_commitment,
)
from hannah_montana_ai.training.sentiment_baseline_commitments import (
    baseline_commitments_sha256,
    build_confirmatory_baseline_commitments,
    directory_commitment,
    file_commitment,
)


def _module() -> ModuleType:
    path = Path("scripts/evaluate_locked_kf_deberta_sentiment.py")
    spec = importlib.util.spec_from_file_location("evaluate_locked_sentiment", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _file_manifest(path: Path) -> dict[str, int | str]:
    return {"bytes": path.stat().st_size, "sha256": _sha256(path)}


def _canonical_sha256(value: object) -> str:
    return sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _no_k_source_provenance() -> dict[str, dict[str, int | str]]:
    excluded = (
        "K_FNSPID_CODEX_GOLD",
        "K_FNSPID_NEWS_AUXILIARY_CODEX_GOLD",
        "K_FNSPID_DISCLOSURE_AUXILIARY_CODEX_GOLD",
        "K_FNSPID_RULE_SILVER",
        "K_FNSPID_DISCLOSURE_RULE_SILVER",
        "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE_NEWS",
        "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE_DISCLOSURE",
    )
    return {
        "PUBLIC_TRAIN": {"decision": "INCLUDED", "pre_dedup_selected_count": 7413},
        **{
            source: {"decision": "EXCLUDED", "pre_dedup_selected_count": 0}
            for source in excluded
        },
    }


def _reservation_commitment(
    root: Path,
    *,
    filename: str,
    partition: str,
    source_type: str,
) -> dict[str, Any]:
    path = root / "data/curation/k_fnspid_sentiment" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "schema_version": "k-fnspid-sentiment-review-row/v1",
            "partition": partition,
            "source_type": source_type,
            "review_status": "NEEDS_BLIND_REVIEW",
            "final_sentiment": "",
            "document_id": f"{source_type.casefold()}-{index}",
            "stock_code": f"{index:06d}",
            "text": f"문서 {index}",
        }
        for index in range(500)
    ]
    _write_jsonl(path, rows)
    item_ids = sorted(f"{row['document_id']}::{row['stock_code']}" for row in rows)
    source_records = sorted(
        (
            {
                "item_id": f"{row['document_id']}::{row['stock_code']}",
                "source_record_sha256": _canonical_sha256(row),
            }
            for row in rows
        ),
        key=lambda row: row["item_id"],
    )
    return {
        "path": str(path.relative_to(root)),
        "sha256": _sha256(path),
        "bytes": path.stat().st_size,
        "sample_count": len(rows),
        "partition": partition,
        "source_type": source_type,
        "item_id_set_sha256": _canonical_sha256(item_ids),
        "source_record_set_sha256": _canonical_sha256(source_records),
    }


def _candidate_lock_fixture(
    root: Path,
    *,
    test_used_for_selection: bool = False,
    gold_used_for_selection: bool = False,
    input_feature_version: str = "source-target-prefix-head-tail/v2",
) -> tuple[Path, Path]:
    module = _module()
    report_dir = root / "reports/candidates"
    artifact_dir = root / "artifacts/sentiment/locked"
    report_dir.mkdir(parents=True)
    artifact_dir.mkdir(parents=True)
    for filename in (
        "adapter_config.json",
        "adapter_model.safetensors",
        "tokenizer.json",
        "tokenizer_config.json",
    ):
        (artifact_dir / filename).write_bytes(f"artifact:{filename}".encode())
    source_manifest = {
        filename: _file_manifest(artifact_dir / filename)
        for filename in (
            "adapter_config.json",
            "adapter_model.safetensors",
            "tokenizer.json",
            "tokenizer_config.json",
        )
    }
    version = "hana-montana-test-candidate"
    logit_bias_by_domain = {
        "NEWS_UNTARGETED": [0.0, 0.0, 0.0],
        "NEWS_TARGETED": [-0.1, 0.2, -0.1],
        "DISCLOSURE_TARGETED": [0.0, 0.1, -0.1],
    }
    metadata = {
        "schema_version": "kf-deberta-sentiment-artifact/v2",
        "version": version,
        "base_model": "kakaobank/kf-deberta-base",
        "base_model_revision": "363b171d71443b0874b0bf9cea053eb5b1650633",
        "label_order": ["NEGATIVE", "NEUTRAL", "POSITIVE"],
        "max_length": 384,
        "input_feature_version": input_feature_version,
        "logit_bias_by_domain": logit_bias_by_domain,
        "artifact_files": source_manifest,
    }
    (artifact_dir / "hannah_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False), encoding="utf-8"
    )
    prepared_commitments = {
        name: {
            "row_count": 10_000 if name == "TRAIN" else 600,
            "sha256": _canonical_sha256({"partition": name}),
        }
        for name in (
            "TRAIN",
            "CHECKPOINT",
            "CALIBRATION",
            "SELECTION",
            "NEWS_CONFIRMATORY_RESERVATION",
            "DISCLOSURE_CONFIRMATORY_RESERVATION",
        )
    }
    report = {
        "schema_version": "kf-deberta-sentiment-training/v2",
        "version": version,
        "max_length": 384,
        "input_feature_version": input_feature_version,
        "logit_bias_by_domain": logit_bias_by_domain,
        "artifact_files": source_manifest,
        "dataset_revision": module.DATASET_REVISION,
        "public_dataset_revision": module.PUBLIC_DATASET_REVISION,
        "training_strategy": (
            "group-purged-three-way-dual-gold-target-swap-rdrop-hierarchical-upper6-lora/v5"
        ),
        "training_arguments": {"data_selection_seed": module.DATA_SELECTION_SEED},
        "base_model_provenance": {
            "repository": module.BASE_MODEL,
            "revision": module.BASE_MODEL_REVISION,
            "source_weight_filename": "pytorch_model.bin",
            "source_weights_format": "pytorch_model.bin",
            "source_weight_sha256": (
                "3cd6cd7811b3c9190e97cae7eb41571c2bc0076431baae7d41d449a8c1c18c6c"
            ),
            "deserialization": "torch_weights_only",
            "trust_remote_code": False,
            "weights_only": True,
        },
        "prepared_partition_commitments": prepared_commitments,
        "training_runtime": {
            "trainer_device": "cpu",
            "global_step": 100,
            "train_runtime": 10.0,
            "train_samples_per_second": 100.0,
            "train_steps_per_second": 10.0,
        },
        "candidate_selection": {
            "test_used_for_selection": test_used_for_selection,
            "operational_gold_used_for_selection": gold_used_for_selection,
            "sealed_test_evaluated": False,
        },
        "test": {
            "sample_count": 0,
            "status": "SEALED_UNTIL_CANDIDATE_LOCK",
        },
    }
    report_path = report_dir / "kf-deberta-sentiment-seed42.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
    locked_manifest = {
        filename: _file_manifest(artifact_dir / filename)
        for filename in (
            "adapter_config.json",
            "adapter_model.safetensors",
            "tokenizer.json",
            "tokenizer_config.json",
            "hannah_metadata.json",
        )
    }
    lock = {
        "schema_version": "sentiment-candidate-lock/v1",
        "locked_at": "2026-07-15T00:00:00+00:00",
        "selection_only": True,
        "public_test_evaluated_before_lock": False,
        "operational_sealed_gold_evaluated_before_lock": False,
        "external_git_commitment_required": True,
        "sealed_reservations": {
            "NEWS": _reservation_commitment(
                root,
                filename="confirmatory_sealed_test_review.jsonl",
                partition="CONFIRMATORY_SEALED_TEST_REVIEW",
                source_type="NEWS",
            ),
            "DISCLOSURE": _reservation_commitment(
                root,
                filename="disclosure_confirmatory_sealed_test_review.jsonl",
                partition="DISCLOSURE_CONFIRMATORY_SEALED_TEST_REVIEW",
                source_type="DISCLOSURE",
            ),
        },
        "winner": {
            "version": version,
            "report_path": "reports/candidates/kf-deberta-sentiment-seed42.json",
            "report_sha256": _sha256(report_path),
            "locked_artifact_dir": "artifacts/sentiment/locked",
            "artifact_files": locked_manifest,
            "data_selection_seed": module.DATA_SELECTION_SEED,
            "prepared_partition_commitments": prepared_commitments,
        },
    }
    codebook = root / "docs/datasets/k-fnspid-sentiment-codebook.md"
    news_report = root / "reports/k-fnspid-sentiment-dataset-report.json"
    disclosure_report = root / "reports/k-fnspid-disclosure-sentiment-dataset-report.json"
    sampling_report = (
        root
        / "reports/k-fnspid-sentiment-confirmatory-sealed-sampling-design-v2.json"
    )
    sampling_implementation = root / "src/hannah_montana_ai/training/sentiment_sampling.py"
    codebook.parent.mkdir(parents=True, exist_ok=True)
    codebook.write_text("codebook", encoding="utf-8")
    news_report.write_text("{}", encoding="utf-8")
    disclosure_report.write_text("{}", encoding="utf-8")
    sampling_report.write_text("{}", encoding="utf-8")
    sampling_implementation.parent.mkdir(parents=True, exist_ok=True)
    sampling_implementation.write_text("# sampling contract\n", encoding="utf-8")
    lock["dataset_provenance"] = {
        "codebook": {"path": str(codebook.relative_to(root)), **_file_manifest(codebook)},
        "sampling_implementation": {
            "path": str(sampling_implementation.relative_to(root)),
            **_file_manifest(sampling_implementation),
        },
        "dataset_reports": {
            "NEWS": {
                "path": str(news_report.relative_to(root)),
                **_file_manifest(news_report),
            },
            "DISCLOSURE": {
                "path": str(disclosure_report.relative_to(root)),
                **_file_manifest(disclosure_report),
            },
            "SAMPLING_DESIGN": {
                "path": str(sampling_report.relative_to(root)),
                **_file_manifest(sampling_report),
            },
        },
    }
    recipe_blobs: dict[str, dict[str, int | str]] = {}
    for name, relative_path in module.RECIPE_RELATIVE_PATHS:
        path = root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(f"# {name}\n", encoding="utf-8")
        recipe_blobs[name] = _provenance_record(path, root)
    lock["recipe"] = {
        "schema_version": "sentiment-candidate-recipe/v2",
        "training_script": recipe_blobs["candidate_trainer"]["path"],
        "training_script_sha256": recipe_blobs["candidate_trainer"]["sha256"],
        "auxiliary_training_gold_promoter": recipe_blobs[
            "historical_auxiliary_promoter"
        ]["path"],
        "auxiliary_training_gold_promoter_sha256": recipe_blobs[
            "historical_auxiliary_promoter"
        ]["sha256"],
        "blobs": recipe_blobs,
    }
    lock["statistical_analysis_plan"] = module.canonical_statistical_analysis_plan()
    baseline_commitments, runtime_parity = _baseline_and_parity_fixture(
        root,
        lock=lock,
        candidate_version=version,
        candidate_manifest_sha256=_canonical_sha256(locked_manifest),
    )
    lock["baseline_commitments"] = baseline_commitments
    lock["baseline_commitments_sha256"] = baseline_commitments_sha256(
        baseline_commitments
    )
    lock["runtime_parity"] = runtime_parity
    lock_path = root / "reports/sentiment-candidate-lock.json"
    lock_path.parent.mkdir(exist_ok=True)
    lock_path.write_text(json.dumps(lock, ensure_ascii=False), encoding="utf-8")
    return lock_path, artifact_dir


def _baseline_and_parity_fixture(
    root: Path,
    *,
    lock: dict[str, Any],
    candidate_version: str,
    candidate_manifest_sha256: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    tfidf = root / "models/tfidf.joblib"
    tfidf.parent.mkdir(parents=True, exist_ok=True)
    tfidf.write_bytes(b"tfidf")
    pre_k = root / "models/pre-k"
    pre_k.mkdir(parents=True)
    (pre_k / "adapter_model.safetensors").write_bytes(b"pre-k")
    (pre_k / "hannah_metadata.json").write_text("{}", encoding="utf-8")
    pre_k_report = root / "reports/pre-k.json"
    pre_k_report.write_text('{"schema_version":"pre-k/v1"}', encoding="utf-8")

    fair_root = root / "artifacts/fair"
    fair_reports = root / "reports/fair"
    fair_runs: list[dict[str, Any]] = []
    for seed in (17, 42, 73):
        path = fair_reports / f"seed{seed}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {"schema_version": "k-fnspid-fair-baseline-training/v1", "seed": seed}
            ),
            encoding="utf-8",
        )
        fair_runs.append({"seed": seed, "report": file_commitment(path, root)})
    (fair_root / "seed42").mkdir(parents=True)
    (fair_root / "seed42/model.safetensors").write_bytes(b"fair")
    fair_selection = fair_reports / "selection.json"
    fair_selection.write_text(
        json.dumps(
            {
                "schema_version": "k-fnspid-fair-baseline-selection/v1",
                "selected_seed": 42,
                "runs": fair_runs,
            }
        ),
        encoding="utf-8",
    )

    no_k_reports_dir = root / "reports/ablations"
    no_k_reports: dict[str, dict[str, int | str]] = {}
    for seed in (17, 42, 73):
        path = no_k_reports_dir / f"no-k-seed{seed}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "schema_version": "k-fnspid-sentiment-ablation-training/v1",
                    "ablation_mode": "NO_K",
                    "artifact_role": "RESEARCH_ABLATION_NOT_DEPLOYABLE",
                    "public_test_opened": False,
                    "test": {
                        "sample_count": 0,
                        "status": "NOT_AVAILABLE_TO_ABLATION_RUNNER",
                    },
                    "seed": seed,
                    "training_strategy": (
                        "group-purged-three-way-ablation-target-swap-rdrop-"
                        "hierarchical-upper6-lora/v1"
                    ),
                    "training_source_distribution": {"PUBLIC_TRAIN": 7413},
                    "source_selection_provenance": _no_k_source_provenance(),
                    "target_swap_count": 0,
                    "target_swap_source_distribution": {},
                    "partition_count": {"PUBLIC_TEST_NOT_LOADED": 0},
                    "decision_calibration": {
                        "public_test_used_for_fit": False,
                        "sealed_gold_used_for_fit": False,
                    },
                }
            ),
            encoding="utf-8",
        )
        no_k_reports[str(seed)] = file_commitment(path, root)
    no_k_artifact = root / "artifacts/no-k/seed42"
    no_k_artifact.mkdir(parents=True)
    (no_k_artifact / "adapter_model.safetensors").write_bytes(b"no-k")
    (no_k_artifact / "hannah_metadata.json").write_text(
        json.dumps(
            {
                "schema_version": "kf-deberta-sentiment-ablation-artifact/v1",
                "artifact_role": "RESEARCH_ABLATION_NOT_DEPLOYABLE",
                "ablation_mode": "NO_K",
                "seed": 42,
            }
        ),
        encoding="utf-8",
    )
    no_k_winner = root / "artifacts/no-k/selection/winner.json"
    no_k_winner.parent.mkdir(parents=True)
    no_k_winner.write_text(
        json.dumps(
            {
                "schema_version": "k-fnspid-sentiment-ablation-winner-manifest/v1",
                "artifact_role": "RESEARCH_ABLATION_NOT_DEPLOYABLE",
                "ablation_mode": "NO_K",
                "selected_seed": 42,
                "selected_training_report": no_k_reports["42"],
                "artifact_directory": str(no_k_artifact.relative_to(root)),
                "artifact_files": directory_commitment(no_k_artifact, root)["files"],
                "confirmatory_or_public_test_used": False,
                "deployment_eligible": False,
            }
        ),
        encoding="utf-8",
    )
    no_k_selection = no_k_reports_dir / "no-k-selection.json"
    no_k_selection.write_text(
        json.dumps(
            {
                "schema_version": "k-fnspid-sentiment-ablation-selection/v1",
                "ablation_mode": "NO_K",
                "candidate_reports": no_k_reports,
                "winner": {"seed": 42},
                "winner_artifact_manifest": file_commitment(no_k_winner, root),
                "deployment_eligible": False,
            }
        ),
        encoding="utf-8",
    )
    baselines = build_confirmatory_baseline_commitments(
        project_root=root,
        tfidf_model=tfidf,
        pre_k_artifact=pre_k,
        pre_k_training_report=pre_k_report,
        fair_artifact_root=fair_root,
        fair_selection_report=fair_selection,
        no_k_selection_report=no_k_selection,
        no_k_winner_manifest=no_k_winner,
    )

    evaluator_base = root / "models/evaluator-base"
    runtime_base = root / "models/runtime-base"
    for path in (evaluator_base, runtime_base):
        path.mkdir(parents=True)
        (path / "model.safetensors").write_bytes(b"same-base")
    reservation_inputs: dict[str, list[dict[str, str]]] = {}
    outputs: list[dict[str, object]] = []
    for source in ("NEWS", "DISCLOSURE"):
        record = lock["sealed_reservations"][source]
        rows = [
            json.loads(line)
            for line in (root / record["path"]).read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        reservation_inputs[source] = []
        for row in rows:
            item_id = f"{row['document_id']}::{row['stock_code']}"
            reservation_inputs[source].append(
                {
                    "item_id": item_id,
                    "source_record_sha256": _canonical_sha256(row),
                }
            )
            outputs.append(
                {"item_id": item_id, "label": "POSITIVE", "logits": [-1.0, 0.0, 1.0]}
            )
    evidence = build_cpu_serving_parity_evidence(
        candidate_version=candidate_version,
        candidate_artifact_manifest_sha256=candidate_manifest_sha256,
        reservation_inputs=reservation_inputs,
        evaluator_outputs=outputs,
        packaged_runtime_outputs=outputs,
        evaluator_base_model=base_encoder_evidence(evaluator_base, root),
        packaged_runtime_base_model=base_encoder_evidence(runtime_base, root),
        generated_at="2026-07-15T00:00:00+00:00",
    )
    parity_path = root / "reports/runtime-parity.json"
    parity_path.write_text(json.dumps(evidence), encoding="utf-8")
    parity = build_runtime_parity_lock_commitment(
        evidence_path=parity_path,
        project_root=root,
        expected_candidate_version=candidate_version,
        expected_candidate_artifact_manifest_sha256=candidate_manifest_sha256,
        sealed_reservations=lock["sealed_reservations"],
    )
    return baselines, parity


def _provenance_record(path: Path, root: Path) -> dict[str, int | str]:
    return {"path": str(path.relative_to(root)), **_file_manifest(path)}


def _same_data_fair_baseline_fixture(
    root: Path,
) -> tuple[Path, Path, dict[str, Any]]:
    module = _module()
    shared_inputs: dict[str, Path] = {}
    for name in module.FAIR_TO_CANDIDATE_INPUTS:
        path = root / "data/training-contract" / f"{name}.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{name}\n", encoding="utf-8")
        shared_inputs[name] = path
    fair_inputs = {name: _provenance_record(path, root) for name, path in shared_inputs.items()}
    candidate_inputs = {
        candidate_name: fair_inputs[fair_name]
        for fair_name, candidate_name in module.FAIR_TO_CANDIDATE_INPUTS.items()
    }

    candidate_report_path = root / "reports/candidates/kf-deberta-sentiment-seed17.json"
    candidate_report_path.parent.mkdir(parents=True, exist_ok=True)
    candidate_arguments = {
        "seed": 17,
        "data_selection_seed": module.DATA_SELECTION_SEED,
        "max_length": 256,
        "epochs": 1.5,
        "batch_size": 8,
        "gradient_accumulation_steps": 2,
        "early_stopping_patience": 1,
        "learning_rate": 1e-4,
        "lr_scheduler_type": "cosine",
        "warmup_fraction": 0.08,
        "weight_decay": 0.01,
        "silver_per_label": 6_000,
        "disclosure_per_label": 900,
        "target_swap_per_source": 1_500,
        "rdrop_alpha": 0.35,
        "max_train_rows": None,
        "gradient_checkpointing": False,
    }
    prepared_commitments = {
        name: {
            "row_count": 10_000 if name == "TRAIN" else 600,
            "sha256": _canonical_sha256({"partition": name}),
        }
        for name in (
            "TRAIN",
            "CHECKPOINT",
            "CALIBRATION",
            "SELECTION",
            "NEWS_CONFIRMATORY_RESERVATION",
            "DISCLOSURE_CONFIRMATORY_RESERVATION",
        )
    }
    training_weight_audit = {
        "total": {"raw_count": 10_000, "effective_weight_sum": 5_000.0}
    }
    candidate_environment = {
        "python": "test",
        "platform": "test",
        "torch": "test",
        "transformers": "test",
        "peft": "test",
        "numpy": "test",
        "mps_available": False,
        "cuda_available": False,
        "trainer_device": "cpu",
        "bitwise_deterministic_guaranteed": False,
        "reproducibility_limit": "test kernels may differ",
    }
    fair_environment = {
        name: candidate_environment[name]
        for name in (
            "mps_available",
            "cuda_available",
            "trainer_device",
            "bitwise_deterministic_guaranteed",
            "reproducibility_limit",
        )
    }
    training_runtime = {
        "trainer_device": "cpu",
        "global_step": 100,
        "train_runtime": 10.0,
        "train_samples_per_second": 100.0,
        "train_steps_per_second": 10.0,
    }
    candidate_report = {
        "schema_version": "kf-deberta-sentiment-training/v2",
        "dataset_revision": module.DATASET_REVISION,
        "public_dataset_revision": module.PUBLIC_DATASET_REVISION,
        "input_feature_version": "source-target-prefix-head-tail/v2",
        "input_artifacts": candidate_inputs,
        "training_arguments": candidate_arguments,
        "prepared_partition_commitments": prepared_commitments,
        "training_weight_audit": training_weight_audit,
        "training_environment": candidate_environment,
        "training_runtime": training_runtime,
        "candidate_selection": {
            "selection_partition": "PUBLIC_AND_K_FNSPID_DEVELOPMENT_SELECTION",
            "test_used_for_selection": False,
            "operational_gold_used_for_selection": False,
            "sealed_test_evaluated": False,
        },
        "loss": {
            "method": "effective-mass-class-balanced-focal-plus-hierarchical-boundary/v2",
            "rdrop_alpha": 0.35,
        },
        "target_swap_hard_negative_augmentation": {
            "method": "deterministic-name-code-alias-absent-target-swap/v2",
            "requested_per_source": 1_500,
            "sample_weight": 0.55,
            "donor_absence_fields": ["stock_name", "stock_code", "stock_aliases"],
            "donor_alias_provenance_preserved": True,
        },
    }
    candidate_report_path.write_text(
        json.dumps(candidate_report, ensure_ascii=False), encoding="utf-8"
    )
    candidate_manifest_path = root / "reports/sentiment-candidate-lock.json"
    candidate_manifest_path.write_text(
        json.dumps(
            {"ranking": [{"seed": seed} for seed in module.FAIR_BASELINE_SEEDS]},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    candidate_lock = {
        "candidate_report_path": str(candidate_report_path.relative_to(root)),
        "manifest_path": str(candidate_manifest_path.relative_to(root)),
    }

    code_paths = {
        "fair_baseline_trainer": root / "scripts/train_k_fnspid_fair_baseline.py",
        "candidate_training_pipeline": root / "scripts/train_kf_deberta_sentiment_v2.py",
        "sentiment_input": root / "src/hannah_montana_ai/services/sentiment_input.py",
        "sentiment_protocol": root / "src/hannah_montana_ai/training/sentiment_protocol.py",
    }
    for name, path in code_paths.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {name}\n", encoding="utf-8")
    training_code = {name: _provenance_record(path, root) for name, path in code_paths.items()}
    lock_paths = {"pyproject": root / "pyproject.toml", "uv_lock": root / "uv.lock"}
    for name, path in lock_paths.items():
        path.write_text(f"# {name}\n", encoding="utf-8")
    lock_files = {name: _provenance_record(path, root) for name, path in lock_paths.items()}
    runtime_versions = {"torch": "test", "transformers": "test"}
    dependency_payload = {
        "lock_files": lock_files,
        "runtime_versions": runtime_versions,
    }
    dependency_provenance = {
        **dependency_payload,
        "dependency_contract_sha256": _canonical_sha256(dependency_payload),
    }
    candidate_report["training_code"] = {"trainer": training_code["candidate_training_pipeline"]}
    candidate_report["dependency_artifacts"] = lock_files
    candidate_report_path.write_text(
        json.dumps(candidate_report, ensure_ascii=False), encoding="utf-8"
    )

    artifact_root = root / "artifacts/sentiment/fair_baselines/kr-finbert-sc"
    selected_artifact = artifact_root / "seed17"
    selected_artifact.mkdir(parents=True)
    for filename in module.FAIR_BASELINE_ARTIFACTS:
        (selected_artifact / filename).write_bytes(f"fair:{filename}".encode())
    artifact_files = {
        filename: _file_manifest(selected_artifact / filename)
        for filename in module.FAIR_BASELINE_ARTIFACTS
    }
    report_root = root / "reports/fair_baselines/kr-finbert-sc"
    report_root.mkdir(parents=True)
    logit_biases = {
        "NEWS_UNTARGETED": [0.0, 0.0, 0.0],
        "NEWS_TARGETED": [-0.1, 0.2, -0.1],
        "DISCLOSURE_TARGETED": [0.0, 0.1, -0.1],
    }
    score_by_seed = {17: (0.82, 0.84), 42: (0.81, 0.90), 73: (0.80, 0.95)}
    run_records = []
    for seed in module.FAIR_BASELINE_SEEDS:
        score, overall = score_by_seed[seed]
        version = f"kr-finbert-sc-k-fnspid-fair-baseline-seed{seed}-test"
        report = {
            "schema_version": "k-fnspid-fair-baseline-training/v1",
            "version": version,
            "base_model": module.FAIR_BASELINE_MODEL,
            "base_model_revision": module.FAIR_BASELINE_MODEL_REVISION,
            "weights_format": "safetensors",
            "label_order": list(module.LABEL_ORDER),
            "max_length": 256,
            "input_feature_version": module.INPUT_FEATURE_VERSION,
            "full_finetune": True,
            "logit_bias_by_domain": logit_biases,
            "trained_at": "2026-07-15T00:00:00+00:00",
            "artifact_files": artifact_files,
            "seed": seed,
            "dataset_revision": module.DATASET_REVISION,
            "public_dataset_revision": module.PUBLIC_DATASET_REVISION,
            "input_artifacts": fair_inputs,
            "training_code": training_code,
            "dependency_provenance": dependency_provenance,
            "base_model_provenance": {
                "repository": module.FAIR_BASELINE_MODEL,
                "revision": module.FAIR_BASELINE_MODEL_REVISION,
                "upstream_main_revision_at_lock": "f8586286cc3161fb648e9fee09a456069fd846d0",
                "weights_format": "safetensors",
                "trust_remote_code": False,
                "weights_only": True,
                "full_finetune": True,
                "classification_head_trainable": True,
            },
            "prepared_partition_commitments": prepared_commitments,
            "training_arguments": {
                **candidate_arguments,
                "seed": seed,
                "seed_budget": list(module.FAIR_BASELINE_SEEDS),
                "learning_rate": 2e-5,
                "early_stopping_patience": 1,
                "target_swap_weight": 0.55,
                "same_data_splits_seeds_epochs_update_schedule_as_candidate": True,
                "comparison_scope": "same data and update schedule",
                "model_specific_optimizer_and_parameterization": True,
            },
            "training_strategy": (
                "full-finetune-same-three-way-dual-gold-target-swap-rdrop-hierarchical/v4"
            ),
            "loss": {
                "method": "effective-mass-class-balanced-focal-plus-hierarchical-boundary/v2",
                "rdrop_alpha": 0.35,
            },
            "target_swap_augmentation": {
                "method": "deterministic-name-code-alias-absent-target-swap/v2",
                "per_source": 1_500,
                "sample_weight": 0.55,
                "generated_count": 100,
                "same_data_augmentation_schedule_as_candidate": True,
                "donor_absence_fields": ["stock_name", "stock_code", "stock_aliases"],
                "donor_alias_provenance_preserved": True,
            },
            "partition_count": {
                "TRAIN": 10_000,
                "CHECKPOINT": 600,
                "CALIBRATION": 600,
                "SELECTION": 600,
                "PUBLIC_TEST": 0,
            },
            "candidate_selection": {
                "selection_partition": "PUBLIC_AND_K_FNSPID_DEVELOPMENT_SELECTION",
                "selection_method": "weakest-source-macro-f1-then-overall/v1",
                "selection_score": score,
                "required_sources": list(module.FAIR_SELECTION_PARTITIONS),
                "public_test_path_accessed": False,
                "public_test_labels_used": False,
                "confirmatory_labels_used": False,
                "confirmatory_reservation_identity_only": True,
            },
            "selection": {"macro_f1": overall},
            "selection_breakdown": {
                partition: {
                    "sample_count": 200,
                    "macro_f1": score if index == 0 else min(1.0, score + index * 0.01),
                }
                for index, partition in enumerate(module.FAIR_SELECTION_PARTITIONS)
            },
            "test": {
                "sample_count": 0,
                "status": "FORBIDDEN_DURING_TRAINING_AND_SELECTION",
            },
            "training_weight_audit": training_weight_audit,
            "training_environment": fair_environment,
            "training_runtime": training_runtime,
            "trainable_parameter_count": 110_000_000,
            "total_parameter_count": 110_000_000,
        }
        report_path = report_root / f"seed{seed}.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
        run_records.append(
            {
                "seed": seed,
                "selection_score": score,
                "overall_selection_macro_f1": overall,
                "report": _provenance_record(report_path, root),
            }
        )
        if seed == 17:
            metadata = {
                key: report[key]
                for key in (
                    "version",
                    "base_model",
                    "base_model_revision",
                    "weights_format",
                    "label_order",
                    "max_length",
                    "input_feature_version",
                    "full_finetune",
                    "logit_bias_by_domain",
                    "trained_at",
                    "artifact_files",
                )
            }
            metadata["schema_version"] = "k-fnspid-fair-baseline-artifact/v1"
            (selected_artifact / "hannah_metadata.json").write_text(
                json.dumps(metadata, ensure_ascii=False), encoding="utf-8"
            )
    selection_path = report_root / "selection.json"
    selection_path.write_text(
        json.dumps(
            {
                "schema_version": "k-fnspid-fair-baseline-selection/v1",
                "base_model": module.FAIR_BASELINE_MODEL,
                "base_model_revision": module.FAIR_BASELINE_MODEL_REVISION,
                "seed_budget": list(module.FAIR_BASELINE_SEEDS),
                "selection_method": ("weakest-source-macro-f1-then-overall-then-lowest-seed/v1"),
                "selected_seed": 17,
                "selected_weakest_source_macro_f1": 0.82,
                "public_test_labels_used": False,
                "confirmatory_labels_used": False,
                "runs": run_records,
                "generated_at": "2026-07-15T00:00:00+00:00",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return artifact_root, selection_path, candidate_lock


def _sealed_row(index: int, label: str, reviewed_at: str) -> dict[str, Any]:
    reviewer = {
        "reviewed_at": reviewed_at,
    }
    return {
        "schema_version": "k-fnspid-sentiment-codex-gold/v1",
        "partition": "SEALED_TEST_REVIEW",
        "document_id": f"document-{index}",
        "source_type": "NEWS",
        "text": f"뉴스 {index}",
        "canonical_url": f"https://example.com/{index}",
        "content_hash": f"content-{index}",
        "event_cluster_id": f"event-{index}",
        "source_review_status": "CODEX_REVIEW_APPROVED",
        "review_status": "CODEX_REVIEW_APPROVED",
        "label_quality": "GOLD",
        "needs_codex_review": False,
        "sentiment": label,
        "teacher_sentiment": label,
        "teacher_generated_at_utc": reviewed_at,
        "reviewer_id": "codex-blind-review-v1",
        "reviewer_1": {**reviewer, "reviewer_id": "codex-stage-1"},
        "reviewer_2": {**reviewer, "reviewer_id": "codex-stage-2"},
        "adjudication": None,
        "reviewed_at": reviewed_at,
        "promoted_at": "2026-07-15T01:00:00+00:00",
    }


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def test_candidate_lock_validates_all_hashes_and_metadata(tmp_path: Path) -> None:
    module = _module()
    lock_path, artifact_dir = _candidate_lock_fixture(tmp_path)

    result = module.validate_candidate_lock(
        lock_path,
        artifact_dir,
        project_root=tmp_path,
    )

    lock_payload = json.loads(lock_path.read_text(encoding="utf-8"))
    artifact_files = lock_payload["winner"]["artifact_files"]
    expected_manifest_hash = sha256(
        json.dumps(
            artifact_files,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    assert result["version"] == "hana-montana-test-candidate"
    assert result["max_length"] == 384
    assert result["input_feature_version"] == "source-target-prefix-head-tail/v2"
    assert result["logit_bias_by_domain"]["NEWS_TARGETED"] == [-0.1, 0.2, -0.1]
    assert result["artifact_manifest_sha256"] == expected_manifest_hash
    assert result["locked_before_evaluation"] is True
    assert set(result["recipe"]["blobs"]) == {
        name for name, _ in module.RECIPE_RELATIVE_PATHS
    }
    assert len(result["statistical_analysis_plan"]["holm_hypotheses"]) == 8


def test_candidate_lock_rejects_statistical_plan_or_recipe_mutation(tmp_path: Path) -> None:
    module = _module()
    lock_path, artifact_dir = _candidate_lock_fixture(tmp_path)
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    lock["statistical_analysis_plan"]["familywise_alpha"] = 0.10
    lock_path.write_text(json.dumps(lock, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(ValueError, match="statistical_analysis_plan"):
        module.validate_candidate_lock(lock_path, artifact_dir, project_root=tmp_path)

    lock_path, artifact_dir = _candidate_lock_fixture(tmp_path / "recipe")
    evaluator_path = tmp_path / "recipe" / "scripts/evaluate_locked_kf_deberta_sentiment.py"
    evaluator_path.write_text("# changed\n", encoding="utf-8")
    with pytest.raises(ValueError, match="recipe evaluator"):
        module.validate_candidate_lock(
            lock_path,
            artifact_dir,
            project_root=tmp_path / "recipe",
        )


@pytest.mark.parametrize(
    ("batch_size", "samples", "seed"),
    [(15, 2_000, 20260715), (16, 1_999, 20260715), (16, 2_000, 20260716)],
)
def test_evaluator_rejects_cli_deviation_from_locked_statistical_plan(
    batch_size: int,
    samples: int,
    seed: int,
) -> None:
    module = _module()
    plan = module.canonical_statistical_analysis_plan()

    with pytest.raises(ValueError, match="evaluation CLI"):
        module.validate_evaluation_runtime_parameters(
            plan,
            batch_size=batch_size,
            bootstrap_samples=samples,
            bootstrap_seed=seed,
        )


def test_cli_plan_deviation_is_rejected_before_any_label_loader(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "evaluate_locked_kf_deberta_sentiment.py",
            "--report",
            str(tmp_path / "report.json"),
            "--consumption-receipt",
            str(tmp_path / "receipt.json"),
            "--batch-size",
            "15",
        ],
    )
    monkeypatch.setattr(
        module,
        "validate_attested_candidate",
        lambda *_args, **_kwargs: (
            {"statistical_analysis_plan": module.canonical_statistical_analysis_plan()},
            {},
        ),
    )

    def forbidden(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("계획 검증 전에 평가 라벨 또는 기준선을 열면 안 됩니다.")

    monkeypatch.setattr(module, "validate_same_data_fair_baseline", forbidden)
    monkeypatch.setattr(module, "load_public_test", forbidden)
    monkeypatch.setattr(module, "load_sealed_gold", forbidden)

    with pytest.raises(ValueError, match="evaluation CLI"):
        module.main()


def test_evaluator_requires_matching_remote_git_attestation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    attestation = {
        "candidate_lock_sha256": "a" * 64,
        "sha256": "b" * 64,
        "commit_sha": "c" * 40,
    }
    candidate_lock = {"manifest_sha256": "a" * 64}
    monkeypatch.setattr(
        module,
        "validate_candidate_git_attestation",
        lambda *_args, **_kwargs: dict(attestation),
    )
    monkeypatch.setattr(
        module,
        "validate_candidate_lock",
        lambda *_args, **_kwargs: dict(candidate_lock),
    )

    validated_lock, validated_attestation = module.validate_attested_candidate(
        tmp_path / "attestation.json",
        tmp_path / "lock.json",
        tmp_path / "artifact",
        project_root=tmp_path,
    )

    assert validated_attestation == attestation
    assert validated_lock["external_git_attestation"] == attestation
    candidate_lock["manifest_sha256"] = "d" * 64
    with pytest.raises(ValueError, match="attestation.*lock hash"):
        module.validate_attested_candidate(
            tmp_path / "attestation.json",
            tmp_path / "lock.json",
            tmp_path / "artifact",
            project_root=tmp_path,
        )


def test_candidate_lock_fails_closed_after_artifact_mutation(tmp_path: Path) -> None:
    module = _module()
    lock_path, artifact_dir = _candidate_lock_fixture(tmp_path)
    (artifact_dir / "adapter_config.json").write_text("tampered", encoding="utf-8")

    with pytest.raises(ValueError, match="artifact 무결성"):
        module.validate_candidate_lock(lock_path, artifact_dir, project_root=tmp_path)


@pytest.mark.parametrize(
    ("test_used", "gold_used"),
    [(True, False), (False, True)],
)
def test_candidate_lock_rejects_test_or_gold_candidate_selection(
    tmp_path: Path,
    test_used: bool,
    gold_used: bool,
) -> None:
    module = _module()
    lock_path, artifact_dir = _candidate_lock_fixture(
        tmp_path,
        test_used_for_selection=test_used,
        gold_used_for_selection=gold_used,
    )

    with pytest.raises(ValueError, match="Test/Gold 봉인 계약"):
        module.validate_candidate_lock(lock_path, artifact_dir, project_root=tmp_path)


def test_candidate_lock_rejects_input_contract_mismatch(tmp_path: Path) -> None:
    module = _module()
    lock_path, artifact_dir = _candidate_lock_fixture(
        tmp_path,
        input_feature_version="plain-truncation/v0",
    )

    with pytest.raises(ValueError, match="입력 계약"):
        module.validate_candidate_lock(lock_path, artifact_dir, project_root=tmp_path)


def test_candidate_lock_rejects_logit_bias_mismatch(tmp_path: Path) -> None:
    module = _module()
    lock_path, artifact_dir = _candidate_lock_fixture(tmp_path)
    metadata_path = artifact_dir / "hannah_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["logit_bias_by_domain"]["NEWS_TARGETED"] = [0.0, 0.0, 0.0]
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    lock["winner"]["artifact_files"]["hannah_metadata.json"] = _file_manifest(metadata_path)
    lock_path.write_text(json.dumps(lock), encoding="utf-8")

    with pytest.raises(ValueError, match="입력 계약"):
        module.validate_candidate_lock(lock_path, artifact_dir, project_root=tmp_path)


def test_same_data_fair_baseline_is_validated_before_label_loading(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _module()
    artifact_root, selection_path, candidate_lock = _same_data_fair_baseline_fixture(tmp_path)

    def forbidden_label_loader(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("공정 기준선 검증에서 확증 라벨을 열면 안 됩니다.")

    monkeypatch.setattr(module, "_load_jsonl", forbidden_label_loader)
    result = module.validate_same_data_fair_baseline(
        artifact_root,
        selection_path,
        candidate_lock=candidate_lock,
        project_root=tmp_path,
    )

    assert result["selected_seed"] == 17
    assert result["same_data_split_selection_budget_verified"] is True
    assert result["full_finetune"] is True
    assert result["public_test_labels_used_for_training_or_selection"] is False
    assert result["confirmatory_labels_used_for_training_or_selection"] is False
    assert set(result["artifact_files"]) == set(module.FAIR_BASELINE_ARTIFACTS)
    assert result["same_data_contract"]["data_selection_seed"] == module.DATA_SELECTION_SEED
    assert "CHECKPOINT" in result["same_data_contract"]["prepared_partition_commitments"]


def test_same_data_fair_baseline_rejects_candidate_partition_mismatch(tmp_path: Path) -> None:
    module = _module()
    artifact_root, selection_path, candidate_lock = _same_data_fair_baseline_fixture(tmp_path)
    candidate_report_path = tmp_path / candidate_lock["candidate_report_path"]
    candidate_report = json.loads(candidate_report_path.read_text(encoding="utf-8"))
    candidate_report["prepared_partition_commitments"]["TRAIN"]["sha256"] = "f" * 64
    candidate_report_path.write_text(json.dumps(candidate_report), encoding="utf-8")

    with pytest.raises(ValueError, match="준비 파티션"):
        module.validate_same_data_fair_baseline(
            artifact_root,
            selection_path,
            candidate_lock=candidate_lock,
            project_root=tmp_path,
        )


def test_same_data_fair_baseline_rejects_data_seed_or_device_mismatch(
    tmp_path: Path,
) -> None:
    module = _module()
    artifact_root, selection_path, candidate_lock = _same_data_fair_baseline_fixture(tmp_path)
    candidate_report_path = tmp_path / candidate_lock["candidate_report_path"]
    candidate_report = json.loads(candidate_report_path.read_text(encoding="utf-8"))
    candidate_report["training_arguments"]["data_selection_seed"] = 1
    candidate_report_path.write_text(json.dumps(candidate_report), encoding="utf-8")

    with pytest.raises(ValueError, match="학습 예산.*data_selection_seed"):
        module.validate_same_data_fair_baseline(
            artifact_root,
            selection_path,
            candidate_lock=candidate_lock,
            project_root=tmp_path,
        )

    candidate_report["training_arguments"]["data_selection_seed"] = module.DATA_SELECTION_SEED
    candidate_report["training_environment"]["trainer_device"] = "mps"
    candidate_report_path.write_text(json.dumps(candidate_report), encoding="utf-8")
    with pytest.raises(ValueError, match="device/update"):
        module.validate_same_data_fair_baseline(
            artifact_root,
            selection_path,
            candidate_lock=candidate_lock,
            project_root=tmp_path,
        )


def test_same_data_fair_baseline_rejects_mismatched_training_budget(tmp_path: Path) -> None:
    module = _module()
    artifact_root, selection_path, candidate_lock = _same_data_fair_baseline_fixture(tmp_path)
    report_path = selection_path.parent / "seed17.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    report["training_arguments"]["epochs"] = 2.0
    report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    selection["runs"][0]["report"] = _provenance_record(report_path, tmp_path)
    selection_path.write_text(json.dumps(selection, ensure_ascii=False), encoding="utf-8")

    with pytest.raises(ValueError, match="학습 예산"):
        module.validate_same_data_fair_baseline(
            artifact_root,
            selection_path,
            candidate_lock=candidate_lock,
            project_root=tmp_path,
        )


def test_same_data_fair_baseline_rejects_artifact_mutation(tmp_path: Path) -> None:
    module = _module()
    artifact_root, selection_path, candidate_lock = _same_data_fair_baseline_fixture(tmp_path)
    (artifact_root / "seed17/model.safetensors").write_bytes(b"tampered")

    with pytest.raises(ValueError, match="artifact 계약"):
        module.validate_same_data_fair_baseline(
            artifact_root,
            selection_path,
            candidate_lock=candidate_lock,
            project_root=tmp_path,
        )


def test_same_data_fair_baseline_predictor_loads_only_local_safetensors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _module()
    tokenizer_calls: list[tuple[object, dict[str, Any]]] = []
    model_calls: list[tuple[object, dict[str, Any]]] = []

    class FakeTokenizerLoader:
        @staticmethod
        def from_pretrained(path: object, **kwargs: Any) -> object:
            tokenizer_calls.append((path, kwargs))
            return object()

    class FakeModel:
        def to(self, device: object) -> None:
            return None

        def eval(self) -> None:
            return None

    class FakeModelLoader:
        @staticmethod
        def from_pretrained(path: object, **kwargs: Any) -> FakeModel:
            model_calls.append((path, kwargs))
            return FakeModel()

    fake_transformers = ModuleType("transformers")
    fake_transformers.AutoTokenizer = FakeTokenizerLoader  # type: ignore[attr-defined]
    fake_transformers.AutoModelForSequenceClassification = FakeModelLoader  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "transformers", fake_transformers)
    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace())
    monkeypatch.setattr(module, "_verify_file_manifest", lambda *args: None)
    monkeypatch.setattr(module, "_torch_device", lambda torch: "cpu")
    provenance = {
        "artifact_files": {"model.safetensors": {"bytes": 1, "sha256": "a" * 64}},
        "max_length": 256,
        "logit_bias_by_domain": {
            "NEWS_UNTARGETED": [0.0, 0.0, 0.0],
            "NEWS_TARGETED": [0.0, 0.0, 0.0],
            "DISCLOSURE_TARGETED": [0.0, 0.0, 0.0],
        },
    }

    assert (
        module.predict_same_data_fair_baseline([], tmp_path / "artifact", provenance, batch_size=8)
        == []
    )
    assert tokenizer_calls[0][1]["local_files_only"] is True
    assert tokenizer_calls[0][1]["trust_remote_code"] is False
    assert model_calls[0][1]["local_files_only"] is True
    assert model_calls[0][1]["trust_remote_code"] is False
    assert model_calls[0][1]["use_safetensors"] is True


def test_sealed_gold_requires_promotion_after_candidate_lock(tmp_path: Path) -> None:
    module = _module()
    path = tmp_path / "sealed.jsonl"
    labels = ["NEGATIVE", "NEUTRAL", "POSITIVE"]
    rows = [
        _sealed_row(index, label, "2026-07-15T01:00:00+00:00") for index, label in enumerate(labels)
    ]
    rows[0]["reviewed_at"] = "2026-07-14T23:59:59+00:00"
    _write_jsonl(path, rows)

    with pytest.raises(ValueError, match="봉인 Gold 검수 계약"):
        module.load_sealed_gold(
            path,
            expected_partition="SEALED_TEST_REVIEW",
            expected_source="NEWS",
            locked_at=datetime(2026, 7, 15, tzinfo=UTC),
        )

    rows = [
        _sealed_row(index, label, "2026-07-15T00:30:00+00:00") for index, label in enumerate(labels)
    ]
    _write_jsonl(path, rows)
    loaded = module.load_sealed_gold(
        path,
        expected_partition="SEALED_TEST_REVIEW",
        expected_source="NEWS",
        locked_at=datetime(2026, 7, 15, tzinfo=UTC),
    )
    assert [row["label"] for row in loaded] == labels

    rows[0]["promoted_at"] = "2026-07-14T23:59:58+00:00"
    _write_jsonl(path, rows)
    with pytest.raises(ValueError, match="봉인 Gold 검수 계약"):
        module.load_sealed_gold(
            path,
            expected_partition="SEALED_TEST_REVIEW",
            expected_source="NEWS",
            locked_at=datetime(2026, 7, 15, tzinfo=UTC),
        )


def test_source_metrics_include_cluster_bootstrap_and_paired_tests() -> None:
    module = _module()
    labels = ["NEGATIVE", "NEUTRAL", "POSITIVE"] * 2
    rows = [
        {"label": label, "event_cluster_id": f"event-{index}"} for index, label in enumerate(labels)
    ]
    result = module.evaluate_partition(
        rows,
        {
            "kf_deberta_lora_locked": labels,
            "hana_tfidf_logistic": ["NEUTRAL"] * len(labels),
        },
        role="diagnostic_fixture",
        cluster_protocol="event_cluster_id",
        bootstrap_samples=100,
        seed=7,
    )

    candidate = result["models"]["kf_deberta_lora_locked"]
    comparison = result["statistical_comparisons"]["candidate_vs_hana_tfidf_logistic"]
    assert candidate["accuracy"] == 1.0
    assert candidate["macro_f1"] == 1.0
    assert candidate["cluster_bootstrap_95_ci"]["cluster_count"] == 6
    assert "paired_record_bootstrap_95_ci" in comparison
    assert "paired_event_cluster_bootstrap_95_ci" in comparison
    assert comparison["mcnemar_exact_two_sided"]["candidate_only_correct"] == 4
    assert comparison["confirmatory_significance_claim_allowed"] is False
    assert comparison["included_in_holm_family"] is False
    assert comparison["diagnostic_only"] is True
    assert comparison["claim_allowed"] is False


def test_probability_sample_metrics_use_design_weights_and_stratified_clusters() -> None:
    module = _module()
    labels = ["NEGATIVE", "NEGATIVE", "NEUTRAL", "NEUTRAL", "POSITIVE", "POSITIVE"]
    rows = [
        {"label": label, "event_cluster_id": f"event-{index}"} for index, label in enumerate(labels)
    ]
    weights = [2.0, 2.0, 20.0, 20.0, 5.0, 5.0]
    strata = ["NEGATIVE", "NEGATIVE", "NEUTRAL", "NEUTRAL", "POSITIVE", "POSITIVE"]

    result = module.evaluate_partition(
        rows,
        {
            "kf_deberta_lora_locked": labels,
            "hana_tfidf_logistic": ["NEUTRAL"] * len(labels),
        },
        role="confirmatory_sealed_gold",
        cluster_protocol="event_cluster_id",
        bootstrap_samples=100,
        seed=19,
        analysis_weights=weights,
        sampling_strata=strata,
        population_counts_by_stratum={"NEGATIVE": 4, "NEUTRAL": 40, "POSITIVE": 10},
    )

    candidate = result["models"]["kf_deberta_lora_locked"]
    comparison = result["statistical_comparisons"]["candidate_vs_hana_tfidf_logistic"]
    assert candidate["sampling_design_weighted"]["accuracy"] == 1.0
    assert result["sampling_design_analysis"]["estimated_population_count"] == 54.0
    assert "stratified_cluster_bootstrap_95_ci" in candidate
    assert "sampling_design_delete_1_jackknife_95_ci" in candidate
    assert "paired_stratified_event_cluster_bootstrap_95_ci" in comparison
    assert "paired_sampling_design_delete_1_jackknife_95_ci" in comparison
    assert "paired_cluster_randomization_two_sided" in comparison


def test_confirmatory_claim_flags_are_limited_to_exact_v6_holm_family() -> None:
    module = _module()
    labels = ["NEGATIVE", "NEGATIVE", "NEUTRAL", "NEUTRAL", "POSITIVE", "POSITIVE"]
    rows = [
        {"label": label, "event_cluster_id": f"event-{index}"}
        for index, label in enumerate(labels)
    ]
    diagnostic_names = {
        "hana_tfidf_logistic",
        "kr_finbert_sc",
        module.QWEN_TEACHER_MODEL_NAME,
        module.NO_K_ABLATION_MODEL_NAME,
    }
    holm_names = {
        "kr_finbert_sc_raw_off_the_shelf",
        module.PRE_K_FNSPID_MODEL_NAME,
        module.V6_FAIR_BASELINE_MODEL_NAME,
        module.V6_NO_K_ABLATION_MODEL_NAME,
    }
    result = module.evaluate_partition(
        rows,
        {
            module.V6_CANDIDATE_MODEL_NAME: labels,
            **{name: ["NEUTRAL"] * len(labels) for name in diagnostic_names | holm_names},
        },
        role="confirmatory_sealed_gold",
        cluster_protocol="event_cluster_id",
        bootstrap_samples=100,
        seed=17,
        analysis_weights=[2.0] * len(labels),
        sampling_strata=labels,
        population_counts_by_stratum={
            "NEGATIVE": 4,
            "NEUTRAL": 4,
            "POSITIVE": 4,
        },
        candidate_model_name=module.V6_CANDIDATE_MODEL_NAME,
    )

    for name in holm_names:
        comparison = result["statistical_comparisons"][f"candidate_vs_{name}"]
        assert comparison["included_in_holm_family"] is True
        assert comparison["claim_allowed"] is True
        assert comparison["diagnostic_only"] is False
    for name in diagnostic_names:
        comparison = result["statistical_comparisons"][f"candidate_vs_{name}"]
        assert comparison["included_in_holm_family"] is False
        assert comparison["claim_allowed"] is False
        assert comparison["diagnostic_only"] is True


def test_weighted_classification_metrics_match_hand_calculated_confusion_matrix() -> None:
    module = _module()
    expected = ["NEGATIVE", "NEGATIVE", "NEUTRAL", "NEUTRAL", "POSITIVE", "POSITIVE"]
    predicted = ["NEGATIVE", "NEUTRAL", "NEUTRAL", "POSITIVE", "NEGATIVE", "POSITIVE"]
    weights = [2.0, 3.0, 5.0, 7.0, 11.0, 13.0]

    result = module.weighted_classification_metrics(expected, predicted, weights)

    assert result["confusion_matrix"] == {
        "NEGATIVE": {"NEGATIVE": 2.0, "NEUTRAL": 3.0, "POSITIVE": 0.0},
        "NEUTRAL": {"NEGATIVE": 0.0, "NEUTRAL": 5.0, "POSITIVE": 7.0},
        "POSITIVE": {"NEGATIVE": 11.0, "NEUTRAL": 0.0, "POSITIVE": 13.0},
    }
    assert result["estimated_population_count"] == 41.0
    assert result["accuracy"] == pytest.approx(20.0 / 41.0)
    assert result["label_metrics"]["NEGATIVE"] == pytest.approx(
        {
            "precision": 2.0 / 13.0,
            "recall": 2.0 / 5.0,
            "f1": 2.0 / 9.0,
            "estimated_support": 5.0,
        }
    )
    assert result["label_metrics"]["NEUTRAL"] == pytest.approx(
        {
            "precision": 5.0 / 8.0,
            "recall": 5.0 / 12.0,
            "f1": 0.5,
            "estimated_support": 12.0,
        }
    )
    assert result["label_metrics"]["POSITIVE"] == pytest.approx(
        {
            "precision": 13.0 / 20.0,
            "recall": 13.0 / 24.0,
            "f1": 13.0 / 22.0,
            "estimated_support": 24.0,
        }
    )
    assert result["macro_f1"] == pytest.approx((2.0 / 9.0 + 0.5 + 13.0 / 22.0) / 3.0)


def test_delete_one_jackknife_applies_finite_population_correction() -> None:
    module = _module()
    expected = ["NEGATIVE", "NEGATIVE", "NEUTRAL", "NEUTRAL", "POSITIVE", "POSITIVE"]
    predicted = ["NEGATIVE", "NEUTRAL", "NEUTRAL", "POSITIVE", "POSITIVE", "NEGATIVE"]
    strata = ["NEGATIVE", "NEGATIVE", "NEUTRAL", "NEUTRAL", "POSITIVE", "POSITIVE"]
    clusters = [f"event-{index}" for index in range(len(expected))]

    census = module.stratified_delete_one_jackknife_metrics(
        expected,
        predicted,
        clusters,
        [1.0] * len(expected),
        strata,
        {"NEGATIVE": 2, "NEUTRAL": 2, "POSITIVE": 2},
    )
    sampled = module.stratified_delete_one_jackknife_metrics(
        expected,
        predicted,
        clusters,
        [10.0] * len(expected),
        strata,
        {"NEGATIVE": 20, "NEUTRAL": 20, "POSITIVE": 20},
    )

    assert census["macro_f1"]["standard_error"] == 0.0
    assert sampled["macro_f1"]["standard_error"] > 0.0


def test_paired_jackknife_fpc_matches_hand_oracle_and_degenerate_case_fails_closed() -> None:
    module = _module()
    expected = ["NEGATIVE", "NEGATIVE", "NEUTRAL", "NEUTRAL", "POSITIVE", "POSITIVE"]
    baseline = ["NEGATIVE", "NEUTRAL", "NEUTRAL", "POSITIVE", "POSITIVE", "NEGATIVE"]
    candidate = ["NEGATIVE", "NEGATIVE", "NEUTRAL", "POSITIVE", "POSITIVE", "POSITIVE"]
    clusters = [f"event-{index}" for index in range(len(expected))]

    sampled = module.paired_stratified_delete_one_jackknife(
        expected,
        baseline,
        candidate,
        clusters,
        [2.0] * len(expected),
        expected,
        {"NEGATIVE": 4, "NEUTRAL": 4, "POSITIVE": 4},
    )
    # 층별 delete-1 base variance 합 1/18에 (1-f)=1/2를 곱한다.
    assert sampled["accuracy_difference"]["variance"] == pytest.approx(1.0 / 36.0)
    assert sampled["accuracy_difference"]["standard_error"] == pytest.approx(1.0 / 6.0)

    census = module.paired_stratified_delete_one_jackknife(
        expected,
        baseline,
        candidate,
        clusters,
        [1.0] * len(expected),
        expected,
        {"NEGATIVE": 2, "NEUTRAL": 2, "POSITIVE": 2},
    )
    assert census["accuracy_difference"]["estimate"] > 0.0
    assert census["accuracy_difference"]["standard_error"] == 0.0
    assert census["accuracy_difference"]["two_sided_normal_p_value"] == 1.0


def test_design_jackknife_rejects_duplicate_sampling_units() -> None:
    module = _module()
    expected = ["NEGATIVE", "NEGATIVE", "NEUTRAL", "NEUTRAL", "POSITIVE", "POSITIVE"]
    with pytest.raises(ValueError, match="고유한 event cluster"):
        module.stratified_delete_one_jackknife_metrics(
            expected,
            expected,
            ["duplicate"] * len(expected),
            [2.0] * len(expected),
            expected,
            {"NEGATIVE": 4, "NEUTRAL": 4, "POSITIVE": 4},
        )


def test_holm_adjustment_controls_familywise_error() -> None:
    module = _module()

    assert module.holm_adjusted_p_values([0.01, 0.03, 0.04]) == pytest.approx([0.03, 0.06, 0.06])


def _confirmatory_result(module: ModuleType, *, fair_low: float = 0.02) -> dict[str, Any]:
    comparisons = {}
    for baseline in (
        "kr_finbert_sc_raw_off_the_shelf",
        module.PRE_K_FNSPID_MODEL_NAME,
        module.FAIR_BASELINE_MODEL_NAME,
        module.NO_K_ABLATION_MODEL_NAME,
    ):
        low = fair_low if baseline == module.FAIR_BASELINE_MODEL_NAME else 0.02
        comparisons[f"candidate_vs_{baseline}"] = {
            "included_in_holm_family": True,
            "diagnostic_only": False,
            "claim_allowed": True,
            "confirmatory_significance_claim_allowed": True,
            "observed_sampling_design_weighted_difference": {"macro_f1": 0.04},
            "paired_sampling_design_delete_1_jackknife_95_ci": {
                "macro_f1_difference": {
                    "estimate": 0.04,
                    "low": low,
                    "high": 0.06,
                    "two_sided_normal_p_value": 0.001,
                }
            },
        }
    return {"statistical_comparisons": comparisons}


def test_confirmatory_holm_family_includes_same_data_fair_baseline() -> None:
    module = _module()
    inference = module.build_confirmatory_inference(
        _confirmatory_result(module),
        _confirmatory_result(module),
    )

    assert inference["family_hypothesis_count"] == 8
    assert inference["family_hypothesis_ids"] == [
        row["hypothesis_id"]
        for row in module.canonical_statistical_analysis_plan()["holm_hypotheses"]
    ]
    assert inference["fair_baseline_superiority_claim_allowed"] is True
    assert module.FAIR_BASELINE_MODEL_NAME in inference["sources"]["NEWS"]
    assert inference["sources"]["NEWS"][module.FAIR_BASELINE_MODEL_NAME][
        "holm_adjusted_p_value"
    ] == pytest.approx(0.008)
    assert inference["no_k_ablation_superiority_claim_allowed"] is True
    assert inference["large_or_material_superiority_claim_allowed"] is True

    failed = module.build_confirmatory_inference(
        _confirmatory_result(module, fair_low=-0.01),
        _confirmatory_result(module),
    )
    assert failed["fair_baseline_superiority_claim_allowed"] is False


def test_deployment_gate_requires_every_source_and_public_check() -> None:
    module = _module()
    news = {
        "sample_count": 500,
        "accuracy": 0.90,
        "macro_f1": 0.85,
        "baseline_accuracy": 0.89,
        "baseline_macro_f1": 0.84,
        "kr_finbert_sc_accuracy": 0.78,
        "kr_finbert_sc_macro_f1": 0.76,
        "kr_finbert_sc_raw_accuracy": 0.77,
        "kr_finbert_sc_raw_macro_f1": 0.75,
        "qwen3_4b_teacher_accuracy": 0.80,
        "qwen3_4b_teacher_macro_f1": 0.78,
        "pre_k_fnspid_macro_f1": 0.84,
        "fair_baseline_accuracy": 0.88,
        "fair_baseline_macro_f1": 0.83,
        "no_k_ablation_accuracy": 0.87,
        "no_k_ablation_macro_f1": 0.82,
    }
    disclosure = dict(news)
    public = {
        "macro_f1": 0.86,
        "kr_finbert_sc_macro_f1": 0.85,
        "pre_k_fnspid_macro_f1": 0.855,
        "fair_baseline_macro_f1": 0.84,
        "no_k_ablation_macro_f1": 0.83,
    }

    passed = module.build_deployment_gate(
        news,
        disclosure,
        public,
        candidate_version="candidate-v1",
        artifact_manifest_sha256="a" * 64,
        confirmatory_inference={
            "raw_kr_finbert_reference_superiority_claim_allowed": True,
            "pre_k_fnspid_superiority_claim_allowed": True,
            "fair_baseline_superiority_claim_allowed": True,
            "no_k_ablation_superiority_claim_allowed": True,
        },
    )
    assert passed["eligible"] is True
    assert passed["candidate_model"] == "kf_deberta_lora_locked"
    assert passed["candidate_artifact_manifest_sha256"] == "a" * 64

    public["macro_f1"] = 0.0
    diagnostic_only = module.build_deployment_gate(
        news,
        disclosure,
        public,
        candidate_version="candidate-v1",
        artifact_manifest_sha256="a" * 64,
        confirmatory_inference={
            "raw_kr_finbert_reference_superiority_claim_allowed": True,
            "pre_k_fnspid_superiority_claim_allowed": True,
            "fair_baseline_superiority_claim_allowed": True,
            "no_k_ablation_superiority_claim_allowed": True,
        },
    )
    assert diagnostic_only["eligible"] is True
    assert (
        diagnostic_only["secondary_regression_diagnostics"]["public_macro_f1_threshold_met"]
        is False
    )

    disclosure["macro_f1"] = 0.8499
    failed = module.build_deployment_gate(
        news,
        disclosure,
        public,
        candidate_version="candidate-v1",
        artifact_manifest_sha256="a" * 64,
        confirmatory_inference={
            "raw_kr_finbert_reference_superiority_claim_allowed": True,
            "pre_k_fnspid_superiority_claim_allowed": True,
            "fair_baseline_superiority_claim_allowed": True,
            "no_k_ablation_superiority_claim_allowed": True,
        },
    )
    assert failed["eligible"] is False
    assert failed["checks"]["disclosure_macro_f1"] is False

    disclosure["macro_f1"] = 0.85
    failed_fair = module.build_deployment_gate(
        news,
        disclosure,
        public,
        candidate_version="candidate-v1",
        artifact_manifest_sha256="a" * 64,
        confirmatory_inference={
            "raw_kr_finbert_reference_superiority_claim_allowed": True,
            "pre_k_fnspid_superiority_claim_allowed": True,
            "fair_baseline_superiority_claim_allowed": False,
            "no_k_ablation_superiority_claim_allowed": True,
        },
    )
    assert failed_fair["eligible"] is False
    assert (
        failed_fair["checks"]["news_and_disclosure_statistically_superior_to_fair_baseline"]
        is False
    )

    failed_raw = module.build_deployment_gate(
        news,
        disclosure,
        public,
        candidate_version="candidate-v1",
        artifact_manifest_sha256="a" * 64,
        confirmatory_inference={
            "raw_kr_finbert_reference_superiority_claim_allowed": False,
            "pre_k_fnspid_superiority_claim_allowed": True,
            "fair_baseline_superiority_claim_allowed": True,
            "no_k_ablation_superiority_claim_allowed": True,
        },
    )
    assert failed_raw["eligible"] is False
    assert (
        failed_raw["checks"][
            "news_and_disclosure_statistically_superior_to_raw_kr_finbert_reference"
        ]
        is False
    )


def test_mcnemar_exact_two_sided_is_symmetric() -> None:
    module = _module()

    assert module.exact_mcnemar_p_value(0, 0) == 1.0
    assert module.exact_mcnemar_p_value(1, 5) == module.exact_mcnemar_p_value(5, 1)


def test_consumption_receipt_writer_is_exclusive(tmp_path: Path) -> None:
    module = _module()
    path = tmp_path / "receipt.json"
    module._write_json_exclusive(path, {"one_shot": True})

    with pytest.raises(ValueError, match="이미 존재"):
        module._write_json_exclusive(path, {"one_shot": False})
