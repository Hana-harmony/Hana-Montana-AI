import argparse
import json
from datetime import date
from pathlib import Path

from hannah_montana_ai.training.collector import (
    collect_naver_news,
    collect_open_dart,
    load_local_env,
    raw_alert_to_dict,
    read_raw_alerts,
    write_jsonl,
)
from hannah_montana_ai.training.weak_labeler import weak_label

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-news-per-query", type=int, default=200)
    parser.add_argument("--dart-days", type=int, default=30)
    parser.add_argument("--dart-pages", type=int, default=3)
    parser.add_argument("--dart-end-date", type=date.fromisoformat)
    parser.add_argument("--reuse-existing-raw", action="store_true")
    parser.add_argument("--skip-news", action="store_true")
    parser.add_argument("--skip-dart", action="store_true")
    args = parser.parse_args()

    load_local_env(PROJECT_ROOT / "secrets.local.env")
    raw_alerts = []
    if args.reuse_existing_raw:
        raw_alerts.extend(read_raw_alerts(PROJECT_ROOT / "data/raw/collected_alerts.jsonl"))
    if not args.skip_news:
        raw_alerts.extend(collect_naver_news(max_per_query=args.max_news_per_query))
    if not args.skip_dart:
        raw_alerts.extend(
            collect_open_dart(
                days=args.dart_days,
                pages=args.dart_pages,
                end_date=args.dart_end_date,
            )
        )
    raw_alerts = list({alert.content_hash: alert for alert in raw_alerts}.values())
    labeled_alerts = [label for alert in raw_alerts if (label := weak_label(alert))]

    write_jsonl(
        PROJECT_ROOT / "data/raw/collected_alerts.jsonl",
        [raw_alert_to_dict(alert) for alert in raw_alerts],
    )
    write_jsonl(
        PROJECT_ROOT / "data/processed/weak_labeled_alerts.jsonl",
        [
            {
                "text": alert.text,
                "tags": alert.tags,
                "sentiment": alert.sentiment,
                "importance": alert.importance,
                "source_type": alert.source_type,
            }
            for alert in labeled_alerts
        ],
    )
    report = {
        "raw_count": len(raw_alerts),
        "weak_labeled_count": len(labeled_alerts),
        "providers": {
            "naver-news": sum(1 for alert in raw_alerts if alert.provider == "naver-news"),
            "open-dart": sum(1 for alert in raw_alerts if alert.provider == "open-dart"),
        },
    }
    (PROJECT_ROOT / "reports").mkdir(exist_ok=True)
    (PROJECT_ROOT / "reports/dataset-collection.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
