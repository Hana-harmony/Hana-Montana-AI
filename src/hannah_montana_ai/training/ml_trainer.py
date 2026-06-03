from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import MultiLabelBinarizer

from hannah_montana_ai.training.dataset import LabeledAlert, load_labeled_alerts

_TOKEN_PATTERN = re.compile(r"[0-9]+(?:\.[0-9]+)?%?|[A-Za-z][A-Za-z0-9+.-]*|[가-힣]+")
_NON_TOKEN_CHAR_PATTERN = re.compile(r"[^0-9a-z가-힣]+")

FINANCIAL_DOMAIN_TERMS: tuple[str, ...] = (
    "감자",
    "거래정지",
    "계약",
    "공급계약",
    "공시",
    "금리",
    "관세",
    "단일판매",
    "배당",
    "변동성",
    "분기보고서",
    "빚투",
    "소송등",
    "상장폐지",
    "실적",
    "영업이익",
    "유상증자",
    "임상",
    "임원주요주주",
    "자사주",
    "자기주식",
    "자기주식처분",
    "자기주식취득",
    "잠정실적",
    "전환사채",
    "지분취득",
    "지분처분",
    "턴어라운드",
    "판매실적",
    "주권매매거래정지",
    "주요사항보고서",
    "주식분할",
    "주주총회",
    "출자증권",
    "타법인주식",
    "증자",
    "수주",
    "횡령배임",
    "합병",
    "회사분할",
    "사업재편",
    "환율",
    "고환율",
    "흑자전환",
)


@dataclass(frozen=True)
class MlTrainingReport:
    version: str
    trained_at: str
    sample_count: int
    training_sources: list[str]
    event_label_distribution: dict[str, int]
    sentiment_label_distribution: dict[str, int]
    importance_label_distribution: dict[str, int]
    validation: MlValidationReport

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "trained_at": self.trained_at,
            "sample_count": self.sample_count,
            "training_sources": self.training_sources,
            "event_label_distribution": self.event_label_distribution,
            "sentiment_label_distribution": self.sentiment_label_distribution,
            "importance_label_distribution": self.importance_label_distribution,
            "validation": self.validation.to_dict(),
        }


@dataclass(frozen=True)
class MlValidationReport:
    sample_count: int
    train_sample_count: int
    event_subset_recall: float
    event_macro_f1: float
    sentiment_accuracy: float
    importance_accuracy: float
    event_label_metrics: dict[str, dict[str, float | int]]
    sentiment_confusion_matrix: dict[str, dict[str, int]]
    importance_confusion_matrix: dict[str, dict[str, int]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "sample_count": self.sample_count,
            "train_sample_count": self.train_sample_count,
            "event_subset_recall": self.event_subset_recall,
            "event_macro_f1": self.event_macro_f1,
            "sentiment_accuracy": self.sentiment_accuracy,
            "importance_accuracy": self.importance_accuracy,
            "event_label_metrics": self.event_label_metrics,
            "sentiment_confusion_matrix": self.sentiment_confusion_matrix,
            "importance_confusion_matrix": self.importance_confusion_matrix,
        }


def train_ml_model(training_paths: list[Path], model_path: Path) -> MlTrainingReport:
    samples = _load_samples(training_paths)
    if len(samples) < 30:
        raise ValueError("ML training requires at least 30 labeled samples")

    validation = _validate_holdout(samples)
    event_texts = [_event_text(sample.text, sample.source_type) for sample in samples]
    texts = [sample.text for sample in samples]
    importance_texts = [_importance_text(sample.text, sample.source_type) for sample in samples]
    event_targets = [sample.tags for sample in samples]
    sentiment_targets = [sample.sentiment for sample in samples]
    importance_targets = [sample.importance for sample in samples]

    event_binarizer = MultiLabelBinarizer()
    event_matrix = event_binarizer.fit_transform(event_targets)

    event_model = Pipeline(
        [
            ("tfidf", _hybrid_vectorizer()),
            (
                "classifier",
                OneVsRestClassifier(
                    LogisticRegression(
                        max_iter=1000,
                        class_weight="balanced",
                    )
                ),
            ),
        ]
    )
    sentiment_model = Pipeline(
        [
            ("tfidf", _hybrid_vectorizer()),
            ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )
    importance_model = Pipeline(
        [
            ("tfidf", _hybrid_vectorizer()),
            ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )

    event_model.fit(event_texts, event_matrix)
    sentiment_model.fit(texts, sentiment_targets)
    importance_model.fit(importance_texts, importance_targets)

    trained_at = datetime.now(UTC).isoformat()
    version = f"financial-ml-tfidf-logreg-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    artifact = {
        "version": version,
        "trained_at": trained_at,
        "event_model": event_model,
        "event_binarizer": event_binarizer,
        "sentiment_model": sentiment_model,
        "importance_model": importance_model,
        "event_probability_threshold": 0.35,
        "sample_count": len(samples),
        "training_sources": _training_source_paths(training_paths),
    }
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, model_path)

    return MlTrainingReport(
        version=version,
        trained_at=trained_at,
        sample_count=len(samples),
        training_sources=artifact["training_sources"],
        event_label_distribution=_event_distribution(samples),
        sentiment_label_distribution=dict(Counter(sentiment_targets)),
        importance_label_distribution=dict(Counter(importance_targets)),
        validation=validation,
    )


