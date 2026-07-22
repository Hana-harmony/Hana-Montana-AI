from __future__ import annotations

import argparse
import csv
import importlib.metadata
import json
import math
import platform
import random
import sys
from collections import Counter
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, cast

import numpy as np
import torch
import torch.nn.functional as functional
from huggingface_hub import hf_hub_download
from numpy.typing import NDArray
from peft import LoraConfig, TaskType, get_peft_model
from sklearn.metrics import accuracy_score, f1_score
from torch.utils.data import Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    EarlyStoppingCallback,
    EvalPrediction,
    Trainer,
    TrainingArguments,
)

from hannah_montana_ai.services.model_artifact_integrity import build_artifact_manifest
from hannah_montana_ai.services.sentiment_input import (
    SENTIMENT_LOGIT_BIAS_DOMAINS,
    encode_sentiment_input,
    sentiment_source_domain,
    validated_sentiment_logit_biases,
)
from hannah_montana_ai.training.sentiment_protocol import (
    assert_sentiment_groups_disjoint,
    decontaminate_public_partitions,
    normalized_sentiment_text,
    purge_sentiment_group_overlap,
    sentiment_provenance,
    stratified_hash_three_way_split,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_MODEL = "kakaobank/kf-deberta-base"
BASE_MODEL_REVISION = "363b171d71443b0874b0bf9cea053eb5b1650633"
BASE_MODEL_WEIGHT_FILENAME = "pytorch_model.bin"
BASE_MODEL_WEIGHT_SHA256 = "3cd6cd7811b3c9190e97cae7eb41571c2bc0076431baae7d41d449a8c1c18c6c"
DATASET_REVISION = "K-FNSPID-v4"
PUBLIC_DATASET_REVISION = "7a8dc8cf6548a08e0a5dab3a12ad0fb8dccfd23f"
DEFAULT_DATASET = PROJECT_ROOT / "data/external/kf_deberta_benchmark"
DEFAULT_SILVER = PROJECT_ROOT / "data/training/k_fnspid_sentiment_silver.jsonl"
DEFAULT_DISCLOSURE_SILVER = (
    PROJECT_ROOT / "data/training/k_fnspid_disclosure_sentiment_silver.jsonl"
)
DEFAULT_TRAIN_GOLD = (
    PROJECT_ROOT / "data/training/k_fnspid_sentiment_codex_gold_review_v3.jsonl"
)
DEFAULT_NEWS_AUXILIARY_GOLD = (
    PROJECT_ROOT / "data/training/k_fnspid_news_sentiment_auxiliary_gold_review_v4.jsonl"
)
DEFAULT_DISCLOSURE_AUXILIARY_GOLD = (
    PROJECT_ROOT
    / "data/training/k_fnspid_disclosure_sentiment_auxiliary_gold_review_v4.jsonl"
)
DEFAULT_NEWS_AUXILIARY_REPORT = (
    PROJECT_ROOT / "reports/k-fnspid-news-sentiment-training-reclassification-review-v4.json"
)
DEFAULT_DISCLOSURE_AUXILIARY_REPORT = (
    PROJECT_ROOT
    / "reports/k-fnspid-disclosure-sentiment-training-reclassification-review-v4.json"
)
DEFAULT_DEVELOPMENT_GOLD = (
    PROJECT_ROOT
    / "data/evaluation/k_fnspid_sentiment_development_gold_review_v3.jsonl"
)
DEFAULT_DISCLOSURE_DEVELOPMENT_GOLD = (
    PROJECT_ROOT
    / "data/evaluation/k_fnspid_disclosure_sentiment_development_gold_review_v3.jsonl"
)
DEFAULT_NEWS_SEALED_REVIEW = PROJECT_ROOT / "data/gold/confirmatory_sealed_test_review.jsonl"
DEFAULT_DISCLOSURE_SEALED_REVIEW = (
    PROJECT_ROOT / "data/gold/disclosure_confirmatory_sealed_test_review.jsonl"
)
DEFAULT_SAMPLING_DESIGN_REPORT = (
    PROJECT_ROOT / "reports/k-fnspid-sentiment-confirmatory-sealed-sampling-design-v2.json"
)
DEFAULT_OUTPUT = PROJECT_ROOT / "artifacts/sentiment/candidates/seed42"
DEFAULT_REPORT = PROJECT_ROOT / "reports/candidates/kf-deberta-sentiment-seed42.json"
LEGACY_EVALUATION_PATHS = (
    PROJECT_ROOT / "data/evaluation/financial_alert_eval.jsonl",
    PROJECT_ROOT / "data/evaluation/financial_alert_real_disclosure_gold.jsonl",
    PROJECT_ROOT / "data/evaluation/financial_alert_real_news_gold.jsonl",
    PROJECT_ROOT / "data/evaluation/financial_alert_stock_review_gold.jsonl",
)
LABEL_ORDER = ("NEGATIVE", "NEUTRAL", "POSITIVE")
SOURCE_LABEL = {"-1": "NEGATIVE", "0": "NEUTRAL", "1": "POSITIVE"}
GOLD_SCHEMA_VERSION = "k-fnspid-sentiment-codex-gold/v1"
LORA_LAYERS = (6, 7, 8, 9, 10, 11)
R_DROP_ALPHA = 0.35
TARGET_SWAP_WEIGHT = 0.55
DATA_SELECTION_SEED = 20_260_715
MIN_DEVELOPMENT_LABEL_COUNT = 5
AUXILIARY_GOLD_SCHEMA_VERSION = "k-fnspid-sentiment-auxiliary-training-gold/v2"
AUXILIARY_REPORT_SCHEMA_VERSION = "k-fnspid-sentiment-training-reclassification/v2"
AUXILIARY_TRAINING_ROLE = "TRAINING_ONLY_NOT_EVALUATION_OR_CLAIM_EVIDENCE"
AUXILIARY_UNRESOLVED_LABEL = "UNRESOLVED"
AUXILIARY_DECISION_FIELDS = frozenset(
    {
        "schema_version",
        "item_id",
        "reviewer_1",
        "reviewer_2",
        "independent_reviewer_count",
        "inter_reviewer_agreement",
        "decision_path",
        "adjudication",
        "final_sentiment",
        "review_note",
        "reviewer_id",
        "reviewed_at",
        "review_status",
        "reviewer_type",
        "model_blind",
        "market_blind",
    }
)
AUXILIARY_REVIEWER_FIELDS = frozenset(
    {
        "stage_1",
        "stage_2",
        "final_sentiment",
        "label_evidence",
        "decision_path",
        "reviewer_id",
        "reviewed_at",
        "reviewer_type",
        "model_blind",
        "market_blind",
    }
)
AUXILIARY_ADJUDICATION_FIELDS = frozenset(
    {
        "item_id",
        "final_sentiment",
        "adjudication_note",
        "adjudicator_id",
        "adjudicated_at",
        "adjudication_status",
    }
)


class EncodedSentimentDataset(Dataset[dict[str, Any]]):
    def __init__(self, rows: list[dict[str, Any]], tokenizer: Any, max_length: int) -> None:
        self.features = []
        for row in rows:
            self.features.append(
                {
                    **encode_sentiment_input(
                        tokenizer,
                        str(row["text"]),
                        str(row.get("source_type", "NEWS")),
                        max_length,
                        _target_security(row),
                    ),
                    "labels": LABEL_ORDER.index(str(row["label"])),
                    "sample_weight": float(row.get("sample_weight", 1.0)),
                }
            )

    def __len__(self) -> int:
        return len(self.features)

    def __getitem__(self, index: int) -> dict[str, Any]:
        return self.features[index]


class WeightedSentimentCollator:
    def __init__(self, tokenizer: Any) -> None:
        self._collator = DataCollatorWithPadding(tokenizer=tokenizer)

    def __call__(self, features: list[dict[str, Any]]) -> dict[str, Any]:
        weights = torch.tensor(
            [float(feature["sample_weight"]) for feature in features], dtype=torch.float32
        )
        model_features = [
            {name: value for name, value in feature.items() if name != "sample_weight"}
            for feature in features
        ]
        batch = self._collator(model_features)
        batch["sample_weight"] = weights
        return batch


class HierarchicalSentimentTrainer(Trainer):
    def __init__(
        self,
        *args: Any,
        class_weights: torch.Tensor,
        rdrop_alpha: float = R_DROP_ALPHA,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._class_weights = class_weights
        self._rdrop_alpha = rdrop_alpha

    def compute_loss(
        self,
        model: Any,
        inputs: dict[str, Any],
        return_outputs: bool = False,
        num_items_in_batch: int | torch.Tensor | None = None,
    ) -> Any:
        del num_items_in_batch
        sample_weights = inputs.pop("sample_weight")
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        primary_loss = hierarchical_focal_loss(
            outputs.logits,
            labels,
            sample_weights,
            self._class_weights.to(outputs.logits.device),
        )
        loss = primary_loss
        if model.training and self._rdrop_alpha > 0.0:
            repeated_outputs = model(**inputs)
            repeated_loss = hierarchical_focal_loss(
                repeated_outputs.logits,
                labels,
                sample_weights,
                self._class_weights.to(repeated_outputs.logits.device),
            )
            consistency = symmetric_kl_consistency_loss(
                outputs.logits,
                repeated_outputs.logits,
                sample_weights,
            )
            loss = 0.5 * (primary_loss + repeated_loss) + self._rdrop_alpha * consistency
        return (loss, outputs) if return_outputs else loss


def hierarchical_focal_loss(
    logits: torch.Tensor,
    labels: torch.Tensor,
    sample_weights: torch.Tensor,
    class_weights: torch.Tensor,
) -> torch.Tensor:
    probabilities = functional.softmax(logits, dim=-1)
    true_probabilities = probabilities.gather(1, labels.unsqueeze(1)).squeeze(1)
    categorical = functional.cross_entropy(
        logits,
        labels,
        weight=class_weights,
        reduction="none",
    )
    focal = (1.0 - true_probabilities).pow(1.5) * categorical

    directional_logits = torch.stack(
        (logits[:, 1], torch.logsumexp(logits[:, (0, 2)], dim=1)), dim=1
    )
    directional_targets = (labels != 1).long()
    directional = functional.cross_entropy(
        directional_logits, directional_targets, reduction="none"
    )

    direction_mask = labels != 1
    direction = torch.zeros_like(focal)
    if bool(direction_mask.any()):
        direction[direction_mask] = functional.cross_entropy(
            logits[direction_mask][:, (0, 2)],
            (labels[direction_mask] == 2).long(),
            reduction="none",
        )
    per_row = focal + 0.35 * directional + 0.20 * direction
    effective_weights = sample_weights.to(logits.device).clamp_min(0.05)
    return cast(torch.Tensor, (per_row * effective_weights).sum() / effective_weights.sum())


def symmetric_kl_consistency_loss(
    first_logits: torch.Tensor,
    second_logits: torch.Tensor,
    sample_weights: torch.Tensor,
) -> torch.Tensor:
    if first_logits.shape != second_logits.shape:
        raise ValueError("R-Drop logit 형상이 일치하지 않습니다.")
    first_log_probabilities = functional.log_softmax(first_logits, dim=-1)
    second_log_probabilities = functional.log_softmax(second_logits, dim=-1)
    first_probabilities = first_log_probabilities.exp()
    second_probabilities = second_log_probabilities.exp()
    forward = functional.kl_div(
        first_log_probabilities,
        second_probabilities,
        reduction="none",
    ).sum(dim=-1)
    reverse = functional.kl_div(
        second_log_probabilities,
        first_probabilities,
        reduction="none",
    ).sum(dim=-1)
    effective_weights = sample_weights.to(first_logits.device).clamp_min(0.05)
    per_row = 0.5 * (forward + reverse)
    return (per_row * effective_weights).sum() / effective_weights.sum()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="누수 차단 K-FNSPID 감성 데이터로 KF-DeBERTa 후보를 학습한다."
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
    parser.add_argument("--news-sealed-review-path", type=Path, default=DEFAULT_NEWS_SEALED_REVIEW)
    parser.add_argument(
        "--disclosure-sealed-review-path",
        type=Path,
        default=DEFAULT_DISCLOSURE_SEALED_REVIEW,
    )
    parser.add_argument(
        "--sampling-design-report",
        type=Path,
        default=DEFAULT_SAMPLING_DESIGN_REPORT,
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-length", type=int, default=256)
    parser.add_argument("--epochs", type=float, default=1.5)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=2)
    parser.add_argument("--learning-rate", type=float, default=1e-4)
    parser.add_argument("--silver-per-label", type=int, default=6_000)
    parser.add_argument("--disclosure-per-label", type=int, default=900)
    parser.add_argument("--target-swap-per-source", type=int, default=1_500)
    parser.add_argument("--rdrop-alpha", type=float, default=R_DROP_ALPHA)
    parser.add_argument("--max-train-rows", type=int)
    parser.add_argument("--gradient-checkpointing", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    if (
        not 16 <= args.max_length <= 512
        or args.epochs <= 0.0
        or args.batch_size < 1
        or args.gradient_accumulation_steps < 1
        or args.learning_rate <= 0.0
        or args.silver_per_label < 1
        or args.disclosure_per_label < 1
        or args.target_swap_per_source < 0
        or not 0.0 <= args.rdrop_alpha <= 2.0
        or (args.max_train_rows is not None and args.max_train_rows < 3)
    ):
        raise SystemExit("학습 인자가 허용 범위를 벗어났습니다.")
    checkpoint_dir = args.output_dir.parent / f".{args.output_dir.name}-checkpoints"
    if not args.validate_only:
        for label, path in (
            ("후보 artifact", args.output_dir),
            ("후보 report", args.report_path),
            ("학습 checkpoint", checkpoint_dir),
        ):
            if path.exists() or path.is_symlink():
                raise SystemExit(f"{label} 출력이 이미 존재합니다: {path}")

    input_paths = {
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
        "news_sealed_review_reservation": args.news_sealed_review_path,
        "disclosure_sealed_review_reservation": args.disclosure_sealed_review_path,
        "sealed_sampling_design": args.sampling_design_report,
    }
    input_paths.update(
        {
            f"legacy_evaluation_{index}": path
            for index, path in enumerate(LEGACY_EVALUATION_PATHS, start=1)
        }
    )
    for name, path in input_paths.items():
        _require_regular_input(path, name)

    _set_seed(args.seed)
    public, public_audit = decontaminate_public_partitions(
        {
            "TRAIN": _load_public_rows(args.dataset_dir / "ratings_train.csv"),
            "VALIDATION": _load_public_rows(args.dataset_dir / "ratings_val.csv"),
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
    train_gold = _load_reviewed_rows(args.train_gold_path, "TRAIN_REVIEW", weight=1.5)
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
    development_gold = _load_reviewed_rows(
        args.development_gold_path, "DEVELOPMENT_REVIEW", weight=1.0
    )
    development_split = stratified_hash_three_way_split(
        development_gold,
        checkpoint_name="CHECKPOINT",
        calibration_name="CALIBRATION",
        selection_name="SELECTION",
        minimum_per_label=MIN_DEVELOPMENT_LABEL_COUNT,
    )
    disclosure_development_gold = _load_reviewed_rows(
        args.disclosure_development_gold_path,
        "DISCLOSURE_DEVELOPMENT_REVIEW",
        weight=1.0,
    )
    disclosure_development_split = stratified_hash_three_way_split(
        disclosure_development_gold,
        checkpoint_name="CHECKPOINT",
        calibration_name="CALIBRATION",
        selection_name="SELECTION",
        minimum_per_label=MIN_DEVELOPMENT_LABEL_COUNT,
    )
    news_sealed_reservation = _load_sealed_reservation_rows(
        args.news_sealed_review_path, "CONFIRMATORY_SEALED_TEST_REVIEW", "NEWS"
    )
    disclosure_sealed_reservation = _load_sealed_reservation_rows(
        args.disclosure_sealed_review_path,
        "DISCLOSURE_CONFIRMATORY_SEALED_TEST_REVIEW",
        "DISCLOSURE",
    )
    protected = [
        *public_development["CHECKPOINT"],
        *public_development["CALIBRATION"],
        *public_development["SELECTION"],
        *development_gold,
        *disclosure_development_gold,
        *news_sealed_reservation,
        *disclosure_sealed_reservation,
        *_load_legacy_protected_rows(),
    ]
    silver, silver_audit = _load_silver_rows(
        args.silver_path,
        protected,
        args.silver_per_label,
        DATA_SELECTION_SEED,
    )
    disclosure_silver, disclosure_silver_audit = _load_silver_rows(
        args.disclosure_silver_path,
        protected,
        args.disclosure_per_label,
        DATA_SELECTION_SEED + 11,
    )
    public_train = [
        {**row, "source_type": "NEWS", "sample_weight": 1.0, "dataset": "PUBLIC_TRAIN"}
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
    train_rows, final_overlap_audit = purge_sentiment_group_overlap(train_rows, protected)
    if args.max_train_rows:
        train_rows = _stratified_limit(train_rows, args.max_train_rows, DATA_SELECTION_SEED)
    target_swap_rows = build_target_swap_hard_negatives(
        train_rows,
        per_source=args.target_swap_per_source,
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
            for row in development_split["CHECKPOINT"]
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
            for row in development_split["CALIBRATION"]
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
            for row in development_split["SELECTION"]
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
            "PUBLIC_TEST": public["TEST"],
            "NEWS_SEALED_RESERVATION": news_sealed_reservation,
            "DISCLOSURE_SEALED_RESERVATION": disclosure_sealed_reservation,
        }
    )
    prepared_partition_commitments = _prepared_partition_commitments(
        train_rows=train_rows,
        checkpoint_rows=checkpoint_rows,
        calibration_rows=calibration_rows,
        selection_rows=selection_rows,
        news_reservation=news_sealed_reservation,
        disclosure_reservation=disclosure_sealed_reservation,
    )
    if args.validate_only:
        print(
            json.dumps(
                {
                    "status": "VALIDATED_WITHOUT_TRAINING",
                    "public_test_opened": False,
                    "train_count": len(train_rows),
                    "checkpoint_count": len(checkpoint_rows),
                    "calibration_count": len(calibration_rows),
                    "selection_count": len(selection_rows),
                    "target_swap_count": len(target_swap_rows),
                    "train_label_distribution": _label_distribution(train_rows),
                    "data_selection_seed": DATA_SELECTION_SEED,
                    "prepared_partition_commitments": prepared_partition_commitments,
                    "input_artifacts": {
                        name: _input_artifact_record(path)
                        for name, path in sorted(input_paths.items())
                    },
                },
                ensure_ascii=False,
            )
        )
        return

    _verify_base_model_weights()
    tokenizer = AutoTokenizer.from_pretrained(
        BASE_MODEL,
        revision=BASE_MODEL_REVISION,
        trust_remote_code=False,
    )
    base = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL,
        revision=BASE_MODEL_REVISION,
        num_labels=len(LABEL_ORDER),
        id2label={index: label for index, label in enumerate(LABEL_ORDER)},
        label2id={label: index for index, label in enumerate(LABEL_ORDER)},
        trust_remote_code=False,
        weights_only=True,
    )
    model = get_peft_model(
        base,
        LoraConfig(
            task_type=TaskType.SEQ_CLS,
            r=24,
            lora_alpha=48,
            lora_dropout=0.08,
            target_modules=["query_proj", "key_proj", "value_proj", "dense"],
            layers_to_transform=list(LORA_LAYERS),
            layers_pattern="layer",
            modules_to_save=["pooler", "classifier"],
        ),
    )
    if args.gradient_checkpointing:
        model.gradient_checkpointing_enable()
        model_config: Any = model.config
        model_config.use_cache = False

    datasets = {
        "TRAIN": EncodedSentimentDataset(train_rows, tokenizer, args.max_length),
        "CHECKPOINT": EncodedSentimentDataset(checkpoint_rows, tokenizer, args.max_length),
        "CALIBRATION": EncodedSentimentDataset(calibration_rows, tokenizer, args.max_length),
        "SELECTION": EncodedSentimentDataset(selection_rows, tokenizer, args.max_length),
    }
    class_weights = _effective_number_weights(train_rows)
    optimizer_steps = max(
        1,
        round(len(train_rows) * args.epochs / (args.batch_size * args.gradient_accumulation_steps)),
    )
    trainer = HierarchicalSentimentTrainer(
        model=model,
        args=TrainingArguments(
            output_dir=str(checkpoint_dir),
            per_device_train_batch_size=args.batch_size,
            per_device_eval_batch_size=max(4, args.batch_size * 2),
            gradient_accumulation_steps=args.gradient_accumulation_steps,
            num_train_epochs=args.epochs,
            learning_rate=args.learning_rate,
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
            seed=args.seed,
            data_seed=args.seed,
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
        callbacks=[EarlyStoppingCallback(early_stopping_patience=1)],
        class_weights=class_weights,
        rdrop_alpha=args.rdrop_alpha,
    )
    train_result = trainer.train()
    trainer.remove_callback(EarlyStoppingCallback)
    calibration_output = trainer.predict(datasets["CALIBRATION"])
    logit_bias_by_domain = _fit_logit_bias_by_domain(
        _prediction_logits(calibration_output), calibration_rows
    )
    uncalibrated_metrics = _metrics(
        EvalPrediction(
            predictions=_prediction_logits(calibration_output),
            label_ids=np.asarray(calibration_output.label_ids),
        )
    )
    calibration_metrics = _evaluate_partition(
        trainer,
        datasets["CALIBRATION"],
        calibration_rows,
        logit_bias_by_domain,
        "calibration",
    )
    selection_metrics = _evaluate_partition(
        trainer,
        datasets["SELECTION"],
        selection_rows,
        logit_bias_by_domain,
        "selection",
    )
    selection_breakdown = _evaluate_breakdown(
        trainer,
        selection_rows,
        tokenizer,
        args.max_length,
        logit_bias_by_domain,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    trained_model: Any = trainer.model
    trained_model.save_pretrained(args.output_dir, safe_serialization=True)
    tokenizer.save_pretrained(args.output_dir)
    artifact_files = build_artifact_manifest(
        args.output_dir,
        (
            "adapter_config.json",
            "adapter_model.safetensors",
            "tokenizer.json",
            "tokenizer_config.json",
        ),
    )
    version = (
        "hana-montana-kf-deberta-k-fnspid-sentiment-"
        f"seed{args.seed}-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    )
    trained_at = datetime.now(UTC).isoformat()
    metadata = {
        "version": version,
        "base_model": BASE_MODEL,
        "base_model_revision": BASE_MODEL_REVISION,
        "label_order": LABEL_ORDER,
        "max_length": args.max_length,
        "input_feature_version": "source-target-prefix-head-tail/v2",
        "logit_bias_by_domain": logit_bias_by_domain,
        "trained_at": trained_at,
        "artifact_files": artifact_files,
    }
    with (args.output_dir / "hannah_metadata.json").open("x", encoding="utf-8") as file:
        file.write(
            json.dumps(
                {"schema_version": "kf-deberta-sentiment-artifact/v2", **metadata},
                ensure_ascii=False,
                indent=2,
            )
            + "\n"
        )
    report = {
        "schema_version": "kf-deberta-sentiment-training/v2",
        **metadata,
        "seed": args.seed,
        "dataset_revision": DATASET_REVISION,
        "public_dataset_revision": PUBLIC_DATASET_REVISION,
        "base_model_provenance": {
            "repository": BASE_MODEL,
            "revision": BASE_MODEL_REVISION,
            "source_weight_filename": "pytorch_model.bin",
            "source_weights_format": "pytorch_model.bin",
            "source_weight_sha256": BASE_MODEL_WEIGHT_SHA256,
            "deserialization": "torch_weights_only",
            "trust_remote_code": False,
            "weights_only": True,
        },
        "input_artifacts": {
            name: _input_artifact_record(path) for name, path in sorted(input_paths.items())
        },
        "training_code": {
            name: _input_artifact_record(path)
            for name, path in {
                "sentiment_input": PROJECT_ROOT
                / "src/hannah_montana_ai/services/sentiment_input.py",
                "sentiment_protocol": PROJECT_ROOT
                / "src/hannah_montana_ai/training/sentiment_protocol.py",
                "sentiment_sampling": PROJECT_ROOT
                / "src/hannah_montana_ai/training/sentiment_sampling.py",
                "model_artifact_integrity": PROJECT_ROOT
                / "src/hannah_montana_ai/services/model_artifact_integrity.py",
                "trainer": Path(__file__).resolve(),
            }.items()
        },
        "dependency_artifacts": {
            name: _input_artifact_record(path)
            for name, path in {
                "pyproject": PROJECT_ROOT / "pyproject.toml",
                "uv_lock": PROJECT_ROOT / "uv.lock",
            }.items()
        },
        "training_environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "torch": torch.__version__,
            "transformers": importlib.metadata.version("transformers"),
            "peft": importlib.metadata.version("peft"),
            "numpy": np.__version__,
            "mps_available": torch.backends.mps.is_available(),
            "cuda_available": torch.cuda.is_available(),
            "trainer_device": str(trainer.args.device),
            "bitwise_deterministic_guaranteed": False,
            "reproducibility_limit": (
                "동일 seed라도 MPS/CUDA 커널과 라이브러리 버전에 따라 bitwise 결과가 달라질 수 있음"
            ),
        },
        "training_arguments": {
            "seed": args.seed,
            "data_selection_seed": DATA_SELECTION_SEED,
            "max_length": args.max_length,
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "gradient_accumulation_steps": args.gradient_accumulation_steps,
            "early_stopping_patience": 1,
            "learning_rate": args.learning_rate,
            "lr_scheduler_type": "cosine",
            "warmup_fraction": 0.08,
            "weight_decay": 0.01,
            "silver_per_label": args.silver_per_label,
            "disclosure_per_label": args.disclosure_per_label,
            "target_swap_per_source": args.target_swap_per_source,
            "rdrop_alpha": args.rdrop_alpha,
            "max_train_rows": args.max_train_rows,
            "gradient_checkpointing": args.gradient_checkpointing,
        },
        "training_strategy": (
            "group-purged-three-way-dual-gold-target-swap-rdrop-hierarchical-upper6-lora/v5"
        ),
        "lora_layers": list(LORA_LAYERS),
        "loss": {
            "method": "effective-mass-class-balanced-focal-plus-hierarchical-boundary/v2",
            "focal_gamma": 1.5,
            "directional_weight": 0.35,
            "polarity_weight": 0.20,
            "rdrop_alpha": args.rdrop_alpha,
            "class_weights": class_weights.tolist(),
        },
        "partition_count": {
            "TRAIN": len(train_rows),
            "CHECKPOINT": len(checkpoint_rows),
            "CALIBRATION": len(calibration_rows),
            "SELECTION": len(selection_rows),
            "PUBLIC_TEST_NOT_LOADED": len(public["TEST"]),
        },
        "training_source_distribution": dict(
            sorted(Counter(str(row["dataset"]) for row in train_rows).items())
        ),
        "training_label_distribution": _label_distribution(train_rows),
        "training_weight_audit": _training_weight_audit(train_rows),
        "prepared_partition_commitments": prepared_partition_commitments,
        "public_partition_leakage_audit": public_audit,
        "silver_audit": silver_audit,
        "disclosure_silver_audit": disclosure_silver_audit,
        "final_group_overlap_purge": final_overlap_audit,
        "target_swap_hard_negative_augmentation": {
            "method": "deterministic-name-code-alias-absent-target-swap/v2",
            "sample_weight": TARGET_SWAP_WEIGHT,
            "requested_per_source": args.target_swap_per_source,
            "selected_count": len(target_swap_rows),
            "source_distribution": dict(
                sorted(Counter(str(row["source_type"]) for row in target_swap_rows).items())
            ),
            "label_distribution": _label_distribution(target_swap_rows),
            "holdout_rows_used": False,
            "donor_absence_fields": ["stock_name", "stock_code", "stock_aliases"],
            "donor_alias_provenance_preserved": True,
        },
        "candidate_selection": {
            "locked_candidate": "kf_deberta_lora",
            "selection_partition": "PUBLIC_AND_K_FNSPID_DEVELOPMENT_SELECTION",
            "selection_score": _selection_score(selection_breakdown),
            "test_used_for_selection": False,
            "operational_gold_used_for_selection": False,
            "sealed_test_evaluated": False,
        },
        "calibration": calibration_metrics,
        "decision_calibration": {
            "method": "validation-only-domain-logit-offset-grid/v1",
            "fit_partition": "CALIBRATION_ONLY",
            "offset_range": [-1.5, 1.5],
            "offset_step": 0.1,
            "minimum_domain_rows": 30,
            "minimum_rows_per_label": 5,
            "selection_used_for_fit": False,
            "public_test_used_for_fit": False,
            "sealed_gold_used_for_fit": False,
            "uncalibrated_metrics": uncalibrated_metrics,
            "domain_sample_count": dict(
                sorted(Counter(_source_domain(row) for row in calibration_rows).items())
            ),
            "logit_bias_by_domain": logit_bias_by_domain,
        },
        "selection": selection_metrics,
        "selection_breakdown": selection_breakdown,
        "training_runtime": _trainer_runtime_record(trainer, train_result),
        "test": {
            "sample_count": 0,
            "status": "SEALED_UNTIL_CANDIDATE_LOCK",
        },
        "trainable_parameter_count": _parameter_counts(trained_model)[0],
        "total_parameter_count": _parameter_counts(trained_model)[1],
    }
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    with args.report_path.open("x", encoding="utf-8") as file:
        file.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False))


def _load_public_rows(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8-sig", newline="") as file:
        return [
            {
                "text": row["document"],
                "label": SOURCE_LABEL[row["label"]],
                "source_type": "NEWS",
            }
            for row in csv.DictReader(file, delimiter="\t")
            if row.get("document") and row.get("label") in SOURCE_LABEL
        ]


def _verify_base_model_weights() -> Path:
    cached = Path(
        hf_hub_download(
            repo_id=BASE_MODEL,
            filename=BASE_MODEL_WEIGHT_FILENAME,
            revision=BASE_MODEL_REVISION,
        )
    )
    try:
        resolved = cached.resolve(strict=True)
    except OSError as exception:
        raise RuntimeError("KF-DeBERTa base weight cache를 확인할 수 없습니다.") from exception
    if not resolved.is_file() or _sha256(resolved) != BASE_MODEL_WEIGHT_SHA256:
        raise RuntimeError("KF-DeBERTa base weight SHA-256이 고정 provenance와 다릅니다.")
    return resolved


def _target_security(row: dict[str, Any]) -> str:
    stock_name = row.get("stock_name")
    if isinstance(stock_name, str) and stock_name.strip():
        return stock_name.strip()
    target = row.get("target_security")
    if isinstance(target, dict):
        value = target.get("name") or target.get("identifier")
        return str(value).strip() if value else ""
    return str(target).strip() if isinstance(target, str) else ""


def _load_reviewed_rows(path: Path, partition: str, *, weight: float) -> list[dict[str, Any]]:
    if not path.exists():
        raise SystemExit(f"Codex 검수 감성 데이터가 없습니다: {path}")
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            payload = json.loads(line)
            if payload.get("partition") != partition:
                raise SystemExit(f"검수 파티션 계약 위반: {path}")
            if (
                payload.get("schema_version") != GOLD_SCHEMA_VERSION
                or payload.get("review_status") != "CODEX_REVIEW_APPROVED"
                or payload.get("sentiment") not in LABEL_ORDER
                or not payload.get("reviewer_id")
                or not payload.get("reviewed_at")
            ):
                raise SystemExit(f"미검수 행이 포함되어 있습니다: {path}")
            rows.append(
                {
                    **payload,
                    "label": str(payload["sentiment"]),
                    "source_type": str(payload.get("source_type", "NEWS")),
                    "sample_weight": weight,
                }
            )
    if not rows:
        raise SystemExit(f"검수 완료 행이 없습니다: {path}")
    return rows


def _load_auxiliary_training_rows(
    path: Path,
    report_path: Path,
    source_type: str,
    *,
    weight: float,
) -> list[dict[str, Any]]:
    report = _read_json_object(report_path, "auxiliary training report")
    gold_rows = _read_jsonl_objects(path, "auxiliary training Gold")
    source = report.get("source")
    reclassification = report.get("reclassification")
    integrity = report.get("integrity")
    lineage = report.get("lineage")
    if (
        report.get("schema_version") != AUXILIARY_REPORT_SCHEMA_VERSION
        or not isinstance(source, dict)
        or source.get("source_type") != source_type
        or isinstance(source.get("sample_count"), bool)
        or not isinstance(source.get("sample_count"), int)
        or source.get("sample_count") != len(gold_rows)
        or not isinstance(reclassification, dict)
        or reclassification.get("previous_role")
        != "REPEATEDLY_EXPOSED_DIAGNOSTIC_NOT_CLAIM_EVIDENCE"
        or reclassification.get("new_role") != AUXILIARY_TRAINING_ROLE
        or reclassification.get("eligible_for_confirmatory_metrics") is not False
        or reclassification.get("eligible_for_superiority_claims") is not False
        or not isinstance(integrity, dict)
        or integrity.get("exact_item_set") is not True
        or integrity.get("independent_dual_review_required") is not True
        or integrity.get("model_blind") is not True
        or integrity.get("market_blind") is not True
        or integrity.get("confirmatory_group_overlap_count") != 0
        or integrity.get("write_once") is not True
        or not isinstance(lineage, dict)
    ):
        raise SystemExit(f"Auxiliary training report contract violation: {report_path}")

    output_record = lineage.get("output")
    review_record = lineage.get("review")
    decision_record = lineage.get("dual_decisions")
    sampling_record = lineage.get("confirmatory_sampling_design")
    reservations = lineage.get("confirmatory_reservations")
    if not isinstance(reservations, dict):
        raise SystemExit(f"Auxiliary training report lineage violation: {report_path}")
    _validate_auxiliary_artifact_record(output_record, path, "output")
    review_path = _validated_lineage_artifact(review_record, report_path, "review")
    decisions_path = _validated_lineage_artifact(decision_record, report_path, "dual decisions")
    sampling_path = _validated_lineage_artifact(
        sampling_record, report_path, "confirmatory sampling design"
    )
    news_reservation = _validated_lineage_artifact(
        reservations.get("NEWS"), report_path, "NEWS confirmatory reservation"
    )
    disclosure_reservation = _validated_lineage_artifact(
        reservations.get("DISCLOSURE"),
        report_path,
        "DISCLOSURE confirmatory reservation",
    )

    review_rows = _read_jsonl_objects(review_path, "historical review")
    decision_rows = _read_jsonl_objects(decisions_path, "historical dual decisions")
    news_confirmatory = _read_jsonl_objects(news_reservation, "NEWS confirmatory reservation")
    disclosure_confirmatory = _read_jsonl_objects(
        disclosure_reservation, "DISCLOSURE confirmatory reservation"
    )
    sampling = _read_json_object(sampling_path, "confirmatory sampling design")
    _validate_auxiliary_sampling_lineage(
        sampling,
        review_record=review_record,
        reservations={"NEWS": reservations["NEWS"], "DISCLOSURE": reservations["DISCLOSURE"]},
    )
    assert_sentiment_groups_disjoint(
        {
            "AUXILIARY_TRAINING_SOURCE": review_rows,
            "NEWS_CONFIRMATORY": news_confirmatory,
            "DISCLOSURE_CONFIRMATORY": disclosure_confirmatory,
        }
    )

    review_order = [_auxiliary_item_id(row) for row in review_rows]
    review_by_id = dict(zip(review_order, review_rows, strict=True))
    decision_by_id = {str(row.get("item_id", "")).strip(): row for row in decision_rows}
    gold_by_id = {str(row.get("item_id", "")).strip(): row for row in gold_rows}
    if (
        len(review_by_id) != len(review_rows)
        or len(decision_by_id) != len(decision_rows)
        or len(gold_by_id) != len(gold_rows)
        or set(review_by_id) != set(decision_by_id)
    ):
        raise SystemExit(f"Auxiliary training lineage item-set violation: {path}")
    eligible_order: list[str] = []
    unresolved_order: list[str] = []
    for item_id in review_order:
        if _validate_auxiliary_decision(decision_by_id[item_id], item_id):
            eligible_order.append(item_id)
        else:
            unresolved_order.append(item_id)
    _validate_auxiliary_subset_report(
        source,
        integrity,
        source_type=source_type,
        review_count=len(review_rows),
        gold_count=len(gold_rows),
        unresolved_count=len(unresolved_order),
        report_path=report_path,
    )
    if set(gold_by_id) != set(eligible_order):
        raise SystemExit(f"Auxiliary training eligible item-set violation: {path}")
    if list(gold_by_id) != eligible_order:
        raise SystemExit(f"Auxiliary training row-order provenance violation: {path}")

    promoted_at = _aware_training_datetime(report.get("generated_at"), "report.generated_at")
    sampling_at = _aware_training_datetime(sampling.get("generated_at"), "sampling.generated_at")
    if promoted_at <= sampling_at:
        raise SystemExit(f"Auxiliary training promotion predates reservation: {report_path}")
    rows: list[dict[str, Any]] = []
    for line_number, payload in enumerate(gold_rows, start=1):
        item_id = str(payload.get("item_id", "")).strip()
        source_row = review_by_id[item_id]
        decision = decision_by_id[item_id]
        source_hash = _canonical_json_sha256(source_row)
        decision_hash = _canonical_json_sha256(decision)
        provenance = {
            "item_id": item_id,
            "source_record_sha256": source_hash,
            "dual_decision_sha256": decision_hash,
            "training_role": AUXILIARY_TRAINING_ROLE,
        }
        source_fields_match = all(
            payload.get(name) == value
            for name, value in source_row.items()
            if name
            not in {
                "schema_version",
                "partition",
                "review_status",
                "final_sentiment",
                "reviewer_id",
                "reviewed_at",
                "review_note",
            }
        )
        decision_fields_match = all(
            payload.get(name) == decision.get(name)
            for name in (
                "reviewer_id",
                "reviewed_at",
                "review_note",
                "independent_reviewer_count",
                "inter_reviewer_agreement",
                "decision_path",
                "reviewer_1",
                "reviewer_2",
                "adjudication",
            )
        )
        if (
            payload.get("schema_version") != AUXILIARY_GOLD_SCHEMA_VERSION
            or payload.get("partition") != "AUXILIARY_TRAINING_GOLD"
            or payload.get("source_partition") != source.get("partition")
            or payload.get("source_type") != source_type
            or payload.get("review_status") != "CODEX_REVIEW_APPROVED"
            or payload.get("sentiment") != decision.get("final_sentiment")
            or payload.get("final_sentiment") != decision.get("final_sentiment")
            or payload.get("sentiment") not in LABEL_ORDER
            or payload.get("label_quality") != "INDEPENDENT_DUAL_CODEX_GOLD"
            or payload.get("model_blind") is not True
            or payload.get("market_blind") is not True
            or payload.get("training_role") != AUXILIARY_TRAINING_ROLE
            or payload.get("promoted_at") != report.get("generated_at")
            or payload.get("source_record_sha256") != source_hash
            or payload.get("dual_decision_sha256") != decision_hash
            or payload.get("promotion_provenance_sha256") != _canonical_json_sha256(provenance)
            or not source_fields_match
            or not decision_fields_match
        ):
            raise SystemExit(f"Auxiliary training Gold provenance violation: {path}:{line_number}")
        rows.append({**payload, "label": str(payload["sentiment"]), "sample_weight": weight})
    if not rows:
        raise SystemExit(f"Auxiliary training Gold is empty: {path}")
    expected_distribution = dict(
        sorted(Counter(str(row["sentiment"]) for row in gold_rows).items())
    )
    if source.get("label_distribution") != expected_distribution:
        raise SystemExit(f"Auxiliary training label distribution mismatch: {report_path}")
    return rows


def _validate_auxiliary_decision(decision: dict[str, Any], item_id: str) -> bool:
    left = decision.get("reviewer_1")
    right = decision.get("reviewer_2")
    final_sentiment = decision.get("final_sentiment")
    unresolved = final_sentiment == AUXILIARY_UNRESOLVED_LABEL
    if (
        set(decision) != AUXILIARY_DECISION_FIELDS
        or decision.get("schema_version") != "k-fnspid-sentiment-dual-review-decision/v1"
        or decision.get("item_id") != item_id
        or final_sentiment not in {*LABEL_ORDER, AUXILIARY_UNRESOLVED_LABEL}
        or decision.get("review_status")
        != ("UNRESOLVED" if unresolved else "CODEX_REVIEW_APPROVED")
        or decision.get("reviewer_type") != "INDEPENDENT_CODEX_AI"
        or decision.get("independent_reviewer_count") != 2
        or not isinstance(decision.get("inter_reviewer_agreement"), bool)
        or decision.get("model_blind") is not True
        or decision.get("market_blind") is not True
        or not isinstance(left, dict)
        or not isinstance(right, dict)
        or set(left) != AUXILIARY_REVIEWER_FIELDS
        or set(right) != AUXILIARY_REVIEWER_FIELDS
        or left.get("reviewer_id") == right.get("reviewer_id")
        or any(
            reviewer.get("reviewer_type") != "CODEX_AI"
            or reviewer.get("final_sentiment") not in LABEL_ORDER
            or reviewer.get("model_blind") is not True
            or reviewer.get("market_blind") is not True
            or reviewer.get("stage_1")
            != ("NEUTRAL" if reviewer.get("final_sentiment") == "NEUTRAL" else "DIRECTIONAL")
            or reviewer.get("stage_2")
            != (
                reviewer.get("final_sentiment")
                if reviewer.get("final_sentiment") != "NEUTRAL"
                else "NOT_APPLICABLE"
            )
            or reviewer.get("decision_path") != "NEUTRAL_DIRECTIONAL_THEN_POLARITY"
            or not str(reviewer.get("reviewer_id", "")).strip()
            or not str(reviewer.get("label_evidence", "")).strip()
            for reviewer in (left, right)
        )
        or not str(decision.get("reviewer_id", "")).strip()
        or not str(decision.get("review_note", "")).strip()
    ):
        raise SystemExit(f"Auxiliary dual-review decision violation: {item_id}")
    left_time = _aware_training_datetime(left.get("reviewed_at"), "reviewer_1.reviewed_at")
    right_time = _aware_training_datetime(right.get("reviewed_at"), "reviewer_2.reviewed_at")
    terminal_time = max(left_time, right_time)
    agreement = decision["inter_reviewer_agreement"]
    adjudication = decision.get("adjudication")
    if agreement:
        valid = (
            not unresolved
            and left.get("final_sentiment") == right.get("final_sentiment")
            and decision.get("final_sentiment") == left.get("final_sentiment")
            and decision.get("decision_path") == "INDEPENDENT_REVIEWER_AGREEMENT"
            and adjudication is None
        )
    else:
        expected_path = "UNRESOLVED_EXCLUDED" if unresolved else "ADJUDICATED"
        expected_status = "UNRESOLVED" if unresolved else "CODEX_ADJUDICATED"
        adjudicator_id = (
            str(adjudication.get("adjudicator_id", "")).strip()
            if isinstance(adjudication, dict)
            else ""
        )
        valid = (
            left.get("final_sentiment") != right.get("final_sentiment")
            and decision.get("decision_path") == expected_path
            and isinstance(adjudication, dict)
            and set(adjudication) == AUXILIARY_ADJUDICATION_FIELDS
            and adjudication.get("item_id") == item_id
            and adjudication.get("final_sentiment") == decision.get("final_sentiment")
            and adjudication.get("adjudication_status") == expected_status
            and bool(adjudicator_id)
            and adjudicator_id not in {left.get("reviewer_id"), right.get("reviewer_id")}
            and bool(str(adjudication.get("adjudication_note", "")).strip())
            and decision.get("reviewer_id") == adjudicator_id
            and decision.get("review_note") == adjudication.get("adjudication_note")
        )
        if valid and isinstance(adjudication, dict):
            adjudicated_at = _aware_training_datetime(
                adjudication.get("adjudicated_at"), "adjudication.adjudicated_at"
            )
            valid = adjudicated_at >= terminal_time
            terminal_time = adjudicated_at
    decision_time = _aware_training_datetime(decision.get("reviewed_at"), "decision.reviewed_at")
    valid = valid and decision_time == terminal_time
    if not valid:
        raise SystemExit(f"Auxiliary dual-review decision path violation: {item_id}")
    return not unresolved


def _validate_auxiliary_subset_report(
    source: dict[str, Any],
    integrity: dict[str, Any],
    *,
    source_type: str,
    review_count: int,
    gold_count: int,
    unresolved_count: int,
    report_path: Path,
) -> None:
    count_fields = {"review_sample_count", "excluded_unresolved_count"}
    present_fields = count_fields.intersection(source)
    flag_present = "unresolved_rows_excluded" in integrity
    new_contract = present_fields == count_fields and flag_present
    old_disclosure_contract = not present_fields and not flag_present
    if new_contract:
        review_sample_count = source.get("review_sample_count")
        excluded_count = source.get("excluded_unresolved_count")
        valid = (
            isinstance(review_sample_count, int)
            and not isinstance(review_sample_count, bool)
            and isinstance(excluded_count, int)
            and not isinstance(excluded_count, bool)
            and review_sample_count == review_count
            and source.get("sample_count") == gold_count
            and excluded_count == unresolved_count
            and review_sample_count == gold_count + excluded_count
            and integrity.get("unresolved_rows_excluded") is True
        )
    else:
        valid = (
            old_disclosure_contract
            and source_type == "DISCLOSURE"
            and unresolved_count == 0
            and review_count == gold_count
            and source.get("sample_count") == gold_count
        )
    if not valid:
        raise SystemExit(f"Auxiliary unresolved exclusion contract violation: {report_path}")


def _validate_auxiliary_artifact_record(record: object, expected_path: Path, label: str) -> None:
    if not isinstance(record, dict):
        raise SystemExit(f"Auxiliary lineage record is missing: {label}")
    resolved = expected_path.resolve()
    raw_path = record.get("path")
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise SystemExit(f"Auxiliary lineage path is invalid: {label}")
    candidate = Path(raw_path)
    recorded_path = (
        candidate.resolve() if candidate.is_absolute() else (PROJECT_ROOT / candidate).resolve()
    )
    if (
        recorded_path != resolved
        or record.get("bytes") != resolved.stat().st_size
        or record.get("sha256") != _sha256(resolved)
    ):
        raise SystemExit(f"Auxiliary lineage artifact mismatch: {label}")


def _validated_lineage_artifact(record: object, report_path: Path, label: str) -> Path:
    if not isinstance(record, dict):
        raise SystemExit(f"Auxiliary lineage record is missing: {label}")
    resolved = _lineage_record_path(record, report_path)
    _require_regular_input(resolved, f"auxiliary lineage {label}")
    if record.get("bytes") != resolved.stat().st_size or record.get("sha256") != _sha256(resolved):
        raise SystemExit(f"Auxiliary lineage artifact mismatch: {label}")
    return resolved


def _lineage_record_path(record: dict[str, Any], report_path: Path) -> Path:
    raw_path = record.get("path")
    if not isinstance(raw_path, str) or not raw_path.strip():
        raise SystemExit(f"Auxiliary lineage path is invalid: {report_path}")
    candidate = Path(raw_path)
    resolved = (
        candidate.resolve() if candidate.is_absolute() else (PROJECT_ROOT / candidate).resolve()
    )
    if report_path.resolve().is_relative_to(PROJECT_ROOT.resolve()):
        try:
            resolved.relative_to(PROJECT_ROOT.resolve())
        except ValueError as exception:
            raise SystemExit("Auxiliary lineage path escapes project root.") from exception
    return resolved


def _validate_auxiliary_sampling_lineage(
    sampling: dict[str, Any],
    *,
    review_record: object,
    reservations: dict[str, object],
) -> None:
    if (
        sampling.get("schema_version")
        not in {
            "k-fnspid-sentiment-confirmatory-sealed-sampling-design/v1",
            "k-fnspid-sentiment-confirmatory-sealed-sampling-design/v2",
        }
        or sampling.get("report_role") != "UNLABELED_CONFIRMATORY_RESERVATION"
        or sampling.get("labels_available_at_reservation") is not False
        or sampling.get("candidate_predictions_available") is not False
    ):
        raise SystemExit("Auxiliary confirmatory sampling contract violation.")
    partitions = sampling.get("partitions")
    commitments = sampling.get("write_once_commitments")
    if not isinstance(partitions, dict) or not isinstance(commitments, dict):
        raise SystemExit("Auxiliary confirmatory commitments are missing.")
    for source, partition in (
        ("NEWS", "CONFIRMATORY_SEALED_TEST_REVIEW"),
        ("DISCLOSURE", "DISCLOSURE_CONFIRMATORY_SEALED_TEST_REVIEW"),
    ):
        reservation = reservations[source]
        details = partitions.get(partition)
        if (
            not isinstance(reservation, dict)
            or not isinstance(details, dict)
            or details.get("source_type") != source
            or details.get("output") != reservation
            or commitments.get(partition) != reservation
        ):
            raise SystemExit(f"Auxiliary confirmatory commitment mismatch: {source}")
    protected = sampling.get("protected_identity_sets")
    categories = protected.get("categories") if isinstance(protected, dict) else None
    protected_records: list[object] = []
    if isinstance(categories, dict):
        for category in categories.values():
            if isinstance(category, dict) and isinstance(category.get("paths"), list):
                protected_records.extend(category["paths"])
    if review_record not in protected_records:
        raise SystemExit("Auxiliary source review was not protected at reservation time.")


def _read_jsonl_objects(path: Path, label: str) -> list[dict[str, Any]]:
    _require_regular_input(path, label)
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise SystemExit(f"JSONL row is not an object: {path}:{line_number}")
            rows.append(value)
    return rows


def _read_json_object(path: Path, label: str) -> dict[str, Any]:
    _require_regular_input(path, label)
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"JSON document is not an object: {path}")
    return value


def _auxiliary_item_id(row: dict[str, Any]) -> str:
    document_id = str(row.get("document_id", "")).strip()
    stock_code = str(row.get("stock_code", "")).strip()
    if not document_id or not stock_code:
        raise SystemExit("Auxiliary source identity is missing.")
    return f"{document_id}::{stock_code}"


def _canonical_json_sha256(value: object) -> str:
    return sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _prepared_partition_commitments(
    *,
    train_rows: list[dict[str, Any]],
    checkpoint_rows: list[dict[str, Any]],
    calibration_rows: list[dict[str, Any]],
    selection_rows: list[dict[str, Any]],
    news_reservation: list[dict[str, Any]],
    disclosure_reservation: list[dict[str, Any]],
) -> dict[str, dict[str, int | str]]:
    return {
        "TRAIN": _rows_commitment(train_rows, include_label=True),
        "CHECKPOINT": _rows_commitment(checkpoint_rows, include_label=True),
        "CALIBRATION": _rows_commitment(calibration_rows, include_label=True),
        "SELECTION": _rows_commitment(selection_rows, include_label=True),
        "NEWS_CONFIRMATORY_RESERVATION": _rows_commitment(
            news_reservation,
            include_label=False,
        ),
        "DISCLOSURE_CONFIRMATORY_RESERVATION": _rows_commitment(
            disclosure_reservation,
            include_label=False,
        ),
    }


def _rows_commitment(
    rows: list[dict[str, Any]],
    *,
    include_label: bool,
) -> dict[str, int | str]:
    records: list[dict[str, Any]] = []
    for row in rows:
        provenance = sentiment_provenance(row)
        record: dict[str, Any] = {
            "canonical_url": provenance.canonical_url,
            "normalized_text_sha256": sha256(
                provenance.normalized_text.encode("utf-8")
            ).hexdigest(),
            "raw_text_sha256": sha256(str(row.get("text", "")).encode("utf-8")).hexdigest(),
            "content_hash": provenance.content_hash,
            "event_cluster_id": provenance.event_cluster_id,
            "document_id": str(row.get("document_id", "")),
            "item_id": str(row.get("item_id", "")),
            "source_record_sha256": str(row.get("source_record_sha256", "")),
            "source_type": str(row.get("source_type", "")).upper(),
            "stock_code": str(row.get("stock_code", "")).strip(),
            "stock_name": str(row.get("stock_name", "")).strip(),
            "stock_aliases": list(_stock_aliases(row)),
            "target_security": _target_security(row),
        }
        if include_label:
            record.update(
                {
                    "label": str(row["label"]),
                    "dataset": str(row.get("dataset", "")),
                    "sample_weight": _sample_weight(row),
                    "augmentation_method": str(row.get("augmentation_method", "")),
                    "augmentation_parent_sha256": str(
                        row.get("augmentation_parent_sha256", "")
                    ),
                    "target_swap_absence_contract": str(
                        row.get("target_swap_absence_contract", "")
                    ),
                    "target_swap_absence_tokens": list(
                        row.get("target_swap_absence_tokens", ())
                    ),
                }
            )
        records.append(record)
    records.sort(
        key=lambda record: json.dumps(
            record,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return {"row_count": len(rows), "sha256": _canonical_json_sha256(records)}


def _aware_training_datetime(value: object, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exception:
        raise SystemExit(f"Auxiliary timestamp is invalid: {field}") from exception
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise SystemExit(f"Auxiliary timestamp lacks timezone: {field}")
    return parsed


def _load_sealed_reservation_rows(
    path: Path,
    partition: str,
    source_type: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            payload = json.loads(line)
            if (
                payload.get("schema_version") != "k-fnspid-sentiment-review-row/v1"
                or payload.get("partition") != partition
                or payload.get("source_type") != source_type
                or payload.get("review_status") != "NEEDS_BLIND_REVIEW"
                or payload.get("final_sentiment") not in {"", None}
            ):
                raise SystemExit(f"봉인 reservation 계약 위반: {path}:{line_number}")
            rows.append(
                {
                    "text": str(payload.get("text", "")),
                    "source_url": str(payload.get("source_url", "")),
                    "canonical_url": str(payload.get("canonical_url", "")),
                    "content_hash": str(payload.get("content_hash", "")),
                    "event_cluster_id": str(payload.get("event_cluster_id", "")),
                }
            )
    if len(rows) < 500:
        raise SystemExit(f"봉인 reservation이 500행보다 작습니다: {path}")
    return rows


def _require_regular_input(path: Path, label: str) -> None:
    if path.is_symlink() or not path.is_file():
        raise SystemExit(f"학습 입력 파일이 없거나 symlink입니다: {label}={path}")


def _input_artifact_record(path: Path) -> dict[str, int | str]:
    _require_regular_input(path, "provenance")
    resolved = path.resolve()
    try:
        display_path = str(resolved.relative_to(PROJECT_ROOT))
    except ValueError:
        display_path = str(resolved)
    return {
        "path": display_path,
        "bytes": resolved.stat().st_size,
        "sha256": _sha256(resolved),
    }


def _load_silver_rows(
    path: Path,
    protected_rows: list[dict[str, Any]],
    per_label: int,
    seed: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            payload = json.loads(line)
            if (
                payload.get("label_provenance") != "STRICT_RULE_SILVER_V1"
                or payload.get("review_status") != "UNREVIEWED_SILVER"
                or payload.get("sentiment") not in LABEL_ORDER
            ):
                continue
            rows.append(
                {
                    **payload,
                    "label": str(payload["sentiment"]),
                    "sample_weight": float(payload["sample_weight"]),
                }
            )
    filtered, overlap_audit = purge_sentiment_group_overlap(rows, protected_rows)
    selected = _per_label_limit(filtered, per_label, seed)
    return selected, {
        "path": str(path.relative_to(PROJECT_ROOT)),
        "sha256": _sha256(path),
        "input_count": len(rows),
        "group_overlap_purge": overlap_audit,
        "selected_count": len(selected),
        "selected_label_distribution": _label_distribution(selected),
        "label_role": "low_weight_silver_not_gold",
    }


def _load_legacy_protected_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    from hannah_montana_ai.training.dataset import load_labeled_alerts

    for path in LEGACY_EVALUATION_PATHS:
        for sample in load_labeled_alerts(path):
            rows.append(
                {
                    "text": sample.text,
                    "source_url": sample.source_url,
                    "content_hash": sample.content_hash,
                    "event_cluster_id": sample.event_cluster_id,
                }
            )
    return rows


def _deduplicate_weighted(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(rows, key=lambda row: float(row.get("sample_weight", 1.0)), reverse=True)
    selected: list[dict[str, Any]] = []
    seen_texts: set[str] = set()
    seen_groups: set[tuple[str, str]] = set()
    for row in ordered:
        text_key = normalized_sentiment_text(str(row["text"]))
        group_keys = sentiment_provenance(row).group_keys - {("normalized_text", text_key)}
        if not text_key or text_key in seen_texts or group_keys & seen_groups:
            continue
        selected.append(row)
        seen_texts.add(text_key)
        seen_groups.update(group_keys)
    return selected


def build_target_swap_hard_negatives(
    rows: list[dict[str, Any]],
    *,
    per_source: int,
    seed: int,
) -> list[dict[str, Any]]:
    """문서에 없는 다른 상장사를 대상으로 바꿔 오귀속 NEUTRAL을 생성한다."""
    if per_source < 0:
        raise ValueError("target-swap 표본 수는 음수일 수 없습니다.")
    if per_source == 0:
        return []
    aliases_by_target: dict[tuple[str, str], set[str]] = {}
    for row in rows:
        code = str(row.get("stock_code", "")).strip()
        name = str(row.get("stock_name", "")).strip()
        if len(name) < 2:
            continue
        aliases_by_target.setdefault((code, name), set()).update(_stock_aliases(row))
    target_pool = [
        (code, name, tuple(sorted(aliases)))
        for (code, name), aliases in sorted(
            aliases_by_target.items(),
            key=lambda item: (item[0][1], item[0][0]),
        )
    ]
    if len(target_pool) < 2:
        return []

    selected: list[dict[str, Any]] = []
    for source_index, source in enumerate(("NEWS", "DISCLOSURE")):
        candidates = sorted(
            (
                row
                for row in rows
                if str(row.get("source_type", "")).upper() == source
                and row.get("label") in {"NEGATIVE", "POSITIVE"}
                and str(row.get("stock_name", "")).strip()
            ),
            key=_augmentation_row_key,
        )
        generator = random.Random(  # noqa: S311  # nosec B311 - 재현 가능한 증강 순서
            seed + 10_003 * (source_index + 1)
        )
        generator.shuffle(candidates)
        donor_offset = generator.randrange(len(target_pool))
        source_selected = 0
        for candidate_index, row in enumerate(candidates):
            normalized_text = normalized_sentiment_text(str(row.get("text", "")))
            original_code = str(row.get("stock_code", "")).strip()
            original_name = str(row.get("stock_name", "")).strip()
            donor: tuple[str, str, tuple[str, ...], tuple[str, ...]] | None = None
            for step in range(len(target_pool)):
                proposed = target_pool[(donor_offset + candidate_index + step) % len(target_pool)]
                proposed_code, proposed_name, proposed_aliases = proposed
                absence_tokens = tuple(
                    sorted(
                        {
                            token
                            for value in (proposed_name, proposed_code, *proposed_aliases)
                            if (token := normalized_sentiment_text(value))
                        }
                    )
                )
                if (
                    proposed_name != original_name
                    and (
                        not proposed_code
                        or not original_code
                        or proposed_code != original_code
                    )
                    and absence_tokens
                    and all(token not in normalized_text for token in absence_tokens)
                ):
                    donor = (*proposed, absence_tokens)
                    break
            if donor is None:
                continue
            donor_code, donor_name, donor_aliases, absence_tokens = donor
            selected.append(
                {
                    **row,
                    "stock_code": donor_code,
                    "stock_name": donor_name,
                    "stock_aliases": list(donor_aliases),
                    "target_security": {
                        "identifier": donor_code,
                        "name": donor_name,
                        "aliases": list(donor_aliases),
                    },
                    "label": "NEUTRAL",
                    "sample_weight": TARGET_SWAP_WEIGHT,
                    "dataset": "K_FNSPID_TARGET_SWAP_HARD_NEGATIVE",
                    "augmentation_method": "ABSENT_TARGET_SWAP_V2",
                    "augmentation_parent_sha256": _augmentation_row_key(row),
                    "target_swap_donor_provenance": {
                        "stock_code": donor_code,
                        "stock_name": donor_name,
                        "stock_aliases": list(donor_aliases),
                    },
                    "target_swap_absence_tokens": list(absence_tokens),
                    "target_swap_absence_contract": "name-code-all-aliases-normalized/v2",
                }
            )
            source_selected += 1
            if source_selected >= per_source:
                break
    return selected


def _stock_aliases(row: dict[str, Any]) -> tuple[str, ...]:
    values: list[object] = [row.get("stock_aliases", ())]
    target = row.get("target_security")
    if isinstance(target, dict):
        values.append(target.get("aliases", ()))
    aliases: set[str] = set()
    for value in values:
        candidates = value if isinstance(value, list | tuple | set | frozenset) else (value,)
        for candidate in candidates:
            alias = str(candidate or "").strip()
            if alias:
                aliases.add(alias)
    return tuple(sorted(aliases))


def _augmentation_row_key(row: dict[str, Any]) -> str:
    payload = {
        "document_id": row.get("document_id", ""),
        "source_type": row.get("source_type", ""),
        "stock_code": row.get("stock_code", ""),
        "stock_name": row.get("stock_name", ""),
        "content_hash": row.get("content_hash", ""),
        "event_cluster_id": row.get("event_cluster_id", ""),
        "text": row.get("text", ""),
    }
    return sha256(
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


def _per_label_limit(rows: list[dict[str, Any]], per_label: int, seed: int) -> list[dict[str, Any]]:
    generator = random.Random(seed)  # noqa: S311  # nosec B311 - 재현 가능한 층화 추출
    selected: list[dict[str, Any]] = []
    for label in LABEL_ORDER:
        bucket = [row for row in rows if row["label"] == label]
        generator.shuffle(bucket)
        selected.extend(bucket[:per_label])
    generator.shuffle(selected)
    return selected


def _stratified_limit(rows: list[dict[str, Any]], limit: int, seed: int) -> list[dict[str, Any]]:
    if len(rows) <= limit:
        return rows
    generator = random.Random(seed)  # noqa: S311  # nosec B311 - 재현 가능한 층화 추출
    selected: list[dict[str, Any]] = []
    for label in LABEL_ORDER:
        bucket = [row for row in rows if row["label"] == label]
        generator.shuffle(bucket)
        selected.extend(bucket[: round(limit * len(bucket) / len(rows))])
    generator.shuffle(selected)
    return selected[:limit]


def _effective_number_weights(rows: list[dict[str, Any]]) -> torch.Tensor:
    beta = 0.9995
    log_beta = math.log(beta)
    masses = {
        label: math.fsum(_sample_weight(row) for row in rows if str(row["label"]) == label)
        for label in LABEL_ORDER
    }
    if any(not math.isfinite(mass) or mass <= 0.0 for mass in masses.values()):
        raise ValueError("모든 감성 라벨의 유효 가중치 합이 양수여야 합니다.")
    values = [
        (1.0 - beta) / -math.expm1(masses[label] * log_beta) for label in LABEL_ORDER
    ]
    normalizer = len(values) / math.fsum(values)
    return torch.tensor([value * normalizer for value in values], dtype=torch.float32)


def _sample_weight(row: dict[str, Any]) -> float:
    value = row.get("sample_weight", 1.0)
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ValueError("학습 sample_weight는 유한한 양수여야 합니다.")
    weight = float(value)
    if not math.isfinite(weight) or weight <= 0.0:
        raise ValueError("학습 sample_weight는 유한한 양수여야 합니다.")
    return weight


def _training_weight_audit(rows: list[dict[str, Any]]) -> dict[str, Any]:
    def aggregate(group_rows: list[dict[str, Any]]) -> dict[str, dict[str, float | int]]:
        return {
            label: {
                "raw_count": sum(str(row["label"]) == label for row in group_rows),
                "effective_weight_sum": math.fsum(
                    _sample_weight(row) for row in group_rows if str(row["label"]) == label
                ),
            }
            for label in LABEL_ORDER
        }

    sources = sorted({str(row.get("source_type", "UNKNOWN")).upper() for row in rows})
    datasets = sorted({str(row.get("dataset", "UNKNOWN")) for row in rows})
    return {
        "total": {
            "raw_count": len(rows),
            "effective_weight_sum": math.fsum(_sample_weight(row) for row in rows),
        },
        "by_source_and_label": {
            source: aggregate(
                [row for row in rows if str(row.get("source_type", "UNKNOWN")).upper() == source]
            )
            for source in sources
        },
        "by_dataset_source_and_label": {
            dataset: {
                source: aggregate(
                    [
                        row
                        for row in rows
                        if str(row.get("dataset", "UNKNOWN")) == dataset
                        and str(row.get("source_type", "UNKNOWN")).upper() == source
                    ]
                )
                for source in sources
                if any(
                    str(row.get("dataset", "UNKNOWN")) == dataset
                    and str(row.get("source_type", "UNKNOWN")).upper() == source
                    for row in rows
                )
            }
            for dataset in datasets
        },
    }


def _trainer_runtime_record(trainer: Trainer, train_result: Any) -> dict[str, Any]:
    raw_metrics = getattr(train_result, "metrics", None)
    if not isinstance(raw_metrics, dict):
        raise RuntimeError("Trainer 학습 runtime 지표가 없습니다.")
    metrics: dict[str, float] = {}
    for name in ("train_runtime", "train_samples_per_second", "train_steps_per_second"):
        value = raw_metrics.get(name)
        if isinstance(value, bool) or not isinstance(value, int | float):
            raise RuntimeError(f"Trainer 학습 runtime 지표가 없습니다: {name}")
        numeric = float(value)
        if not math.isfinite(numeric) or numeric < 0.0:
            raise RuntimeError(f"Trainer 학습 runtime 지표가 올바르지 않습니다: {name}")
        metrics[name] = numeric
    return {
        "trainer_device": str(trainer.args.device),
        "global_step": int(trainer.state.global_step),
        **metrics,
    }


def _metrics(prediction: EvalPrediction) -> dict[str, float]:
    expected = np.asarray(prediction.label_ids).astype(int)
    raw = prediction.predictions
    logits = raw[0] if isinstance(raw, tuple) else raw
    predicted = np.asarray(logits).argmax(axis=-1)
    return {
        "accuracy": float(accuracy_score(expected, predicted)),
        "macro_f1": float(
            f1_score(
                expected,
                predicted,
                labels=range(len(LABEL_ORDER)),
                average="macro",
                zero_division=0,
            )
        ),
    }


def _evaluate_partition(
    trainer: Trainer,
    dataset: EncodedSentimentDataset,
    rows: list[dict[str, Any]],
    logit_bias_by_domain: dict[str, list[float]],
    prefix: str,
) -> dict[str, float | int]:
    output = trainer.predict(dataset, metric_key_prefix=prefix)
    expected = np.asarray(output.label_ids).astype(int)
    adjusted = _apply_logit_bias(_prediction_logits(output), rows, logit_bias_by_domain)
    predicted = adjusted.argmax(axis=-1)
    return {
        "accuracy": float(accuracy_score(expected, predicted)),
        "macro_f1": float(
            f1_score(
                expected,
                predicted,
                labels=range(len(LABEL_ORDER)),
                average="macro",
                zero_division=0,
            )
        ),
        "sample_count": len(dataset),
    }


def _evaluate_breakdown(
    trainer: Trainer,
    rows: list[dict[str, Any]],
    tokenizer: Any,
    max_length: int,
    logit_bias_by_domain: dict[str, list[float]],
) -> dict[str, dict[str, float | int]]:
    result: dict[str, dict[str, float | int]] = {}
    for dataset_name in sorted({str(row["dataset"]) for row in rows}):
        subset = [row for row in rows if row["dataset"] == dataset_name]
        result[dataset_name] = _evaluate_partition(
            trainer,
            EncodedSentimentDataset(subset, tokenizer, max_length),
            subset,
            logit_bias_by_domain,
            "breakdown",
        )
    return result


def _prediction_logits(output: Any) -> NDArray[np.float64]:
    raw = output.predictions
    values = raw[0] if isinstance(raw, tuple) else raw
    logits = np.asarray(values, dtype=np.float64)
    if logits.ndim != 2 or logits.shape[1] != len(LABEL_ORDER):
        raise ValueError("감성 예측 logit 형상이 올바르지 않습니다.")
    return logits


def _source_domain(row: dict[str, Any]) -> str:
    return sentiment_source_domain(str(row.get("source_type", "NEWS")), _target_security(row))


def _fit_logit_bias_by_domain(
    logits: NDArray[np.float64],
    rows: list[dict[str, Any]],
) -> dict[str, list[float]]:
    if len(logits) != len(rows):
        raise ValueError("감성 calibration logit과 행 수가 다릅니다.")
    result: dict[str, list[float]] = {}
    labels = np.asarray([LABEL_ORDER.index(str(row["label"])) for row in rows])
    for domain in SENTIMENT_LOGIT_BIAS_DOMAINS:
        indices = np.asarray(
            [index for index, row in enumerate(rows) if _source_domain(row) == domain]
        )
        if len(indices) < 30:
            result[domain] = [0.0] * len(LABEL_ORDER)
            continue
        counts = np.bincount(labels[indices], minlength=len(LABEL_ORDER)).astype(np.float64)
        if bool((counts < 5).any()):
            result[domain] = [0.0] * len(LABEL_ORDER)
            continue
        best: tuple[float, float, float] | None = None
        best_bias = np.zeros(len(LABEL_ORDER), dtype=np.float64)
        offsets = np.linspace(-1.5, 1.5, 31)
        for negative_offset in offsets:
            for positive_offset in offsets:
                bias = np.asarray([negative_offset, 0.0, positive_offset], dtype=np.float64)
                bias -= bias.mean()
                predicted = (logits[indices] + bias).argmax(axis=-1)
                macro_f1 = float(
                    f1_score(
                        labels[indices],
                        predicted,
                        labels=range(len(LABEL_ORDER)),
                        average="macro",
                        zero_division=0,
                    )
                )
                accuracy = float(accuracy_score(labels[indices], predicted))
                score = (macro_f1, accuracy, -float(np.square(bias).sum()))
                if best is None or score > best:
                    best = score
                    best_bias = bias
        result[domain] = [round(float(value), 8) for value in best_bias]
    validated_sentiment_logit_biases(result)
    return result


def _apply_logit_bias(
    logits: NDArray[np.float64],
    rows: list[dict[str, Any]],
    logit_bias_by_domain: dict[str, list[float]],
) -> NDArray[np.float64]:
    if len(logits) != len(rows):
        raise ValueError("감성 logit과 행 수가 다릅니다.")
    validated = validated_sentiment_logit_biases(logit_bias_by_domain)
    adjusted = logits.copy()
    for index, row in enumerate(rows):
        bias = validated[_source_domain(row)]
        adjusted[index] += np.asarray(bias, dtype=np.float64)
    return adjusted


def _selection_score(breakdown: dict[str, dict[str, float | int]]) -> float:
    required = (
        "PUBLIC_SELECTION",
        "K_FNSPID_DEVELOPMENT_SELECTION",
        "K_FNSPID_DISCLOSURE_DEVELOPMENT_SELECTION",
    )
    return min(float(breakdown[name]["macro_f1"]) for name in required)


def _label_distribution(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(str(row["label"]) for row in rows)
    return {label: counts[label] for label in LABEL_ORDER}


def _set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def _parameter_counts(model: Any) -> tuple[int, int]:
    trainable = 0
    total = 0
    for parameter in model.parameters():
        count = int(parameter.numel())
        total += count
        if bool(parameter.requires_grad):
            trainable += count
    return trainable, total


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    main()
