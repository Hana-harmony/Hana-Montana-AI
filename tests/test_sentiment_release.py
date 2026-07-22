from __future__ import annotations

import base64
import json
import math
import sys
from contextlib import nullcontext
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from hannah_montana_ai.services import sentiment_release as sentiment_release_module
from hannah_montana_ai.services.model import ModelArtifactInvalidError
from hannah_montana_ai.services.sentiment_release import (
    ARTIFACT_SCHEMA_VERSION,
    AUXILIARY_TRAINING_INPUTS,
    BASE_MODEL,
    BASE_MODEL_REVISION,
    BENCHMARK_SCHEMA_VERSION,
    CANDIDATE_MODEL,
    CONFIRMATORY_METHOD,
    CURRENT_SCHEMA_VERSION,
    DSSE_PAYLOAD_TYPE,
    FAIR_BASELINE_MODEL,
    INPUT_FEATURE_VERSION,
    LABEL_ORDER,
    LOCAL_ATTESTATION_MODE,
    LOCK_SCHEMA_VERSION,
    LOCKED_ARTIFACT_FILES,
    NO_K_ABLATION_MODEL,
    PRE_K_FNSPID_MODEL,
    PRODUCTION_ATTESTATION_MODE,
    RECEIPT_SCHEMA_VERSION,
    REFERENCE_BASELINES,
    RELEASE_SCHEMA_VERSION,
    REQUIRED_EVIDENCE_ROLES,
    REQUIRED_RUNTIME_CODE,
    TRAINING_ARTIFACT_FILES,
    TRAINING_SCHEMA_VERSION,
    SentimentReleaseError,
    VerifiedSentimentRelease,
    expected_sentiment_gate_checks,
    verify_sentiment_release,
)
from hannah_montana_ai.services.sentiment_runtime_parity import (
    base_encoder_evidence,
    build_cpu_serving_parity_evidence,
    build_runtime_parity_lock_commitment,
)
from hannah_montana_ai.services.transformer_sentiment_model import (
    KfDebertaSentimentModel,
)
from hannah_montana_ai.training.sentiment_baseline_commitments import (
    SCHEMA_VERSION as BASELINE_COMMITMENTS_SCHEMA_VERSION,
)
from hannah_montana_ai.training.sentiment_baseline_commitments import (
    baseline_commitments_sha256,
)
from hannah_montana_ai.training.sentiment_evaluation_plan import (
    RECIPE_RELATIVE_PATHS,
    canonical_statistical_analysis_plan,
)
from hannah_montana_ai.training.sentiment_git_attestation import (
    LIMITATIONS as GIT_ATTESTATION_LIMITATIONS,
)

RELEASE_ID = "sentiment-v2-seed17-7f2f7d2d"
VERSION = "hana-montana-kf-deberta-k-fnspid-sentiment-seed17"
GIT_COMMIT = "a" * 40


@dataclass(slots=True)
class ReleaseFixture:
    project_root: Path
    release_root: Path
    release_dir: Path
    current_path: Path
    manifest_path: Path
    artifact_path: Path
    evidence_paths: dict[str, Path]
    base_model_path: Path
    runtime_paths: dict[str, Path]
    manifest: dict[str, Any]
    pointer: dict[str, Any]


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _auxiliary_report(
    tmp_path: Path, *, source: str, include_exclusion_contract: bool
) -> tuple[Path, Path, dict[str, int | str]]:
    gold_path = tmp_path / f"{source.lower()}-auxiliary-gold.jsonl"
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
    commitment: dict[str, int | str] = {
        "path": f"data/training/{source.lower()}-auxiliary-gold.jsonl",
        "bytes": gold_path.stat().st_size,
        "sha256": _sha256(gold_path),
    }
    source_record: dict[str, Any] = {"source_type": source, "sample_count": 1}
    integrity = {
        "exact_item_set": True,
        "independent_dual_review_required": True,
        "model_blind": True,
        "market_blind": True,
        "confirmatory_sampling_commitments_verified": True,
        "promotion_after_confirmatory_reservation": True,
        "source_review_protected_at_confirmatory_reservation": True,
        "write_once": True,
        "confirmatory_group_overlap_count": 0,
    }
    if include_exclusion_contract:
        source_record.update(
            {"review_sample_count": 2, "excluded_unresolved_count": 1}
        )
        integrity["unresolved_rows_excluded"] = True
    report_path = tmp_path / f"{source.lower()}-auxiliary-report.json"
    _write_json(
        report_path,
        {
            "schema_version": "k-fnspid-sentiment-training-reclassification/v2",
            "source": source_record,
            "reclassification": {
                "previous_role": "REPEATEDLY_EXPOSED_DIAGNOSTIC_NOT_CLAIM_EVIDENCE",
                "new_role": "TRAINING_ONLY_NOT_EVALUATION_OR_CLAIM_EVIDENCE",
                "confirmatory_created_before_reclassification": True,
                "eligible_for_confirmatory_metrics": False,
                "eligible_for_evaluation": False,
                "eligible_for_model_selection": False,
                "eligible_for_superiority_claims": False,
            },
            "integrity": integrity,
            "lineage": {"output": commitment},
        },
    )
    return report_path, gold_path, commitment


def test_auxiliary_report_accepts_only_legacy_disclosure_without_new_counts(
    tmp_path: Path,
) -> None:
    report_path, gold_path, commitment = _auxiliary_report(
        tmp_path, source="DISCLOSURE", include_exclusion_contract=False
    )

    sentiment_release_module._validate_auxiliary_training_report(
        report_path,
        source="DISCLOSURE",
        gold_path=gold_path,
        gold_commitment=commitment,
    )

    news_report, news_gold, news_commitment = _auxiliary_report(
        tmp_path, source="NEWS", include_exclusion_contract=False
    )
    with pytest.raises(SentimentReleaseError, match="report 계약"):
        sentiment_release_module._validate_auxiliary_training_report(
            news_report,
            source="NEWS",
            gold_path=news_gold,
            gold_commitment=news_commitment,
        )


