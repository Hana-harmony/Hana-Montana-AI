import json
from pathlib import Path

from hannah_montana_ai.training.ml_trainer import train_ml_model

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "src/hannah_montana_ai/model_store/financial_nlp_ml.joblib"
REPORT_PATH = PROJECT_ROOT / "reports/ml-training-report.json"
TRAINING_PATHS = [
    PROJECT_ROOT / "data/training/financial_alert_corpus.jsonl",
    PROJECT_ROOT / "data/training/financial_alert_augmented.jsonl",
    PROJECT_ROOT / "data/processed/weak_labeled_alerts.jsonl",
]


def main() -> None:
    report = train_ml_model(TRAINING_PATHS, MODEL_PATH)
    REPORT_PATH.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report.to_dict(), ensure_ascii=False))


if __name__ == "__main__":
    main()
