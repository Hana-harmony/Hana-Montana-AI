import csv
import json
from collections import defaultdict
from datetime import UTC, date, datetime
from pathlib import Path

import joblib

from hannah_montana_ai.services.foreign_ownership_quantity_model import (
    ForeignOwnershipQuantityModel,
    ForeignOwnershipQuantityPoint,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "src/hannah_montana_ai/model_store/foreign_ownership_quantity_ml.joblib"
HISTORY_PATH = PROJECT_ROOT / "data/training/foreign_ownership_quantity_history.csv"
RESTRICTED_STOCK_CODES_PATH = (
    PROJECT_ROOT / "data/training/foreign_ownership_restricted_stock_codes.csv"
)
REPORT_PATH = PROJECT_ROOT / "reports/foreign-ownership-serving-interval-audit.json"


def main() -> None:
    payload = joblib.load(MODEL_PATH)
    histories = _load_histories()
    model = ForeignOwnershipQuantityModel(MODEL_PATH)
    rows = []
    for stock_code in sorted(payload["prediction_interval_abs_p90_by_stock"]):
        history = histories[stock_code]
        prediction = model.predict(stock_code, history)
        limit_quantity = history[-1].foreign_limit_quantity
        width_quantity = prediction.upper_quantity - prediction.lower_quantity
        rows.append(
            {
                "stock_code": stock_code,
                "base_date": str(history[-1].base_date),
                "lower_quantity": prediction.lower_quantity,
                "predicted_quantity": prediction.predicted_quantity,
                "upper_quantity": prediction.upper_quantity,
                "full_width_quantity": width_quantity,
                "full_width_limit_exhaustion_percentage_points": (
                    width_quantity * 100.0 / limit_quantity
                ),
                "walk_forward_abs_p90_cap_quantity": payload[
                    "prediction_interval_abs_p90_by_stock"
                ][stock_code],
                "walk_forward_coverage": payload["prediction_interval_coverage_by_stock"][
                    stock_code
                ],
            }
        )
    widths = sorted(float(row["full_width_limit_exhaustion_percentage_points"]) for row in rows)
    with RESTRICTED_STOCK_CODES_PATH.open(newline="", encoding="utf-8") as csv_file:
        restricted_stock_codes = {row["stock_code"] for row in csv.DictReader(csv_file)}
    interval_stock_codes = {str(row["stock_code"]) for row in rows}
    report = {
        "schema_version": "foreign-ownership-serving-interval-audit/v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "model_version": payload["model_version"],
        "restricted_stock_count": len(restricted_stock_codes),
        "ml_interval_stock_count": len(rows),
        "zero_limit_excluded_stock_codes": sorted(restricted_stock_codes - interval_stock_codes),
        "interval_policy": (
            "stock-level walk-forward absolute-error p90 cap with latest "
            "60-observation absolute-delta p90 regime adaptation"
        ),
        "walk_forward_coverage_min": min(float(row["walk_forward_coverage"]) for row in rows),
        "full_width_limit_exhaustion_percentage_points": {
            "min": widths[0],
            "median": widths[len(widths) // 2],
            "p90": widths[min(len(widths) - 1, int(len(widths) * 0.9))],
            "max": widths[-1],
        },
        "rows": rows,
    }
    REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({key: value for key, value in report.items() if key != "rows"}))


def _load_histories() -> dict[str, list[ForeignOwnershipQuantityPoint]]:
    histories: dict[str, list[ForeignOwnershipQuantityPoint]] = defaultdict(list)
    with HISTORY_PATH.open(newline="", encoding="utf-8") as csv_file:
        for row in csv.DictReader(csv_file):
            stock_code = row["stock_code"]
            histories[stock_code].append(
                ForeignOwnershipQuantityPoint(
                    stock_code=stock_code,
                    base_date=date.fromisoformat(row["base_date"]),
                    foreign_owned_quantity=int(row["foreign_owned_quantity"]),
                    foreign_limit_quantity=int(row["foreign_limit_quantity"]),
                )
            )
    return histories


if __name__ == "__main__":
    main()
