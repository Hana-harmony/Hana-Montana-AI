from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn.functional as functional
from peft import LoraConfig, TaskType, get_peft_model
from sklearn.metrics import accuracy_score, cohen_kappa_score, f1_score
from torch.utils.data import Dataset
from train_k_fnspid_impact_model import LABEL_ORDER, load_rows
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

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_MODEL = "kakaobank/kf-deberta-base"
BASE_MODEL_REVISION = "363b171d71443b0874b0bf9cea053eb5b1650633"
DEFAULT_DATASET = PROJECT_ROOT / "data/k_fnspid/v2"
DEFAULT_OUTPUT = PROJECT_ROOT / "src/hannah_montana_ai/model_store/k_fnspid_impact_transformer"
DEFAULT_REPORT = PROJECT_ROOT / "reports/k-fnspid-transformer-training-report.json"
DEFAULT_BASELINE_REPORT = PROJECT_ROOT / "reports/k-fnspid-impact-training-report.json"


class EncodedImpactDataset(Dataset[dict[str, Any]]):
    def __init__(
        self,
        rows: list[dict[str, Any]],
        tokenizer: Any,
        max_length: int,
    ) -> None:
        encoded = tokenizer(
            [str(row["text"]) for row in rows],
            truncation=True,
            max_length=max_length,
        )
        self.features = [
            {
                **{name: values[index] for name, values in encoded.items()},
                "labels": LABEL_ORDER.index(str(row["importance"])),
            }
            for index, row in enumerate(rows)
        ]

    def __len__(self) -> int:
        return len(self.features)

    def __getitem__(self, index: int) -> dict[str, Any]:
        return self.features[index]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="KF-DeBERTa LoRA 기반 K-FNSPID 시장영향 모델을 학습한다."
    )
    parser.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--baseline-report-path", type=Path, default=DEFAULT_BASELINE_REPORT)
    parser.add_argument("--max-length", type=int, default=256)
    parser.add_argument("--epochs", type=float, default=3.0)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--gradient-accumulation", type=int, default=4)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--max-train-rows", type=int)
    parser.add_argument("--max-validation-rows", type=int)
    parser.add_argument("--max-test-rows", type=int)
    parser.add_argument(
        "--gradient-checkpointing",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="GPU 메모리가 부족할 때만 activation checkpointing을 사용한다.",
    )
    parser.add_argument(
        "--mixed-precision",
        choices=("none", "fp16", "bf16"),
        default="none",
        help="학습 가속기가 지원하는 mixed precision을 선택한다.",
    )
    args = parser.parse_args()

    _set_seed(42)
    rows = load_rows(args.dataset_dir)
    partitions = {
        name: [row for row in rows if row["split"] == name]
        for name in ("TRAIN", "VALIDATION", "TEST")
    }
    if args.max_train_rows:
        partitions["TRAIN"] = _stratified_limit(partitions["TRAIN"], args.max_train_rows, seed=42)
    if args.max_validation_rows:
        partitions["VALIDATION"] = _stratified_limit(
            partitions["VALIDATION"], args.max_validation_rows, seed=43
        )
    if args.max_test_rows:
        partitions["TEST"] = _stratified_limit(partitions["TEST"], args.max_test_rows, seed=44)
    if min(len(partitions["TRAIN"]), len(partitions["VALIDATION"]), len(partitions["TEST"])) < 100:
        raise SystemExit("각 시간 분할에 최소 100개의 비혼입 시장영향 라벨이 필요하다.")

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

    train_dataset = EncodedImpactDataset(partitions["TRAIN"], tokenizer, args.max_length)
    validation_dataset = EncodedImpactDataset(partitions["VALIDATION"], tokenizer, args.max_length)
    test_dataset = EncodedImpactDataset(partitions["TEST"], tokenizer, args.max_length)
    class_weights = _class_weights(partitions["TRAIN"])
    run_dir = args.output_dir.parent / f".{args.output_dir.name}-checkpoints"
    optimizer_steps = max(
        1,
        round(len(train_dataset) * args.epochs / (args.batch_size * args.gradient_accumulation)),
    )
    trainer = Trainer(
        model=model,
        args=TrainingArguments(
            output_dir=str(run_dir),
            per_device_train_batch_size=args.batch_size,
            per_device_eval_batch_size=max(args.batch_size * 2, 8),
            gradient_accumulation_steps=args.gradient_accumulation,
            num_train_epochs=args.epochs,
            learning_rate=args.learning_rate,
            lr_scheduler_type="cosine",
            warmup_steps=max(1, round(optimizer_steps * 0.08)),
            weight_decay=0.01,
            max_grad_norm=1.0,
            gradient_checkpointing=args.gradient_checkpointing,
            fp16=args.mixed_precision == "fp16",
            bf16=args.mixed_precision == "bf16",
            eval_strategy="epoch",
            save_strategy="epoch",
            logging_steps=50,
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
        train_dataset=train_dataset,
        eval_dataset=validation_dataset,
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
        processing_class=tokenizer,
        compute_loss_func=_loss_function(class_weights),
        compute_metrics=_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=1)],
    )
    trainer.train()
    trainer.remove_callback(EarlyStoppingCallback)
    validation_metrics = _clean_metrics(trainer.evaluate(validation_dataset))
    test_metrics = _clean_metrics(trainer.evaluate(test_dataset, metric_key_prefix="test"))
    validation_metrics["sample_count"] = len(validation_dataset)
    test_metrics["sample_count"] = len(test_dataset)
    baseline_report = json.loads(args.baseline_report_path.read_text(encoding="utf-8"))
    baseline_test = baseline_report.get("test", {})
    deployment_eligible = (
        len(test_dataset) >= 1_000
        and float(test_metrics.get("macro_f1", 0.0)) >= 0.35
        and float(test_metrics.get("quadratic_kappa", 0.0)) >= 0.20
        and float(test_metrics.get("macro_f1", 0.0)) >= float(baseline_test.get("macro_f1", 0.0))
        and float(test_metrics.get("quadratic_kappa", 0.0))
        >= float(baseline_test.get("quadratic_kappa", 0.0))
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    trainer.model.save_pretrained(args.output_dir, safe_serialization=True)
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
    version = f"k-fnspid-impact-kf-deberta-lora-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
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
            {"schema_version": "k-fnspid-transformer-artifact/v1", **metadata},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    report = {
        "schema_version": "k-fnspid-transformer-training/v1",
        **metadata,
        "dataset_dir": str(args.dataset_dir.resolve().relative_to(PROJECT_ROOT)),
        "partition_count": {name: len(values) for name, values in partitions.items()},
        "label_distribution": {
            name: dict(Counter(str(row["importance"]) for row in values))
            for name, values in partitions.items()
        },
        "trainable_parameter_count": sum(
            parameter.numel() for parameter in model.parameters() if parameter.requires_grad
        ),
        "total_parameter_count": sum(parameter.numel() for parameter in model.parameters()),
        "validation": validation_metrics,
        "test": test_metrics,
        "baseline_test": baseline_test,
        "deployment_gate": {
            "minimum_test_sample_count": 1_000,
            "minimum_macro_f1": 0.35,
            "minimum_quadratic_kappa": 0.20,
            "must_match_or_exceed_baseline": "k-fnspid-impact-tfidf-logreg",
            "eligible": deployment_eligible,
            "decision": (
                "DEPLOY_KF_DEBERTA_IMPACT" if deployment_eligible else "KEEP_TFIDF_IMPACT"
            ),
        },
    }
    args.report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))


