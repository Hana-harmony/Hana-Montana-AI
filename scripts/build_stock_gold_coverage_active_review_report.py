import argparse
import json
from pathlib import Path

from hannah_montana_ai.training.active_review import (
    build_stock_gold_coverage_active_review_packet,
    build_stock_gold_coverage_active_review_report,
    write_stock_gold_active_review_packet,
    write_stock_gold_active_review_report,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "src/hannah_montana_ai/model_store/financial_nlp_ml.joblib"
COVERAGE_PLAN_PATH = PROJECT_ROOT / "data/curation/stock_gold_coverage_review_plan.jsonl"
PACKET_PATH = (
    PROJECT_ROOT / "data/curation/stock_gold_coverage_active_review_packet.jsonl"
)
REPORT_PATH = PROJECT_ROOT / "reports/stock-gold-coverage-active-review-report.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=MODEL_PATH)
    parser.add_argument("--coverage-plan", type=Path, default=COVERAGE_PLAN_PATH)
    parser.add_argument("--packet-output", type=Path, default=PACKET_PATH)
    parser.add_argument("--top-n-per-split", type=int, default=100)
    parser.add_argument("--top-n-per-wave", type=int, default=10)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    args = parser.parse_args()

    packet_rows = build_stock_gold_coverage_active_review_packet(
        coverage_plan_path=args.coverage_plan,
        model_path=args.model,
    )
    report = build_stock_gold_coverage_active_review_report(
        coverage_plan_path=args.coverage_plan,
        model_path=args.model,
        top_n_per_split=args.top_n_per_split,
        top_n_per_wave=args.top_n_per_wave,
    )
    write_stock_gold_active_review_packet(args.packet_output, packet_rows)
    write_stock_gold_active_review_report(args.report, report)
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