def _load_samples(paths: list[Path]) -> list[LabeledAlert]:
    samples: list[LabeledAlert] = []
    seen: set[str] = set()
    for path in paths:
        if not path.exists():
            continue
        for sample in load_labeled_alerts(path):
            key = f"{sample.source_type}:{sample.text}"
            if key in seen:
                continue
            samples.append(sample)
            seen.add(key)
    return samples


def _training_source_paths(paths: list[Path]) -> list[str]:
    repository_root = Path.cwd().resolve()
    sources: list[str] = []
    for path in paths:
        if not path.exists():
            continue
        resolved_path = path.resolve()
        try:
            sources.append(str(resolved_path.relative_to(repository_root)))
        except ValueError:
            sources.append(str(resolved_path))
    return sources


def _char_vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(2, 5),
        min_df=1,
        max_features=120_000,
        sublinear_tf=True,
    )


def _hybrid_vectorizer() -> FeatureUnion:
    return FeatureUnion(
        [
            (
                "char_wb",
                _char_vectorizer(),
            ),
            (
                "financial_word",
                TfidfVectorizer(
                    tokenizer=financial_tokenize,
                    token_pattern=None,
                    ngram_range=(1, 2),
                    min_df=1,
                    max_features=80_000,
                    sublinear_tf=True,
                    lowercase=False,
                ),
            ),
        ],
        transformer_weights={
            "char_wb": 1.0,
            "financial_word": 1.2,
        },
    )


def financial_tokenize(text: str) -> list[str]:
    normalized_text = text.lower()
    tokens = _TOKEN_PATTERN.findall(normalized_text)
    compact_text = _NON_TOKEN_CHAR_PATTERN.sub("", normalized_text)

    # 한국어 금융 복합어는 띄어쓰기와 조사 때문에 일반 token split만으로 놓치기 쉽다.
    domain_tokens = [
        f"finance:{term}"
        for term in FINANCIAL_DOMAIN_TERMS
        if _NON_TOKEN_CHAR_PATTERN.sub("", term) in compact_text
    ]
    return [*tokens, *domain_tokens]


def _importance_text(text: str, source_type: str) -> str:
    return f"source_type={source_type} {text}"


def _event_text(text: str, source_type: str) -> str:
    return f"source_type={source_type} {text}"


