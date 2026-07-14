from __future__ import annotations

import argparse
import json
import random
from collections import Counter
from datetime import UTC, datetime
from hashlib import sha256
from importlib.metadata import version as package_version
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import accuracy_score, cohen_kappa_score, f1_score
from train_k_fnspid_impact_model import LABEL_ORDER, load_rows

from hannah_montana_ai.services.impact_model_features import IMPACT_INPUT_FEATURE_VERSION
from hannah_montana_ai.services.model_artifact_integrity import build_artifact_manifest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_MODEL = "kakaobank/kf-deberta-base"
BASE_MODEL_REVISION = "363b171d71443b0874b0bf9cea053eb5b1650633"
DEFAULT_DATASET = PROJECT_ROOT / "data/k_fnspid/v3"
DEFAULT_OUTPUT = PROJECT_ROOT / "src/hannah_montana_ai/model_store/k_fnspid_impact_transformer"
DEFAULT_REPORT = PROJECT_ROOT / "reports/k-fnspid-transformer-training-report.json"
DEFAULT_PREDICTIONS = PROJECT_ROOT / "reports/k-fnspid-transformer-test-predictions.jsonl"
DEFAULT_BASELINE_REPORT = PROJECT_ROOT / "reports/k-fnspid-impact-training-report.json"


