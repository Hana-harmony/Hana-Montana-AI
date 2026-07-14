from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

import joblib
import numpy as np
import torch
from peft import PeftModel
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from hannah_montana_ai.services.model import MachineLearningFinancialNlpModel
from hannah_montana_ai.services.sentiment_stacker import (
    FEATURE_VERSION,
    LABEL_ORDER,
    build_stacker_features,
)
from hannah_montana_ai.training.dataset import load_labeled_alerts

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_VALIDATION = PROJECT_ROOT / "data/external/kf_deberta_benchmark/ratings_val.csv"
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

    rows, excluded_overlap_count = load_calibration_rows(args.public_validation)
    baseline = MachineLearningFinancialNlpModel(args.baseline_model)
    baseline_probabilities = [baseline.sentiment_probabilities(row["text"]) for row in rows]
    transformer_probabilities = predict_transformer_probabilities(
        [row["text"] for row in rows],
        adapter_path=args.adapter_path,
        batch_size=args.batch_size,
        max_length=args.max_length,
    )
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
                transformer_probabilities,
                baseline_probabilities,
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
        "schema_version": "sentiment-stacker-training/v1",
        "version": version,
        "feature_version": FEATURE_VERSION,
        "sample_count": len(rows),
        "transformer_max_length": args.max_length,
        "calibration_protocol": (
            "KF-DeBERTa 학습 문장을 제외한 공개 VALIDATION으로만 결합기를 학습하고 "
            "공개 TEST는 최종 평가까지 봉인한다."
        ),
        "source_distribution": dict(sorted(Counter(row["dataset"] for row in rows).items())),
        "label_distribution": dict(sorted(Counter(targets.tolist()).items())),
        "excluded_evaluation_overlap_count": excluded_overlap_count,
        "cross_validation": cross_validation,
        "artifact": artifact,
        "limitations": [
            "스태커 교차검증은 결합기 보정 성능이며 독립 Test 성능을 대신하지 않는다.",
            (
                "기반 모델 조기종료에도 같은 공개 VALIDATION을 사용했으므로 "
                "최종 성능은 TEST만 판정한다."
            ),
            "최종 승격은 공개 Test와 운영 Gold를 함께 평가하는 별도 benchmark가 결정한다.",
        ],
    }
    args.report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))


def load_calibration_rows(public_validation: Path) -> tuple[list[dict[str, str]], int]:
    evaluation_texts = {
        sample.text for path in EVALUATION_PATHS for sample in load_labeled_alerts(path)
    }
    rows: list[dict[str, str]] = []
    with public_validation.open(encoding="utf-8-sig", newline="") as file:
        rows.extend(
            {
                "text": row["document"],
                "label": SOURCE_LABEL[row["label"]],
                "source_type": "NEWS",
                "dataset": "public_validation",
            }
            for row in csv.DictReader(file, delimiter="\t")
            if row.get("document")
            and row.get("label") in SOURCE_LABEL
            and row["document"] not in evaluation_texts
        )
    unique: dict[str, dict[str, str]] = {}
    conflicts: set[str] = set()
    for row in rows:
        previous = unique.get(row["text"])
        if previous is not None and previous["label"] != row["label"]:
            conflicts.add(row["text"])
        else:
            unique[row["text"]] = row
    result = [row for text, row in unique.items() if text not in conflicts]
    return result, len(rows) - len(result)


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
