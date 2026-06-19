import argparse
from datetime import UTC, datetime
from pathlib import Path

from hannah_montana_ai.training.translation_sample_report import (
    DEFAULT_TRANSLATION_SAMPLE_LIMIT_PER_SOURCE,
    build_translation_sample_report,
    report_to_json,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_NEWS_GOLD_PATH = PROJECT_ROOT / "data/evaluation/financial_alert_real_news_gold.jsonl"
DEFAULT_DISCLOSURE_GOLD_PATH = (
    PROJECT_ROOT / "data/evaluation/financial_alert_real_disclosure_gold.jsonl"
)
DEFAULT_REPORT_PATH = PROJECT_ROOT / "reports/translation-sample-report.json"


def main() -> None:
    args = _parse_args()
    generated_at = (
        datetime.fromisoformat(args.generated_at)
        if args.generated_at
        else datetime.now(UTC)
    )
    report = build_translation_sample_report(
        news_gold_path=_project_path(args.news_gold),
        disclosure_gold_path=_project_path(args.disclosure_gold),
        sample_limit_per_source=args.sample_limit_per_source,
        generated_at=generated_at,
    )
    report_path = _project_path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_to_json(report), encoding="utf-8")
    print(report_to_json(report), end="")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a real news/disclosure translation sample report with Hannah AI analysis, "
            "local glossary translation, and review findings."
        )
    )
    parser.add_argument("--news-gold", type=Path, default=DEFAULT_NEWS_GOLD_PATH)
    parser.add_argument("--disclosure-gold", type=Path, default=DEFAULT_DISCLOSURE_GOLD_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument(
        "--sample-limit-per-source",
        type=int,
        default=DEFAULT_TRANSLATION_SAMPLE_LIMIT_PER_SOURCE,
    )
    parser.add_argument("--generated-at")
    return parser.parse_args()


def _project_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


if __name__ == "__main__":
    main()
