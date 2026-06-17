import argparse
from pathlib import Path

from hannah_montana_ai.training.collector import load_local_env
from hannah_montana_ai.training.live_news_evaluation import (
    DEFAULT_LIVE_NEWS_INTENTS,
    build_live_news_evaluation_batch,
    report_to_json,
    rows_to_jsonl,
)
from hannah_montana_ai.training.stock_universe import load_stock_universe

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_PATH = PROJECT_ROOT / "secrets.local.env"
DEFAULT_STOCK_UNIVERSE_PATH = PROJECT_ROOT / "data/reference/korea_stock_universe.csv"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "data/evaluation/live_news_evaluation_batch.jsonl"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "reports/live-news-evaluation-report.json"


def main() -> None:
    args = _parse_args()
    env_path = _project_path(args.env_file)
    stock_universe_path = _project_path(args.stock_universe)
    output_path = _project_path(args.output)
    report_path = _project_path(args.report)

    load_local_env(env_path)
    stock_universe = load_stock_universe(stock_universe_path)
    batch = build_live_news_evaluation_batch(
        stock_universe=stock_universe,
        stock_universe_path=stock_universe_path,
        output_path=output_path,
        stock_sample_size=args.stock_sample_size,
        max_news_per_query=args.max_news_per_query,
        intents=tuple(args.intent or DEFAULT_LIVE_NEWS_INTENTS),
        seed=args.seed,
        sleep_seconds=args.sleep_seconds,
        max_retries=args.max_retries,
        sample_limit=args.sample_limit,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rows_to_jsonl(batch.rows), encoding="utf-8")
    report_path.write_text(report_to_json(batch.report), encoding="utf-8")
    print(report_to_json(batch.report), end="")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build an unlabeled live Naver news evaluation batch for smoke/drift review."
    )
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV_PATH)
    parser.add_argument("--stock-universe", type=Path, default=DEFAULT_STOCK_UNIVERSE_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--stock-sample-size", type=int, default=20)
    parser.add_argument("--max-news-per-query", type=int, default=3)
    parser.add_argument("--intent", action="append")
    parser.add_argument("--seed", type=int, default=20260613)
    parser.add_argument("--sleep-seconds", type=float, default=0.2)
    parser.add_argument("--max-retries", type=int, default=2)
    parser.add_argument("--sample-limit", type=int)
    return parser.parse_args()


def _project_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


if __name__ == "__main__":
    main()
