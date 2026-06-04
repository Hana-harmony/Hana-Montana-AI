import argparse
import json
from pathlib import Path

from hannah_montana_ai.training.active_review import (
    build_stock_gold_active_review_report,
    write_stock_gold_active_review_report,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "src/hannah_montana_ai/model_store/financial_nlp_ml.joblib"
TRAINING_REVIEW_PATH = PROJECT_ROOT / "data/curation/stock_gold_training_review_batch.jsonl"
EVALUATION_REVIEW_PATH = (
    PROJECT_ROOT / "data/curation/stock_gold_evaluation_review_batch.jsonl"
)
REPORT_PATH = PROJECT_ROOT / "reports/stock-gold-active-review-report.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=MODEL_PATH)
    parser.add_argument("--training-review", type=Path, default=TRAINING_REVIEW_PATH)
    parser.add_argument("--evaluation-review", type=Path, default=EVALUATION_REVIEW_PATH)
    parser.add_argument("--top-n-per-split", type=int, default=50)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    args = parser.parse_args()

    report = build_stock_gold_active_review_report(
        training_review_path=args.training_review,
        evaluation_review_path=args.evaluation_review,
        model_path=args.model,
        top_n_per_split=args.top_n_per_split,
    )
    write_stock_gold_active_review_report(args.report, report)
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
