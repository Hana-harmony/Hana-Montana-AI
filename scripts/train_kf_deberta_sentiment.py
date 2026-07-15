from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn.functional as functional
from peft import LoraConfig, PeftModel, TaskType, get_peft_model
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
from hannah_montana_ai.training.dataset import load_labeled_alerts
from hannah_montana_ai.training.sentiment_protocol import (
    conflict_safe_deduplicate,
    decontaminate_public_partitions,
    label_distribution,
    load_disclosure_domain_partitions,
    normalized_sentiment_text,
    stratified_hash_split,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_MODEL = "kakaobank/kf-deberta-base"
BASE_MODEL_REVISION = "363b171d71443b0874b0bf9cea053eb5b1650633"
DATASET_REVISION = "7a8dc8cf6548a08e0a5dab3a12ad0fb8dccfd23f"
DEFAULT_DATASET = PROJECT_ROOT / "data/external/kf_deberta_benchmark"
DEFAULT_OUTPUT = PROJECT_ROOT / "src/hannah_montana_ai/model_store/kf_deberta_sentiment"
DEFAULT_REPORT = PROJECT_ROOT / "reports/kf-deberta-sentiment-training-report.json"
DISCLOSURE_DOMAIN_DATASET = PROJECT_ROOT / "data/training/financial_alert_full_content_gold.jsonl"
OPERATIONAL_TRAINING_PATHS = (
    PROJECT_ROOT / "data/training/financial_alert_augmented.jsonl",
    PROJECT_ROOT / "data/training/financial_alert_corpus.jsonl",
    PROJECT_ROOT / "data/training/financial_alert_news_style_augmented.jsonl",
    PROJECT_ROOT / "data/training/financial_alert_real_news_gold.jsonl",
    PROJECT_ROOT / "data/training/financial_alert_stock_review_gold.jsonl",
)
OPERATIONAL_EVALUATION_PATHS = (
    PROJECT_ROOT / "data/evaluation/financial_alert_eval.jsonl",
    PROJECT_ROOT / "data/evaluation/financial_alert_real_disclosure_gold.jsonl",
    PROJECT_ROOT / "data/evaluation/financial_alert_real_news_gold.jsonl",
    PROJECT_ROOT / "data/evaluation/financial_alert_stock_review_gold.jsonl",
)
LABEL_ORDER = ("NEGATIVE", "NEUTRAL", "POSITIVE")
SOURCE_LABEL = {"-1": "NEGATIVE", "0": "NEUTRAL", "1": "POSITIVE"}


class EncodedSentimentDataset(Dataset[dict[str, Any]]):
    def __init__(self, rows: list[dict[str, str]], tokenizer: Any, max_length: int) -> None:
        encoded = tokenizer(
            [row["text"] for row in rows],
            truncation=True,
            max_length=max_length,
        )
        self.features = [
            {
                **{name: values[index] for name, values in encoded.items()},
                "labels": LABEL_ORDER.index(row["label"]),
            }
            for index, row in enumerate(rows)
        ]

    def __len__(self) -> int:
        return len(self.features)

    def __getitem__(self, index: int) -> dict[str, Any]:
        return self.features[index]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="공개 한국 금융 뉴스 벤치마크로 KF-DeBERTa 감성 모델을 학습한다."
    )
    parser.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--parent-adapter-path", type=Path)
    parser.add_argument("--parent-report-path", type=Path)
    parser.add_argument("--max-length", type=int, default=192)
    parser.add_argument("--epochs", type=float, default=3.0)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--max-rows", type=int)
    parser.add_argument("--gradient-checkpointing", action="store_true")
    parser.add_argument("--domain-adaptation", action="store_true")
    parser.add_argument("--public-replay-limit", type=int, default=6_000)
    parser.add_argument("--disclosure-per-label-limit", type=int, default=800)
    parser.add_argument("--real-news-replay-multiplier", type=int, default=10)
    args = parser.parse_args()

    _set_seed(42)
    raw_partitions = {
        "TRAIN": _load_rows(args.dataset_dir / "ratings_train.csv"),
        "VALIDATION": _load_rows(args.dataset_dir / "ratings_val.csv"),
        "TEST": _load_rows(args.dataset_dir / "ratings_test.csv"),
    }
    partitions, public_leakage_audit = decontaminate_public_partitions(raw_partitions)
    public_validation_split = stratified_hash_split(
        partitions.pop("VALIDATION"),
        left_name="CALIBRATION",
        right_name="SELECTION",
    )
    partitions.update(public_validation_split)
    disclosure_partitions, disclosure_audit = load_disclosure_domain_partitions(
        DISCLOSURE_DOMAIN_DATASET,
        OPERATIONAL_EVALUATION_PATHS,
    )
    operational_rows, excluded_overlap_count = _load_operational_training_rows(
        OPERATIONAL_TRAINING_PATHS,
        OPERATIONAL_EVALUATION_PATHS,
        partitions["CALIBRATION"] + partitions["SELECTION"] + partitions["TEST"],
    )
    parent_version = ""
    parent_training_exposure_count = 0
    disclosure_training_rows = _per_label_limit(
        disclosure_partitions["TRAIN"], args.disclosure_per_label_limit, seed=79
    )
    if args.domain_adaptation:
        parent_adapter_path = args.parent_adapter_path or args.output_dir
        parent_report_path = args.parent_report_path or args.report_path
        metadata_path = parent_adapter_path / "hannah_metadata.json"
        if not metadata_path.exists():
            raise SystemExit("도메인 적응에는 기존 검증 어댑터가 필요하다.")
        parent_version = str(json.loads(metadata_path.read_text())["version"])
        if parent_report_path.exists():
            parent_report = json.loads(parent_report_path.read_text())
            parent_training_exposure_count = int(
                parent_report.get(
                    "cumulative_training_exposure_count",
                    parent_report["partition_count"]["TRAIN"],
                )
            )
        real_news_rows, _ = _load_operational_training_rows(
            (PROJECT_ROOT / "data/training/financial_alert_real_news_gold.jsonl",),
            OPERATIONAL_EVALUATION_PATHS,
            partitions["CALIBRATION"] + partitions["SELECTION"] + partitions["TEST"],
        )
        real_news_texts = {row["text"] for row in real_news_rows}
        other_operational_rows = [
            row for row in operational_rows if row["text"] not in real_news_texts
        ]
        partitions["TRAIN"] = (
            _stratified_limit(partitions["TRAIN"], args.public_replay_limit, seed=71)
            + _stratified_limit(other_operational_rows, 1_200, seed=73)
            + real_news_rows * args.real_news_replay_multiplier
            + disclosure_training_rows
        )
    else:
        partitions["TRAIN"] = _deduplicate_rows(
            partitions["TRAIN"] + operational_rows + disclosure_training_rows
        )
    if args.max_rows:
        partitions = {
            name: _stratified_limit(rows, args.max_rows, seed=42 + index)
            for index, (name, rows) in enumerate(partitions.items())
        }
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
    )
    if args.domain_adaptation:
        model = PeftModel.from_pretrained(
            model,
            args.parent_adapter_path or args.output_dir,
            is_trainable=True,
            use_safetensors=True,
        )
    else:
        model = get_peft_model(
            model,
            LoraConfig(
                task_type=TaskType.SEQ_CLS,
                r=16,
                lora_alpha=32,
                lora_dropout=0.1,
                target_modules=["query_proj", "key_proj", "value_proj"],
                modules_to_save=["pooler", "classifier"],
            ),
        )
    if args.gradient_checkpointing:
        model.gradient_checkpointing_enable()
        model.config.use_cache = False

    datasets = {
        name: EncodedSentimentDataset(rows, tokenizer, args.max_length)
        for name, rows in partitions.items()
    }
    class_weights = _class_weights(partitions["TRAIN"])
    optimizer_steps = max(1, round(len(datasets["TRAIN"]) * args.epochs / args.batch_size))
    run_dir = args.output_dir.parent / f".{args.output_dir.name}-checkpoints"
    trainer = Trainer(
        model=model,
        args=TrainingArguments(
            output_dir=str(run_dir),
            per_device_train_batch_size=args.batch_size,
            per_device_eval_batch_size=args.batch_size * 2,
            num_train_epochs=args.epochs,
            learning_rate=args.learning_rate,
            lr_scheduler_type="cosine",
            warmup_steps=max(1, round(optimizer_steps * 0.08)),
            weight_decay=0.01,
            gradient_checkpointing=args.gradient_checkpointing,
            eval_strategy="epoch",
            save_strategy="epoch",
            logging_steps=25,
            load_best_model_at_end=True,
            metric_for_best_model="macro_f1",
            greater_is_better=True,
            save_total_limit=2,
            seed=42,
            data_seed=42,
            report_to="none",
            dataloader_num_workers=0,
            dataloader_pin_memory=False,
        ),
        train_dataset=datasets["TRAIN"],
        eval_dataset=datasets["CALIBRATION"],
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
        processing_class=tokenizer,
        compute_loss_func=_loss_function(class_weights),
        compute_metrics=_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=1)],
    )
    trainer.train()
    trainer.remove_callback(EarlyStoppingCallback)
    validation = _clean_metrics(trainer.evaluate(datasets["CALIBRATION"]), "eval")
    selection = _clean_metrics(
        trainer.evaluate(datasets["SELECTION"], metric_key_prefix="selection"),
        "selection",
    )
    test = _clean_metrics(trainer.evaluate(datasets["TEST"], metric_key_prefix="test"), "test")
    disclosure_selection_dataset = EncodedSentimentDataset(
        disclosure_partitions["SELECTION"], tokenizer, args.max_length
    )
    disclosure_selection = _clean_metrics(
        trainer.evaluate(disclosure_selection_dataset, metric_key_prefix="disclosure_selection"),
        "disclosure_selection",
    )
    validation["sample_count"] = len(datasets["CALIBRATION"])
    selection["sample_count"] = len(datasets["SELECTION"])
    test["sample_count"] = len(datasets["TEST"])
    disclosure_selection["sample_count"] = len(disclosure_selection_dataset)

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
    version = f"kf-deberta-finance-sentiment-lora-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    metadata = {
        "version": version,
        "base_model": BASE_MODEL,
        "base_model_revision": BASE_MODEL_REVISION,
        "label_order": LABEL_ORDER,
        "max_length": args.max_length,
        "trained_at": datetime.now(UTC).isoformat(),
        "artifact_files": artifact_files,
    }
    (args.output_dir / "hannah_metadata.json").write_text(
        json.dumps(
            {"schema_version": "kf-deberta-sentiment-artifact/v1", **metadata},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    report = {
        "schema_version": "kf-deberta-sentiment-training/v1",
        **metadata,
        "dataset_source": "mssongit/finance-task:fnsentiment",
        "training_strategy": (
            "operational-domain-adaptation-with-public-replay"
            if args.domain_adaptation
            else "public-and-operational-multidomain"
        ),
        "parent_version": parent_version,
        "cumulative_training_exposure_count": (
            parent_training_exposure_count + len(partitions["TRAIN"])
        ),
        "dataset_revision": DATASET_REVISION,
        "dataset_files": {
            path.name: {"bytes": path.stat().st_size, "sha256": _sha256(path)}
            for path in sorted(args.dataset_dir.glob("ratings_*.csv"))
        },
        "operational_training_files": {
            str(path.relative_to(PROJECT_ROOT)): {
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
            for path in OPERATIONAL_TRAINING_PATHS
        },
        "operational_training_count": len(operational_rows),
        "domain_replay": {
            "public_limit": args.public_replay_limit,
            "real_news_multiplier": args.real_news_replay_multiplier,
        },
        "excluded_evaluation_overlap_count": excluded_overlap_count,
        "public_partition_leakage_audit": public_leakage_audit,
        "public_validation_protocol": {
            "method": "label-stratified-normalized-text-sha256/v1",
            "calibration_partition": "CALIBRATION",
            "candidate_selection_partition": "SELECTION",
            "test_partition": "TEST",
        },
        "disclosure_domain_dataset": {
            "path": str(DISCLOSURE_DOMAIN_DATASET.relative_to(PROJECT_ROOT)),
            "label_provenance": "RULE_WEAK_SUPERVISION_V2",
            "gold_used_for_training": False,
            "audit": disclosure_audit,
            "partition_count": {name: len(rows) for name, rows in disclosure_partitions.items()},
            "training_selection": {
                "method": "per-label-cap/v1",
                "per_label_limit": args.disclosure_per_label_limit,
                "selected_count": len(disclosure_training_rows),
                "selected_label_distribution": label_distribution(disclosure_training_rows),
            },
            "label_distribution": {
                name: label_distribution(rows) for name, rows in disclosure_partitions.items()
            },
        },
        "partition_count": {name: len(rows) for name, rows in partitions.items()},
        "label_distribution": {
            name: dict(Counter(row["label"] for row in rows)) for name, rows in partitions.items()
        },
        "trainable_parameter_count": sum(
            parameter.numel() for parameter in model.parameters() if parameter.requires_grad
        ),
        "total_parameter_count": sum(parameter.numel() for parameter in model.parameters()),
        "validation": validation,
        "selection": selection,
        "disclosure_selection": disclosure_selection,
        "test": test,
    }
    args.report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))


def _load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as file:
        return [
            {"text": row["document"], "label": SOURCE_LABEL[row["label"]]}
            for row in csv.DictReader(file, delimiter="\t")
            if row.get("document") and row.get("label") in SOURCE_LABEL
        ]


def _load_operational_training_rows(
    training_paths: tuple[Path, ...],
    evaluation_paths: tuple[Path, ...],
    public_holdout_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], int]:
    holdout_texts = {normalized_sentiment_text(row["text"]) for row in public_holdout_rows}
    for path in evaluation_paths:
        holdout_texts.update(
            normalized_sentiment_text(sample.text) for sample in load_labeled_alerts(path)
        )
    rows = [
        {"text": sample.text, "label": sample.sentiment}
        for path in training_paths
        for sample in load_labeled_alerts(path)
        if sample.sentiment in LABEL_ORDER
    ]
    filtered = [row for row in rows if normalized_sentiment_text(row["text"]) not in holdout_texts]
    return _deduplicate_rows(filtered), len(rows) - len(filtered)


