from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import torch
from peft import PeftModel
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from hannah_montana_ai.services.model import MachineLearningFinancialNlpModel
from hannah_montana_ai.services.sentiment_calibration import apply_source_logit_bias
from hannah_montana_ai.services.sentiment_stacker import (
    FEATURE_VERSION,
    LABEL_ORDER,
    build_stacker_features,
)
from hannah_montana_ai.training.sentiment_protocol import (
    decontaminate_public_partitions,
    load_disclosure_domain_partitions,
    stratified_hash_split,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_VALIDATION = PROJECT_ROOT / "data/external/kf_deberta_benchmark/ratings_val.csv"
PUBLIC_TRAIN = PROJECT_ROOT / "data/external/kf_deberta_benchmark/ratings_train.csv"
PUBLIC_TEST = PROJECT_ROOT / "data/external/kf_deberta_benchmark/ratings_test.csv"
DISCLOSURE_DOMAIN_DATASET = PROJECT_ROOT / "data/training/financial_alert_full_content_gold.jsonl"
BASELINE_MODEL = PROJECT_ROOT / "src/hannah_montana_ai/model_store/financial_nlp_ml.joblib"
ADAPTER_PATH = PROJECT_ROOT / "src/hannah_montana_ai/model_store/kf_deberta_sentiment"
OUTPUT_PATH = PROJECT_ROOT / "src/hannah_montana_ai/model_store/sentiment_stacker.joblib"
REPORT_PATH = PROJECT_ROOT / "reports/sentiment-stacker-training-report.json"
BASE_MODEL = "kakaobank/kf-deberta-base"
BASE_MODEL_REVISION = "363b171d71443b0874b0bf9cea053eb5b1650633"
SOURCE_LABEL = {"-1": "NEGATIVE", "0": "NEUTRAL", "1": "POSITIVE"}
EVALUATION_PATHS = (
    PROJECT_ROOT / "data/evaluation/financial_alert_eval.jsonl",
    PROJECT_ROOT / "data/evaluation/financial_alert_real_disclosure_gold.jsonl",
    PROJECT_ROOT / "data/evaluation/financial_alert_real_news_gold.jsonl",
    PROJECT_ROOT / "data/evaluation/financial_alert_stock_review_gold.jsonl",
)


def main() -> None:
    parser = argparse.ArgumentParser(description="감성 Transformer와 기준선의 스태커를 학습한다.")
    parser.add_argument("--public-validation", type=Path, default=PUBLIC_VALIDATION)
    parser.add_argument("--baseline-model", type=Path, default=BASELINE_MODEL)
    parser.add_argument("--adapter-path", type=Path, default=ADAPTER_PATH)
    parser.add_argument("--output-path", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--report-path", type=Path, default=REPORT_PATH)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--max-length", type=int, default=128)
    parser.add_argument("--seed", type=int, default=20260713)
    args = parser.parse_args()

    prepared = load_protocol_rows(args.public_validation)
    rows = prepared["CALIBRATION"]
    selection_rows = prepared["SELECTION"]
    all_rows = rows + selection_rows
    baseline = MachineLearningFinancialNlpModel(args.baseline_model)
    baseline_probabilities = [baseline.sentiment_probabilities(row["text"]) for row in all_rows]
    transformer_probabilities = predict_transformer_probabilities(
        [row["text"] for row in all_rows],
        adapter_path=args.adapter_path,
        batch_size=args.batch_size,
        max_length=args.max_length,
    )
    calibration_baseline = baseline_probabilities[: len(rows)]
    calibration_transformer = transformer_probabilities[: len(rows)]
    features = np.asarray(
        [
            build_stacker_features(
                transformer,
                baseline_row,
                row["text"],
                row["source_type"],
            )
            for row, transformer, baseline_row in zip(
                rows,
                calibration_transformer,
                calibration_baseline,
                strict=True,
            )
        ],
        dtype=np.float64,
    )
    targets = np.asarray([row["label"] for row in rows])
    model = LogisticRegression(
        max_iter=2_000,
        class_weight="balanced",
        solver="lbfgs",
        C=0.7,
    )
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=args.seed)
    cross_validated = cross_val_predict(model, features, targets, cv=folds, method="predict")
    cross_validation = {
        "accuracy": float(accuracy_score(targets, cross_validated)),
        "macro_f1": float(f1_score(targets, cross_validated, labels=LABEL_ORDER, average="macro")),
    }
    model.fit(features, targets)
    selection_baseline = baseline_probabilities[len(rows) :]
    selection_transformer = transformer_probabilities[len(rows) :]
    selection_features = np.asarray(
        [
            build_stacker_features(
                transformer,
                baseline_row,
                row["text"],
                row["source_type"],
            )
            for row, transformer, baseline_row in zip(
                selection_rows,
                selection_transformer,
                selection_baseline,
                strict=True,
            )
        ],
        dtype=np.float64,
    )
    stacker_probabilities = [
        {str(label): float(value) for label, value in zip(model.classes_, values, strict=True)}
        for values in model.predict_proba(selection_features)
    ]
    ensemble_probabilities = [
        {label: 0.8 * transformer[label] + 0.2 * baseline_row[label] for label in LABEL_ORDER}
        for transformer, baseline_row in zip(selection_transformer, selection_baseline, strict=True)
    ]
    source_biases, calibration_metrics = _select_source_biases(
        rows,
        calibration_transformer,
    )
    calibrated_probabilities = [
        apply_source_logit_bias(probabilities, row["source_type"], source_biases)
        for row, probabilities in zip(selection_rows, selection_transformer, strict=True)
    ]
    selection_metrics = _selection_metrics(
        selection_rows,
        {
            "kf_deberta_lora": selection_transformer,
            "kf_deberta_lora_ensemble": ensemble_probabilities,
            "kf_deberta_lora_stacker": stacker_probabilities,
            "kf_deberta_lora_calibrated": calibrated_probabilities,
        },
    )
    locked_candidate = max(
        selection_metrics,
        key=lambda name: (
            float(selection_metrics[name]["by_source"]["NEWS"]["macro_f1"]),
            float(selection_metrics[name]["by_source"]["NEWS"]["accuracy"]),
            name == "kf_deberta_lora",
        ),
    )
    version = f"sentiment-stacker-logreg-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    payload = {
        "version": version,
        "feature_version": FEATURE_VERSION,
        "label_order": LABEL_ORDER,
        "model": model,
    }
    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(payload, args.output_path)
    artifact = {
        "path": str(args.output_path.relative_to(PROJECT_ROOT)),
        "bytes": args.output_path.stat().st_size,
        "sha256": file_sha256(args.output_path),
    }
    report = {
        "schema_version": "sentiment-stacker-training/v2",
        "version": version,
        "feature_version": FEATURE_VERSION,
        "sample_count": len(rows),
        "transformer_max_length": args.max_length,
        "calibration_protocol": (
            "공개 VALIDATION과 2026 공시 약지도를 각각 Calibration/Selection으로 "
            "해시 분할하고 Calibration으로만 결합기를 학습한다."
        ),
        "source_distribution": dict(sorted(Counter(row["dataset"] for row in rows).items())),
        "label_distribution": dict(sorted(Counter(targets.tolist()).items())),
        "candidate_selection": {
            "locked_candidate": locked_candidate,
            "selection_partition": "PUBLIC_VALIDATION_SELECTION",
            "diagnostic_partition": "DISCLOSURE_2026_SELECTION_WEAK_LABEL",
            "selection_metrics": selection_metrics,
            "test_used_for_selection": False,
            "operational_gold_used_for_selection": False,
            "tie_break": "news-macro-f1,news-accuracy,plain-adapter",
            "calibration": {
                "method": "source-logit-bias-grid/v1",
                "fit_partition": "CALIBRATION",
                "source_biases": source_biases,
                "fit_metrics": calibration_metrics,
            },
        },
        "protocol_audit": prepared["AUDIT"],
        "cross_validation": cross_validation,
        "artifact": artifact,
        "limitations": [
            "스태커 교차검증은 Calibration 내부 성능이며 Selection 성능을 대신하지 않는다.",
            "공시 Selection 라벨은 약지도이므로 독립 전문가 Gold를 대신하지 않는다.",
            "공개 Test와 운영 Gold는 고정 후보의 최종 gate에만 사용한다.",
        ],
    }
    args.report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))


