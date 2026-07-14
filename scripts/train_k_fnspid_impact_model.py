from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

import joblib
import pyarrow.parquet as pq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, cohen_kappa_score, f1_score
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline

from hannah_montana_ai.services.impact_model_features import (
    IMPACT_INPUT_FEATURE_VERSION,
    build_impact_model_text,
)
from hannah_montana_ai.training.k_fnspid.sampling import (
    select_unconfounded_representatives,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = PROJECT_ROOT / "data/k_fnspid/v3"
DEFAULT_MODEL = PROJECT_ROOT / "src/hannah_montana_ai/model_store/k_fnspid_impact_ml.joblib"
DEFAULT_REPORT = PROJECT_ROOT / "reports/k-fnspid-impact-training-report.json"
DEFAULT_PREDICTIONS = PROJECT_ROOT / "reports/k-fnspid-impact-test-predictions.jsonl"
LABEL_ORDER = ("LOW", "MEDIUM", "HIGH", "CRITICAL")


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the K-FNSPID market-impact model.")
    parser.add_argument("--dataset-dir", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--predictions-path", type=Path, default=DEFAULT_PREDICTIONS)
    args = parser.parse_args()

    rows = load_rows(args.dataset_dir)
    dataset_manifest = compact_dataset_manifest(args.dataset_dir)
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
    test_metrics = evaluate(validation_model, partitions["TEST"])
    predictions_manifest = write_predictions(
        args.predictions_path,
        validation_model,
        partitions["TEST"],
    )

    # 배포 산출물만 검증 분할을 추가 학습하며 논문 Test는 TRAIN 전용 모델로 측정한다.
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
        "input_feature_version": IMPACT_INPUT_FEATURE_VERSION,
    }
    args.model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, args.model_path)
    artifact_manifest = {
        "path": str(args.model_path.relative_to(PROJECT_ROOT)),
        "bytes": args.model_path.stat().st_size,
        "sha256": _file_sha256(args.model_path),
    }

    report = {
        "schema_version": "k-fnspid-impact-training/v1",
        "version": version,
        "dataset_dir": str(args.dataset_dir.relative_to(PROJECT_ROOT)),
        "dataset_manifest": dataset_manifest,
        "artifact": artifact_manifest,
        "input_feature_version": IMPACT_INPUT_FEATURE_VERSION,
        "partition_count": {name: len(values) for name, values in partitions.items()},
        "final_training_count": len(final_training_rows),
        "evaluation_training_count": len(partitions["TRAIN"]),
        "evaluation_protocol": "TRAIN fit, VALIDATION selection, frozen TEST evaluation",
        "label_distribution": dict(Counter(str(row["importance"]) for row in rows)),
        "validation": validation_metrics,
        "test": test_metrics,
        "test_predictions": predictions_manifest,
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


def load_rows(
    dataset_dir: Path,
    *,
    include_full_text: bool = True,
    include_source_prefix: bool = True,
) -> list[dict[str, Any]]:
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
    candidates: list[dict[str, Any]] = []
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
        candidates.append(
            {
                "document_id": impact["document_id"],
                "event_cluster_id": document["event_cluster_id"],
                "stock_code": entity["stock_code"],
                "effective_trade_date": impact["effective_trade_date"],
                "source_type": document["source_type"],
                "text": _impact_text(
                    document,
                    entity,
                    include_full_text=include_full_text,
                    include_source_prefix=include_source_prefix,
                ),
                "importance": impact["importance"],
                "split": splits.get(impact["document_id"], "EMBARGO"),
            }
        )
    return select_unconfounded_representatives(candidates)


def _impact_text(
    document: dict[str, Any],
    entity: dict[str, Any],
    *,
    include_full_text: bool,
    include_source_prefix: bool,
) -> str:
    text = " ".join(
        str(part)
        for part in (
            document["title"],
            document["snippet"],
            document["full_text"] if include_full_text else "",
            entity["stock_name"],
        )
        if part
    )
    if not include_source_prefix:
        return text
    return build_impact_model_text(text, str(document["source_type"]))


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
        "macro_f1": float(
            f1_score(
                expected,
                predicted,
                labels=LABEL_ORDER,
                average="macro",
                zero_division=0,
            )
        ),
        "quadratic_kappa": float(
            cohen_kappa_score(expected_ordinal, predicted_ordinal, weights="quadratic")
        ),
    }


def write_predictions(
    path: Path,
    model: Pipeline,
    rows: list[dict[str, Any]],
) -> dict[str, str | int]:
    texts = [str(row["text"]) for row in rows]
    predictions = model.predict(texts).tolist()
    probability_rows = model.predict_proba(texts).tolist()
    classes = [str(label) for label in model.classes_]
    lines = [
        json.dumps(
            {
                "document_id": row["document_id"],
                "stock_code": row["stock_code"],
                "effective_trade_date": row["effective_trade_date"],
                "source_type": row["source_type"],
                "expected": row["importance"],
                "predicted": predicted,
                "probabilities": {
                    label: round(float(value), 8)
                    for label, value in zip(classes, probabilities, strict=True)
                },
            },
            ensure_ascii=False,
        )
        + "\n"
        for row, predicted, probabilities in zip(rows, predictions, probability_rows, strict=True)
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(lines), encoding="utf-8")
    return {
        "path": str(path.relative_to(PROJECT_ROOT)),
        "sample_count": len(rows),
        "bytes": path.stat().st_size,
        "sha256": sha256(path.read_bytes()).hexdigest(),
    }


def compact_dataset_manifest(dataset_dir: Path) -> dict[str, str | int]:
    path = dataset_dir.resolve() / "manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("status") != "pass" or not payload.get("dataset_version"):
        raise SystemExit("검증된 K-FNSPID manifest만 학습에 사용할 수 있습니다.")
    return {
        "path": str(path.relative_to(PROJECT_ROOT)),
        "dataset_version": str(payload["dataset_version"]),
        "bytes": path.stat().st_size,
        "sha256": _file_sha256(path),
    }


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    main()