def _deduplicate_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return conflict_safe_deduplicate(rows)[0]


def _loss_function(class_weights: torch.Tensor) -> Any:
    def compute_loss(
        outputs: Any,
        labels: torch.Tensor,
        num_items_in_batch: int | torch.Tensor | None = None,
    ) -> torch.Tensor:
        del num_items_in_batch
        return functional.cross_entropy(
            outputs.logits,
            labels,
            weight=class_weights.to(outputs.logits.device),
            label_smoothing=0.05,
        )

    return compute_loss


def _class_weights(rows: list[dict[str, str]]) -> torch.Tensor:
    counts = Counter(row["label"] for row in rows)
    total = sum(counts.values())
    return torch.tensor(
        [total / (len(LABEL_ORDER) * max(counts[label], 1)) for label in LABEL_ORDER],
        dtype=torch.float32,
    )


def _metrics(prediction: EvalPrediction) -> dict[str, float]:
    expected = prediction.label_ids.astype(int)
    raw_predictions = prediction.predictions
    logits = raw_predictions[0] if isinstance(raw_predictions, tuple) else raw_predictions
    predicted = np.asarray(logits).argmax(axis=-1)
    return {
        "accuracy": float(accuracy_score(expected, predicted)),
        "macro_f1": float(
            f1_score(expected, predicted, labels=range(len(LABEL_ORDER)), average="macro")
        ),
    }