def _loss_function(class_weights: torch.Tensor) -> Any:
    def compute_loss(
        outputs: Any,
        labels: torch.Tensor,
        num_items_in_batch: int | torch.Tensor | None = None,
    ) -> torch.Tensor:
        del num_items_in_batch
        weights = class_weights.to(outputs.logits.device)
        cross_entropy = functional.cross_entropy(outputs.logits, labels, weight=weights)
        probabilities = torch.softmax(outputs.logits, dim=-1)
        ordinal_axis = torch.arange(len(LABEL_ORDER), device=outputs.logits.device).float()
        expected = (probabilities * ordinal_axis).sum(dim=-1)
        ordinal_loss = functional.smooth_l1_loss(expected, labels.float())
        return cross_entropy + 0.15 * ordinal_loss

    return compute_loss


def _class_weights(rows: list[dict[str, Any]]) -> torch.Tensor:
    counts = Counter(str(row["importance"]) for row in rows)
    total = sum(counts.values())
    weights = [total / (len(LABEL_ORDER) * max(counts[label], 1)) for label in LABEL_ORDER]
    return torch.tensor(weights, dtype=torch.float32)


def _metrics(prediction: EvalPrediction) -> dict[str, float]:
    expected = prediction.label_ids.astype(int)
    predicted = np.asarray(prediction.predictions).argmax(axis=-1)
    return {
        "accuracy": float(accuracy_score(expected, predicted)),
        "macro_f1": float(
            f1_score(expected, predicted, labels=range(len(LABEL_ORDER)), average="macro")
        ),
        "quadratic_kappa": float(cohen_kappa_score(expected, predicted, weights="quadratic")),
    }


def _clean_metrics(metrics: dict[str, Any]) -> dict[str, float | int]:
    return {
        key.removeprefix("eval_").removeprefix("test_"): int(value)
        if key.endswith("samples")
        else float(value)
        for key, value in metrics.items()
        if key not in {"epoch"} and isinstance(value, int | float)
    }


def _stratified_limit(rows: list[dict[str, Any]], limit: int, seed: int) -> list[dict[str, Any]]:
    if len(rows) <= limit:
        return rows
    random_generator = random.Random(seed)  # noqa: S311
    buckets = {label: [row for row in rows if row["importance"] == label] for label in LABEL_ORDER}
    selected: list[dict[str, Any]] = []
    for bucket in buckets.values():
        random_generator.shuffle(bucket)
        target = max(1, round(limit * len(bucket) / len(rows)))
        selected.extend(bucket[:target])
    random_generator.shuffle(selected)
    return selected[:limit]


def _set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


if __name__ == "__main__":
    main()
