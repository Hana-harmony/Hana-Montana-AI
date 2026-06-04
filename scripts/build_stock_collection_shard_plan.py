import argparse
import json
from pathlib import Path

from hannah_montana_ai.training.stock_collection_plan import (
    build_stock_collection_shard_plan,
    write_stock_collection_shard_plan,
    write_stock_collection_shard_report,
)
from hannah_montana_ai.training.stock_universe import DEFAULT_NEWS_INTENTS

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STOCK_UNIVERSE_PATH = PROJECT_ROOT / "data/reference/korea_stock_universe.csv"
RAW_ALERTS_PATH = PROJECT_ROOT / "data/raw/collected_alerts.jsonl"
CANDIDATE_PATH = PROJECT_ROOT / "data/curation/stock_training_candidate_queue.jsonl"
PLAN_PATH = PROJECT_ROOT / "data/curation/stock_collection_shard_plan.jsonl"
REPORT_PATH = PROJECT_ROOT / "reports/stock-collection-shard-plan.json"
TRAINING_PATHS = [
    PROJECT_ROOT / "data/training/financial_alert_corpus.jsonl",
    PROJECT_ROOT / "data/training/financial_alert_augmented.jsonl",
    PROJECT_ROOT / "data/training/financial_alert_news_style_augmented.jsonl",
    PROJECT_ROOT / "data/training/financial_alert_real_news_gold.jsonl",
    PROJECT_ROOT / "data/training/financial_alert_stock_review_gold.jsonl",
]
EVALUATION_PATHS = [
    PROJECT_ROOT / "data/evaluation/financial_alert_eval.jsonl",
    PROJECT_ROOT / "data/evaluation/financial_alert_real_disclosure_gold.jsonl",
    PROJECT_ROOT / "data/evaluation/financial_alert_real_news_gold.jsonl",
    PROJECT_ROOT / "data/evaluation/financial_alert_stock_review_gold.jsonl",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stock-universe", type=Path, default=STOCK_UNIVERSE_PATH)
    parser.add_argument("--raw-alerts", type=Path, default=RAW_ALERTS_PATH)
    parser.add_argument("--candidate-queue", type=Path, default=CANDIDATE_PATH)
    parser.add_argument("--output", type=Path, default=PLAN_PATH)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    parser.add_argument("--training-path", action="append", type=Path)
    parser.add_argument("--evaluation-path", action="append", type=Path)
    parser.add_argument("--shard-size", type=int, default=100)
    parser.add_argument("--stock-limit", type=int)
    parser.add_argument("--intent", action="append")
    args = parser.parse_args()

    result = build_stock_collection_shard_plan(
        stock_universe_path=args.stock_universe,
        raw_alert_path=args.raw_alerts,
        candidate_path=args.candidate_queue,
        training_paths=args.training_path or TRAINING_PATHS,
        evaluation_paths=args.evaluation_path or EVALUATION_PATHS,
        shard_size=args.shard_size,
        stock_limit=args.stock_limit,
        intents=tuple(args.intent) if args.intent else DEFAULT_NEWS_INTENTS,
    )
    write_stock_collection_shard_plan(args.output, result.rows)
    write_stock_collection_shard_report(args.report, result.report)
    print(json.dumps(result.report, ensure_ascii=False))


if __name__ == "__main__":
    main()
