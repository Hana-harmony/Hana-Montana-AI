from __future__ import annotations

import argparse
import json
import time
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
from typing import Any

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from hannah_montana_ai.services.model import MachineLearningFinancialNlpModel
from hannah_montana_ai.training.dataset import LabeledAlert, load_labeled_alerts

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GOLD = PROJECT_ROOT / "data/evaluation/financial_alert_real_news_gold.jsonl"
TRAINING_GOLD = PROJECT_ROOT / "data/training/financial_alert_real_news_gold.jsonl"
DEFAULT_REPORT = PROJECT_ROOT / "reports/financial-alert-sota-benchmark.json"
DEFAULT_MODEL = "snunlp/KR-FinBERT-SC"
DEFAULT_MODEL_REVISION = "f8586286cc3161fb648e9fee09a456069fd846d0"
CURRENT_MODEL_PATH = PROJECT_ROOT / "src/hannah_montana_ai/model_store/financial_nlp_ml.joblib"


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare Hannah sentiment with KR-FinBERT-SC.")
    parser.add_argument("--gold", type=Path, default=DEFAULT_GOLD)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--sota-model", default=DEFAULT_MODEL)
    parser.add_argument("--sota-model-revision", default=DEFAULT_MODEL_REVISION)
    args = parser.parse_args()

    all_samples = load_labeled_alerts(args.gold)
    training_urls = {row.source_url for row in load_labeled_alerts(TRAINING_GOLD)}
    samples = [row for row in all_samples if row.source_url not in training_urls]
    if not samples or any(row.source_review_status != "CODEX_REVIEW_APPROVED" for row in samples):
        raise SystemExit("SOTA benchmark requires the Codex-reviewed gold set")

    started = time.perf_counter()
    current_model = MachineLearningFinancialNlpModel(CURRENT_MODEL_PATH)
    current_metrics = classification_metrics(
        [row.sentiment for row in samples],
        [current_model.classify_sentiment(row.model_text) for row in samples],
    )
    current_seconds = time.perf_counter() - started

    started = time.perf_counter()
    sota_predictions = predict_sota(samples, args.sota_model, args.sota_model_revision)
    sota_seconds = time.perf_counter() - started
    sota_metrics = classification_metrics(
        [row.sentiment for row in samples],
        sota_predictions,
    )
    report: dict[str, Any] = {
        "schema_version": "financial-alert-sota-benchmark/v1",
        "gold_path": str(args.gold.relative_to(PROJECT_ROOT)),
        "gold_sha256": sha256(args.gold.read_bytes()).hexdigest(),
        "reviewer": "codex-financial-review-v1",
        "sample_count": len(samples),
        "excluded_training_overlap_count": len(all_samples) - len(samples),
        "current_model": {
            "name": "hannah-financial-nlp-ml",
            **current_metrics,
            "elapsed_seconds": round(current_seconds, 6),
        },
        "sota_reference": {
            "name": args.sota_model,
            "revision": args.sota_model_revision,
            **sota_metrics,
            "elapsed_seconds": round(sota_seconds, 6),
        },
        "decision": model_decision(
            float(current_metrics["sentiment_accuracy"]),
            float(sota_metrics["sentiment_accuracy"]),
        ),
    }
    args.report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))


def predict_sota(
    samples: list[LabeledAlert],
    model_name: str,
    revision: str,
) -> list[str]:
    if len(revision) != 40 or any(character not in "0123456789abcdef" for character in revision):
        raise ValueError("SOTA 모델 revision은 40자리 Git commit SHA여야 합니다.")
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        revision=revision,
        trust_remote_code=False,
    )
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        revision=revision,
        trust_remote_code=False,
    )
    model.eval()
    predictions: list[str] = []
    texts = [row.model_text for row in samples]
    for start in range(0, len(texts), 16):
        encoded = tokenizer(
            texts[start : start + 16],
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt",
        )
        with torch.inference_mode():
            indices = model(**encoded).logits.argmax(dim=-1).tolist()
        predictions.extend(str(model.config.id2label[index]).upper() for index in indices)
    return predictions


def classification_metrics(expected: list[str], predicted: list[str]) -> dict[str, Any]:
    matrix: defaultdict[str, defaultdict[str, int]] = defaultdict(lambda: defaultdict(int))
    for truth, guess in zip(expected, predicted, strict=True):
        matrix[truth][guess] += 1
    confusion = {truth: dict(sorted(values.items())) for truth, values in sorted(matrix.items())}
    accuracy = sum(truth == guess for truth, guess in zip(expected, predicted, strict=True)) / len(
        expected
    )
    return {
        "sentiment_accuracy": accuracy,
        "sentiment_macro_f1": macro_f1_from_confusion(confusion),
        "sentiment_confusion_matrix": confusion,
    }


def macro_f1_from_confusion(matrix: dict[str, dict[str, int]]) -> float:
    labels = sorted(
        set(matrix) | {label for predictions in matrix.values() for label in predictions}
    )
    scores: list[float] = []
    for label in labels:
        true_positive = matrix.get(label, {}).get(label, 0)
        false_positive = sum(
            matrix.get(other, {}).get(label, 0) for other in labels if other != label
        )
        false_negative = sum(
            value for guess, value in matrix.get(label, {}).items() if guess != label
        )
        precision = (
            true_positive / (true_positive + false_positive)
            if true_positive + false_positive
            else 0.0
        )
        recall = (
            true_positive / (true_positive + false_negative)
            if true_positive + false_negative
            else 0.0
        )
        scores.append(2 * precision * recall / (precision + recall) if precision + recall else 0.0)
    return sum(scores) / len(scores) if scores else 0.0


def model_decision(current_accuracy: float, sota_accuracy: float) -> str:
    if current_accuracy >= sota_accuracy:
        return "KEEP_CURRENT_SENTIMENT_MODEL"
    return "SOTA_REFERENCE_OUTPERFORMS_RETRAIN_REQUIRED"


if __name__ == "__main__":
    main()
