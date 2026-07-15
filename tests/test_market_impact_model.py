import json
from hashlib import sha256
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from hannah_montana_ai.domain.schemas import StockCandidate
from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.services.market_impact_model import (
    KFnspidMarketImpactModel,
    MarketImpactPrediction,
    _matches_file_manifest,
    blend_importance,
)


def test_blend_keeps_semantic_label_and_confidence_for_high_market_signal() -> None:
    prediction = MarketImpactPrediction(
        importance="CRITICAL",
        confidence=0.8,
        materiality_score=0.9,
        model_version="impact-v1",
    )

    importance, confidence = blend_importance("LOW", 0.6, prediction)

    assert importance == "LOW"
    assert confidence == 0.6


def test_blend_keeps_semantic_label_and_confidence_for_uncertain_market_signal() -> None:
    prediction = MarketImpactPrediction(
        importance="HIGH",
        confidence=0.4,
        materiality_score=0.5,
        model_version="impact-v1",
    )

    importance, confidence = blend_importance("MEDIUM", 0.7, prediction)

    assert importance == "MEDIUM"
    assert confidence == 0.7


def test_joblib_manifest_is_checked_before_deserialization(tmp_path: Path) -> None:
    artifact = tmp_path / "model.joblib"
    artifact.write_bytes(b"verified-artifact")
    manifest = {
        "bytes": artifact.stat().st_size,
        "sha256": sha256(artifact.read_bytes()).hexdigest(),
    }

    assert _matches_file_manifest(artifact, manifest)

    artifact.write_bytes(b"tampered-artifact")
    assert not _matches_file_manifest(artifact, manifest)


def test_joblib_manifest_rejects_symbolic_link(tmp_path: Path) -> None:
    target = tmp_path / "target.joblib"
    target.write_bytes(b"verified-artifact")
    link = tmp_path / "model.joblib"
    link.symlink_to(target)
    manifest = {
        "bytes": target.stat().st_size,
        "sha256": sha256(target.read_bytes()).hexdigest(),
    }

    assert not _matches_file_manifest(link, manifest)


def test_source_expert_rejects_cross_source_prediction(tmp_path: Path) -> None:
    model_path = tmp_path / "disclosure.joblib"
    report_path = tmp_path / "disclosure-report.json"
    labels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"] * 2
    model = Pipeline(
        [
            ("tfidf", TfidfVectorizer()),
            ("classifier", LogisticRegression(max_iter=100)),
        ]
    ).fit([f"[SOURCE=DISCLOSURE] sample {index}" for index in range(8)], labels)
    joblib.dump(
        {
            "model": model,
            "version": "disclosure-expert-v1",
            "source_type": "DISCLOSURE",
            "input_feature_version": "k-fnspid-text-v2",
        },
        model_path,
    )
    report_path.write_text(
        json.dumps(
            {
                "source_type": "DISCLOSURE",
                "test": {
                    "sample_count": 500,
                    "macro_f1": 0.31,
                    "quadratic_kappa": 0.09,
                },
                "deployment_gate": {
                    "minimum_test_sample_count": 500,
                    "minimum_macro_f1": 0.30,
                    "minimum_quadratic_kappa": 0.08,
                    "eligible": True,
                },
                "artifact": {
                    "bytes": model_path.stat().st_size,
                    "sha256": sha256(model_path.read_bytes()).hexdigest(),
                },
            }
        ),
        encoding="utf-8",
    )

    expert = KFnspidMarketImpactModel(model_path, report_path, "DISCLOSURE")

    assert expert.enabled is True
    assert expert.predict("sample", "NEWS") is None
    assert expert.predict("sample", "DISCLOSURE") is not None


def test_serving_impact_input_appends_primary_stock_like_training() -> None:
    stock = StockCandidate(
        stock_code="005930",
        stock_name="삼성전자",
        stock_name_en="Samsung Electronics",
    )

    assert AlertAnalyzer._market_impact_input("반도체 실적 개선", stock) == (
        "반도체 실적 개선 삼성전자"
    )
    assert AlertAnalyzer._market_impact_input("시장 요약", None) == "시장 요약"
