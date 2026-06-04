from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any, NamedTuple

from hannah_montana_ai.services.model import MachineLearningFinancialNlpModel
from hannah_montana_ai.training.dataset import LabeledAlert, load_labeled_alerts

MODEL_CONFIDENCE_CALIBRATION_SCHEMA_VERSION = "model-confidence-calibration/v1"


class _EventError(NamedTuple):
    error_score: float
    error_type: str
    label: str
    probability: float
    expected: bool
    sample: LabeledAlert


def build_model_confidence_calibration_report(
    evaluation_paths: Mapping[str, Path],
    model_path: Path,
    *,
    bin_count: int = 10,
    high_confidence_threshold: float = 0.85,
    max_error_examples: int = 20,
) -> dict[str, Any]:
    model = MachineLearningFinancialNlpModel(model_path)
    datasets = {
        name: _calibrate_dataset(
            samples=load_labeled_alerts(path) if path.exists() else [],
            model=model,
            bin_count=bin_count,
            high_confidence_threshold=high_confidence_threshold,
            max_error_examples=max_error_examples,
        )
        for name, path in evaluation_paths.items()
    }
    return {
        "schema_version": MODEL_CONFIDENCE_CALIBRATION_SCHEMA_VERSION,
        "model_version": model.version,
        "model_path": _report_path(model_path),
        "bin_count": bin_count,
        "high_confidence_threshold": high_confidence_threshold,
        "datasets": datasets,
        "calibration_policy": (
            "confidence metrics are release monitoring signals and do not create "
            "or promote labels"
        ),
    }


