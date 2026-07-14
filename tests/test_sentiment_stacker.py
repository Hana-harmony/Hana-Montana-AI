from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

import joblib
import pytest
from sklearn.linear_model import LogisticRegression

from hannah_montana_ai.services.sentiment_stacker import (
    FEATURE_VERSION,
    SentimentStacker,
    build_stacker_features,
)


def _write_stacker(tmp_path: Path) -> tuple[Path, Path]:
    model = LogisticRegression().fit(
        [
            [0.8, 0.1, 0.1, 0.7, 0.2, 0.1, 0.6, 0.5, 0.7, 0.5, 0.0, 0.3, 0.0],
            [0.1, 0.8, 0.1, 0.2, 0.7, 0.1, 0.5, 0.6, 0.7, 0.5, 0.0, 0.3, 1.0],
            [0.1, 0.1, 0.8, 0.1, 0.2, 0.7, 0.6, 0.5, 0.7, 0.5, 0.0, 0.3, 0.0],
        ],
        ["NEGATIVE", "NEUTRAL", "POSITIVE"],
    )
    artifact_path = tmp_path / "stacker.joblib"
    joblib.dump(
        {
            "version": "test-stacker",
            "feature_version": FEATURE_VERSION,
            "model": model,
        },
        artifact_path,
    )
    report_path = tmp_path / "report.json"
    report_path.write_text(
        json.dumps(
            {
                "feature_version": FEATURE_VERSION,
                "sample_count": 900,
                "cross_validation": {"macro_f1": 0.8},
                "artifact": {
                    "bytes": artifact_path.stat().st_size,
                    "sha256": sha256(artifact_path.read_bytes()).hexdigest(),
                },
            }
        ),
        encoding="utf-8",
    )
    return artifact_path, report_path


def test_build_stacker_features_contains_source_and_disagreement() -> None:
    features = build_stacker_features(
        {"NEGATIVE": 0.8, "NEUTRAL": 0.1, "POSITIVE": 0.1},
        {"NEGATIVE": 0.1, "NEUTRAL": 0.2, "POSITIVE": 0.7},
        "실적이 시장 예상치를 하회했다",
        "DISCLOSURE",
    )

    assert len(features) == 13
    assert features[10] == 1.0
    assert features[12] == 1.0


def test_stacker_rejects_tampered_artifact(tmp_path: Path) -> None:
    artifact_path, report_path = _write_stacker(tmp_path)
    artifact_path.write_bytes(artifact_path.read_bytes() + b"tampered")

    assert SentimentStacker(artifact_path, report_path).enabled is False


def test_stacker_returns_normalized_probabilities(tmp_path: Path) -> None:
    artifact_path, report_path = _write_stacker(tmp_path)
    stacker = SentimentStacker(artifact_path, report_path)

    probabilities = stacker.probabilities(
        transformer={"NEGATIVE": 0.8, "NEUTRAL": 0.1, "POSITIVE": 0.1},
        baseline={"NEGATIVE": 0.7, "NEUTRAL": 0.2, "POSITIVE": 0.1},
        text="영업이익이 감소했다",
        source_type="NEWS",
    )

    assert stacker.enabled is True
    assert probabilities is not None
    assert set(probabilities) == {"NEGATIVE", "NEUTRAL", "POSITIVE"}
    assert sum(probabilities.values()) == pytest.approx(1.0)


def test_stacker_requires_benchmark_selection_for_serving(tmp_path: Path) -> None:
    artifact_path, report_path = _write_stacker(tmp_path)
    benchmark_path = tmp_path / "benchmark.json"
    benchmark_path.write_text(
        json.dumps(
            {
                "deployment_gate": {
                    "eligible": True,
                    "candidate_model": "kf_deberta_lora_ensemble",
                }
            }
        ),
        encoding="utf-8",
    )

    assert SentimentStacker(artifact_path, report_path, benchmark_path).enabled is False

    benchmark_path.write_text(
        json.dumps(
            {
                "deployment_gate": {
                    "eligible": True,
                    "candidate_model": "kf_deberta_lora_stacker",
                }
            }
        ),
        encoding="utf-8",
    )
    assert SentimentStacker(artifact_path, report_path, benchmark_path).enabled is True
