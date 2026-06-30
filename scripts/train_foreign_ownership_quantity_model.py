import argparse
import json
from pathlib import Path

from hannah_montana_ai.training.foreign_ownership_quantity_trainer import (
    ForeignOwnershipQuantityModelTrainingReport,
    train_foreign_ownership_quantity_model,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRAINING_DATA_PATH = (
    PROJECT_ROOT / "data/training/foreign_ownership_quantity_history.csv"
)
DEFAULT_MODEL_PATH = (
    PROJECT_ROOT / "src/hannah_montana_ai/model_store/foreign_ownership_quantity_ml.joblib"
)
DEFAULT_REPORT_PATH = PROJECT_ROOT / "reports/foreign-ownership-quantity-training-report.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--training-data", type=Path, default=DEFAULT_TRAINING_DATA_PATH)
    parser.add_argument("--model-path", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--restricted-stock-codes", type=Path)
    parser.add_argument("--min-promotable-stock-count", type=int, default=1_000)
    parser.add_argument("--min-promotable-history-days", type=int, default=730)
    parser.add_argument("--min-promotable-observations", type=int, default=100_000)
    parser.add_argument("--max-model-training-samples", type=int, default=250_000)
    args = parser.parse_args()

    report = train_foreign_ownership_quantity_model(
        args.training_data,
        args.model_path,
        restricted_stock_codes_path=args.restricted_stock_codes,
        minimum_promotable_stock_count=args.min_promotable_stock_count,
        minimum_promotable_history_days=args.min_promotable_history_days,
        minimum_promotable_observations=args.min_promotable_observations,
        max_model_training_samples=args.max_model_training_samples,
    )
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(_summary(report, args.report_path), ensure_ascii=False))


def _summary(
    report: ForeignOwnershipQuantityModelTrainingReport,
    report_path: Path,
) -> dict[str, object]:
    report_dict = report.to_dict()
    runtime_by_stock = dict(report_dict["runtime_by_stock"])
    return {
        "release_status": report.release_status,
        "stock_count": report.stock_count,
        "observation_count": report.observation_count,
        "sample_count": report.sample_count,
        "train_date_min": report.train_date_min,
        "train_date_max": report.train_date_max,
        "selected_model": report.selected_model,
        "selected_blend_alpha": report.selected_blend_alpha,
        "baseline_metrics": report.baseline_metrics,
        "guarded_runtime_metrics": report.guarded_runtime_metrics,
        "guarded_improvement_over_baseline": report.guarded_improvement_over_baseline,
        "quality_gates": report.quality_gates,
        "ml_runtime_stock_count": sum(
            1 for runtime in runtime_by_stock.values() if runtime == "ml"
        ),
        "baseline_runtime_stock_count": sum(
            1 for runtime in runtime_by_stock.values() if runtime == "baseline"
        ),
        "model_path": report.model_path,
        "report_path": str(report_path),
    }


if __name__ == "__main__":
    main()
