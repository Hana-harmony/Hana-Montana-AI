from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
import pyarrow.parquet as pq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, cohen_kappa_score, f1_score
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = PROJECT_ROOT / "data/k_fnspid/v1"
DEFAULT_MODEL = PROJECT_ROOT / "src/hannah_montana_ai/model_store/k_fnspid_impact_ml.joblib"
DEFAULT_REPORT = PROJECT_ROOT / "reports/k-fnspid-impact-training-report.json"
LABEL_ORDER = ("LOW", "MEDIUM", "HIGH", "CRITICAL")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the K-FNSPID market-impact model.")
    parser.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    rows = load_rows(args.dataset_dir)
    partitions = {
        name: [row for row in rows if row["split"] == name]
        for name in ("TRAIN", "VALIDATION", "TEST")
    }
    if len(partitions["TRAIN"]) < 100:
        raise SystemExit("K-FNSPID impact training requires at least 100 train rows")
    validation_model = build_model()
    validation_model.fit(
        [str(row["text"]) for row in partitions["TRAIN"]],
        [str(row["importance"]) for row in partitions["TRAIN"]],
    )
    validation_metrics = evaluate(validation_model, partitions["VALIDATION"])

    final_training_rows = [*partitions["TRAIN"], *partitions["VALIDATION"]]
    model = build_model()
    model.fit(
        [str(row["text"]) for row in final_training_rows],
        [str(row["importance"]) for row in final_training_rows],
    )
    version = f"k-fnspid-impact-tfidf-logreg-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    artifact = {
        "version": version,
        "trained_at": datetime.now(UTC).isoformat(),
        "model": model,
        "label_order": LABEL_ORDER,
        "dataset_manifest": json.loads((args.dataset_dir / "manifest.json").read_text()),
    }
    args.model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, args.model_path)

    report = {
        "schema_version": "k-fnspid-impact-training/v1",
        "version": version,
        "dataset_dir": str(args.dataset_dir.relative_to(PROJECT_ROOT)),
        "partition_count": {name: len(values) for name, values in partitions.items()},
        "final_training_count": len(final_training_rows),
        "label_distribution": dict(Counter(str(row["importance"]) for row in rows)),
        "validation": validation_metrics,
        "test": evaluate(model, partitions["TEST"]),
    }
    args.report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))


def build_model() -> Pipeline:
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=(2, 5),
                    min_df=2,
                    max_features=180_000,
                    sublinear_tf=True,
                ),
            ),
            (
                "classifier",
                OneVsRestClassifier(
                    LogisticRegression(
                        max_iter=1_500,
                        class_weight="balanced",
                        solver="liblinear",
                    )
                ),
            ),
        ]
    )


def load_rows(dataset_dir: Path) -> list[dict[str, Any]]:
    documents = {
        row["document_id"]: row
        for row in pq.read_table(dataset_dir / "documents.parquet").to_pylist()
    }
    splits = {
        row["document_id"]: row["split"]
        for row in pq.read_table(dataset_dir / "splits.parquet").to_pylist()
    }
    primary = {
        row["document_id"]: row
        for row in pq.read_table(dataset_dir / "document_entities.parquet").to_pylist()
        if row["relation"] == "PRIMARY"
    }
    rows: list[dict[str, Any]] = []
    for impact in pq.read_table(dataset_dir / "market_impacts.parquet").to_pylist():
        document = documents.get(impact["document_id"])
        entity = primary.get(impact["document_id"])
        if (
            document is None
            or entity is None
            or impact["importance"] not in LABEL_ORDER
            or impact["confounded"]
        ):
            continue
        rows.append(
            {
                "document_id": impact["document_id"],
                "text": " ".join(
                    part
                    for part in (
                        document["title"],
                        document["snippet"],
                        document["full_text"],
                        entity["stock_name"],
                    )
                    if part
                ),
                "importance": impact["importance"],
                "split": splits.get(impact["document_id"], "EMBARGO"),
            }
        )
    return rows


def evaluate(model: Pipeline, rows: list[dict[str, Any]]) -> dict[str, float | int]:
    if not rows:
        return {"sample_count": 0, "accuracy": 0.0, "macro_f1": 0.0, "quadratic_kappa": 0.0}
    expected = [str(row["importance"]) for row in rows]
    predicted = model.predict([str(row["text"]) for row in rows]).tolist()
    expected_ordinal = [LABEL_ORDER.index(label) for label in expected]
    predicted_ordinal = [LABEL_ORDER.index(label) for label in predicted]
    return {
        "sample_count": len(rows),
        "accuracy": float(accuracy_score(expected, predicted)),
        "macro_f1": float(f1_score(expected, predicted, labels=LABEL_ORDER, average="macro")),
        "quadratic_kappa": float(
            cohen_kappa_score(expected_ordinal, predicted_ordinal, weights="quadratic")
        ),
    }


if __name__ == "__main__":
    main()
