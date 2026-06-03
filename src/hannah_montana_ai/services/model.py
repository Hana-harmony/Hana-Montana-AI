from pathlib import Path
from typing import Any, cast

import joblib

from hannah_montana_ai.domain.schemas import Importance, Sentiment
from hannah_montana_ai.training.ml_trainer import _importance_text


class MachineLearningFinancialNlpModel:
    def __init__(self, model_path: Path) -> None:
        payload: dict[str, Any] = joblib.load(model_path)
        self.version = str(payload["version"])
        self.event_model = payload["event_model"]
        self.event_binarizer = payload["event_binarizer"]
        self.sentiment_model = payload["sentiment_model"]
        self.importance_model = payload["importance_model"]
        self.event_probability_threshold = float(payload.get("event_probability_threshold", 0.5))

    def predict_event_tags(self, text: str) -> list[str]:
        probabilities = self.event_model.predict_proba([text])[0]
        classes = list(self.event_binarizer.classes_)
        tags = [
            str(label)
            for label, probability in zip(classes, probabilities, strict=True)
            if probability >= self.event_probability_threshold
        ]
        if tags:
            return sorted(tags)

        top_index = int(max(range(len(probabilities)), key=lambda index: probabilities[index]))
        return [str(classes[top_index])] if classes else ["GENERAL_MARKET"]

    def classify_sentiment(self, text: str) -> Sentiment:
        return cast(Sentiment, self.sentiment_model.predict([text])[0])

    def classify_importance(self, text: str, source_type: str) -> Importance:
        prediction = self.importance_model.predict([_importance_text(text, source_type)])[0]
        return cast(Importance, prediction)
