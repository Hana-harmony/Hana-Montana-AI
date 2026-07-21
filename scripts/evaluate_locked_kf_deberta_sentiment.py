from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import tempfile
from collections import Counter
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)

from hannah_montana_ai.services.kr_finbert_sc_raw_reference import (
    BASE_MODEL as RAW_REFERENCE_MODEL_REPOSITORY,
)
from hannah_montana_ai.services.kr_finbert_sc_raw_reference import (
    BASE_MODEL_REVISION as RAW_REFERENCE_MODEL_REVISION,
)
from hannah_montana_ai.services.kr_finbert_sc_raw_reference import (
    load_raw_reference_model,
)
from hannah_montana_ai.services.kr_finbert_sc_v6_baseline import (
    load_kr_finbert_sc_v6_runtime,
    validate_kr_finbert_sc_v6_artifact,
)
from hannah_montana_ai.services.model_artifact_integrity import (
    verify_artifact_manifest,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    BENCHMARK_SCHEMA_VERSION as V6_BENCHMARK_SCHEMA_VERSION,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    CANDIDATE_MODEL as V6_CANDIDATE_MODEL,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    LOCK_SCHEMA_VERSION as V6_LOCK_SCHEMA_VERSION,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    MODEL_FAMILY as V6_MODEL_FAMILY,
)
from hannah_montana_ai.services.sentiment_artifact_contract import (
    validate_source_hierarchical_artifact,
    validate_source_hierarchical_base_directory,
)
from hannah_montana_ai.services.sentiment_input import (
    encode_sentiment_input,
    sentiment_source_domain,
    validated_sentiment_logit_biases,
)
from hannah_montana_ai.services.sentiment_runtime_parity import (
    validate_runtime_parity_lock_commitment,
)
from hannah_montana_ai.services.source_hierarchical_sentiment import (
    load_source_hierarchical_runtime,
    validate_domain_calibration,
)
from hannah_montana_ai.training.dataset import load_labeled_alerts
from hannah_montana_ai.training.sentiment_baseline_commitments import (
    baseline_commitments_sha256,
    validate_confirmatory_baseline_commitments,
)
from hannah_montana_ai.training.sentiment_evaluation_plan import (
    CANDIDATE_MODEL_NAME,
    CONFIRMATORY_BASELINE_MODEL_NAMES,
    DEFAULT_BOOTSTRAP_SAMPLES,
    DEFAULT_BOOTSTRAP_SEED,
    EVALUATION_BATCH_SIZE,
    FAIR_BASELINE_MODEL_NAME,
    FAMILYWISE_ALPHA,
    MIN_PUBLIC_MACRO_F1,
    MIN_SEALED_ACCURACY,
    MIN_SEALED_MACRO_F1,
    MIN_SEALED_SAMPLE_COUNT,
    NO_K_ABLATION_MODEL_NAME,
    PRE_K_FNSPID_MODEL_NAME,
    QWEN_TEACHER_MODEL_NAME,
    RECIPE_RELATIVE_PATHS,
    canonical_statistical_analysis_plan,
    validate_evaluation_runtime_parameters,
    validate_statistical_analysis_plan,
)
from hannah_montana_ai.training.sentiment_git_attestation import (
    validate_candidate_git_attestation,
)
from hannah_montana_ai.training.sentiment_protocol import decontaminate_public_partitions
from hannah_montana_ai.training.sentiment_sampling import prevalence_sampling_stratum
from hannah_montana_ai.training.sentiment_v6_evaluation_contract import (
    CONFIRMATORY_BASELINES as V6_CONFIRMATORY_BASELINES,
)
from hannah_montana_ai.training.sentiment_v6_evaluation_contract import (
    CONFIRMATORY_SOURCES,
    V6_CANDIDATE_MODEL_NAME,
    V6_FAIR_BASELINE_MODEL_NAME,
    V6_NO_K_ABLATION_MODEL_NAME,
    v6_baseline_paths,
    validate_v6_confirmatory_baseline_commitments,
    validate_v6_evaluation_runtime_parameters,
    validate_v6_statistical_analysis_plan,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCK_MANIFEST = PROJECT_ROOT / "reports/sentiment-candidate-lock.json"
DEFAULT_GIT_ATTESTATION = PROJECT_ROOT / "reports/sentiment-candidate-git-attestation.json"
DEFAULT_LOCKED_ARTIFACT = PROJECT_ROOT / "artifacts/sentiment/locked"
DEFAULT_PUBLIC_DATASET = PROJECT_ROOT / "data/external/kf_deberta_benchmark"
DEFAULT_NEWS_SEALED_GOLD = (
    PROJECT_ROOT / "data/evaluation/k_fnspid_sentiment_confirmatory_sealed_gold.jsonl"
)
DEFAULT_DISCLOSURE_SEALED_GOLD = (
    PROJECT_ROOT / "data/evaluation/k_fnspid_disclosure_sentiment_confirmatory_sealed_gold.jsonl"
)
DEFAULT_NEWS_SEALED_PROMOTION_REPORT = (
    PROJECT_ROOT / "reports/k-fnspid-sentiment-confirmatory-sealed-gold-promotion-report.json"
)
DEFAULT_DISCLOSURE_SEALED_PROMOTION_REPORT = (
    PROJECT_ROOT
    / "reports/k-fnspid-disclosure-sentiment-confirmatory-sealed-gold-promotion-report.json"
)
DEFAULT_SAMPLING_DESIGN_REPORT = (
    PROJECT_ROOT / "reports/k-fnspid-sentiment-confirmatory-sealed-sampling-design-v2.json"
)
DEFAULT_LEGACY_NEWS_GOLD = PROJECT_ROOT / "data/evaluation/financial_alert_real_news_gold.jsonl"
DEFAULT_LEGACY_DISCLOSURE_GOLD = (
    PROJECT_ROOT / "data/evaluation/financial_alert_real_disclosure_gold.jsonl"
)
DEFAULT_TFIDF_MODEL = PROJECT_ROOT / "src/hannah_montana_ai/model_store/financial_nlp_ml.joblib"
DEFAULT_RAW_REFERENCE_ARTIFACT = PROJECT_ROOT / "models/kr-finbert-sc-raw-reference"
DEFAULT_PRE_K_FNSPID_ARTIFACT = (
    PROJECT_ROOT / "src/hannah_montana_ai/model_store/kf_deberta_sentiment"
)
DEFAULT_PRE_K_FNSPID_TRAINING_REPORT = (
    PROJECT_ROOT / "reports/kf-deberta-sentiment-training-report-pre-k-fnspid.json"
)
DEFAULT_FAIR_BASELINE_ARTIFACT_ROOT = (
    PROJECT_ROOT / "artifacts/sentiment/fair_baselines/kr-finbert-sc"
)
DEFAULT_FAIR_BASELINE_SELECTION_REPORT = (
    PROJECT_ROOT / "reports/fair_baselines/kr-finbert-sc/selection.json"
)
DEFAULT_V6_FAIR_BASELINE_ARTIFACT_ROOT = (
    PROJECT_ROOT / "artifacts/sentiment/fair_baselines/kr-finbert-sc-v6"
)
DEFAULT_V6_FAIR_BASELINE_SELECTION_REPORT = (
    PROJECT_ROOT / "reports/fair_baselines/kr-finbert-sc-v6/selection.json"
)
DEFAULT_REPORT = PROJECT_ROOT / "reports/korean-finance-sentiment-benchmark-v4.json"
DEFAULT_CONSUMPTION_RECEIPT = PROJECT_ROOT / "reports/sentiment-sealed-evaluation-consumption.json"
DEFAULT_CANDIDATE_BASE_MODEL = PROJECT_ROOT / "models/kf-deberta-base"

SCHEMA_VERSION = "korean-finance-sentiment-benchmark/v4"
LOCK_SCHEMA_VERSION = "sentiment-candidate-lock/v1"
TRAINING_SCHEMA_VERSION = "kf-deberta-sentiment-training/v2"
ARTIFACT_SCHEMA_VERSION = "kf-deberta-sentiment-artifact/v2"
INPUT_FEATURE_VERSION = "source-target-prefix-head-tail/v2"
BASE_MODEL = "kakaobank/kf-deberta-base"
BASE_MODEL_REVISION = "363b171d71443b0874b0bf9cea053eb5b1650633"
FAIR_BASELINE_MODEL = "snunlp/KR-FinBert-SC"
FAIR_BASELINE_MODEL_REVISION = "36b3d36898bc9925ca58c3508b1048e4449f1370"
LABEL_ORDER = ("NEGATIVE", "NEUTRAL", "POSITIVE")
SOURCE_LABEL = {"-1": "NEGATIVE", "0": "NEUTRAL", "1": "POSITIVE"}
REQUIRED_ARTIFACTS = (
    "adapter_config.json",
    "adapter_model.safetensors",
    "tokenizer.json",
    "tokenizer_config.json",
    "hannah_metadata.json",
)
FAIR_BASELINE_ARTIFACTS = (
    "config.json",
    "model.safetensors",
    "special_tokens_map.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "vocab.txt",
)
FAIR_BASELINE_SEEDS = (17, 42, 73)
DATA_SELECTION_SEED = 20_260_715
DATASET_REVISION = "K-FNSPID-v4"
PUBLIC_DATASET_REVISION = "7a8dc8cf6548a08e0a5dab3a12ad0fb8dccfd23f"
FAIR_SELECTION_PARTITIONS = (
    "PUBLIC_SELECTION",
    "K_FNSPID_DEVELOPMENT_SELECTION",
    "K_FNSPID_DISCLOSURE_DEVELOPMENT_SELECTION",
)
FAIR_TO_CANDIDATE_INPUTS = {
    "public_train": "public_train",
    "public_validation": "public_validation",
    "news_silver": "news_silver",
    "disclosure_silver": "disclosure_silver",
    "train_gold": "train_gold",
    "news_auxiliary_training_gold": "news_auxiliary_training_gold",
    "disclosure_auxiliary_training_gold": "disclosure_auxiliary_training_gold",
    "news_auxiliary_training_report": "news_auxiliary_training_report",
    "disclosure_auxiliary_training_report": "disclosure_auxiliary_training_report",
    "news_development_gold": "news_development_gold",
    "disclosure_development_gold": "disclosure_development_gold",
    "news_confirmatory_reservation": "news_sealed_review_reservation",
    "disclosure_confirmatory_reservation": "disclosure_sealed_review_reservation",
    "confirmatory_sampling_design": "sealed_sampling_design",
    "legacy_evaluation_1": "legacy_evaluation_1",
    "legacy_evaluation_2": "legacy_evaluation_2",
    "legacy_evaluation_3": "legacy_evaluation_3",
    "legacy_evaluation_4": "legacy_evaluation_4",
}
FAIR_EQUAL_TRAINING_ARGUMENTS = (
    "data_selection_seed",
    "max_length",
    "epochs",
    "batch_size",
    "gradient_accumulation_steps",
    "early_stopping_patience",
    "lr_scheduler_type",
    "warmup_fraction",
    "weight_decay",
    "silver_per_label",
    "disclosure_per_label",
    "target_swap_per_source",
    "rdrop_alpha",
    "max_train_rows",
    "gradient_checkpointing",
)
V6_RECIPE_RELATIVE_PATHS = {
    "candidate_trainer": "scripts/train_kf_deberta_sentiment_v6.py",
    "candidate_locker": "scripts/lock_kf_deberta_sentiment_candidate.py",
    "canonical_evaluator": "scripts/evaluate_locked_kf_deberta_sentiment.py",
    "runtime_parity_generator": "scripts/generate_sentiment_cpu_runtime_parity.py",
    "artifact_contract": "src/hannah_montana_ai/services/sentiment_artifact_contract.py",
    "hierarchical_runtime": (
        "src/hannah_montana_ai/services/source_hierarchical_sentiment.py"
    ),
    "serving_loader": "src/hannah_montana_ai/services/transformer_sentiment_model.py",
    "input_contract": "src/hannah_montana_ai/services/sentiment_input.py",
    "protocol": "src/hannah_montana_ai/training/sentiment_protocol.py",
    "v6_ablation_trainer": "scripts/train_kf_deberta_sentiment_v6_ablation.py",
    "v6_evaluation_contract": (
        "src/hannah_montana_ai/training/sentiment_v6_evaluation_contract.py"
    ),
    "v6_fair_baseline_trainer": "scripts/train_kr_finbert_sc_sentiment_v6.py",
    "v6_fair_baseline_runtime": (
        "src/hannah_montana_ai/services/kr_finbert_sc_v6_baseline.py"
    ),
    "v6_raw_reference_runtime": (
        "src/hannah_montana_ai/services/kr_finbert_sc_raw_reference.py"
    ),
    "v6_raw_reference_materializer": (
        "scripts/materialize_kr_finbert_sc_raw_reference.py"
    ),
    "v6_fair_baseline_commitment": (
        "src/hannah_montana_ai/training/sentiment_v6_baseline_commitment.py"
    ),
    "dependency_manifest": "pyproject.toml",
    "dependency_lock": "uv.lock",
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="잠긴 KF-DeBERTa 후보를 봉인 Gold와 재사용 진단셋에서 평가한다."
    )
    parser.add_argument("--lock-manifest", type=Path, default=DEFAULT_LOCK_MANIFEST)
    parser.add_argument(
        "--candidate-git-attestation",
        type=Path,
        default=DEFAULT_GIT_ATTESTATION,
    )
    parser.add_argument("--locked-artifact", type=Path, default=DEFAULT_LOCKED_ARTIFACT)
    parser.add_argument(
        "--candidate-base-model",
        type=Path,
        default=DEFAULT_CANDIDATE_BASE_MODEL,
    )
    parser.add_argument("--public-dataset", type=Path, default=DEFAULT_PUBLIC_DATASET)
    parser.add_argument("--news-sealed-gold", type=Path, default=DEFAULT_NEWS_SEALED_GOLD)
    parser.add_argument(
        "--disclosure-sealed-gold", type=Path, default=DEFAULT_DISCLOSURE_SEALED_GOLD
    )
    parser.add_argument(
        "--news-sealed-promotion-report",
        type=Path,
        default=DEFAULT_NEWS_SEALED_PROMOTION_REPORT,
    )
    parser.add_argument(
        "--disclosure-sealed-promotion-report",
        type=Path,
        default=DEFAULT_DISCLOSURE_SEALED_PROMOTION_REPORT,
    )
    parser.add_argument(
        "--sampling-design-report",
        type=Path,
        default=DEFAULT_SAMPLING_DESIGN_REPORT,
    )
    parser.add_argument("--legacy-news-gold", type=Path, default=DEFAULT_LEGACY_NEWS_GOLD)
    parser.add_argument(
        "--legacy-disclosure-gold", type=Path, default=DEFAULT_LEGACY_DISCLOSURE_GOLD
    )
    parser.add_argument("--tfidf-model", type=Path, default=DEFAULT_TFIDF_MODEL)
    parser.add_argument(
        "--raw-reference-artifact",
        type=Path,
        default=DEFAULT_RAW_REFERENCE_ARTIFACT,
    )
    parser.add_argument(
        "--pre-k-fnspid-artifact",
        type=Path,
        default=DEFAULT_PRE_K_FNSPID_ARTIFACT,
    )
    parser.add_argument(
        "--pre-k-fnspid-training-report",
        type=Path,
        default=DEFAULT_PRE_K_FNSPID_TRAINING_REPORT,
    )
    parser.add_argument(
        "--fair-baseline-artifact-root",
        type=Path,
        default=DEFAULT_FAIR_BASELINE_ARTIFACT_ROOT,
    )
    parser.add_argument(
        "--fair-baseline-selection-report",
        type=Path,
        default=DEFAULT_FAIR_BASELINE_SELECTION_REPORT,
    )
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--consumption-receipt", type=Path, default=DEFAULT_CONSUMPTION_RECEIPT)
    parser.add_argument("--batch-size", type=int, default=EVALUATION_BATCH_SIZE)
    parser.add_argument("--bootstrap-samples", type=int, default=DEFAULT_BOOTSTRAP_SAMPLES)
    parser.add_argument("--bootstrap-seed", type=int, default=DEFAULT_BOOTSTRAP_SEED)
    args = parser.parse_args()
    if args.batch_size < 1 or args.bootstrap_samples < 100:
        raise SystemExit("batch-size는 1 이상, bootstrap-samples는 100 이상이어야 합니다.")
    if args.report.exists() or args.report.is_symlink():
        raise SystemExit(f"봉인 평가 report가 이미 존재합니다: {args.report}")
    if args.consumption_receipt.exists() or args.consumption_receipt.is_symlink():
        raise SystemExit(f"봉인 평가셋이 이미 소비됐습니다: {args.consumption_receipt}")

    # 라벨 파일을 열기 전에 원격 이력, 후보, 공정 비교 artifact를 검증한다.
    candidate_lock, git_attestation = validate_attested_candidate(
        args.candidate_git_attestation,
        args.lock_manifest,
        args.locked_artifact,
        project_root=PROJECT_ROOT,
    )
    is_v6 = candidate_lock.get("model_family") == V6_MODEL_FAMILY
    runtime_plan_validator = (
        validate_v6_evaluation_runtime_parameters
        if is_v6
        else validate_evaluation_runtime_parameters
    )
    statistical_analysis_plan = runtime_plan_validator(
        candidate_lock.get("statistical_analysis_plan"),
        batch_size=args.batch_size,
        bootstrap_samples=args.bootstrap_samples,
        bootstrap_seed=args.bootstrap_seed,
    )
    locked_baseline_paths = _locked_baseline_paths(candidate_lock, PROJECT_ROOT)
    candidate_model_name = V6_CANDIDATE_MODEL_NAME if is_v6 else CANDIDATE_MODEL_NAME
    fair_model_name = (
        V6_FAIR_BASELINE_MODEL_NAME if is_v6 else FAIR_BASELINE_MODEL_NAME
    )
    no_k_model_name = (
        V6_NO_K_ABLATION_MODEL_NAME if is_v6 else NO_K_ABLATION_MODEL_NAME
    )
    fair_artifact_root_arg = (
        DEFAULT_V6_FAIR_BASELINE_ARTIFACT_ROOT
        if is_v6
        and args.fair_baseline_artifact_root == DEFAULT_FAIR_BASELINE_ARTIFACT_ROOT
        else args.fair_baseline_artifact_root
    )
    fair_selection_arg = (
        DEFAULT_V6_FAIR_BASELINE_SELECTION_REPORT
        if is_v6
        and args.fair_baseline_selection_report
        == DEFAULT_FAIR_BASELINE_SELECTION_REPORT
        else args.fair_baseline_selection_report
    )
    explicit_paths = {
        "tfidf_model": args.tfidf_model.resolve(),
        "pre_k_artifact": args.pre_k_fnspid_artifact.resolve(),
        "pre_k_training_report": args.pre_k_fnspid_training_report.resolve(),
        "fair_selection_report": fair_selection_arg.resolve(),
    }
    for name, path in explicit_paths.items():
        if path != locked_baseline_paths[name]:
            raise SystemExit(f"{name} CLI 경로가 candidate lock의 baseline 경로와 다릅니다.")
    raw_reference_path = args.raw_reference_artifact.resolve()
    if is_v6 and raw_reference_path != locked_baseline_paths["raw_reference_artifact"]:
        raise SystemExit(
            "raw_reference_artifact CLI 경로가 candidate lock의 baseline 경로와 다릅니다."
        )
    raw_reference_tokenizer, raw_reference_model, raw_reference_contract = (
        load_raw_reference_model(raw_reference_path)
    )
    if int(candidate_lock["max_length"]) != raw_reference_contract.max_length:
        raise SystemExit("raw KR-FinBERT-SC first-token 길이가 잠긴 후보와 다릅니다.")
    if is_v6:
        fair_record = candidate_lock["baseline_commitments"]["baselines"][
            V6_FAIR_BASELINE_MODEL_NAME
        ]
        fair_baseline_artifact = locked_baseline_paths["fair_winner_artifact"]
        selected_run = fair_record["seed_runs"][str(fair_record["selected_seed"])]
        selected_report = selected_run["report"]
        fair_contract = validate_kr_finbert_sc_v6_artifact(fair_baseline_artifact)
        fair_baseline = {
            "schema_version": "k-fnspid-v6-fair-evaluation-provenance/v1",
            "selected_seed": fair_record["selected_seed"],
            "artifact_dir": _display_path(fair_baseline_artifact, PROJECT_ROOT),
            "artifact_manifest_sha256": fair_contract.artifact_manifest_sha256,
            "metadata_sha256": file_sha256(
                fair_baseline_artifact / "hannah_metadata.json"
            ),
            "selection_report_path": fair_record["selection_report"]["path"],
            "selection_report_sha256": fair_record["selection_report"]["sha256"],
            "training_report_path": selected_report["path"],
            "training_report_sha256": selected_report["sha256"],
            "same_data_contract_sha256": canonical_json_sha256(
                candidate_lock["baseline_commitments"]["candidate_matching_contract"]
            ),
        }
    else:
        fair_baseline = validate_same_data_fair_baseline(
            fair_artifact_root_arg,
            fair_selection_arg,
            candidate_lock=candidate_lock,
            project_root=PROJECT_ROOT,
        )
        fair_baseline_artifact = (
            fair_artifact_root_arg
            / f"seed{int(fair_baseline['selected_seed'])}"
        )
        if fair_baseline_artifact.resolve() != locked_baseline_paths["fair_winner_artifact"]:
            raise SystemExit("공정 기준선 winner artifact가 candidate lock과 다릅니다.")
    no_k_artifact = locked_baseline_paths["no_k_winner_artifact"]
    if is_v6:
        no_k_record = candidate_lock["baseline_commitments"]["baselines"][
            V6_NO_K_ABLATION_MODEL_NAME
        ]
        no_k_provenance = {
            "schema_version": "k-fnspid-v6-no-k-evaluation-provenance/v1",
            "selected_seed": no_k_record["selected_seed"],
            "artifact_files": no_k_record["winner_artifact"]["files"],
            "artifact_manifest_sha256": no_k_record["winner_artifact"][
                "manifest_sha256"
            ],
            "selection_report": no_k_record["selection_report"],
            "winner_manifest": no_k_record["winner_manifest"],
            "runtime_loader_contract": no_k_record["runtime_loader_contract"],
            "confirmatory_labels_used_for_training_or_selection": False,
            "legacy_v5_no_k_final_holm_eligible": False,
        }
    else:
        no_k_provenance = _locked_no_k_provenance(candidate_lock)
    locked_at = _parse_aware_datetime(str(candidate_lock["locked_at"]), "locked_at")
    annotation_not_before = max(
        locked_at,
        _parse_aware_datetime(
            str(git_attestation["committer_time_iso"]),
            "git attestation committer_time_iso",
        ),
    )
    public_rows, public_audit = load_public_test(args.public_dataset)
    news_derivation = validate_sealed_gold_derivation(
        args.news_sealed_gold,
        args.news_sealed_promotion_report,
        candidate_lock["sealed_reservations"]["NEWS"],
        expected_partition="CONFIRMATORY_SEALED_TEST_REVIEW",
        expected_source="NEWS",
        expected_candidate_manifest_sha256=str(candidate_lock["manifest_sha256"]),
        expected_git_attestation_sha256=str(git_attestation["sha256"]),
        expected_git_commit_sha=str(git_attestation["commit_sha"]),
    )
    disclosure_derivation = validate_sealed_gold_derivation(
        args.disclosure_sealed_gold,
        args.disclosure_sealed_promotion_report,
        candidate_lock["sealed_reservations"]["DISCLOSURE"],
        expected_partition="DISCLOSURE_CONFIRMATORY_SEALED_TEST_REVIEW",
        expected_source="DISCLOSURE",
        expected_candidate_manifest_sha256=str(candidate_lock["manifest_sha256"]),
        expected_git_attestation_sha256=str(git_attestation["sha256"]),
        expected_git_commit_sha=str(git_attestation["commit_sha"]),
    )
    sampling_design = validate_probability_sampling_design(
        args.sampling_design_report,
        candidate_lock,
    )
    consumption_receipt = create_consumption_receipt(
        args.consumption_receipt,
        candidate_lock=candidate_lock,
        news_sealed_gold=args.news_sealed_gold,
        disclosure_sealed_gold=args.disclosure_sealed_gold,
        news_promotion_report=args.news_sealed_promotion_report,
        disclosure_promotion_report=args.disclosure_sealed_promotion_report,
        sampling_design_report=args.sampling_design_report,
        tfidf_model=args.tfidf_model,
        pre_k_fnspid_artifact=args.pre_k_fnspid_artifact,
        pre_k_fnspid_training_report=args.pre_k_fnspid_training_report,
        fair_baseline=fair_baseline,
        report_path=args.report,
        bootstrap_samples=args.bootstrap_samples,
        bootstrap_seed=args.bootstrap_seed,
    )
    news_rows = load_sealed_gold(
        args.news_sealed_gold,
        expected_partition="CONFIRMATORY_SEALED_TEST_REVIEW",
        expected_source="NEWS",
        locked_at=annotation_not_before,
        expected_sha256=str(news_derivation["gold_sha256"]),
        expected_candidate_manifest_sha256=str(candidate_lock["manifest_sha256"]),
        expected_git_attestation_sha256=str(git_attestation["sha256"]),
        expected_git_commit_sha=str(git_attestation["commit_sha"]),
    )
    disclosure_rows = load_sealed_gold(
        args.disclosure_sealed_gold,
        expected_partition="DISCLOSURE_CONFIRMATORY_SEALED_TEST_REVIEW",
        expected_source="DISCLOSURE",
        locked_at=annotation_not_before,
        expected_sha256=str(disclosure_derivation["gold_sha256"]),
        expected_candidate_manifest_sha256=str(candidate_lock["manifest_sha256"]),
        expected_git_attestation_sha256=str(git_attestation["sha256"]),
        expected_git_commit_sha=str(git_attestation["commit_sha"]),
    )
    news_rows = attach_probability_sampling_weights(
        news_rows,
        candidate_lock["sealed_reservations"]["NEWS"],
        sampling_design["NEWS"],
    )
    disclosure_rows = attach_probability_sampling_weights(
        disclosure_rows,
        candidate_lock["sealed_reservations"]["DISCLOSURE"],
        sampling_design["DISCLOSURE"],
    )
    legacy_news_rows = load_legacy_diagnostic(args.legacy_news_gold, "NEWS")
    legacy_disclosure_rows = load_legacy_diagnostic(args.legacy_disclosure_gold, "DISCLOSURE")

    partitions = {
        "public_test": public_rows,
        "sealed_news": news_rows,
        "sealed_disclosure": disclosure_rows,
        "legacy_news": legacy_news_rows,
        "legacy_disclosure": legacy_disclosure_rows,
    }
    all_rows = [row for rows in partitions.values() for row in rows]
    candidate_predictions = predict_locked_candidate(
        all_rows,
        args.locked_artifact,
        candidate_lock,
        batch_size=args.batch_size,
        base_model_dir=args.candidate_base_model,
    )
    tfidf_predictions = predict_tfidf(all_rows, args.tfidf_model)
    pre_k_fnspid_predictions, pre_k_fnspid_provenance = predict_pre_k_fnspid(
        all_rows,
        args.pre_k_fnspid_artifact,
        args.pre_k_fnspid_training_report,
        batch_size=args.batch_size,
    )
    fair_baseline_predictions = (
        predict_v6_same_data_fair_baseline(
            all_rows,
            fair_baseline_artifact,
            batch_size=args.batch_size,
        )
        if is_v6
        else predict_same_data_fair_baseline(
            all_rows,
            fair_baseline_artifact,
            fair_baseline,
            batch_size=args.batch_size,
        )
    )
    no_k_predictions = (
        predict_v6_no_k_ablation(
            all_rows,
            no_k_artifact,
            no_k_provenance,
            base_model_dir=args.candidate_base_model,
            batch_size=args.batch_size,
        )
        if is_v6
        else predict_no_k_ablation(
            all_rows,
            no_k_artifact,
            no_k_provenance,
            batch_size=args.batch_size,
        )
    )
    candidate_by_partition = _partition_predictions(partitions, candidate_predictions)
    tfidf_by_partition = _partition_predictions(partitions, tfidf_predictions)
    pre_k_fnspid_by_partition = _partition_predictions(partitions, pre_k_fnspid_predictions)
    fair_baseline_by_partition = _partition_predictions(partitions, fair_baseline_predictions)
    no_k_by_partition = _partition_predictions(partitions, no_k_predictions)
    reference_rows = [*public_rows, *news_rows, *disclosure_rows]
    reference_predictions = predict_kr_finbert(
        reference_rows,
        tokenizer=raw_reference_tokenizer,
        model=raw_reference_model,
        batch_size=args.batch_size,
        target_aware=True,
        max_length=int(candidate_lock["max_length"]),
    )
    raw_reference_predictions = predict_kr_finbert(
        reference_rows,
        tokenizer=raw_reference_tokenizer,
        model=raw_reference_model,
        batch_size=args.batch_size,
        target_aware=False,
        max_length=int(candidate_lock["max_length"]),
    )
    public_end = len(public_rows)
    news_end = public_end + len(news_rows)
    reference_by_partition = {
        "public_test": reference_predictions[:public_end],
        "sealed_news": reference_predictions[public_end:news_end],
        "sealed_disclosure": reference_predictions[news_end:],
    }
    raw_reference_by_partition = {
        "public_test": raw_reference_predictions[:public_end],
        "sealed_news": raw_reference_predictions[public_end:news_end],
        "sealed_disclosure": raw_reference_predictions[news_end:],
    }

    public_result = evaluate_partition(
        public_rows,
        {
            candidate_model_name: candidate_by_partition["public_test"],
            "hana_tfidf_logistic": tfidf_by_partition["public_test"],
            PRE_K_FNSPID_MODEL_NAME: pre_k_fnspid_by_partition["public_test"],
            fair_model_name: fair_baseline_by_partition["public_test"],
            no_k_model_name: no_k_by_partition["public_test"],
            "kr_finbert_sc": reference_by_partition["public_test"],
            "kr_finbert_sc_raw_off_the_shelf": raw_reference_by_partition["public_test"],
        },
        role="repeatedly_exposed_secondary_regression_set_non_gating",
        cluster_protocol="record_bootstrap_public_dataset_has_no_event_cluster",
        bootstrap_samples=args.bootstrap_samples,
        seed=args.bootstrap_seed,
        candidate_model_name=candidate_model_name,
    )
    news_result = evaluate_partition(
        news_rows,
        {
            candidate_model_name: candidate_by_partition["sealed_news"],
            "hana_tfidf_logistic": tfidf_by_partition["sealed_news"],
            PRE_K_FNSPID_MODEL_NAME: pre_k_fnspid_by_partition["sealed_news"],
            fair_model_name: fair_baseline_by_partition["sealed_news"],
            no_k_model_name: no_k_by_partition["sealed_news"],
            "kr_finbert_sc": reference_by_partition["sealed_news"],
            "kr_finbert_sc_raw_off_the_shelf": raw_reference_by_partition["sealed_news"],
            QWEN_TEACHER_MODEL_NAME: [str(row["teacher_sentiment"]) for row in news_rows],
        },
        role="confirmatory_sealed_gold",
        cluster_protocol="event_cluster_id",
        bootstrap_samples=args.bootstrap_samples,
        seed=args.bootstrap_seed + 1,
        analysis_weights=[float(row["analysis_weight"]) for row in news_rows],
        sampling_strata=[str(row["sampling_stratum"]) for row in news_rows],
        population_counts_by_stratum={
            label: int(sampling_design["NEWS"]["strata"][label]["frame_N_h"])
            for label in LABEL_ORDER
        },
        candidate_model_name=candidate_model_name,
    )
    disclosure_result = evaluate_partition(
        disclosure_rows,
        {
            candidate_model_name: candidate_by_partition["sealed_disclosure"],
            "hana_tfidf_logistic": tfidf_by_partition["sealed_disclosure"],
            PRE_K_FNSPID_MODEL_NAME: pre_k_fnspid_by_partition["sealed_disclosure"],
            fair_model_name: fair_baseline_by_partition["sealed_disclosure"],
            no_k_model_name: no_k_by_partition["sealed_disclosure"],
            "kr_finbert_sc": reference_by_partition["sealed_disclosure"],
            "kr_finbert_sc_raw_off_the_shelf": raw_reference_by_partition["sealed_disclosure"],
            QWEN_TEACHER_MODEL_NAME: [str(row["teacher_sentiment"]) for row in disclosure_rows],
        },
        role="confirmatory_sealed_gold",
        cluster_protocol="event_cluster_id",
        bootstrap_samples=args.bootstrap_samples,
        seed=args.bootstrap_seed + 2,
        analysis_weights=[float(row["analysis_weight"]) for row in disclosure_rows],
        sampling_strata=[str(row["sampling_stratum"]) for row in disclosure_rows],
        population_counts_by_stratum={
            label: int(sampling_design["DISCLOSURE"]["strata"][label]["frame_N_h"])
            for label in LABEL_ORDER
        },
        candidate_model_name=candidate_model_name,
    )
    legacy_news_result = evaluate_partition(
        legacy_news_rows,
        {
            candidate_model_name: candidate_by_partition["legacy_news"],
            "hana_tfidf_logistic": tfidf_by_partition["legacy_news"],
            PRE_K_FNSPID_MODEL_NAME: pre_k_fnspid_by_partition["legacy_news"],
            fair_model_name: fair_baseline_by_partition["legacy_news"],
            no_k_model_name: no_k_by_partition["legacy_news"],
        },
        role="contaminated_legacy_gold_diagnostic_only",
        cluster_protocol="legacy_identity_proxy_no_event_cluster",
        bootstrap_samples=args.bootstrap_samples,
        seed=args.bootstrap_seed + 3,
        candidate_model_name=candidate_model_name,
    )
    legacy_disclosure_result = evaluate_partition(
        legacy_disclosure_rows,
        {
            candidate_model_name: candidate_by_partition["legacy_disclosure"],
            "hana_tfidf_logistic": tfidf_by_partition["legacy_disclosure"],
            PRE_K_FNSPID_MODEL_NAME: pre_k_fnspid_by_partition["legacy_disclosure"],
            fair_model_name: fair_baseline_by_partition["legacy_disclosure"],
            no_k_model_name: no_k_by_partition["legacy_disclosure"],
        },
        role="contaminated_legacy_gold_diagnostic_only",
        cluster_protocol="legacy_identity_proxy_no_event_cluster",
        bootstrap_samples=args.bootstrap_samples,
        seed=args.bootstrap_seed + 4,
        candidate_model_name=candidate_model_name,
    )

    news_summary = source_summary(
        news_result,
        args.news_sealed_gold,
        candidate_model_name=candidate_model_name,
        fair_model_name=fair_model_name,
        no_k_model_name=no_k_model_name,
    )
    disclosure_summary = source_summary(
        disclosure_result,
        args.disclosure_sealed_gold,
        candidate_model_name=candidate_model_name,
        fair_model_name=fair_model_name,
        no_k_model_name=no_k_model_name,
    )
    public_summary = public_test_summary(
        public_result,
        args.public_dataset / "ratings_test.csv",
        candidate_model_name=candidate_model_name,
        fair_model_name=fair_model_name,
        no_k_model_name=no_k_model_name,
    )
    confirmatory_inference = build_confirmatory_inference(
        news_result,
        disclosure_result,
        statistical_analysis_plan=statistical_analysis_plan,
        fair_model_name=fair_model_name,
        no_k_model_name=no_k_model_name,
    )
    gate = build_deployment_gate(
        news_summary,
        disclosure_summary,
        public_summary,
        candidate_version=str(candidate_lock["version"]),
        artifact_manifest_sha256=str(candidate_lock["artifact_manifest_sha256"]),
        confirmatory_inference=confirmatory_inference,
        candidate_model=(
            V6_CANDIDATE_MODEL
            if candidate_lock.get("model_family") == V6_MODEL_FAMILY
            else CANDIDATE_MODEL_NAME
        ),
        candidate_model_family=(
            V6_MODEL_FAMILY if candidate_lock.get("model_family") == V6_MODEL_FAMILY else None
        ),
    )
    _assert_file_sha256(args.news_sealed_gold, str(news_derivation["gold_sha256"]))
    _assert_file_sha256(args.disclosure_sealed_gold, str(disclosure_derivation["gold_sha256"]))
    _assert_file_sha256(
        args.news_sealed_promotion_report,
        str(news_derivation["promotion_report_sha256"]),
    )
    _assert_file_sha256(
        args.disclosure_sealed_promotion_report,
        str(disclosure_derivation["promotion_report_sha256"]),
    )
    _assert_file_sha256(
        args.tfidf_model,
        str(consumption_receipt["baseline_artifacts"]["hana_tfidf_logistic"]["sha256"]),
    )
    _assert_file_sha256(
        args.pre_k_fnspid_artifact / "hannah_metadata.json",
        str(consumption_receipt["baseline_artifacts"][PRE_K_FNSPID_MODEL_NAME]["metadata_sha256"]),
    )
    _assert_file_sha256(
        args.pre_k_fnspid_training_report,
        str(
            consumption_receipt["baseline_artifacts"][PRE_K_FNSPID_MODEL_NAME][
                "training_report_sha256"
            ]
        ),
    )
    if is_v6:
        current_fair = validate_kr_finbert_sc_v6_artifact(fair_baseline_artifact)
        if (
            current_fair.artifact_manifest_sha256
            != fair_baseline["artifact_manifest_sha256"]
        ):
            raise ValueError("v6 fair baseline artifact가 평가 중 변경됐습니다.")
        _assert_file_sha256(
            fair_selection_arg,
            str(fair_baseline["selection_report_sha256"]),
        )
    else:
        assert_same_data_fair_baseline_unchanged(
            fair_baseline_artifact,
            fair_selection_arg,
            fair_baseline,
            project_root=PROJECT_ROOT,
        )
    if is_v6:
        locked_candidate_report = _load_json_object(
            _safe_project_path(
                PROJECT_ROOT,
                candidate_lock["candidate_report_path"],
                "v6 candidate report",
            ),
            "v6 candidate report",
        )
        revalidated_baselines = validate_v6_confirmatory_baseline_commitments(
            candidate_lock["baseline_commitments"],
            PROJECT_ROOT,
            candidate_training_report=locked_candidate_report,
        )
    else:
        revalidated_baselines = validate_confirmatory_baseline_commitments(
            candidate_lock["baseline_commitments"], PROJECT_ROOT
        )
    if revalidated_baselines != candidate_lock["baseline_commitments"]:
        raise ValueError("확증 평가 중 baseline 실제 바이트가 변경됐습니다.")
    if validate_runtime_parity_lock_commitment(
        candidate_lock["runtime_parity"],
        project_root=PROJECT_ROOT,
        expected_candidate_version=str(candidate_lock["version"]),
        expected_candidate_artifact_manifest_sha256=str(
            candidate_lock["artifact_manifest_sha256"]
        ),
        sealed_reservations=candidate_lock["sealed_reservations"],
        expected_candidate_model_family=candidate_lock.get("model_family"),
        expected_base_source_kind=candidate_lock.get("base_source_kind"),
    ) != candidate_lock["runtime_parity"]:
        raise ValueError("확증 평가 중 CPU runtime parity evidence가 변경됐습니다.")
    report = {
        "schema_version": (
            V6_BENCHMARK_SCHEMA_VERSION
            if candidate_lock.get("model_family") == V6_MODEL_FAMILY
            else SCHEMA_VERSION
        ),
        "generated_at": datetime.now(UTC).isoformat(),
        "input_feature_version": INPUT_FEATURE_VERSION,
        "candidate_lock": candidate_lock,
        "sealed_evaluation_consumption": {
            **consumption_receipt,
            "receipt_path": _display_path(args.consumption_receipt, PROJECT_ROOT),
            "receipt_sha256": file_sha256(args.consumption_receipt),
        },
        "pre_k_fnspid_baseline": pre_k_fnspid_provenance,
        "same_data_fair_baseline": fair_baseline,
        "no_k_ablation_baseline": no_k_provenance,
        "cpu_runtime_parity": candidate_lock["runtime_parity"],
        "raw_reference_model": {
            "display_name": (
                "raw KR-FinBERT-SC, first-256-token, no target conditioning"
            ),
            "repository": RAW_REFERENCE_MODEL_REPOSITORY,
            "safetensors_revision": RAW_REFERENCE_MODEL_REVISION,
            "artifact_path": _display_path(raw_reference_path, PROJECT_ROOT),
            "artifact_manifest_sha256": raw_reference_contract.manifest_sha256,
            "max_length": raw_reference_contract.max_length,
            "target_conditioning": False,
            "local_files_only": True,
            "weights_format": "safetensors",
            "trust_remote_code": False,
        },
        "sampling_design": sampling_design,
        "statistical_analysis_plan": statistical_analysis_plan,
        "confirmatory_inference": confirmatory_inference,
        "evaluation_contract": {
            "candidate_selection_completed_before_evaluation_labels_loaded": True,
            "locked_before_evaluation": True,
            "test_used_for_candidate_selection": False,
            "sealed_gold_used_for_candidate_selection": False,
            "candidate_selection_inputs": ["CALIBRATION", "SELECTION"],
            "confirmatory_inputs": [
                str(args.news_sealed_gold.relative_to(PROJECT_ROOT)),
                str(args.disclosure_sealed_gold.relative_to(PROJECT_ROOT)),
                str(args.sampling_design_report.relative_to(PROJECT_ROOT)),
            ],
            "diagnostic_only_inputs": [
                str((args.public_dataset / "ratings_test.csv").relative_to(PROJECT_ROOT)),
                str(args.legacy_news_gold.relative_to(PROJECT_ROOT)),
                str(args.legacy_disclosure_gold.relative_to(PROJECT_ROOT)),
            ],
            "claim_scope": (
                "신규 뉴스/공시 층화 확률표본 Gold만 확증 평가에 사용하고 고정 "
                "설계가중 혼동행렬의 plug-in Macro-F1을 계산한다. 공개 Test와 기존 "
                "Gold는 반복 사용 또는 오염 이력 때문에 회귀 진단에만 사용한다."
            ),
        },
        "source_sealed_gold": {
            "NEWS": news_summary,
            "DISCLOSURE": disclosure_summary,
        },
        "public_test": {
            **public_summary,
            "public_partition_leakage_audit": public_audit,
        },
        "diagnostics": {
            "legacy_news_gold": {
                **legacy_news_result,
                "path": str(args.legacy_news_gold.relative_to(PROJECT_ROOT)),
                "sha256": file_sha256(args.legacy_news_gold),
            },
            "legacy_disclosure_gold": {
                **legacy_disclosure_result,
                "path": str(args.legacy_disclosure_gold.relative_to(PROJECT_ROOT)),
                "sha256": file_sha256(args.legacy_disclosure_gold),
            },
        },
        "deployment_gate": gate,
    }
    _write_json_atomic(args.report, report)
    print(json.dumps(report, ensure_ascii=False))


def validate_attested_candidate(
    git_attestation_path: Path,
    manifest_path: Path,
    artifact_dir: Path,
    *,
    project_root: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    git_attestation = validate_candidate_git_attestation(
        git_attestation_path,
        manifest_path,
        project_root=project_root,
    )
    candidate_lock = validate_candidate_lock(
        manifest_path,
        artifact_dir,
        project_root=project_root,
    )
    if git_attestation["candidate_lock_sha256"] != candidate_lock["manifest_sha256"]:
        raise ValueError("Git attestation과 검증된 candidate lock hash가 다릅니다.")
    candidate_lock["external_git_attestation"] = git_attestation
    return candidate_lock, git_attestation


def validate_candidate_lock(
    manifest_path: Path,
    artifact_dir: Path,
    *,
    project_root: Path,
) -> dict[str, Any]:
    manifest = _load_json_object(manifest_path, "후보 lock manifest")
    if manifest.get("schema_version") == V6_LOCK_SCHEMA_VERSION:
        return _validate_v6_candidate_lock(
            manifest,
            manifest_path=manifest_path,
            artifact_dir=artifact_dir,
            project_root=project_root,
        )
    if (
        manifest.get("schema_version") != LOCK_SCHEMA_VERSION
        or manifest.get("selection_only") is not True
        or manifest.get("public_test_evaluated_before_lock") is not False
        or manifest.get("operational_sealed_gold_evaluated_before_lock") is not False
        or manifest.get("external_git_commitment_required") is not True
    ):
        raise ValueError("후보 lock이 봉인 평가 계약을 충족하지 않습니다.")
    locked_at = _parse_aware_datetime(str(manifest.get("locked_at", "")), "locked_at")
    if locked_at > datetime.now(UTC):
        raise ValueError("후보 lock 시각이 미래입니다.")
    sealed_reservations = manifest.get("sealed_reservations")
    if not isinstance(sealed_reservations, dict) or set(sealed_reservations) != {
        "NEWS",
        "DISCLOSURE",
    }:
        raise ValueError("후보 lock에 봉인 reservation commitment가 없습니다.")
    validated_reservations = {
        "NEWS": _validate_reservation_commitment(
            sealed_reservations["NEWS"],
            project_root,
            "NEWS",
            "CONFIRMATORY_SEALED_TEST_REVIEW",
        ),
        "DISCLOSURE": _validate_reservation_commitment(
            sealed_reservations["DISCLOSURE"],
            project_root,
            "DISCLOSURE",
            "DISCLOSURE_CONFIRMATORY_SEALED_TEST_REVIEW",
        ),
    }
    dataset_provenance = _validate_dataset_provenance(
        manifest.get("dataset_provenance"), project_root
    )
    recipe = _validate_recipe_commitments(manifest.get("recipe"), project_root)
    statistical_analysis_plan = validate_statistical_analysis_plan(
        manifest.get("statistical_analysis_plan")
    )
    baseline_commitments = validate_confirmatory_baseline_commitments(
        manifest.get("baseline_commitments"), project_root
    )
    if manifest.get("baseline_commitments_sha256") != baseline_commitments_sha256(
        baseline_commitments
    ):
        raise ValueError("후보 lock baseline commitment digest가 다릅니다.")

    winner = manifest.get("winner")
    if not isinstance(winner, dict):
        raise ValueError("후보 lock winner가 없습니다.")
    report_path = _safe_project_path(project_root, winner.get("report_path"), "후보 report")
    expected_report_hash = _sha256_value(winner.get("report_sha256"), "후보 report")
    if file_sha256(report_path) != expected_report_hash:
        raise ValueError("잠긴 후보 report hash가 일치하지 않습니다.")
    training_report = _load_json_object(report_path, "후보 학습 report")
    _validate_training_report(training_report, winner)

    configured_artifact_dir = _safe_project_path(
        project_root, winner.get("locked_artifact_dir"), "잠긴 artifact"
    )
    if configured_artifact_dir != artifact_dir.resolve():
        raise ValueError("lock manifest와 평가 artifact 경로가 다릅니다.")
    artifact_files = winner.get("artifact_files")
    if not isinstance(artifact_files, dict) or set(artifact_files) != set(REQUIRED_ARTIFACTS):
        raise ValueError("잠긴 artifact manifest 구성이 올바르지 않습니다.")
    _verify_file_manifest(artifact_dir, artifact_files)

    metadata_path = artifact_dir / "hannah_metadata.json"
    metadata = _load_json_object(metadata_path, "감성 artifact metadata")
    _validate_metadata(metadata, training_report, winner)
    if metadata.get("artifact_files") != training_report.get("artifact_files"):
        raise ValueError("metadata와 후보 report의 artifact manifest가 다릅니다.")
    source_artifact_manifest = metadata.get("artifact_files")
    if not isinstance(source_artifact_manifest, dict):
        raise ValueError("metadata artifact manifest가 없습니다.")
    _verify_file_manifest(artifact_dir, source_artifact_manifest)

    artifact_manifest_hash = canonical_json_sha256(artifact_files)
    runtime_parity = validate_runtime_parity_lock_commitment(
        manifest.get("runtime_parity"),
        project_root=project_root,
        expected_candidate_version=str(metadata["version"]),
        expected_candidate_artifact_manifest_sha256=artifact_manifest_hash,
        sealed_reservations=validated_reservations,
    )
    logit_bias_by_domain = validated_sentiment_logit_biases(metadata["logit_bias_by_domain"])
    return {
        "schema_version": LOCK_SCHEMA_VERSION,
        "manifest_path": _display_path(manifest_path, project_root),
        "manifest_sha256": file_sha256(manifest_path),
        "locked_at": locked_at.isoformat(),
        "locked_before_evaluation": True,
        "selection_only": True,
        "version": str(metadata["version"]),
        "candidate_report_path": _display_path(report_path, project_root),
        "candidate_report_sha256": expected_report_hash,
        "artifact_dir": _display_path(artifact_dir, project_root),
        "artifact_files": artifact_files,
        "artifact_manifest_sha256": artifact_manifest_hash,
        "base_model": BASE_MODEL,
        "base_model_revision": BASE_MODEL_REVISION,
        "max_length": int(metadata["max_length"]),
        "input_feature_version": INPUT_FEATURE_VERSION,
        "logit_bias_by_domain": {
            domain: list(bias) for domain, bias in logit_bias_by_domain.items()
        },
        "sealed_reservations": validated_reservations,
        "dataset_provenance": dataset_provenance,
        "recipe": recipe,
        "statistical_analysis_plan": statistical_analysis_plan,
        "baseline_commitments": baseline_commitments,
        "baseline_commitments_sha256": baseline_commitments_sha256(baseline_commitments),
        "runtime_parity": runtime_parity,
    }


def _validate_v6_candidate_lock(
    manifest: dict[str, Any],
    *,
    manifest_path: Path,
    artifact_dir: Path,
    project_root: Path,
) -> dict[str, Any]:
    if (
        manifest.get("schema_version") != V6_LOCK_SCHEMA_VERSION
        or manifest.get("selection_only") is not True
        or manifest.get("public_test_evaluated_before_lock") is not False
        or manifest.get("operational_sealed_gold_evaluated_before_lock") is not False
        or manifest.get("external_git_commitment_required") is not True
    ):
        raise ValueError("v6 후보 lock이 봉인 평가 계약을 충족하지 않습니다.")
    locked_at = _parse_aware_datetime(str(manifest.get("locked_at", "")), "locked_at")
    if locked_at > datetime.now(UTC):
        raise ValueError("v6 후보 lock 시각이 미래입니다.")
    sealed_raw = manifest.get("sealed_reservations")
    if not isinstance(sealed_raw, dict) or set(sealed_raw) != {"NEWS", "DISCLOSURE"}:
        raise ValueError("v6 후보 lock에 봉인 reservation commitment가 없습니다.")
    reservations = {
        "NEWS": _validate_reservation_commitment(
            sealed_raw["NEWS"],
            project_root,
            "NEWS",
            "CONFIRMATORY_SEALED_TEST_REVIEW",
        ),
        "DISCLOSURE": _validate_reservation_commitment(
            sealed_raw["DISCLOSURE"],
            project_root,
            "DISCLOSURE",
            "DISCLOSURE_CONFIRMATORY_SEALED_TEST_REVIEW",
        ),
    }
    winner = manifest.get("winner")
    if not isinstance(winner, dict) or winner.get("model_family") != V6_MODEL_FAMILY:
        raise ValueError("v6 후보 lock winner/model family가 없습니다.")
    report_path = _safe_project_path(project_root, winner.get("report_path"), "v6 후보 report")
    report_sha256 = _sha256_value(winner.get("report_sha256"), "v6 후보 report")
    if file_sha256(report_path) != report_sha256:
        raise ValueError("잠긴 v6 후보 report hash가 일치하지 않습니다.")
    report = _load_json_object(report_path, "v6 후보 학습 report")
    selection = report.get("candidate_selection")
    if (
        not isinstance(selection, dict)
        or selection.get("public_test_used") is not False
        or selection.get("confirmatory_used") is not False
        or selection.get("independent_generalization_evidence") is not False
        or report.get("public_test_opened") is not False
        or report.get("confirmatory_labels_opened") is not False
    ):
        raise ValueError("v6 후보 학습 report가 selection-only 계약을 위반했습니다.")
    configured_artifact = _safe_project_path(
        project_root,
        winner.get("locked_artifact_dir"),
        "잠긴 v6 artifact",
    )
    resolved_artifact = artifact_dir.resolve(strict=True)
    if configured_artifact != resolved_artifact:
        raise ValueError("v6 lock manifest와 평가 artifact 경로가 다릅니다.")
    contract = validate_source_hierarchical_artifact(resolved_artifact, report)
    if (
        winner.get("version") != contract.version
        or winner.get("base_source_kind") != contract.base_source_kind
        or winner.get("base_source") != contract.base_source
        or winner.get("artifact_files") != contract.locked_manifest
        or winner.get("artifact_manifest_sha256") != contract.locked_manifest_sha256
        or winner.get("prepared_partition_commitments")
        != report.get("prepared_partition_commitments")
    ):
        raise ValueError("v6 winner와 artifact/report commitment가 다릅니다.")
    dataset_provenance = _validate_dataset_provenance(
        manifest.get("dataset_provenance"),
        project_root,
    )
    recipe = _validate_v6_recipe_commitments(manifest.get("recipe"), project_root)
    statistical_analysis_plan = validate_v6_statistical_analysis_plan(
        manifest.get("statistical_analysis_plan")
    )
    baseline_commitments = validate_v6_confirmatory_baseline_commitments(
        manifest.get("baseline_commitments"),
        project_root,
        candidate_training_report=report,
    )
    if manifest.get("baseline_commitments_sha256") != baseline_commitments_sha256(
        baseline_commitments
    ):
        raise ValueError("v6 후보 lock baseline commitment digest가 다릅니다.")
    runtime_parity = validate_runtime_parity_lock_commitment(
        manifest.get("runtime_parity"),
        project_root=project_root,
        expected_candidate_version=contract.version,
        expected_candidate_artifact_manifest_sha256=contract.locked_manifest_sha256,
        expected_candidate_model_family=V6_MODEL_FAMILY,
        expected_base_source_kind=contract.base_source_kind,
        sealed_reservations=reservations,
    )
    return {
        "schema_version": V6_LOCK_SCHEMA_VERSION,
        "manifest_path": _display_path(manifest_path, project_root),
        "manifest_sha256": file_sha256(manifest_path),
        "locked_at": locked_at.isoformat(),
        "locked_before_evaluation": True,
        "selection_only": True,
        "model_family": V6_MODEL_FAMILY,
        "version": contract.version,
        "candidate_report_path": _display_path(report_path, project_root),
        "candidate_report_sha256": report_sha256,
        "artifact_dir": _display_path(resolved_artifact, project_root),
        "artifact_files": contract.locked_manifest,
        "artifact_manifest_sha256": contract.locked_manifest_sha256,
        "base_model": BASE_MODEL,
        "base_model_revision": BASE_MODEL_REVISION,
        "base_source_kind": contract.base_source_kind,
        "base_source": contract.base_source,
        "max_length": contract.max_length,
        "input_feature_version": INPUT_FEATURE_VERSION,
        "sealed_reservations": reservations,
        "dataset_provenance": dataset_provenance,
        "recipe": recipe,
        "statistical_analysis_plan": statistical_analysis_plan,
        "baseline_commitments": baseline_commitments,
        "baseline_commitments_sha256": baseline_commitments_sha256(baseline_commitments),
        "runtime_parity": runtime_parity,
    }


def _locked_baseline_paths(
    candidate_lock: dict[str, Any], project_root: Path
) -> dict[str, Path]:
    commitments = candidate_lock.get("baseline_commitments")
    if candidate_lock.get("model_family") == V6_MODEL_FAMILY:
        return v6_baseline_paths(commitments, project_root)
    if not isinstance(commitments, dict):
        raise ValueError("candidate lock baseline commitments가 없습니다.")
    baselines = commitments.get("baselines")
    if not isinstance(baselines, dict):
        raise ValueError("candidate lock baseline 집합이 없습니다.")

    def locked_path(record: object, label: str) -> Path:
        if not isinstance(record, dict):
            raise ValueError(f"{label} commitment가 없습니다.")
        value = record.get("path")
        if not isinstance(value, str) or not value:
            raise ValueError(f"{label} path가 없습니다.")
        resolved = (project_root / value).resolve()
        try:
            resolved.relative_to(project_root.resolve())
        except ValueError as exception:
            raise ValueError(f"{label} path가 프로젝트 밖입니다.") from exception
        return resolved

    tfidf = baselines["hana_tfidf_logistic"]
    pre_k = baselines[PRE_K_FNSPID_MODEL_NAME]
    fair = baselines[FAIR_BASELINE_MODEL_NAME]
    no_k = baselines[NO_K_ABLATION_MODEL_NAME]
    return {
        "tfidf_model": locked_path(tfidf["artifact"], "TF-IDF artifact"),
        "pre_k_artifact": locked_path(pre_k["winner_artifact"], "pre-K artifact"),
        "pre_k_training_report": locked_path(
            pre_k["training_report"], "pre-K training report"
        ),
        "fair_selection_report": locked_path(
            fair["selection_report"], "fair selection report"
        ),
        "fair_winner_artifact": locked_path(
            fair["winner_artifact"], "fair winner artifact"
        ),
        "no_k_winner_artifact": locked_path(
            no_k["winner_artifact"], "no-K winner artifact"
        ),
    }


def _locked_no_k_provenance(candidate_lock: dict[str, Any]) -> dict[str, Any]:
    commitments = candidate_lock["baseline_commitments"]["baselines"][
        NO_K_ABLATION_MODEL_NAME
    ]
    winner = commitments["winner_artifact"]
    return {
        "selected_seed": commitments["selected_seed"],
        "artifact_files": winner["files"],
        "artifact_manifest_sha256": winner["manifest_sha256"],
        "selection_report": commitments["selection_report"],
        "winner_manifest": commitments["winner_manifest"],
        "confirmatory_labels_used_for_training_or_selection": False,
    }


def validate_same_data_fair_baseline(
    artifact_root: Path,
    selection_report_path: Path,
    *,
    candidate_lock: dict[str, Any],
    project_root: Path,
) -> dict[str, Any]:
    """확증 라벨을 열기 전에 공정 비교군의 선택·학습·artifact 계약을 검증한다."""
    resolved_artifact_root = _require_project_directory(
        artifact_root, project_root, "동일 데이터 공정 기준선 artifact root"
    )
    resolved_selection_report = _require_project_file(
        selection_report_path, project_root, "동일 데이터 공정 기준선 selection report"
    )
    selection = _load_json_object(
        resolved_selection_report, "동일 데이터 공정 기준선 selection report"
    )
    runs = selection.get("runs")
    if (
        selection.get("schema_version") != "k-fnspid-fair-baseline-selection/v1"
        or selection.get("base_model") != FAIR_BASELINE_MODEL
        or selection.get("base_model_revision") != FAIR_BASELINE_MODEL_REVISION
        or tuple(selection.get("seed_budget", ())) != FAIR_BASELINE_SEEDS
        or selection.get("selection_method")
        != "weakest-source-macro-f1-then-overall-then-lowest-seed/v1"
        or selection.get("public_test_labels_used") is not False
        or selection.get("confirmatory_labels_used") is not False
        or not isinstance(runs, list)
        or len(runs) != len(FAIR_BASELINE_SEEDS)
    ):
        raise ValueError("동일 데이터 공정 기준선 selection 계약이 올바르지 않습니다.")
    _parse_aware_datetime(str(selection.get("generated_at", "")), "fair generated_at")

    reports: dict[int, tuple[Path, dict[str, Any], float, float]] = {}
    protocol_signatures: set[str] = set()
    for run in runs:
        if not isinstance(run, dict):
            raise ValueError("동일 데이터 공정 기준선 run이 JSON 객체가 아닙니다.")
        seed = _strict_int(run.get("seed"), "공정 기준선 seed")
        if seed in reports or seed not in FAIR_BASELINE_SEEDS:
            raise ValueError("동일 데이터 공정 기준선 seed 집합이 올바르지 않습니다.")
        report_record = run.get("report")
        if not isinstance(report_record, dict):
            raise ValueError("동일 데이터 공정 기준선 run report commitment가 없습니다.")
        report_path = _safe_project_path(
            project_root, report_record.get("path"), f"공정 기준선 seed{seed} report"
        )
        expected_report_path = resolved_selection_report.parent / f"seed{seed}.json"
        if report_path != expected_report_path.resolve():
            raise ValueError("공정 기준선 report가 selection report와 같은 디렉터리가 아닙니다.")
        _validate_regular_file_commitment(report_path, report_record, f"공정 기준선 seed{seed}")
        report = _load_json_object(report_path, f"공정 기준선 seed{seed} 학습 report")
        selection_score, overall_macro_f1 = _validate_fair_training_report(report, seed)
        if not math.isclose(
            _strict_float(run.get("selection_score"), "공정 기준선 selection_score"),
            selection_score,
            rel_tol=0.0,
            abs_tol=1e-12,
        ) or not math.isclose(
            _strict_float(
                run.get("overall_selection_macro_f1"),
                "공정 기준선 overall selection Macro-F1",
            ),
            overall_macro_f1,
            rel_tol=0.0,
            abs_tol=1e-12,
        ):
            raise ValueError("공정 기준선 selection 지표를 seed report에서 재현할 수 없습니다.")
        _validate_fair_training_provenance(report, project_root)
        reports[seed] = (report_path, report, selection_score, overall_macro_f1)
        protocol_signatures.add(_fair_protocol_signature(report))
    if set(reports) != set(FAIR_BASELINE_SEEDS) or len(protocol_signatures) != 1:
        raise ValueError("공정 기준선 3개 seed의 데이터·학습 예산이 동일하지 않습니다.")

    expected_seed = max(
        reports,
        key=lambda seed: (reports[seed][2], reports[seed][3], -seed),
    )
    selected_seed = _strict_int(selection.get("selected_seed"), "선택된 공정 기준선 seed")
    if selected_seed != expected_seed or not math.isclose(
        _strict_float(
            selection.get("selected_weakest_source_macro_f1"),
            "선택된 공정 기준선 최저 출처 Macro-F1",
        ),
        reports[expected_seed][2],
        rel_tol=0.0,
        abs_tol=1e-12,
    ):
        raise ValueError("공정 기준선 winner를 3개 seed에서 재현할 수 없습니다.")

    selected_report_path, selected_report, _, _ = reports[selected_seed]
    same_data_contract = _validate_same_data_training_contract(
        selected_report,
        candidate_lock,
        project_root,
    )
    selected_artifact_dir = resolved_artifact_root / f"seed{selected_seed}"
    if selected_artifact_dir.is_symlink() or not selected_artifact_dir.is_dir():
        raise ValueError("선택된 동일 데이터 공정 기준선 artifact가 없습니다.")
    metadata_path = selected_artifact_dir / "hannah_metadata.json"
    metadata = _load_json_object(metadata_path, "동일 데이터 공정 기준선 metadata")
    artifact_manifest = _validate_fair_artifact_metadata(
        metadata,
        selected_report,
        selected_artifact_dir,
    )
    selection_sha256 = file_sha256(resolved_selection_report)
    report_sha256 = file_sha256(selected_report_path)
    return {
        "model_name": FAIR_BASELINE_MODEL_NAME,
        "base_model": FAIR_BASELINE_MODEL,
        "base_model_revision": FAIR_BASELINE_MODEL_REVISION,
        "version": str(metadata["version"]),
        "selected_seed": selected_seed,
        "seed_budget": list(FAIR_BASELINE_SEEDS),
        "selection_method": str(selection["selection_method"]),
        "selection_report_path": _display_path(resolved_selection_report, project_root),
        "selection_report_sha256": selection_sha256,
        "training_report_path": _display_path(selected_report_path, project_root),
        "training_report_sha256": report_sha256,
        "artifact_dir": _display_path(selected_artifact_dir, project_root),
        "artifact_files": artifact_manifest,
        "artifact_manifest_sha256": canonical_json_sha256(artifact_manifest),
        "metadata_sha256": file_sha256(metadata_path),
        "max_length": int(metadata["max_length"]),
        "input_feature_version": INPUT_FEATURE_VERSION,
        "logit_bias_by_domain": {
            domain: list(values)
            for domain, values in validated_sentiment_logit_biases(
                metadata["logit_bias_by_domain"]
            ).items()
        },
        "full_finetune": True,
        "same_data_split_selection_budget_verified": True,
        "same_data_contract": same_data_contract,
        "same_data_contract_sha256": canonical_json_sha256(same_data_contract),
        "public_test_labels_used_for_training_or_selection": False,
        "confirmatory_labels_used_for_training_or_selection": False,
    }


def _validate_fair_training_report(
    report: dict[str, Any], expected_seed: int
) -> tuple[float, float]:
    arguments = report.get("training_arguments")
    selection = report.get("candidate_selection")
    partition_count = report.get("partition_count")
    test = report.get("test")
    base_provenance = report.get("base_model_provenance")
    environment = report.get("training_environment")
    runtime = report.get("training_runtime")
    trainable_parameters = report.get("trainable_parameter_count")
    total_parameters = report.get("total_parameter_count")
    if (
        report.get("schema_version") != "k-fnspid-fair-baseline-training/v1"
        or report.get("base_model") != FAIR_BASELINE_MODEL
        or report.get("base_model_revision") != FAIR_BASELINE_MODEL_REVISION
        or report.get("weights_format") != "safetensors"
        or report.get("full_finetune") is not True
        or report.get("training_strategy")
        != "full-finetune-same-three-way-dual-gold-target-swap-rdrop-hierarchical/v4"
        or report.get("dataset_revision") != DATASET_REVISION
        or report.get("public_dataset_revision") != PUBLIC_DATASET_REVISION
        or report.get("input_feature_version") != INPUT_FEATURE_VERSION
        or tuple(report.get("label_order", ())) != LABEL_ORDER
        or _strict_int(report.get("seed"), "공정 기준선 report seed") != expected_seed
        or not isinstance(arguments, dict)
        or _strict_int(arguments.get("seed"), "공정 기준선 학습 seed") != expected_seed
        or tuple(arguments.get("seed_budget", ())) != FAIR_BASELINE_SEEDS
        or arguments.get("data_selection_seed") != DATA_SELECTION_SEED
        or arguments.get("max_train_rows") is not None
        or arguments.get("same_data_splits_seeds_epochs_update_schedule_as_candidate") is not True
        or arguments.get("model_specific_optimizer_and_parameterization") is not True
        or _strict_int(arguments.get("early_stopping_patience"), "early stopping patience") != 1
        or not isinstance(selection, dict)
        or tuple(selection.get("required_sources", ())) != FAIR_SELECTION_PARTITIONS
        or selection.get("selection_method") != "weakest-source-macro-f1-then-overall/v1"
        or selection.get("public_test_path_accessed") is not False
        or selection.get("public_test_labels_used") is not False
        or selection.get("confirmatory_labels_used") is not False
        or selection.get("confirmatory_reservation_identity_only") is not True
        or not isinstance(partition_count, dict)
        or _strict_int(partition_count.get("CHECKPOINT"), "CHECKPOINT 표본 수") < 1
        or partition_count.get("PUBLIC_TEST") != 0
        or not isinstance(test, dict)
        or test.get("sample_count") != 0
        or test.get("status") != "FORBIDDEN_DURING_TRAINING_AND_SELECTION"
        or not isinstance(base_provenance, dict)
        or base_provenance.get("repository") != FAIR_BASELINE_MODEL
        or base_provenance.get("revision") != FAIR_BASELINE_MODEL_REVISION
        or base_provenance.get("weights_format") != "safetensors"
        or base_provenance.get("trust_remote_code") is not False
        or base_provenance.get("weights_only") is not True
        or base_provenance.get("full_finetune") is not True
        or base_provenance.get("classification_head_trainable") is not True
        or isinstance(trainable_parameters, bool)
        or not isinstance(trainable_parameters, int)
        or trainable_parameters < 1
        or trainable_parameters != total_parameters
        or not isinstance(environment, dict)
        or set(environment)
        != {
            "mps_available",
            "cuda_available",
            "trainer_device",
            "bitwise_deterministic_guaranteed",
            "reproducibility_limit",
        }
        or not isinstance(environment.get("mps_available"), bool)
        or not isinstance(environment.get("cuda_available"), bool)
        or not str(environment.get("trainer_device", "")).strip()
        or environment.get("bitwise_deterministic_guaranteed") is not False
        or not str(environment.get("reproducibility_limit", "")).strip()
    ):
        raise ValueError("동일 데이터 공정 기준선 학습 report 계약이 올바르지 않습니다.")
    _validate_training_runtime(runtime, "공정 기준선")
    _parse_aware_datetime(str(report.get("trained_at", "")), "fair trained_at")
    _validate_fair_partition_commitments(report.get("prepared_partition_commitments"))
    selection_breakdown = report.get("selection_breakdown")
    if not isinstance(selection_breakdown, dict):
        raise ValueError("공정 기준선 출처별 selection 지표가 없습니다.")
    values: list[float] = []
    for partition in FAIR_SELECTION_PARTITIONS:
        metrics = selection_breakdown.get(partition)
        if (
            not isinstance(metrics, dict)
            or _strict_int(metrics.get("sample_count"), f"{partition} 표본 수") < 1
        ):
            raise ValueError(f"공정 기준선 {partition} selection 지표가 올바르지 않습니다.")
        value = _strict_probability(metrics.get("macro_f1"), f"{partition} Macro-F1")
        values.append(value)
    selection_score = min(values)
    if not math.isclose(
        _strict_probability(selection.get("selection_score"), "selection score"),
        selection_score,
        rel_tol=0.0,
        abs_tol=1e-12,
    ):
        raise ValueError("공정 기준선 최저 출처 selection score를 재현할 수 없습니다.")
    overall = report.get("selection")
    if not isinstance(overall, dict):
        raise ValueError("공정 기준선 전체 selection 지표가 없습니다.")
    return selection_score, _strict_probability(overall.get("macro_f1"), "전체 Macro-F1")


def _validate_fair_partition_commitments(raw: Any) -> None:
    required = {
        "TRAIN",
        "CHECKPOINT",
        "CALIBRATION",
        "SELECTION",
        "NEWS_CONFIRMATORY_RESERVATION",
        "DISCLOSURE_CONFIRMATORY_RESERVATION",
    }
    if not isinstance(raw, dict) or set(raw) != required:
        raise ValueError("공정 기준선 준비 파티션 commitment가 없습니다.")
    for name, commitment in raw.items():
        if not isinstance(commitment, dict):
            raise ValueError(f"공정 기준선 {name} commitment가 올바르지 않습니다.")
        count = commitment.get("row_count")
        if isinstance(count, bool) or not isinstance(count, int) or count < 1:
            raise ValueError(f"공정 기준선 {name} commitment가 올바르지 않습니다.")
        _sha256_value(commitment.get("sha256"), str(name))


def _validate_training_runtime(raw: Any, label: str) -> None:
    required = {
        "trainer_device",
        "global_step",
        "train_runtime",
        "train_samples_per_second",
        "train_steps_per_second",
    }
    if not isinstance(raw, dict) or set(raw) != required:
        raise ValueError(f"{label} Trainer runtime provenance가 올바르지 않습니다.")
    global_step = raw.get("global_step")
    if isinstance(global_step, bool) or not isinstance(global_step, int) or global_step < 1:
        raise ValueError(f"{label} Trainer global_step이 올바르지 않습니다.")
    if not str(raw.get("trainer_device", "")).strip():
        raise ValueError(f"{label} Trainer device provenance가 없습니다.")
    for name in required - {"trainer_device", "global_step"}:
        value = raw.get(name)
        if (
            isinstance(value, bool)
            or not isinstance(value, int | float)
            or not math.isfinite(float(value))
            or float(value) < 0.0
        ):
            raise ValueError(f"{label} Trainer runtime 지표가 올바르지 않습니다: {name}")


def _validate_fair_training_provenance(report: dict[str, Any], project_root: Path) -> None:
    code = report.get("training_code")
    expected_code = {
        "fair_baseline_trainer": project_root / "scripts/train_k_fnspid_fair_baseline.py",
        "candidate_training_pipeline": project_root / "scripts/train_kf_deberta_sentiment_v2.py",
        "sentiment_input": project_root / "src/hannah_montana_ai/services/sentiment_input.py",
        "sentiment_protocol": project_root / "src/hannah_montana_ai/training/sentiment_protocol.py",
    }
    if not isinstance(code, dict) or set(code) != set(expected_code):
        raise ValueError("공정 기준선 학습 코드 provenance가 없습니다.")
    for name, path in expected_code.items():
        _validate_regular_file_commitment(path, code[name], f"공정 기준선 코드 {name}")

    dependencies = report.get("dependency_provenance")
    if not isinstance(dependencies, dict):
        raise ValueError("공정 기준선 dependency provenance가 없습니다.")
    lock_files = dependencies.get("lock_files")
    runtime_versions = dependencies.get("runtime_versions")
    expected_locks = {
        "pyproject": project_root / "pyproject.toml",
        "uv_lock": project_root / "uv.lock",
    }
    if (
        not isinstance(lock_files, dict)
        or set(lock_files) != set(expected_locks)
        or not isinstance(runtime_versions, dict)
        or not runtime_versions
    ):
        raise ValueError("공정 기준선 dependency provenance가 없습니다.")
    for name, path in expected_locks.items():
        _validate_regular_file_commitment(path, lock_files[name], f"공정 기준선 dependency {name}")
    dependency_payload = {"lock_files": lock_files, "runtime_versions": runtime_versions}
    if dependencies.get("dependency_contract_sha256") != canonical_json_sha256(dependency_payload):
        raise ValueError("공정 기준선 dependency provenance hash가 일치하지 않습니다.")


def _fair_protocol_signature(report: dict[str, Any]) -> str:
    arguments = report["training_arguments"]
    loss = report.get("loss")
    augmentation = report.get("target_swap_augmentation")
    selection = report.get("candidate_selection")
    prepared = report.get("prepared_partition_commitments")
    payload = {
        "dataset_revision": report.get("dataset_revision"),
        "public_dataset_revision": report.get("public_dataset_revision"),
        "input_artifacts": report.get("input_artifacts"),
        "training_arguments": {name: value for name, value in arguments.items() if name != "seed"},
        "training_strategy": report.get("training_strategy"),
        "loss_method": loss.get("method") if isinstance(loss, dict) else None,
        "rdrop_alpha": loss.get("rdrop_alpha") if isinstance(loss, dict) else None,
        "augmentation_method": (
            augmentation.get("method") if isinstance(augmentation, dict) else None
        ),
        "augmentation_budget": (
            augmentation.get("per_source") if isinstance(augmentation, dict) else None
        ),
        "augmentation_weight": (
            augmentation.get("sample_weight") if isinstance(augmentation, dict) else None
        ),
        "selection_method": (
            selection.get("selection_method") if isinstance(selection, dict) else None
        ),
        "required_sources": (
            selection.get("required_sources") if isinstance(selection, dict) else None
        ),
        "prepared_partition_commitments": prepared,
        "training_weight_audit": report.get("training_weight_audit"),
        "training_device_contract": report.get("training_environment"),
    }
    return canonical_json_sha256(payload)


def _validate_same_data_training_contract(
    fair_report: dict[str, Any],
    candidate_lock: dict[str, Any],
    project_root: Path,
) -> dict[str, Any]:
    candidate_report_path = _safe_project_path(
        project_root, candidate_lock.get("candidate_report_path"), "잠긴 후보 학습 report"
    )
    candidate_report = _load_json_object(candidate_report_path, "잠긴 후보 학습 report")
    candidate_manifest_path = _safe_project_path(
        project_root, candidate_lock.get("manifest_path"), "잠긴 후보 manifest"
    )
    candidate_manifest = _load_json_object(candidate_manifest_path, "잠긴 후보 manifest")
    ranking = candidate_manifest.get("ranking")
    if (
        not isinstance(ranking, list)
        or {
            _strict_int(row.get("seed"), "잠긴 후보 ranking seed")
            for row in ranking
            if isinstance(row, dict)
        }
        != set(FAIR_BASELINE_SEEDS)
        or len(ranking) != len(FAIR_BASELINE_SEEDS)
    ):
        raise ValueError("후보와 공정 기준선의 3-seed 선택 예산이 일치하지 않습니다.")

    candidate_inputs = candidate_report.get("input_artifacts")
    fair_inputs = fair_report.get("input_artifacts")
    if not isinstance(candidate_inputs, dict) or not isinstance(fair_inputs, dict):
        raise ValueError("후보 또는 공정 기준선 학습 입력 provenance가 없습니다.")
    matched_inputs: dict[str, dict[str, int | str]] = {}
    for fair_name, candidate_name in FAIR_TO_CANDIDATE_INPUTS.items():
        fair_record = fair_inputs.get(fair_name)
        candidate_record = candidate_inputs.get(candidate_name)
        if not isinstance(fair_record, dict) or not isinstance(candidate_record, dict):
            raise ValueError(f"동일 학습 입력 commitment가 없습니다: {fair_name}")
        fair_identity = _provenance_identity(fair_record, fair_name)
        candidate_identity = _provenance_identity(candidate_record, candidate_name)
        if fair_identity != candidate_identity:
            raise ValueError(f"후보와 공정 기준선의 학습 입력이 다릅니다: {fair_name}")
        matched_inputs[fair_name] = fair_identity

    candidate_arguments = candidate_report.get("training_arguments")
    fair_arguments = fair_report.get("training_arguments")
    if not isinstance(candidate_arguments, dict) or not isinstance(fair_arguments, dict):
        raise ValueError("후보 또는 공정 기준선 학습 예산 provenance가 없습니다.")
    equal_arguments: dict[str, Any] = {}
    for name in FAIR_EQUAL_TRAINING_ARGUMENTS:
        if candidate_arguments.get(name) != fair_arguments.get(name):
            raise ValueError(f"후보와 공정 기준선의 학습 예산이 다릅니다: {name}")
        equal_arguments[name] = fair_arguments[name]
    if equal_arguments.get("data_selection_seed") != DATA_SELECTION_SEED:
        raise ValueError("후보와 공정 기준선의 data selection seed가 고정값과 다릅니다.")
    if fair_report.get("dataset_revision") != candidate_report.get("dataset_revision"):
        raise ValueError("후보와 공정 기준선의 데이터셋 revision이 다릅니다.")
    if (
        fair_report.get("dataset_revision") != DATASET_REVISION
        or fair_report.get("public_dataset_revision") != PUBLIC_DATASET_REVISION
        or fair_report.get("public_dataset_revision")
        != candidate_report.get("public_dataset_revision")
    ):
        raise ValueError("후보와 공정 기준선의 K-FNSPID/공개 데이터 revision이 다릅니다.")
    candidate_prepared = candidate_report.get("prepared_partition_commitments")
    fair_prepared = fair_report.get("prepared_partition_commitments")
    _validate_fair_partition_commitments(candidate_prepared)
    _validate_fair_partition_commitments(fair_prepared)
    if candidate_prepared != fair_prepared:
        raise ValueError("후보와 공정 기준선의 준비 파티션 행 commitment가 다릅니다.")
    candidate_weight_audit = candidate_report.get("training_weight_audit")
    fair_weight_audit = fair_report.get("training_weight_audit")
    if not isinstance(candidate_weight_audit, dict) or candidate_weight_audit != fair_weight_audit:
        raise ValueError("후보와 공정 기준선의 학습 유효 가중치 구성이 다릅니다.")
    candidate_loss = candidate_report.get("loss")
    fair_loss = fair_report.get("loss")
    candidate_augmentation = candidate_report.get("target_swap_hard_negative_augmentation")
    fair_augmentation = fair_report.get("target_swap_augmentation")
    if (
        not isinstance(candidate_loss, dict)
        or not isinstance(fair_loss, dict)
        or candidate_loss.get("method") != fair_loss.get("method")
        or candidate_loss.get("rdrop_alpha") != fair_loss.get("rdrop_alpha")
        or not isinstance(candidate_augmentation, dict)
        or not isinstance(fair_augmentation, dict)
        or candidate_augmentation.get("method") != fair_augmentation.get("method")
        or candidate_augmentation.get("requested_per_source") != fair_augmentation.get("per_source")
        or candidate_augmentation.get("sample_weight") != fair_augmentation.get("sample_weight")
        or fair_augmentation.get("same_data_augmentation_schedule_as_candidate") is not True
        or candidate_augmentation.get("donor_absence_fields")
        != fair_augmentation.get("donor_absence_fields")
        or candidate_augmentation.get("donor_alias_provenance_preserved") is not True
        or fair_augmentation.get("donor_alias_provenance_preserved") is not True
    ):
        raise ValueError("후보와 공정 기준선의 손실·정규화 예산이 다릅니다.")
    candidate_code = candidate_report.get("training_code")
    fair_code = fair_report.get("training_code")
    if not isinstance(candidate_code, dict) or not isinstance(fair_code, dict):
        raise ValueError("후보 또는 공정 기준선 학습 코드 provenance가 없습니다.")
    candidate_trainer = candidate_code.get("trainer")
    fair_candidate_trainer = fair_code.get("candidate_training_pipeline")
    if (
        not isinstance(candidate_trainer, dict)
        or not isinstance(fair_candidate_trainer, dict)
        or _provenance_identity(candidate_trainer, "후보 trainer")
        != _provenance_identity(fair_candidate_trainer, "공정 기준선의 후보 trainer")
    ):
        raise ValueError("후보와 공정 기준선이 참조한 후보 학습 코드가 다릅니다.")
    candidate_dependencies = candidate_report.get("dependency_artifacts")
    fair_dependencies = fair_report.get("dependency_provenance")
    fair_lock_files = (
        fair_dependencies.get("lock_files") if isinstance(fair_dependencies, dict) else None
    )
    if not isinstance(candidate_dependencies, dict) or not isinstance(fair_lock_files, dict):
        raise ValueError("후보 또는 공정 기준선 dependency provenance가 없습니다.")
    for name in ("pyproject", "uv_lock"):
        candidate_dependency = candidate_dependencies.get(name)
        fair_dependency = fair_lock_files.get(name)
        if (
            not isinstance(candidate_dependency, dict)
            or not isinstance(fair_dependency, dict)
            or _provenance_identity(candidate_dependency, f"후보 {name}")
            != _provenance_identity(fair_dependency, f"공정 기준선 {name}")
        ):
            raise ValueError(f"후보와 공정 기준선 dependency가 다릅니다: {name}")
    candidate_selection = candidate_report.get("candidate_selection")
    fair_selection = fair_report.get("candidate_selection")
    if (
        not isinstance(candidate_selection, dict)
        or not isinstance(fair_selection, dict)
        or candidate_selection.get("selection_partition")
        != fair_selection.get("selection_partition")
        or candidate_selection.get("test_used_for_selection") is not False
        or candidate_selection.get("operational_gold_used_for_selection") is not False
        or candidate_selection.get("sealed_test_evaluated") is not False
    ):
        raise ValueError("후보와 공정 기준선의 selection 입력 계약이 다릅니다.")
    candidate_environment = candidate_report.get("training_environment")
    fair_environment = fair_report.get("training_environment")
    candidate_runtime = candidate_report.get("training_runtime")
    fair_runtime = fair_report.get("training_runtime")
    _validate_training_runtime(candidate_runtime, "후보")
    _validate_training_runtime(fair_runtime, "공정 기준선")
    device_fields = ("mps_available", "cuda_available", "trainer_device")
    if (
        not isinstance(candidate_environment, dict)
        or not isinstance(fair_environment, dict)
        or any(
            candidate_environment.get(name) != fair_environment.get(name)
            for name in device_fields
        )
        or not isinstance(candidate_runtime, dict)
        or not isinstance(fair_runtime, dict)
        or candidate_runtime.get("global_step") != fair_runtime.get("global_step")
    ):
        raise ValueError("후보와 공정 기준선의 실제 학습 device/update 계약이 다릅니다.")
    return {
        "candidate_training_report_sha256": file_sha256(candidate_report_path),
        "candidate_lock_manifest_sha256": file_sha256(candidate_manifest_path),
        "dataset_revision": str(fair_report.get("dataset_revision")),
        "public_dataset_revision": str(fair_report.get("public_dataset_revision")),
        "data_selection_seed": DATA_SELECTION_SEED,
        "seed_budget": list(FAIR_BASELINE_SEEDS),
        "matched_input_artifacts": matched_inputs,
        "equal_training_arguments": equal_arguments,
        "prepared_partition_commitments": fair_prepared,
        "training_weight_audit_sha256": canonical_json_sha256(fair_weight_audit),
        "training_device_contract": {
            name: fair_environment[name] for name in device_fields
        },
        "actual_global_step": int(fair_runtime["global_step"]),
        "model_specific_learning_rates": {
            "candidate_kf_deberta_lora": candidate_arguments.get("learning_rate"),
            "fair_kr_finbert_full_finetune": fair_arguments.get("learning_rate"),
            "reason": "optimizer stability differs between LoRA and full fine-tuning",
        },
        "loss_method": str(fair_loss["method"]),
        "target_swap_method": str(fair_augmentation["method"]),
        "candidate_trainer_sha256": str(candidate_trainer["sha256"]),
        "dependency_lock_sha256": {
            name: str(fair_lock_files[name]["sha256"]) for name in ("pyproject", "uv_lock")
        },
        "selection_inputs": list(FAIR_SELECTION_PARTITIONS),
        "public_test_labels_used": False,
        "confirmatory_labels_used": False,
    }


def _validate_fair_artifact_metadata(
    metadata: dict[str, Any],
    report: dict[str, Any],
    artifact_dir: Path,
) -> dict[str, Any]:
    manifest = metadata.get("artifact_files")
    try:
        metadata_biases = validated_sentiment_logit_biases(metadata.get("logit_bias_by_domain"))
        report_biases = validated_sentiment_logit_biases(report.get("logit_bias_by_domain"))
    except ValueError as exception:
        raise ValueError("공정 기준선 logit 보정 계약이 올바르지 않습니다.") from exception
    if (
        metadata.get("schema_version") != "k-fnspid-fair-baseline-artifact/v1"
        or metadata.get("version") != report.get("version")
        or metadata.get("base_model") != FAIR_BASELINE_MODEL
        or metadata.get("base_model_revision") != FAIR_BASELINE_MODEL_REVISION
        or metadata.get("weights_format") != "safetensors"
        or metadata.get("full_finetune") is not True
        or metadata.get("input_feature_version") != INPUT_FEATURE_VERSION
        or tuple(metadata.get("label_order", ())) != LABEL_ORDER
        or metadata.get("max_length") != report.get("max_length")
        or metadata.get("trained_at") != report.get("trained_at")
        or metadata_biases != report_biases
        or not isinstance(manifest, dict)
        or set(manifest) != set(FAIR_BASELINE_ARTIFACTS)
        or manifest != report.get("artifact_files")
        or not verify_artifact_manifest(artifact_dir, manifest)
    ):
        raise ValueError("동일 데이터 공정 기준선 artifact 계약이 올바르지 않습니다.")
    return manifest


def assert_same_data_fair_baseline_unchanged(
    artifact_dir: Path,
    selection_report_path: Path,
    provenance: dict[str, Any],
    *,
    project_root: Path,
) -> None:
    if _display_path(artifact_dir, project_root) != provenance.get("artifact_dir"):
        raise ValueError("공정 기준선 artifact 경로가 평가 중 변경됐습니다.")
    _assert_file_sha256(selection_report_path, str(provenance["selection_report_sha256"]))
    training_report_path = _safe_project_path(
        project_root, provenance.get("training_report_path"), "공정 기준선 학습 report"
    )
    _assert_file_sha256(training_report_path, str(provenance["training_report_sha256"]))
    _assert_file_sha256(artifact_dir / "hannah_metadata.json", str(provenance["metadata_sha256"]))
    manifest = provenance.get("artifact_files")
    if not isinstance(manifest, dict):
        raise ValueError("공정 기준선 artifact manifest가 없습니다.")
    _verify_file_manifest(artifact_dir, manifest)
    if canonical_json_sha256(manifest) != provenance.get("artifact_manifest_sha256"):
        raise ValueError("공정 기준선 artifact manifest hash가 평가 중 변경됐습니다.")


def create_consumption_receipt(
    path: Path,
    *,
    candidate_lock: dict[str, Any],
    news_sealed_gold: Path,
    disclosure_sealed_gold: Path,
    news_promotion_report: Path,
    disclosure_promotion_report: Path,
    sampling_design_report: Path,
    tfidf_model: Path,
    pre_k_fnspid_artifact: Path,
    pre_k_fnspid_training_report: Path,
    fair_baseline: dict[str, Any],
    report_path: Path,
    bootstrap_samples: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    for label, sealed_path in (
        ("뉴스", news_sealed_gold),
        ("공시", disclosure_sealed_gold),
    ):
        if sealed_path.is_symlink() or not sealed_path.is_file():
            raise ValueError(f"{label} 봉인 Gold가 없거나 symlink입니다: {sealed_path}")
    is_v6 = candidate_lock.get("model_family") == V6_MODEL_FAMILY
    fair_model_name = (
        V6_FAIR_BASELINE_MODEL_NAME if is_v6 else FAIR_BASELINE_MODEL_NAME
    )
    no_k_model_name = (
        V6_NO_K_ABLATION_MODEL_NAME if is_v6 else NO_K_ABLATION_MODEL_NAME
    )
    payload = {
        "schema_version": "sentiment-sealed-evaluation-consumption/v1",
        "consumed_at": datetime.now(UTC).isoformat(),
        "labels_loaded_before_receipt": False,
        "one_shot": True,
        "candidate_version": str(candidate_lock["version"]),
        "candidate_lock_manifest_sha256": str(candidate_lock["manifest_sha256"]),
        "candidate_artifact_manifest_sha256": str(candidate_lock["artifact_manifest_sha256"]),
        "candidate_git_attestation": dict(candidate_lock["external_git_attestation"]),
        "locked_baseline_commitments": candidate_lock["baseline_commitments"],
        "locked_baseline_commitments_sha256": candidate_lock[
            "baseline_commitments_sha256"
        ],
        "cpu_runtime_parity": candidate_lock["runtime_parity"],
        "sealed_gold": {
            "NEWS": {
                "path": _display_path(news_sealed_gold, PROJECT_ROOT),
                "sha256": file_sha256(news_sealed_gold),
            },
            "DISCLOSURE": {
                "path": _display_path(disclosure_sealed_gold, PROJECT_ROOT),
                "sha256": file_sha256(disclosure_sealed_gold),
            },
        },
        "promotion_reports": {
            "NEWS": {
                "path": _display_path(news_promotion_report, PROJECT_ROOT),
                "sha256": file_sha256(news_promotion_report),
            },
            "DISCLOSURE": {
                "path": _display_path(disclosure_promotion_report, PROJECT_ROOT),
                "sha256": file_sha256(disclosure_promotion_report),
            },
        },
        "sampling_design_report": {
            "path": _display_path(sampling_design_report, PROJECT_ROOT),
            "sha256": file_sha256(sampling_design_report),
        },
        "baseline_artifacts": {
            "hana_tfidf_logistic": {
                "path": _display_path(tfidf_model, PROJECT_ROOT),
                "sha256": file_sha256(tfidf_model),
            },
            PRE_K_FNSPID_MODEL_NAME: {
                "artifact_dir": _display_path(pre_k_fnspid_artifact, PROJECT_ROOT),
                "metadata_sha256": file_sha256(pre_k_fnspid_artifact / "hannah_metadata.json"),
                "training_report_path": _display_path(pre_k_fnspid_training_report, PROJECT_ROOT),
                "training_report_sha256": file_sha256(pre_k_fnspid_training_report),
            },
            fair_model_name: {
                "artifact_dir": fair_baseline["artifact_dir"],
                "artifact_manifest_sha256": fair_baseline["artifact_manifest_sha256"],
                "metadata_sha256": fair_baseline["metadata_sha256"],
                "selection_report_path": fair_baseline["selection_report_path"],
                "selection_report_sha256": fair_baseline["selection_report_sha256"],
                "training_report_path": fair_baseline["training_report_path"],
                "training_report_sha256": fair_baseline["training_report_sha256"],
                "same_data_contract_sha256": fair_baseline["same_data_contract_sha256"],
            },
            no_k_model_name: candidate_lock["baseline_commitments"]["baselines"][
                no_k_model_name
            ],
        },
        "evaluation_script_sha256": file_sha256(Path(__file__).resolve()),
        "planned_report_path": _display_path(report_path, PROJECT_ROOT),
        "bootstrap_samples": bootstrap_samples,
        "bootstrap_seed": bootstrap_seed,
    }
    _write_json_exclusive(path, payload)
    return payload


def _validate_reservation_commitment(
    raw: object,
    project_root: Path,
    expected_source: str,
    expected_partition: str,
) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise ValueError("봉인 reservation commitment가 JSON 객체가 아닙니다.")
    path = _safe_project_path(project_root, raw.get("path"), "봉인 reservation")
    if (
        raw.get("source_type") != expected_source
        or raw.get("partition") != expected_partition
        or raw.get("sha256") != file_sha256(path)
        or raw.get("bytes") != path.stat().st_size
    ):
        raise ValueError("봉인 reservation 파일 commitment가 일치하지 않습니다.")
    rows = _load_jsonl(path)
    item_ids, source_records = _reservation_identity_sets(rows, expected_source, expected_partition)
    if (
        raw.get("sample_count") != len(rows)
        or raw.get("item_id_set_sha256") != canonical_json_sha256(item_ids)
        or raw.get("source_record_set_sha256") != canonical_json_sha256(source_records)
    ):
        raise ValueError("봉인 reservation identity commitment가 일치하지 않습니다.")
    return dict(raw)


def _reservation_identity_sets(
    rows: list[dict[str, Any]],
    expected_source: str,
    expected_partition: str,
) -> tuple[list[str], list[dict[str, str]]]:
    item_ids: list[str] = []
    source_records: list[dict[str, str]] = []
    for row in rows:
        if (
            row.get("schema_version") != "k-fnspid-sentiment-review-row/v1"
            or row.get("source_type") != expected_source
            or row.get("partition") != expected_partition
            or row.get("review_status") != "NEEDS_BLIND_REVIEW"
            or row.get("final_sentiment") not in {"", None}
        ):
            raise ValueError("봉인 reservation review 계약이 올바르지 않습니다.")
        source_hash = canonical_json_sha256(row)
        item_id = _review_item_id(row, source_hash)
        item_ids.append(item_id)
        source_records.append({"item_id": item_id, "source_record_sha256": source_hash})
    if len(item_ids) < MIN_SEALED_SAMPLE_COUNT or len(item_ids) != len(set(item_ids)):
        raise ValueError("봉인 reservation 행 수 또는 item_id가 올바르지 않습니다.")
    item_ids.sort()
    source_records.sort(key=lambda row: row["item_id"])
    return item_ids, source_records


def _review_item_id(row: dict[str, Any], source_sha256: str) -> str:
    for field in ("review_key", "annotation_id", "item_id"):
        value = row.get(field)
        if isinstance(value, str) and value.strip():
            return value.strip()
    document_id = row.get("document_id")
    target = row.get("target_security") or row.get("stock_code")
    target_value = target.strip() if isinstance(target, str) else "UNSPECIFIED"
    if isinstance(document_id, str) and document_id.strip():
        return f"{document_id.strip()}::{target_value}"
    content_hash = row.get("content_hash")
    if isinstance(content_hash, str) and content_hash.strip():
        return f"{content_hash.strip()}::{target_value}"
    return source_sha256


def _validate_dataset_provenance(raw: object, project_root: Path) -> dict[str, dict[str, Any]]:
    if not isinstance(raw, dict):
        raise ValueError("후보 lock dataset provenance가 없습니다.")
    codebook = raw.get("codebook")
    sampling_implementation = raw.get("sampling_implementation")
    reports = raw.get("dataset_reports")
    if (
        not isinstance(codebook, dict)
        or not isinstance(sampling_implementation, dict)
        or not isinstance(reports, dict)
    ):
        raise ValueError("후보 lock dataset provenance 구성이 올바르지 않습니다.")
    validated: dict[str, dict[str, Any]] = {}
    for label, details in {
        "codebook": codebook,
        "sampling_implementation": sampling_implementation,
        **reports,
    }.items():
        if not isinstance(details, dict):
            raise ValueError(f"dataset provenance 항목이 올바르지 않습니다: {label}")
        path = _safe_project_path(project_root, details.get("path"), label)
        if (
            details.get("sha256") != file_sha256(path)
            or details.get("bytes") != path.stat().st_size
        ):
            raise ValueError(f"dataset provenance 파일이 변경됐습니다: {label}")
        validated[label] = {
            "path": _display_path(path, project_root),
            "sha256": str(details["sha256"]),
            "bytes": int(details["bytes"]),
        }
    if "SAMPLING_DESIGN" not in validated:
        raise ValueError("확률표본 sampling design provenance가 없습니다.")
    return validated


def _validate_recipe_commitments(raw: object, project_root: Path) -> dict[str, Any]:
    required_fields = {
        "schema_version",
        "training_script",
        "training_script_sha256",
        "auxiliary_training_gold_promoter",
        "auxiliary_training_gold_promoter_sha256",
        "blobs",
    }
    if not isinstance(raw, dict) or set(raw) != required_fields:
        raise ValueError("후보 lock recipe 구성이 올바르지 않습니다.")
    blobs = raw.get("blobs")
    expected_paths = dict(RECIPE_RELATIVE_PATHS)
    if (
        raw.get("schema_version") != "sentiment-candidate-recipe/v2"
        or not isinstance(blobs, dict)
        or set(blobs) != set(expected_paths)
    ):
        raise ValueError("후보 lock recipe blob 집합이 완전하지 않습니다.")
    validated_blobs: dict[str, dict[str, int | str]] = {}
    for name, expected_path in expected_paths.items():
        commitment = blobs.get(name)
        if (
            not isinstance(commitment, dict)
            or set(commitment) != {"path", "bytes", "sha256"}
            or commitment.get("path") != expected_path
        ):
            raise ValueError(f"후보 lock recipe commitment가 올바르지 않습니다: {name}")
        path = _safe_project_path(project_root, expected_path, f"recipe {name}")
        _validate_regular_file_commitment(path, commitment, f"recipe {name}")
        validated_blobs[name] = {
            "path": expected_path,
            "bytes": int(commitment["bytes"]),
            "sha256": str(commitment["sha256"]),
        }
    candidate_trainer = validated_blobs["candidate_trainer"]
    historical_promoter = validated_blobs["historical_auxiliary_promoter"]
    if (
        raw.get("training_script") != candidate_trainer["path"]
        or raw.get("training_script_sha256") != candidate_trainer["sha256"]
        or raw.get("auxiliary_training_gold_promoter") != historical_promoter["path"]
        or raw.get("auxiliary_training_gold_promoter_sha256")
        != historical_promoter["sha256"]
    ):
        raise ValueError("후보 lock recipe legacy commitment가 blob 집합과 다릅니다.")
    return {
        "schema_version": str(raw["schema_version"]),
        "training_script": str(raw["training_script"]),
        "training_script_sha256": str(raw["training_script_sha256"]),
        "auxiliary_training_gold_promoter": str(
            raw["auxiliary_training_gold_promoter"]
        ),
        "auxiliary_training_gold_promoter_sha256": str(
            raw["auxiliary_training_gold_promoter_sha256"]
        ),
        "blobs": validated_blobs,
    }


def _validate_v6_recipe_commitments(raw: object, project_root: Path) -> dict[str, Any]:
    if not isinstance(raw, dict) or set(raw) != {"schema_version", "blobs"}:
        raise ValueError("v6 후보 lock recipe 구성이 올바르지 않습니다.")
    blobs = raw.get("blobs")
    if (
        raw.get("schema_version") != "sentiment-candidate-recipe/v3"
        or not isinstance(blobs, dict)
        or set(blobs) != set(V6_RECIPE_RELATIVE_PATHS)
    ):
        raise ValueError("v6 후보 lock recipe blob 집합이 완전하지 않습니다.")
    validated: dict[str, dict[str, int | str]] = {}
    for name, relative in V6_RECIPE_RELATIVE_PATHS.items():
        commitment = blobs.get(name)
        if (
            not isinstance(commitment, dict)
            or set(commitment) != {"path", "bytes", "sha256"}
            or commitment.get("path") != relative
        ):
            raise ValueError(f"v6 후보 lock recipe commitment가 다릅니다: {name}")
        path = _safe_project_path(project_root, relative, f"v6 recipe {name}")
        _validate_regular_file_commitment(path, commitment, f"v6 recipe {name}")
        validated[name] = {
            "path": relative,
            "bytes": int(commitment["bytes"]),
            "sha256": str(commitment["sha256"]),
        }
    return {"schema_version": "sentiment-candidate-recipe/v3", "blobs": validated}


def validate_probability_sampling_design(
    report_path: Path,
    candidate_lock: dict[str, Any],
) -> dict[str, Any]:
    provenance = candidate_lock.get("dataset_provenance")
    commitment = provenance.get("SAMPLING_DESIGN") if isinstance(provenance, dict) else None
    if not isinstance(commitment, dict):
        raise ValueError("후보 lock에 sampling design commitment가 없습니다.")
    if (
        Path(str(commitment.get("path", ""))) != report_path.relative_to(PROJECT_ROOT)
        or commitment.get("sha256") != file_sha256(report_path)
        or commitment.get("bytes") != report_path.stat().st_size
    ):
        raise ValueError("sampling design report가 후보 lock과 일치하지 않습니다.")
    report = _load_json_object(report_path, "확률표본 sampling design")
    design = report.get("sampling_design")
    partitions = report.get("partitions")
    if (
        report.get("schema_version") != "k-fnspid-sentiment-confirmatory-sealed-sampling-design/v2"
        or report.get("report_role") != "UNLABELED_CONFIRMATORY_RESERVATION"
        or report.get("labels_available_at_reservation") is not False
        or report.get("candidate_predictions_available") is not False
        or not isinstance(design, dict)
        or design.get("method")
        != "stratified_equal_allocation_without_replacement_by_seeded_sha256_rank/v1"
        or not isinstance(design.get("weak_rule_stratum"), dict)
        or design["weak_rule_stratum"].get("version") != "k-fnspid-confirmatory-weak-stratum/v1"
        or not isinstance(partitions, dict)
    ):
        raise ValueError("확률표본 sampling design 계약이 올바르지 않습니다.")
    frame = report.get("estimand_and_frame")
    if (
        not isinstance(frame, dict)
        or not isinstance(frame.get("primary_estimands"), str)
        or not isinstance(frame.get("descriptive_secondary_estimand"), str)
        or frame.get("sampling_strata_role")
        != "Gold 감성이 아닌 사전 고정 weak-rule auxiliary strata"
        or frame.get("effective_trade_date_end_inclusive") != "2026-07-13"
        or frame.get("snapshot_max_effective_trade_date_observed_at_generation") != "2026-07-13"
        or frame.get("future_dates_after_snapshot_claimed") is not False
    ):
        raise ValueError("확률표본 모집단 snapshot 계약이 올바르지 않습니다.")
    expected = {
        "NEWS": "CONFIRMATORY_SEALED_TEST_REVIEW",
        "DISCLOSURE": "DISCLOSURE_CONFIRMATORY_SEALED_TEST_REVIEW",
    }
    normalized: dict[str, Any] = {
        "schema_version": str(report["schema_version"]),
        "report_path": _display_path(report_path, PROJECT_ROOT),
        "report_sha256": file_sha256(report_path),
        "method": str(design["method"]),
        "weak_rule_stratum": dict(design["weak_rule_stratum"]),
    }
    for source, partition_name in expected.items():
        partition = partitions.get(partition_name)
        reservation = candidate_lock["sealed_reservations"][source]
        if not isinstance(partition, dict) or not isinstance(reservation, dict):
            raise ValueError(f"{source} 확률표본 설계가 없습니다.")
        output = partition.get("output")
        strata = partition.get("strata")
        if (
            partition.get("source_type") != source
            or not isinstance(output, dict)
            or output.get("path") != reservation.get("path")
            or output.get("sha256") != reservation.get("sha256")
            or output.get("bytes") != reservation.get("bytes")
            or not isinstance(strata, dict)
            or set(strata) != set(LABEL_ORDER)
        ):
            raise ValueError(f"{source} 확률표본 artifact commitment가 다릅니다.")
        normalized_strata: dict[str, dict[str, float | int | str]] = {}
        total_sample = 0
        for label in LABEL_ORDER:
            stratum = strata[label]
            if not isinstance(stratum, dict):
                raise ValueError(f"{source}/{label} sampling stratum이 없습니다.")
            frame_count = stratum.get("frame_N_h")
            sample_count = stratum.get("sample_n_h")
            probability = stratum.get("inclusion_probability")
            weight = stratum.get("analysis_weight")
            finite_population = stratum.get("finite_population_correction")
            if (
                not isinstance(frame_count, int)
                or isinstance(frame_count, bool)
                or not isinstance(sample_count, int)
                or isinstance(sample_count, bool)
                or not 1 < sample_count <= frame_count
                or not isinstance(probability, (int, float))
                or isinstance(probability, bool)
                or not isinstance(weight, (int, float))
                or isinstance(weight, bool)
                or not math.isclose(float(probability), sample_count / frame_count)
                or not math.isclose(float(weight), frame_count / sample_count)
                or not isinstance(finite_population, dict)
            ):
                raise ValueError(f"{source}/{label} inclusion probability가 틀립니다.")
            expected_variance_multiplier = (frame_count - sample_count) / frame_count
            variance_multiplier = finite_population.get("variance_multiplier")
            standard_error_multiplier = finite_population.get("standard_error_multiplier")
            if (
                not isinstance(variance_multiplier, (int, float))
                or isinstance(variance_multiplier, bool)
                or not isinstance(standard_error_multiplier, (int, float))
                or isinstance(standard_error_multiplier, bool)
                or not math.isclose(
                    float(variance_multiplier),
                    expected_variance_multiplier,
                )
                or not math.isclose(
                    float(standard_error_multiplier),
                    math.sqrt(expected_variance_multiplier),
                )
            ):
                raise ValueError(f"{source}/{label} finite population correction이 틀립니다.")
            total_sample += sample_count
            normalized_strata[label] = {
                "frame_N_h": frame_count,
                "sample_n_h": sample_count,
                "inclusion_probability": float(probability),
                "analysis_weight": float(weight),
                "inclusion_probability_exact": str(stratum.get("inclusion_probability_exact", "")),
                "analysis_weight_exact": str(stratum.get("analysis_weight_exact", "")),
                "finite_population_variance_multiplier": expected_variance_multiplier,
            }
        if (
            partition.get("sample_count") != total_sample
            or reservation.get("sample_count") != total_sample
        ):
            raise ValueError(f"{source} 층별 표본 수 합계가 다릅니다.")
        normalized[source] = {
            "source_type": source,
            "partition": partition_name,
            "sample_count": total_sample,
            "population_frame_count": sum(
                int(row["frame_N_h"]) for row in normalized_strata.values()
            ),
            "strata": normalized_strata,
        }
    return normalized


def attach_probability_sampling_weights(
    gold_rows: list[dict[str, Any]],
    reservation: dict[str, Any],
    source_design: dict[str, Any],
) -> list[dict[str, Any]]:
    source = str(source_design["source_type"])
    partition = str(source_design["partition"])
    reservation_path = _safe_project_path(
        PROJECT_ROOT, reservation.get("path"), "확률표본 reservation"
    )
    review_rows = _load_jsonl(
        reservation_path,
        expected_sha256=str(reservation["sha256"]),
    )
    review_by_id: dict[str, dict[str, Any]] = {}
    for review_row in review_rows:
        source_hash = canonical_json_sha256(review_row)
        item_id = _review_item_id(review_row, source_hash)
        if item_id in review_by_id:
            raise ValueError("확률표본 reservation item_id가 중복됐습니다.")
        review_by_id[item_id] = review_row
    gold_by_id = {str(row.get("item_id", "")): row for row in gold_rows}
    if (
        len(gold_by_id) != len(gold_rows)
        or set(gold_by_id) != set(review_by_id)
        or len(gold_rows) != int(source_design["sample_count"])
    ):
        raise ValueError("확증 Gold는 봉인 확률표본 600건을 모두 포함해야 합니다.")
    observed: Counter[str] = Counter()
    weighted: list[dict[str, Any]] = []
    for gold_row in gold_rows:
        item_id = str(gold_row["item_id"])
        review_row = review_by_id[item_id]
        if review_row.get("source_type") != source or review_row.get("partition") != partition:
            raise ValueError("확률표본 reservation 출처 또는 파티션이 다릅니다.")
        stratum = prevalence_sampling_stratum(str(review_row["text"]), source)
        stratum_design = source_design["strata"][stratum]
        observed[stratum] += 1
        weighted.append(
            {
                **gold_row,
                "sampling_stratum": stratum,
                "inclusion_probability": float(stratum_design["inclusion_probability"]),
                "analysis_weight": float(stratum_design["analysis_weight"]),
            }
        )
    expected_counts = {
        label: int(source_design["strata"][label]["sample_n_h"]) for label in LABEL_ORDER
    }
    if dict(observed) != expected_counts:
        raise ValueError("확률표본 weak-rule 층별 표본 수가 sampling design과 다릅니다.")
    return weighted


def validate_sealed_gold_derivation(
    gold_path: Path,
    promotion_report_path: Path,
    reservation: dict[str, Any],
    *,
    expected_partition: str,
    expected_source: str,
    expected_candidate_manifest_sha256: str,
    expected_git_attestation_sha256: str,
    expected_git_commit_sha: str,
) -> dict[str, Any]:
    report = _load_json_object(promotion_report_path, "봉인 Gold 승격 report")
    hashes = report.get("file_sha256")
    integrity = report.get("integrity")
    provenance = report.get("provenance")
    review_provenance = provenance.get("review") if isinstance(provenance, dict) else None
    codex_provenance = provenance.get("codex_review") if isinstance(provenance, dict) else None
    coverage = report.get("coverage")
    source_distribution = (
        coverage.get("source_type_distribution") if isinstance(coverage, dict) else None
    )
    if (
        report.get("schema_version") != "k-fnspid-sentiment-gold-promotion-report/v1"
        or report.get("status") != "pass"
        or not isinstance(hashes, dict)
        or not isinstance(integrity, dict)
        or not isinstance(review_provenance, dict)
        or not isinstance(codex_provenance, dict)
        or review_provenance.get("partition") != expected_partition
        or codex_provenance.get("candidate_manifest_sha256") != expected_candidate_manifest_sha256
        or codex_provenance.get("candidate_git_attestation_sha256")
        != expected_git_attestation_sha256
        or codex_provenance.get("candidate_git_commit_sha") != expected_git_commit_sha
        or hashes.get("review_input") != reservation.get("sha256")
        or integrity.get("item_id_set_sha256") != reservation.get("item_id_set_sha256")
        or integrity.get("source_record_set_sha256") != reservation.get("source_record_set_sha256")
        or not isinstance(source_distribution, dict)
        or set(source_distribution) != {expected_source}
        or report.get("sample_count") != source_distribution.get(expected_source)
        or report.get("sample_count") != reservation.get("sample_count")
        or hashes.get("gold_output") != file_sha256(gold_path)
    ):
        raise ValueError("봉인 Gold가 pre-lock reservation에서 승격됐음을 증명할 수 없습니다.")
    return {
        "gold_sha256": str(hashes["gold_output"]),
        "promotion_report_sha256": file_sha256(promotion_report_path),
    }


def _assert_file_sha256(path: Path, expected: str) -> None:
    if file_sha256(path) != expected:
        raise ValueError(f"봉인 평가 중 파일이 변경됐습니다: {path}")


def _validate_training_report(report: dict[str, Any], winner: dict[str, Any]) -> None:
    selection = report.get("candidate_selection")
    test = report.get("test")
    arguments = report.get("training_arguments")
    base = report.get("base_model_provenance")
    prepared = report.get("prepared_partition_commitments")
    if (
        report.get("schema_version") != TRAINING_SCHEMA_VERSION
        or str(report.get("version", "")) != str(winner.get("version", ""))
        or not isinstance(selection, dict)
        or selection.get("test_used_for_selection") is not False
        or selection.get("operational_gold_used_for_selection") is not False
        or selection.get("sealed_test_evaluated") is not False
        or not isinstance(test, dict)
        or int(test.get("sample_count", -1)) != 0
        or test.get("status") != "SEALED_UNTIL_CANDIDATE_LOCK"
        or report.get("dataset_revision") != DATASET_REVISION
        or report.get("public_dataset_revision") != PUBLIC_DATASET_REVISION
        or report.get("training_strategy")
        != "group-purged-three-way-dual-gold-target-swap-rdrop-hierarchical-upper6-lora/v5"
        or not isinstance(arguments, dict)
        or arguments.get("data_selection_seed") != DATA_SELECTION_SEED
        or winner.get("data_selection_seed") != DATA_SELECTION_SEED
        or not isinstance(base, dict)
        or base.get("repository") != BASE_MODEL
        or base.get("revision") != BASE_MODEL_REVISION
        or base.get("source_weight_filename") != "pytorch_model.bin"
        or base.get("source_weights_format") != "pytorch_model.bin"
        or base.get("source_weight_sha256")
        != "3cd6cd7811b3c9190e97cae7eb41571c2bc0076431baae7d41d449a8c1c18c6c"
        or base.get("deserialization") != "torch_weights_only"
        or base.get("trust_remote_code") is not False
        or base.get("weights_only") is not True
    ):
        raise ValueError("후보 학습 report가 Test/Gold 봉인 계약을 위반했습니다.")
    _validate_fair_partition_commitments(prepared)
    if prepared != winner.get("prepared_partition_commitments"):
        raise ValueError("잠긴 후보의 준비 파티션 commitment가 report와 다릅니다.")
    _validate_training_runtime(report.get("training_runtime"), "후보")


def _validate_metadata(
    metadata: dict[str, Any],
    training_report: dict[str, Any],
    winner: dict[str, Any],
) -> None:
    max_length = metadata.get("max_length")
    try:
        metadata_biases = validated_sentiment_logit_biases(metadata.get("logit_bias_by_domain"))
        training_biases = validated_sentiment_logit_biases(
            training_report.get("logit_bias_by_domain")
        )
    except ValueError as exception:
        raise ValueError("artifact metadata의 감성 보정 계약이 올바르지 않습니다.") from exception
    if (
        metadata.get("schema_version") != ARTIFACT_SCHEMA_VERSION
        or metadata.get("version") != training_report.get("version")
        or metadata.get("version") != winner.get("version")
        or metadata.get("base_model") != BASE_MODEL
        or metadata.get("base_model_revision") != BASE_MODEL_REVISION
        or metadata.get("input_feature_version") != INPUT_FEATURE_VERSION
        or training_report.get("input_feature_version") != INPUT_FEATURE_VERSION
        or not isinstance(max_length, int)
        or isinstance(max_length, bool)
        or not 16 <= max_length <= 512
        or max_length != training_report.get("max_length")
        or tuple(metadata.get("label_order", ())) != LABEL_ORDER
        or metadata_biases != training_biases
    ):
        raise ValueError("artifact metadata의 버전 또는 입력 계약이 일치하지 않습니다.")


def load_public_test(dataset_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    partitions, audit = decontaminate_public_partitions(
        {
            "TRAIN": _load_public_rows(dataset_dir / "ratings_train.csv"),
            "VALIDATION": _load_public_rows(dataset_dir / "ratings_val.csv"),
            "TEST": _load_public_rows(dataset_dir / "ratings_test.csv"),
        }
    )
    rows: list[dict[str, Any]] = []
    for index, row in enumerate(partitions["TEST"]):
        text = str(row["text"])
        rows.append(
            {
                **row,
                "source_type": "NEWS",
                "event_cluster_id": f"public-record-{index}-{_text_sha256(text)[:16]}",
            }
        )
    if not rows:
        raise ValueError("공개 FNSentiment Test가 비어 있습니다.")
    return rows, audit


def _load_public_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"공개 감성 데이터 파일이 없습니다: {path}")
    rows: list[dict[str, str]] = []
    with path.open(encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file, delimiter="\t"):
            if row.get("document") and row.get("label") in SOURCE_LABEL:
                rows.append(
                    {"text": str(row["document"]), "label": SOURCE_LABEL[str(row["label"])]}
                )
    return rows


def load_sealed_gold(
    path: Path,
    *,
    expected_partition: str,
    expected_source: str,
    locked_at: datetime,
    expected_sha256: str | None = None,
    expected_candidate_manifest_sha256: str | None = None,
    expected_git_attestation_sha256: str | None = None,
    expected_git_commit_sha: str | None = None,
) -> list[dict[str, Any]]:
    payloads = _load_jsonl(path, expected_sha256=expected_sha256)
    rows: list[dict[str, Any]] = []
    identities: dict[str, set[str]] = {
        "document_id": set(),
        "canonical_url": set(),
        "content_hash": set(),
        "event_cluster_id": set(),
    }
    for payload in payloads:
        label = payload.get("sentiment")
        reviewed_at = _parse_aware_datetime(str(payload.get("reviewed_at", "")), "reviewed_at")
        promoted_at = _parse_aware_datetime(str(payload.get("promoted_at", "")), "promoted_at")
        annotation_times = _sealed_annotation_times(payload)
        if (
            payload.get("schema_version") != "k-fnspid-sentiment-codex-gold/v1"
            or payload.get("partition") != expected_partition
            or str(payload.get("source_type", "")).upper() != expected_source
            or payload.get("source_review_status") != "CODEX_REVIEW_APPROVED"
            or payload.get("review_status") != "CODEX_REVIEW_APPROVED"
            or payload.get("label_quality") != "GOLD"
            or payload.get("needs_codex_review") is not False
            or label not in LABEL_ORDER
            or payload.get("teacher_sentiment") not in LABEL_ORDER
            or not str(payload.get("reviewer_id", "")).strip()
            or reviewed_at > promoted_at
            or any(timestamp < locked_at for timestamp in annotation_times)
            or promoted_at < locked_at
            or not str(payload.get("text", "")).strip()
            or (
                expected_candidate_manifest_sha256 is not None
                and payload.get("candidate_manifest_sha256")
                != expected_candidate_manifest_sha256
            )
            or (
                expected_git_attestation_sha256 is not None
                and payload.get("candidate_git_attestation_sha256")
                != expected_git_attestation_sha256
            )
            or (
                expected_git_commit_sha is not None
                and payload.get("candidate_git_commit_sha") != expected_git_commit_sha
            )
        ):
            raise ValueError(f"봉인 Gold 검수 계약을 위반한 행이 있습니다: {path}")
        for key in identities:
            value = str(payload.get(key, "")).strip()
            if not value or value in identities[key]:
                raise ValueError(f"봉인 Gold {key}가 없거나 중복되었습니다: {path}")
            identities[key].add(value)
        rows.append(
            {
                **payload,
                "text": str(payload["text"]),
                "label": str(label),
                "source_type": expected_source,
            }
        )
    if not rows or set(str(row["label"]) for row in rows) != set(LABEL_ORDER):
        raise ValueError(f"봉인 Gold가 비었거나 3개 감성 등급을 모두 포함하지 않습니다: {path}")
    return rows


def _sealed_annotation_times(payload: dict[str, Any]) -> tuple[datetime, ...]:
    """후보 고정 이후에 생성된 teacher·독립 검수·재정 판정만 허용한다."""
    values: list[tuple[str, object]] = [
        ("teacher_generated_at_utc", payload.get("teacher_generated_at_utc")),
        ("reviewed_at", payload.get("reviewed_at")),
    ]
    for reviewer_name in ("reviewer_1", "reviewer_2"):
        reviewer = payload.get(reviewer_name)
        if not isinstance(reviewer, dict):
            raise ValueError(f"봉인 Gold {reviewer_name} provenance가 없습니다.")
        values.append((f"{reviewer_name}.reviewed_at", reviewer.get("reviewed_at")))
    adjudication = payload.get("adjudication")
    if isinstance(adjudication, dict):
        values.append(("adjudication.adjudicated_at", adjudication.get("adjudicated_at")))
    return tuple(_parse_aware_datetime(str(value or ""), field) for field, value in values)


def load_legacy_diagnostic(path: Path, expected_source: str) -> list[dict[str, Any]]:
    samples = load_labeled_alerts(path)
    rows: list[dict[str, Any]] = []
    for index, sample in enumerate(samples):
        if sample.sentiment not in LABEL_ORDER or sample.source_type != expected_source:
            raise ValueError(f"기존 Gold 감성 또는 출처가 올바르지 않습니다: {path}")
        identity = sample.event_cluster_id or sample.content_hash or sample.source_url
        if not identity:
            identity = f"legacy-record-{index}-{_text_sha256(sample.model_text)[:16]}"
        rows.append(
            {
                "text": sample.model_text,
                "label": sample.sentiment,
                "source_type": sample.source_type,
                "event_cluster_id": identity,
            }
        )
    if not rows:
        raise ValueError(f"기존 진단 Gold가 비어 있습니다: {path}")
    return rows


def predict_locked_candidate(
    rows: list[dict[str, Any]],
    artifact_dir: Path,
    candidate_lock: dict[str, Any],
    *,
    batch_size: int,
    base_model_dir: Path | None = None,
) -> list[str]:
    if candidate_lock.get("model_family") == V6_MODEL_FAMILY:
        if base_model_dir is None:
            raise ValueError("v6 canonical evaluator에는 검증할 base model 경로가 필요합니다.")
        contract = validate_source_hierarchical_artifact(artifact_dir)
        if (
            contract.version != candidate_lock.get("version")
            or contract.locked_manifest != candidate_lock.get("artifact_files")
            or contract.locked_manifest_sha256
            != candidate_lock.get("artifact_manifest_sha256")
            or contract.base_source_kind != candidate_lock.get("base_source_kind")
            or contract.base_source != candidate_lock.get("base_source")
        ):
            raise ValueError("v6 evaluator artifact가 candidate lock과 다릅니다.")
        base = validate_source_hierarchical_base_directory(base_model_dir)
        if contract.base_source_kind == "DAPT_MERGED_FP32":
            declared = contract.base_source.get("merged_directory")
            if (
                base.name != "merged_fp32"
                or not isinstance(declared, str)
                or base != Path(declared).resolve(strict=True)
            ):
                raise ValueError("v6 evaluator DAPT base는 잠긴 merged_fp32만 허용합니다.")
        runtime = load_source_hierarchical_runtime(
            artifact_dir=contract.artifact_dir,
            base_model_dir=base,
            max_length=contract.max_length,
            calibration_by_domain=contract.calibration_by_domain,
        )
        v6_predictions: list[str] = []
        for start in range(0, len(rows), batch_size):
            batch_rows = rows[start : start + batch_size]
            batch_predictions = runtime.predict_batch(
                tuple(
                    (
                        str(row["text"]),
                        str(row["source_type"]),
                        _target_security(row),
                    )
                    for row in batch_rows
                )
            )
            v6_predictions.extend(prediction.label for prediction in batch_predictions)
        post_load = validate_source_hierarchical_artifact(artifact_dir)
        if post_load.locked_manifest_sha256 != contract.locked_manifest_sha256:
            raise ValueError("v6 evaluator 실행 중 artifact가 변경되었습니다.")
        return v6_predictions

    import torch
    from peft import PeftModel
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(  # nosec B615 - hash 검증된 로컬 artifact
        artifact_dir,
        revision="local-verified-artifact",
        trust_remote_code=False,
        local_files_only=True,
    )
    base = AutoModelForSequenceClassification.from_pretrained(  # nosec B615 - revision 고정
        BASE_MODEL,
        revision=BASE_MODEL_REVISION,
        num_labels=len(LABEL_ORDER),
        id2label={index: label for index, label in enumerate(LABEL_ORDER)},
        label2id={label: index for index, label in enumerate(LABEL_ORDER)},
        trust_remote_code=False,
    )
    model = PeftModel.from_pretrained(
        base,
        artifact_dir,
        is_trainable=False,
        local_files_only=True,
        use_safetensors=True,
    )
    device = _torch_device(torch)
    model.to(device)
    model.eval()
    predictions: list[str] = []
    max_length = int(candidate_lock["max_length"])
    logit_bias_by_domain = validated_sentiment_logit_biases(candidate_lock["logit_bias_by_domain"])
    for start in range(0, len(rows), batch_size):
        batch_rows = rows[start : start + batch_size]
        features = [
            encode_sentiment_input(
                tokenizer,
                str(row["text"]),
                str(row["source_type"]),
                max_length,
                _target_security(row),
            )
            for row in batch_rows
        ]
        padded = tokenizer.pad(features, padding=True, return_tensors="pt")
        encoded = {name: value.to(device) for name, value in padded.items()}
        with torch.inference_mode():
            logits = model(**encoded).logits
            bias = logits.new_tensor(
                [
                    logit_bias_by_domain[
                        sentiment_source_domain(str(row["source_type"]), _target_security(row))
                    ]
                    for row in batch_rows
                ]
            )
            indices = (logits + bias).argmax(dim=-1).cpu().tolist()
        predictions.extend(LABEL_ORDER[int(index)] for index in indices)
    return predictions


def build_v6_contract_evaluation_fixture(
    *,
    rows: list[dict[str, Any]],
    artifact_dir: Path,
    base_model_dir: Path,
    candidate_lock: dict[str, Any],
    batch_size: int = EVALUATION_BATCH_SIZE,
) -> dict[str, Any]:
    winner = candidate_lock.get("winner")
    if (
        candidate_lock.get("schema_version") != V6_LOCK_SCHEMA_VERSION
        or candidate_lock.get("selection_only") is not True
        or not isinstance(winner, dict)
        or winner.get("model_family") != V6_MODEL_FAMILY
        or not rows
    ):
        raise ValueError("v6 evaluation fixture candidate lock 계약이 다릅니다.")
    allowed_fields = {"fixture_only", "item_id", "text", "source_type", "target_security"}
    for row in rows:
        if (
            set(row) - allowed_fields
            or row.get("fixture_only") is not True
            or not isinstance(row.get("item_id"), str)
            or not isinstance(row.get("text"), str)
            or row.get("source_type") not in {"NEWS", "DISCLOSURE"}
            or (
                row.get("source_type") == "DISCLOSURE"
                and not isinstance(row.get("target_security"), str)
            )
        ):
            raise ValueError("v6 evaluation fixture에는 명시적 mock 입력만 허용됩니다.")
    contract = validate_source_hierarchical_artifact(artifact_dir)
    if (
        winner.get("version") != contract.version
        or winner.get("artifact_files") != contract.locked_manifest
        or winner.get("artifact_manifest_sha256") != contract.locked_manifest_sha256
        or winner.get("base_source_kind") != contract.base_source_kind
        or winner.get("base_source") != contract.base_source
    ):
        raise ValueError("v6 evaluation fixture artifact가 candidate lock과 다릅니다.")
    normalized_lock = {
        "schema_version": V6_LOCK_SCHEMA_VERSION,
        "selection_only": True,
        "model_family": V6_MODEL_FAMILY,
        "version": contract.version,
        "artifact_files": contract.locked_manifest,
        "artifact_manifest_sha256": contract.locked_manifest_sha256,
    }
    predictions = predict_locked_candidate(
        rows,
        artifact_dir,
        {
            **normalized_lock,
            "base_source_kind": contract.base_source_kind,
            "base_source": contract.base_source,
        },
        batch_size=batch_size,
        base_model_dir=base_model_dir,
    )
    return {
        "schema_version": V6_BENCHMARK_SCHEMA_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "input_feature_version": INPUT_FEATURE_VERSION,
        "fixture_contract": {
            "schema_version": "sentiment-v6-evaluation-fixture/v1",
            "real_labels_opened": False,
            "mock_labels_only": True,
            "production_eligible": False,
        },
        "candidate_lock": normalized_lock,
        "mock_predictions": [
            {"item_id": str(row["item_id"]), "prediction": prediction}
            for row, prediction in zip(rows, predictions, strict=True)
        ],
        "deployment_gate": {
            "eligible": False,
            "decision": "FIXTURE_ONLY_DO_NOT_DEPLOY",
            "candidate_model": V6_CANDIDATE_MODEL,
            "candidate_model_family": V6_MODEL_FAMILY,
            "candidate_version": contract.version,
            "candidate_artifact_manifest_sha256": contract.locked_manifest_sha256,
        },
    }


def predict_tfidf(rows: list[dict[str, Any]], model_path: Path) -> list[str]:
    from hannah_montana_ai.services.model import MachineLearningFinancialNlpModel

    if not model_path.is_file() or model_path.is_symlink():
        raise ValueError(f"TF-IDF 모델 artifact가 없습니다: {model_path}")
    model = MachineLearningFinancialNlpModel(model_path)
    return [str(model.classify_sentiment(str(row["text"]))) for row in rows]


def predict_pre_k_fnspid(
    rows: list[dict[str, Any]],
    artifact_dir: Path,
    training_report_path: Path,
    *,
    batch_size: int,
) -> tuple[list[str], dict[str, Any]]:
    import torch
    from peft import PeftModel
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    if artifact_dir.is_symlink() or not artifact_dir.is_dir():
        raise ValueError("K-FNSPID 도입 전 감성 artifact가 없습니다.")
    metadata_path = artifact_dir / "hannah_metadata.json"
    metadata = _load_json_object(metadata_path, "K-FNSPID 도입 전 artifact metadata")
    training_report = _load_json_object(training_report_path, "K-FNSPID 도입 전 학습 report")
    manifest = metadata.get("artifact_files")
    max_length = metadata.get("max_length")
    if (
        metadata.get("schema_version") != "kf-deberta-sentiment-artifact/v1"
        or metadata.get("base_model") != BASE_MODEL
        or metadata.get("base_model_revision") != BASE_MODEL_REVISION
        or tuple(metadata.get("label_order", ())) != LABEL_ORDER
        or isinstance(max_length, bool)
        or not isinstance(max_length, int)
        or not 16 <= max_length <= 512
        or not isinstance(manifest, dict)
        or set(manifest) != set(REQUIRED_ARTIFACTS) - {"hannah_metadata.json"}
        or not verify_artifact_manifest(artifact_dir, manifest)
    ):
        raise ValueError("K-FNSPID 도입 전 감성 artifact 계약이 올바르지 않습니다.")
    pre_k_inputs = _validate_pre_k_training_report(training_report, metadata, manifest)
    tokenizer = AutoTokenizer.from_pretrained(  # nosec B615 - 검증된 로컬 artifact
        artifact_dir,
        revision="local-verified-artifact",
        trust_remote_code=False,
        local_files_only=True,
    )
    base = AutoModelForSequenceClassification.from_pretrained(  # nosec B615 - revision 고정
        BASE_MODEL,
        revision=BASE_MODEL_REVISION,
        num_labels=len(LABEL_ORDER),
        id2label={index: label for index, label in enumerate(LABEL_ORDER)},
        label2id={label: index for index, label in enumerate(LABEL_ORDER)},
        trust_remote_code=False,
    )
    model = PeftModel.from_pretrained(
        base,
        artifact_dir,
        is_trainable=False,
        local_files_only=True,
        use_safetensors=True,
    )
    device = _torch_device(torch)
    model.to(device)
    model.eval()
    texts = [str(row["text"]) for row in rows]
    predictions: list[str] = []
    for start in range(0, len(texts), batch_size):
        encoded = tokenizer(
            texts[start : start + batch_size],
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
        model_inputs = {name: value.to(device) for name, value in encoded.items()}
        with torch.inference_mode():
            indices = model(**model_inputs).logits.argmax(dim=-1).cpu().tolist()
        predictions.extend(LABEL_ORDER[int(index)] for index in indices)
    return predictions, {
        "model_name": PRE_K_FNSPID_MODEL_NAME,
        "version": str(metadata.get("version", "")),
        "artifact_dir": _display_path(artifact_dir, PROJECT_ROOT),
        "metadata_sha256": file_sha256(metadata_path),
        "training_report_path": _display_path(training_report_path, PROJECT_ROOT),
        "training_report_sha256": file_sha256(training_report_path),
        "input_feature_version": "plain-front-truncation/v1",
        "max_length": max_length,
        "k_fnspid_used_for_training": pre_k_inputs["k_fnspid_used_for_training"],
        "training_input_paths": pre_k_inputs["training_input_paths"],
    }


def predict_same_data_fair_baseline(
    rows: list[dict[str, Any]],
    artifact_dir: Path,
    provenance: dict[str, Any],
    *,
    batch_size: int,
) -> list[str]:
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    manifest = provenance.get("artifact_files")
    if not isinstance(manifest, dict):
        raise ValueError("동일 데이터 공정 기준선 artifact manifest가 없습니다.")
    _verify_file_manifest(artifact_dir, manifest)
    tokenizer = AutoTokenizer.from_pretrained(  # nosec B615 - hash 검증된 로컬 artifact
        artifact_dir,
        revision="local-verified-artifact",
        trust_remote_code=False,
        local_files_only=True,
    )
    model = AutoModelForSequenceClassification.from_pretrained(  # nosec B615 - 로컬 safetensors
        artifact_dir,
        revision="local-verified-artifact",
        trust_remote_code=False,
        local_files_only=True,
        use_safetensors=True,
    )
    device = _torch_device(torch)
    model.to(device)
    model.eval()
    max_length = _strict_int(provenance.get("max_length"), "공정 기준선 max_length")
    biases = validated_sentiment_logit_biases(provenance.get("logit_bias_by_domain"))
    predictions: list[str] = []
    for start in range(0, len(rows), batch_size):
        batch_rows = rows[start : start + batch_size]
        features = [
            encode_sentiment_input(
                tokenizer,
                str(row["text"]),
                str(row["source_type"]),
                max_length,
                _target_security(row),
            )
            for row in batch_rows
        ]
        padded = tokenizer.pad(features, padding=True, return_tensors="pt")
        encoded = {name: value.to(device) for name, value in padded.items()}
        with torch.inference_mode():
            logits = model(**encoded).logits
            bias = logits.new_tensor(
                [
                    biases[sentiment_source_domain(str(row["source_type"]), _target_security(row))]
                    for row in batch_rows
                ]
            )
            indices = (logits + bias).argmax(dim=-1).cpu().tolist()
        predictions.extend(LABEL_ORDER[int(index)] for index in indices)
    return predictions


def predict_v6_same_data_fair_baseline(
    rows: list[dict[str, Any]],
    artifact_dir: Path,
    *,
    batch_size: int,
) -> list[str]:
    try:
        runtime = load_kr_finbert_sc_v6_runtime(artifact_dir)
    except RuntimeError as exception:
        raise ValueError("v6 fair KR-FinBERT-SC runtime을 load할 수 없습니다.") from exception
    predictions: list[str] = []
    for start in range(0, len(rows), batch_size):
        batch = rows[start : start + batch_size]
        predicted = runtime.predict_batch(
            [
                (str(row["text"]), str(row["source_type"]), _target_security(row))
                for row in batch
            ]
        )
        predictions.extend(str(item.label) for item in predicted)
    return predictions


def predict_no_k_ablation(
    rows: list[dict[str, Any]],
    artifact_dir: Path,
    provenance: dict[str, Any],
    *,
    batch_size: int,
) -> list[str]:
    import torch
    from peft import PeftModel
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    manifest = provenance.get("artifact_files")
    if not isinstance(manifest, dict) or not manifest:
        raise ValueError("no-K ablation winner full manifest가 없습니다.")
    _verify_file_manifest(artifact_dir, manifest)
    if canonical_json_sha256(manifest) != provenance.get("artifact_manifest_sha256"):
        raise ValueError("no-K ablation artifact manifest digest가 다릅니다.")
    metadata = _load_json_object(
        artifact_dir / "hannah_metadata.json", "no-K ablation artifact metadata"
    )
    max_length = _strict_int(metadata.get("max_length"), "no-K max_length")
    if (
        metadata.get("schema_version") != "kf-deberta-sentiment-ablation-artifact/v1"
        or metadata.get("artifact_role") != "RESEARCH_ABLATION_NOT_DEPLOYABLE"
        or metadata.get("ablation_mode", metadata.get("mode")) != "NO_K"
        or tuple(metadata.get("label_order", ())) != LABEL_ORDER
        or not 16 <= max_length <= 512
    ):
        raise ValueError("no-K ablation artifact가 연구 전용 계약과 다릅니다.")
    biases = validated_sentiment_logit_biases(metadata.get("logit_bias_by_domain"))
    tokenizer = AutoTokenizer.from_pretrained(  # nosec B615 - hash 검증된 로컬 artifact
        artifact_dir,
        revision="local-verified-no-k-ablation",
        trust_remote_code=False,
        local_files_only=True,
    )
    if (artifact_dir / "adapter_model.safetensors").is_file():
        base = AutoModelForSequenceClassification.from_pretrained(  # nosec B615
            BASE_MODEL,
            revision=BASE_MODEL_REVISION,
            num_labels=len(LABEL_ORDER),
            id2label={index: label for index, label in enumerate(LABEL_ORDER)},
            label2id={label: index for index, label in enumerate(LABEL_ORDER)},
            trust_remote_code=False,
        )
        model = PeftModel.from_pretrained(
            base,
            artifact_dir,
            is_trainable=False,
            local_files_only=True,
            use_safetensors=True,
        )
    else:
        model = AutoModelForSequenceClassification.from_pretrained(  # nosec B615
            artifact_dir,
            revision="local-verified-no-k-ablation",
            trust_remote_code=False,
            local_files_only=True,
            use_safetensors=True,
        )
    device = torch.device("cpu")
    model.to(device)
    model.eval()
    predictions: list[str] = []
    for start in range(0, len(rows), batch_size):
        batch_rows = rows[start : start + batch_size]
        features = [
            encode_sentiment_input(
                tokenizer,
                str(row["text"]),
                str(row["source_type"]),
                max_length,
                _target_security(row),
            )
            for row in batch_rows
        ]
        padded = tokenizer.pad(features, padding=True, return_tensors="pt")
        encoded = {name: value.to(device) for name, value in padded.items()}
        with torch.inference_mode():
            logits = model(**encoded).logits
            bias = logits.new_tensor(
                [
                    biases[
                        sentiment_source_domain(
                            str(row["source_type"]), _target_security(row)
                        )
                    ]
                    for row in batch_rows
                ]
            )
            indices = (logits + bias).argmax(dim=-1).cpu().tolist()
        predictions.extend(LABEL_ORDER[int(index)] for index in indices)
    return predictions


def predict_v6_no_k_ablation(
    rows: list[dict[str, Any]],
    artifact_dir: Path,
    provenance: dict[str, Any],
    *,
    base_model_dir: Path,
    batch_size: int,
) -> list[str]:
    manifest = provenance.get("artifact_files")
    runtime_contract = provenance.get("runtime_loader_contract")
    if not isinstance(manifest, dict) or not isinstance(runtime_contract, dict):
        raise ValueError("v6 no-K artifact/runtime commitment가 없습니다.")
    _verify_file_manifest(artifact_dir, manifest)
    if canonical_json_sha256(manifest) != provenance.get("artifact_manifest_sha256"):
        raise ValueError("v6 no-K artifact manifest digest가 다릅니다.")
    try:
        verified_base = validate_source_hierarchical_base_directory(base_model_dir)
        calibration = validate_domain_calibration(runtime_contract.get("calibration"))
        runtime = load_source_hierarchical_runtime(
            artifact_dir=artifact_dir,
            base_model_dir=verified_base,
            max_length=_strict_int(runtime_contract.get("max_length"), "v6 no-K max_length"),
            calibration_by_domain=calibration,
        )
    except (RuntimeError, ValueError) as exception:
        raise ValueError("v6 no-K source-hierarchical runtime을 load할 수 없습니다.") from exception
    predictions: list[str] = []
    for start in range(0, len(rows), batch_size):
        batch = rows[start : start + batch_size]
        predicted = runtime.predict_batch(
            [
                (str(row["text"]), str(row["source_type"]), _target_security(row))
                for row in batch
            ]
        )
        predictions.extend(str(item.label) for item in predicted)
    return predictions


def _validate_pre_k_training_report(
    report: dict[str, Any],
    metadata: dict[str, Any],
    artifact_manifest: dict[str, Any],
) -> dict[str, Any]:
    dataset_files = report.get("dataset_files")
    operational_files = report.get("operational_training_files")
    if (
        report.get("schema_version") != "kf-deberta-sentiment-training/v1"
        or report.get("version") != metadata.get("version")
        or report.get("base_model") != BASE_MODEL
        or report.get("base_model_revision") != BASE_MODEL_REVISION
        or tuple(report.get("label_order", ())) != LABEL_ORDER
        or report.get("max_length") != metadata.get("max_length")
        or report.get("trained_at") != metadata.get("trained_at")
        or report.get("artifact_files") != artifact_manifest
        or report.get("dataset_source") != "mssongit/finance-task:fnsentiment"
        or not isinstance(dataset_files, dict)
        or not isinstance(operational_files, dict)
    ):
        raise ValueError("K-FNSPID 도입 전 학습 report 계약이 올바르지 않습니다.")
    training_input_paths = sorted(
        [f"data/external/kf_deberta_benchmark/{name}" for name in dataset_files]
        + [str(name) for name in operational_files]
    )
    if any("k_fnspid" in path.casefold() for path in training_input_paths):
        raise ValueError("K-FNSPID 도입 전 baseline 학습 입력에 K-FNSPID가 포함됐습니다.")
    return {
        "k_fnspid_used_for_training": False,
        "training_input_paths": training_input_paths,
    }


def _target_security(row: dict[str, Any]) -> str:
    target_security = row.get("target_security")
    if isinstance(target_security, str) and target_security.strip():
        return target_security.strip()
    stock_name = row.get("stock_name")
    if isinstance(stock_name, str) and stock_name.strip():
        return stock_name.strip()
    stock_code = row.get("stock_code")
    return str(stock_code).strip() if isinstance(stock_code, str) else ""


def predict_kr_finbert(
    rows: list[dict[str, Any]],
    *,
    tokenizer: Any,
    model: Any,
    batch_size: int,
    target_aware: bool,
    max_length: int,
) -> list[str]:
    import torch

    device = _torch_device(torch)
    model.to(device)
    model.eval()
    predictions: list[str] = []
    for start in range(0, len(rows), batch_size):
        batch_rows = rows[start : start + batch_size]
        if target_aware:
            features = [
                encode_sentiment_input(
                    tokenizer,
                    str(row["text"]),
                    str(row["source_type"]),
                    max_length,
                    _target_security(row),
                )
                for row in batch_rows
            ]
            encoded = tokenizer.pad(features, padding=True, return_tensors="pt")
        else:
            encoded = tokenizer(
                [str(row["text"]) for row in batch_rows],
                padding=True,
                truncation=True,
                max_length=max_length,
                return_tensors="pt",
            )
        model_inputs = {name: value.to(device) for name, value in encoded.items()}
        with torch.inference_mode():
            indices = model(**model_inputs).logits.argmax(dim=-1).cpu().tolist()
        for index in indices:
            configured = str(model.config.id2label.get(int(index), "")).upper()
            label = configured if configured in LABEL_ORDER else LABEL_ORDER[int(index)]
            predictions.append(label)
    return predictions


def evaluate_partition(
    rows: list[dict[str, Any]],
    predictions_by_model: dict[str, list[str]],
    *,
    role: str,
    cluster_protocol: str,
    bootstrap_samples: int,
    seed: int,
    analysis_weights: list[float] | None = None,
    sampling_strata: list[str] | None = None,
    population_counts_by_stratum: dict[str, int] | None = None,
    candidate_model_name: str = CANDIDATE_MODEL_NAME,
) -> dict[str, Any]:
    expected = [str(row["label"]) for row in rows]
    clusters = [str(row["event_cluster_id"]) for row in rows]
    provided_design_inputs = (
        analysis_weights is not None,
        sampling_strata is not None,
        population_counts_by_stratum is not None,
    )
    if any(provided_design_inputs) and not all(provided_design_inputs):
        raise ValueError("설계가중치, sampling strata, 모집단 층 크기는 함께 제공해야 합니다.")
    if role == "confirmatory_sealed_gold" and not all(provided_design_inputs):
        raise ValueError("확증 평가는 잠긴 확률표본 설계 입력을 모두 요구합니다.")
    if (
        analysis_weights is not None
        and sampling_strata is not None
        and population_counts_by_stratum is not None
    ):
        _validate_sampling_vectors(expected, analysis_weights, sampling_strata)
        _validate_population_counts(
            analysis_weights,
            sampling_strata,
            population_counts_by_stratum,
        )
    if candidate_model_name not in predictions_by_model:
        raise ValueError("잠긴 후보 예측이 없습니다.")
    models: dict[str, Any] = {}
    for index, (name, predicted) in enumerate(predictions_by_model.items()):
        model_result: dict[str, Any] = {
            **classification_metrics(expected, predicted),
            "cluster_bootstrap_95_ci": cluster_bootstrap_metrics(
                expected,
                predicted,
                clusters,
                samples=bootstrap_samples,
                seed=seed + index,
            ),
        }
        if (
            analysis_weights is not None
            and sampling_strata is not None
            and population_counts_by_stratum is not None
        ):
            model_result["sampling_design_weighted"] = weighted_classification_metrics(
                expected,
                predicted,
                analysis_weights,
            )
            model_result["stratified_cluster_bootstrap_95_ci"] = (
                stratified_cluster_bootstrap_metrics(
                    expected,
                    predicted,
                    clusters,
                    analysis_weights,
                    sampling_strata,
                    samples=bootstrap_samples,
                    seed=seed + 20 + index,
                )
            )
            model_result["sampling_design_delete_1_jackknife_95_ci"] = (
                stratified_delete_one_jackknife_metrics(
                    expected,
                    predicted,
                    clusters,
                    analysis_weights,
                    sampling_strata,
                    population_counts_by_stratum,
                )
            )
        models[name] = model_result
    confirmatory_partition = role == "confirmatory_sealed_gold"
    if candidate_model_name == V6_CANDIDATE_MODEL_NAME:
        claim_eligible_baselines = frozenset(V6_CONFIRMATORY_BASELINES)
    elif candidate_model_name == CANDIDATE_MODEL_NAME:
        claim_eligible_baselines = frozenset(CONFIRMATORY_BASELINE_MODEL_NAMES)
    else:
        # 알 수 없는 후보는 확증 유의성 주장을 만들 수 없다.
        claim_eligible_baselines = frozenset()
    comparisons: dict[str, Any] = {}
    for index, (name, baseline) in enumerate(predictions_by_model.items()):
        if name == candidate_model_name:
            continue
        included_in_holm_family = confirmatory_partition and name in claim_eligible_baselines
        comparison = paired_comparison(
            expected,
            baseline,
            predictions_by_model[candidate_model_name],
            clusters,
            samples=bootstrap_samples,
            seed=seed + 100 + index,
            confirmatory=included_in_holm_family,
            analysis_weights=analysis_weights,
            sampling_strata=sampling_strata,
            population_counts_by_stratum=population_counts_by_stratum,
        )
        comparison.update(
            {
                "included_in_holm_family": included_in_holm_family,
                "diagnostic_only": not included_in_holm_family,
                "claim_allowed": included_in_holm_family,
            }
        )
        comparisons[f"candidate_vs_{name}"] = comparison
    return {
        "role": role,
        "sample_count": len(rows),
        "label_distribution": dict(sorted(Counter(expected).items())),
        "event_cluster_count": len(set(clusters)),
        "cluster_bootstrap_protocol": cluster_protocol,
        "sampling_design_analysis": (
            {
                "method": (
                    "design-weighted plug-in confusion-matrix estimator with "
                    "SRSWOR FPC delete-1 jackknife"
                ),
                "primary_metric": "sampling-design-weighted plug-in Macro-F1",
                "macro_f1_estimator": (
                    "고정 설계가중 혼동행렬 셀 총계에 precision/recall/F1 함수를 "
                    "plug-in한 뒤 세 클래스 F1을 동일 가중 평균"
                ),
                "stratum_distribution": dict(sorted(Counter(sampling_strata).items())),
                "population_count_by_stratum": population_counts_by_stratum,
                "estimated_population_count": sum(analysis_weights),
                "weighted_metrics_are_primary": True,
                "primary_variance_method": (
                    "stratified SRSWOR delete-1 jackknife with finite-population correction"
                ),
            }
            if analysis_weights is not None and sampling_strata is not None
            else None
        ),
        "models": models,
        "statistical_comparisons": comparisons,
    }


def classification_metrics(expected: list[str], predicted: list[str]) -> dict[str, Any]:
    _validate_prediction_vectors(expected, predicted)
    matrix = confusion_matrix(expected, predicted, labels=LABEL_ORDER)
    precision, recall, class_f1, support = precision_recall_fscore_support(
        expected,
        predicted,
        labels=LABEL_ORDER,
        zero_division=0,
    )
    return {
        "accuracy": float(accuracy_score(expected, predicted)),
        "macro_f1": float(
            f1_score(
                expected,
                predicted,
                labels=LABEL_ORDER,
                average="macro",
                zero_division=0,
            )
        ),
        "label_metrics": {
            label: {
                "precision": float(precision[index]),
                "recall": float(recall[index]),
                "f1": float(class_f1[index]),
                "support": int(support[index]),
            }
            for index, label in enumerate(LABEL_ORDER)
        },
        "confusion_matrix": {
            truth: {
                guess: int(matrix[truth_index, guess_index])
                for guess_index, guess in enumerate(LABEL_ORDER)
            }
            for truth_index, truth in enumerate(LABEL_ORDER)
        },
        "confusion_matrix_label_order": list(LABEL_ORDER),
    }


def weighted_classification_metrics(
    expected: list[str],
    predicted: list[str],
    weights: list[float],
) -> dict[str, Any]:
    _validate_prediction_vectors(expected, predicted)
    _validate_weights(expected, weights)
    indices = {label: index for index, label in enumerate(LABEL_ORDER)}
    matrix = [[0.0] * len(LABEL_ORDER) for _ in LABEL_ORDER]
    for truth, guess, weight in zip(expected, predicted, weights, strict=True):
        matrix[indices[truth]][indices[guess]] += weight
    row_totals = [sum(row) for row in matrix]
    column_totals = [
        sum(row[column] for row in matrix) for column in range(len(LABEL_ORDER))
    ]
    class_metrics: dict[str, dict[str, float]] = {}
    class_f1: list[float] = []
    for index, label in enumerate(LABEL_ORDER):
        true_positive = matrix[index][index]
        precision = true_positive / column_totals[index] if column_totals[index] else 0.0
        recall = true_positive / row_totals[index] if row_totals[index] else 0.0
        f1 = 2.0 * precision * recall / (precision + recall) if precision + recall else 0.0
        class_f1.append(f1)
        class_metrics[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "estimated_support": row_totals[index],
        }
    population_count = sum(weights)
    return {
        "estimator": "sampling-design-weighted plug-in confusion-matrix/v1",
        "macro_f1_definition": (
            "설계가중 혼동행렬로 클래스별 precision·recall·F1을 plug-in 계산한 뒤 "
            "NEGATIVE/NEUTRAL/POSITIVE F1을 동일 가중 평균"
        ),
        "accuracy": sum(matrix[index][index] for index in range(len(LABEL_ORDER)))
        / population_count,
        "macro_f1": sum(class_f1) / len(LABEL_ORDER),
        "label_metrics": class_metrics,
        "confusion_matrix": {
            truth: {
                guess: matrix[truth_index][guess_index]
                for guess_index, guess in enumerate(LABEL_ORDER)
            }
            for truth_index, truth in enumerate(LABEL_ORDER)
        },
        "confusion_matrix_label_order": list(LABEL_ORDER),
        "estimated_population_count": population_count,
    }


def cluster_bootstrap_metrics(
    expected: list[str],
    predicted: list[str],
    clusters: list[str],
    *,
    samples: int,
    seed: int,
) -> dict[str, Any]:
    grouped = _cluster_indices(clusters)
    generator = random.Random(seed)  # noqa: S311  # nosec B311 - 재현 가능한 통계 표본
    cluster_names = sorted(grouped)
    values: dict[str, list[float]] = {"accuracy": [], "macro_f1": []}
    for _ in range(samples):
        indices = [
            index for _ in cluster_names for index in grouped[generator.choice(cluster_names)]
        ]
        metrics = _fast_metrics(
            [expected[index] for index in indices],
            [predicted[index] for index in indices],
        )
        for name in values:
            values[name].append(metrics[name])
    return {
        "samples": samples,
        "seed": seed,
        "cluster_count": len(grouped),
        **{name: percentile_interval(metric_values) for name, metric_values in values.items()},
    }


def stratified_cluster_bootstrap_metrics(
    expected: list[str],
    predicted: list[str],
    clusters: list[str],
    weights: list[float],
    strata: list[str],
    *,
    samples: int,
    seed: int,
) -> dict[str, Any]:
    grouped = _stratified_cluster_groups(clusters, strata)
    generator = random.Random(seed)  # noqa: S311  # nosec B311 - 재현 가능한 통계 표본
    values: dict[str, list[float]] = {"accuracy": [], "macro_f1": []}
    for _ in range(samples):
        indices = [
            index
            for stratum in LABEL_ORDER
            for _ in grouped[stratum]
            for index in grouped[stratum][generator.randrange(len(grouped[stratum]))]
        ]
        metrics = _fast_weighted_metrics(
            [expected[index] for index in indices],
            [predicted[index] for index in indices],
            [weights[index] for index in indices],
        )
        for name in values:
            values[name].append(metrics[name])
    return {
        "samples": samples,
        "seed": seed,
        "resampling_unit": "event_cluster_within_sampling_stratum",
        "cluster_count_by_stratum": {label: len(grouped[label]) for label in LABEL_ORDER},
        **{name: percentile_interval(metric_values) for name, metric_values in values.items()},
    }


def stratified_delete_one_jackknife_metrics(
    expected: list[str],
    predicted: list[str],
    clusters: list[str],
    weights: list[float],
    strata: list[str],
    population_counts: dict[str, int],
) -> dict[str, Any]:
    """층화 SRSWOR 확률표본의 비선형 지표 분산을 FPC jackknife로 추정한다."""
    _validate_unique_sampling_units(clusters, strata)
    _validate_population_counts(weights, strata, population_counts)
    estimate = _fast_weighted_metrics(expected, predicted, weights)
    replicate_metrics = _delete_one_replicate_metrics(
        expected,
        predicted,
        weights,
        strata,
    )
    intervals = {
        metric: _fpc_jackknife_interval(
            estimate[metric],
            {label: [row[metric] for row in replicate_metrics[label]] for label in LABEL_ORDER},
            population_counts,
        )
        for metric in ("accuracy", "macro_f1")
    }
    return {
        "method": "stratified_delete_1_jackknife_srswor_fpc/v1",
        "resampling_unit": "unique_event_cluster",
        "replicate_count": sum(len(rows) for rows in replicate_metrics.values()),
        "sample_n_h": dict(sorted(Counter(strata).items())),
        "population_N_h": {label: population_counts[label] for label in LABEL_ORDER},
        **intervals,
    }


def paired_stratified_delete_one_jackknife(
    expected: list[str],
    baseline: list[str],
    candidate: list[str],
    clusters: list[str],
    weights: list[float],
    strata: list[str],
    population_counts: dict[str, int],
) -> dict[str, Any]:
    _validate_unique_sampling_units(clusters, strata)
    _validate_population_counts(weights, strata, population_counts)
    baseline_estimate = _fast_weighted_metrics(expected, baseline, weights)
    candidate_estimate = _fast_weighted_metrics(expected, candidate, weights)
    baseline_replicates = _delete_one_replicate_metrics(
        expected,
        baseline,
        weights,
        strata,
    )
    candidate_replicates = _delete_one_replicate_metrics(
        expected,
        candidate,
        weights,
        strata,
    )
    results: dict[str, Any] = {}
    for metric in ("accuracy", "macro_f1"):
        estimate = candidate_estimate[metric] - baseline_estimate[metric]
        replicate_differences = {
            label: [
                candidate_row[metric] - baseline_row[metric]
                for baseline_row, candidate_row in zip(
                    baseline_replicates[label],
                    candidate_replicates[label],
                    strict=True,
                )
            ]
            for label in LABEL_ORDER
        }
        interval = _fpc_jackknife_interval(
            estimate,
            replicate_differences,
            population_counts,
            bounded=False,
        )
        standard_error = float(interval["standard_error"])
        if standard_error == 0.0:
            # 비선형 Macro-F1의 퇴화 jackknife를 완전한 증거로 해석하지 않는다.
            p_value = 1.0
        else:
            p_value = math.erfc(abs(estimate / standard_error) / math.sqrt(2.0))
        results[f"{metric}_difference"] = {
            **interval,
            "two_sided_normal_p_value": p_value,
        }
    return {
        "method": "paired_stratified_delete_1_jackknife_srswor_fpc/v1",
        "resampling_unit": "unique_event_cluster",
        "replicate_count": sum(Counter(strata).values()),
        "sample_n_h": dict(sorted(Counter(strata).items())),
        "population_N_h": {label: population_counts[label] for label in LABEL_ORDER},
        **results,
    }


def _delete_one_replicate_metrics(
    expected: list[str],
    predicted: list[str],
    weights: list[float],
    strata: list[str],
) -> dict[str, list[dict[str, float]]]:
    indices_by_stratum = {
        label: [index for index, stratum in enumerate(strata) if stratum == label]
        for label in LABEL_ORDER
    }
    replicates: dict[str, list[dict[str, float]]] = {label: [] for label in LABEL_ORDER}
    for label, stratum_indices in indices_by_stratum.items():
        sample_count = len(stratum_indices)
        if sample_count < 2:
            raise ValueError(f"{label} 층은 delete-1 jackknife에 2건 이상 필요합니다.")
        stratum_set = set(stratum_indices)
        inflation = sample_count / (sample_count - 1)
        for deleted_index in stratum_indices:
            kept_indices = [index for index in range(len(expected)) if index != deleted_index]
            replicate_weights = [
                weights[index] * inflation if index in stratum_set else weights[index]
                for index in kept_indices
            ]
            replicates[label].append(
                _fast_weighted_metrics(
                    [expected[index] for index in kept_indices],
                    [predicted[index] for index in kept_indices],
                    replicate_weights,
                )
            )
    return replicates


def _fpc_jackknife_interval(
    estimate: float,
    replicates: dict[str, list[float]],
    population_counts: dict[str, int],
    *,
    bounded: bool = True,
) -> dict[str, float]:
    variance = 0.0
    for label in LABEL_ORDER:
        values = replicates[label]
        sample_count = len(values)
        mean = sum(values) / sample_count
        population_count = population_counts[label]
        fpc = (population_count - sample_count) / population_count
        variance += (
            fpc * (sample_count - 1) / sample_count * sum((value - mean) ** 2 for value in values)
        )
    standard_error = math.sqrt(max(0.0, variance))
    low = estimate - 1.959963984540054 * standard_error
    high = estimate + 1.959963984540054 * standard_error
    if bounded:
        low, high = max(0.0, low), min(1.0, high)
    return {
        "estimate": estimate,
        "variance": variance,
        "standard_error": standard_error,
        "low": low,
        "high": high,
    }


def paired_comparison(
    expected: list[str],
    baseline: list[str],
    candidate: list[str],
    clusters: list[str],
    *,
    samples: int,
    seed: int,
    confirmatory: bool,
    analysis_weights: list[float] | None = None,
    sampling_strata: list[str] | None = None,
    population_counts_by_stratum: dict[str, int] | None = None,
) -> dict[str, Any]:
    _validate_prediction_vectors(expected, baseline)
    _validate_prediction_vectors(expected, candidate)
    observed_baseline = _fast_metrics(expected, baseline)
    observed_candidate = _fast_metrics(expected, candidate)
    record_differences = _paired_bootstrap_differences(
        expected,
        baseline,
        candidate,
        [[index] for index in range(len(expected))],
        samples=samples,
        seed=seed,
    )
    cluster_differences = _paired_bootstrap_differences(
        expected,
        baseline,
        candidate,
        list(_cluster_indices(clusters).values()),
        samples=samples,
        seed=seed + 1,
    )
    baseline_only = sum(
        truth == left and truth != right
        for truth, left, right in zip(expected, baseline, candidate, strict=True)
    )
    candidate_only = sum(
        truth != left and truth == right
        for truth, left, right in zip(expected, baseline, candidate, strict=True)
    )
    result: dict[str, Any] = {
        "observed_difference": {
            name: observed_candidate[name] - observed_baseline[name]
            for name in ("accuracy", "macro_f1")
        },
        "paired_record_bootstrap_95_ci": record_differences,
        "paired_event_cluster_bootstrap_95_ci": cluster_differences,
        "mcnemar_exact_two_sided": {
            "baseline_only_correct": baseline_only,
            "candidate_only_correct": candidate_only,
            "discordant_count": baseline_only + candidate_only,
            "p_value": exact_mcnemar_p_value(baseline_only, candidate_only),
        },
        "confirmatory_significance_claim_allowed": confirmatory,
    }
    if analysis_weights is not None and sampling_strata is not None:
        if population_counts_by_stratum is None:
            raise ValueError("확증 비교에 모집단 층 크기가 없습니다.")
        _validate_sampling_vectors(expected, analysis_weights, sampling_strata)
        _validate_population_counts(
            analysis_weights,
            sampling_strata,
            population_counts_by_stratum,
        )
        weighted_baseline = _fast_weighted_metrics(expected, baseline, analysis_weights)
        weighted_candidate = _fast_weighted_metrics(expected, candidate, analysis_weights)
        grouped = _stratified_cluster_groups(clusters, sampling_strata)
        result["observed_sampling_design_weighted_difference"] = {
            name: weighted_candidate[name] - weighted_baseline[name]
            for name in ("accuracy", "macro_f1")
        }
        result["paired_stratified_event_cluster_bootstrap_95_ci"] = (
            _paired_stratified_bootstrap_differences(
                expected,
                baseline,
                candidate,
                analysis_weights,
                grouped,
                samples=samples,
                seed=seed + 2,
            )
        )
        result["paired_cluster_randomization_two_sided"] = _paired_cluster_randomization_test(
            expected,
            baseline,
            candidate,
            analysis_weights,
            grouped,
            samples=samples,
            seed=seed + 3,
        )
        result["paired_sampling_design_delete_1_jackknife_95_ci"] = (
            paired_stratified_delete_one_jackknife(
                expected,
                baseline,
                candidate,
                clusters,
                analysis_weights,
                sampling_strata,
                population_counts_by_stratum,
            )
        )
    return result


def _paired_bootstrap_differences(
    expected: list[str],
    baseline: list[str],
    candidate: list[str],
    groups: list[list[int]],
    *,
    samples: int,
    seed: int,
) -> dict[str, Any]:
    if not groups:
        raise ValueError("bootstrap 그룹이 없습니다.")
    generator = random.Random(seed)  # noqa: S311  # nosec B311 - 재현 가능한 통계 표본
    values: dict[str, list[float]] = {
        "accuracy_difference": [],
        "macro_f1_difference": [],
    }
    for _ in range(samples):
        indices = [index for _ in groups for index in generator.choice(groups)]
        truth = [expected[index] for index in indices]
        left = _fast_metrics(truth, [baseline[index] for index in indices])
        right = _fast_metrics(truth, [candidate[index] for index in indices])
        values["accuracy_difference"].append(right["accuracy"] - left["accuracy"])
        values["macro_f1_difference"].append(right["macro_f1"] - left["macro_f1"])
    return {
        "samples": samples,
        "seed": seed,
        **{name: percentile_interval(metric_values) for name, metric_values in values.items()},
    }


def _paired_stratified_bootstrap_differences(
    expected: list[str],
    baseline: list[str],
    candidate: list[str],
    weights: list[float],
    grouped: dict[str, list[list[int]]],
    *,
    samples: int,
    seed: int,
) -> dict[str, Any]:
    generator = random.Random(seed)  # noqa: S311  # nosec B311 - 재현 가능한 통계 표본
    values: dict[str, list[float]] = {
        "accuracy_difference": [],
        "macro_f1_difference": [],
    }
    for _ in range(samples):
        indices = [
            index
            for stratum in LABEL_ORDER
            for _ in grouped[stratum]
            for index in grouped[stratum][generator.randrange(len(grouped[stratum]))]
        ]
        truth = [expected[index] for index in indices]
        sampled_weights = [weights[index] for index in indices]
        left = _fast_weighted_metrics(
            truth,
            [baseline[index] for index in indices],
            sampled_weights,
        )
        right = _fast_weighted_metrics(
            truth,
            [candidate[index] for index in indices],
            sampled_weights,
        )
        values["accuracy_difference"].append(right["accuracy"] - left["accuracy"])
        values["macro_f1_difference"].append(right["macro_f1"] - left["macro_f1"])
    return {
        "samples": samples,
        "seed": seed,
        "resampling_unit": "event_cluster_within_sampling_stratum",
        **{name: percentile_interval(metric_values) for name, metric_values in values.items()},
    }


def _paired_cluster_randomization_test(
    expected: list[str],
    baseline: list[str],
    candidate: list[str],
    weights: list[float],
    grouped: dict[str, list[list[int]]],
    *,
    samples: int,
    seed: int,
) -> dict[str, Any]:
    observed = (
        _fast_weighted_metrics(expected, candidate, weights)["macro_f1"]
        - (_fast_weighted_metrics(expected, baseline, weights)["macro_f1"])
    )
    generator = random.Random(seed)  # noqa: S311  # nosec B311 - 재현 가능한 통계 표본
    extreme = 0
    all_groups = [group for label in LABEL_ORDER for group in grouped[label]]
    for _ in range(samples):
        randomized_baseline = list(baseline)
        randomized_candidate = list(candidate)
        for group in all_groups:
            if generator.getrandbits(1):
                for index in group:
                    randomized_baseline[index], randomized_candidate[index] = (
                        randomized_candidate[index],
                        randomized_baseline[index],
                    )
        randomized = (
            _fast_weighted_metrics(expected, randomized_candidate, weights)["macro_f1"]
            - _fast_weighted_metrics(expected, randomized_baseline, weights)["macro_f1"]
        )
        if abs(randomized) >= abs(observed):
            extreme += 1
    return {
        "metric": "sampling_design_weighted_macro_f1_difference",
        "resampling_unit": "event_cluster",
        "samples": samples,
        "seed": seed,
        "observed_difference": observed,
        "p_value": (extreme + 1) / (samples + 1),
    }


def source_summary(
    result: dict[str, Any],
    path: Path,
    *,
    candidate_model_name: str = CANDIDATE_MODEL_NAME,
    fair_model_name: str = FAIR_BASELINE_MODEL_NAME,
    no_k_model_name: str = NO_K_ABLATION_MODEL_NAME,
) -> dict[str, Any]:
    candidate = result["models"][candidate_model_name]
    baseline = result["models"]["hana_tfidf_logistic"]
    candidate_primary = candidate.get("sampling_design_weighted", candidate)
    baseline_primary = baseline.get("sampling_design_weighted", baseline)
    summary = {
        **result,
        "path": _display_path(path, PROJECT_ROOT),
        "sha256": file_sha256(path),
        "sample_count": int(result["sample_count"]),
        "accuracy": float(candidate_primary["accuracy"]),
        "macro_f1": float(candidate_primary["macro_f1"]),
        "unweighted_sample_accuracy": float(candidate["accuracy"]),
        "unweighted_sample_macro_f1": float(candidate["macro_f1"]),
        "baseline_accuracy": float(baseline_primary["accuracy"]),
        "baseline_macro_f1": float(baseline_primary["macro_f1"]),
    }
    reference = result["models"].get("kr_finbert_sc")
    if isinstance(reference, dict):
        reference_primary = reference.get("sampling_design_weighted", reference)
        summary["kr_finbert_sc_accuracy"] = float(reference_primary["accuracy"])
        summary["kr_finbert_sc_macro_f1"] = float(reference_primary["macro_f1"])
    raw_reference = result["models"].get("kr_finbert_sc_raw_off_the_shelf")
    if isinstance(raw_reference, dict):
        raw_primary = raw_reference.get("sampling_design_weighted", raw_reference)
        summary["kr_finbert_sc_raw_accuracy"] = float(raw_primary["accuracy"])
        summary["kr_finbert_sc_raw_macro_f1"] = float(raw_primary["macro_f1"])
    teacher = result["models"].get(QWEN_TEACHER_MODEL_NAME)
    if isinstance(teacher, dict):
        teacher_primary = teacher.get("sampling_design_weighted", teacher)
        summary["qwen3_4b_teacher_accuracy"] = float(teacher_primary["accuracy"])
        summary["qwen3_4b_teacher_macro_f1"] = float(teacher_primary["macro_f1"])
    pre_k_fnspid = result["models"].get(PRE_K_FNSPID_MODEL_NAME)
    if isinstance(pre_k_fnspid, dict):
        pre_k_primary = pre_k_fnspid.get("sampling_design_weighted", pre_k_fnspid)
        summary["pre_k_fnspid_accuracy"] = float(pre_k_primary["accuracy"])
        summary["pre_k_fnspid_macro_f1"] = float(pre_k_primary["macro_f1"])
    fair_baseline = result["models"].get(fair_model_name)
    if isinstance(fair_baseline, dict):
        fair_primary = fair_baseline.get("sampling_design_weighted", fair_baseline)
        summary["fair_baseline_accuracy"] = float(fair_primary["accuracy"])
        summary["fair_baseline_macro_f1"] = float(fair_primary["macro_f1"])
    no_k = result["models"].get(no_k_model_name)
    if isinstance(no_k, dict):
        no_k_primary = no_k.get("sampling_design_weighted", no_k)
        summary["no_k_ablation_accuracy"] = float(no_k_primary["accuracy"])
        summary["no_k_ablation_macro_f1"] = float(no_k_primary["macro_f1"])
    return summary


def public_test_summary(
    result: dict[str, Any],
    path: Path,
    *,
    candidate_model_name: str = CANDIDATE_MODEL_NAME,
    fair_model_name: str = FAIR_BASELINE_MODEL_NAME,
    no_k_model_name: str = NO_K_ABLATION_MODEL_NAME,
) -> dict[str, Any]:
    candidate = result["models"][candidate_model_name]
    reference = result["models"]["kr_finbert_sc"]
    raw_reference = result["models"]["kr_finbert_sc_raw_off_the_shelf"]
    baseline = result["models"]["hana_tfidf_logistic"]
    pre_k_fnspid = result["models"][PRE_K_FNSPID_MODEL_NAME]
    fair_baseline = result["models"][fair_model_name]
    no_k = result["models"][no_k_model_name]
    return {
        **result,
        "path": _display_path(path, PROJECT_ROOT),
        "sha256": file_sha256(path),
        "sample_count": int(result["sample_count"]),
        "accuracy": float(candidate["accuracy"]),
        "macro_f1": float(candidate["macro_f1"]),
        "baseline_accuracy": float(baseline["accuracy"]),
        "baseline_macro_f1": float(baseline["macro_f1"]),
        "kr_finbert_sc_accuracy": float(reference["accuracy"]),
        "kr_finbert_sc_macro_f1": float(reference["macro_f1"]),
        "kr_finbert_sc_raw_accuracy": float(raw_reference["accuracy"]),
        "kr_finbert_sc_raw_macro_f1": float(raw_reference["macro_f1"]),
        "pre_k_fnspid_accuracy": float(pre_k_fnspid["accuracy"]),
        "pre_k_fnspid_macro_f1": float(pre_k_fnspid["macro_f1"]),
        "fair_baseline_accuracy": float(fair_baseline["accuracy"]),
        "fair_baseline_macro_f1": float(fair_baseline["macro_f1"]),
        "no_k_ablation_accuracy": float(no_k["accuracy"]),
        "no_k_ablation_macro_f1": float(no_k["macro_f1"]),
    }


def build_confirmatory_inference(
    news: dict[str, Any],
    disclosure: dict[str, Any],
    *,
    statistical_analysis_plan: dict[str, Any] | None = None,
    fair_model_name: str = FAIR_BASELINE_MODEL_NAME,
    no_k_model_name: str = NO_K_ABLATION_MODEL_NAME,
) -> dict[str, Any]:
    plan = statistical_analysis_plan or canonical_statistical_analysis_plan()
    hypotheses = plan["holm_hypotheses"]
    if not isinstance(hypotheses, list) or len(hypotheses) != 8:
        raise ValueError("canonical Holm 가설군은 정확히 8개여야 합니다.")
    paired_design = plan.get("paired_design_inference")
    practical_rule = (
        paired_design.get("practical_superiority_rule")
        if isinstance(paired_design, dict)
        else None
    )
    practical_margin_value = (
        practical_rule.get("minimum_difference")
        if isinstance(practical_rule, dict)
        else None
    )
    if (
        isinstance(practical_margin_value, bool)
        or not isinstance(practical_margin_value, (int, float))
        or not 0.0 < float(practical_margin_value) < 1.0
    ):
        raise ValueError("확증 실질 우월성 margin이 사전 고정되지 않았습니다.")
    practical_margin = float(practical_margin_value)
    source_results = {"NEWS": news, "DISCLOSURE": disclosure}
    raw_tests: list[tuple[str, str, str, dict[str, Any], float]] = []
    for hypothesis in hypotheses:
        if not isinstance(hypothesis, dict):
            raise ValueError("canonical Holm 가설이 JSON 객체가 아닙니다.")
        hypothesis_id = str(hypothesis["hypothesis_id"])
        source = str(hypothesis["source_type"])
        baseline = str(hypothesis["baseline_model"])
        result = source_results[source]
        comparisons = result.get("statistical_comparisons")
        if not isinstance(comparisons, dict):
            raise ValueError(f"{source} 확증 통계 비교가 없습니다.")
        comparison = comparisons.get(f"candidate_vs_{baseline}")
        jackknife = (
            comparison.get("paired_sampling_design_delete_1_jackknife_95_ci")
            if isinstance(comparison, dict)
            else None
        )
        macro_f1 = jackknife.get("macro_f1_difference") if isinstance(jackknife, dict) else None
        if not isinstance(comparison, dict) or not isinstance(macro_f1, dict):
            raise ValueError(f"{source}/{baseline} 확증 설계기반 jackknife가 없습니다.")
        if (
            comparison.get("included_in_holm_family") is not True
            or comparison.get("diagnostic_only") is not False
            or comparison.get("claim_allowed") is not True
            or comparison.get("confirmatory_significance_claim_allowed") is not True
        ):
            raise ValueError(f"{source}/{baseline} Holm claim 계약이 닫혀 있습니다.")
        p_value = float(macro_f1.get("two_sided_normal_p_value", -1.0))
        if not 0.0 <= p_value <= 1.0:
            raise ValueError(f"{source}/{baseline} p-value가 올바르지 않습니다.")
        raw_tests.append((hypothesis_id, source, baseline, comparison, p_value))
    adjusted = holm_adjusted_p_values([row[4] for row in raw_tests])
    results: dict[str, dict[str, Any]] = {"NEWS": {}, "DISCLOSURE": {}}
    for (hypothesis_id, source, baseline, comparison, p_value), adjusted_p in zip(
        raw_tests, adjusted, strict=True
    ):
        confidence_interval = comparison["paired_sampling_design_delete_1_jackknife_95_ci"][
            "macro_f1_difference"
        ]
        observed = comparison["observed_sampling_design_weighted_difference"]["macro_f1"]
        superior = (
            float(observed) > 0.0
            and float(confidence_interval["low"]) > 0.0
            and adjusted_p < FAMILYWISE_ALPHA
        )
        practically_superior = (
            superior
            and float(observed) >= practical_margin
            and float(confidence_interval["low"]) >= practical_margin
        )
        results[source][baseline] = {
            "hypothesis_id": hypothesis_id,
            "observed_weighted_macro_f1_difference": float(observed),
            "paired_sampling_design_jackknife_95_ci": confidence_interval,
            "sampling_design_jackknife_normal_p_value": p_value,
            "holm_adjusted_p_value": adjusted_p,
            "statistically_superior": superior,
            "practical_superiority_margin": practical_margin,
            "practically_superior": practically_superior,
        }
    raw_reference_superior = all(
        bool(results[source][baseline]["statistically_superior"])
        for source in ("NEWS", "DISCLOSURE")
        for baseline in ("kr_finbert_sc_raw_off_the_shelf",)
    )
    pre_k_superior = all(
        bool(results[source][PRE_K_FNSPID_MODEL_NAME]["statistically_superior"])
        for source in ("NEWS", "DISCLOSURE")
    )
    fair_baseline_superior = all(
        bool(results[source][fair_model_name]["statistically_superior"])
        for source in ("NEWS", "DISCLOSURE")
    )
    no_k_ablation_superior = all(
        bool(results[source][no_k_model_name]["statistically_superior"])
        for source in ("NEWS", "DISCLOSURE")
    )
    materially_superior_to_all_named_baselines = all(
        bool(results[source][baseline]["practically_superior"])
        for source in CONFIRMATORY_SOURCES
        for baseline in (
            "kr_finbert_sc_raw_off_the_shelf",
            PRE_K_FNSPID_MODEL_NAME,
            fair_model_name,
            no_k_model_name,
        )
    )
    return {
        "family": (
            "NEWS/DISCLOSURE x raw KR-FinBERT-SC/pre-K-FNSPID/"
            "same-data KR-FinBERT-SC/no-K ablation"
        ),
        "family_hypothesis_count": len(raw_tests),
        "family_hypothesis_ids": [row[0] for row in raw_tests],
        "multiple_comparison_correction": f"Holm family-wise alpha={FAMILYWISE_ALPHA}",
        "primary_metric": "sampling-design-weighted plug-in Macro-F1",
        "paired_inference": (
            "stratified SRSWOR delete-1 jackknife with finite-population correction; "
            "Holm-adjusted paired normal tests"
        ),
        "sources": results,
        "raw_kr_finbert_reference_superiority_claim_allowed": raw_reference_superior,
        "pre_k_fnspid_superiority_claim_allowed": pre_k_superior,
        "fair_baseline_superiority_claim_allowed": fair_baseline_superior,
        "no_k_ablation_superiority_claim_allowed": no_k_ablation_superior,
        "practical_superiority_margin_macro_f1": practical_margin,
        "large_or_material_superiority_claim_allowed": (
            materially_superior_to_all_named_baselines
        ),
        "qwen_confirmatory_exclusion": plan["excluded_confirmatory_models"][
            QWEN_TEACHER_MODEL_NAME
        ],
        "target_aware_kr_finbert_input_ablation": {
            "role": "candidate_input_format_diagnostic_non_claim",
            "reason": (
                "KR-FinBERT-SC가 학습하지 않은 source/target prefix와 head-tail 절단을 "
                "적용하므로 공정한 주 비교로 사용하지 않는다."
            ),
        },
        "global_sota_claim_allowed": plan["claim_scope"]["global_sota_claim_allowed"],
        "claim_scope": (
            "비교 대상과 고정된 신규 K-FNSPID 확률표본에 한정한다. 외부 한국 금융 "
            "벤치마크 전체에 대한 전역 SOTA를 뜻하지 않는다."
        ),
    }


def holm_adjusted_p_values(p_values: list[float]) -> list[float]:
    if not p_values or any(not 0.0 <= value <= 1.0 for value in p_values):
        raise ValueError("Holm 보정 p-value 입력이 올바르지 않습니다.")
    ordered = sorted(enumerate(p_values), key=lambda row: row[1])
    adjusted = [0.0] * len(p_values)
    running = 0.0
    count = len(p_values)
    for rank, (original_index, value) in enumerate(ordered):
        running = max(running, min(1.0, value * (count - rank)))
        adjusted[original_index] = running
    return adjusted


def build_deployment_gate(
    news: dict[str, Any],
    disclosure: dict[str, Any],
    public: dict[str, Any],
    *,
    candidate_version: str,
    artifact_manifest_sha256: str,
    confirmatory_inference: dict[str, Any],
    candidate_model: str = CANDIDATE_MODEL_NAME,
    candidate_model_family: str | None = None,
) -> dict[str, Any]:
    checks = {
        "news_sample_count": int(news["sample_count"]) >= MIN_SEALED_SAMPLE_COUNT,
        "news_accuracy": float(news["accuracy"]) >= MIN_SEALED_ACCURACY,
        "news_macro_f1": float(news["macro_f1"]) >= MIN_SEALED_MACRO_F1,
        "news_tfidf_accuracy_non_regression": (
            float(news["accuracy"]) >= float(news["baseline_accuracy"])
        ),
        "news_tfidf_macro_f1_non_regression": (
            float(news["macro_f1"]) >= float(news["baseline_macro_f1"])
        ),
        "news_kr_finbert_macro_f1_non_regression": (
            float(news["macro_f1"]) >= float(news["kr_finbert_sc_macro_f1"])
        ),
        "news_kr_finbert_accuracy_non_regression": (
            float(news["accuracy"]) >= float(news["kr_finbert_sc_accuracy"])
        ),
        "news_raw_kr_finbert_macro_f1_non_regression": (
            float(news["macro_f1"]) >= float(news["kr_finbert_sc_raw_macro_f1"])
        ),
        "news_raw_kr_finbert_accuracy_non_regression": (
            float(news["accuracy"]) >= float(news["kr_finbert_sc_raw_accuracy"])
        ),
        "news_pre_k_fnspid_macro_f1_improvement": (
            float(news["macro_f1"]) > float(news["pre_k_fnspid_macro_f1"])
        ),
        "news_fair_baseline_macro_f1_non_regression": (
            float(news["macro_f1"]) >= float(news["fair_baseline_macro_f1"])
        ),
        "news_fair_baseline_accuracy_non_regression": (
            float(news["accuracy"]) >= float(news["fair_baseline_accuracy"])
        ),
        "news_no_k_ablation_macro_f1_non_regression": (
            float(news["macro_f1"]) >= float(news["no_k_ablation_macro_f1"])
        ),
        "news_no_k_ablation_accuracy_non_regression": (
            float(news["accuracy"]) >= float(news["no_k_ablation_accuracy"])
        ),
        "disclosure_sample_count": (int(disclosure["sample_count"]) >= MIN_SEALED_SAMPLE_COUNT),
        "disclosure_accuracy": float(disclosure["accuracy"]) >= MIN_SEALED_ACCURACY,
        "disclosure_macro_f1": (float(disclosure["macro_f1"]) >= MIN_SEALED_MACRO_F1),
        "disclosure_tfidf_accuracy_non_regression": (
            float(disclosure["accuracy"]) >= float(disclosure["baseline_accuracy"])
        ),
        "disclosure_tfidf_macro_f1_non_regression": (
            float(disclosure["macro_f1"]) >= float(disclosure["baseline_macro_f1"])
        ),
        "disclosure_kr_finbert_macro_f1_non_regression": (
            float(disclosure["macro_f1"]) >= float(disclosure["kr_finbert_sc_macro_f1"])
        ),
        "disclosure_kr_finbert_accuracy_non_regression": (
            float(disclosure["accuracy"]) >= float(disclosure["kr_finbert_sc_accuracy"])
        ),
        "disclosure_raw_kr_finbert_macro_f1_non_regression": (
            float(disclosure["macro_f1"]) >= float(disclosure["kr_finbert_sc_raw_macro_f1"])
        ),
        "disclosure_raw_kr_finbert_accuracy_non_regression": (
            float(disclosure["accuracy"]) >= float(disclosure["kr_finbert_sc_raw_accuracy"])
        ),
        "disclosure_pre_k_fnspid_macro_f1_improvement": (
            float(disclosure["macro_f1"]) > float(disclosure["pre_k_fnspid_macro_f1"])
        ),
        "disclosure_fair_baseline_macro_f1_non_regression": (
            float(disclosure["macro_f1"]) >= float(disclosure["fair_baseline_macro_f1"])
        ),
        "disclosure_fair_baseline_accuracy_non_regression": (
            float(disclosure["accuracy"]) >= float(disclosure["fair_baseline_accuracy"])
        ),
        "disclosure_no_k_ablation_macro_f1_non_regression": (
            float(disclosure["macro_f1"])
            >= float(disclosure["no_k_ablation_macro_f1"])
        ),
        "disclosure_no_k_ablation_accuracy_non_regression": (
            float(disclosure["accuracy"]) >= float(disclosure["no_k_ablation_accuracy"])
        ),
        "news_and_disclosure_statistically_superior_to_raw_kr_finbert_reference": bool(
            confirmatory_inference.get("raw_kr_finbert_reference_superiority_claim_allowed", False)
        ),
        "news_and_disclosure_statistically_superior_to_pre_k_fnspid": bool(
            confirmatory_inference.get("pre_k_fnspid_superiority_claim_allowed", False)
        ),
        "news_and_disclosure_statistically_superior_to_fair_baseline": bool(
            confirmatory_inference.get("fair_baseline_superiority_claim_allowed", False)
        ),
        "news_and_disclosure_statistically_superior_to_no_k_ablation": bool(
            confirmatory_inference.get("no_k_ablation_superiority_claim_allowed", False)
        ),
    }
    eligible = all(checks.values())
    secondary_regression_diagnostics = {
        "role": "repeatedly_exposed_secondary_regression_set_non_gating",
        "public_macro_f1_threshold_met": float(public["macro_f1"]) >= MIN_PUBLIC_MACRO_F1,
        "public_kr_finbert_macro_f1_non_regression": (
            float(public["macro_f1"]) >= float(public["kr_finbert_sc_macro_f1"])
        ),
        "public_pre_k_fnspid_macro_f1_non_regression": (
            float(public["macro_f1"]) >= float(public["pre_k_fnspid_macro_f1"])
        ),
        "public_fair_baseline_macro_f1_non_regression": (
            float(public["macro_f1"]) >= float(public["fair_baseline_macro_f1"])
        ),
        "public_no_k_ablation_macro_f1_non_regression": (
            float(public["macro_f1"]) >= float(public["no_k_ablation_macro_f1"])
        ),
        "qwen_blind_teacher_role": "diagnostic_only_not_in_holm_or_gate",
        "affects_deployment_decision": False,
    }
    gate = {
        "candidate_model": candidate_model,
        "candidate_version": candidate_version,
        "candidate_artifact_manifest_sha256": artifact_manifest_sha256,
        "thresholds": {
            "minimum_sealed_sample_count_per_source": MIN_SEALED_SAMPLE_COUNT,
            "minimum_sealed_accuracy_per_source": MIN_SEALED_ACCURACY,
            "minimum_sealed_macro_f1_per_source": MIN_SEALED_MACRO_F1,
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
                "positive weighted Macro-F1 difference, positive paired SRSWOR "
                "FPC delete-1 jackknife lower bound, and Holm-adjusted jackknife-normal "
                "p<0.05 for NEWS and DISCLOSURE"
            ),
        },
        "checks": checks,
        "secondary_regression_diagnostics": secondary_regression_diagnostics,
        "eligible": eligible,
        "decision": "DEPLOY_HANA_MONTANA_AI" if eligible else "KEEP_CURRENT_MODEL",
    }
    if candidate_model_family is not None:
        gate["candidate_model_family"] = candidate_model_family
    return gate


def percentile_interval(values: list[float]) -> dict[str, float]:
    if not values:
        raise ValueError("신뢰구간 표본이 없습니다.")
    ordered = sorted(values)
    low_index = max(0, math.floor((len(ordered) - 1) * 0.025))
    high_index = min(len(ordered) - 1, math.ceil((len(ordered) - 1) * 0.975))
    return {
        "mean": sum(ordered) / len(ordered),
        "low": ordered[low_index],
        "high": ordered[high_index],
    }


def exact_mcnemar_p_value(baseline_only: int, candidate_only: int) -> float:
    if baseline_only < 0 or candidate_only < 0:
        raise ValueError("McNemar 빈도는 음수일 수 없습니다.")
    discordant = baseline_only + candidate_only
    if discordant == 0:
        return 1.0
    tail = sum(
        math.comb(discordant, value) for value in range(min(baseline_only, candidate_only) + 1)
    ) / (2**discordant)
    return float(min(1.0, 2.0 * tail))


def canonical_json_sha256(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def file_sha256(path: Path) -> str:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"hash 대상 파일이 없거나 symlink입니다: {path}")
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _verify_file_manifest(directory: Path, manifest: dict[str, Any]) -> None:
    resolved_directory = directory.resolve()
    if not resolved_directory.is_dir() or directory.is_symlink():
        raise ValueError(f"artifact 디렉터리가 없거나 symlink입니다: {directory}")
    for filename, expected in manifest.items():
        if (
            not isinstance(filename, str)
            or Path(filename).name != filename
            or not isinstance(expected, dict)
        ):
            raise ValueError("artifact manifest 경로가 안전하지 않습니다.")
        path = resolved_directory / filename
        if path.is_symlink() or not path.is_file() or path.resolve().parent != resolved_directory:
            raise ValueError(f"artifact 파일이 없거나 안전하지 않습니다: {filename}")
        expected_hash = _sha256_value(expected.get("sha256"), filename)
        expected_bytes = expected.get("bytes")
        if (
            not isinstance(expected_bytes, int)
            or isinstance(expected_bytes, bool)
            or path.stat().st_size != expected_bytes
            or file_sha256(path) != expected_hash
        ):
            raise ValueError(f"artifact 무결성 검증에 실패했습니다: {filename}")


def _require_project_directory(path: Path, root: Path, name: str) -> Path:
    resolved_root = root.resolve()
    resolved = path.resolve()
    if path.is_symlink() or not resolved.is_relative_to(resolved_root) or not resolved.is_dir():
        raise ValueError(f"{name} 경로가 없거나 안전하지 않습니다.")
    return resolved


def _require_project_file(path: Path, root: Path, name: str) -> Path:
    resolved_root = root.resolve()
    resolved = path.resolve()
    if path.is_symlink() or not resolved.is_relative_to(resolved_root) or not resolved.is_file():
        raise ValueError(f"{name} 파일이 없거나 안전하지 않습니다.")
    return resolved


def _validate_regular_file_commitment(path: Path, raw: Any, name: str) -> None:
    if not isinstance(raw, dict):
        raise ValueError(f"{name} 파일 commitment가 없습니다.")
    committed_path = raw.get("path")
    if committed_path is not None and not isinstance(committed_path, str):
        raise ValueError(f"{name} commitment 경로가 올바르지 않습니다.")
    expected_bytes = raw.get("bytes")
    expected_sha256 = _sha256_value(raw.get("sha256"), name)
    if (
        path.is_symlink()
        or not path.is_file()
        or isinstance(expected_bytes, bool)
        or not isinstance(expected_bytes, int)
        or path.stat().st_size != expected_bytes
        or file_sha256(path) != expected_sha256
    ):
        raise ValueError(f"{name} 파일 commitment가 일치하지 않습니다.")


def _provenance_identity(raw: dict[str, Any], name: str) -> dict[str, int | str]:
    path = raw.get("path")
    size = raw.get("bytes")
    digest = _sha256_value(raw.get("sha256"), name)
    if (
        not isinstance(path, str)
        or not path
        or isinstance(size, bool)
        or not isinstance(size, int)
        or size < 0
    ):
        raise ValueError(f"{name} provenance가 올바르지 않습니다.")
    return {"path": path, "bytes": size, "sha256": digest}


def _strict_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} 값이 정수가 아닙니다.")
    return value


def _strict_float(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError(f"{name} 값이 수치가 아닙니다.")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} 값이 유한하지 않습니다.")
    return result


def _strict_probability(value: Any, name: str) -> float:
    result = _strict_float(value, name)
    if not 0.0 <= result <= 1.0:
        raise ValueError(f"{name} 값이 [0, 1] 범위가 아닙니다.")
    return result


def _safe_project_path(root: Path, value: Any, name: str) -> Path:
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise ValueError(f"{name} 상대경로가 올바르지 않습니다.")
    resolved_root = root.resolve()
    unresolved = resolved_root / value
    resolved = unresolved.resolve()
    if (
        unresolved.is_symlink()
        or not resolved.is_relative_to(resolved_root)
        or not resolved.exists()
    ):
        raise ValueError(f"{name} 경로가 안전하지 않습니다.")
    return resolved


def _load_json_object(path: Path, name: str) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"{name} 파일이 없거나 symlink입니다: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{name}은 JSON 객체여야 합니다.")
    return payload


def _load_jsonl(
    path: Path,
    *,
    expected_sha256: str | None = None,
) -> list[dict[str, Any]]:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"JSONL 파일이 없거나 symlink입니다: {path}")
    raw = path.read_bytes()
    if expected_sha256 is not None and sha256(raw).hexdigest() != expected_sha256:
        raise ValueError(f"JSONL hash가 receipt commitment와 다릅니다: {path}")
    rows: list[dict[str, Any]] = []
    try:
        lines = raw.decode("utf-8").splitlines()
    except UnicodeDecodeError as exception:
        raise ValueError(f"JSONL은 UTF-8이어야 합니다: {path}") from exception
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise ValueError(f"JSONL {line_number}행은 객체여야 합니다: {path}")
        rows.append(payload)
    return rows


