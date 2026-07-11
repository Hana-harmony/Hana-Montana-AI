import argparse
import json
import os
from pathlib import Path

from hannah_montana_ai.training.stock_universe import (
    STOCK_UNIVERSE_SCHEMA_VERSION,
    fetch_kis_stock_universe,
    fetch_open_dart_stock_universe,
    load_env_file,
    load_stock_universe,
    merge_stock_universe_metadata,
    write_json_report,
    write_stock_universe,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
UNIVERSE_PATH = PROJECT_ROOT / "data/reference/korea_stock_universe.csv"
REPORT_PATH = PROJECT_ROOT / "reports/stock-universe-sync.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=UNIVERSE_PATH)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    parser.add_argument("--env-file", type=Path, default=PROJECT_ROOT / "secrets.local.env")
    args = parser.parse_args()

    load_env_file(args.env_file)
    existing_entries = load_stock_universe(args.output)
    api_key = os.environ.get("OPEN_DART_API_KEY")
    dart_entries = fetch_open_dart_stock_universe(api_key) if api_key else []
    entries = merge_stock_universe_metadata(
        fetch_kis_stock_universe(),
        [existing_entries, dart_entries],
    )
    write_stock_universe(args.output, entries)
    report = {
        "schema_version": STOCK_UNIVERSE_SCHEMA_VERSION,
        "provider": "kis-stock-master+open-dart-metadata",
        "output_path": _report_path(args.output),
        "stock_count": len(entries),
        "credential_policy": (
            "KIS master is public; OPEN_DART_API_KEY metadata enrichment is optional "
            "and loaded from gitignored local env only"
        ),
    }
    write_json_report(args.report, report)
    print(json.dumps(report, ensure_ascii=False))


def _report_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    main()
