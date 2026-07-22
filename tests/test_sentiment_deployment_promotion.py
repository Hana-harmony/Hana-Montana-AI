from __future__ import annotations

import importlib.util
import json
import math
import shutil
import subprocess  # nosec B404
import sys
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from types import ModuleType
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
)
from hannah_montana_ai.training.sentiment_evaluation_plan import (
    RECIPE_RELATIVE_PATHS,
    canonical_statistical_analysis_plan,
)
from hannah_montana_ai.training.sentiment_git_attestation import LIMITATIONS


def _module() -> ModuleType:
    path = Path("scripts/promote_kf_deberta_sentiment_deployment.py")
    spec = importlib.util.spec_from_file_location("promote_sentiment_deployment", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _git(root: Path, *arguments: str) -> str:
    executable = shutil.which("git")
    assert executable is not None
    result = subprocess.run(  # noqa: S603  # nosec B603
        [executable, *arguments],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _manifest(directory: Path, filenames: set[str]) -> dict[str, dict[str, int | str]]:
    return {
        filename: {
            "bytes": (directory / filename).stat().st_size,
            "sha256": _sha256(directory / filename),
        }
        for filename in sorted(filenames)
    }


def _metrics(sample_count: int = 600) -> dict[str, int | float]:
    return {
        "sample_count": sample_count,
        "accuracy": 0.95,
        "macro_f1": 0.94,
        "baseline_accuracy": 0.80,
        "baseline_macro_f1": 0.79,
        "kr_finbert_sc_accuracy": 0.90,
        "kr_finbert_sc_macro_f1": 0.89,
        "kr_finbert_sc_raw_accuracy": 0.88,
        "kr_finbert_sc_raw_macro_f1": 0.87,
        "qwen3_4b_teacher_accuracy": 0.90,
        "qwen3_4b_teacher_macro_f1": 0.89,
        "pre_k_fnspid_accuracy": 0.75,
        "pre_k_fnspid_macro_f1": 0.74,
        "fair_baseline_accuracy": 0.86,
        "fair_baseline_macro_f1": 0.85,
        "no_k_ablation_accuracy": 0.84,
        "no_k_ablation_macro_f1": 0.83,
    }


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


def _thresholds() -> dict[str, Any]:
    return {
        "minimum_sealed_sample_count_per_source": 500,
        "minimum_sealed_accuracy_per_source": 0.90,
        "minimum_sealed_macro_f1_per_source": 0.85,
        "sealed_must_not_regress_vs_current_tfidf": True,
        "sealed_must_match_or_exceed_reference_family": [
            "target-aware snunlp/KR-FinBERT-SC",
            "raw snunlp/KR-FinBERT-SC",
            "same-data/split/selection-budget full-finetuned snunlp/KR-FinBERT-SC",
            "locked KF-DeBERTa no-K-FNSPID ablation",
        ],
        "blind_teacher_diagnostic_only_not_gating": "Qwen3-4B-GGUF-Q4",
        "sealed_must_improve_vs_pre_k_fnspid_model": True,
        "confirmatory_superiority_requires": (
            "positive weighted Macro-F1 difference, positive paired SRSWOR FPC "
            "delete-1 jackknife lower bound, and Holm-adjusted jackknife-normal p<0.05"
        ),
    }


def _fixture(tmp_path: Path, module: ModuleType) -> dict[str, Any]:
    root = tmp_path / "project"
    locked_artifact = root / "artifacts/sentiment/locked"
    report_path = root / "reports/candidates/kf-deberta-sentiment-seed17.json"
    lock_path = root / "reports/sentiment-candidate-lock.json"
    benchmark_path = root / "reports/korean-finance-sentiment-benchmark-v4.json"
    receipt_path = root / "reports/sentiment-sealed-evaluation-consumption.json"
    training_script = root / "scripts/train_kf_deberta_sentiment_v2.py"
    evaluation_script = root / "scripts/evaluate_locked_kf_deberta_sentiment.py"
    target_artifact = root / "src/hannah_montana_ai/model_store/kf_deberta_sentiment_v2"
    legacy_artifact = root / "src/hannah_montana_ai/model_store/kf_deberta_sentiment"
    target_report = root / "reports/kf-deberta-sentiment-training-report.json"
    target_benchmark = root / "reports/korean-finance-sentiment-benchmark.json"
    releases_root = root / "releases/sentiment"
    current_pointer = releases_root / "current.json"
    base_model = root / "base-model"
    training_script.parent.mkdir(parents=True, exist_ok=True)
    training_script.write_text("# locked training recipe\n", encoding="utf-8")
    evaluation_script.write_text("# one-shot evaluator\n", encoding="utf-8")
    for relative in sorted(module.REQUIRED_RUNTIME_CODE):
        runtime_path = root / relative
        if not runtime_path.exists():
            runtime_path.parent.mkdir(parents=True, exist_ok=True)
            runtime_path.write_text(f"# {relative}\n", encoding="utf-8")
    base_model.mkdir(parents=True)
    (base_model / "config.json").write_text('{"model_type":"deberta-v2"}\n', encoding="utf-8")
    (base_model / "model.safetensors").write_bytes(b"base-model")
    locked_artifact.mkdir(parents=True)
    legacy_artifact.mkdir(parents=True)
    (legacy_artifact / "baseline.marker").write_text("do-not-replace", encoding="utf-8")
    _write_json(legacy_artifact / "hannah_metadata.json", {"version": "pre-k"})
    pre_k_report = root / "reports/kf-deberta-sentiment-training-report-pre-k-fnspid.json"
    _write_json(pre_k_report, {"version": "pre-k"})
    tfidf_model = root / "src/hannah_montana_ai/model_store/financial_nlp_ml.joblib"
    tfidf_model.parent.mkdir(parents=True, exist_ok=True)
    tfidf_model.write_bytes(b"tfidf-baseline")
    fair_artifact = root / "artifacts/sentiment/fair_baselines/kr-finbert-sc/seed17"
    fair_artifact.mkdir(parents=True)
    _write_json(fair_artifact / "hannah_metadata.json", {"version": "fair-v1"})
    (fair_artifact / "model.safetensors").write_bytes(b"fair-baseline-model")
    fair_manifest = _manifest(
        fair_artifact,
        {"hannah_metadata.json", "model.safetensors"},
    )
    fair_selection = root / "reports/fair_baselines/kr-finbert-sc/selection.json"
    fair_training = root / "reports/fair_baselines/kr-finbert-sc/seed17.json"
    _write_json(fair_selection, {"selected_seed": 17})
    _write_json(fair_training, {"version": "fair-v1"})

    adapter_config = {
        "base_model_name_or_path": module.BASE_MODEL,
        "peft_type": "LORA",
        "task_type": "SEQ_CLS",
        "target_modules": ["query_proj", "key_proj", "value_proj", "dense"],
        "layers_to_transform": list(range(6, 12)),
        "layers_pattern": "layer",
        "modules_to_save": ["pooler", "classifier"],
    }
    _write_json(locked_artifact / "adapter_config.json", adapter_config)
    (locked_artifact / "adapter_model.safetensors").write_bytes(b"safe-adapter")
    _write_json(locked_artifact / "tokenizer.json", {"version": "1.0", "model": {}})
    _write_json(locked_artifact / "tokenizer_config.json", {"tokenizer_class": "BertTokenizer"})
    training_artifacts = _manifest(locked_artifact, set(module.TRAINING_ARTIFACTS))

    now = datetime.now(UTC)
    trained_at = (now - timedelta(hours=2)).isoformat()
    locked_at = (now - timedelta(hours=1)).isoformat()
    consumed_at = (now - timedelta(minutes=30)).isoformat()
    generated_at = (now - timedelta(minutes=20)).isoformat()
    version = "hana-montana-kf-deberta-k-fnspid-sentiment-seed17-20260715120000"
    biases = {
        "NEWS_UNTARGETED": [0.0, 0.1, -0.1],
        "NEWS_TARGETED": [-0.1, 0.2, -0.1],
        "DISCLOSURE_TARGETED": [-0.2, 0.3, -0.1],
    }
    metadata = {
        "schema_version": module.ARTIFACT_SCHEMA_VERSION,
        "version": version,
        "base_model": module.BASE_MODEL,
        "base_model_revision": module.BASE_MODEL_REVISION,
        "label_order": list(module.LABEL_ORDER),
        "max_length": 256,
        "input_feature_version": module.INPUT_FEATURE_VERSION,
        "logit_bias_by_domain": biases,
        "trained_at": trained_at,
        "artifact_files": training_artifacts,
    }
    _write_json(locked_artifact / "hannah_metadata.json", metadata)
    locked_artifacts = _manifest(locked_artifact, set(module.LOCKED_ARTIFACTS))
    auxiliary_paths = {
        role: root / relative
        for role, relative in module.AUXILIARY_TRAINING_INPUTS.items()
    }
    for source, gold_role, report_role in (
        ("NEWS", "news_auxiliary_training_gold", "news_auxiliary_training_report"),
        (
            "DISCLOSURE",
            "disclosure_auxiliary_training_gold",
            "disclosure_auxiliary_training_report",
        ),
    ):
        gold_path = auxiliary_paths[gold_role]
        gold_path.parent.mkdir(parents=True, exist_ok=True)
        gold_path.write_text(
            json.dumps(
                {
                    "schema_version": "k-fnspid-sentiment-auxiliary-training-gold/v2",
                    "partition": "AUXILIARY_TRAINING_GOLD",
                    "source_type": source,
                    "sentiment": "NEUTRAL",
                    "final_sentiment": "NEUTRAL",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        _write_json(
            auxiliary_paths[report_role],
            {
                "schema_version": "k-fnspid-sentiment-training-reclassification/v2",
                "source": {
                    "source_type": source,
                    "review_sample_count": 1,
                    "sample_count": 1,
                    "excluded_unresolved_count": 0,
                },
                "reclassification": {
                    "previous_role": (
                        "REPEATEDLY_EXPOSED_DIAGNOSTIC_NOT_CLAIM_EVIDENCE"
                    ),
                    "new_role": "TRAINING_ONLY_NOT_EVALUATION_OR_CLAIM_EVIDENCE",
                    "confirmatory_created_before_reclassification": True,
                    "eligible_for_confirmatory_metrics": False,
                    "eligible_for_evaluation": False,
                    "eligible_for_model_selection": False,
                    "eligible_for_superiority_claims": False,
                },
                "integrity": {
                    "exact_item_set": True,
                    "independent_dual_review_required": True,
                    "model_blind": True,
                    "market_blind": True,
                    "confirmatory_sampling_commitments_verified": True,
                    "promotion_after_confirmatory_reservation": True,
                    "source_review_protected_at_confirmatory_reservation": True,
                    "write_once": True,
                    "unresolved_rows_excluded": True,
                    "confirmatory_group_overlap_count": 0,
                },
                "lineage": {
                    "output": {
                        "path": module.AUXILIARY_TRAINING_INPUTS[gold_role],
                        "bytes": gold_path.stat().st_size,
                        "sha256": _sha256(gold_path),
                    }
                },
            },
        )
    auxiliary_records = {
        name: {
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": _sha256(path),
        }
        for name, path in auxiliary_paths.items()
    }
    _write_json(
        fair_training,
        {
            "schema_version": "k-fnspid-fair-baseline-training/v1",
            "version": "fair-v1",
            "training_strategy": (
                "full-finetune-same-three-way-dual-gold-target-swap-rdrop-hierarchical/v4"
            ),
            "input_artifacts": auxiliary_records,
        },
    )

    training = {
        "schema_version": module.TRAINING_SCHEMA_VERSION,
        **{key: value for key, value in metadata.items() if key != "schema_version"},
        "seed": 17,
        "training_strategy": (
            "group-purged-three-way-dual-gold-target-swap-rdrop-hierarchical-upper6-lora/v5"
        ),
        "input_artifacts": auxiliary_records,
        "lora_layers": list(range(6, 12)),
        "candidate_selection": {
            "locked_candidate": "kf_deberta_lora",
            "selection_score": 0.91,
            "test_used_for_selection": False,
            "operational_gold_used_for_selection": False,
            "sealed_test_evaluated": False,
        },
        "decision_calibration": {
            "method": "validation-only-domain-logit-offset-grid/v1",
            "fit_partition": "CALIBRATION_ONLY",
            "selection_used_for_fit": False,
            "public_test_used_for_fit": False,
            "sealed_gold_used_for_fit": False,
            "logit_bias_by_domain": biases,
        },
        "test": {"sample_count": 0, "status": "SEALED_UNTIL_CANDIDATE_LOCK"},
    }
    _write_json(report_path, training)

    news_reservation = root / "data/gold/news-reservation.jsonl"
    disclosure_reservation = root / "data/gold/disclosure-reservation.jsonl"
    news_reservation.parent.mkdir(parents=True)
    news_reservation.write_text('{"source_type":"NEWS"}\n', encoding="utf-8")
    disclosure_reservation.write_text(
        '{"source_type":"DISCLOSURE"}\n', encoding="utf-8"
    )
    codebook = root / "docs/datasets/sentiment-codebook.md"
    sampling_code = root / "src/hannah_montana_ai/training/sentiment_sampling.py"
    dataset_news = root / "reports/news-dataset.json"
    dataset_disclosure = root / "reports/disclosure-dataset.json"
    dataset_sampling = root / "reports/sampling-dataset.json"
    codebook.parent.mkdir(parents=True)
    codebook.write_text("# codebook\n", encoding="utf-8")
    sampling_code.parent.mkdir(parents=True, exist_ok=True)
    sampling_code.write_text("# sampling\n", encoding="utf-8")
    _write_json(dataset_news, {"source": "NEWS"})
    _write_json(dataset_disclosure, {"source": "DISCLOSURE"})
    _write_json(dataset_sampling, {"source": "SAMPLING_DESIGN"})

    def provenance(path: Path) -> dict[str, int | str]:
        return {
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": _sha256(path),
        }

    for name, relative_path in RECIPE_RELATIVE_PATHS:
        recipe_path = root / relative_path
        recipe_path.parent.mkdir(parents=True, exist_ok=True)
        if not recipe_path.exists():
            recipe_path.write_text(f"# {name}\n", encoding="utf-8")
    recipe_blobs = {
        name: provenance(root / relative_path) for name, relative_path in RECIPE_RELATIVE_PATHS
    }

    fair_runs: list[dict[str, Any]] = []
    for seed in (17, 42, 73):
        seed_report = root / f"reports/fair_baselines/kr-finbert-sc/seed{seed}.json"
        if seed != 17:
            _write_json(
                seed_report,
                {
                    "schema_version": "k-fnspid-fair-baseline-training/v1",
                    "version": f"fair-seed{seed}",
                    "training_strategy": (
                        "full-finetune-same-three-way-dual-gold-target-swap-rdrop-"
                        "hierarchical/v4"
                    ),
                    "input_artifacts": auxiliary_records,
                },
            )
        fair_runs.append({"seed": seed, "report": provenance(seed_report)})
    _write_json(
        fair_selection,
        {
            "schema_version": "k-fnspid-fair-baseline-selection/v1",
            "selected_seed": 17,
            "runs": fair_runs,
        },
    )

    no_k_artifact = root / "artifacts/sentiment/ablations/no-k/seed17"
    no_k_artifact.mkdir(parents=True)
    _write_json(
        no_k_artifact / "hannah_metadata.json",
        {
            "schema_version": "kf-deberta-sentiment-ablation-artifact/v1",
            "artifact_role": "RESEARCH_ABLATION_NOT_DEPLOYABLE",
            "ablation_mode": "NO_K",
            "seed": 17,
        },
    )
    (no_k_artifact / "adapter_model.safetensors").write_bytes(b"no-k-ablation")
    no_k_reports: dict[str, dict[str, int | str]] = {}
    for seed in (17, 42, 73):
        no_k_report = root / f"reports/ablations/kf-deberta-sentiment-no-k-seed{seed}.json"
        _write_json(
            no_k_report,
            {
                "schema_version": "k-fnspid-sentiment-ablation-training/v1",
                "ablation_mode": "NO_K",
                "artifact_role": "RESEARCH_ABLATION_NOT_DEPLOYABLE",
                "seed": seed,
                "public_test_opened": False,
                "test": {
                    "sample_count": 0,
                    "status": "NOT_AVAILABLE_TO_ABLATION_RUNNER",
                },
                "training_strategy": (
                    "group-purged-three-way-ablation-target-swap-rdrop-hierarchical-"
                    "upper6-lora/v1"
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
            },
        )
        no_k_reports[str(seed)] = provenance(no_k_report)
    no_k_winner_manifest = (
        root
        / "artifacts/sentiment/ablations/no-k/selection/winner-artifact-manifest.json"
    )
    _write_json(
        no_k_winner_manifest,
        {
            "schema_version": "k-fnspid-sentiment-ablation-winner-manifest/v1",
            "artifact_role": "RESEARCH_ABLATION_NOT_DEPLOYABLE",
            "ablation_mode": "NO_K",
            "deployment_eligible": False,
            "confirmatory_or_public_test_used": False,
            "selected_seed": 17,
            "selected_training_report": no_k_reports["17"],
            "artifact_directory": no_k_artifact.relative_to(root).as_posix(),
            "artifact_files": _manifest(
                no_k_artifact,
                {"hannah_metadata.json", "adapter_model.safetensors"},
            ),
        },
    )
    no_k_selection = (
        root / "reports/ablations/kf-deberta-sentiment-no-k-selection.json"
    )
    _write_json(
        no_k_selection,
        {
            "schema_version": "k-fnspid-sentiment-ablation-selection/v1",
            "ablation_mode": "NO_K",
            "deployment_eligible": False,
            "candidate_reports": no_k_reports,
            "winner": {"seed": 17},
            "winner_artifact_manifest": provenance(no_k_winner_manifest),
        },
    )
    baseline_commitments = build_confirmatory_baseline_commitments(
        project_root=root,
        tfidf_model=tfidf_model,
        pre_k_artifact=legacy_artifact,
        pre_k_training_report=pre_k_report,
        fair_artifact_root=fair_artifact.parent,
        fair_selection_report=fair_selection,
        no_k_selection_report=no_k_selection,
        no_k_winner_manifest=no_k_winner_manifest,
    )
    baseline_digest = baseline_commitments_sha256(baseline_commitments)

    reservation_inputs = {
        "NEWS": [
            {"item_id": "news-reservation-1", "source_record_sha256": "6" * 64}
        ],
        "DISCLOSURE": [
            {
                "item_id": "disclosure-reservation-1",
                "source_record_sha256": "7" * 64,
            }
        ],
    }
    sealed_reservations: dict[str, dict[str, Any]] = {}
    for source, reservation_path in (
        ("NEWS", news_reservation),
        ("DISCLOSURE", disclosure_reservation),
    ):
        rows = reservation_inputs[source]
        sealed_reservations[source] = {
            **provenance(reservation_path),
            "sample_count": len(rows),
            "item_id_set_sha256": module._canonical_json_sha256(
                sorted(row["item_id"] for row in rows)
            ),
            "source_record_set_sha256": module._canonical_json_sha256(
                sorted(rows, key=lambda row: row["item_id"])
            ),
        }
    artifact_manifest_sha256 = module._canonical_json_sha256(locked_artifacts)
    parity_outputs = [
        {
            "item_id": "news-reservation-1",
            "label": "POSITIVE",
            "logits": [-0.2, 0.1, 0.8],
        },
        {
            "item_id": "disclosure-reservation-1",
            "label": "NEUTRAL",
            "logits": [-0.1, 0.6, 0.2],
        },
    ]
    base_evidence = base_encoder_evidence(base_model, root)
    parity_evidence = build_cpu_serving_parity_evidence(
        candidate_version=version,
        candidate_artifact_manifest_sha256=artifact_manifest_sha256,
        reservation_inputs=reservation_inputs,
        evaluator_outputs=parity_outputs,
        packaged_runtime_outputs=parity_outputs,
        evaluator_base_model=base_evidence,
        packaged_runtime_base_model=base_evidence,
        generated_at=(now - timedelta(minutes=50)).isoformat(),
    )
    parity_evidence_path = root / "reports/sentiment-cpu-runtime-parity.json"
    _write_json(parity_evidence_path, parity_evidence)
    runtime_parity = build_runtime_parity_lock_commitment(
        evidence_path=parity_evidence_path,
        project_root=root,
        expected_candidate_version=version,
        expected_candidate_artifact_manifest_sha256=artifact_manifest_sha256,
        sealed_reservations=sealed_reservations,
    )

    lock = {
        "schema_version": module.LOCK_SCHEMA_VERSION,
        "locked_at": locked_at,
        "selection_only": True,
        "external_git_commitment_required": True,
        "public_test_evaluated_before_lock": False,
        "operational_sealed_gold_evaluated_before_lock": False,
        "sealed_reservations": sealed_reservations,
        "dataset_provenance": {
            "codebook": provenance(codebook),
            "sampling_implementation": provenance(sampling_code),
            "dataset_reports": {
                "NEWS": provenance(dataset_news),
                "DISCLOSURE": provenance(dataset_disclosure),
                "SAMPLING_DESIGN": provenance(dataset_sampling),
            },
        },
        "winner": {
            "seed": 17,
            "version": version,
            "selection_score": 0.91,
            "report_path": "reports/candidates/kf-deberta-sentiment-seed17.json",
            "report_sha256": _sha256(report_path),
            "source_artifact_dir": "artifacts/sentiment/candidates/seed17",
            "locked_artifact_dir": "artifacts/sentiment/locked",
            "artifact_files": locked_artifacts,
        },
        "ranking": [],
        "statistical_analysis_plan": canonical_statistical_analysis_plan(),
        "recipe": {
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
        },
        "baseline_commitments": baseline_commitments,
        "baseline_commitments_sha256": baseline_digest,
        "runtime_parity": runtime_parity,
    }
    _write_json(lock_path, lock)
    _git(root, "init", "-q")
    _git(root, "config", "user.name", "Release Test")
    _git(root, "config", "user.email", "release-test@example.com")
    _git(root, "remote", "add", "origin", ".")
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "lock sentiment candidate")
    candidate_commit = _git(root, "rev-parse", "HEAD")
    candidate_tree = _git(root, "show", "-s", "--format=%T", candidate_commit)
    committer_time = _git(root, "show", "-s", "--format=%cI", candidate_commit)
    _git(root, "update-ref", "refs/remotes/origin/feature", candidate_commit)
    git_attestation = {
        "schema_version": "sentiment-candidate-git-attestation/v1",
        "role": "REMOTE_GIT_HISTORY_COMMITMENT_NOT_INDEPENDENT_TIMESTAMP",
        "git": {
            "commit_sha": candidate_commit,
            "tree_sha": candidate_tree,
            "committer_time_iso": committer_time,
            "remote_name": "origin",
            "remote_tracking_ref": "refs/remotes/origin/feature",
            "commit_is_ancestor_of_remote_tracking_ref": True,
        },
        "candidate_lock": {
            "path": "reports/sentiment-candidate-lock.json",
            "bytes": lock_path.stat().st_size,
            "sha256": _sha256(lock_path),
            "bytes_equal_local_lock": True,
        },
        "committed_artifact_manifests": {
            "sealed_reservations": {
                source: {
                    key: lock["sealed_reservations"][source][key]
                    for key in ("path", "bytes", "sha256")
                }
                for source in ("NEWS", "DISCLOSURE")
            },
            "dataset_provenance": lock["dataset_provenance"],
            "code_provenance": {
                "training_script": {
                    **recipe_blobs["candidate_trainer"],
                }
            },
            "recipe_blobs": recipe_blobs,
            "baseline_commitments": baseline_commitments,
            "baseline_commitments_sha256": baseline_digest,
            "runtime_parity": runtime_parity,
            "runtime_parity_evidence": runtime_parity["evidence"],
        },
        "limitations": list(LIMITATIONS),
        "attested_at": datetime.now(UTC).isoformat(),
    }
    git_attestation_path = root / "reports/sentiment-candidate-git-attestation.json"
    _write_json(git_attestation_path, git_attestation)
    normalized_git_attestation = module.validate_candidate_git_attestation(
        git_attestation_path,
        lock_path,
        project_root=root,
    )
    artifact_manifest_sha256 = module._canonical_json_sha256(locked_artifacts)

    sealed_news = root / "sealed/news.jsonl"
    sealed_disclosure = root / "sealed/disclosure.jsonl"
    news_promotion = root / "reports/news-sealed-promotion.json"
    disclosure_promotion = root / "reports/disclosure-sealed-promotion.json"
    sampling_design = root / "reports/sampling-design.json"
    sealed_news.parent.mkdir(parents=True)
    gold_commitment = {
        "candidate_manifest_sha256": _sha256(lock_path),
        "candidate_git_attestation_sha256": normalized_git_attestation["sha256"],
        "candidate_git_commit_sha": candidate_commit,
    }
    sealed_news.write_text(
        json.dumps(
            {"source_type": "NEWS", "sentiment": "NEUTRAL", **gold_commitment}
        )
        + "\n",
        encoding="utf-8",
    )
    sealed_disclosure.write_text(
        json.dumps(
            {
                "source_type": "DISCLOSURE",
                "sentiment": "NEUTRAL",
                **gold_commitment,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    _write_json(
        news_promotion,
        {"status": "pass", "provenance": {"codex_review": gold_commitment}},
    )
    _write_json(
        disclosure_promotion,
        {"status": "pass", "provenance": {"codex_review": gold_commitment}},
    )
    _write_json(sampling_design, {"schema_version": "sampling/v1"})

    same_data_contract = {"matched_input_artifacts": auxiliary_records}
    same_data_contract_sha256 = module._canonical_json_sha256(same_data_contract)
    receipt = {
        "schema_version": "sentiment-sealed-evaluation-consumption/v1",
        "consumed_at": consumed_at,
        "labels_loaded_before_receipt": False,
        "one_shot": True,
        "candidate_version": version,
        "candidate_lock_manifest_sha256": _sha256(lock_path),
        "candidate_artifact_manifest_sha256": artifact_manifest_sha256,
        "candidate_git_attestation": normalized_git_attestation,
        "locked_baseline_commitments": baseline_commitments,
        "locked_baseline_commitments_sha256": baseline_digest,
        "cpu_runtime_parity": runtime_parity,
        "sealed_gold": {
            "NEWS": {"path": "sealed/news.jsonl", "sha256": _sha256(sealed_news)},
            "DISCLOSURE": {
                "path": "sealed/disclosure.jsonl",
                "sha256": _sha256(sealed_disclosure),
            },
        },
        "promotion_reports": {
            "NEWS": {
                "path": "reports/news-sealed-promotion.json",
                "sha256": _sha256(news_promotion),
            },
            "DISCLOSURE": {
                "path": "reports/disclosure-sealed-promotion.json",
                "sha256": _sha256(disclosure_promotion),
            },
        },
        "sampling_design_report": {
            "path": "reports/sampling-design.json",
            "sha256": _sha256(sampling_design),
        },
        "baseline_artifacts": {
            "hana_tfidf_logistic": {
                "path": "src/hannah_montana_ai/model_store/financial_nlp_ml.joblib",
                "sha256": _sha256(tfidf_model),
            },
            "pre_k_fnspid_kf_deberta": {
                "artifact_dir": "src/hannah_montana_ai/model_store/kf_deberta_sentiment",
                "metadata_sha256": _sha256(legacy_artifact / "hannah_metadata.json"),
                "training_report_path": (
                    "reports/kf-deberta-sentiment-training-report-pre-k-fnspid.json"
                ),
                "training_report_sha256": _sha256(pre_k_report),
            },
            "kr_finbert_sc_same_data_fair": {
                "artifact_dir": (
                    "artifacts/sentiment/fair_baselines/kr-finbert-sc/seed17"
                ),
                "artifact_manifest_sha256": module._canonical_json_sha256(
                    fair_manifest
                ),
                "metadata_sha256": _sha256(fair_artifact / "hannah_metadata.json"),
                "selection_report_path": (
                    "reports/fair_baselines/kr-finbert-sc/selection.json"
                ),
                "selection_report_sha256": _sha256(fair_selection),
                "training_report_path": (
                    "reports/fair_baselines/kr-finbert-sc/seed17.json"
                ),
                "training_report_sha256": _sha256(fair_training),
                "same_data_contract_sha256": same_data_contract_sha256,
            },
            "kf_deberta_no_k_ablation": baseline_commitments["baselines"][
                "kf_deberta_no_k_ablation"
            ],
        },
        "evaluation_script_sha256": _sha256(evaluation_script),
        "planned_report_path": "reports/korean-finance-sentiment-benchmark-v4.json",
        "bootstrap_samples": 2_000,
        "bootstrap_seed": 20260715,
    }
    _write_json(receipt_path, receipt)
    public_metrics = _metrics(sample_count=1_000)
    benchmark = {
        "schema_version": module.BENCHMARK_SCHEMA_VERSION,
        "generated_at": generated_at,
        "input_feature_version": module.INPUT_FEATURE_VERSION,
        "candidate_lock": {
            "schema_version": module.LOCK_SCHEMA_VERSION,
            "manifest_path": "reports/sentiment-candidate-lock.json",
            "manifest_sha256": _sha256(lock_path),
            "locked_at": locked_at,
            "locked_before_evaluation": True,
            "selection_only": True,
            "version": version,
            "candidate_report_path": "reports/candidates/kf-deberta-sentiment-seed17.json",
            "candidate_report_sha256": _sha256(report_path),
            "artifact_dir": "artifacts/sentiment/locked",
            "artifact_files": locked_artifacts,
            "artifact_manifest_sha256": artifact_manifest_sha256,
            "base_model": module.BASE_MODEL,
            "base_model_revision": module.BASE_MODEL_REVISION,
            "max_length": 256,
            "input_feature_version": module.INPUT_FEATURE_VERSION,
            "logit_bias_by_domain": biases,
        },
        "sealed_evaluation_consumption": {
            **receipt,
            "receipt_path": "reports/sentiment-sealed-evaluation-consumption.json",
            "receipt_sha256": _sha256(receipt_path),
        },
        "evaluation_contract": {
            "candidate_selection_completed_before_evaluation_labels_loaded": True,
            "locked_before_evaluation": True,
            "test_used_for_candidate_selection": False,
            "sealed_gold_used_for_candidate_selection": False,
            "candidate_selection_inputs": ["CALIBRATION", "SELECTION"],
        },
        "sampling_design": {
            "report_path": "reports/sampling-design.json",
            "report_sha256": _sha256(sampling_design),
        },
        "same_data_fair_baseline": {
            "same_data_contract": same_data_contract,
            "same_data_contract_sha256": same_data_contract_sha256,
            "same_data_split_selection_budget_verified": True,
            "public_test_labels_used_for_training_or_selection": False,
            "confirmatory_labels_used_for_training_or_selection": False,
        },
        "cpu_runtime_parity": runtime_parity,
        "source_sealed_gold": {
            "NEWS": _metrics(),
            "DISCLOSURE": _metrics(),
        },
        "public_test": public_metrics,
    }
    p_value = math.erfc(10.0 / math.sqrt(2.0))
    interval = {
        "estimate": 0.10,
        "variance": 0.0001,
        "standard_error": 0.01,
        "low": 0.10 - 1.959963984540054 * 0.01,
        "high": 0.10 + 1.959963984540054 * 0.01,
        "two_sided_normal_p_value": p_value,
    }
    design = {
        "resampling_unit": "unique_event_cluster",
        "replicate_count": 600,
        "sample_n_h": {label: 200 for label in module.LABEL_ORDER},
        "population_N_h": {label: 1_000 for label in module.LABEL_ORDER},
    }
    inference_sources: dict[str, Any] = {}
    for source_type in ("NEWS", "DISCLOSURE"):
        source_metrics = benchmark["source_sealed_gold"][source_type]
        source_metrics["models"] = {
            model: {
                "sampling_design_delete_1_jackknife_95_ci": {
                    "method": "stratified_delete_1_jackknife_srswor_fpc/v1",
                    **design,
                    "accuracy": {
                        key: value
                        for key, value in interval.items()
                        if key != "two_sided_normal_p_value"
                    },
                    "macro_f1": {
                        key: value
                        for key, value in interval.items()
                        if key != "two_sided_normal_p_value"
                    },
                }
            }
            for model in (
                module.CANDIDATE_MODEL,
                "kr_finbert_sc_raw_off_the_shelf",
                "pre_k_fnspid_kf_deberta",
                "kr_finbert_sc_same_data_fair",
                "kf_deberta_no_k_ablation",
            )
        }
        source_metrics["statistical_comparisons"] = {
            f"candidate_vs_{baseline}": {
                "paired_sampling_design_delete_1_jackknife_95_ci": {
                    "method": "paired_stratified_delete_1_jackknife_srswor_fpc/v1",
                    **design,
                    "accuracy_difference": dict(interval),
                    "macro_f1_difference": dict(interval)
                }
            }
            for baseline in (
                "kr_finbert_sc_raw_off_the_shelf",
                "pre_k_fnspid_kf_deberta",
                "kr_finbert_sc_same_data_fair",
                "kf_deberta_no_k_ablation",
            )
        }
        inference_sources[source_type] = {
            baseline: {
                "paired_sampling_design_jackknife_95_ci": dict(interval),
                "sampling_design_jackknife_normal_p_value": p_value,
                "holm_adjusted_p_value": p_value * 8,
                "statistically_superior": True,
            }
            for baseline in (
                "kr_finbert_sc_raw_off_the_shelf",
                "pre_k_fnspid_kf_deberta",
                "kr_finbert_sc_same_data_fair",
                "kf_deberta_no_k_ablation",
            )
        }
    benchmark["confirmatory_inference"] = {
        "family": (
            "NEWS/DISCLOSURE x raw KR-FinBERT-SC/pre-K-FNSPID/"
            "same-data KR-FinBERT-SC/no-K ablation"
        ),
        "family_hypothesis_count": 8,
        "multiple_comparison_correction": "Holm family-wise alpha=0.05",
        "primary_metric": "sampling-design-weighted plug-in Macro-F1",
        "paired_inference": (
            "stratified SRSWOR delete-1 jackknife with finite-population correction; "
            "Holm-adjusted paired normal tests"
        ),
        "sources": inference_sources,
        "raw_kr_finbert_reference_superiority_claim_allowed": True,
        "pre_k_fnspid_superiority_claim_allowed": True,
        "fair_baseline_superiority_claim_allowed": True,
        "no_k_ablation_superiority_claim_allowed": True,
        "qwen_confirmatory_exclusion": {
            "model": "Qwen3-4B-GGUF-Q4",
            "role": "blind_teacher_diagnostic_only",
            "affects_deployment_gate": False,
            "included_in_holm_family": False,
        },
        "target_aware_kr_finbert_input_ablation": {
            "role": "candidate_input_format_diagnostic_non_claim"
        },
        "global_sota_claim_allowed": False,
    }
    benchmark["deployment_gate"] = {
        "candidate_model": module.CANDIDATE_MODEL,
        "candidate_version": version,
        "candidate_artifact_manifest_sha256": artifact_manifest_sha256,
        "thresholds": _thresholds(),
        "checks": module._expected_gate_checks(benchmark),
        "secondary_regression_diagnostics": {
            "role": "repeatedly_exposed_secondary_regression_set_non_gating",
            "affects_deployment_decision": False,
        },
        "eligible": True,
        "decision": "DEPLOY_HANA_MONTANA_AI",
    }
    _write_json(benchmark_path, benchmark)
    return {
        "project_root": root,
        "lock_manifest": lock_path,
        "locked_artifact": locked_artifact,
        "candidate_report": report_path,
        "benchmark_report": benchmark_path,
        "target_artifact": target_artifact,
        "target_report": target_report,
        "target_benchmark": target_benchmark,
        "legacy_artifact": legacy_artifact,
        "releases_root": releases_root,
        "current_pointer": current_pointer,
        "base_model": base_model,
        "git_commit": candidate_commit,
        "git_tree": candidate_tree,
        "git_attestation_sha256": str(normalized_git_attestation["sha256"]),
    }


def _promote(module: ModuleType, paths: dict[str, Any]) -> dict[str, Any]:
    return module.promote_candidate(
        project_root=paths["project_root"],
        lock_manifest=paths["lock_manifest"],
        locked_artifact=paths["locked_artifact"],
        candidate_report=paths["candidate_report"],
        benchmark_report=paths["benchmark_report"],
        base_model_path=paths["base_model"],
        runtime_base_model_path=Path("/app/models/kf-deberta-base"),
        releases_root=paths["releases_root"],
        current_pointer=paths["current_pointer"],
        source_git_commit=paths["git_commit"],
        source_dirty=True,
    )


def test_promotes_verified_release_without_overwriting_legacy_artifact(tmp_path: Path) -> None:
    module = _module()
    paths = _fixture(tmp_path, module)

    result = _promote(module, paths)

    pointer = json.loads(paths["current_pointer"].read_text(encoding="utf-8"))
    release_dir = paths["releases_root"] / result["release_id"]
    manifest = json.loads((release_dir / "release.json").read_text(encoding="utf-8"))
    assert pointer["release_id"] == result["release_id"]
    assert pointer["attestation"] == {
        "mode": "local-untrusted",
        "production_eligible": False,
    }
    assert set(path.name for path in (release_dir / "artifact").iterdir()) == set(
        module.LOCKED_ARTIFACTS
    )
    assert set(manifest["evidence"]) == set(module.REQUIRED_EVIDENCE_ROLES)
    assert manifest["dependency_lock"] == manifest["runtime_code"]["uv.lock"]
    assert manifest["source"] == {
        "git_commit": paths["git_commit"],
        "dirty": True,
        "candidate_lock_git_commit": paths["git_commit"],
        "candidate_lock_git_tree": paths["git_tree"],
        "candidate_git_attestation_sha256": paths["git_attestation_sha256"],
    }
    assert (paths["legacy_artifact"] / "baseline.marker").read_text() == "do-not-replace"
    assert not paths["target_artifact"].exists()
    assert not paths["target_report"].exists()
    assert not paths["target_benchmark"].exists()


@pytest.mark.parametrize(
    "mutation", ["gate", "bias", "report", "lock_path", "auxiliary"]
)
def test_tampering_fails_closed_without_deployment(tmp_path: Path, mutation: str) -> None:
    module = _module()
    paths = _fixture(tmp_path, module)
    if mutation == "report":
        paths["candidate_report"].write_text("{}\n", encoding="utf-8")
    elif mutation == "lock_path":
        lock = json.loads(paths["lock_manifest"].read_text(encoding="utf-8"))
        lock["winner"]["locked_artifact_dir"] = "src/hannah_montana_ai/model_store/x"
        _write_json(paths["lock_manifest"], lock)
    elif mutation == "auxiliary":
        auxiliary = paths["project_root"] / module.AUXILIARY_TRAINING_INPUTS[
            "news_auxiliary_training_gold"
        ]
        auxiliary.write_text('{"tampered":true}\n', encoding="utf-8")
    else:
        benchmark = json.loads(paths["benchmark_report"].read_text(encoding="utf-8"))
        if mutation == "gate":
            benchmark["deployment_gate"]["eligible"] = False
        else:
            benchmark["candidate_lock"]["logit_bias_by_domain"]["NEWS_TARGETED"] = [0, 0, 0]
        _write_json(paths["benchmark_report"], benchmark)

    with pytest.raises(module.PromotionError):
        _promote(module, paths)

    assert not paths["current_pointer"].exists()


def test_symlinked_locked_file_fails_closed(tmp_path: Path) -> None:
    module = _module()
    paths = _fixture(tmp_path, module)
    tokenizer = paths["locked_artifact"] / "tokenizer.json"
    replacement = paths["project_root"] / "outside-tokenizer.json"
    replacement.write_bytes(tokenizer.read_bytes())
    tokenizer.unlink()
    tokenizer.symlink_to(replacement)

    with pytest.raises(module.PromotionError, match="일반 파일"):
        _promote(module, paths)

    assert not paths["current_pointer"].exists()


def test_failed_current_activation_preserves_previous_pointer(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _module()
    paths = _fixture(tmp_path, module)
    first = _promote(module, paths)
    original_pointer = paths["current_pointer"].read_bytes()
    real_replace = module.os.replace

    def failing_replace(source: Path | str, destination: Path | str) -> None:
        source_path = Path(source)
        destination_path = Path(destination)
        if (
            destination_path == paths["current_pointer"]
            and "staging" in source_path.name
        ):
            raise OSError("injected install failure")
        real_replace(source, destination)

    monkeypatch.setattr(module.os, "replace", failing_replace)

    with pytest.raises(module.PromotionError):
        _promote(module, paths)

    assert paths["current_pointer"].read_bytes() == original_pointer
    assert json.loads(original_pointer)["release_id"] == first["release_id"]
    assert not any("current-staging" in path.name for path in paths["releases_root"].iterdir())


@pytest.mark.parametrize("target", ("root", "pointer"))
def test_noncanonical_release_activation_target_is_rejected(
    tmp_path: Path,
    target: str,
) -> None:
    module = _module()
    paths = _fixture(tmp_path, module)
    if target == "root":
        paths["releases_root"] = paths["project_root"] / "releases/other"
    else:
        paths["current_pointer"] = paths["releases_root"] / "other.json"

    with pytest.raises(module.PromotionError, match="release root|current"):
        _promote(module, paths)

    assert (paths["legacy_artifact"] / "baseline.marker").read_text() == "do-not-replace"
