from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from hannah_montana_ai.domain.schemas import AlertAnalysisRequest, StockCandidate
from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.training.dataset import LabeledAlert


@dataclass(frozen=True)
class LabelMetric:
    precision: float
    recall: float
    f1: float
    support: int

    def to_dict(self) -> dict[str, float | int]:
        return {
            "precision": self.precision,
            "recall": self.recall,
            "f1": self.f1,
            "support": self.support,
        }


@dataclass(frozen=True)
class EvaluationResult:
    sample_count: int
    event_tag_recall: float
    sentiment_accuracy: float
    importance_accuracy: float
    stock_accuracy: float
    event_label_metrics: dict[str, LabelMetric] = field(default_factory=dict)
    event_macro_f1: float = 0.0
    sentiment_confusion_matrix: dict[str, dict[str, int]] = field(default_factory=dict)
    importance_confusion_matrix: dict[str, dict[str, int]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sample_count": self.sample_count,
            "event_tag_recall": self.event_tag_recall,
            "sentiment_accuracy": self.sentiment_accuracy,
            "importance_accuracy": self.importance_accuracy,
            "stock_accuracy": self.stock_accuracy,
            "event_macro_f1": self.event_macro_f1,
            "event_label_metrics": {
                label: metric.to_dict() for label, metric in self.event_label_metrics.items()
            },
            "sentiment_confusion_matrix": self.sentiment_confusion_matrix,
            "importance_confusion_matrix": self.importance_confusion_matrix,
        }


def evaluate_alert_analyzer(
    samples: list[LabeledAlert],
    analyzer: AlertAnalyzer,
) -> EvaluationResult:
    event_hits = 0
    sentiment_hits = 0
    importance_hits = 0
    stock_hits = 0
    expected_event_tags: list[set[str]] = []
    predicted_event_tags: list[set[str]] = []
    sentiment_pairs: list[tuple[str, str]] = []
    importance_pairs: list[tuple[str, str]] = []

    for sample in samples:
        request = _request_from_sample(sample)
        prediction = analyzer.analyze(request)
        expected_tags = set(sample.tags)
        predicted_tags = set(prediction.event_tags)
        expected_event_tags.append(expected_tags)
        predicted_event_tags.append(predicted_tags)
        sentiment_pairs.append((sample.sentiment, prediction.sentiment))
        importance_pairs.append((sample.importance, prediction.importance))
        if expected_tags.issubset(predicted_tags):
            event_hits += 1
        if prediction.sentiment == sample.sentiment:
            sentiment_hits += 1
        if prediction.importance == sample.importance:
            importance_hits += 1
        if prediction.stock_code == sample.stock_code:
            stock_hits += 1

    total = len(samples)
    event_label_metrics = _event_label_metrics(expected_event_tags, predicted_event_tags)
    return EvaluationResult(
        sample_count=total,
        event_tag_recall=event_hits / total,
        sentiment_accuracy=sentiment_hits / total,
        importance_accuracy=importance_hits / total,
        stock_accuracy=stock_hits / total,
        event_label_metrics=event_label_metrics,
        event_macro_f1=_macro_f1(event_label_metrics),
        sentiment_confusion_matrix=_confusion_matrix(sentiment_pairs),
        importance_confusion_matrix=_confusion_matrix(importance_pairs),
    )


def _request_from_sample(sample: LabeledAlert) -> AlertAnalysisRequest:
    stock_universe = []
    if sample.stock_code and sample.stock_name:
        stock_universe.append(
            StockCandidate(
                stock_code=sample.stock_code,
                stock_name=sample.stock_name,
                stock_name_en=sample.stock_name,
                aliases=[],
            )
        )

    return AlertAnalysisRequest.model_validate(
        {
            "source_type": sample.source_type,
            "title": sample.text,
            "snippet": "",
            "original_url": "https://example.com/evaluation",
            "stock_universe": [stock.model_dump() for stock in stock_universe],
        }
    )


def _event_label_metrics(
    expected_tags: list[set[str]],
    predicted_tags: list[set[str]],
) -> dict[str, LabelMetric]:
    labels = sorted(set().union(*expected_tags, *predicted_tags))
    metrics: dict[str, LabelMetric] = {}
    for label in labels:
        true_positive = sum(
            1 for expected, predicted in zip(expected_tags, predicted_tags, strict=True)
            if label in expected and label in predicted
        )
        false_positive = sum(
            1 for expected, predicted in zip(expected_tags, predicted_tags, strict=True)
            if label not in expected and label in predicted
        )
        false_negative = sum(
            1 for expected, predicted in zip(expected_tags, predicted_tags, strict=True)
            if label in expected and label not in predicted
        )
        precision = _safe_divide(true_positive, true_positive + false_positive)
        recall = _safe_divide(true_positive, true_positive + false_negative)
        metrics[label] = LabelMetric(
            precision=precision,
            recall=recall,
            f1=_f1(precision, recall),
            support=sum(1 for expected in expected_tags if label in expected),
        )
    return metrics


def _confusion_matrix(pairs: list[tuple[str, str]]) -> dict[str, dict[str, int]]:
    matrix: defaultdict[str, defaultdict[str, int]] = defaultdict(lambda: defaultdict(int))
    for expected, predicted in pairs:
        matrix[expected][predicted] += 1
    return {
        expected: dict(sorted(predictions.items()))
        for expected, predictions in sorted(matrix.items())
    }


def _macro_f1(metrics: dict[str, LabelMetric]) -> float:
    if not metrics:
        return 0.0
    return sum(metric.f1 for metric in metrics.values()) / len(metrics)


def _f1(precision: float, recall: float) -> float:
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _safe_divide(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator
