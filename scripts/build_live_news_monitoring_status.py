import argparse
import json
from pathlib import Path
from typing import Any

from hannah_montana_ai.training.live_news_evaluation import (
    build_live_news_monitoring_status,
    report_to_json,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LIVE_REPORT_PATH = PROJECT_ROOT / "reports/live-news-evaluation-report.json"
DEFAULT_RELEASE_REPORT_PATH = PROJECT_ROOT / "reports/model-release-report.json"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "reports/live-news-monitoring-status.json"


def main() -> None:
    args = _parse_args()
    live_report_path = _project_path(args.live_report)
    release_report_path = _project_path(args.release_report)
    output_path = _project_path(args.output)

    status = build_live_news_monitoring_status(
        live_report=_read_json(live_report_path),
        release_report=_read_json(release_report_path),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report_to_json(status), encoding="utf-8")
    print(report_to_json(status), end="")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate live news smoke/drift report freshness against the released model."
    )
    parser.add_argument("--live-report", type=Path, default=DEFAULT_LIVE_REPORT_PATH)
    parser.add_argument("--release-report", type=Path, default=DEFAULT_RELEASE_REPORT_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    return parser.parse_args()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _project_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


if __name__ == "__main__":
    main()
