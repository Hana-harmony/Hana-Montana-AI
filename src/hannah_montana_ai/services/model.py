import json
from pathlib import Path
from typing import cast

from hannah_montana_ai.domain.schemas import Importance, Sentiment


class KeywordFinancialNlpModel:
    def __init__(self, model_path: Path) -> None:
        with model_path.open(encoding="utf-8") as file:
            payload = json.load(file)
        self.version: str = payload["version"]
        self.event_keywords: dict[str, list[str]] = payload["event_keywords"]
        self.sentiment_keywords: dict[str, list[str]] = payload["sentiment_keywords"]
        self.importance_keywords: dict[str, list[str]] = payload["importance_keywords"]

    def predict_event_tags(self, text: str) -> list[str]:
        tags = [
            tag
            for tag, keywords in self.event_keywords.items()
            if self._score(text, keywords) > 0
        ]
        return tags or ["GENERAL_MARKET"]

    def classify_sentiment(self, text: str) -> Sentiment:
        scores = {
            label: self._score(text, keywords)
            for label, keywords in self.sentiment_keywords.items()
            if label in {"POSITIVE", "NEUTRAL", "NEGATIVE"}
        }
        top_label, top_score = max(scores.items(), key=lambda item: item[1])
        if top_score == 0:
            return "NEUTRAL"
        return cast(Sentiment, top_label)

    def classify_importance(self, text: str, source_type: str) -> Importance:
        if self._score(text, self.importance_keywords.get("CRITICAL", [])) > 0:
            return "CRITICAL"
        if source_type == "DISCLOSURE":
            return "HIGH"

        scores = {
            label: self._score(text, keywords)
            for label, keywords in self.importance_keywords.items()
            if label in {"LOW", "MEDIUM", "HIGH"}
        }
        top_label, top_score = max(scores.items(), key=lambda item: item[1])
        if top_score == 0:
            return "MEDIUM" if len(text) > 80 else "LOW"
        return cast(Importance, top_label)

    def _score(self, text: str, keywords: list[str]) -> int:
        return sum(1 for keyword in keywords if keyword in text)