class EncodedImpactDataset:
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
    from peft import LoraConfig, TaskType, get_peft_model
    from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
        DataCollatorWithPadding,
        EarlyStoppingCallback,
        Trainer,
        TrainingArguments,
    )

    parser = argparse.ArgumentParser(
        description="KF-DeBERTa LoRA 기반 K-FNSPID 시장영향 모델을 학습한다."
    )
    parser.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--predictions-path", type=Path, default=DEFAULT_PREDICTIONS)
    parser.add_argument("--baseline-report-path", type=Path, default=DEFAULT_BASELINE_REPORT)
    parser.add_argument(
        "--resume-from-checkpoint",
        type=Path,
        help="중단된 학습을 검증된 Trainer 체크포인트에서 재개한다.",
    )
    parser.add_argument("--max-length", type=int, default=256)
    parser.add_argument("--epochs", type=float, default=3.0)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--gradient-accumulation", type=int, default=4)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--focal-gamma", type=float, default=1.5)
    parser.add_argument("--ordinal-loss-weight", type=float, default=0.30)
    parser.add_argument("--label-smoothing", type=float, default=0.02)
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
    for attribute in (
        "dataset_dir",
        "output_dir",
        "report_path",
        "predictions_path",
        "baseline_report_path",
        "resume_from_checkpoint",
    ):
        value = getattr(args, attribute)
        if value is not None:
            setattr(args, attribute, _project_path(value))

    _set_seed(args.seed)
    rows = load_rows(args.dataset_dir)
    dataset_manifest = _dataset_manifest(args.dataset_dir)
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
    warmup_steps = max(1, round(optimizer_steps * 0.08))
    evaluation_batch_size = max(args.batch_size * 2, 8)
    training_hyperparameters = {
        "epochs_requested": args.epochs,
        "per_device_train_batch_size": args.batch_size,
        "per_device_eval_batch_size": evaluation_batch_size,
        "gradient_accumulation_steps": args.gradient_accumulation,
        "effective_batch_size": args.batch_size * args.gradient_accumulation,
        "learning_rate": args.learning_rate,
        "lr_scheduler_type": "cosine",
        "warmup_steps": warmup_steps,
        "warmup_ratio_of_optimizer_steps": 0.08,
        "weight_decay": 0.01,
        "max_grad_norm": 1.0,
        "early_stopping_patience_epochs": 1,
        "gradient_checkpointing": args.gradient_checkpointing,
        "mixed_precision": args.mixed_precision,
        "lora": {
            "rank": 16,
            "alpha": 32,
            "dropout": 0.1,
            "target_modules": ["query_proj", "key_proj", "value_proj"],
            "modules_to_save": ["pooler", "classifier"],
        },
    }
    trainer = Trainer(
        model=model,
        args=TrainingArguments(
            output_dir=str(run_dir),
            per_device_train_batch_size=args.batch_size,
            per_device_eval_batch_size=evaluation_batch_size,
            gradient_accumulation_steps=args.gradient_accumulation,
            num_train_epochs=args.epochs,
            learning_rate=args.learning_rate,
            lr_scheduler_type="cosine",
            warmup_steps=warmup_steps,
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
            seed=args.seed,
            data_seed=args.seed,
            report_to="none",
            dataloader_num_workers=0,
            dataloader_pin_memory=False,
        ),
        train_dataset=train_dataset,
        eval_dataset=validation_dataset,
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
        processing_class=tokenizer,
        compute_loss_func=_loss_function(
            class_weights,
            focal_gamma=args.focal_gamma,
            ordinal_loss_weight=args.ordinal_loss_weight,
            label_smoothing=args.label_smoothing,
        ),
        compute_metrics=_metrics_with_prior(partitions["TRAIN"]),
        callbacks=[EarlyStoppingCallback(early_stopping_patience=1)],
    )
    trainer.train(
        resume_from_checkpoint=(
            str(args.resume_from_checkpoint) if args.resume_from_checkpoint else None
        )
    )
    trainer.remove_callback(EarlyStoppingCallback)
    validation_output = trainer.predict(validation_dataset, metric_key_prefix="validation")
    test_output = trainer.predict(test_dataset, metric_key_prefix="test")
    validation_logits = np.asarray(validation_output.predictions)
    test_logits = np.asarray(test_output.predictions)
    postprocessing = _select_log_prior_correction(
        validation_logits,
        validation_output.label_ids.astype(int),
        partitions["TRAIN"],
    )
    corrected_validation_logits = _apply_log_prior_correction(
        validation_logits,
        postprocessing,
    )
    corrected_test_logits = _apply_log_prior_correction(test_logits, postprocessing)
    validation_raw_metrics = _classification_metrics(
        validation_output.label_ids.astype(int),
        validation_logits.argmax(axis=-1),
    )
    test_raw_metrics = _classification_metrics(
        test_output.label_ids.astype(int),
        test_logits.argmax(axis=-1),
    )
    validation_metrics = _classification_metrics(
        validation_output.label_ids.astype(int),
        corrected_validation_logits.argmax(axis=-1),
    )
    test_metrics = _classification_metrics(
        test_output.label_ids.astype(int),
        corrected_test_logits.argmax(axis=-1),
    )
    validation_metrics["sample_count"] = len(validation_dataset)
    test_metrics["sample_count"] = len(test_dataset)
    baseline_report = json.loads(args.baseline_report_path.read_text(encoding="utf-8"))
    if baseline_report.get("dataset_manifest", {}).get("sha256") != dataset_manifest["sha256"]:
        raise SystemExit("기준선과 Transformer의 K-FNSPID manifest가 다릅니다.")
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
    version = (
        f"k-fnspid-impact-kf-deberta-lora-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
        f"-prior{float(postprocessing['selected_strength']):.2f}"
    )
    metadata = {
        "version": version,
        "base_model": BASE_MODEL,
        "base_model_revision": BASE_MODEL_REVISION,
        "label_order": LABEL_ORDER,
        "max_length": args.max_length,
        "trained_at": datetime.now(UTC).isoformat(),
        "artifact_files": artifact_files,
        "input_feature_version": IMPACT_INPUT_FEATURE_VERSION,
        "seed": args.seed,
        "postprocessing": postprocessing,
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
        "dataset_manifest": dataset_manifest,
        "artifact_dir": str(args.output_dir.resolve().relative_to(PROJECT_ROOT)),
        "evaluation_protocol": (
            "TRAIN fit; Validation selects checkpoint, log-prior correction, and seed; "
            "frozen TEST is evaluated once for final deployment and superiority gates"
        ),
        "training_hyperparameters": training_hyperparameters,
        "training_state": {
            "completed_epoch": float(trainer.state.epoch or 0.0),
            "global_optimizer_steps": int(trainer.state.global_step),
            "best_validation_macro_f1": float(trainer.state.best_metric or 0.0),
        },
        "runtime": {
            "device": str(trainer.args.device),
            "python_packages": {
                "torch": package_version("torch"),
                "transformers": package_version("transformers"),
                "peft": package_version("peft"),
            },
        },
        "training_objective": {
            "name": "class-balanced-focal-plus-ordinal-cdf",
            "focal_gamma": args.focal_gamma,
            "ordinal_loss_weight": args.ordinal_loss_weight,
            "label_smoothing": args.label_smoothing,
        },
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
        "validation_raw": validation_raw_metrics,
        "test": test_metrics,
        "test_raw": test_raw_metrics,
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
    predictions_manifest = _write_predictions(
        args.predictions_path,
        partitions["TEST"],
        corrected_test_logits,
    )
    report["test_predictions"] = predictions_manifest
    args.report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))


