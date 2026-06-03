import json
from pathlib import Path

from hannah_montana_ai.training.trainer import train_keyword_model

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRAINING_DATA = PROJECT_ROOT / "data/training/financial_alert_corpus.jsonl"
MODEL_PATH = PROJECT_ROOT / "src/hannah_montana_ai/model_store/financial_nlp_baseline.json"


def main() -> None:
    payload = train_keyword_model(TRAINING_DATA)
    MODEL_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