def _event_distribution(samples: list[LabeledAlert]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for sample in samples:
        counter.update(sample.tags)
    return dict(counter)


def _validate_holdout(samples: list[LabeledAlert]) -> MlValidationReport:
    stratify_labels = _safe_stratify_labels(samples)
    train_samples, validation_samples = train_test_split(
        samples,
        test_size=0.2,
        random_state=42,
        stratify=stratify_labels,
    )

    event_binarizer = MultiLabelBinarizer()
    event_train_matrix = event_binarizer.fit_transform([sample.tags for sample in train_samples])

    event_model = _event_model()
    sentiment_model = _single_label_model()
    importance_model = _importance_model()

    event_model.fit(
        [_event_text(sample.text, sample.source_type) for sample in train_samples],
        event_train_matrix,
    )
    sentiment_model.fit(
        [sample.text for sample in train_samples],
        [sample.sentiment for sample in train_samples],
    )
    importance_model.fit(
        [_importance_text(sample.text, sample.source_type) for sample in train_samples],
        [sample.importance for sample in train_samples],
    )

    probabilities = event_model.predict_proba(
        [_event_text(sample.text, sample.source_type) for sample in validation_samples]
    )
    event_classes = list(event_binarizer.classes_)
    predicted_event_tags = [
        _event_tags_from_probabilities(event_classes, row, threshold=0.35)
        for row in probabilities
    ]
    expected_event_tags = [set(sample.tags) for sample in validation_samples]

    predicted_sentiments = list(
        sentiment_model.predict([sample.text for sample in validation_samples])
    )
    expected_sentiments = [sample.sentiment for sample in validation_samples]

    predicted_importance = list(
        importance_model.predict(
            [_importance_text(sample.text, sample.source_type) for sample in validation_samples]
        )
    )
    expected_importance = [sample.importance for sample in validation_samples]

    event_metrics = _event_label_metrics(expected_event_tags, predicted_event_tags)
    return MlValidationReport(
        sample_count=len(validation_samples),
        train_sample_count=len(train_samples),
        event_subset_recall=_subset_recall(expected_event_tags, predicted_event_tags),
        event_macro_f1=_macro_f1(event_metrics),
        sentiment_accuracy=_accuracy(expected_sentiments, predicted_sentiments),
        importance_accuracy=_accuracy(expected_importance, predicted_importance),
        event_label_metrics=event_metrics,
        sentiment_confusion_matrix=_confusion_matrix(expected_sentiments, predicted_sentiments),
        importance_confusion_matrix=_confusion_matrix(expected_importance, predicted_importance),
    )


def _event_model() -> Pipeline:
    return Pipeline(
        [
            ("tfidf", _hybrid_vectorizer()),
            (
                "classifier",
                OneVsRestClassifier(
                    LogisticRegression(
                        max_iter=1000,
                        class_weight="balanced",
                    )
                ),
            ),
        ]
    )


def _single_label_model() -> Pipeline:
    return Pipeline(
        [
            ("tfidf", _hybrid_vectorizer()),
            ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )


def _importance_model() -> Pipeline:
    return Pipeline(
        [
            ("tfidf", _hybrid_vectorizer()),
            ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )


def _event_tags_from_probabilities(
    classes: list[str],
    probabilities: Any,
    threshold: float,
) -> set[str]:
    tags = {
        str(label)
        for label, probability in zip(classes, probabilities, strict=True)
        if probability >= threshold
    }
    if tags:
        return tags
    top_index = int(max(range(len(probabilities)), key=lambda index: probabilities[index]))
    return {str(classes[top_index])} if classes else {"GENERAL_MARKET"}


def _event_label_metrics(
    expected_tags: list[set[str]],
    predicted_tags: list[set[str]],
) -> dict[str, dict[str, float | int]]:
    labels = sorted(set().union(*expected_tags, *predicted_tags))
    metrics: dict[str, dict[str, float | int]] = {}
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
        metrics[label] = {
            "precision": precision,
            "recall": recall,
            "f1": _f1(precision, recall),
            "support": sum(1 for expected in expected_tags if label in expected),
        }
    return metrics


def _subset_recall(expected_tags: list[set[str]], predicted_tags: list[set[str]]) -> float:
    hits = sum(
        1 for expected, predicted in zip(expected_tags, predicted_tags, strict=True)
        if expected.issubset(predicted)
    )
    return _safe_divide(hits, len(expected_tags))


def _macro_f1(metrics: dict[str, dict[str, float | int]]) -> float:
    if not metrics:
        return 0.0
    return sum(float(metric["f1"]) for metric in metrics.values()) / len(metrics)


def _accuracy(expected: list[str], predicted: list[str]) -> float:
    hits = sum(1 for left, right in zip(expected, predicted, strict=True) if left == right)
    return _safe_divide(hits, len(expected))


def _confusion_matrix(expected: list[str], predicted: list[str]) -> dict[str, dict[str, int]]:
    matrix: dict[str, dict[str, int]] = {}
    for expected_label, predicted_label in zip(expected, predicted, strict=True):
        matrix.setdefault(expected_label, {})
        matrix[expected_label][predicted_label] = matrix[expected_label].get(predicted_label, 0) + 1
    return {
        expected_label: dict(sorted(predictions.items()))
        for expected_label, predictions in sorted(matrix.items())
    }


def _f1(precision: float, recall: float) -> float:
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _safe_divide(numerator: int | float, denominator: int | float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _safe_stratify_labels(samples: list[LabeledAlert]) -> list[str] | None:
    labels = [sample.tags[0] for sample in samples]
    counts = Counter(labels)
    if min(counts.values(), default=0) < 2:
        return None
    return labels
