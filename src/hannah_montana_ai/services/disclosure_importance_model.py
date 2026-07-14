from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import joblib
import numpy as np

from hannah_montana_ai.domain.schemas import Importance
from hannah_montana_ai.services.market_impact_model import _matches_file_manifest

LABEL_ORDER: tuple[Importance, ...] = ("LOW", "MEDIUM", "HIGH", "CRITICAL")
INPUT_FEATURE_VERSION = "disclosure-validation-selected-view-v3"
ALLOWED_FIELDS = {"title", "snippet", "full_content"}


@dataclass(frozen=True)
class DisclosureImportancePrediction:
    importance: Importance
    confidence: float
    probabilities: dict[str, float]


class DisclosureImportanceModel:
    def __init__(self, model_path: Path, report_path: Path) -> None:
        self.enabled = False
        self.version = "disclosure-importance-unavailable"
        self.model: Any = None
        self.probability_temperature = 1.0
        self.selected_fields: tuple[str, ...] = ()
        if not model_path.exists() or not report_path.exists():
            return
        report = json.loads(report_path.read_text(encoding="utf-8"))
        label_metrics = report.get("gold_test", {}).get("label_metrics", {})
        minimum_label_f1 = float(
            report.get("deployment_gate", {}).get("minimum_gold_label_f1", 1.0)
        )
        if (
            report.get("deployment_gate", {}).get("eligible") is not True
            or report.get("input_feature_version") != INPUT_FEATURE_VERSION
            or int(report.get("gold_test", {}).get("sample_count", 0)) < 500
            or float(report.get("gold_test", {}).get("macro_f1", 0.0)) < 0.70
            or set(label_metrics) != set(LABEL_ORDER)
            or any(
                float(label_metrics[label].get("f1", 0.0)) < minimum_label_f1
                for label in LABEL_ORDER
            )
            or not _matches_file_manifest(model_path, report.get("artifact", {}))
        ):
            return
        payload: dict[str, Any] = joblib.load(model_path)
        if payload.get("schema_version") != "disclosure-importance-artifact/v1":
            return
        if payload.get("input_feature_version") != INPUT_FEATURE_VERSION:
            return
        if tuple(payload.get("label_order", ())) != LABEL_ORDER:
            return
        selected_fields = tuple(str(field) for field in payload.get("selected_fields", ()))
        report_fields = tuple(
            str(field) for field in report.get("feature_selection", {}).get("selected_fields", ())
        )
        if (
            not selected_fields
            or selected_fields != report_fields
            or not set(selected_fields).issubset(ALLOWED_FIELDS)
        ):
            return
        self.model = payload["model"]
        self.selected_fields = selected_fields
        self.probability_temperature = float(payload.get("probability_temperature", 1.0))
        if not 0.1 <= self.probability_temperature <= 10.0:
            self.model = None
            return
        self.version = str(payload["version"])
        self.enabled = True

    def predict(
        self,
        title: str,
        snippet: str = "",
        full_content: str = "",
    ) -> DisclosureImportancePrediction | None:
        if not self.enabled or self.model is None:
            return None
        values_by_field = {
            "title": title,
            "snippet": snippet,
            "full_content": full_content,
        }
        text = " ".join(
            values_by_field[field].strip()
            for field in self.selected_fields
            if values_by_field[field].strip()
        )
        if not text:
            return None
        values = np.clip(self.model.predict_proba([text])[0], 1e-9, 1.0)
        values = np.power(values, 1.0 / self.probability_temperature)
        values = values / values.sum()
        classes = [str(label) for label in self.model.classes_]
        probabilities = {label: float(value) for label, value in zip(classes, values, strict=True)}
        predicted = max(probabilities, key=probabilities.__getitem__)
        return DisclosureImportancePrediction(
            importance=cast(Importance, predicted),
            confidence=probabilities[predicted],
            probabilities=probabilities,
        )
