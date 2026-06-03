import json
from pathlib import Path

from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.training.dataset import load_labeled_alerts
from hannah_montana_ai.training.evaluator import evaluate_alert_analyzer

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_DATA = PROJECT_ROOT / "data/evaluation/financial_alert_eval.jsonl"
REPORT_PATH = PROJECT_ROOT / "reports/model-evaluation.json"


def main() -> None:
    samples = load_labeled_alerts(EVALUATION_DATA)
    result = evaluate_alert_analyzer(samples, AlertAnalyzer())
    REPORT_PATH.write_text(
        json.dumps(result.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
