from pathlib import Path

from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.training.dataset import load_labeled_alerts
from hannah_montana_ai.training.evaluator import evaluate_alert_analyzer
from hannah_montana_ai.training.ml_trainer import train_ml_model


def test_training_builds_supervised_ml_artifact(tmp_path: Path) -> None:
    model_path = tmp_path / "financial_nlp_ml.joblib"
    report = train_ml_model(
        [
            Path("data/training/financial_alert_corpus.jsonl"),
            Path("data/training/financial_alert_augmented.jsonl"),
        ],
        model_path,
    )

    assert model_path.exists()
    assert report.sample_count >= 300
    assert report.event_label_distribution["MACRO"] >= 40
    assert report.sentiment_label_distribution["NEGATIVE"] >= 100
    assert report.importance_label_distribution["CRITICAL"] >= 50


def test_ml_model_passes_evaluation_dataset() -> None:
    samples = load_labeled_alerts(Path("data/evaluation/financial_alert_eval.jsonl"))
    result = evaluate_alert_analyzer(samples, AlertAnalyzer())

    assert result.sample_count == 18
    assert result.event_tag_recall >= 1.0
    assert result.sentiment_accuracy >= 1.0
    assert result.importance_accuracy >= 1.0
    assert result.stock_accuracy >= 1.0
