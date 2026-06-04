import argparse
import json
from pathlib import Path

from hannah_montana_ai.training.stock_curation import (
    validate_stock_gold_review_batches,
    write_stock_gold_review_validation_report,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRAINING_REVIEW_PATH = PROJECT_ROOT / "data/curation/stock_gold_training_review_batch.jsonl"
EVALUATION_REVIEW_PATH = (
    PROJECT_ROOT / "data/curation/stock_gold_evaluation_review_batch.jsonl"
)
REPORT_PATH = PROJECT_ROOT / "reports/stock-gold-review-validation-report.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--training-review", type=Path, default=TRAINING_REVIEW_PATH)
    parser.add_argument("--evaluation-review", type=Path, default=EVALUATION_REVIEW_PATH)
    parser.add_argument("--training-stock-target", type=int, default=300)
    parser.add_argument("--evaluation-stock-target", type=int, default=100)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    args = parser.parse_args()

    result = validate_stock_gold_review_batches(
        training_review_path=args.training_review,
        evaluation_review_path=args.evaluation_review,
        training_stock_target=args.training_stock_target,
        evaluation_stock_target=args.evaluation_stock_target,
    )
    write_stock_gold_review_validation_report(args.report, result.report)
    print(json.dumps(result.report, ensure_ascii=False))


if __name__ == "__main__":
    main()