def load_protocol_rows(public_validation: Path) -> dict[str, Any]:
    public, public_audit = decontaminate_public_partitions(
        {
            "TRAIN": _load_public_rows(PUBLIC_TRAIN),
            "VALIDATION": _load_public_rows(public_validation),
            "TEST": _load_public_rows(PUBLIC_TEST),
        }
    )
    public_split = stratified_hash_split(
        public["VALIDATION"], left_name="CALIBRATION", right_name="SELECTION"
    )
    disclosure, disclosure_audit = load_disclosure_domain_partitions(
        DISCLOSURE_DOMAIN_DATASET,
        EVALUATION_PATHS,
    )
    calibration = [
        {**row, "source_type": "NEWS", "dataset": "public_validation_calibration"}
        for row in public_split["CALIBRATION"]
    ] + [{**row, "dataset": "disclosure_2026_calibration"} for row in disclosure["CALIBRATION"]]
    selection = [
        {**row, "source_type": "NEWS", "dataset": "public_validation_selection"}
        for row in public_split["SELECTION"]
    ] + [{**row, "dataset": "disclosure_2026_selection"} for row in disclosure["SELECTION"]]
    return {
        "CALIBRATION": calibration,
        "SELECTION": selection,
        "AUDIT": {
            "public": public_audit,
            "disclosure": disclosure_audit,
            "partition_count": {
                "CALIBRATION": len(calibration),
                "SELECTION": len(selection),
            },
        },
    }


