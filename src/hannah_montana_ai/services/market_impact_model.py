from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import joblib

from hannah_montana_ai.domain.schemas import Importance

LABEL_ORDER: tuple[Importance, ...] = ("LOW", "MEDIUM", "HIGH", "CRITICAL")


@dataclass(frozen=True)
class MarketImpactPrediction:
    importance: Importance
    confidence: float
    materiality_score: float
    model_version: str


class KFnspidMarketImpactModel:
    def __init__(self, model_path: Path, report_path: Path) -> None:
        self.enabled = False
        self.version = "k-fnspid-impact-unavailable"
        self.model: Any = None
        if not model_path.exists() or not report_path.exists():
            return
        report = json.loads(report_path.read_text(encoding="utf-8"))
        test = report.get("test", {})
        if (
            int(test.get("sample_count", 0)) < 1_000
            or float(test.get("macro_f1", 0.0)) < 0.30
            or float(test.get("quadratic_kappa", 0.0)) < 0.20
        ):
            return
        payload: dict[str, Any] = joblib.load(model_path)
        self.model = payload["model"]
        self.version = str(payload["version"])
        self.enabled = True

    def predict(self, text: str) -> MarketImpactPrediction | None:
        if not self.enabled or self.model is None:
            return None
        probabilities = self.model.predict_proba([text])[0]
        classes = [str(label) for label in self.model.classes_]
        by_label = {
            label: float(probability)
            for label, probability in zip(classes, probabilities, strict=True)
        }
        predicted = max(by_label, key=by_label.get)  # type: ignore[arg-type]
        expected = sum(
            index * by_label.get(label, 0.0) for index, label in enumerate(LABEL_ORDER)
        ) / (len(LABEL_ORDER) - 1)
        return MarketImpactPrediction(
            importance=cast(Importance, predicted),
            confidence=by_label[predicted],
            materiality_score=round(expected, 6),
            model_version=self.version,
        )


def blend_importance(
    semantic_importance: Importance,
    semantic_confidence: float,
    market_prediction: MarketImpactPrediction | None,
) -> tuple[Importance, float]:
    if market_prediction is None:
        return semantic_importance, semantic_confidence
    if market_prediction.importance == semantic_importance:
        return semantic_importance, max(semantic_confidence, market_prediction.confidence)
    semantic_index = LABEL_ORDER.index(semantic_importance)
    market_index = LABEL_ORDER.index(market_prediction.importance)
    if market_prediction.confidence >= 0.72 and market_index > semantic_index:
        upgraded = LABEL_ORDER[min(semantic_index + 1, market_index)]
        return upgraded, min(max(semantic_confidence, market_prediction.confidence), 0.95)
    return semantic_importance, min(semantic_confidence, 0.49)