def _loss_function(
    class_weights: Any,
    *,
    focal_gamma: float,
    ordinal_loss_weight: float,
    label_smoothing: float,
) -> Any:
    import torch
    import torch.nn.functional as functional

    def compute_loss(
        outputs: Any,
        labels: Any,
        num_items_in_batch: int | Any | None = None,
    ) -> Any:
        del num_items_in_batch
        weights = class_weights.to(outputs.logits.device)
        per_sample_cross_entropy = functional.cross_entropy(
            outputs.logits,
            labels,
            weight=weights,
            label_smoothing=label_smoothing,
            reduction="none",
        )
        probabilities = torch.softmax(outputs.logits, dim=-1)
        true_class_probability = probabilities.gather(1, labels.unsqueeze(1)).squeeze(1)
        focal_loss = (
            (1.0 - true_class_probability).pow(focal_gamma) * per_sample_cross_entropy
        ).mean()
        target_distribution = functional.one_hot(labels, num_classes=len(LABEL_ORDER)).float()
        predicted_cdf = probabilities.cumsum(dim=-1)
        target_cdf = target_distribution.cumsum(dim=-1)
        ordinal_cdf_loss = functional.mse_loss(predicted_cdf, target_cdf)
        return focal_loss + ordinal_loss_weight * ordinal_cdf_loss

    return compute_loss


def _class_weights(rows: list[dict[str, Any]]) -> Any:
    import torch

    counts = Counter(str(row["importance"]) for row in rows)
    total = sum(counts.values())
    weights = [total / (len(LABEL_ORDER) * max(counts[label], 1)) for label in LABEL_ORDER]
    return torch.tensor(weights, dtype=torch.float32)


def _metrics_with_prior(
    training_rows: list[dict[str, Any]],
) -> Any:
    def compute_metrics(prediction: Any) -> dict[str, float]:
        expected = prediction.label_ids.astype(int)
        logits = np.asarray(prediction.predictions)
        postprocessing = _select_log_prior_correction(logits, expected, training_rows)
        corrected = _apply_log_prior_correction(logits, postprocessing)
        return _classification_metrics(expected, corrected.argmax(axis=-1))

    return compute_metrics


def _classification_metrics(
    expected: np.ndarray,
    predicted: np.ndarray,
) -> dict[str, float]:
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
        "quadratic_kappa": float(cohen_kappa_score(expected, predicted, weights="quadratic")),
    }


