from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import FeatureUnion, Pipeline

from hannah_montana_ai.training.dataset import load_jsonl_payloads, resolve_jsonl_paths

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRAINING = PROJECT_ROOT / "data/training/financial_alert_full_content_gold.jsonl"
DEFAULT_GOLD = PROJECT_ROOT / "data/evaluation/financial_alert_real_disclosure_gold.jsonl"
DEFAULT_BASELINE = PROJECT_ROOT / "reports/ml-model-evaluation.json"
DEFAULT_MODEL = PROJECT_ROOT / "src/hannah_montana_ai/model_store/disclosure_importance_ml.joblib"
DEFAULT_REPORT = PROJECT_ROOT / "reports/disclosure-importance-training-report.json"
LABEL_ORDER = ("LOW", "MEDIUM", "HIGH", "CRITICAL")
INPUT_FEATURE_VERSION = "disclosure-validation-selected-view-v3"
MINIMUM_LABEL_F1 = 0.70
FEATURE_VIEWS = {
    "title_only": ("title",),
    "title_and_snippet": ("title", "snippet"),
    "title_snippet_full_content": ("title", "snippet", "full_content"),
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gold와 분리된 약한 감독 공시 중요도 모델을 학습한다."
    )
    parser.add_argument("--training-path", type=Path, default=DEFAULT_TRAINING)
    parser.add_argument("--gold-path", type=Path, default=DEFAULT_GOLD)
    parser.add_argument("--baseline-report", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    gold_rows = load_jsonl_payloads(args.gold_path)
    gold_urls = {str(row.get("source_url", "")) for row in gold_rows}
    source_rows = load_jsonl_payloads(args.training_path)
    excluded_gold_overlap = sum(
        row.get("source_type") == "DISCLOSURE" and str(row.get("source_url", "")) in gold_urls
        for row in source_rows
    )
    real_training_rows = _training_rows(source_rows, gold_urls)
    augmented_rows = _critical_augmentations()
    training_rows = [*real_training_rows, *augmented_rows]
    if len(training_rows) < 1_000 or len(gold_rows) < 500:
        raise SystemExit("공시 중요도 학습 1,000건과 독립 Gold 500건 이상이 필요합니다.")

    train_rows = [row for row in training_rows if str(row["published_at"]) < "20260101"]
    validation_rows = [row for row in training_rows if str(row["published_at"]) >= "20260101"]
    if len(validation_rows) < 100:
        raise SystemExit("2026년 시간 Validation이 100건 미만입니다.")

    candidates: dict[str, dict[str, Any]] = {}
    for name, fields in FEATURE_VIEWS.items():
        candidate = build_model()
        candidate.fit(
            [_model_text(row, fields) for row in train_rows],
            [str(row["importance"]) for row in train_rows],
        )
        temperature = _select_probability_temperature(candidate, validation_rows, fields)
        candidates[name] = {
            "fields": list(fields),
            "probability_temperature": temperature,
            "validation": _evaluate(candidate, validation_rows, temperature, fields),
        }
    selected_name = _select_feature_view(candidates)
    selected_fields = FEATURE_VIEWS[selected_name]
    probability_temperature = float(candidates[selected_name]["probability_temperature"])
    validation = candidates[selected_name]["validation"]

    final_model = build_model()
    final_model.fit(
        [_model_text(row, selected_fields) for row in training_rows],
        [str(row["importance"]) for row in training_rows],
    )
    gold = _evaluate(final_model, gold_rows, probability_temperature, selected_fields)
    baseline_report = json.loads(args.baseline_report.read_text(encoding="utf-8"))
    baseline_gold = baseline_report["real_disclosure_gold"]
    eligible = (
        float(gold["accuracy"]) >= 0.80
        and float(gold["macro_f1"]) >= 0.70
        and float(gold["accuracy"]) >= float(baseline_gold["importance_accuracy"])
        and float(gold["macro_f1"]) > float(baseline_gold["importance_macro_f1"])
        and all(
            float(metrics["f1"]) >= MINIMUM_LABEL_F1 for metrics in gold["label_metrics"].values()
        )
    )

    version = f"disclosure-importance-tfidf-logreg-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    payload = {
        "schema_version": "disclosure-importance-artifact/v1",
        "version": version,
        "input_feature_version": INPUT_FEATURE_VERSION,
        "selected_feature_view": selected_name,
        "selected_fields": list(selected_fields),
        "label_order": LABEL_ORDER,
        "probability_temperature": probability_temperature,
        "model": final_model,
    }
    args.model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(payload, args.model_path)
    artifact = _file_manifest(args.model_path)
    report = {
        "schema_version": "disclosure-importance-training/v1",
        "version": version,
        "input_feature_version": INPUT_FEATURE_VERSION,
        "feature_selection": {
            "partition": "VALIDATION",
            "criterion": "macro_f1, multiclass_brier_score, richer-context tie-break",
            "selected": selected_name,
            "selected_fields": list(selected_fields),
            "candidates": candidates,
            "gold_used_for_selection": False,
        },
        "training_source": _source_manifest(args.training_path),
        "gold_source": _source_manifest(args.gold_path),
        "gold_url_overlap_count": sum(
            str(row.get("source_url", "")) in gold_urls for row in training_rows
        ),
        "gold_url_excluded_count": excluded_gold_overlap,
        "augmentation": {
            "method": "terminal-risk lexical template augmentation",
            "synthetic_count": len(augmented_rows),
            "gold_rows_used": 0,
        },
        "calibration": {
            "method": "temperature-scaling",
            "selection_partition": "VALIDATION",
            "temperature": probability_temperature,
        },
        "partition_count": {
            "TRAIN": len(train_rows),
            "VALIDATION": len(validation_rows),
            "FINAL_TRAIN": len(training_rows),
            "GOLD_TEST": len(gold_rows),
        },
        "label_distribution": {
            "TRAIN": dict(Counter(str(row["importance"]) for row in train_rows)),
            "VALIDATION": dict(Counter(str(row["importance"]) for row in validation_rows)),
            "GOLD_TEST": dict(Counter(str(row["importance"]) for row in gold_rows)),
        },
        "validation": validation,
        "gold_test": gold,
        "baseline_gold_test": {
            "accuracy": baseline_gold["importance_accuracy"],
            "macro_f1": baseline_gold["importance_macro_f1"],
        },
        "artifact": artifact,
        "deployment_gate": {
            "minimum_gold_accuracy": 0.80,
            "minimum_gold_macro_f1": 0.70,
            "minimum_gold_label_f1": MINIMUM_LABEL_F1,
            "must_be_accuracy_noninferior_and_exceed_macro_f1": True,
            "eligible": eligible,
            "decision": "DEPLOY_DISCLOSURE_IMPORTANCE" if eligible else "KEEP_EXISTING_ANALYZER",
        },
    }
    args.report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))


