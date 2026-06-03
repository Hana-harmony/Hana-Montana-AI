from pathlib import Path

from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.training.dataset import load_labeled_alerts
from hannah_montana_ai.training.evaluator import evaluate_alert_analyzer
from hannah_montana_ai.training.trainer import train_keyword_model


def test_training_builds_model_profile_from_corpus() -> None:
    payload = train_keyword_model(Path("data/training/financial_alert_corpus.jsonl"))

    assert payload["sample_count"] >= 18
    assert "MACRO" in payload["event_keywords"]
    assert "위험" in payload["sentiment_keywords"]["NEGATIVE"]
    assert "승인" in payload["sentiment_keywords"]["POSITIVE"]


def test_baseline_model_passes_evaluation_dataset() -> None:
    samples = load_labeled_alerts(Path("data/evaluation/financial_alert_eval.jsonl"))
    result = evaluate_alert_analyzer(samples, AlertAnalyzer())

    assert result.sample_count == 6
    assert result.event_tag_recall >= 1.0
    assert result.sentiment_accuracy >= 1.0
    assert result.importance_accuracy >= 1.0
    assert result.stock_accuracy >= 1.0
