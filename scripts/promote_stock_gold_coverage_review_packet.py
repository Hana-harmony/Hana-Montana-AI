import argparse
import json
from pathlib import Path

from hannah_montana_ai.training.stock_curation import (
    promote_approved_stock_gold_coverage_reviews,
    write_stock_gold_promotion_report,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
COVERAGE_REVIEW_PACKET_PATH = (
    PROJECT_ROOT / "data/curation/stock_gold_coverage_active_review_packet.jsonl"
)
TRAINING_OUTPUT_PATH = (
    PROJECT_ROOT / "data/training/financial_alert_stock_review_gold.jsonl"
)
EVALUATION_OUTPUT_PATH = (
    PROJECT_ROOT / "data/evaluation/financial_alert_stock_review_gold.jsonl"
)
REPORT_PATH = PROJECT_ROOT / "reports/stock-gold-coverage-promotion-report.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--coverage-review-packet",
        type=Path,
        default=COVERAGE_REVIEW_PACKET_PATH,
    )
    parser.add_argument("--training-output", type=Path, default=TRAINING_OUTPUT_PATH)
    parser.add_argument("--evaluation-output", type=Path, default=EVALUATION_OUTPUT_PATH)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    args = parser.parse_args()

    result = promote_approved_stock_gold_coverage_reviews(
        coverage_review_packet_path=args.coverage_review_packet,
        training_output_path=args.training_output,
        evaluation_output_path=args.evaluation_output,
    )
    write_stock_gold_promotion_report(args.report, result.report)
    print(json.dumps(result.report, ensure_ascii=False))


if __name__ == "__main__":
    main()
