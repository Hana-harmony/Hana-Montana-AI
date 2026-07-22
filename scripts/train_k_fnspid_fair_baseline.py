from __future__ import annotations

import argparse
import importlib.metadata
import json
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    EarlyStoppingCallback,
    TrainingArguments,
)

from hannah_montana_ai.services.model_artifact_integrity import build_artifact_manifest
from hannah_montana_ai.training.sentiment_gold_provenance import (
    add_gold_provenance_arguments,
    gold_provenance_paths,
    validate_all_gold_provenance,
)
from hannah_montana_ai.training.sentiment_protocol import (
    assert_sentiment_groups_disjoint,
    decontaminate_public_partitions,
    purge_sentiment_group_overlap,
    stratified_hash_three_way_split,
)

from train_kf_deberta_sentiment_v2 import (  # isort: skip
    DATASET_REVISION,
    DATA_SELECTION_SEED,
    DEFAULT_DATASET,
    DEFAULT_DEVELOPMENT_GOLD,
    DEFAULT_DISCLOSURE_AUXILIARY_GOLD,
    DEFAULT_DISCLOSURE_AUXILIARY_REPORT,
    DEFAULT_DISCLOSURE_DEVELOPMENT_GOLD,
    DEFAULT_DISCLOSURE_SILVER,
    DEFAULT_SILVER,
    DEFAULT_TRAIN_GOLD,
    DEFAULT_NEWS_AUXILIARY_GOLD,
    DEFAULT_NEWS_AUXILIARY_REPORT,
    LABEL_ORDER,
    LEGACY_EVALUATION_PATHS,
    R_DROP_ALPHA,
    MIN_DEVELOPMENT_LABEL_COUNT,
    PUBLIC_DATASET_REVISION,
    TARGET_SWAP_WEIGHT,
    EncodedSentimentDataset,
    HierarchicalSentimentTrainer,
    WeightedSentimentCollator,
    _deduplicate_weighted,
    _effective_number_weights,
    _evaluate_breakdown,
    _evaluate_partition,
    _fit_logit_bias_by_domain,
    _input_artifact_record,
    _label_distribution,
    _load_legacy_protected_rows,
    _load_auxiliary_training_rows,
    _load_public_rows,
    _load_reviewed_rows,
    _load_sealed_reservation_rows,
    _load_silver_rows,
    _metrics,
    _parameter_counts,
    _prepared_partition_commitments as _build_prepared_partition_commitments,
    _prediction_logits,
    _require_regular_input,
    _selection_score,
    _set_seed,
    _stratified_limit,
    _trainer_runtime_record,
    _training_weight_audit,
    build_target_swap_hard_negatives,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_MODEL = "snunlp/KR-FinBert-SC"
# 공식 저장소의 safetensors 변환 commit을 고정해 pickle 가중치 로딩을 막는다.
BASE_MODEL_REVISION = "36b3d36898bc9925ca58c3508b1048e4449f1370"
BASE_MODEL_UPSTREAM_MAIN_REVISION = "f8586286cc3161fb648e9fee09a456069fd846d0"
FAIR_SEEDS = (17, 42, 73)
MAX_LENGTH = 256
EPOCHS = 1.5
BATCH_SIZE = 8
GRADIENT_ACCUMULATION_STEPS = 2
EARLY_STOPPING_PATIENCE = 1
LEARNING_RATE = 2e-5
SILVER_PER_LABEL = 6_000
DISCLOSURE_PER_LABEL = 900
TARGET_SWAP_PER_SOURCE = 1_500
DEFAULT_NEWS_CONFIRMATORY_RESERVATION = (
    PROJECT_ROOT / "data/gold/confirmatory_sealed_test_review.jsonl"
)
DEFAULT_DISCLOSURE_CONFIRMATORY_RESERVATION = (
    PROJECT_ROOT / "data/gold/disclosure_confirmatory_sealed_test_review.jsonl"
)
DEFAULT_CONFIRMATORY_SAMPLING_DESIGN = (
    PROJECT_ROOT / "reports/k-fnspid-sentiment-confirmatory-sealed-sampling-design-v2.json"
)
NEWS_CONFIRMATORY_PARTITION = "CONFIRMATORY_SEALED_TEST_REVIEW"
DISCLOSURE_CONFIRMATORY_PARTITION = "DISCLOSURE_CONFIRMATORY_SEALED_TEST_REVIEW"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "artifacts/sentiment/fair_baselines/kr-finbert-sc"
DEFAULT_REPORT_ROOT = PROJECT_ROOT / "reports/fair_baselines/kr-finbert-sc"
REQUIRED_SELECTION_DATASETS = (
    "PUBLIC_SELECTION",
    "K_FNSPID_DEVELOPMENT_SELECTION",
    "K_FNSPID_DISCLOSURE_DEVELOPMENT_SELECTION",
)


@dataclass(frozen=True, slots=True)
class PreparedTrainingData:
    train_rows: list[dict[str, Any]]
    checkpoint_rows: list[dict[str, Any]]
    calibration_rows: list[dict[str, Any]]
    selection_rows: list[dict[str, Any]]
    news_confirmatory_reservation: list[dict[str, Any]]
    disclosure_confirmatory_reservation: list[dict[str, Any]]
    input_paths: dict[str, Path]
    gold_provenance: dict[str, dict[str, Any]]
    public_audit: dict[str, Any]
    silver_audit: dict[str, Any]
    disclosure_silver_audit: dict[str, Any]
    final_overlap_audit: dict[str, Any]


def main(argv: Sequence[str] | None = None) -> None:
    args = _parser().parse_args(argv)
    _validate_arguments(args)
    _preflight_output_roots(args.output_root, args.report_root)

    prepared = prepare_training_data(args)
    prepared_by_seed = {seed: prepared for seed in FAIR_SEEDS}
    if args.validate_only:
        print(
            json.dumps(
                _validation_plan(args, prepared_by_seed),
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return

    args.output_root.mkdir(parents=True, exist_ok=False)
    args.report_root.mkdir(parents=True, exist_ok=False)
    reports = [train_seed(args, seed, prepared_by_seed[seed]) for seed in FAIR_SEEDS]
    summary = _selection_summary(args, reports)
    summary_path = args.report_root / "selection.json"
    _write_new_json(summary_path, summary)
    print(json.dumps(summary, ensure_ascii=False))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "동일 K-FNSPID 데이터·분할·선택 예산으로 KR-FinBERT-SC 전체 fine-tune "
            "기준선을 학습한다."
        )
    )
    parser.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--silver-path", type=Path, default=DEFAULT_SILVER)
    parser.add_argument("--disclosure-silver-path", type=Path, default=DEFAULT_DISCLOSURE_SILVER)
    parser.add_argument("--train-gold-path", type=Path, default=DEFAULT_TRAIN_GOLD)
    parser.add_argument(
        "--news-auxiliary-gold-path", type=Path, default=DEFAULT_NEWS_AUXILIARY_GOLD
    )
    parser.add_argument(
        "--disclosure-auxiliary-gold-path",
        type=Path,
        default=DEFAULT_DISCLOSURE_AUXILIARY_GOLD,
    )
    parser.add_argument(
        "--news-auxiliary-report-path",
        type=Path,
        default=DEFAULT_NEWS_AUXILIARY_REPORT,
    )
    parser.add_argument(
        "--disclosure-auxiliary-report-path",
        type=Path,
        default=DEFAULT_DISCLOSURE_AUXILIARY_REPORT,
    )
    parser.add_argument("--development-gold-path", type=Path, default=DEFAULT_DEVELOPMENT_GOLD)
    parser.add_argument(
        "--disclosure-development-gold-path",
        type=Path,
        default=DEFAULT_DISCLOSURE_DEVELOPMENT_GOLD,
    )
    parser.add_argument(
        "--news-confirmatory-reservation",
        type=Path,
        default=DEFAULT_NEWS_CONFIRMATORY_RESERVATION,
    )
    parser.add_argument(
        "--disclosure-confirmatory-reservation",
        type=Path,
        default=DEFAULT_DISCLOSURE_CONFIRMATORY_RESERVATION,
    )
    parser.add_argument(
        "--confirmatory-sampling-design",
        type=Path,
        default=DEFAULT_CONFIRMATORY_SAMPLING_DESIGN,
    )
    add_gold_provenance_arguments(parser)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--report-root", type=Path, default=DEFAULT_REPORT_ROOT)
    parser.add_argument("--gradient-checkpointing", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument(
        "--max-train-rows",
        type=int,
        help="validate-only smoke에서만 쓰는 층화 행 제한",
    )
    return parser


def _validate_arguments(args: argparse.Namespace) -> None:
    if args.max_train_rows is not None and args.max_train_rows < len(LABEL_ORDER):
        raise SystemExit("max-train-rows는 라벨 수 이상이어야 합니다.")
    if args.max_train_rows is not None and not args.validate_only:
        raise SystemExit("공정 기준선 실제 학습에서는 max-train-rows를 허용하지 않습니다.")
    if args.output_root.resolve() == args.report_root.resolve():
        raise SystemExit("artifact와 report 출력 경로는 분리해야 합니다.")


def _preflight_output_roots(output_root: Path, report_root: Path) -> None:
    for label, path in (("artifact", output_root), ("report", report_root)):
        if path.exists() or path.is_symlink():
            raise SystemExit(f"{label} 출력은 write-once이며 이미 존재합니다: {path}")


def prepare_training_data(
    args: argparse.Namespace,
) -> PreparedTrainingData:
    input_paths = _training_input_paths(args)
    for name, path in input_paths.items():
        _require_regular_input(path, name)
    gold_provenance = validate_all_gold_provenance(args)

    # 공개 Test는 경로나 라벨을 열지 않고 새 confirmatory reservation만 보호한다.
    public, public_audit = decontaminate_public_partitions(
        {
            "TRAIN": _load_public_rows(input_paths["public_train"]),
            "VALIDATION": _load_public_rows(input_paths["public_validation"]),
            "TEST": [],
        }
    )
    public_development = stratified_hash_three_way_split(
        public["VALIDATION"],
        checkpoint_name="CHECKPOINT",
        calibration_name="CALIBRATION",
        selection_name="SELECTION",
        minimum_per_label=MIN_DEVELOPMENT_LABEL_COUNT,
    )
    train_gold = _load_reviewed_rows(
        args.train_gold_path,
        "TRAIN_REVIEW",
        weight=1.5,
    )
    news_auxiliary_gold = _load_auxiliary_training_rows(
        args.news_auxiliary_gold_path,
        args.news_auxiliary_report_path,
        "NEWS",
        weight=1.5,
    )
    disclosure_auxiliary_gold = _load_auxiliary_training_rows(
        args.disclosure_auxiliary_gold_path,
        args.disclosure_auxiliary_report_path,
        "DISCLOSURE",
        weight=1.5,
    )
    news_development = _load_reviewed_rows(
        args.development_gold_path,
        "DEVELOPMENT_REVIEW",
        weight=1.0,
    )
    news_development_split = stratified_hash_three_way_split(
        news_development,
        checkpoint_name="CHECKPOINT",
        calibration_name="CALIBRATION",
        selection_name="SELECTION",
        minimum_per_label=MIN_DEVELOPMENT_LABEL_COUNT,
    )
    disclosure_development = _load_reviewed_rows(
        args.disclosure_development_gold_path,
        "DISCLOSURE_DEVELOPMENT_REVIEW",
        weight=1.0,
    )
    disclosure_development_split = stratified_hash_three_way_split(
        disclosure_development,
        checkpoint_name="CHECKPOINT",
        calibration_name="CALIBRATION",
        selection_name="SELECTION",
        minimum_per_label=MIN_DEVELOPMENT_LABEL_COUNT,
    )
    news_confirmatory = _load_sealed_reservation_rows(
        args.news_confirmatory_reservation,
        NEWS_CONFIRMATORY_PARTITION,
        "NEWS",
    )
    disclosure_confirmatory = _load_sealed_reservation_rows(
        args.disclosure_confirmatory_reservation,
        DISCLOSURE_CONFIRMATORY_PARTITION,
        "DISCLOSURE",
    )
    protected = [
        *public_development["CHECKPOINT"],
        *public_development["CALIBRATION"],
        *public_development["SELECTION"],
        *news_development,
        *disclosure_development,
        *news_confirmatory,
        *disclosure_confirmatory,
        *_load_legacy_protected_rows(),
    ]
    silver, silver_audit = _load_silver_rows(
        args.silver_path,
        protected,
        SILVER_PER_LABEL,
        DATA_SELECTION_SEED,
    )
    disclosure_silver, disclosure_silver_audit = _load_silver_rows(
        args.disclosure_silver_path,
        protected,
        DISCLOSURE_PER_LABEL,
        DATA_SELECTION_SEED + 11,
    )
    public_train = [
        {
            **row,
            "source_type": "NEWS",
            "sample_weight": 1.0,
            "dataset": "PUBLIC_TRAIN",
        }
        for row in public["TRAIN"]
    ]
    train_rows = _deduplicate_weighted(
        [
            *public_train,
            *[{**row, "dataset": "K_FNSPID_CODEX_GOLD"} for row in train_gold],
            *[
                {**row, "dataset": "K_FNSPID_NEWS_AUXILIARY_CODEX_GOLD"}
                for row in news_auxiliary_gold
            ],
            *[
                {**row, "dataset": "K_FNSPID_DISCLOSURE_AUXILIARY_CODEX_GOLD"}
                for row in disclosure_auxiliary_gold
            ],
            *[{**row, "dataset": "K_FNSPID_RULE_SILVER"} for row in silver],
            *[{**row, "dataset": "K_FNSPID_DISCLOSURE_RULE_SILVER"} for row in disclosure_silver],
        ]
    )
    train_rows, final_overlap_audit = purge_sentiment_group_overlap(
        train_rows,
        protected,
    )
    if args.max_train_rows is not None:
        train_rows = _stratified_limit(train_rows, args.max_train_rows, DATA_SELECTION_SEED)
    target_swap_rows = build_target_swap_hard_negatives(
        train_rows,
        per_source=TARGET_SWAP_PER_SOURCE,
        seed=DATA_SELECTION_SEED,
    )
    train_rows = [*train_rows, *target_swap_rows]

    checkpoint_rows = [
        *[
            {**row, "source_type": "NEWS", "dataset": "PUBLIC_CHECKPOINT"}
            for row in public_development["CHECKPOINT"]
        ],
        *[
            {**row, "dataset": "K_FNSPID_DEVELOPMENT_CHECKPOINT"}
            for row in news_development_split["CHECKPOINT"]
        ],
        *[
            {**row, "dataset": "K_FNSPID_DISCLOSURE_DEVELOPMENT_CHECKPOINT"}
            for row in disclosure_development_split["CHECKPOINT"]
        ],
    ]
    calibration_rows = [
        *[
            {**row, "source_type": "NEWS", "dataset": "PUBLIC_CALIBRATION"}
            for row in public_development["CALIBRATION"]
        ],
        *[
            {**row, "dataset": "K_FNSPID_DEVELOPMENT_CALIBRATION"}
            for row in news_development_split["CALIBRATION"]
        ],
        *[
            {**row, "dataset": "K_FNSPID_DISCLOSURE_DEVELOPMENT_CALIBRATION"}
            for row in disclosure_development_split["CALIBRATION"]
        ],
    ]
    selection_rows = [
        *[
            {**row, "source_type": "NEWS", "dataset": "PUBLIC_SELECTION"}
            for row in public_development["SELECTION"]
        ],
        *[
            {**row, "dataset": "K_FNSPID_DEVELOPMENT_SELECTION"}
            for row in news_development_split["SELECTION"]
        ],
        *[
            {**row, "dataset": "K_FNSPID_DISCLOSURE_DEVELOPMENT_SELECTION"}
            for row in disclosure_development_split["SELECTION"]
        ],
    ]
    assert_sentiment_groups_disjoint(
        {
            "TRAIN": train_rows,
            "CHECKPOINT": checkpoint_rows,
            "CALIBRATION": calibration_rows,
            "SELECTION": selection_rows,
            "NEWS_CONFIRMATORY_RESERVATION": news_confirmatory,
            "DISCLOSURE_CONFIRMATORY_RESERVATION": disclosure_confirmatory,
        }
    )
    return PreparedTrainingData(
        train_rows=train_rows,
        checkpoint_rows=checkpoint_rows,
        calibration_rows=calibration_rows,
        selection_rows=selection_rows,
        news_confirmatory_reservation=news_confirmatory,
        disclosure_confirmatory_reservation=disclosure_confirmatory,
        input_paths=input_paths,
        gold_provenance=gold_provenance,
        public_audit=public_audit,
        silver_audit=silver_audit,
        disclosure_silver_audit=disclosure_silver_audit,
        final_overlap_audit=final_overlap_audit,
    )


def _training_input_paths(args: argparse.Namespace) -> dict[str, Path]:
    result = {
        "public_train": args.dataset_dir / "ratings_train.csv",
        "public_validation": args.dataset_dir / "ratings_val.csv",
        "news_silver": args.silver_path,
        "disclosure_silver": args.disclosure_silver_path,
        "train_gold": args.train_gold_path,
        "news_auxiliary_training_gold": args.news_auxiliary_gold_path,
        "disclosure_auxiliary_training_gold": args.disclosure_auxiliary_gold_path,
        "news_auxiliary_training_report": args.news_auxiliary_report_path,
        "disclosure_auxiliary_training_report": args.disclosure_auxiliary_report_path,
        "news_development_gold": args.development_gold_path,
        "disclosure_development_gold": args.disclosure_development_gold_path,
        "news_confirmatory_reservation": args.news_confirmatory_reservation,
        "disclosure_confirmatory_reservation": args.disclosure_confirmatory_reservation,
        "confirmatory_sampling_design": args.confirmatory_sampling_design,
    }
    result.update(
        {
            f"legacy_evaluation_{index}": path
            for index, path in enumerate(LEGACY_EVALUATION_PATHS, start=1)
        }
    )
    result.update(gold_provenance_paths(args))
    return result


def train_seed(
    args: argparse.Namespace,
    seed: int,
    prepared: PreparedTrainingData,
) -> dict[str, Any]:
    seed_output = args.output_root / f"seed{seed}"
    seed_report = args.report_root / f"seed{seed}.json"
    checkpoint_dir = args.output_root / ".checkpoints" / f"seed{seed}"
    for label, path in (
        ("seed artifact", seed_output),
        ("seed report", seed_report),
        ("seed checkpoint", checkpoint_dir),
    ):
        if path.exists() or path.is_symlink():
            raise SystemExit(f"{label} 출력이 이미 존재합니다: {path}")

    _set_seed(seed)
    tokenizer, model = _load_base_model()
    if args.gradient_checkpointing:
        model.gradient_checkpointing_enable()
        model_config: Any = model.config
        model_config.use_cache = False

    datasets = {
        "TRAIN": EncodedSentimentDataset(
            prepared.train_rows,
            tokenizer,
            MAX_LENGTH,
        ),
        "CHECKPOINT": EncodedSentimentDataset(
            prepared.checkpoint_rows,
            tokenizer,
            MAX_LENGTH,
        ),
        "CALIBRATION": EncodedSentimentDataset(
            prepared.calibration_rows,
            tokenizer,
            MAX_LENGTH,
        ),
        "SELECTION": EncodedSentimentDataset(
            prepared.selection_rows,
            tokenizer,
            MAX_LENGTH,
        ),
    }
    class_weights = _effective_number_weights(prepared.train_rows)
    optimizer_steps = max(
        1,
        round(len(prepared.train_rows) * EPOCHS / (BATCH_SIZE * GRADIENT_ACCUMULATION_STEPS)),
    )
    trainer = HierarchicalSentimentTrainer(
        model=model,
        args=TrainingArguments(
            output_dir=str(checkpoint_dir),
            per_device_train_batch_size=BATCH_SIZE,
            per_device_eval_batch_size=max(4, BATCH_SIZE * 2),
            gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
            num_train_epochs=EPOCHS,
            learning_rate=LEARNING_RATE,
            lr_scheduler_type="cosine",
            warmup_steps=max(1, round(optimizer_steps * 0.08)),
            weight_decay=0.01,
            gradient_checkpointing=args.gradient_checkpointing,
            eval_strategy="epoch",
            save_strategy="epoch",
            logging_steps=50,
            load_best_model_at_end=True,
            metric_for_best_model="macro_f1",
            greater_is_better=True,
            save_total_limit=2,
            seed=seed,
            data_seed=seed,
            report_to="none",
            dataloader_num_workers=0,
            dataloader_pin_memory=False,
            remove_unused_columns=False,
        ),
        train_dataset=datasets["TRAIN"],
        eval_dataset=datasets["CHECKPOINT"],
        data_collator=WeightedSentimentCollator(tokenizer),
        processing_class=tokenizer,
        compute_metrics=_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=EARLY_STOPPING_PATIENCE)],
        class_weights=class_weights,
        rdrop_alpha=R_DROP_ALPHA,
    )
    train_result = trainer.train()
    calibration_output = trainer.predict(datasets["CALIBRATION"])
    logit_bias_by_domain = _fit_logit_bias_by_domain(
        _prediction_logits(calibration_output),
        prepared.calibration_rows,
    )
    calibration_metrics = _evaluate_partition(
        trainer,
        datasets["CALIBRATION"],
        prepared.calibration_rows,
        logit_bias_by_domain,
        "calibration",
    )
    selection_metrics = _evaluate_partition(
        trainer,
        datasets["SELECTION"],
        prepared.selection_rows,
        logit_bias_by_domain,
        "selection",
    )
    selection_breakdown = _evaluate_breakdown(
        trainer,
        prepared.selection_rows,
        tokenizer,
        MAX_LENGTH,
        logit_bias_by_domain,
    )
    weakest_source_score = _selection_score(selection_breakdown)

    seed_output.mkdir(parents=True, exist_ok=False)
    trained_model: Any = trainer.model
    if trained_model is None:
        raise RuntimeError("학습 완료 모델이 없습니다.")
    trained_model.save_pretrained(seed_output, safe_serialization=True)
    tokenizer.save_pretrained(seed_output)
    artifact_files = build_artifact_manifest(
        seed_output,
        (
            "config.json",
            "model.safetensors",
            "special_tokens_map.json",
            "tokenizer.json",
            "tokenizer_config.json",
            "vocab.txt",
        ),
    )
    trained_at = datetime.now(UTC).isoformat()
    metadata = {
        "schema_version": "k-fnspid-fair-baseline-artifact/v1",
        "version": (
            "kr-finbert-sc-k-fnspid-fair-baseline-"
            f"seed{seed}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
        ),
        "base_model": BASE_MODEL,
        "base_model_revision": BASE_MODEL_REVISION,
        "weights_format": "safetensors",
        "label_order": LABEL_ORDER,
        "max_length": MAX_LENGTH,
        "input_feature_version": "source-target-prefix-head-tail/v2",
        "full_finetune": True,
        "logit_bias_by_domain": logit_bias_by_domain,
        "trained_at": trained_at,
        "artifact_files": artifact_files,
    }
    _write_new_json(seed_output / "hannah_metadata.json", metadata)

    report = {
        **metadata,
        "schema_version": "k-fnspid-fair-baseline-training/v1",
        "seed": seed,
        "dataset_revision": DATASET_REVISION,
        "public_dataset_revision": PUBLIC_DATASET_REVISION,
        "input_artifacts": _input_provenance(prepared.input_paths),
        "training_code": _code_provenance(),
        "dependency_provenance": _dependency_provenance(),
        "base_model_provenance": _base_model_provenance(),
        "prepared_partition_commitments": _prepared_partition_commitments(prepared),
        "verified_gold_provenance": prepared.gold_provenance,
        "training_arguments": _training_arguments(args, seed),
        "training_strategy": (
            "full-finetune-same-three-way-dual-gold-target-swap-rdrop-hierarchical/v4"
        ),
        "loss": {
            "method": "effective-mass-class-balanced-focal-plus-hierarchical-boundary/v2",
            "focal_gamma": 1.5,
            "directional_weight": 0.35,
            "polarity_weight": 0.20,
            "rdrop_alpha": R_DROP_ALPHA,
            "class_weights": class_weights.tolist(),
        },
        "target_swap_augmentation": {
            "method": "deterministic-name-code-alias-absent-target-swap/v2",
            "per_source": TARGET_SWAP_PER_SOURCE,
            "sample_weight": TARGET_SWAP_WEIGHT,
            "generated_count": len(
                [
                    row
                    for row in prepared.train_rows
                    if row.get("augmentation_method") == "ABSENT_TARGET_SWAP_V2"
                ]
            ),
            "same_data_augmentation_schedule_as_candidate": True,
            "donor_absence_fields": ["stock_name", "stock_code", "stock_aliases"],
            "donor_alias_provenance_preserved": True,
        },
        "partition_count": {
            "TRAIN": len(prepared.train_rows),
            "CHECKPOINT": len(prepared.checkpoint_rows),
            "CALIBRATION": len(prepared.calibration_rows),
            "SELECTION": len(prepared.selection_rows),
            "PUBLIC_TEST": 0,
        },
        "training_source_distribution": dict(
            sorted(Counter(str(row["dataset"]) for row in prepared.train_rows).items())
        ),
        "training_label_distribution": _label_distribution(prepared.train_rows),
        "training_weight_audit": _training_weight_audit(prepared.train_rows),
        "public_partition_leakage_audit": prepared.public_audit,
        "silver_audit": prepared.silver_audit,
        "disclosure_silver_audit": prepared.disclosure_silver_audit,
        "final_group_overlap_purge": prepared.final_overlap_audit,
        "candidate_selection": {
            "selection_partition": "PUBLIC_AND_K_FNSPID_DEVELOPMENT_SELECTION",
            "selection_method": "weakest-source-macro-f1-then-overall/v1",
            "selection_score": weakest_source_score,
            "required_sources": REQUIRED_SELECTION_DATASETS,
            "public_test_path_accessed": False,
            "public_test_labels_used": False,
            "confirmatory_labels_used": False,
            "confirmatory_reservation_identity_only": True,
        },
        "calibration": calibration_metrics,
        "selection": selection_metrics,
        "selection_breakdown": selection_breakdown,
        "training_environment": {
            "mps_available": torch.backends.mps.is_available(),
            "cuda_available": torch.cuda.is_available(),
            "trainer_device": str(trainer.args.device),
            "bitwise_deterministic_guaranteed": False,
            "reproducibility_limit": (
                "동일 seed라도 MPS/CUDA 커널과 라이브러리 버전에 따라 bitwise 결과가 달라질 수 있음"
            ),
        },
        "training_runtime": _trainer_runtime_record(trainer, train_result),
        "test": {
            "sample_count": 0,
            "status": "FORBIDDEN_DURING_TRAINING_AND_SELECTION",
        },
        "trainable_parameter_count": _parameter_counts(trained_model)[0],
        "total_parameter_count": _parameter_counts(trained_model)[1],
    }
    if report["trainable_parameter_count"] != report["total_parameter_count"]:
        raise RuntimeError("전체 fine-tune parameter 계약이 저장 직전에 깨졌습니다.")
    _write_new_json(seed_report, report)
    return report


