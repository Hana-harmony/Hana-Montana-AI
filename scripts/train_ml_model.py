import json
from pathlib import Path

from hannah_montana_ai.training.ml_trainer import train_ml_model
from hannah_montana_ai.training.weak_distiller import write_weak_distillation_report

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "src/hannah_montana_ai/model_store/financial_nlp_ml.joblib"
REPORT_PATH = PROJECT_ROOT / "reports/ml-training-report.json"
WEAK_LABEL_PATH = PROJECT_ROOT / "data/processed/weak_labeled_alerts.jsonl"
STOCK_CANDIDATE_PATH = PROJECT_ROOT / "data/curation/stock_training_candidate_queue.jsonl"
WEAK_DISTILLATION_REPORT_PATH = PROJECT_ROOT / "reports/weak-distillation-report.json"
TRAINING_PATHS = [
    PROJECT_ROOT / "data/training/financial_alert_corpus.jsonl",
    PROJECT_ROOT / "data/training/financial_alert_augmented.jsonl",
    PROJECT_ROOT / "data/training/financial_alert_news_style_augmented.jsonl",
    PROJECT_ROOT / "data/training/financial_alert_real_news_gold.jsonl",
]


def main() -> None:
    report = train_ml_model(
        TRAINING_PATHS,
        MODEL_PATH,
        pseudo_label_path=WEAK_LABEL_PATH,
        stock_candidate_path=STOCK_CANDIDATE_PATH,
    )
    distillation_report = report.pseudo_labeling
    write_weak_distillation_report(
        distillation_report,
        WEAK_DISTILLATION_REPORT_PATH,
    )

    REPORT_PATH.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report.to_dict(), ensure_ascii=False))


if __name__ == "__main__":
    main()
