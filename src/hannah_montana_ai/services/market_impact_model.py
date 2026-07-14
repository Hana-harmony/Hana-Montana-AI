from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, cast

import joblib

from hannah_montana_ai.domain.schemas import Importance
from hannah_montana_ai.services.impact_model_features import (
    IMPACT_INPUT_FEATURE_VERSION,
    build_impact_model_text,
)

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
        self.input_feature_version = "k-fnspid-text-v1"
        if not model_path.exists() or not report_path.exists():
            return
        report = json.loads(report_path.read_text(encoding="utf-8"))
        test = report.get("test", {})
        artifact = report.get("artifact", {})
        if (
            int(test.get("sample_count", 0)) < 1_000
            or float(test.get("macro_f1", 0.0)) < 0.30
            or float(test.get("quadratic_kappa", 0.0)) < 0.20
            or not _matches_file_manifest(model_path, artifact)
        ):
            return
        payload: dict[str, Any] = joblib.load(model_path)
        self.model = payload["model"]
        self.version = str(payload["version"])
        self.input_feature_version = str(payload.get("input_feature_version", "k-fnspid-text-v1"))
        self.enabled = True

    def predict(self, text: str, source_type: str = "NEWS") -> MarketImpactPrediction | None:
        if not self.enabled or self.model is None:
            return None
        model_text = (
            build_impact_model_text(text, source_type)
            if self.input_feature_version == IMPACT_INPUT_FEATURE_VERSION
            else text
        )
        probabilities = self.model.predict_proba([model_text])[0]
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
    # 의미 중요도와 관측 가격충격은 서로 다른 과제이므로 라벨과 confidence를 합치지 않는다.
    del market_prediction
    return semantic_importance, semantic_confidence


def _matches_file_manifest(path: Path, manifest: Any) -> bool:
    if not isinstance(manifest, dict) or not path.is_file() or path.is_symlink():
        return False
    if path.stat().st_size != int(manifest.get("bytes", -1)):
        return False
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest() == str(manifest.get("sha256", ""))