def test_auxiliary_report_accepts_news_eligible_subset_counts(tmp_path: Path) -> None:
    report_path, gold_path, commitment = _auxiliary_report(
        tmp_path, source="NEWS", include_exclusion_contract=True
    )

    sentiment_release_module._validate_auxiliary_training_report(
        report_path,
        source="NEWS",
        gold_path=gold_path,
        gold_commitment=commitment,
    )


def _sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()
    return sha256(payload).hexdigest()


def _file_commitment(path: Path, relative: str) -> dict[str, int | str]:
    return {
        "path": relative,
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _directory_manifest(directory: Path) -> dict[str, dict[str, int | str]]:
    return {
        path.relative_to(directory).as_posix(): {
            "bytes": path.stat().st_size,
            "sha256": _sha256(path),
        }
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


def _jackknife_interval(
    *,
    estimate: float = 0.05,
    bounded: bool = False,
    include_p_value: bool = True,
) -> dict[str, float]:
    standard_error = 0.01
    low = estimate - 1.959963984540054 * standard_error
    high = estimate + 1.959963984540054 * standard_error
    if bounded:
        low, high = max(0.0, low), min(1.0, high)
    result = {
        "estimate": estimate,
        "variance": 0.0001,
        "standard_error": standard_error,
        "low": low,
        "high": high,
    }
    if include_p_value:
        result["two_sided_normal_p_value"] = math.erfc(
            abs(estimate / standard_error) / math.sqrt(2.0)
        )
    return result


def _design_jackknife(*, estimate: float, paired: bool) -> dict[str, Any]:
    fields = (
        ("accuracy_difference", "macro_f1_difference")
        if paired
        else ("accuracy", "macro_f1")
    )
    return {
        "method": (
            "paired_stratified_delete_1_jackknife_srswor_fpc/v1"
            if paired
            else "stratified_delete_1_jackknife_srswor_fpc/v1"
        ),
        "resampling_unit": "unique_event_cluster",
        "replicate_count": 600,
        "sample_n_h": {label: 200 for label in LABEL_ORDER},
        "population_N_h": {label: 1_000 for label in LABEL_ORDER},
        **{
            field: _jackknife_interval(
                estimate=estimate,
                bounded=not paired,
                include_p_value=paired,
            )
            for field in fields
        },
    }


def _source_metrics() -> dict[str, Any]:
    models = {
        CANDIDATE_MODEL: {
            "sampling_design_delete_1_jackknife_95_ci": _design_jackknife(
                estimate=0.94, paired=False
            )
        },
        "kr_finbert_sc": {
            "sampling_design_delete_1_jackknife_95_ci": _design_jackknife(
                estimate=0.89, paired=False
            )
        },
        "kr_finbert_sc_raw_off_the_shelf": {
            "sampling_design_delete_1_jackknife_95_ci": _design_jackknife(
                estimate=0.87, paired=False
            )
        },
        PRE_K_FNSPID_MODEL: {
            "sampling_design_delete_1_jackknife_95_ci": _design_jackknife(
                estimate=0.74, paired=False
            )
        },
        FAIR_BASELINE_MODEL: {
            "sampling_design_delete_1_jackknife_95_ci": _design_jackknife(
                estimate=0.86, paired=False
            )
        },
        NO_K_ABLATION_MODEL: {
            "sampling_design_delete_1_jackknife_95_ci": _design_jackknife(
                estimate=0.83, paired=False
            )
        },
    }
    comparisons = {
        f"candidate_vs_{baseline}": {
            "paired_sampling_design_delete_1_jackknife_95_ci": _design_jackknife(
                estimate=0.05, paired=True
            )
        }
        for baseline in REFERENCE_BASELINES
    }
    return {
        "sample_count": 600,
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
        "fair_baseline_accuracy": 0.87,
        "fair_baseline_macro_f1": 0.86,
        "no_k_ablation_accuracy": 0.84,
        "no_k_ablation_macro_f1": 0.83,
        "models": models,
        "statistical_comparisons": comparisons,
    }


def _confirmatory_inference() -> dict[str, Any]:
    interval = _jackknife_interval()
    p_value = interval["two_sided_normal_p_value"]
    sources = {
        source: {
            baseline: {
                "paired_sampling_design_jackknife_95_ci": dict(interval),
                "sampling_design_jackknife_normal_p_value": p_value,
                "holm_adjusted_p_value": p_value * 8,
                "statistically_superior": True,
            }
            for baseline in REFERENCE_BASELINES
        }
        for source in ("NEWS", "DISCLOSURE")
    }
    return {
        "paired_inference": CONFIRMATORY_METHOD,
        "family": (
            "NEWS/DISCLOSURE x raw KR-FinBERT-SC/pre-K-FNSPID/"
            "same-data KR-FinBERT-SC/no-K ablation"
        ),
        "family_hypothesis_count": 8,
        "multiple_comparison_correction": "Holm family-wise alpha=0.05",
        "primary_metric": "sampling-design-weighted plug-in Macro-F1",
        "qwen_confirmatory_exclusion": {
            "model": "Qwen3-4B-GGUF-Q4",
            "role": "blind_teacher_diagnostic_only",
            "affects_deployment_gate": False,
            "included_in_holm_family": False,
        },
        "target_aware_kr_finbert_input_ablation": {
            "role": "candidate_input_format_diagnostic_non_claim"
        },
        "sources": sources,
        "raw_kr_finbert_reference_superiority_claim_allowed": True,
        "pre_k_fnspid_superiority_claim_allowed": True,
        "fair_baseline_superiority_claim_allowed": True,
        "no_k_ablation_superiority_claim_allowed": True,
        "global_sota_claim_allowed": False,
    }


def _build_release(tmp_path: Path) -> ReleaseFixture:
    project_root = tmp_path / "project"
    project_root.mkdir()
    runtime_paths: dict[str, Path] = {}
    for index, relative in enumerate(sorted(REQUIRED_RUNTIME_CODE), start=1):
        path = project_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"runtime-code-{index}\n", encoding="utf-8")
        runtime_paths[relative] = path
    recipe_paths: dict[str, Path] = {}
    for index, (name, relative) in enumerate(RECIPE_RELATIVE_PATHS, start=1):
        path = project_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(f"recipe-code-{index}-{name}\n", encoding="utf-8")
        recipe_paths[name] = path

    base_model_path = project_root / "models/kf-deberta-base"
    base_model_path.mkdir(parents=True)
    _write_json(base_model_path / "config.json", {"model_type": "deberta-v2"})
    (base_model_path / "model.safetensors").write_bytes(b"pinned-base-model")
    base_manifest = _directory_manifest(base_model_path)

    release_root = project_root / "releases/sentiment"
    release_dir = release_root / RELEASE_ID
    artifact_path = release_dir / "artifact"
    evidence_dir = release_dir / "evidence"
    fair_artifact_path = release_dir / "reference-artifacts/same-data-fair-baseline"
    artifact_path.mkdir(parents=True)
    evidence_dir.mkdir()
    fair_artifact_path.mkdir(parents=True)
    _write_json(fair_artifact_path / "hannah_metadata.json", {"version": "fair-v1"})
    (fair_artifact_path / "model.safetensors").write_bytes(b"fair-baseline-model")
    fair_manifest = _directory_manifest(fair_artifact_path)
    _write_json(artifact_path / "adapter_config.json", {"peft_type": "LORA"})
    (artifact_path / "adapter_model.safetensors").write_bytes(b"locked-adapter")
    _write_json(artifact_path / "tokenizer.json", {"version": "1.0"})
    _write_json(artifact_path / "tokenizer_config.json", {"model_max_length": 256})
    training_manifest = _directory_manifest(artifact_path)
    assert set(training_manifest) == set(TRAINING_ARTIFACT_FILES)
    logit_bias_by_domain = {
        "NEWS_UNTARGETED": [0.0, 0.0, 0.0],
        "NEWS_TARGETED": [-0.1, 0.2, -0.1],
        "DISCLOSURE_TARGETED": [-0.2, 0.3, -0.1],
    }
    metadata = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "version": VERSION,
        "base_model": BASE_MODEL,
        "base_model_revision": BASE_MODEL_REVISION,
        "label_order": list(LABEL_ORDER),
        "max_length": 256,
        "input_feature_version": INPUT_FEATURE_VERSION,
        "artifact_files": training_manifest,
        "logit_bias_by_domain": logit_bias_by_domain,
    }
    _write_json(artifact_path / "hannah_metadata.json", metadata)
    artifact_manifest = _directory_manifest(artifact_path)
    assert set(artifact_manifest) == set(LOCKED_ARTIFACT_FILES)
    artifact_manifest_sha256 = _canonical_sha256(artifact_manifest)

    evidence_paths = {
        role: evidence_dir / f"{index:02d}-{role}.evidence"
        for index, role in enumerate(sorted(REQUIRED_EVIDENCE_ROLES), start=1)
    }
    for role, path in evidence_paths.items():
        if role in {
            "training_report",
            "benchmark_report",
            "candidate_lock",
            "candidate_git_attestation",
            "consumption_receipt",
            "sealed_gold_news",
            "sealed_gold_disclosure",
            "gold_promotion_news",
            "gold_promotion_disclosure",
        }:
            continue
        if role == "tfidf_baseline":
            path.write_bytes(b"tfidf-joblib-baseline")
        else:
            _write_json(path, {"role": role, "status": "locked"})
    for source, gold_role, report_role in (
        ("NEWS", "news_auxiliary_training_gold", "news_auxiliary_training_report"),
        (
            "DISCLOSURE",
            "disclosure_auxiliary_training_gold",
            "disclosure_auxiliary_training_report",
        ),
    ):
        gold_path = evidence_paths[gold_role]
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
            evidence_paths[report_role],
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
                        "path": AUXILIARY_TRAINING_INPUTS[gold_role],
                        "bytes": gold_path.stat().st_size,
                        "sha256": _sha256(gold_path),
                    }
                },
            },
        )
    auxiliary_input_records = {
        role: {
            "path": expected_path,
            "bytes": evidence_paths[role].stat().st_size,
            "sha256": _sha256(evidence_paths[role]),
        }
        for role, expected_path in AUXILIARY_TRAINING_INPUTS.items()
    }
    _write_json(
        evidence_paths["fair_baseline_training_report"],
        {
            "schema_version": "k-fnspid-fair-baseline-training/v1",
            "training_strategy": (
                "full-finetune-same-three-way-dual-gold-target-swap-rdrop-hierarchical/v4"
            ),
            "input_artifacts": auxiliary_input_records,
        },
    )

    training = {
        "schema_version": TRAINING_SCHEMA_VERSION,
        "training_strategy": (
            "group-purged-three-way-dual-gold-target-swap-rdrop-hierarchical-upper6-lora/v5"
        ),
        "version": VERSION,
        "base_model": BASE_MODEL,
        "base_model_revision": BASE_MODEL_REVISION,
        "label_order": list(LABEL_ORDER),
        "max_length": 256,
        "input_feature_version": INPUT_FEATURE_VERSION,
        "artifact_files": training_manifest,
        "logit_bias_by_domain": logit_bias_by_domain,
        "input_artifacts": auxiliary_input_records,
    }
    training_path = evidence_paths["training_report"]
    _write_json(training_path, training)

    recipe_blobs = {
        name: _file_commitment(path, dict(RECIPE_RELATIVE_PATHS)[name])
        for name, path in recipe_paths.items()
    }

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
    for source, role, source_path in (
        ("NEWS", "reservation_news", "sealed/reservations/news.json"),
        (
            "DISCLOSURE",
            "reservation_disclosure",
            "sealed/reservations/disclosure.json",
        ),
    ):
        source_rows = reservation_inputs[source]
        sealed_reservations[source] = {
            "path": source_path,
            "bytes": evidence_paths[role].stat().st_size,
            "sha256": _sha256(evidence_paths[role]),
            "sample_count": len(source_rows),
            "item_id_set_sha256": _canonical_sha256(
                sorted(row["item_id"] for row in source_rows)
            ),
            "source_record_set_sha256": _canonical_sha256(
                sorted(source_rows, key=lambda row: row["item_id"])
            ),
        }
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
    base_evidence = base_encoder_evidence(base_model_path, project_root)
    parity_evidence = build_cpu_serving_parity_evidence(
        candidate_version=VERSION,
        candidate_artifact_manifest_sha256=artifact_manifest_sha256,
        reservation_inputs=reservation_inputs,
        evaluator_outputs=parity_outputs,
        packaged_runtime_outputs=parity_outputs,
        evaluator_base_model=base_evidence,
        packaged_runtime_base_model=base_evidence,
        generated_at="2026-07-15T09:00:00+00:00",
    )
    _write_json(evidence_paths["cpu_runtime_parity"], parity_evidence)
    runtime_parity = build_runtime_parity_lock_commitment(
        evidence_path=evidence_paths["cpu_runtime_parity"],
        project_root=project_root,
        expected_candidate_version=VERSION,
        expected_candidate_artifact_manifest_sha256=artifact_manifest_sha256,
        sealed_reservations=sealed_reservations,
    )
    baseline_commitments = {
        "schema_version": BASELINE_COMMITMENTS_SCHEMA_VERSION,
        "confirmatory_labels_used": False,
        "public_test_labels_used": False,
        "baselines": {
            "hana_tfidf_logistic": {"fixture": "locked-before-labels"},
            PRE_K_FNSPID_MODEL: {"fixture": "locked-before-labels"},
            FAIR_BASELINE_MODEL: {"fixture": "locked-before-labels"},
            NO_K_ABLATION_MODEL: {"fixture": "locked-before-labels"},
        },
    }
    baseline_digest = baseline_commitments_sha256(baseline_commitments)

    lock = {
        "schema_version": LOCK_SCHEMA_VERSION,
        "selection_only": True,
        "external_git_commitment_required": True,
        "winner": {
            "version": VERSION,
            "report_path": "reports/candidates/seed17.json",
            "report_sha256": _sha256(training_path),
            "artifact_files": artifact_manifest,
        },
        "sealed_reservations": sealed_reservations,
        "dataset_provenance": {
            "codebook": {
                "path": "docs/sentiment-codebook.md",
                "bytes": 1,
                "sha256": "1" * 64,
            },
            "sampling_implementation": {
                "path": "src/sentiment-sampling.py",
                "bytes": 1,
                "sha256": "2" * 64,
            },
            "dataset_reports": {
                "NEWS": {
                    "path": "reports/news-dataset.json",
                    "bytes": 1,
                    "sha256": "3" * 64,
                },
                "DISCLOSURE": {
                    "path": "reports/disclosure-dataset.json",
                    "bytes": 1,
                    "sha256": "4" * 64,
                },
                "SAMPLING_DESIGN": {
                    "path": "reports/sampling-dataset.json",
                    "bytes": 1,
                    "sha256": "5" * 64,
                },
            },
        },
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
    lock_path = evidence_paths["candidate_lock"]
    _write_json(lock_path, lock)
    committed_reservations = {
        source: {
            key: lock["sealed_reservations"][source][key]
            for key in ("path", "bytes", "sha256")
        }
        for source in ("NEWS", "DISCLOSURE")
    }
    attestation = {
        "schema_version": "sentiment-candidate-git-attestation/v1",
        "role": "REMOTE_GIT_HISTORY_COMMITMENT_NOT_INDEPENDENT_TIMESTAMP",
        "git": {
            "commit_sha": GIT_COMMIT,
            "tree_sha": "b" * 40,
            "committer_time_iso": "2026-07-15T10:00:00+00:00",
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
            "sealed_reservations": committed_reservations,
            "dataset_provenance": lock["dataset_provenance"],
            "code_provenance": {
                "training_script": recipe_blobs["candidate_trainer"]
            },
            "recipe_blobs": recipe_blobs,
            "baseline_commitments": baseline_commitments,
            "baseline_commitments_sha256": baseline_digest,
            "runtime_parity": runtime_parity,
            "runtime_parity_evidence": runtime_parity["evidence"],
        },
        "limitations": list(GIT_ATTESTATION_LIMITATIONS),
        "attested_at": "2026-07-15T11:00:00+00:00",
    }
    _write_json(evidence_paths["candidate_git_attestation"], attestation)
    normalized_attestation = {
        "schema_version": attestation["schema_version"],
        "role": attestation["role"],
        "path": "reports/sentiment-candidate-git-attestation.json",
        "sha256": _sha256(evidence_paths["candidate_git_attestation"]),
        "attested_at": attestation["attested_at"],
        "commit_sha": attestation["git"]["commit_sha"],
        "tree_sha": attestation["git"]["tree_sha"],
        "committer_time_iso": attestation["git"]["committer_time_iso"],
        "remote_name": attestation["git"]["remote_name"],
        "remote_tracking_ref": attestation["git"]["remote_tracking_ref"],
        "candidate_lock_path": "reports/sentiment-candidate-lock.json",
        "candidate_lock_sha256": _sha256(lock_path),
        "committed_artifact_manifests": attestation[
            "committed_artifact_manifests"
        ],
        "limitations": list(GIT_ATTESTATION_LIMITATIONS),
    }
    gold_commitment = {
        "candidate_manifest_sha256": _sha256(lock_path),
        "candidate_git_attestation_sha256": normalized_attestation["sha256"],
        "candidate_git_commit_sha": GIT_COMMIT,
    }
    for source, gold_role, promotion_role in (
        ("NEWS", "sealed_gold_news", "gold_promotion_news"),
        ("DISCLOSURE", "sealed_gold_disclosure", "gold_promotion_disclosure"),
    ):
        evidence_paths[gold_role].write_text(
            json.dumps(
                {
                    "source_type": source,
                    "sentiment": "NEUTRAL",
                    **gold_commitment,
                },
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        _write_json(
            evidence_paths[promotion_role],
            {
                "status": "pass",
                "provenance": {"codex_review": dict(gold_commitment)},
            },
        )

    same_data_contract = {
        "matched_input_artifacts": auxiliary_input_records,
    }
    same_data_contract_sha256 = _canonical_sha256(same_data_contract)
    receipt = {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "candidate_version": VERSION,
        "candidate_lock_manifest_sha256": _sha256(lock_path),
        "candidate_artifact_manifest_sha256": artifact_manifest_sha256,
        "candidate_git_attestation": normalized_attestation,
        "locked_baseline_commitments": baseline_commitments,
        "locked_baseline_commitments_sha256": baseline_digest,
        "cpu_runtime_parity": runtime_parity,
        "sealed_gold": {
            "NEWS": {
                "path": "sealed/gold/news.jsonl",
                "sha256": _sha256(evidence_paths["sealed_gold_news"]),
            },
            "DISCLOSURE": {
                "path": "sealed/gold/disclosure.jsonl",
                "sha256": _sha256(evidence_paths["sealed_gold_disclosure"]),
            },
        },
        "promotion_reports": {
            "NEWS": {
                "path": "reports/gold-promotion-news.json",
                "sha256": _sha256(evidence_paths["gold_promotion_news"]),
            },
            "DISCLOSURE": {
                "path": "reports/gold-promotion-disclosure.json",
                "sha256": _sha256(evidence_paths["gold_promotion_disclosure"]),
            },
        },
        "sampling_design_report": {
            "path": "reports/sampling-design.json",
            "sha256": _sha256(evidence_paths["sampling_design"]),
        },
        "baseline_artifacts": {
            "hana_tfidf_logistic": {
                "path": "models/financial_nlp_ml.joblib",
                "sha256": _sha256(evidence_paths["tfidf_baseline"]),
            },
            "pre_k_fnspid_kf_deberta": {
                "artifact_dir": "models/pre-k-fnspid",
                "metadata_sha256": _sha256(evidence_paths["pre_k_fnspid_metadata"]),
                "training_report_path": "reports/pre-k-fnspid-training.json",
                "training_report_sha256": _sha256(
                    evidence_paths["pre_k_fnspid_training_report"]
                ),
            },
            FAIR_BASELINE_MODEL: {
                "artifact_dir": "artifacts/fair/seed17",
                "artifact_manifest_sha256": _canonical_sha256(fair_manifest),
                "metadata_sha256": _sha256(
                    fair_artifact_path / "hannah_metadata.json"
                ),
                "selection_report_path": "reports/fair/selection.json",
                "selection_report_sha256": _sha256(
                    evidence_paths["fair_baseline_selection_report"]
                ),
                "training_report_path": "reports/fair/seed17.json",
                "training_report_sha256": _sha256(
                    evidence_paths["fair_baseline_training_report"]
                ),
                "same_data_contract_sha256": same_data_contract_sha256,
            },
            NO_K_ABLATION_MODEL: baseline_commitments["baselines"][
                NO_K_ABLATION_MODEL
            ],
        },
        "evaluation_script_sha256": _sha256(
            runtime_paths["scripts/evaluate_locked_kf_deberta_sentiment.py"]
        ),
    }
    receipt_path = evidence_paths["consumption_receipt"]
    _write_json(receipt_path, receipt)

    benchmark = {
        "schema_version": BENCHMARK_SCHEMA_VERSION,
        "input_feature_version": INPUT_FEATURE_VERSION,
        "candidate_lock": {
            "schema_version": LOCK_SCHEMA_VERSION,
            "selection_only": True,
            "manifest_path": "reports/sentiment-candidate-lock.json",
            "manifest_sha256": _sha256(lock_path),
            "version": VERSION,
            "candidate_report_path": "reports/candidates/seed17.json",
            "candidate_report_sha256": _sha256(training_path),
            "artifact_files": artifact_manifest,
            "artifact_manifest_sha256": artifact_manifest_sha256,
            "logit_bias_by_domain": logit_bias_by_domain,
        },
        "sealed_evaluation_consumption": {
            **receipt,
            "receipt_path": "reports/sentiment-consumption.json",
            "receipt_sha256": _sha256(receipt_path),
        },
        "sampling_design": {
            "report_path": "reports/sampling-design.json",
            "report_sha256": _sha256(evidence_paths["sampling_design"]),
        },
        "same_data_fair_baseline": {
            "same_data_contract": same_data_contract,
            "same_data_contract_sha256": same_data_contract_sha256,
            "same_data_split_selection_budget_verified": True,
            "public_test_labels_used_for_training_or_selection": False,
            "confirmatory_labels_used_for_training_or_selection": False,
        },
        "cpu_runtime_parity": runtime_parity,
        "confirmatory_inference": _confirmatory_inference(),
        "source_sealed_gold": {
            "NEWS": _source_metrics(),
            "DISCLOSURE": _source_metrics(),
        },
        "public_test": {
            "sample_count": 1_000,
            "accuracy": 0.93,
            "macro_f1": 0.92,
            "kr_finbert_sc_accuracy": 0.89,
            "kr_finbert_sc_macro_f1": 0.88,
            "kr_finbert_sc_raw_accuracy": 0.87,
            "kr_finbert_sc_raw_macro_f1": 0.86,
            "pre_k_fnspid_accuracy": 0.78,
            "pre_k_fnspid_macro_f1": 0.77,
            "fair_baseline_accuracy": 0.86,
            "fair_baseline_macro_f1": 0.85,
            "no_k_ablation_accuracy": 0.84,
            "no_k_ablation_macro_f1": 0.83,
        },
    }
    benchmark["deployment_gate"] = {
        "candidate_model": CANDIDATE_MODEL,
        "candidate_version": VERSION,
        "candidate_artifact_manifest_sha256": artifact_manifest_sha256,
        "thresholds": {
            "minimum_sealed_sample_count_per_source": 500,
            "minimum_sealed_accuracy_per_source": 0.90,
            "minimum_sealed_macro_f1_per_source": 0.85,
            "sealed_must_match_or_exceed_reference_family": [
                "target-aware snunlp/KR-FinBERT-SC",
                "raw snunlp/KR-FinBERT-SC",
                "same-data/split/selection-budget full-finetuned snunlp/KR-FinBERT-SC",
                "locked KF-DeBERTa no-K-FNSPID ablation",
            ],
            "blind_teacher_diagnostic_only_not_gating": "Qwen3-4B-GGUF-Q4",
            "confirmatory_superiority_requires": (
                "positive delete-1 jackknife lower bound and Holm-adjusted p<0.05"
            ),
        },
        "secondary_regression_diagnostics": {
            "role": "repeatedly_exposed_secondary_regression_set_non_gating",
            "affects_deployment_decision": False,
        },
        "checks": {},
        "eligible": True,
        "decision": "DEPLOY_HANA_MONTANA_AI",
    }
    benchmark["deployment_gate"]["checks"] = expected_sentiment_gate_checks(benchmark)
    benchmark_path = evidence_paths["benchmark_report"]
    _write_json(benchmark_path, benchmark)

    evidence = {
        role: _file_commitment(path, f"evidence/{path.name}")
        for role, path in evidence_paths.items()
    }
    runtime_code = {
        relative: _file_commitment(path, relative)
        for relative, path in runtime_paths.items()
    }
    manifest = {
        "schema_version": RELEASE_SCHEMA_VERSION,
        "release_id": RELEASE_ID,
        "source": {
            "git_commit": GIT_COMMIT,
            "dirty": False,
            "candidate_lock_git_commit": GIT_COMMIT,
            "candidate_lock_git_tree": attestation["git"]["tree_sha"],
            "candidate_git_attestation_sha256": normalized_attestation["sha256"],
        },
        "candidate": {
            "name": CANDIDATE_MODEL,
            "version": VERSION,
            "input_feature_version": INPUT_FEATURE_VERSION,
            "label_order": list(LABEL_ORDER),
            "max_length": 256,
        },
        "artifact": {
            "path": "artifact",
            "files": artifact_manifest,
            "manifest_sha256": artifact_manifest_sha256,
        },
        "base_model": {
            "model_id": BASE_MODEL,
            "revision": BASE_MODEL_REVISION,
            "runtime_path": str(base_model_path),
            "files": base_manifest,
            "manifest_sha256": _canonical_sha256(base_manifest),
        },
        "evidence": evidence,
        "reference_artifacts": {
            FAIR_BASELINE_MODEL: {
                "path": "reference-artifacts/same-data-fair-baseline",
                "files": fair_manifest,
                "manifest_sha256": _canonical_sha256(fair_manifest),
                "metadata_sha256": _sha256(
                    fair_artifact_path / "hannah_metadata.json"
                ),
                "same_data_contract_sha256": same_data_contract_sha256,
            }
        },
        "runtime_code": runtime_code,
        "dependency_lock": runtime_code["uv.lock"],
    }
    manifest_path = release_dir / "release.json"
    _write_json(manifest_path, manifest)
    pointer = {
        "schema_version": CURRENT_SCHEMA_VERSION,
        "release_id": RELEASE_ID,
        "release_manifest_path": f"{RELEASE_ID}/release.json",
        "release_manifest": _file_commitment(
            manifest_path,
            f"{RELEASE_ID}/release.json",
        ),
        "attestation": {
            "mode": LOCAL_ATTESTATION_MODE,
            "production_eligible": False,
        },
    }
    current_path = release_root / "current.json"
    _write_json(current_path, pointer)
    return ReleaseFixture(
        project_root=project_root,
        release_root=release_root,
        release_dir=release_dir,
        current_path=current_path,
        manifest_path=manifest_path,
        artifact_path=artifact_path,
        evidence_paths=evidence_paths,
        base_model_path=base_model_path,
        runtime_paths=runtime_paths,
        manifest=manifest,
        pointer=pointer,
    )


@pytest.fixture
def release_fixture(tmp_path: Path) -> ReleaseFixture:
    return _build_release(tmp_path)


def _rewrite_pointer(fixture: ReleaseFixture) -> None:
    _write_json(fixture.current_path, fixture.pointer)


def _rewrite_manifest(fixture: ReleaseFixture) -> None:
    _write_json(fixture.manifest_path, fixture.manifest)
    fixture.pointer["release_manifest"] = _file_commitment(
        fixture.manifest_path,
        f"{RELEASE_ID}/release.json",
    )
    _rewrite_pointer(fixture)


def _verify_local(fixture: ReleaseFixture) -> VerifiedSentimentRelease:
    return verify_sentiment_release(
        fixture.current_path,
        fixture.base_model_path,
        project_root=fixture.project_root,
        runtime_environment="test",
        attestation_mode=LOCAL_ATTESTATION_MODE,
    )


def _dsse_pae(payload_type: str, payload: bytes) -> bytes:
    type_bytes = payload_type.encode()
    return b"DSSEv1 %d %s %d %s" % (
        len(type_bytes),
        type_bytes,
        len(payload),
        payload,
    )


def _enable_production_dsse(
    fixture: ReleaseFixture,
) -> tuple[Path, str, Path]:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    public_key_path = fixture.project_root / "release-signing-public.pem"
    public_key_path.write_bytes(
        public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )
    raw_public_key = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    signer_key_id = sha256(raw_public_key).hexdigest()
    payload = fixture.manifest_path.read_bytes()
    signature = private_key.sign(_dsse_pae(DSSE_PAYLOAD_TYPE, payload))
    envelope = {
        "payloadType": DSSE_PAYLOAD_TYPE,
        "payload": base64.b64encode(payload).decode(),
        "signatures": [
            {
                "keyid": signer_key_id,
                "sig": base64.b64encode(signature).decode(),
            }
        ],
    }
    envelope_path = fixture.release_dir / "release.dsse.json"
    _write_json(envelope_path, envelope)
    fixture.pointer["attestation"] = {
        "mode": PRODUCTION_ATTESTATION_MODE,
        "production_eligible": True,
        "envelope": _file_commitment(
            envelope_path,
            f"{RELEASE_ID}/release.dsse.json",
        ),
    }
    _rewrite_pointer(fixture)
    return public_key_path, signer_key_id, envelope_path


def _verify_production(
    fixture: ReleaseFixture,
    public_key_path: Path,
    signer_key_id: str,
    *,
    expected_release_id: str = RELEASE_ID,
    expected_git_commit: str = GIT_COMMIT,
) -> VerifiedSentimentRelease:
    return verify_sentiment_release(
        fixture.current_path,
        fixture.base_model_path,
        project_root=fixture.project_root,
        runtime_environment="production",
        attestation_mode=PRODUCTION_ATTESTATION_MODE,
        public_key_path=public_key_path,
        signer_key_id=signer_key_id,
        expected_release_id=expected_release_id,
        expected_git_commit=expected_git_commit,
    )


def test_valid_local_untrusted_release_is_verified(
    release_fixture: ReleaseFixture,
) -> None:
    verified = _verify_local(release_fixture)

    assert verified.release_id == RELEASE_ID
    assert verified.version == VERSION
    assert verified.artifact_path == release_fixture.artifact_path
    assert verified.base_model_path == release_fixture.base_model_path


def test_artifact_byte_tamper_fails_closed(release_fixture: ReleaseFixture) -> None:
    (release_fixture.artifact_path / "adapter_model.safetensors").write_bytes(b"tampered")

    with pytest.raises(SentimentReleaseError, match="artifact.*hash"):
        _verify_local(release_fixture)


def test_fair_baseline_artifact_tamper_fails_closed(
    release_fixture: ReleaseFixture,
) -> None:
    fair_model = (
        release_fixture.release_dir
        / "reference-artifacts/same-data-fair-baseline/model.safetensors"
    )
    fair_model.write_bytes(b"tampered-fair-baseline")

    with pytest.raises(SentimentReleaseError, match="공정 기준선 artifact.*hash"):
        _verify_local(release_fixture)


def test_missing_evidence_fails_closed(release_fixture: ReleaseFixture) -> None:
    release_fixture.evidence_paths["sealed_gold_news"].unlink()

    with pytest.raises(SentimentReleaseError, match="evidence sealed_gold_news"):
        _verify_local(release_fixture)


def test_evidence_commitment_tamper_fails_closed(release_fixture: ReleaseFixture) -> None:
    release_fixture.manifest["evidence"]["sampling_design"]["sha256"] = "0" * 64
    _rewrite_manifest(release_fixture)

    with pytest.raises(SentimentReleaseError, match="evidence sampling_design hash"):
        _verify_local(release_fixture)


def test_auxiliary_gold_self_consistent_outer_tamper_fails_closed(
    release_fixture: ReleaseFixture,
) -> None:
    path = release_fixture.evidence_paths["news_auxiliary_training_gold"]
    path.write_text('{"tampered":true}\n', encoding="utf-8")
    release_fixture.manifest["evidence"]["news_auxiliary_training_gold"] = (
        _file_commitment(path, f"evidence/{path.name}")
    )
    _rewrite_manifest(release_fixture)

    with pytest.raises(SentimentReleaseError, match="학습 입력 commitment"):
        _verify_local(release_fixture)


def test_base_model_byte_mismatch_fails_closed(release_fixture: ReleaseFixture) -> None:
    (release_fixture.base_model_path / "model.safetensors").write_bytes(b"different-base")

    with pytest.raises(SentimentReleaseError, match="base model.*hash"):
        _verify_local(release_fixture)


def test_base_model_runtime_path_mismatch_fails_closed(
    release_fixture: ReleaseFixture,
) -> None:
    other_path = release_fixture.project_root / "models/uncommitted-base"
    other_path.mkdir()

    with pytest.raises(SentimentReleaseError, match="runtime 경로"):
        verify_sentiment_release(
            release_fixture.current_path,
            other_path,
            project_root=release_fixture.project_root,
            runtime_environment="test",
            attestation_mode=LOCAL_ATTESTATION_MODE,
        )


def test_runtime_code_mismatch_fails_closed(release_fixture: ReleaseFixture) -> None:
    runtime_path = release_fixture.runtime_paths[
        "src/hannah_montana_ai/services/sentiment_input.py"
    ]
    runtime_path.write_text("changed-after-release\n", encoding="utf-8")

    with pytest.raises(SentimentReleaseError, match="runtime code.*hash"):
        _verify_local(release_fixture)


def test_dependency_lock_commitment_mismatch_fails_closed(
    release_fixture: ReleaseFixture,
) -> None:
    release_fixture.manifest["dependency_lock"] = release_fixture.manifest["runtime_code"][
        "pyproject.toml"
    ]
    _rewrite_manifest(release_fixture)

    with pytest.raises(SentimentReleaseError, match="dependency lock"):
        _verify_local(release_fixture)


def test_candidate_git_attestation_semantic_tamper_fails_closed(
    release_fixture: ReleaseFixture,
) -> None:
    path = release_fixture.evidence_paths["candidate_git_attestation"]
    attestation = json.loads(path.read_text(encoding="utf-8"))
    attestation["git"]["commit_is_ancestor_of_remote_tracking_ref"] = False
    _write_json(path, attestation)
    release_fixture.manifest["evidence"]["candidate_git_attestation"] = _file_commitment(
        path,
        f"evidence/{path.name}",
    )
    _rewrite_manifest(release_fixture)

    with pytest.raises(SentimentReleaseError, match="remote commitment"):
        _verify_local(release_fixture)


def test_partial_pointer_fails_closed(release_fixture: ReleaseFixture) -> None:
    del release_fixture.pointer["release_manifest"]
    _rewrite_pointer(release_fixture)

    with pytest.raises(SentimentReleaseError, match="release manifest"):
        _verify_local(release_fixture)


def test_pointer_to_missing_manifest_fails_closed(release_fixture: ReleaseFixture) -> None:
    release_fixture.manifest_path.unlink()

    with pytest.raises(SentimentReleaseError, match="release manifest.*없습니다"):
        _verify_local(release_fixture)


def test_partial_release_manifest_fails_closed(release_fixture: ReleaseFixture) -> None:
    del release_fixture.manifest["runtime_code"]
    _rewrite_manifest(release_fixture)

    with pytest.raises(SentimentReleaseError, match="runtime code"):
        _verify_local(release_fixture)


def test_production_rejects_local_untrusted_release(
    release_fixture: ReleaseFixture,
) -> None:
    with pytest.raises(SentimentReleaseError, match="production.*DSSE"):
        verify_sentiment_release(
            release_fixture.current_path,
            release_fixture.base_model_path,
            project_root=release_fixture.project_root,
            runtime_environment="production",
            attestation_mode=LOCAL_ATTESTATION_MODE,
            expected_release_id=RELEASE_ID,
            expected_git_commit=GIT_COMMIT,
        )


def test_real_ed25519_dsse_release_is_verified(
    release_fixture: ReleaseFixture,
) -> None:
    public_key_path, signer_key_id, _ = _enable_production_dsse(release_fixture)

    verified = _verify_production(release_fixture, public_key_path, signer_key_id)

    assert verified.release_id == RELEASE_ID
    assert verified.version == VERSION


def test_ed25519_signature_tamper_fails_closed(
    release_fixture: ReleaseFixture,
) -> None:
    public_key_path, signer_key_id, envelope_path = _enable_production_dsse(release_fixture)
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    signature = bytearray(base64.b64decode(envelope["signatures"][0]["sig"]))
    signature[0] ^= 1
    envelope["signatures"][0]["sig"] = base64.b64encode(signature).decode()
    _write_json(envelope_path, envelope)
    release_fixture.pointer["attestation"]["envelope"] = _file_commitment(
        envelope_path,
        f"{RELEASE_ID}/release.dsse.json",
    )
    _rewrite_pointer(release_fixture)

    with pytest.raises(SentimentReleaseError, match="DSSE 서명 검증"):
        _verify_production(release_fixture, public_key_path, signer_key_id)


@pytest.mark.parametrize(
    ("expected_release_id", "expected_git_commit", "message"),
    (
        ("different-release", GIT_COMMIT, "release ID"),
        (RELEASE_ID, "b" * 40, "Git commit"),
    ),
)
def test_production_rejects_expected_release_or_git_mismatch(
    release_fixture: ReleaseFixture,
    expected_release_id: str,
    expected_git_commit: str,
    message: str,
) -> None:
    public_key_path, signer_key_id, _ = _enable_production_dsse(release_fixture)

    with pytest.raises(SentimentReleaseError, match=message):
        _verify_production(
            release_fixture,
            public_key_path,
            signer_key_id,
            expected_release_id=expected_release_id,
            expected_git_commit=expected_git_commit,
        )


def _install_fake_transformer_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeTokenizer:
        cls_token_id = 1
        sep_token_id = 2
        model_input_names = ["input_ids", "attention_mask"]

        @classmethod
        def from_pretrained(cls, *_args: object, **_kwargs: object) -> FakeTokenizer:
            return cls()

        def encode(self, _text: str, *, add_special_tokens: bool) -> list[int]:
            assert add_special_tokens is False
            return [10, 11, 12]

        def num_special_tokens_to_add(self, *, pair: bool) -> int:
            assert pair is False
            return 2

    class FakeValues:
        def cpu(self) -> FakeValues:
            return self

        def tolist(self) -> list[float]:
            return [0.2, 0.3, 0.5]

    class FakeLogits:
        def __getitem__(self, index: int) -> FakeLogits:
            assert index == 0
            return self

        def new_tensor(self, _value: object) -> FakeLogits:
            return self

        def __add__(self, _other: object) -> FakeLogits:
            return self

    class FakeModel:
        @classmethod
        def from_pretrained(cls, *_args: object, **_kwargs: object) -> FakeModel:
            return cls()

        def eval(self) -> None:
            return None

        def __call__(self, **_kwargs: object) -> object:
            return type("Output", (), {"logits": FakeLogits()})()

    torch_module = ModuleType("torch")
    torch_module.tensor = lambda value: value  # type: ignore[attr-defined]
    torch_module.softmax = lambda _value, dim: FakeValues()  # type: ignore[attr-defined]
    torch_module.inference_mode = nullcontext  # type: ignore[attr-defined]
    peft_module = ModuleType("peft")
    peft_module.PeftModel = FakeModel  # type: ignore[attr-defined]
    transformers_module = ModuleType("transformers")
    transformers_module.AutoTokenizer = FakeTokenizer  # type: ignore[attr-defined]
    transformers_module.AutoModelForSequenceClassification = FakeModel  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "torch", torch_module)
    monkeypatch.setitem(sys.modules, "peft", peft_module)
    monkeypatch.setitem(sys.modules, "transformers", transformers_module)


def test_runtime_loads_exact_current_release_and_predicts(
    release_fixture: ReleaseFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_fake_transformer_runtime(monkeypatch)

    model = KfDebertaSentimentModel(
        release_fixture.project_root / "legacy-artifact",
        release_fixture.project_root / "legacy-training.json",
        release_fixture.project_root / "legacy-benchmark.json",
        release_fixture.base_model_path,
        release_current_path=release_fixture.current_path,
        project_root=release_fixture.project_root,
        runtime_environment="test",
    )

    assert model.enabled is True
    assert model.release_id == RELEASE_ID
    assert model.version == VERSION
    assert model.probabilities("실적이 개선됐다", "NEWS") == {
        "NEGATIVE": 0.2,
        "NEUTRAL": 0.3,
        "POSITIVE": 0.5,
    }


def test_runtime_does_not_fallback_when_current_release_is_tampered(
    release_fixture: ReleaseFixture,
) -> None:
    release_fixture.pointer["release_manifest"]["sha256"] = "0" * 64
    _rewrite_pointer(release_fixture)

    with pytest.raises(ModelArtifactInvalidError, match="활성 sentiment release 검증 실패"):
        KfDebertaSentimentModel(
            release_fixture.project_root / "legacy-artifact",
            release_fixture.project_root / "legacy-training.json",
            release_fixture.project_root / "legacy-benchmark.json",
            release_fixture.base_model_path,
            release_current_path=release_fixture.current_path,
            project_root=release_fixture.project_root,
            runtime_environment="test",
        )


def test_production_runtime_requires_current_release(tmp_path: Path) -> None:
    with pytest.raises(ModelArtifactInvalidError, match="current release"):
        KfDebertaSentimentModel(
            tmp_path / "legacy-artifact",
            tmp_path / "legacy-training.json",
            tmp_path / "legacy-benchmark.json",
            tmp_path / "base-model",
            release_current_path=tmp_path / "releases/sentiment/current.json",
            project_root=tmp_path,
            runtime_environment="production",
            release_attestation_mode=PRODUCTION_ATTESTATION_MODE,
        )
