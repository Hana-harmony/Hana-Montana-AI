import argparse
import json
from pathlib import Path

from hannah_montana_ai.training.stock_linker_trainer import (
    train_stock_linker_model,
    write_stock_linker_report,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
STOCK_UNIVERSE_PATH = PROJECT_ROOT / "data/reference/korea_stock_universe.csv"
MODEL_PATH = PROJECT_ROOT / "src/hannah_montana_ai/model_store/stock_linker_ml.joblib"
TRAINING_DATA_PATH = PROJECT_ROOT / "data/training/stock_linker_training.jsonl"
REPORT_PATH = PROJECT_ROOT / "reports/stock-linker-training-report.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stock-universe", type=Path, default=STOCK_UNIVERSE_PATH)
    parser.add_argument("--model-path", type=Path, default=MODEL_PATH)
    parser.add_argument("--training-data", type=Path, default=TRAINING_DATA_PATH)
    parser.add_argument("--report", type=Path, default=REPORT_PATH)
    args = parser.parse_args()

    result = train_stock_linker_model(
        stock_universe_path=args.stock_universe,
        model_path=args.model_path,
        training_data_path=args.training_data,
    )
    write_stock_linker_report(args.report, result.report)
    print(json.dumps(result.report, ensure_ascii=False))


if __name__ == "__main__":
    main()