def build_model() -> Pipeline:
    features = FeatureUnion(
        [
            (
                "char",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=(2, 5),
                    min_df=2,
                    max_features=140_000,
                    sublinear_tf=True,
                ),
            ),
            (
                "word",
                TfidfVectorizer(
                    analyzer="word",
                    ngram_range=(1, 2),
                    min_df=2,
                    max_features=40_000,
                    sublinear_tf=True,
                ),
            ),
        ]
    )
    classifier = OneVsRestClassifier(
        LogisticRegression(
            max_iter=1_500,
            class_weight="balanced",
            solver="liblinear",
            C=2.0,
        )
    )
    return Pipeline([("features", features), ("classifier", classifier)])


def _training_rows(rows: list[dict[str, Any]], gold_urls: set[str]) -> list[dict[str, Any]]:
    by_url: dict[str, dict[str, Any]] = {}
    for row in rows:
        source_url = str(row.get("source_url", ""))
        if (
            row.get("source_type") != "DISCLOSURE"
            or row.get("label_provenance") != "RULE_WEAK_SUPERVISION_V2"
            or row.get("source_review_status") != "UNREVIEWED_WEAK_LABEL"
            or row.get("importance") not in LABEL_ORDER
            or not source_url
            or source_url in gold_urls
        ):
            continue
        by_url[source_url] = row
    return sorted(by_url.values(), key=lambda row: str(row.get("content_hash", "")))


def _critical_augmentations() -> list[dict[str, Any]]:
    patterns = (
        "부도발생",
        "회생절차개시신청",
        "회생절차개시결정",
        "회생절차폐지신청",
        "파산신청",
        "파산절차관련사실발생",
        "횡령ㆍ배임혐의발생",
        "횡령ㆍ배임사실확인",
        "상장폐지사유발생",
        "감사의견거절",
    )
    rows: list[dict[str, Any]] = []
    for pattern_index, pattern in enumerate(patterns):
        for company_index in range(40):
            title = f"증강기업{company_index:03d} 주요사항보고서({pattern})"
            rows.append(
                {
                    "title": title,
                    "snippet": pattern,
                    "importance": "CRITICAL",
                    "published_at": "20240101",
                    "source_url": f"synthetic://critical/{pattern_index}/{company_index}",
                    "content_hash": sha256(title.encode()).hexdigest(),
                }
            )
    return rows


def _model_text(
    row: dict[str, Any],
    fields: tuple[str, ...] = FEATURE_VIEWS["title_snippet_full_content"],
) -> str:
    structured = " ".join(str(row.get(field, "")).strip() for field in fields if row.get(field))
    return structured or str(row.get("text", "")).strip()


def _select_feature_view(candidates: dict[str, dict[str, Any]]) -> str:
    """Validation만 사용해 입력 뷰를 고정한다."""
    return max(
        candidates,
        key=lambda name: (
            float(candidates[name]["validation"]["macro_f1"]),
            -float(candidates[name]["validation"]["multiclass_brier_score"]),
            len(candidates[name]["fields"]),
        ),
    )


