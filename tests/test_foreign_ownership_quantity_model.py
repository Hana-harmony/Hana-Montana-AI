import csv
import json
from datetime import date, timedelta
from pathlib import Path

from hannah_montana_ai.domain.schemas import (
    ForeignOwnershipHistoryPoint,
    ForeignOwnershipQuantityRetrainRequest,
    ForeignOwnershipQuantityTrainingPoint,
    ForeignOwnershipTimeseriesPredictionRequest,
)
from hannah_montana_ai.services.foreign_ownership import (
    ForeignOwnershipTimeseriesPredictionService,
)
from hannah_montana_ai.services.foreign_ownership_model_maintenance import (
    ForeignOwnershipModelMaintenancePaths,
    ForeignOwnershipModelMaintenanceService,
)
from hannah_montana_ai.training.foreign_ownership_quantity_benchmark import (
    benchmark_foreign_ownership_quantity_models,
)
from hannah_montana_ai.training.foreign_ownership_quantity_trainer import (
    train_foreign_ownership_quantity_model,
)

LIGHTWEIGHT_CANDIDATE_MODELS = ("ridge_delta_ratio",)


def test_foreign_owned_quantity_training_builds_walk_forward_artifact(tmp_path: Path) -> None:
    training_data_path = tmp_path / "foreign_ownership_quantity_history.csv"
    model_path = tmp_path / "foreign_ownership_quantity_ml.joblib"
    restricted_codes_path = tmp_path / "foreign_ownership_restricted_stock_codes.csv"
    _write_synthetic_foreign_ownership_quantity_history(training_data_path)
    _write_synthetic_restricted_stock_codes(restricted_codes_path)

    report = train_foreign_ownership_quantity_model(
        training_data_path,
        model_path,
        restricted_stock_codes_path=restricted_codes_path,
        minimum_promotable_stock_count=6,
        minimum_promotable_history_days=60,
        minimum_promotable_observations=300,
        candidate_model_names=LIGHTWEIGHT_CANDIDATE_MODELS,
    )

    assert model_path.exists()
    assert report.stock_count == 6
    assert report.sample_count >= 300
    assert len(report.walk_forward_folds) >= 3
    assert report.selected_model in {
        "ridge_delta_ratio",
        "hist_gradient_boosting_delta_ratio",
        "hist_gradient_boosting_delta_ratio_sensitive",
        "extra_trees_delta_ratio",
        "hurdle_hist_gradient_delta_ratio",
        "stock_routed_ml_ensemble",
    }
    assert set(report.model_by_stock) == set(report.runtime_by_stock)
    assert set(report.blend_alpha_by_stock) == set(report.runtime_by_stock)
    assert set(report.runtime_by_stock.values()).issubset(
        {
            "baseline",
            "stale_guarded_mean_delta_20",
            "median_multi_delta",
            "mean_delta_20",
            "micro_median_delta_3",
            "ml",
        }
    )
    assert report.selected_model_metrics["mae"] <= report.baseline_metrics["mae"] * 1.2
    assert report.residual_abs_p90_ratio > 0


def test_foreign_owned_quantity_service_uses_trained_ml_artifact(tmp_path: Path) -> None:
    training_data_path = tmp_path / "foreign_ownership_quantity_history.csv"
    model_path = tmp_path / "foreign_ownership_quantity_ml.joblib"
    restricted_codes_path = tmp_path / "foreign_ownership_restricted_stock_codes.csv"
    _write_synthetic_foreign_ownership_quantity_history(training_data_path)
    _write_synthetic_restricted_stock_codes(restricted_codes_path)
    train_foreign_ownership_quantity_model(
        training_data_path,
        model_path,
        restricted_stock_codes_path=restricted_codes_path,
        minimum_promotable_stock_count=6,
        minimum_promotable_history_days=60,
        minimum_promotable_observations=300,
        candidate_model_names=LIGHTWEIGHT_CANDIDATE_MODELS,
    )
    service = ForeignOwnershipTimeseriesPredictionService(model_path=model_path)
    history = [
        ForeignOwnershipHistoryPoint(
            base_date=date(2025, 1, 1) + timedelta(days=index),
            foreign_owned_quantity=4_000_000 + index * 1_000,
            foreign_ownership_rate=40.0,
            foreign_limit_quantity=10_000_000,
            foreign_limit_exhaustion_rate=40.0,
        )
        for index in range(80)
    ]

    response = service.predict(
        ForeignOwnershipTimeseriesPredictionRequest(
            stock_code="005930",
            side="BUY",
            quantity=9_999_999,
            foreign_owned_quantity=history[-1].foreign_owned_quantity,
            foreign_ownership_rate=40.0,
            foreign_limit_quantity=10_000_000,
            foreign_limit_exhaustion_rate=40.0,
            base_date=history[-1].base_date,
            observed_intraday_volume=9_999_999,
            history=history,
        )
    )

    assert response.min_foreign_owned_quantity <= response.predicted_foreign_owned_quantity
    assert response.predicted_foreign_owned_quantity <= response.max_foreign_owned_quantity
    assert (
        abs(response.predicted_foreign_owned_quantity - history[-1].foreign_owned_quantity)
        < 20_000
    )
    assert response.order_impact_rate == 0.0
    assert response.observed_intraday_volume == 0
    assert response.model_version == "hannah-foreign-owned-quantity-ml-v1"
    assert response.confidence_level in {
        "AI_FOREIGN_OWNED_QUANTITY_ML",
        "AI_FOREIGN_OWNED_QUANTITY_STOCK_GUARDED_BASELINE",
        "AI_FOREIGN_OWNED_QUANTITY_STOCK_GUARDED_HEURISTIC",
    }