def _load_base_model() -> tuple[Any, Any]:
    tokenizer = AutoTokenizer.from_pretrained(
        BASE_MODEL,
        revision=BASE_MODEL_REVISION,
        trust_remote_code=False,
    )
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL,
        revision=BASE_MODEL_REVISION,
        num_labels=len(LABEL_ORDER),
        id2label={index: label for index, label in enumerate(LABEL_ORDER)},
        label2id={label: index for index, label in enumerate(LABEL_ORDER)},
        trust_remote_code=False,
        use_safetensors=True,
        weights_only=True,
    )
    _assert_full_finetune(model)
    return tokenizer, model


def _assert_full_finetune(model: Any) -> None:
    parameters = list(model.named_parameters())
    if not parameters or any(not bool(parameter.requires_grad) for _, parameter in parameters):
        raise RuntimeError("KR-FinBERT-SC의 모든 parameter가 학습 가능해야 합니다.")
    classifier_parameters = [
        parameter
        for name, parameter in parameters
        if "classifier" in name.casefold() or name.casefold().startswith("score")
    ]
    if not classifier_parameters or any(
        not bool(parameter.requires_grad) for parameter in classifier_parameters
    ):
        raise RuntimeError("분류 head가 전체 fine-tune 대상이 아닙니다.")