def _evaluate(
    model: Pipeline,
    rows: list[dict[str, Any]],
    probability_temperature: float,
    fields: tuple[str, ...] = FEATURE_VIEWS["title_snippet_full_content"],
) -> dict[str, Any]:
    expected = [str(row["importance"]) for row in rows]
    probabilities = _calibrated_probabilities(
        model,
        [_model_text(row, fields) for row in rows],
        probability_temperature,
    )
    classes = [str(label) for label in model.classes_]
    predicted = [classes[int(index)] for index in probabilities.argmax(axis=1)]
    matrix = confusion_matrix(expected, predicted, labels=LABEL_ORDER)
    precision, recall, label_f1, support = precision_recall_fscore_support(
        expected,
        predicted,
        labels=LABEL_ORDER,
        zero_division=0,
    )
    calibration = _calibration_metrics(expected, classes, probabilities)
    return {
        "sample_count": len(rows),
        "accuracy": float(accuracy_score(expected, predicted)),
        "macro_f1": float(
            f1_score(expected, predicted, labels=LABEL_ORDER, average="macro", zero_division=0)
        ),
        "confusion_matrix": {
            truth: {
                prediction: int(matrix[row_index, column_index])
                for column_index, prediction in enumerate(LABEL_ORDER)
            }
            for row_index, truth in enumerate(LABEL_ORDER)
        },
        "label_metrics": {
            label: {
                "precision": float(precision[index]),
                "recall": float(recall[index]),
                "f1": float(label_f1[index]),
                "support": int(support[index]),
            }
            for index, label in enumerate(LABEL_ORDER)
        },
        **calibration,
    }


def _select_probability_temperature(
    model: Pipeline,
    rows: list[dict[str, Any]],
    fields: tuple[str, ...] = FEATURE_VIEWS["title_snippet_full_content"],
) -> float:
    expected = [str(row["importance"]) for row in rows]
    classes = [str(label) for label in model.classes_]
    expected_indices = np.asarray([classes.index(label) for label in expected])
    raw = np.clip(
        np.asarray(
            model.predict_proba([_model_text(row, fields) for row in rows]),
            dtype=float,
        ),
        1e-9,
        1.0,
    )
    best_temperature = 1.0
    best_loss = float("inf")
    for temperature in np.linspace(0.2, 3.0, 57):
        calibrated = _temperature_scale(raw, float(temperature))
        loss = float(-np.log(calibrated[np.arange(len(rows)), expected_indices]).mean())
        if loss < best_loss:
            best_loss = loss
            best_temperature = float(temperature)
    return best_temperature


def _calibrated_probabilities(
    model: Pipeline,
    texts: list[str],
    probability_temperature: float,
) -> np.ndarray:
    raw = np.clip(np.asarray(model.predict_proba(texts), dtype=float), 1e-9, 1.0)
    return _temperature_scale(raw, probability_temperature)


def _temperature_scale(probabilities: np.ndarray, temperature: float) -> np.ndarray:
    scaled = np.power(probabilities, 1.0 / max(temperature, 1e-6))
    return scaled / scaled.sum(axis=1, keepdims=True)


def _calibration_metrics(
    expected: list[str],
    classes: list[str],
    probabilities: np.ndarray,
    bins: int = 15,
) -> dict[str, float]:
    expected_indices = np.asarray([classes.index(label) for label in expected])
    predicted_indices = probabilities.argmax(axis=1)
    confidences = probabilities.max(axis=1)
    ece = 0.0
    for lower in np.linspace(0.0, 1.0, bins, endpoint=False):
        upper = lower + 1.0 / bins
        mask = (confidences >= lower) & (confidences < upper if upper < 1.0 else True)
        if not mask.any():
            continue
        ece += float(mask.mean()) * abs(
            float((predicted_indices[mask] == expected_indices[mask]).mean())
            - float(confidences[mask].mean())
        )
    one_hot = np.eye(len(classes))[expected_indices]
    return {
        "expected_calibration_error_15_bin": ece,
        "multiclass_brier_score": float(np.square(probabilities - one_hot).sum(axis=1).mean()),
    }


def _source_manifest(path: Path) -> dict[str, Any]:
    resolved = resolve_jsonl_paths(path) if path.suffix == ".jsonl" else [path]
    files = [path, *resolved] if resolved != [path] else [path]
    entries = [
        {
            "path": _display_path(file, path),
            **_file_manifest(file),
        }
        for file in files
    ]
    composite = sha256()
    for entry in entries:
        composite.update(f"{entry['path']}:{entry['sha256']}\n".encode())
    return {
        "path": str(path.relative_to(PROJECT_ROOT)),
        "bytes": sum(int(entry["bytes"]) for entry in entries),
        "sha256": (str(entries[0]["sha256"]) if len(entries) == 1 else composite.hexdigest()),
        "files": entries,
    }


def _display_path(file: Path, source_path: Path) -> str:
    try:
        return str(file.relative_to(PROJECT_ROOT))
    except ValueError:
        return str((source_path.parent / file.name).relative_to(PROJECT_ROOT))


def _file_manifest(path: Path) -> dict[str, str | int]:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return {
        "bytes": path.stat().st_size,
        "sha256": digest.hexdigest(),
    }


if __name__ == "__main__":
    main()
