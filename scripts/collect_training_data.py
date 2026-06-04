import argparse
import json
from datetime import date
from pathlib import Path

from hannah_montana_ai.training.collector import (
    NAVER_QUERIES,
    collect_naver_news,
    collect_open_dart,
    collection_status_to_dict,
    load_local_env,
    merge_raw_alerts,
    raw_alert_to_dict,
    read_raw_alerts,
    should_write_raw_alerts,
    write_jsonl,
)
from hannah_montana_ai.training.stock_collection_plan import (
    load_stock_collection_plan_queries,
)
from hannah_montana_ai.training.stock_universe import (
    StockUniverseMatcher,
    attach_stock_metadata,
    build_stock_news_queries,
    load_stock_universe,
)
from hannah_montana_ai.training.weak_labeler import weak_label

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_ALERTS_PATH = PROJECT_ROOT / "data/raw/collected_alerts.jsonl"
WEAK_LABELED_PATH = PROJECT_ROOT / "data/processed/weak_labeled_alerts.jsonl"
REPORT_PATH = PROJECT_ROOT / "reports/dataset-collection.json"
DEFAULT_STOCK_UNIVERSE_PATH = PROJECT_ROOT / "data/reference/korea_stock_universe.csv"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-news-per-query", type=int, default=200)
    parser.add_argument("--news-sleep-seconds", type=float, default=0.4)
    parser.add_argument("--news-max-retries", type=int, default=3)
    parser.add_argument("--dart-days", type=int, default=30)
    parser.add_argument("--dart-pages", type=int, default=3)
    parser.add_argument("--dart-end-date", type=date.fromisoformat)
    parser.add_argument("--dart-sleep-seconds", type=float, default=0.1)
    parser.add_argument("--reuse-existing-raw", action="store_true")
    parser.add_argument("--force-overwrite-raw", action="store_true")
    parser.add_argument("--skip-news", action="store_true")
    parser.add_argument("--skip-dart", action="store_true")
    parser.add_argument("--stock-universe-path", type=Path, default=DEFAULT_STOCK_UNIVERSE_PATH)
    parser.add_argument("--use-stock-universe-news-queries", action="store_true")
    parser.add_argument("--stock-query-limit", type=int)
    parser.add_argument("--stock-collection-plan", type=Path)
    parser.add_argument("--stock-collection-plan-shard-index", type=int)
    args = parser.parse_args()

    load_local_env(PROJECT_ROOT / "secrets.local.env")
    stock_universe = load_stock_universe(args.stock_universe_path)
    stock_matcher = StockUniverseMatcher(stock_universe) if stock_universe else None
    existing_raw_alerts = read_raw_alerts(RAW_ALERTS_PATH)
    raw_alerts = []
    collection_statuses = []
    if args.reuse_existing_raw:
        raw_alerts.extend(existing_raw_alerts)
    if not args.skip_news:
        news_queries = None
        if args.stock_collection_plan:
            news_queries = list(
                dict.fromkeys(
                    [
                        *NAVER_QUERIES,
                        *load_stock_collection_plan_queries(
                            args.stock_collection_plan,
                            shard_index=args.stock_collection_plan_shard_index,
                            stock_limit=args.stock_query_limit,
                        ),
                    ]
                )
            )
        elif args.use_stock_universe_news_queries:
            news_queries = list(
                dict.fromkeys(
                    [
                        *NAVER_QUERIES,
                        *build_stock_news_queries(
                            stock_universe,
                            stock_limit=args.stock_query_limit,
                        ),
                    ]
                )
            )
        result = collect_naver_news(
            max_per_query=args.max_news_per_query,
            sleep_seconds=args.news_sleep_seconds,
            max_retries=args.news_max_retries,
            queries=news_queries,
        )
        raw_alerts.extend(result.alerts)
        collection_statuses.append(result.status)
    if not args.skip_dart:
        result = collect_open_dart(
            days=args.dart_days,
            pages=args.dart_pages,
            end_date=args.dart_end_date,
            sleep_seconds=args.dart_sleep_seconds,
        )
        raw_alerts.extend(result.alerts)
        collection_statuses.append(result.status)
    raw_alerts = merge_raw_alerts(raw_alerts)
    labeled_alerts = [
        attach_stock_metadata(label, stock_matcher)
        for alert in raw_alerts
        if (label := weak_label(alert))
    ]
    should_write = should_write_raw_alerts(
        existing_count=len(existing_raw_alerts),
        next_count=len(raw_alerts),
        force=args.force_overwrite_raw,
    )

    if should_write:
        write_jsonl(RAW_ALERTS_PATH, [raw_alert_to_dict(alert) for alert in raw_alerts])
        write_jsonl(
            WEAK_LABELED_PATH,
            [
                {
                    "text": alert.text,
                    "tags": alert.tags,
                    "sentiment": alert.sentiment,
                    "importance": alert.importance,
                    "source_type": alert.source_type,
                    "stock_code": alert.stock_code,
                    "stock_name": alert.stock_name,
                    "stock_aliases": alert.stock_aliases,
                }
                for alert in labeled_alerts
            ],
        )

    report = {
        "raw_write_status": "written" if should_write else "skipped_existing_dataset_is_larger",
        "existing_raw_count": len(existing_raw_alerts),
        "raw_count": len(raw_alerts),
        "weak_labeled_count": len(labeled_alerts),
        "stock_universe": {
            "path": _report_path(args.stock_universe_path),
            "stock_count": len(stock_universe),
            "news_query_mode": _news_query_mode(args),
            "stock_query_limit": args.stock_query_limit,
            "stock_collection_plan": _report_path(args.stock_collection_plan)
            if args.stock_collection_plan
            else None,
            "stock_collection_plan_shard_index": args.stock_collection_plan_shard_index,
            "matched_weak_labeled_stock_count": len(
                {alert.stock_code for alert in labeled_alerts if alert.stock_code}
            ),
        },
        "providers": {
            "naver-news": sum(1 for alert in raw_alerts if alert.provider == "naver-news"),
            "open-dart": sum(1 for alert in raw_alerts if alert.provider == "open-dart"),
        },
        "provider_statuses": collection_status_to_dict(collection_statuses),
    }
    (PROJECT_ROOT / "reports").mkdir(exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))


def _report_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def _news_query_mode(args: argparse.Namespace) -> str:
    if args.stock_collection_plan:
        return "stock_collection_shard_plan"
    if args.use_stock_universe_news_queries:
        return "stock_universe"
    return "fixed_seed_queries"


if __name__ == "__main__":
    main()
