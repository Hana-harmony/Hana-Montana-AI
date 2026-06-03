from pathlib import Path

import joblib
import pytest

from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.services.model import (
    MachineLearningFinancialNlpModel,
    ModelArtifactInvalidError,
    ModelArtifactNotFoundError,
)
from hannah_montana_ai.training.collector import should_write_raw_alerts
from hannah_montana_ai.training.dataset import load_labeled_alerts
from hannah_montana_ai.training.evaluator import evaluate_alert_analyzer
from hannah_montana_ai.training.ml_trainer import financial_tokenize, train_ml_model

GOLD_EVENT_LABEL_QUALITY_GATES = {
    "CAPITAL_ACTION": {"precision": 0.90, "recall": 0.70, "f1": 0.80, "support": 70},
    "CONTRACT": {"precision": 0.70, "recall": 0.95, "f1": 0.80, "support": 70},
    "CORPORATE_ACTION": {"precision": 0.90, "recall": 0.95, "f1": 0.90, "support": 90},
    "DISCLOSURE": {"precision": 0.85, "recall": 0.80, "f1": 0.80, "support": 300},
    "EARNINGS": {"precision": 0.70, "recall": 0.95, "f1": 0.80, "support": 100},
    "GENERAL_MARKET": {"precision": 0.95, "recall": 0.95, "f1": 0.95, "support": 70},
    "MACRO": {"precision": 0.70, "recall": 0.90, "f1": 0.80, "support": 140},
    "RISK": {"precision": 0.95, "recall": 0.80, "f1": 0.85, "support": 160},
}


def test_training_builds_supervised_ml_artifact(tmp_path: Path) -> None:
    model_path = tmp_path / "financial_nlp_ml.joblib"
    report = train_ml_model(
        [
            Path("data/training/financial_alert_corpus.jsonl"),
            Path("data/training/financial_alert_augmented.jsonl"),
            Path("data/training/financial_alert_news_style_augmented.jsonl"),
            Path("data/training/financial_alert_real_news_gold.jsonl"),
        ],
        model_path,
    )

    assert model_path.exists()
    assert report.sample_count >= 300
    assert report.event_label_distribution["MACRO"] >= 40
    assert report.sentiment_label_distribution["NEGATIVE"] >= 100
    assert report.importance_label_distribution["CRITICAL"] >= 50
    assert report.training_sources == [
        "data/training/financial_alert_corpus.jsonl",
        "data/training/financial_alert_augmented.jsonl",
        "data/training/financial_alert_news_style_augmented.jsonl",
        "data/training/financial_alert_real_news_gold.jsonl",
    ]
    assert report.validation.sample_count >= 90
    assert report.validation.train_sample_count >= 300
    assert report.validation.event_macro_f1 >= 0.8
    assert report.validation.sentiment_accuracy >= 0.8
    assert report.validation.importance_accuracy >= 0.8
    assert report.validation.event_label_metrics["DISCLOSURE"]["support"] >= 10


def test_financial_tokenizer_extracts_domain_terms_without_spacing_dependency() -> None:
    tokens = financial_tokenize("삼성전자 잠정실적 공시와 고환율 속 수주 턴어라운드")

    assert "잠정실적" in tokens
    assert "수주" in tokens
    assert "finance:잠정실적" in tokens
    assert "finance:고환율" in tokens
    assert "finance:턴어라운드" in tokens


def test_missing_model_artifact_raises_explicit_error(tmp_path: Path) -> None:
    with pytest.raises(ModelArtifactNotFoundError):
        MachineLearningFinancialNlpModel(tmp_path / "missing.joblib")


def test_invalid_model_artifact_requires_expected_payload_keys(tmp_path: Path) -> None:
    model_path = tmp_path / "invalid.joblib"
    joblib.dump({"version": "broken"}, model_path)

    with pytest.raises(ModelArtifactInvalidError):
        MachineLearningFinancialNlpModel(model_path)