def write_model_confidence_calibration_report(
    path: Path,
    report: dict[str, Any],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _calibrate_dataset(
    samples: Sequence[LabeledAlert],
    model: MachineLearningFinancialNlpModel,
    bin_count: int,
    high_confidence_threshold: float,
    max_error_examples: int,
) -> dict[str, Any]:
    event_decisions: list[tuple[str, float, bool, LabeledAlert]] = []
    sentiment_rows: list[dict[str, Any]] = []
    importance_rows: list[dict[str, Any]] = []

    for sample in samples:
        event_scores = model.event_tag_probabilities(sample.text, sample.source_type)
        event_decisions.extend(
            (
                label,
                probability,
                label in sample.tags,
                sample,
            )
            for label, probability in event_scores.items()
        )
        sentiment_rows.append(
            _class_probability_row(
                probabilities=model.sentiment_probabilities(sample.text),
                expected_label=sample.sentiment,
                sample=sample,
            )
        )
        importance_rows.append(
            _class_probability_row(
                probabilities=model.importance_probabilities(
                    sample.text,
                    sample.source_type,
                ),
                expected_label=sample.importance,
                sample=sample,
            )
        )

    return {
        "sample_count": len(samples),
        "event_tags": _event_calibration(
            event_decisions,
            bin_count,
            high_confidence_threshold,
            max_error_examples,
        ),
        "sentiment": _class_calibration(
            sentiment_rows,
            bin_count,
            high_confidence_threshold,
            max_error_examples,
        ),
        "importance": _class_calibration(
            importance_rows,
            bin_count,
            high_confidence_threshold,
            max_error_examples,
        ),
    }


def _event_calibration(
    decisions: Sequence[tuple[str, float, bool, LabeledAlert]],
    bin_count: int,
    high_confidence_threshold: float,
    max_error_examples: int,
) -> dict[str, Any]:
    labels = sorted({label for label, _, _, _ in decisions})
    low_confidence_threshold = 1.0 - high_confidence_threshold
    by_label: dict[str, Any] = {}
    for label in labels:
        label_decisions = [
            (probability, expected)
            for decision_label, probability, expected, _ in decisions
            if decision_label == label
        ]
        by_label[label] = {
            "decision_count": len(label_decisions),
            "positive_count": sum(1 for _, expected in label_decisions if expected),
            "brier_score": _round(_binary_brier_score(label_decisions)),
            "expected_calibration_error": _round(
                _expected_calibration_error(label_decisions, bin_count)
            ),
            "high_confidence_false_positive_count": sum(
                1
                for probability, expected in label_decisions
                if probability >= high_confidence_threshold and not expected
            ),
            "high_confidence_false_negative_count": sum(
                1
                for probability, expected in label_decisions
                if probability <= low_confidence_threshold and expected
            ),
        }

    overall_decisions = [
        (probability, expected) for _, probability, expected, _ in decisions
    ]
    return {
        "decision_count": len(overall_decisions),
        "brier_score": _round(_binary_brier_score(overall_decisions)),
        "expected_calibration_error": _round(
            _expected_calibration_error(overall_decisions, bin_count)
        ),
        "labels": by_label,
        "high_confidence_errors": _event_error_examples(
            decisions,
            high_confidence_threshold,
            max_error_examples,
        ),
    }


def _class_calibration(
    rows: Sequence[dict[str, Any]],
    bin_count: int,
    high_confidence_threshold: float,
    max_error_examples: int,
) -> dict[str, Any]:
    top_confidence_rows = [
        (float(row["confidence"]), bool(row["correct"])) for row in rows
    ]
    correct_count = sum(1 for _, correct in top_confidence_rows if correct)
    high_confidence_errors = [
        row for row in rows if row["confidence"] >= high_confidence_threshold and not row["correct"]
    ]
    return {
        "sample_count": len(rows),
        "accuracy": _round(_safe_divide(correct_count, len(rows))),
        "average_top_confidence": _round(
            _average(float(row["confidence"]) for row in rows)
        ),
        "top_confidence_ece": _round(
            _expected_calibration_error(top_confidence_rows, bin_count)
        ),
        "multiclass_brier_score": _round(
            _average(float(row["brier_score"]) for row in rows)
        ),
        "high_confidence_error_count": len(high_confidence_errors),
        "high_confidence_errors": [
            _class_error_example(row)
            for row in sorted(
                high_confidence_errors,
                key=lambda row: (-float(row["confidence"]), str(row["sample"].text)),
            )[:max_error_examples]
        ],
    }


def _class_probability_row(
    probabilities: Mapping[str, float],
    expected_label: str,
    sample: LabeledAlert,
) -> dict[str, Any]:
    predicted_label, confidence = _top_label(probabilities)
    return {
        "sample": sample,
        "expected_label": expected_label,
        "predicted_label": predicted_label,
        "confidence": confidence,
        "correct": predicted_label == expected_label,
        "brier_score": _multiclass_brier_score(probabilities, expected_label),
    }


def _event_error_examples(
    decisions: Sequence[tuple[str, float, bool, LabeledAlert]],
    high_confidence_threshold: float,
    max_error_examples: int,
) -> list[dict[str, Any]]:
    low_confidence_threshold = 1.0 - high_confidence_threshold
    errors = [
        _EventError(
            error_score=probability if not expected else 1.0 - probability,
            error_type=(
                "high_confidence_false_positive"
                if probability >= high_confidence_threshold
                else "high_confidence_false_negative"
            ),
            label=label,
            probability=_round(probability),
            expected=expected,
            sample=sample,
        )
        for label, probability, expected, sample in decisions
        if (
            (probability >= high_confidence_threshold and not expected)
            or (probability <= low_confidence_threshold and expected)
        )
    ]
    return [
        _event_error_example(error)
        for error in sorted(
            errors,
            key=lambda row: (-row.error_score, row.sample.text),
        )[:max_error_examples]
    ]


def _event_error_example(row: _EventError) -> dict[str, Any]:
    sample = row.sample
    return {
        "error_type": row.error_type,
        "label": row.label,
        "probability": row.probability,
        "expected_tags": sample.tags,
        "source_type": sample.source_type,
        "stock_code": sample.stock_code,
        "stock_name": sample.stock_name,
        "text": sample.text,
    }


def _class_error_example(row: dict[str, Any]) -> dict[str, Any]:
    sample = row["sample"]
    return {
        "expected_label": row["expected_label"],
        "predicted_label": row["predicted_label"],
        "confidence": _round(float(row["confidence"])),
        "source_type": sample.source_type,
        "stock_code": sample.stock_code,
        "stock_name": sample.stock_name,
        "text": sample.text,
    }


def _expected_calibration_error(
    decisions: Sequence[tuple[float, bool]],
    bin_count: int,
) -> float:
    if not decisions:
        return 0.0
    bins: list[list[tuple[float, bool]]] = [[] for _ in range(bin_count)]
    for confidence, expected in decisions:
        bin_index = min(int(confidence * bin_count), bin_count - 1)
        bins[bin_index].append((confidence, expected))
    return sum(
        len(bucket)
        / len(decisions)
        * abs(_average(confidence for confidence, _ in bucket) - _observed_rate(bucket))
        for bucket in bins
        if bucket
    )


def _binary_brier_score(decisions: Sequence[tuple[float, bool]]) -> float:
    return _average((probability - float(expected)) ** 2 for probability, expected in decisions)


def _multiclass_brier_score(
    probabilities: Mapping[str, float],
    expected_label: str,
) -> float:
    return sum(
        (probability - (1.0 if label == expected_label else 0.0)) ** 2
        for label, probability in probabilities.items()
    )


def _observed_rate(decisions: Sequence[tuple[float, bool]]) -> float:
    return _safe_divide(sum(1 for _, expected in decisions if expected), len(decisions))


def _top_label(scores: Mapping[str, float]) -> tuple[str, float]:
    if not scores:
        return "", 0.0
    label, score = max(scores.items(), key=lambda item: item[1])
    return label, score


def _average(values: Iterable[float]) -> float:
    collected_values = list(values)
    if not collected_values:
        return 0.0
    return sum(collected_values) / len(collected_values)


def _safe_divide(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _round(value: float) -> float:
    return round(value, 6)


def _report_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)
