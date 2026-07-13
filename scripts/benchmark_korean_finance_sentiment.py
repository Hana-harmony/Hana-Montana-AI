from __future__ import annotations

import argparse
import csv
import json
import time
from collections import Counter
from hashlib import sha256
from pathlib import Path
from typing import Any

import torch
from peft import PeftModel
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from hannah_montana_ai.services.model import MachineLearningFinancialNlpModel
from hannah_montana_ai.services.sentiment_policy import apply_financial_sentiment_policy
from hannah_montana_ai.training.dataset import load_labeled_alerts

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEST = PROJECT_ROOT / "data/external/kf_deberta_benchmark/ratings_test.csv"
DEFAULT_REPORT = PROJECT_ROOT / "reports/korean-finance-sentiment-benchmark.json"
CURRENT_MODEL_PATH = PROJECT_ROOT / "src/hannah_montana_ai/model_store/financial_nlp_ml.joblib"
ADAPTER_PATH = PROJECT_ROOT / "src/hannah_montana_ai/model_store/kf_deberta_sentiment"
BASE_MODEL = "kakaobank/kf-deberta-base"
BASE_MODEL_REVISION = "363b171d71443b0874b0bf9cea053eb5b1650633"
REFERENCE_MODEL = "snunlp/KR-FinBERT-SC"
REFERENCE_MODEL_REVISION = "f8586286cc3161fb648e9fee09a456069fd846d0"
LABEL_ORDER = ("NEGATIVE", "NEUTRAL", "POSITIVE")
SOURCE_LABEL = {"-1": "NEGATIVE", "0": "NEUTRAL", "1": "POSITIVE"}
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
            {"text": sample.text, "label": sample.sentiment}
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
    predictions = [_top_label(probabilities) for probabilities in current_probabilities]
    results["hannah_tfidf_logistic"] = {
        **_metrics(expected, predictions),
        "elapsed_seconds": round(time.perf_counter() - started, 6),
    }

    started = time.perf_counter()
    predictions = _predict_reference(
        texts,
        model_name=REFERENCE_MODEL,
        batch_size=args.batch_size,
        max_length=args.max_length,
    )
    results["kr_finbert_sc"] = {
        **_metrics(expected, predictions),
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
    predictions = [_top_label(probabilities) for probabilities in adapter_probabilities]
    predictions = predictions[: len(texts)]
    results["kf_deberta_lora"] = {
        **_metrics(expected, predictions),
        "elapsed_seconds": round(time.perf_counter() - started, 6),
    }

    ensemble_probabilities = [
        {
            label: 0.8 * adapter[label] + 0.2 * baseline[label]
            for label in LABEL_ORDER
        }
        for adapter, baseline in zip(
            external_adapter_probabilities, current_probabilities, strict=True
        )
    ]
    results["kf_deberta_lora_ensemble"] = {
        **_metrics(expected, [_top_label(row) for row in ensemble_probabilities]),
        "transformer_weight": 0.8,
        "baseline_weight": 0.2,
    }

    operational_results: dict[str, Any] = {}
    offset = len(texts)
    for name, path in OPERATIONAL_GOLD_PATHS.items():
        gold_rows = operational_rows[name]
        size = len(gold_rows)
        adapter_rows = adapter_probabilities[offset : offset + size]
        baseline_rows = [current.sentiment_probabilities(row["text"]) for row in gold_rows]
        blended_rows = [
            {
                label: 0.8 * adapter[label] + 0.2 * baseline[label]
                for label in LABEL_ORDER
            }
            for adapter, baseline in zip(adapter_rows, baseline_rows, strict=True)
        ]
        operational_results[name] = {
            **_metrics(
                [row["label"] for row in gold_rows],
                [
                    apply_financial_sentiment_policy(row["text"], _top_label(probabilities))
                    for row, probabilities in zip(gold_rows, blended_rows, strict=True)
                ],
            ),
            "sample_count": size,
            "path": str(path.relative_to(PROJECT_ROOT)),
            "sha256": _sha256(path),
        }
        offset += size

    candidate = results["kf_deberta_lora_ensemble"]
    reference = results["kr_finbert_sc"]
    eligible = (
        len(rows) >= 900
        and float(candidate["macro_f1"]) >= 0.85
        and float(candidate["macro_f1"]) >= float(reference["macro_f1"])
        and all(
            result["sample_count"] >= 30 and float(result["accuracy"]) >= 0.90
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
        "deployment_gate": {
            "minimum_sample_count": 900,
            "minimum_macro_f1": 0.85,
            "must_match_or_exceed_reference": REFERENCE_MODEL,
            "minimum_operational_gold_accuracy": 0.90,
            "eligible": eligible,
            "decision": "DEPLOY_KF_DEBERTA_ENSEMBLE" if eligible else "KEEP_CURRENT_MODEL",
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
    }


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    main()