def _select_log_prior_correction(
    logits: np.ndarray,
    expected: np.ndarray,
    training_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    counts = Counter(str(row["importance"]) for row in training_rows)
    total = sum(counts.values())
    priors = np.asarray([counts[label] / total for label in LABEL_ORDER], dtype=np.float64)
    candidates: list[tuple[tuple[float, float, float, float], float, dict[str, float]]] = []
    for strength in np.linspace(0.0, 2.0, 41).tolist():
        corrected = logits + strength * np.log(priors)[None, :]
        metrics = _classification_metrics(expected, corrected.argmax(axis=-1))
        objective = (
            metrics["macro_f1"],
            metrics["quadratic_kappa"],
            metrics["accuracy"],
            -strength,
        )
        candidates.append((objective, strength, metrics))
    _, selected_strength, selected_metrics = max(candidates, key=lambda row: row[0])
    return {
        "method": "validation-selected-log-prior-correction/v1",
        "selection_partition": "VALIDATION",
        "selection_objective": "macro_f1, then quadratic_kappa, accuracy, lower strength",
        "strength_grid": {"minimum": 0.0, "maximum": 2.0, "step": 0.05},
        "selected_strength": selected_strength,
        "training_class_priors": {
            label: float(prior) for label, prior in zip(LABEL_ORDER, priors, strict=True)
        },
        "selected_validation_metrics": selected_metrics,
    }


def _apply_log_prior_correction(
    logits: np.ndarray,
    postprocessing: dict[str, Any],
) -> np.ndarray:
    strength = float(postprocessing["selected_strength"])
    priors = np.asarray(
        [postprocessing["training_class_priors"][label] for label in LABEL_ORDER],
        dtype=np.float64,
    )
    if strength < 0 or np.any(priors <= 0) or not np.isclose(priors.sum(), 1.0):
        raise ValueError("시장영향 log-prior 보정 설정이 올바르지 않습니다.")
    return logits + strength * np.log(priors)[None, :]


def _write_predictions(
    path: Path,
    rows: list[dict[str, Any]],
    logits: np.ndarray,
) -> dict[str, str | int]:
    shifted = logits - logits.max(axis=-1, keepdims=True)
    exponentials = np.exp(shifted)
    probabilities = exponentials / exponentials.sum(axis=-1, keepdims=True)
    lines: list[str] = []
    for row, values in zip(rows, probabilities.tolist(), strict=True):
        predicted_index = max(range(len(values)), key=values.__getitem__)
        lines.append(
            json.dumps(
                {
                    "document_id": row["document_id"],
                    "stock_code": row["stock_code"],
                    "effective_trade_date": row["effective_trade_date"],
                    "source_type": row["source_type"],
                    "expected": row["importance"],
                    "predicted": LABEL_ORDER[predicted_index],
                    "probabilities": {
                        label: round(float(value), 8)
                        for label, value in zip(LABEL_ORDER, values, strict=True)
                    },
                },
                ensure_ascii=False,
            )
            + "\n"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(lines), encoding="utf-8")
    return {
        "path": str(path.relative_to(PROJECT_ROOT)),
        "sample_count": len(rows),
        "bytes": path.stat().st_size,
        "sha256": sha256(path.read_bytes()).hexdigest(),
    }


def _project_path(path: Path) -> Path:
    """CLI 경로를 프로젝트 내부의 절대경로로 정규화한다."""
    resolved = path.resolve() if path.is_absolute() else (PROJECT_ROOT / path).resolve()
    if not resolved.is_relative_to(PROJECT_ROOT.resolve()):
        raise ValueError(f"프로젝트 밖의 경로는 사용할 수 없습니다: {path}")
    return resolved


def _dataset_manifest(dataset_dir: Path) -> dict[str, str | int]:
    path = dataset_dir.resolve() / "manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("status") != "pass" or not payload.get("dataset_version"):
        raise SystemExit("검증된 K-FNSPID manifest만 학습에 사용할 수 있습니다.")
    return {
        "path": str(path.relative_to(PROJECT_ROOT)),
        "dataset_version": str(payload["dataset_version"]),
        "bytes": path.stat().st_size,
        "sha256": sha256(path.read_bytes()).hexdigest(),
    }


def _stratified_limit(rows: list[dict[str, Any]], limit: int, seed: int) -> list[dict[str, Any]]:
    if len(rows) <= limit:
        return rows
    random_generator = random.Random(seed)  # noqa: S311  # nosec B311 - 재현 가능한 층화 표본
    buckets = {label: [row for row in rows if row["importance"] == label] for label in LABEL_ORDER}
    selected: list[dict[str, Any]] = []
    for bucket in buckets.values():
        random_generator.shuffle(bucket)
        target = max(1, round(limit * len(bucket) / len(rows)))
        selected.extend(bucket[:target])
    random_generator.shuffle(selected)
    return selected[:limit]


def _set_seed(seed: int) -> None:
    import torch

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


if __name__ == "__main__":
    main()