def _parse_aware_datetime(value: str, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exception:
        raise ValueError(f"{field}가 ISO-8601 형식이 아닙니다.") from exception
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field}에는 시간대가 필요합니다.")
    return parsed.astimezone(UTC)


def _sha256_value(value: Any, name: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{name} SHA-256이 올바르지 않습니다.")
    return value


def _display_path(path: Path, root: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(root.resolve()))
    except ValueError:
        return str(resolved)


def _text_sha256(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def _cluster_indices(clusters: list[str]) -> dict[str, list[int]]:
    grouped: dict[str, list[int]] = {}
    for index, cluster in enumerate(clusters):
        if not cluster:
            raise ValueError("event cluster가 없습니다.")
        grouped.setdefault(cluster, []).append(index)
    if not grouped:
        raise ValueError("event cluster가 비어 있습니다.")
    return grouped


def _stratified_cluster_groups(
    clusters: list[str], strata: list[str]
) -> dict[str, list[list[int]]]:
    if len(clusters) != len(strata) or not clusters:
        raise ValueError("cluster와 sampling stratum 길이가 다릅니다.")
    owner: dict[str, str] = {}
    grouped: dict[str, dict[str, list[int]]] = {label: {} for label in LABEL_ORDER}
    for index, (cluster, stratum) in enumerate(zip(clusters, strata, strict=True)):
        if not cluster or stratum not in LABEL_ORDER:
            raise ValueError("cluster 또는 sampling stratum이 올바르지 않습니다.")
        previous = owner.setdefault(cluster, stratum)
        if previous != stratum:
            raise ValueError("동일 event cluster가 서로 다른 sampling stratum에 속합니다.")
        grouped[stratum].setdefault(cluster, []).append(index)
    if any(not grouped[label] for label in LABEL_ORDER):
        raise ValueError("모든 sampling stratum에 event cluster가 있어야 합니다.")
    return {
        label: [grouped[label][cluster] for cluster in sorted(grouped[label])]
        for label in LABEL_ORDER
    }


def _fast_metrics(expected: list[str], predicted: list[str]) -> dict[str, float]:
    _validate_prediction_vectors(expected, predicted)
    indices = {label: index for index, label in enumerate(LABEL_ORDER)}
    matrix = [[0] * len(LABEL_ORDER) for _ in LABEL_ORDER]
    for truth, guess in zip(expected, predicted, strict=True):
        matrix[indices[truth]][indices[guess]] += 1
    row_totals = [sum(row) for row in matrix]
    column_totals = [
        sum(matrix[row][column] for row in range(len(LABEL_ORDER)))
        for column in range(len(LABEL_ORDER))
    ]
    class_f1 = [
        2.0 * matrix[index][index] / (row_totals[index] + column_totals[index])
        if row_totals[index] + column_totals[index]
        else 0.0
        for index in range(len(LABEL_ORDER))
    ]
    return {
        "accuracy": sum(matrix[index][index] for index in range(len(LABEL_ORDER))) / len(expected),
        "macro_f1": sum(class_f1) / len(LABEL_ORDER),
    }


def _fast_weighted_metrics(
    expected: list[str], predicted: list[str], weights: list[float]
) -> dict[str, float]:
    _validate_prediction_vectors(expected, predicted)
    _validate_weights(expected, weights)
    indices = {label: index for index, label in enumerate(LABEL_ORDER)}
    matrix = [[0.0] * len(LABEL_ORDER) for _ in LABEL_ORDER]
    for truth, guess, weight in zip(expected, predicted, weights, strict=True):
        matrix[indices[truth]][indices[guess]] += weight
    row_totals = [sum(row) for row in matrix]
    column_totals = [
        sum(matrix[row][column] for row in range(len(LABEL_ORDER)))
        for column in range(len(LABEL_ORDER))
    ]
    class_f1 = [
        2.0 * matrix[index][index] / (row_totals[index] + column_totals[index])
        if row_totals[index] + column_totals[index]
        else 0.0
        for index in range(len(LABEL_ORDER))
    ]
    return {
        "accuracy": sum(matrix[index][index] for index in range(len(LABEL_ORDER))) / sum(weights),
        "macro_f1": sum(class_f1) / len(LABEL_ORDER),
    }


def _validate_prediction_vectors(expected: list[str], predicted: list[str]) -> None:
    if not expected or len(expected) != len(predicted):
        raise ValueError("정답과 예측 길이가 일치하지 않거나 비어 있습니다.")
    if any(label not in LABEL_ORDER for label in [*expected, *predicted]):
        raise ValueError("지원하지 않는 감성 등급이 있습니다.")


def _validate_weights(expected: list[str], weights: list[float]) -> None:
    if len(expected) != len(weights) or any(
        not math.isfinite(weight) or weight <= 0.0 for weight in weights
    ):
        raise ValueError("설계가중치는 예측과 길이가 같고 양의 유한수여야 합니다.")


def _validate_sampling_vectors(
    expected: list[str], weights: list[float], strata: list[str]
) -> None:
    _validate_weights(expected, weights)
    if len(expected) != len(strata) or any(label not in LABEL_ORDER for label in strata):
        raise ValueError("sampling stratum 벡터가 올바르지 않습니다.")


def _validate_population_counts(
    weights: list[float],
    strata: list[str],
    population_counts: dict[str, int],
) -> None:
    if set(population_counts) != set(LABEL_ORDER):
        raise ValueError("모집단 층 크기는 세 감성 층을 정확히 포함해야 합니다.")
    sample_counts = Counter(strata)
    for label in LABEL_ORDER:
        population_count = population_counts[label]
        sample_count = sample_counts[label]
        if (
            not isinstance(population_count, int)
            or isinstance(population_count, bool)
            or sample_count < 2
            or population_count < sample_count
        ):
            raise ValueError(f"{label} 층의 N_h/n_h가 올바르지 않습니다.")
        expected_weight = population_count / sample_count
        observed_weights = [
            weight for weight, stratum in zip(weights, strata, strict=True) if stratum == label
        ]
        if any(
            not math.isclose(weight, expected_weight, rel_tol=1e-12, abs_tol=1e-12)
            for weight in observed_weights
        ):
            raise ValueError(f"{label} 층의 설계가중치가 N_h/n_h와 다릅니다.")


def _validate_unique_sampling_units(clusters: list[str], strata: list[str]) -> None:
    if len(clusters) != len(strata) or any(not cluster for cluster in clusters):
        raise ValueError("확률표본 event cluster 벡터가 올바르지 않습니다.")
    if len(set(clusters)) != len(clusters):
        raise ValueError("delete-1 설계분산에는 고유한 event cluster 표본단위가 필요합니다.")


def _partition_predictions(
    partitions: dict[str, list[dict[str, Any]]], predictions: list[str]
) -> dict[str, list[str]]:
    expected_count = sum(len(rows) for rows in partitions.values())
    if len(predictions) != expected_count:
        raise ValueError("파티션과 예측 수가 일치하지 않습니다.")
    result: dict[str, list[str]] = {}
    offset = 0
    for name, rows in partitions.items():
        result[name] = predictions[offset : offset + len(rows)]
        offset += len(rows)
    return result


def _torch_device(torch: Any) -> Any:
    # 확증 평가의 수치 재현 경계는 SAP에 고정된 CPU backend다.
    return torch.device("cpu")


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    _write_json_exclusive(path, payload)


def _write_json_exclusive(path: Path, payload: dict[str, Any]) -> None:
    if path.exists() or path.is_symlink():
        raise ValueError(f"JSON 출력이 이미 존재하거나 symlink입니다: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as file:
            file.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
            file.flush()
            os.fsync(file.fileno())
        os.chmod(temporary, 0o600)
        try:
            os.link(temporary, path, follow_symlinks=False)
        except FileExistsError as exception:
            raise ValueError(f"JSON 출력이 이미 존재하거나 symlink입니다: {path}") from exception
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
