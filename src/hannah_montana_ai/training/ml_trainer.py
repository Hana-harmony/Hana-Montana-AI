from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MultiLabelBinarizer

from hannah_montana_ai.training.dataset import LabeledAlert, load_labeled_alerts


@dataclass(frozen=True)
class MlTrainingReport:
    version: str
    trained_at: str
    sample_count: int
    training_sources: list[str]
    event_label_distribution: dict[str, int]
    sentiment_label_distribution: dict[str, int]
    importance_label_distribution: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "trained_at": self.trained_at,
            "sample_count": self.sample_count,
            "training_sources": self.training_sources,
            "event_label_distribution": self.event_label_distribution,
            "sentiment_label_distribution": self.sentiment_label_distribution,
            "importance_label_distribution": self.importance_label_distribution,
        }


def train_ml_model(training_paths: list[Path], model_path: Path) -> MlTrainingReport:
    samples = _load_samples(training_paths)
    if len(samples) < 30:
        raise ValueError("ML training requires at least 30 labeled samples")

    texts = [sample.text for sample in samples]
    importance_texts = [_importance_text(sample.text, sample.source_type) for sample in samples]
    event_targets = [sample.tags for sample in samples]
    sentiment_targets = [sample.sentiment for sample in samples]
    importance_targets = [sample.importance for sample in samples]

    event_binarizer = MultiLabelBinarizer()
    event_matrix = event_binarizer.fit_transform(event_targets)

    event_model = Pipeline(
        [
            ("tfidf", _vectorizer()),
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
            ("tfidf", _vectorizer()),
            ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )
    importance_model = Pipeline(
        [
            ("tfidf", _vectorizer()),
            ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )

    event_model.fit(texts, event_matrix)
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
        "event_probability_threshold": 0.30,
        "sample_count": len(samples),
        "training_sources": [str(path) for path in training_paths if path.exists()],
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


def _vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(2, 5),
        min_df=1,
        max_features=120_000,
        sublinear_tf=True,
    )


def _importance_text(text: str, source_type: str) -> str:
    return f"source_type={source_type} {text}"


def _event_distribution(samples: list[LabeledAlert]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for sample in samples:
        counter.update(sample.tags)
    return dict(counter)