def _training_arguments(args: argparse.Namespace, seed: int) -> dict[str, Any]:
    return {
        "seed": seed,
        "data_selection_seed": DATA_SELECTION_SEED,
        "seed_budget": FAIR_SEEDS,
        "max_length": MAX_LENGTH,
        "epochs": EPOCHS,
        "batch_size": BATCH_SIZE,
        "gradient_accumulation_steps": GRADIENT_ACCUMULATION_STEPS,
        "early_stopping_patience": EARLY_STOPPING_PATIENCE,
        "learning_rate": LEARNING_RATE,
        "lr_scheduler_type": "cosine",
        "warmup_fraction": 0.08,
        "weight_decay": 0.01,
        "silver_per_label": SILVER_PER_LABEL,
        "disclosure_per_label": DISCLOSURE_PER_LABEL,
        "target_swap_per_source": TARGET_SWAP_PER_SOURCE,
        "target_swap_weight": TARGET_SWAP_WEIGHT,
        "rdrop_alpha": R_DROP_ALPHA,
        "same_data_splits_seeds_epochs_update_schedule_as_candidate": True,
        "comparison_scope": (
            "same prepared rows, split commitments, model seeds, epochs, batch, "
            "gradient accumulation, scheduler and early-stop schedule"
        ),
        "model_specific_optimizer_and_parameterization": True,
        "gradient_checkpointing": bool(args.gradient_checkpointing),
        "max_train_rows": args.max_train_rows,
    }


