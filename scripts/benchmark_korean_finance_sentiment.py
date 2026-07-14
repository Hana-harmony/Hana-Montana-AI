from __future__ import annotations

import argparse
import csv
import json
import math
import random
import time
from collections import Counter
from hashlib import sha256
from pathlib import Path
from typing import Any, cast

import torch
from peft import PeftModel
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from hannah_montana_ai.domain.schemas import Sentiment
from hannah_montana_ai.services.model import MachineLearningFinancialNlpModel
from hannah_montana_ai.services.sentiment_policy import apply_financial_sentiment_policy
from hannah_montana_ai.services.sentiment_stacker import SentimentStacker
from hannah_montana_ai.training.dataset import load_labeled_alerts

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEST = PROJECT_ROOT / "data/external/kf_deberta_benchmark/ratings_test.csv"
DEFAULT_REPORT = PROJECT_ROOT / "reports/korean-finance-sentiment-benchmark.json"
CURRENT_MODEL_PATH = PROJECT_ROOT / "src/hannah_montana_ai/model_store/financial_nlp_ml.joblib"
ADAPTER_PATH = PROJECT_ROOT / "src/hannah_montana_ai/model_store/kf_deberta_sentiment"
STACKER_PATH = PROJECT_ROOT / "src/hannah_montana_ai/model_store/sentiment_stacker.joblib"
STACKER_REPORT_PATH = PROJECT_ROOT / "reports/sentiment-stacker-training-report.json"
BASE_MODEL = "kakaobank/kf-deberta-base"
BASE_MODEL_REVISION = "363b171d71443b0874b0bf9cea053eb5b1650633"
REFERENCE_MODEL = "snunlp/KR-FinBERT-SC"
REFERENCE_MODEL_REVISION = "f8586286cc3161fb648e9fee09a456069fd846d0"
LABEL_ORDER = ("NEGATIVE", "NEUTRAL", "POSITIVE")
SOURCE_LABEL = {"-1": "NEGATIVE", "0": "NEUTRAL", "1": "POSITIVE"}
MIN_OPERATIONAL_GOLD_MACRO_F1 = 0.80
BOOTSTRAP_SAMPLES = 2_000
BOOTSTRAP_SEED = 20260713
OPERATIONAL_GOLD_PATHS = {
    "real_disclosure_gold": PROJECT_ROOT
    / "data/evaluation/financial_alert_real_disclosure_gold.jsonl",
    "real_news_gold": PROJECT_ROOT / "data/evaluation/financial_alert_real_news_gold.jsonl",
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="동일한 한국 금융 뉴스 테스트셋에서 감성 모델을 비교한다."
    )
    parser.add_argument("--test-path", type=Path, default=DEFAULT_TEST)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--max-length", type=int, default=128)
    args = parser.parse_args()

    rows = _load_rows(args.test_path)
    expected = [row["label"] for row in rows]
    texts = [row["text"] for row in rows]
    operational_rows = {
        name: [
            {
                "text": sample.text,
                "label": sample.sentiment,
                "source_type": sample.source_type,
            }
            for sample in load_labeled_alerts(path)
        ]
        for name, path in OPERATIONAL_GOLD_PATHS.items()
    }
    operational_texts = [
        row["text"] for name in OPERATIONAL_GOLD_PATHS for row in operational_rows[name]
    ]
    results: dict[str, Any] = {}

    started = time.perf_counter()
    current = MachineLearningFinancialNlpModel(CURRENT_MODEL_PATH)
    current_probabilities = [current.sentiment_probabilities(text) for text in texts]
    baseline_predictions = [_top_label(probabilities) for probabilities in current_probabilities]
    results["hannah_tfidf_logistic"] = {
        **_metrics(expected, baseline_predictions),
        "elapsed_seconds": round(time.perf_counter() - started, 6),
    }

    started = time.perf_counter()
    reference_predictions = _predict_reference(
        texts,
        model_name=REFERENCE_MODEL,
        batch_size=args.batch_size,
        max_length=args.max_length,
    )
    results["kr_finbert_sc"] = {
        **_metrics(expected, reference_predictions),
        "elapsed_seconds": round(time.perf_counter() - started, 6),
    }

    started = time.perf_counter()
    adapter_probabilities = _predict_adapter_probabilities(
        texts + operational_texts,
        adapter_path=ADAPTER_PATH,
        batch_size=args.batch_size,
        max_length=args.max_length,
    )
    external_adapter_probabilities = adapter_probabilities[: len(texts)]
    adapter_predictions = [
        _top_label(probabilities) for probabilities in external_adapter_probabilities
    ]
    results["kf_deberta_lora"] = {
        **_metrics(expected, adapter_predictions),
        "elapsed_seconds": round(time.perf_counter() - started, 6),
    }

    ensemble_probabilities = [
        {label: 0.8 * adapter[label] + 0.2 * baseline[label] for label in LABEL_ORDER}
        for adapter, baseline in zip(
            external_adapter_probabilities, current_probabilities, strict=True
        )
    ]
    ensemble_predictions = [_top_label(row) for row in ensemble_probabilities]
    results["kf_deberta_lora_ensemble"] = {
        **_metrics(expected, ensemble_predictions),
        "transformer_weight": 0.8,
        "baseline_weight": 0.2,
    }

    stacker = SentimentStacker(STACKER_PATH, STACKER_REPORT_PATH)
    candidate_predictions = {
        "kf_deberta_lora": adapter_predictions,
        "kf_deberta_lora_ensemble": ensemble_predictions,
    }
    if stacker.enabled:
        stacked_probabilities = [
            stacker.probabilities(
                transformer=adapter,
                baseline=baseline,
                text=text,
                source_type="NEWS",
            )
            for text, adapter, baseline in zip(
                texts,
                external_adapter_probabilities,
                current_probabilities,
                strict=True,
            )
        ]
        if all(row is not None for row in stacked_probabilities):
            stacker_predictions = [
                _top_label(row) for row in stacked_probabilities if row is not None
            ]
            candidate_predictions["kf_deberta_lora_stacker"] = stacker_predictions
            results["kf_deberta_lora_stacker"] = {
                **_metrics(expected, stacker_predictions),
                "artifact": str(STACKER_PATH.relative_to(PROJECT_ROOT)),
            }

    operational_by_model: dict[str, dict[str, Any]] = {}
    offset = len(texts)
    for name, path in OPERATIONAL_GOLD_PATHS.items():
        gold_rows = operational_rows[name]
        size = len(gold_rows)
        adapter_rows = adapter_probabilities[offset : offset + size]
        baseline_rows = [current.sentiment_probabilities(row["text"]) for row in gold_rows]
        blended_rows = [
            {label: 0.8 * adapter[label] + 0.2 * baseline[label] for label in LABEL_ORDER}
            for adapter, baseline in zip(adapter_rows, baseline_rows, strict=True)
        ]
        probability_sets: dict[str, list[dict[str, float]]] = {
            "kf_deberta_lora": adapter_rows,
            "kf_deberta_lora_ensemble": blended_rows,
        }
        if stacker.enabled:
            stacked_rows = [
                stacker.probabilities(
                    transformer=adapter,
                    baseline=baseline,
                    text=row["text"],
                    source_type=row["source_type"],
                )
                for row, adapter, baseline in zip(
                    gold_rows,
                    adapter_rows,
                    baseline_rows,
                    strict=True,
                )
            ]
            if all(row is not None for row in stacked_rows):
                probability_sets["kf_deberta_lora_stacker"] = [
                    row for row in stacked_rows if row is not None
                ]
        operational_by_model[name] = {
            model_name: {
                **_metrics(
                    [row["label"] for row in gold_rows],
                    [
                        apply_financial_sentiment_policy(
                            row["text"], cast(Sentiment, _top_label(probabilities))
                        )
                        for row, probabilities in zip(
                            gold_rows,
                            model_probabilities,
                            strict=True,
                        )
                    ],
                ),
                "sample_count": size,
                "path": str(path.relative_to(PROJECT_ROOT)),
                "sha256": _sha256(path),
            }
            for model_name, model_probabilities in probability_sets.items()
        }
        offset += size

    deployable_candidates = [
        model_name
        for model_name in (
            "kf_deberta_lora",
            "kf_deberta_lora_ensemble",
            "kf_deberta_lora_stacker",
        )
        if model_name in results
        and float(results[model_name]["macro_f1"]) >= 0.85
        and all(
            model_name in model_results
            and model_results[model_name]["sample_count"] >= 30
            and float(model_results[model_name]["accuracy"]) >= 0.90
            and float(model_results[model_name]["macro_f1"]) >= MIN_OPERATIONAL_GOLD_MACRO_F1
            for model_results in operational_by_model.values()
        )
    ]
    candidate_name = max(
        deployable_candidates or ["kf_deberta_lora"],
        key=lambda name: float(results[name]["macro_f1"]),
    )
    candidate = results[candidate_name]
    reference = results["kr_finbert_sc"]
    operational_results = {
        name: model_results[candidate_name]
        for name, model_results in operational_by_model.items()
        if candidate_name in model_results
    }
    eligible = (
        len(rows) >= 900
        and float(candidate["macro_f1"]) >= 0.85
        and float(candidate["macro_f1"]) >= float(reference["macro_f1"])
        and all(
            result["sample_count"] >= 30
            and float(result["accuracy"]) >= 0.90
            and float(result["macro_f1"]) >= MIN_OPERATIONAL_GOLD_MACRO_F1
            for result in operational_results.values()
        )
    )
    report = {
        "schema_version": "korean-finance-sentiment-benchmark/v1",
        "dataset_source": "mssongit/finance-task:fnsentiment:test",
        "test_path": str(args.test_path.relative_to(PROJECT_ROOT)),
        "test_sha256": _sha256(args.test_path),
        "sample_count": len(rows),
        "label_distribution": dict(sorted(Counter(expected).items())),
        "models": results,
        "operational_gold": operational_results,
        "operational_gold_by_model": operational_by_model,
        "statistical_comparison": {
            "protocol": {
                "paired_bootstrap_samples": BOOTSTRAP_SAMPLES,
                "seed": BOOTSTRAP_SEED,
                "mcnemar": "exact two-sided",
            },
            "candidate_vs_kr_finbert_sc": _paired_comparison(
                expected,
                reference_predictions,
                candidate_predictions[candidate_name],
            ),
            "candidate_vs_hana_tfidf_logistic": _paired_comparison(
                expected,
                baseline_predictions,
                candidate_predictions[candidate_name],
            ),
        },
        "deployment_gate": {
            "minimum_sample_count": 900,
            "minimum_macro_f1": 0.85,
            "must_match_or_exceed_reference": REFERENCE_MODEL,
            "minimum_operational_gold_accuracy": 0.90,
            "minimum_operational_gold_macro_f1": MIN_OPERATIONAL_GOLD_MACRO_F1,
            "candidate_model": candidate_name,
            "eligible": eligible,
            "decision": "DEPLOY_HANA_MONTANA_AI" if eligible else "KEEP_CURRENT_MODEL",
        },
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


def _predict_reference(
    texts: list[str],
    *,
    model_name: str,
    batch_size: int,
    max_length: int,
) -> list[str]:
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        revision=REFERENCE_MODEL_REVISION,
        trust_remote_code=False,
    )
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        revision=REFERENCE_MODEL_REVISION,
        trust_remote_code=False,
    )
    return _batched_predictions(texts, tokenizer, model, batch_size, max_length)


