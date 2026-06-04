import json
from pathlib import Path

from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.training.dataset import load_labeled_alerts
from hannah_montana_ai.training.evaluator import evaluate_alert_analyzer

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_DATA = PROJECT_ROOT / "data/evaluation/financial_alert_eval.jsonl"
REAL_DISCLOSURE_GOLD_DATA = (
    PROJECT_ROOT / "data/evaluation/financial_alert_real_disclosure_gold.jsonl"
)
REAL_NEWS_GOLD_DATA = PROJECT_ROOT / "data/evaluation/financial_alert_real_news_gold.jsonl"
STOCK_REVIEW_GOLD_DATA = (
    PROJECT_ROOT / "data/evaluation/financial_alert_stock_review_gold.jsonl"
)
REPORT_PATH = PROJECT_ROOT / "reports/ml-model-evaluation.json"


def main() -> None:
    analyzer = AlertAnalyzer()
    result = evaluate_alert_analyzer(load_labeled_alerts(EVALUATION_DATA), analyzer)
    real_disclosure_result = evaluate_alert_analyzer(
        load_labeled_alerts(REAL_DISCLOSURE_GOLD_DATA),
        analyzer,
    )
    real_news_result = evaluate_alert_analyzer(
        load_labeled_alerts(REAL_NEWS_GOLD_DATA),
        analyzer,
    )
    stock_review_gold_samples = (
        load_labeled_alerts(STOCK_REVIEW_GOLD_DATA)
        if STOCK_REVIEW_GOLD_DATA.exists()
        else []
    )
    report = {
        "benchmark": result.to_dict(),
        "real_disclosure_gold": real_disclosure_result.to_dict(),
        "real_news_gold": real_news_result.to_dict(),
    }
    if stock_review_gold_samples:
        report["stock_review_gold"] = evaluate_alert_analyzer(
            stock_review_gold_samples,
            analyzer,
        ).to_dict()
    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