def _selection_summary(
    args: argparse.Namespace,
    reports: list[dict[str, Any]],
) -> dict[str, Any]:
    if {int(report["seed"]) for report in reports} != set(FAIR_SEEDS):
        raise ValueError("공정 기준선은 고정된 3개 seed report가 모두 필요합니다.")
    winner = max(
        reports,
        key=lambda report: (
            float(report["candidate_selection"]["selection_score"]),
            float(report["selection"]["macro_f1"]),
            -int(report["seed"]),
        ),
    )
    run_records = []
    for report in sorted(reports, key=lambda item: int(item["seed"])):
        path = args.report_root / f"seed{int(report['seed'])}.json"
        run_records.append(
            {
                "seed": int(report["seed"]),
                "selection_score": float(report["candidate_selection"]["selection_score"]),
                "overall_selection_macro_f1": float(report["selection"]["macro_f1"]),
                "report": _input_artifact_record(path),
            }
        )
    return {
        "schema_version": "k-fnspid-fair-baseline-selection/v1",
        "base_model": BASE_MODEL,
        "base_model_revision": BASE_MODEL_REVISION,
        "seed_budget": FAIR_SEEDS,
        "selection_method": "weakest-source-macro-f1-then-overall-then-lowest-seed/v1",
        "selected_seed": int(winner["seed"]),
        "selected_weakest_source_macro_f1": float(winner["candidate_selection"]["selection_score"]),
        "public_test_labels_used": False,
        "confirmatory_labels_used": False,
        "runs": run_records,
        "generated_at": datetime.now(UTC).isoformat(),
    }