def _clean_metrics(metrics: dict[str, Any], prefix: str) -> dict[str, float]:
    return {
        key.removeprefix(f"{prefix}_"): float(value)
        for key, value in metrics.items()
        if key != "epoch" and isinstance(value, int | float)
    }


def _stratified_limit(rows: list[dict[str, str]], limit: int, seed: int) -> list[dict[str, str]]:
    if len(rows) <= limit:
        return rows
    random_generator = random.Random(seed)  # noqa: S311
    selected: list[dict[str, str]] = []
    for label in LABEL_ORDER:
        bucket = [row for row in rows if row["label"] == label]
        random_generator.shuffle(bucket)
        selected.extend(bucket[: max(1, round(limit * len(bucket) / len(rows)))])
    random_generator.shuffle(selected)
    return selected[:limit]


def _per_label_limit(
    rows: list[dict[str, str]], per_label_limit: int, seed: int
) -> list[dict[str, str]]:
    random_generator = random.Random(seed)  # noqa: S311
    selected: list[dict[str, str]] = []
    for label in LABEL_ORDER:
        bucket = [row for row in rows if row["label"] == label]
        random_generator.shuffle(bucket)
        selected.extend(bucket[:per_label_limit])
    random_generator.shuffle(selected)
    return selected


def _set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    main()
