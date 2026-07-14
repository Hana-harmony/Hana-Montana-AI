from __future__ import annotations

import json
import math
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from typing import Any

import joblib
import numpy as np

LABEL_ORDER = ("NEGATIVE", "NEUTRAL", "POSITIVE")
FEATURE_VERSION = "sentiment-stacker-v1"


class SentimentStacker:
    def __init__(
        self,
        artifact_path: Path,
        report_path: Path,
        benchmark_report_path: Path | None = None,
    ) -> None:
        self.enabled = False
        self.version = "sentiment-stacker-unavailable"
        self.model: Any = None
        if not artifact_path.exists() or not report_path.exists():
            return
        if benchmark_report_path is not None:
            if not benchmark_report_path.exists():
                return
            benchmark = json.loads(benchmark_report_path.read_text(encoding="utf-8"))
            gate = benchmark.get("deployment_gate", {})
            if (
                gate.get("eligible") is not True
                or gate.get("candidate_model") != "kf_deberta_lora_stacker"
            ):
                return
        report = json.loads(report_path.read_text(encoding="utf-8"))
        artifact = report.get("artifact", {})
        if (
            report.get("feature_version") != FEATURE_VERSION
            or int(report.get("sample_count", 0)) < 900
            or float(report.get("cross_validation", {}).get("macro_f1", 0.0)) < 0.75
            or int(artifact.get("bytes", -1)) != artifact_path.stat().st_size
            or str(artifact.get("sha256", "")) != _sha256(artifact_path)
        ):
            return
        payload: dict[str, Any] = joblib.load(artifact_path)
        if payload.get("feature_version") != FEATURE_VERSION:
            return
        self.model = payload["model"]
        self.version = str(payload["version"])
        self.enabled = True

    def probabilities(
        self,
        *,
        transformer: dict[str, float],
        baseline: dict[str, float],
        text: str,
        source_type: str,
    ) -> dict[str, float] | None:
        if not self.enabled or self.model is None:
            return None
        features = build_stacker_features(transformer, baseline, text, source_type)
        values = self.model.predict_proba(np.asarray([features], dtype=np.float64))[0]
        classes = [str(label) for label in self.model.classes_]
        return {label: float(value) for label, value in zip(classes, values, strict=True)}


def build_stacker_features(
    transformer: dict[str, float],
    baseline: dict[str, float],
    text: str,
    source_type: str,
) -> list[float]:
    transformer_values = [float(transformer[label]) for label in LABEL_ORDER]
    baseline_values = [float(baseline[label]) for label in LABEL_ORDER]
    return [
        *transformer_values,
        *baseline_values,
        _entropy(transformer_values),
        _entropy(baseline_values),
        _margin(transformer_values),
        _margin(baseline_values),
        float(
            max(transformer, key=transformer.__getitem__) != max(baseline, key=baseline.__getitem__)
        ),
        min(math.log1p(len(text)) / 8.0, 1.0),
        float(source_type.upper() == "DISCLOSURE"),
    ]


def _entropy(values: list[float]) -> float:
    return -sum(value * math.log(max(value, 1e-12)) for value in values)


def _margin(values: list[float]) -> float:
    ordered = sorted(values, reverse=True)
    return ordered[0] - ordered[1]


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


@lru_cache(maxsize=1)
def load_sentiment_stacker(
    artifact_path: Path,
    report_path: Path,
    benchmark_report_path: Path,
) -> SentimentStacker:
    return SentimentStacker(artifact_path, report_path, benchmark_report_path)