def _predict_adapter_probabilities(
    texts: list[str],
    *,
    adapter_path: Path,
    batch_size: int,
    max_length: int,
) -> list[dict[str, float]]:
    if not adapter_path.exists():
        raise SystemExit(f"학습된 감성 어댑터가 없습니다: {adapter_path}")
    tokenizer = AutoTokenizer.from_pretrained(  # nosec B615
        adapter_path,
        revision="local-verified-artifact",
        trust_remote_code=False,
        local_files_only=True,
    )
    base = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL,
        revision=BASE_MODEL_REVISION,
        num_labels=len(LABEL_ORDER),
        id2label={index: label for index, label in enumerate(LABEL_ORDER)},
        label2id={label: index for index, label in enumerate(LABEL_ORDER)},
    )
    model = PeftModel.from_pretrained(
        base,
        adapter_path,
        local_files_only=True,
        use_safetensors=True,
    )
    return _batched_probabilities(texts, tokenizer, model, batch_size, max_length)


def _batched_probabilities(
    texts: list[str],
    tokenizer: Any,
    model: Any,
    batch_size: int,
    max_length: int,
) -> list[dict[str, float]]:
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    model.to(device)
    model.eval()
    probabilities: list[dict[str, float]] = []
    for start in range(0, len(texts), batch_size):
        encoded = tokenizer(
            texts[start : start + batch_size],
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
        encoded = {name: value.to(device) for name, value in encoded.items()}
        with torch.inference_mode():
            rows = torch.softmax(model(**encoded).logits, dim=-1).cpu().tolist()
        probabilities.extend(
            {
                str(model.config.id2label[index]).upper(): float(value)
                for index, value in enumerate(row)
            }
            for row in rows
        )
    return probabilities


def _top_label(probabilities: dict[str, float]) -> str:
    return max(probabilities, key=probabilities.__getitem__)


def _batched_predictions(
    texts: list[str],
    tokenizer: Any,
    model: Any,
    batch_size: int,
    max_length: int,
) -> list[str]:
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    model.to(device)
    model.eval()
    predictions: list[str] = []
    for start in range(0, len(texts), batch_size):
        encoded = tokenizer(
            texts[start : start + batch_size],
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )
        encoded = {name: value.to(device) for name, value in encoded.items()}
        with torch.inference_mode():
            indices = model(**encoded).logits.argmax(dim=-1).cpu().tolist()
        predictions.extend(str(model.config.id2label[index]).upper() for index in indices)
    return predictions


def _metrics(expected: list[str], predicted: list[str]) -> dict[str, Any]:
    matrix = confusion_matrix(expected, predicted, labels=LABEL_ORDER)
    precision, recall, f1, support = precision_recall_fscore_support(
        expected,
        predicted,
        labels=LABEL_ORDER,
        zero_division=0,
    )
    return {
        "accuracy": float(accuracy_score(expected, predicted)),
        "macro_f1": float(f1_score(expected, predicted, labels=LABEL_ORDER, average="macro")),
        "confusion_matrix": {
            expected_label: {
                predicted_label: int(matrix[row_index, column_index])
                for column_index, predicted_label in enumerate(LABEL_ORDER)
            }
            for row_index, expected_label in enumerate(LABEL_ORDER)
        },
        "label_metrics": {
            label: {
                "precision": float(precision[index]),
                "recall": float(recall[index]),
                "f1": float(f1[index]),
                "support": int(support[index]),
            }
            for index, label in enumerate(LABEL_ORDER)
        },
    }


def _paired_comparison(
    expected: list[str],
    reference: list[str],
    candidate: list[str],
) -> dict[str, Any]:
    generator = random.Random(BOOTSTRAP_SEED)  # noqa: S311  # nosec B311 - 재현 가능한 통계 표본
    accuracy_differences: list[float] = []
    macro_f1_differences: list[float] = []
    for _ in range(BOOTSTRAP_SAMPLES):
        indices = [generator.randrange(len(expected)) for _ in expected]
        truth = [expected[index] for index in indices]
        left = [reference[index] for index in indices]
        right = [candidate[index] for index in indices]
        accuracy_differences.append(
            float(accuracy_score(truth, right) - accuracy_score(truth, left))
        )
        macro_f1_differences.append(
            float(
                f1_score(truth, right, labels=LABEL_ORDER, average="macro", zero_division=0)
                - f1_score(truth, left, labels=LABEL_ORDER, average="macro", zero_division=0)
            )
        )
    reference_only = sum(
        truth == left and truth != right
        for truth, left, right in zip(expected, reference, candidate, strict=True)
    )
    candidate_only = sum(
        truth != left and truth == right
        for truth, left, right in zip(expected, reference, candidate, strict=True)
    )
    macro_interval = _percentile_interval(macro_f1_differences)
    return {
        "accuracy_difference_95_ci": _percentile_interval(accuracy_differences),
        "macro_f1_difference_95_ci": macro_interval,
        "mcnemar_exact": {
            "reference_only_correct": reference_only,
            "candidate_only_correct": candidate_only,
            "p_value": _exact_mcnemar_p_value(reference_only, candidate_only),
        },
        "statistically_significant_macro_f1_gain": macro_interval["low"] > 0.0,
    }


def _percentile_interval(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    low_index = max(0, math.floor((len(ordered) - 1) * 0.025))
    high_index = min(len(ordered) - 1, math.ceil((len(ordered) - 1) * 0.975))
    return {
        "mean": sum(ordered) / len(ordered),
        "low": ordered[low_index],
        "high": ordered[high_index],
    }


def _exact_mcnemar_p_value(reference_only: int, candidate_only: int) -> float:
    discordant = reference_only + candidate_only
    if discordant == 0:
        return 1.0
    tail = sum(
        math.comb(discordant, value) for value in range(min(reference_only, candidate_only) + 1)
    ) / (2**discordant)
    return float(min(1.0, 2.0 * tail))


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    main()
