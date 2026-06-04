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
ML_TRAINING_REPORT_PATH = PROJECT_ROOT / "reports/ml-training-report.json"
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
    parser.add_argument("--ml-training-report", type=Path, default=ML_TRAINING_REPORT_PATH)
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
    payload["event_model_pseudo_training_coverage"] = _pseudo_training_coverage(
        args.ml_training_report,
        payload["training_stock_count"],
    )
    write_json_report(args.report, payload)
    print(json.dumps(payload, ensure_ascii=False))


def _pseudo_training_coverage(
    ml_training_report_path: Path,
    supervised_training_stock_count: int,
) -> dict[str, object]:
    if not ml_training_report_path.exists():
        return {
            "status": "source_missing",
            "source_path": _report_path(ml_training_report_path),
            "stock_candidate_event_training_sample_count": 0,
            "stock_candidate_event_training_stock_count": 0,
            "effective_event_training_stock_count_lower_bound": (
                supervised_training_stock_count
            ),
        }

    report = json.loads(ml_training_report_path.read_text(encoding="utf-8"))
    stock_candidate = report.get("pseudo_labeling", {}).get(
        "stock_candidate_labeling",
        {},
    )
    stock_count = int(stock_candidate.get("accepted_stock_count", 0) or 0)
    return {
        "status": stock_candidate.get("status", "not_configured"),
        "source_path": _report_path(ml_training_report_path),
        "stock_candidate_event_training_sample_count": int(
            stock_candidate.get("accepted_count", 0) or 0
        ),
        "stock_candidate_event_training_stock_count": stock_count,
        "stock_candidate_label_distribution": stock_candidate.get(
            "accepted_count_by_primary_label",
            {},
        ),
        "stock_candidate_per_stock_quota": stock_candidate.get("per_stock_quota"),
        "effective_event_training_stock_count_lower_bound": max(
            supervised_training_stock_count,
            stock_count,
        ),
        "interpretation": (
            "pseudo event labels are model-training coverage, not supervised gold coverage"
        ),
    }


def _report_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT.resolve()))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    main()