def _validation_plan(
    args: argparse.Namespace,
    prepared_by_seed: dict[int, PreparedTrainingData],
) -> dict[str, Any]:
    first = prepared_by_seed[FAIR_SEEDS[0]]
    return {
        "schema_version": "k-fnspid-fair-baseline-validation-plan/v1",
        "status": "VALIDATED_WITHOUT_MODEL_LOAD_OR_TRAINING",
        "base_model_provenance": _base_model_provenance(),
        "training_arguments": {str(seed): _training_arguments(args, seed) for seed in FAIR_SEEDS},
        "input_artifacts": _input_provenance(first.input_paths),
        "training_code": _code_provenance(),
        "dependency_provenance": _dependency_provenance(),
        "prepared_partition_commitments": {
            str(seed): _prepared_partition_commitments(prepared)
            for seed, prepared in sorted(prepared_by_seed.items())
        },
        "verified_gold_provenance": first.gold_provenance,
        "public_test_path_accessed": False,
        "public_test_labels_used": False,
        "confirmatory_labels_used": False,
        "output_created": False,
    }


def _prepared_partition_commitments(
    prepared: PreparedTrainingData,
) -> dict[str, dict[str, int | str]]:
    return _build_prepared_partition_commitments(
        train_rows=prepared.train_rows,
        checkpoint_rows=prepared.checkpoint_rows,
        calibration_rows=prepared.calibration_rows,
        selection_rows=prepared.selection_rows,
        news_reservation=prepared.news_confirmatory_reservation,
        disclosure_reservation=prepared.disclosure_confirmatory_reservation,
    )


