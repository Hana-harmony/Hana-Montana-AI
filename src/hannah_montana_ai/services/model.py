from pathlib import Path
from typing import Any, cast

import joblib

from hannah_montana_ai.domain.schemas import Importance, Sentiment
from hannah_montana_ai.training.ml_trainer import _event_text, _importance_text


class ModelArtifactError(RuntimeError):
    pass


class ModelArtifactNotFoundError(ModelArtifactError):
    pass


class ModelArtifactInvalidError(ModelArtifactError):
    pass


class MachineLearningFinancialNlpModel:
    def __init__(self, model_path: Path) -> None:
        if not model_path.exists():
            raise ModelArtifactNotFoundError(f"ML model artifact not found: {model_path}")

        try:
            payload: dict[str, Any] = joblib.load(model_path)
        except Exception as exception:
            message = f"ML model artifact cannot be loaded: {model_path}"
            raise ModelArtifactInvalidError(message) from exception

        self._validate_payload(payload, model_path)
        self.version = str(payload["version"])
        self.event_model = payload["event_model"]
        self.event_binarizer = payload["event_binarizer"]
        self.sentiment_model = payload["sentiment_model"]
        self.importance_model = payload["importance_model"]
        self.event_probability_threshold = float(payload.get("event_probability_threshold", 0.5))
        self.event_label_thresholds = {
            str(label): float(threshold)
            for label, threshold in payload.get("event_label_thresholds", {}).items()
        }

    def _validate_payload(self, payload: dict[str, Any], model_path: Path) -> None:
        required_keys = {
            "version",
            "event_model",
            "event_binarizer",
            "sentiment_model",
            "importance_model",
        }
        missing_keys = sorted(required_keys - set(payload))
        if missing_keys:
            joined_keys = ", ".join(missing_keys)
            message = f"ML model artifact is missing required keys: {joined_keys} ({model_path})"
            raise ModelArtifactInvalidError(message)

    def predict_event_tags(self, text: str, source_type: str) -> list[str]:
        probability_by_label = self.event_tag_probabilities(text, source_type)
        tags = [
            label
            for label, probability in probability_by_label.items()
            if probability >= self.event_label_thresholds.get(
                label,
                self.event_probability_threshold,
            )
        ]
        if tags:
            return sorted(tags)

        if not probability_by_label:
            return ["GENERAL_MARKET"]
        return [max(probability_by_label.items(), key=lambda item: item[1])[0]]

    def event_tag_probabilities(self, text: str, source_type: str) -> dict[str, float]:
        probabilities = self.event_model.predict_proba([_event_text(text, source_type)])[0]
        classes = list(self.event_binarizer.classes_)
        return {
            str(label): float(probability)
            for label, probability in zip(classes, probabilities, strict=True)
        }

    def classify_sentiment(self, text: str) -> Sentiment:
        return cast(Sentiment, self.sentiment_model.predict([text])[0])

    def sentiment_probabilities(self, text: str) -> dict[str, float]:
        probabilities = self.sentiment_model.predict_proba([text])[0]
        classes = list(self.sentiment_model.classes_)
        return {
            str(label): float(probability)
            for label, probability in zip(classes, probabilities, strict=True)
        }

    def classify_importance(self, text: str, source_type: str) -> Importance:
        prediction = self.importance_model.predict([_importance_text(text, source_type)])[0]
        return cast(Importance, prediction)

    def importance_probabilities(self, text: str, source_type: str) -> dict[str, float]:
        probabilities = self.importance_model.predict_proba(
            [_importance_text(text, source_type)]
        )[0]
        classes = list(self.importance_model.classes_)
        return {
            str(label): float(probability)
            for label, probability in zip(classes, probabilities, strict=True)
        }
