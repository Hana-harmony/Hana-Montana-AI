import argparse
import json
from pathlib import Path

from hannah_montana_ai.training.stock_candidate_experiment import (
    build_stock_candidate_quota_experiment_report,
    write_stock_candidate_quota_experiment_report,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = PROJECT_ROOT / "reports/stock-candidate-quota-experiment.json"
WEAK_LABEL_PATH = PROJECT_ROOT / "data/processed/weak_labeled_alerts.jsonl"
STOCK_CANDIDATE_PATH = PROJECT_ROOT / "data/curation/stock_training_candidate_queue.jsonl"
TRAINING_PATHS = [
    PROJECT_ROOT / "data/training/financial_alert_corpus.jsonl",
    PROJECT_ROOT / "data/training/financial_alert_augmented.jsonl",
    PROJECT_ROOT / "data/training/financial_alert_news_style_augmented.jsonl",
    PROJECT_ROOT / "data/training/financial_alert_real_news_gold.jsonl",
    PROJECT_ROOT / "data/training/financial_alert_stock_review_gold.jsonl",
]
EVALUATION_PATHS = {
    "benchmark": PROJECT_ROOT / "data/evaluation/financial_alert_eval.jsonl",
    "real_disclosure_gold": (
        PROJECT_ROOT / "data/evaluation/financial_alert_real_disclosure_gold.jsonl"
    ),
    "real_news_gold": PROJECT_ROOT / "data/evaluation/financial_alert_real_news_gold.jsonl",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    args = parser.parse_args()

    report = build_stock_candidate_quota_experiment_report(
        training_paths=TRAINING_PATHS,
        pseudo_label_path=WEAK_LABEL_PATH,
        stock_candidate_path=STOCK_CANDIDATE_PATH,
        evaluation_paths=EVALUATION_PATHS,
    )
    write_stock_candidate_quota_experiment_report(args.report, report)
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
