import argparse
import json
from pathlib import Path

from hannah_montana_ai.training.stock_universe import (
    build_stock_coverage_report,
    write_json_report,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
UNIVERSE_PATH = PROJECT_ROOT / "data/reference/korea_stock_universe.csv"
RAW_ALERTS_PATH = PROJECT_ROOT / "data/raw/collected_alerts.jsonl"
REPORT_PATH = PROJECT_ROOT / "reports/stock-coverage-report.json"
TRAINING_PATHS = [
    PROJECT_ROOT / "data/training/financial_alert_corpus.jsonl",
    PROJECT_ROOT / "data/training/financial_alert_augmented.jsonl",
    PROJECT_ROOT / "data/training/financial_alert_news_style_augmented.jsonl",
    PROJECT_ROOT / "data/training/financial_alert_real_news_gold.jsonl",
]
EVALUATION_PATHS = [
    PROJECT_ROOT / "data/evaluation/financial_alert_eval.jsonl",
    PROJECT_ROOT / "data/evaluation/financial_alert_real_disclosure_gold.jsonl",
    PROJECT_ROOT / "data/evaluation/financial_alert_real_news_gold.jsonl",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--universe", type=Path, default=UNIVERSE_PATH)
    parser.add_argument("--raw-alerts", type=Path, default=RAW_ALERTS_PATH)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    parser.add_argument("--minimum-universe-count", type=int, default=2_000)
    parser.add_argument("--minimum-real-data-stock-count", type=int, default=300)
    args = parser.parse_args()

    report = build_stock_coverage_report(
        universe_path=args.universe,
        training_paths=TRAINING_PATHS,
        evaluation_paths=EVALUATION_PATHS,
        raw_alert_path=args.raw_alerts,
        minimum_universe_count=args.minimum_universe_count,
        minimum_real_data_stock_count=args.minimum_real_data_stock_count,
    )
    payload = report.to_dict()
    write_json_report(args.report, payload)
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