def test_ml_model_passes_evaluation_dataset() -> None:
    samples = load_labeled_alerts(Path("data/evaluation/financial_alert_eval.jsonl"))
    result = evaluate_alert_analyzer(samples, AlertAnalyzer())

    assert result.sample_count >= 500
    assert result.event_tag_recall >= 0.8
    assert result.sentiment_accuracy >= 0.85
    assert result.importance_accuracy >= 0.8
    assert result.stock_accuracy >= 1.0
    assert result.event_macro_f1 >= 0.8
    assert result.event_label_metrics["DISCLOSURE"].support >= 300
    assert result.event_label_metrics["GENERAL_MARKET"].f1 >= 0.9
    assert result.sentiment_confusion_matrix["NEGATIVE"]["NEGATIVE"] >= 200
    assert result.importance_confusion_matrix["CRITICAL"]["CRITICAL"] >= 70


def test_ml_model_passes_label_level_golden_quality_gates() -> None:
    samples = load_labeled_alerts(Path("data/evaluation/financial_alert_eval.jsonl"))
    result = evaluate_alert_analyzer(samples, AlertAnalyzer())

    for label, gates in GOLD_EVENT_LABEL_QUALITY_GATES.items():
        metric = result.event_label_metrics[label]
        assert metric.precision >= gates["precision"], label
        assert metric.recall >= gates["recall"], label
        assert metric.f1 >= gates["f1"], label
        assert metric.support >= gates["support"], label

    assert result.sentiment_confusion_matrix["NEGATIVE"]["NEGATIVE"] >= 200
    assert result.sentiment_confusion_matrix["POSITIVE"]["POSITIVE"] >= 230
    assert result.sentiment_confusion_matrix["NEUTRAL"]["NEUTRAL"] >= 230
    assert result.importance_confusion_matrix["CRITICAL"]["CRITICAL"] >= 80
    assert result.importance_confusion_matrix["HIGH"]["HIGH"] >= 290
    assert result.importance_confusion_matrix["MEDIUM"]["MEDIUM"] >= 230
    assert result.importance_confusion_matrix["LOW"]["LOW"] >= 20


def test_ml_model_passes_real_disclosure_gold_dataset() -> None:
    samples = load_labeled_alerts(
        Path("data/evaluation/financial_alert_real_disclosure_gold.jsonl")
    )
    result = evaluate_alert_analyzer(samples, AlertAnalyzer())

    assert result.sample_count >= 30
    assert result.event_tag_recall >= 0.9
    assert result.event_macro_f1 >= 0.9
    assert result.sentiment_accuracy >= 0.9
    assert result.importance_accuracy >= 0.9
    assert result.stock_accuracy >= 1.0
    assert result.event_label_metrics["DISCLOSURE"].f1 >= 0.95
    assert result.event_label_metrics["RISK"].recall >= 0.9
    assert result.sentiment_confusion_matrix["NEGATIVE"]["NEGATIVE"] >= 7
    assert result.importance_confusion_matrix["LOW"]["LOW"] >= 6


def test_ml_model_passes_real_news_gold_dataset() -> None:
    samples = load_labeled_alerts(Path("data/evaluation/financial_alert_real_news_gold.jsonl"))
    result = evaluate_alert_analyzer(samples, AlertAnalyzer())

    assert result.sample_count >= 30
    assert result.event_tag_recall >= 0.85
    assert result.event_macro_f1 >= 0.85
    assert result.sentiment_accuracy >= 0.85
    assert result.importance_accuracy >= 0.85
    assert result.stock_accuracy >= 1.0
    assert result.event_label_metrics["GENERAL_MARKET"].recall >= 0.85
    assert result.event_label_metrics["MACRO"].recall >= 0.85
    assert result.event_label_metrics["EARNINGS"].recall >= 0.85
    assert result.event_label_metrics["RISK"].recall >= 0.75


def test_real_news_gold_training_and_evaluation_are_disjoint() -> None:
    training_samples = load_labeled_alerts(
        Path("data/training/financial_alert_real_news_gold.jsonl")
    )
    evaluation_samples = load_labeled_alerts(
        Path("data/evaluation/financial_alert_real_news_gold.jsonl")
    )

    training_texts = {sample.text for sample in training_samples}
    evaluation_texts = {sample.text for sample in evaluation_samples}

    assert len(training_samples) >= 20
    assert len(evaluation_samples) >= 30
    assert training_texts.isdisjoint(evaluation_texts)


def test_collection_guard_prevents_dataset_shrink() -> None:
    assert should_write_raw_alerts(existing_count=1000, next_count=900) is False
    assert should_write_raw_alerts(existing_count=1000, next_count=1000) is True
    assert should_write_raw_alerts(existing_count=1000, next_count=1, force=True) is True
