import argparse
import json
from pathlib import Path

from hannah_montana_ai.training.calibration import (
    build_model_confidence_calibration_report,
    write_model_confidence_calibration_report,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "src/hannah_montana_ai/model_store/financial_nlp_ml.joblib"
REPORT_PATH = PROJECT_ROOT / "reports/model-confidence-calibration.json"
EVALUATION_PATHS = {
    "benchmark": PROJECT_ROOT / "data/evaluation/financial_alert_eval.jsonl",
    "real_disclosure_gold": (
        PROJECT_ROOT / "data/evaluation/financial_alert_real_disclosure_gold.jsonl"
    ),
    "real_news_gold": PROJECT_ROOT / "data/evaluation/financial_alert_real_news_gold.jsonl",
    "stock_review_gold": (
        PROJECT_ROOT / "data/evaluation/financial_alert_stock_review_gold.jsonl"
    ),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=MODEL_PATH)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    parser.add_argument("--bin-count", type=int, default=10)
    parser.add_argument("--high-confidence-threshold", type=float, default=0.85)
    parser.add_argument("--max-error-examples", type=int, default=20)
    args = parser.parse_args()

    report = build_model_confidence_calibration_report(
        EVALUATION_PATHS,
        args.model,
        bin_count=args.bin_count,
        high_confidence_threshold=args.high_confidence_threshold,
        max_error_examples=args.max_error_examples,
    )
    write_model_confidence_calibration_report(args.report, report)
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