def _input_provenance(paths: dict[str, Path]) -> dict[str, dict[str, int | str]]:
    return {name: _input_artifact_record(path) for name, path in sorted(paths.items())}


def _code_provenance() -> dict[str, dict[str, int | str]]:
    paths = {
        "fair_baseline_trainer": Path(__file__).resolve(),
        "candidate_training_pipeline": PROJECT_ROOT / "scripts/train_kf_deberta_sentiment_v2.py",
        "sentiment_input": PROJECT_ROOT / "src/hannah_montana_ai/services/sentiment_input.py",
        "sentiment_protocol": PROJECT_ROOT / "src/hannah_montana_ai/training/sentiment_protocol.py",
    }
    return _input_provenance(paths)


def _dependency_provenance() -> dict[str, Any]:
    lock_files = _input_provenance(
        {
            "pyproject": PROJECT_ROOT / "pyproject.toml",
            "uv_lock": PROJECT_ROOT / "uv.lock",
        }
    )
    versions = {
        name: importlib.metadata.version(name)
        for name in ("accelerate", "numpy", "peft", "torch", "transformers")
    }
    encoded = json.dumps(
        {"lock_files": lock_files, "runtime_versions": versions},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return {
        "lock_files": lock_files,
        "runtime_versions": versions,
        "dependency_contract_sha256": sha256(encoded).hexdigest(),
    }


def _base_model_provenance() -> dict[str, Any]:
    if len(BASE_MODEL_REVISION) != 40 or any(
        character not in "0123456789abcdef" for character in BASE_MODEL_REVISION
    ):
        raise RuntimeError("기준선 base revision이 완전한 git SHA가 아닙니다.")
    return {
        "repository": BASE_MODEL,
        "revision": BASE_MODEL_REVISION,
        "upstream_main_revision_at_lock": BASE_MODEL_UPSTREAM_MAIN_REVISION,
        "weights_format": "safetensors",
        "trust_remote_code": False,
        "weights_only": True,
        "full_finetune": True,
        "classification_head_trainable": True,
    }


def _write_new_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as file:
        file.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