def _load_public_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as file:
        return [
            {"text": row["document"], "label": SOURCE_LABEL[row["label"]]}
            for row in csv.DictReader(file, delimiter="\t")
            if row.get("document") and row.get("label") in SOURCE_LABEL
        ]


def _selection_metrics(
    rows: list[dict[str, str]],
    probability_sets: dict[str, list[dict[str, float]]],
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for model_name, probabilities in probability_sets.items():
        by_source: dict[str, dict[str, float | int]] = {}
        for source_type in ("NEWS", "DISCLOSURE"):
            indices = [index for index, row in enumerate(rows) if row["source_type"] == source_type]
            expected = [rows[index]["label"] for index in indices]
            predicted = [
                max(probabilities[index], key=probabilities[index].__getitem__) for index in indices
            ]
            by_source[source_type] = {
                "sample_count": len(indices),
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
            }
        source_macro = [float(metrics["macro_f1"]) for metrics in by_source.values()]
        result[model_name] = {
            "by_source": by_source,
            "mean_source_macro_f1": sum(source_macro) / len(source_macro),
            "minimum_source_macro_f1": min(source_macro),
        }
    return result


def _select_source_biases(
    rows: list[dict[str, str]],
    probabilities: list[dict[str, float]],
) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, float]]]:
    grid = (-1.0, -0.75, -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0)
    source_biases: dict[str, dict[str, float]] = {}
    metrics: dict[str, dict[str, float]] = {}
    for source_type in ("NEWS", "DISCLOSURE"):
        indices = [index for index, row in enumerate(rows) if row["source_type"] == source_type]
        expected = [rows[index]["label"] for index in indices]
        candidates: list[tuple[float, float, float, dict[str, float], list[str]]] = []
        for negative_bias in grid:
            for positive_bias in grid:
                biases = {
                    "NEGATIVE": negative_bias,
                    "NEUTRAL": 0.0,
                    "POSITIVE": positive_bias,
                }
                predicted = []
                for index in indices:
                    calibrated = apply_source_logit_bias(
                        probabilities[index], source_type, {source_type: biases}
                    )
                    predicted.append(max(calibrated, key=calibrated.__getitem__))
                macro_f1 = float(
                    f1_score(
                        expected,
                        predicted,
                        labels=LABEL_ORDER,
                        average="macro",
                        zero_division=0,
                    )
                )
                accuracy = float(accuracy_score(expected, predicted))
                magnitude = abs(negative_bias) + abs(positive_bias)
                candidates.append((macro_f1, accuracy, -magnitude, biases, predicted))
        macro_f1, accuracy, _, biases, _ = max(candidates, key=lambda row: row[:3])
        source_biases[source_type] = biases
        metrics[source_type] = {
            "sample_count": len(indices),
            "accuracy": accuracy,
            "macro_f1": macro_f1,
        }
    return source_biases, metrics


def predict_transformer_probabilities(
    texts: list[str],
    *,
    adapter_path: Path,
    batch_size: int,
    max_length: int,
) -> list[dict[str, float]]:
    # 원격 다운로드 없이 SHA 검증된 로컬 artifact만 읽는다.
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
        trust_remote_code=False,
    )
    model = PeftModel.from_pretrained(
        base,
        adapter_path,
        local_files_only=True,
        use_safetensors=True,
    )
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
            values = torch.softmax(model(**encoded).logits, dim=-1).cpu().tolist()
        probabilities.extend(
            {label: float(value) for label, value in zip(LABEL_ORDER, row, strict=True)}
            for row in values
        )
    return probabilities


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    main()