def test_foreign_owned_quantity_training_guards_small_production_dataset(
    tmp_path: Path,
) -> None:
    training_data_path = tmp_path / "foreign_ownership_quantity_history.csv"
    model_path = tmp_path / "foreign_ownership_quantity_ml.joblib"
    _write_synthetic_foreign_ownership_quantity_history(training_data_path)

    report = train_foreign_ownership_quantity_model(
        training_data_path,
        model_path,
        candidate_model_names=LIGHTWEIGHT_CANDIDATE_MODELS,
    )

    assert report.release_status == "guarded"
    assert report.quality_gates["status"] == "fail"
    assert "restricted_universe_not_applied" in report.quality_gates["failures"]
    assert "insufficient_stock_count" in report.quality_gates["failures"]


def test_foreign_owned_quantity_benchmark_report_includes_policy_baselines(
    tmp_path: Path,
) -> None:
    training_data_path = tmp_path / "foreign_ownership_quantity_history.csv"
    model_path = tmp_path / "foreign_ownership_quantity_ml.joblib"
    report_path = tmp_path / "foreign_ownership_quantity_training_report.json"
    restricted_codes_path = tmp_path / "foreign_ownership_restricted_stock_codes.csv"
    _write_synthetic_foreign_ownership_quantity_history(training_data_path)
    _write_synthetic_restricted_stock_codes(restricted_codes_path)
    report = train_foreign_ownership_quantity_model(
        training_data_path,
        model_path,
        restricted_stock_codes_path=restricted_codes_path,
        minimum_promotable_stock_count=6,
        minimum_promotable_history_days=60,
        minimum_promotable_observations=300,
        candidate_model_names=LIGHTWEIGHT_CANDIDATE_MODELS,
    )
    report_path.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False),
        encoding="utf-8",
    )

    benchmark = benchmark_foreign_ownership_quantity_models(
        training_data_path=training_data_path,
        training_report_path=report_path,
        restricted_stock_codes_path=restricted_codes_path,
        include_neural_sota=False,
    )

    full_universe_models = {
        row["model"] for row in benchmark["full_universe_walk_forward"]
    }
    assert "baseline" in full_universe_models
    assert "stale_guarded_mean_delta_20" in full_universe_models
    assert benchmark["published_sota_diagnostics"][0]["status"] == "not_run"


def test_foreign_owned_quantity_retrain_promotes_and_replaces_artifacts(
    tmp_path: Path,
) -> None:
    source_training_data_path = tmp_path / "source_history.csv"
    _write_synthetic_foreign_ownership_quantity_history(source_training_data_path)
    with source_training_data_path.open(newline="", encoding="utf-8") as csv_file:
        history = [
            ForeignOwnershipQuantityTrainingPoint(
                stock_code=row["stock_code"],
                base_date=date.fromisoformat(row["base_date"]),
                foreign_owned_quantity=int(row["foreign_owned_quantity"]),
                foreign_limit_quantity=int(row["foreign_limit_quantity"]),
            )
            for row in csv.DictReader(csv_file)
        ]
    request = ForeignOwnershipQuantityRetrainRequest(
        history=history,
        restricted_stock_codes=[f"{5930 + stock_index:06d}" for stock_index in range(6)],
        minimum_promotable_stock_count=6,
        minimum_promotable_history_days=60,
        minimum_promotable_observations=300,
        max_model_training_samples=10_000,
        candidate_model_names=list(LIGHTWEIGHT_CANDIDATE_MODELS),
    )
    paths = ForeignOwnershipModelMaintenancePaths(
        training_data_path=tmp_path / "promoted_history.csv",
        restricted_codes_path=tmp_path / "restricted_codes.csv",
        model_path=tmp_path / "foreign_ownership_quantity_ml.joblib",
        report_path=tmp_path / "training_report.json",
        candidate_report_path=tmp_path / "candidate_report.json",
    )
    response = ForeignOwnershipModelMaintenanceService(paths).retrain(
        request,
        reload_model=True,
    )

    assert response.promoted is True
    assert response.model_reloaded is True
    assert response.release_status == "promoted"
    assert paths.training_data_path.exists()
    assert paths.restricted_codes_path.exists()
    assert paths.model_path.exists()
    assert paths.report_path.exists()
    assert not paths.candidate_report_path.exists()


def _write_synthetic_foreign_ownership_quantity_history(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=[
                "stock_code",
                "base_date",
                "foreign_owned_quantity",
                "foreign_limit_quantity",
            ],
        )
        writer.writeheader()
        start = date(2025, 1, 1)
        for stock_index in range(6):
            stock_code = f"{5930 + stock_index:06d}"
            base_quantity = 10_000_000 + stock_index * 300_000
            for day_index in range(90):
                weekly_wave = (day_index % 5) * 20
                writer.writerow(
                    {
                        "stock_code": stock_code,
                        "base_date": start + timedelta(days=day_index),
                        "foreign_owned_quantity": (
                            base_quantity
                            + day_index * (800 + stock_index * 25)
                            + weekly_wave
                        ),
                        "foreign_limit_quantity": base_quantity * 2,
                    }
                )


def _write_synthetic_restricted_stock_codes(path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["stock_code"])
        writer.writeheader()
        for stock_index in range(6):
            writer.writerow({"stock_code": f"{5930 + stock_index:06d}"})
