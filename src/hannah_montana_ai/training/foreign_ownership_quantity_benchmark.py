import argparse
import contextlib
import io
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from hannah_montana_ai.services.foreign_ownership_quantity_model import (
    RUNTIME_POLICIES,
    RUNTIME_POLICY_ML,
    build_training_samples,
    regression_metrics,
    runtime_policy_quantity,
)
from hannah_montana_ai.training.foreign_ownership_quantity_trainer import (
    _load_restricted_stock_codes,
    _walk_forward_folds,
    load_foreign_ownership_quantity_points,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TRAINING_DATA_PATH = (
    PROJECT_ROOT / "data/training/foreign_ownership_quantity_history.csv"
)
DEFAULT_TRAINING_REPORT_PATH = (
    PROJECT_ROOT / "reports/foreign-ownership-quantity-training-report.json"
)
DEFAULT_BENCHMARK_REPORT_PATH = (
    PROJECT_ROOT / "reports/foreign-ownership-quantity-sota-benchmark.json"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--training-data", type=Path, default=DEFAULT_TRAINING_DATA_PATH)
    parser.add_argument("--training-report", type=Path, default=DEFAULT_TRAINING_REPORT_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_BENCHMARK_REPORT_PATH)
    parser.add_argument("--restricted-stock-codes", type=Path)
    parser.add_argument("--include-neural-sota", action="store_true")
    parser.add_argument("--sota-top-stock-count", type=int, default=30)
    parser.add_argument("--sota-max-steps", type=int, default=20)
    args = parser.parse_args()

    report = benchmark_foreign_ownership_quantity_models(
        training_data_path=args.training_data,
        training_report_path=args.training_report,
        restricted_stock_codes_path=args.restricted_stock_codes,
        include_neural_sota=args.include_neural_sota,
        sota_top_stock_count=args.sota_top_stock_count,
        sota_max_steps=args.sota_max_steps,
    )
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    args.report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(_summary(report, args.report_path), ensure_ascii=False))


def benchmark_foreign_ownership_quantity_models(
    *,
    training_data_path: Path,
    training_report_path: Path,
    restricted_stock_codes_path: Path | None = None,
    include_neural_sota: bool = False,
    sota_top_stock_count: int = 30,
    sota_max_steps: int = 20,
) -> dict[str, Any]:
    points = load_foreign_ownership_quantity_points(training_data_path)
    restricted_stock_codes = _load_restricted_stock_codes(restricted_stock_codes_path)
    if restricted_stock_codes is not None:
        points = [point for point in points if point.stock_code in restricted_stock_codes]
    samples = build_training_samples(points)
    folds = _walk_forward_folds(samples)
    training_report = _load_training_report(training_report_path)
    benchmark: dict[str, Any] = {
        "schema_version": "foreign-ownership-quantity-benchmark/v1",
        "generated_at": datetime.now(UTC).isoformat(),
        "training_data_path": str(training_data_path),
        "training_report_path": str(training_report_path),
        "restricted_stock_codes_path": (
            str(restricted_stock_codes_path) if restricted_stock_codes_path else None
        ),
        "restricted_universe_applied": restricted_stock_codes is not None,
        "stock_count": len({point.stock_code for point in points}),
        "observation_count": len(points),
        "sample_count": len(samples),
        "walk_forward_fold_count": len(folds),
        "current_model_report": _training_report_summary(training_report),
        "published_sota_diagnostics": [],
        "notes": [
            "Full-universe rows use one-step walk-forward evaluation over every "
            "available restricted-stock sample.",
            "Neural SOTA diagnostics are optional because N-HiTS/PatchTST require "
            "heavy torch dependencies and CPU runtime grows quickly.",
        ],
    }
    benchmark["full_universe_walk_forward"] = _full_universe_policy_benchmark(
        folds,
        training_report,
    )
    if include_neural_sota:
        benchmark["published_sota_diagnostics"] = _neural_sota_diagnostics(
            points,
            folds,
            top_stock_count=sota_top_stock_count,
            max_steps=sota_max_steps,
        )
    else:
        benchmark["published_sota_diagnostics"] = [
            {
                "model": "N-HiTS",
                "status": "not_run",
                "reason": (
                    "Run with --include-neural-sota to execute optional "
                    "neuralforecast benchmark."
                ),
            },
            {
                "model": "PatchTST",
                "status": "not_run",
                "reason": (
                    "Run with --include-neural-sota to execute optional "
                    "neuralforecast benchmark."
                ),
            },
        ]
    return benchmark


def _full_universe_policy_benchmark(
    folds: list[Any],
    training_report: dict[str, Any],
) -> list[dict[str, Any]]:
    actual: list[int] = []
    predictions_by_policy: dict[str, list[int]] = {
        policy: [] for policy in RUNTIME_POLICIES if policy != RUNTIME_POLICY_ML
    }
    for _, test_samples in folds:
        for sample in test_samples:
            actual.append(sample.target_quantity)
            for policy in predictions_by_policy:
                predictions_by_policy[policy].append(
                    runtime_policy_quantity(
                        sample.previous_quantity,
                        sample.features,
                        policy,
                    )
                )
    rows: list[dict[str, Any]] = [
        {
            "model": policy,
            "scope": "full_universe_walk_forward",
            "metrics": regression_metrics(actual, predicted),
            "sample_count": len(actual),
        }
        for policy, predicted in predictions_by_policy.items()
    ]
    if training_report.get("guarded_runtime_metrics"):
        rows.append(
            {
                "model": "hannah_promoted_guarded_runtime",
                "scope": "full_universe_walk_forward",
                "metrics": training_report["guarded_runtime_metrics"],
                "sample_count": len(actual),
                "selected_model": training_report.get("selected_model"),
                "selected_blend_alpha": training_report.get("selected_blend_alpha"),
                "release_status": training_report.get("release_status"),
                "runtime_policy_counts": _runtime_policy_counts(training_report),
            }
        )
    baseline_metrics = cast(dict[str, float], rows[0]["metrics"])
    for row in rows:
        row["improvement_over_persistence"] = _improvement(
            baseline_metrics,
            cast(dict[str, float], row["metrics"]),
        )
    return sorted(rows, key=lambda row: row["metrics"]["mae"])


def _neural_sota_diagnostics(
    points: list[Any],
    folds: list[Any],
    *,
    top_stock_count: int,
    max_steps: int,
) -> list[dict[str, Any]]:
    try:
        import pandas as pd
        from neuralforecast import NeuralForecast
        from neuralforecast.models import NHITS, PatchTST
    except ImportError as exception:
        return [
            {
                "model": "neuralforecast",
                "status": "not_run",
                "reason": f"Optional dependency unavailable: {exception}",
            }
        ]

    all_test_stocks = sorted(
        {
            sample.stock_code
            for _, test_samples in folds
            for sample in test_samples
        }
    )
    latest_quantity_by_stock: dict[str, int] = {
        stock_code: 0 for stock_code in all_test_stocks
    }
    points_by_stock: dict[str, list[Any]] = {}
    for point in points:
        if point.stock_code in latest_quantity_by_stock:
            latest_quantity_by_stock[point.stock_code] = point.foreign_owned_quantity
            points_by_stock.setdefault(point.stock_code, []).append(point)
    selected_stocks = sorted(
        latest_quantity_by_stock,
        key=lambda stock_code: latest_quantity_by_stock[stock_code],
        reverse=True,
    )[:top_stock_count or len(all_test_stocks)]
    selected_stock_set = set(selected_stocks)
    sequence_frame, sequence_lookup = _sequential_neural_dataframe(
        points_by_stock,
        selected_stock_set,
        pd,
    )
    diagnostics: list[dict[str, Any]] = []
    for model_name, model_alias, model_factory in [
        ("N-HiTS", "NHITS", _nhits_factory(NHITS, max_steps)),
        ("PatchTST", "PatchTST", _patchtst_factory(PatchTST, max_steps)),
    ]:
        try:
            actual: list[int] = []
            predicted: list[int] = []
            persistence: list[int] = []
            for fold_index, (_, test_samples) in enumerate(folds, start=1):
                fold_samples = [
                    sample
                    for sample in test_samples
                    if sample.stock_code in selected_stock_set
                ]
                if not fold_samples:
                    continue
                fold_prediction = _neural_fold_predictions(
                    sequence_frame,
                    sequence_lookup,
                    fold_samples,
                    NeuralForecast,
                    model_factory,
                    model_alias,
                    pd,
                )
                actual.extend(fold_prediction["actual"])
                predicted.extend(fold_prediction["predicted"])
                persistence.extend(fold_prediction["persistence"])
                print(
                    "[foreign-ownership-benchmark] "
                    f"model={model_name} fold={fold_index} "
                    f"samples={len(fold_prediction['actual'])}"
                )
            diagnostics.append(
                {
                    "model": model_name,
                    "status": "completed",
                    "scope": "restricted_walk_forward_same_folds",
                    "sample_count": len(actual),
                    "stock_count": len(selected_stocks),
                    "fold_count": len(folds),
                    "max_steps": max_steps,
                    "metrics": regression_metrics(actual, predicted),
                    "same_scope_persistence_metrics": regression_metrics(
                        actual,
                        persistence,
                    ),
                    "stock_selection": (
                        "all_restricted_walk_forward_stocks"
                        if len(selected_stocks) == len(all_test_stocks)
                        else f"top_{len(selected_stocks)}_recent_quantity_stocks"
                    ),
                    "same_stock_universe": len(selected_stocks) == len(all_test_stocks),
                    "same_walk_forward_samples": len(selected_stocks) == len(all_test_stocks),
                    "forecast_protocol": "one_step_with_observed_history_until_previous_point",
                }
            )
        except Exception as exception:  # noqa: BLE001
            diagnostics.append(
                {
                    "model": model_name,
                    "status": "failed",
                    "reason": str(exception),
                }
            )
    return diagnostics


def _sequential_neural_dataframe(
    points_by_stock: dict[str, list[Any]],
    selected_stocks: set[str],
    pd: Any,
) -> tuple[Any, dict[tuple[str, Any], dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    lookup: dict[tuple[str, Any], dict[str, Any]] = {}
    for stock_code in sorted(selected_stocks):
        ordered_points = sorted(
            points_by_stock.get(stock_code, []),
            key=lambda point: point.base_date,
        )
        for sequence_index, point in enumerate(ordered_points):
            row = {
                "unique_id": stock_code,
                "ds": sequence_index,
                "base_date": point.base_date,
                "y": float(point.foreign_owned_quantity),
            }
            rows.append(row)
            lookup[(stock_code, point.base_date)] = row
    return pd.DataFrame(rows), lookup


def _neural_fold_predictions(
    sequence_frame: Any,
    sequence_lookup: dict[tuple[str, Any], dict[str, Any]],
    fold_samples: list[Any],
    neural_forecast_type: Any,
    model_factory: Any,
    model_alias: str,
    pd: Any,
) -> dict[str, list[int]]:
    fold_start_date = min(sample.sample_date for sample in fold_samples)
    train_frame = sequence_frame[sequence_frame["base_date"] < fold_start_date][
        ["unique_id", "ds", "y"]
    ]
    with (
        contextlib.redirect_stdout(io.StringIO()),
        contextlib.redirect_stderr(io.StringIO()),
    ):
        neural_forecast = neural_forecast_type(
            models=[model_factory(1)],
            freq=1,
        )
        neural_forecast.fit(train_frame)
    samples_by_date: dict[Any, list[Any]] = {}
    for sample in fold_samples:
        samples_by_date.setdefault(sample.sample_date, []).append(sample)
    actual: list[int] = []
    predicted: list[int] = []
    persistence: list[int] = []
    for sample_date in sorted(samples_by_date):
        history_frame = sequence_frame[sequence_frame["base_date"] < sample_date][
            ["unique_id", "ds", "y"]
        ]
        with (
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            prediction_frame = neural_forecast.predict(df=history_frame)
        prediction_lookup = {
            (str(row.unique_id), int(row.ds)): int(
                round(float(getattr(row, model_alias)))
            )
            for row in prediction_frame.itertuples(index=False)
        }
        for sample in samples_by_date[sample_date]:
            target_row = sequence_lookup[(sample.stock_code, sample.sample_date)]
            key = (sample.stock_code, int(target_row["ds"]))
            actual.append(sample.target_quantity)
            predicted.append(prediction_lookup[key])
            persistence.append(sample.previous_quantity)
    return {
        "actual": actual,
        "predicted": predicted,
        "persistence": persistence,
    }


def _nhits_factory(model_type: Any, max_steps: int) -> Any:
    def factory(horizon: int) -> Any:
        return model_type(
            h=horizon,
            input_size=20,
            max_steps=max_steps,
            batch_size=64,
            windows_batch_size=512,
            scaler_type="robust",
            random_seed=42,
            alias="NHITS",
            enable_checkpointing=False,
            enable_progress_bar=False,
            logger=False,
            accelerator="cpu",
        )

    return factory


def _patchtst_factory(model_type: Any, max_steps: int) -> Any:
    def factory(horizon: int) -> Any:
        return model_type(
            h=horizon,
            input_size=20,
            max_steps=max_steps,
            batch_size=64,
            windows_batch_size=512,
            scaler_type="robust",
            random_seed=42,
            alias="PatchTST",
            enable_checkpointing=False,
            enable_progress_bar=False,
            logger=False,
            accelerator="cpu",
        )

    return factory


def _training_report_summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "selected_model": report.get("selected_model"),
        "selected_blend_alpha": report.get("selected_blend_alpha"),
        "release_status": report.get("release_status"),
        "baseline_metrics": report.get("baseline_metrics"),
        "selected_model_metrics": report.get("selected_model_metrics"),
        "guarded_runtime_metrics": report.get("guarded_runtime_metrics"),
        "guarded_improvement_over_baseline": report.get(
            "guarded_improvement_over_baseline"
        ),
        "runtime_policy_counts": _runtime_policy_counts(report),
    }


def _runtime_policy_counts(report: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for policy in dict(report.get("runtime_by_stock", {})).values():
        counts[str(policy)] = counts.get(str(policy), 0) + 1
    return counts


def _load_training_report(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _improvement(
    baseline_metrics: dict[str, float],
    challenger_metrics: dict[str, float],
) -> dict[str, float]:
    return {
        key: (
            (baseline_metrics[key] - challenger_metrics[key])
            / baseline_metrics[key]
            if baseline_metrics[key] > 0
            else 0.0
        )
        for key in ("mae", "rmse", "mape")
    }


def _summary(report: dict[str, Any], report_path: Path) -> dict[str, Any]:
    full_universe = list(report["full_universe_walk_forward"])
    return {
        "best_full_universe_model": full_universe[0]["model"],
        "best_full_universe_metrics": full_universe[0]["metrics"],
        "published_sota_diagnostics": report["published_sota_diagnostics"],
        "report_path": str(report_path),
    }


if __name__ == "__main__":
    main()
