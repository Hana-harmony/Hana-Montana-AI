import json
from pathlib import Path

from hannah_montana_ai.training.collector import read_raw_alerts, write_sharded_jsonl
from hannah_montana_ai.training.stock_universe import (
    StockUniverseMatcher,
    attach_stock_metadata,
    load_stock_universe,
)
from hannah_montana_ai.training.weak_labeler import weak_label

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data/raw/collected_alerts.jsonl"
OUTPUT_PATH = PROJECT_ROOT / "data/processed/weak_labeled_alerts.jsonl"
STOCK_UNIVERSE_PATH = PROJECT_ROOT / "data/reference/korea_stock_universe.csv"


def main() -> None:
    stock_universe = load_stock_universe(STOCK_UNIVERSE_PATH)
    stock_matcher = StockUniverseMatcher(stock_universe)
    rows: list[dict[str, object]] = []

    for alert in read_raw_alerts(RAW_PATH):
        label = weak_label(alert)
        if label is None:
            continue
        labeled = attach_stock_metadata(label, stock_matcher)
        rows.append(
            {
                "text": labeled.text,
                "tags": labeled.tags,
                "sentiment": labeled.sentiment,
                "importance": labeled.importance,
                "source_type": labeled.source_type,
                "stock_code": labeled.stock_code,
                "stock_name": labeled.stock_name,
                "stock_aliases": labeled.stock_aliases,
                "provider": labeled.provider,
                "published_at": labeled.published_at,
                "source_url": labeled.source_url,
                "content_hash": labeled.content_hash,
            }
        )

    write_sharded_jsonl(OUTPUT_PATH, rows)
    print(
        json.dumps(
            {"source": str(RAW_PATH.relative_to(PROJECT_ROOT)), "weak_labeled_count": len(rows)},
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
