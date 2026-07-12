from __future__ import annotations

import csv
import sys
from collections import Counter
from collections.abc import Collection
from dataclasses import dataclass
from datetime import UTC, date, datetime
from math import exp, log
from pathlib import Path
from typing import Any

import joblib
from sklearn.ensemble import (
    ExtraTreesRegressor,
    HistGradientBoostingClassifier,
    HistGradientBoostingRegressor,
)
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from hannah_montana_ai.services.foreign_ownership_quantity_model import (
    MIN_HISTORY_OBSERVATIONS,
    MODEL_SCHEMA_VERSION,
    MODEL_VERSION,
    RUNTIME_POLICIES,
    RUNTIME_POLICY_BASELINE,
    RUNTIME_POLICY_MEDIAN_MULTI_DELTA,
    RUNTIME_POLICY_MICRO_MEDIAN_DELTA_3,
    RUNTIME_POLICY_ML,
    RUNTIME_POLICY_STALE_GUARDED_MEAN_DELTA_20,
    ConstantChangeProbabilityClassifier,
    ForeignOwnershipQuantityFeatureSample,
    ForeignOwnershipQuantityHurdleDeltaModel,
    ForeignOwnershipQuantityPoint,
    baseline_prediction,
    blended_model_prediction,
    build_training_samples,
    regression_metrics,
    residual_abs_p90_ratio,
    runtime_policy_quantity,
)

MIN_TRAINING_SAMPLES = 120
MIN_WALK_FORWARD_FOLDS = 3
MIN_PROMOTABLE_STOCK_COUNT = 1_000
MIN_PROMOTABLE_HISTORY_DAYS = 730
MIN_PROMOTABLE_OBSERVATIONS = 100_000
DEFAULT_MAX_MODEL_TRAINING_SAMPLES = 250_000
BLEND_ALPHA_CANDIDATES = (
    0.0005,
    0.001,
    0.002,
    0.003,
    0.005,
    0.01,
    0.02,
    0.03,
    0.05,
    0.1,
    0.15,
    0.2,
    0.25,
    0.35,
    0.4,
    0.5,
    0.6,
    0.75,
    0.9,
    1.0,
    1.1,
    1.25,
    1.5,
    1.75,
)
HURDLE_THRESHOLD_CANDIDATES = (0.05, 0.1, 0.2, 0.35, 0.5, 0.7, 0.85, 0.9, 0.95)
PREDICTION_MODE_DELTA_RATIO = "delta_ratio"
PREDICTION_MODE_DELTA_QUANTITY = "delta_quantity"
PREDICTION_MODE_TARGET_QUANTITY = "target_quantity"
PREDICTION_MODE_LOG_DELTA_RATIO = "log_delta_ratio"
PREDICTION_MODE_RESIDUAL_PREFIX = "residual:"


@dataclass(frozen=True)
class RegressionCandidate:
    estimator: Pipeline
    target_mode: str
    prediction_mode: str
    sample_weight_mode: str | None = None


@dataclass(frozen=True)
class HurdleCandidate:
    classifier: Pipeline
    regressor: Pipeline


type CandidateModel = RegressionCandidate | HurdleCandidate
type WalkForwardFold = tuple[
    list[ForeignOwnershipQuantityFeatureSample],
    list[ForeignOwnershipQuantityFeatureSample],
]


@dataclass(frozen=True)
class ForeignOwnershipQuantityModelTrainingReport:
    schema_version: str
    model_version: str
    trained_at: str
    model_path: str
    training_data_path: str
    observation_count: int
    stock_count: int
    sample_count: int
    train_date_min: str
    train_date_max: str
    selected_model: str
    selected_blend_alpha: float
    release_status: str
    baseline_metrics: dict[str, float]
    selected_model_metrics: dict[str, float]
    guarded_runtime_metrics: dict[str, float]
    improvement_over_baseline: dict[str, float]
    guarded_improvement_over_baseline: dict[str, float]
    candidate_metrics: list[dict[str, Any]]
    walk_forward_folds: list[dict[str, Any]]
    per_stock_validation: list[dict[str, Any]]
    runtime_by_stock: dict[str, str]
    model_by_stock: dict[str, str]
    blend_alpha_by_stock: dict[str, float]
    model_prediction_modes: dict[str, str]
    residual_abs_p90_ratio: float
    prediction_interval_abs_p90_by_stock: dict[str, int]
    prediction_interval_coverage_by_stock: dict[str, float]
    quality_gates: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "model_version": self.model_version,
            "trained_at": self.trained_at,
            "model_path": self.model_path,
            "training_data_path": self.training_data_path,
            "observation_count": self.observation_count,
            "stock_count": self.stock_count,
            "sample_count": self.sample_count,
            "train_date_min": self.train_date_min,
            "train_date_max": self.train_date_max,
            "selected_model": self.selected_model,
            "selected_blend_alpha": self.selected_blend_alpha,
            "release_status": self.release_status,
            "baseline_metrics": self.baseline_metrics,
            "selected_model_metrics": self.selected_model_metrics,
            "guarded_runtime_metrics": self.guarded_runtime_metrics,
            "improvement_over_baseline": self.improvement_over_baseline,
            "guarded_improvement_over_baseline": self.guarded_improvement_over_baseline,
            "candidate_metrics": self.candidate_metrics,
            "walk_forward_folds": self.walk_forward_folds,
            "per_stock_validation": self.per_stock_validation,
            "runtime_by_stock": self.runtime_by_stock,
            "model_by_stock": self.model_by_stock,
            "blend_alpha_by_stock": self.blend_alpha_by_stock,
            "model_prediction_modes": self.model_prediction_modes,
            "residual_abs_p90_ratio": self.residual_abs_p90_ratio,
            "prediction_interval_abs_p90_by_stock": self.prediction_interval_abs_p90_by_stock,
            "prediction_interval_coverage_by_stock": self.prediction_interval_coverage_by_stock,
            "quality_gates": self.quality_gates,
        }


def train_foreign_ownership_quantity_model(
    training_data_path: Path,
    model_path: Path,
    *,
    restricted_stock_codes_path: Path | None = None,
    minimum_promotable_stock_count: int = MIN_PROMOTABLE_STOCK_COUNT,
    minimum_promotable_history_days: int = MIN_PROMOTABLE_HISTORY_DAYS,
    minimum_promotable_observations: int = MIN_PROMOTABLE_OBSERVATIONS,
    max_model_training_samples: int = DEFAULT_MAX_MODEL_TRAINING_SAMPLES,
    candidate_model_names: Collection[str] | None = None,
) -> ForeignOwnershipQuantityModelTrainingReport:
    observations = load_foreign_ownership_quantity_points(training_data_path)
    restricted_stock_codes = _load_restricted_stock_codes(restricted_stock_codes_path)
    restricted_universe_applied = restricted_stock_codes is not None
    if restricted_stock_codes is not None:
        observations = [
            point for point in observations if point.stock_code in restricted_stock_codes
        ]
    samples = build_training_samples(observations)
    if len(samples) < MIN_TRAINING_SAMPLES:
        raise ValueError(
            "Foreign ownership quantity ML training requires at least "
            f"{MIN_TRAINING_SAMPLES} feature samples"
        )

    folds = _walk_forward_folds(samples)
    candidate_reports: list[dict[str, Any]] = []
    fold_reports: list[dict[str, Any]] = []
    candidate_scores: dict[tuple[str, float], list[dict[str, float]]] = {}
    baseline_fold_metrics: list[dict[str, float]] = []
    fold_predictions_by_model: dict[tuple[str, int], list[float]] = {}
    candidate_models = _candidate_models()
    if candidate_model_names is not None:
        requested_model_names = set(candidate_model_names)
        unknown_model_names = sorted(requested_model_names - set(candidate_models))
        if unknown_model_names:
            raise ValueError(
                "Unknown foreign ownership quantity candidate models: "
                + ", ".join(unknown_model_names)
            )
        candidate_models = {
            model_name: model
            for model_name, model in candidate_models.items()
            if model_name in requested_model_names
        }
        if not candidate_models:
            raise ValueError("At least one candidate model is required")
    model_prediction_modes = {
        model_name: _candidate_prediction_mode(model)
        for model_name, model in candidate_models.items()
    }

    _log_training(
        "loaded observations="
        f"{len(observations)} samples={len(samples)} stocks="
        f"{len({point.stock_code for point in observations})}"
    )
    _log_training(f"walk_forward_folds={len(folds)}")

    for fold_index, (train_samples, test_samples) in enumerate(folds, start=1):
        _log_training(
            f"fold={fold_index} train_samples={len(train_samples)} test_samples={len(test_samples)}"
        )
        actual = [sample.target_quantity for sample in test_samples]
        baseline_predicted = [baseline_prediction(sample) for sample in test_samples]
        baseline_metrics = regression_metrics(actual, baseline_predicted)
        baseline_fold_metrics.append(baseline_metrics)
        fold_candidate_metrics: list[dict[str, Any]] = []

        for model_name, model in candidate_models.items():
            _log_training(f"fold={fold_index} fitting model={model_name}")
            fitted_model = _fit_model(
                model,
                train_samples,
                max_model_training_samples=max_model_training_samples,
            )
            raw_predictions = [
                float(value)
                for value in fitted_model.predict([sample.features for sample in test_samples])
            ]
            fold_predictions_by_model[(model_name, fold_index)] = raw_predictions
            prediction_mode = model_prediction_modes[model_name]
            for blend_alpha in BLEND_ALPHA_CANDIDATES:
                predicted = [
                    _quantity_prediction(sample, raw_prediction, blend_alpha, prediction_mode)
                    for sample, raw_prediction in zip(
                        test_samples,
                        raw_predictions,
                        strict=True,
                    )
                ]
                metrics = regression_metrics(actual, predicted)
                key = (model_name, blend_alpha)
                candidate_scores.setdefault(key, []).append(metrics)
                fold_candidate_metrics.append(
                    {
                        "model": model_name,
                        "blend_alpha": blend_alpha,
                        "metrics": metrics,
                    }
                )

        fold_reports.append(
            {
                "fold": fold_index,
                "train_sample_count": len(train_samples),
                "test_sample_count": len(test_samples),
                "test_date_min": str(test_samples[0].sample_date),
                "test_date_max": str(test_samples[-1].sample_date),
                "baseline_metrics": baseline_metrics,
                "candidate_metrics": fold_candidate_metrics,
            }
        )

    baseline_metrics = _baseline_metrics_from_folds(folds)
    for (model_name, blend_alpha), metric_list in candidate_scores.items():
        candidate_reports.append(
            {
                "model": model_name,
                "blend_alpha": blend_alpha,
                "metrics": _mean_metrics(metric_list),
            }
        )
    selected_candidate = min(
        candidate_reports,
        key=lambda report: (
            report["metrics"]["mae"],
            report["metrics"]["rmse"],
        ),
    )
    fallback_model_name = str(selected_candidate["model"])
    fallback_blend_alpha = float(selected_candidate["blend_alpha"])
    selected_model_name = "stock_routed_ml_ensemble"
    selected_blend_alpha = fallback_blend_alpha
    per_stock_validation = _per_stock_validation(
        folds,
        fold_predictions_by_model,
        model_prediction_modes,
    )
    runtime_by_stock = {
        str(report["stock_code"]): str(report["recommended_runtime"])
        for report in per_stock_validation
    }
    model_by_stock = {
        str(report["stock_code"]): str(report["best_ml_model"]) for report in per_stock_validation
    }
    blend_alpha_by_stock = {
        str(report["stock_code"]): float(report["best_ml_blend_alpha"])
        for report in per_stock_validation
    }
    prediction_interval_abs_p90_by_stock = {
        str(report["stock_code"]): int(report["prediction_interval_abs_p90_quantity"])
        for report in per_stock_validation
    }
    prediction_interval_coverage_by_stock = {
        str(report["stock_code"]): float(report["prediction_interval_coverage"])
        for report in per_stock_validation
    }
    selected_metrics = _stock_routed_model_metrics(
        folds,
        fold_predictions_by_model,
        model_by_stock,
        blend_alpha_by_stock,
        fallback_model_name,
        fallback_blend_alpha,
        model_prediction_modes,
    )
    _log_training(
        "selected_model="
        f"{selected_model_name} fallback={fallback_model_name} "
        f"fallback_blend_alpha={fallback_blend_alpha}"
    )
    guarded_metrics = _guarded_runtime_metrics(
        folds,
        runtime_by_stock,
        model_by_stock,
        blend_alpha_by_stock,
        fold_predictions_by_model,
        fallback_model_name,
        fallback_blend_alpha,
        model_prediction_modes,
    )
    dates = [sample.sample_date for sample in samples]
    stock_counts = Counter(point.stock_code for point in observations)
    quality_gates = _quality_gates(
        observation_count=len(observations),
        stock_count=len(stock_counts),
        history_days=max(1, (max(dates) - min(dates)).days),
        fold_count=len(folds),
        baseline_metrics=baseline_metrics,
        guarded_metrics=guarded_metrics,
        minimum_promotable_stock_count=minimum_promotable_stock_count,
        minimum_promotable_history_days=minimum_promotable_history_days,
        minimum_promotable_observations=minimum_promotable_observations,
        restricted_universe_applied=restricted_universe_applied,
    )
    release_status = "promoted" if quality_gates["status"] == "pass" else "guarded"
    _log_training(f"quality_gate_status={quality_gates['status']} release={release_status}")
    final_model_names = {fallback_model_name, *model_by_stock.values()}
    final_models_by_name = {}
    for model_name in sorted(final_model_names):
        _log_training(f"fitting final_model={model_name}")
        final_models_by_name[model_name] = _fit_model(
            candidate_models[model_name],
            samples,
            max_model_training_samples=max_model_training_samples,
        )
    final_model = final_models_by_name[fallback_model_name]
    residual_ratio = _estimate_stock_routed_residual_ratio(
        final_models_by_name,
        _fit_sample_window(samples, max_model_training_samples),
        model_by_stock,
        blend_alpha_by_stock,
        fallback_model_name,
        fallback_blend_alpha,
        model_prediction_modes,
    )
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "schema_version": MODEL_SCHEMA_VERSION,
            "model_version": MODEL_VERSION,
            "trained_at": datetime.now(UTC).isoformat(),
            "model": final_model,
            "models_by_name": final_models_by_name,
            "selected_model": selected_model_name,
            "fallback_model": fallback_model_name,
            "blend_alpha": selected_blend_alpha,
            "residual_abs_p90_ratio": residual_ratio,
            "prediction_interval_abs_p90_by_stock": prediction_interval_abs_p90_by_stock,
            "prediction_interval_coverage_by_stock": prediction_interval_coverage_by_stock,
            "prediction_interval_target_coverage": 0.9,
            "minimum_history_observations": MIN_HISTORY_OBSERVATIONS,
            "release_status": release_status,
            "runtime_by_stock": runtime_by_stock,
            "model_by_stock": model_by_stock,
            "blend_alpha_by_stock": blend_alpha_by_stock,
            "model_prediction_modes": model_prediction_modes,
            "training_sample_count": len(samples),
            "max_model_training_samples": max_model_training_samples,
            "restricted_universe_applied": restricted_universe_applied,
            "restricted_stock_codes_path": (
                str(restricted_stock_codes_path) if restricted_stock_codes_path else None
            ),
        },
        model_path,
    )

    improvement = _improvement_over_baseline(baseline_metrics, selected_metrics)
    guarded_improvement = _improvement_over_baseline(baseline_metrics, guarded_metrics)
    return ForeignOwnershipQuantityModelTrainingReport(
        schema_version=MODEL_SCHEMA_VERSION,
        model_version=MODEL_VERSION,
        trained_at=datetime.now(UTC).isoformat(),
        model_path=str(model_path),
        training_data_path=str(training_data_path),
        observation_count=len(observations),
        stock_count=len(stock_counts),
        sample_count=len(samples),
        train_date_min=str(min(dates)),
        train_date_max=str(max(dates)),
        selected_model=selected_model_name,
        selected_blend_alpha=selected_blend_alpha,
        release_status=release_status,
        baseline_metrics=baseline_metrics,
        selected_model_metrics=selected_metrics,
        guarded_runtime_metrics=guarded_metrics,
        improvement_over_baseline=improvement,
        guarded_improvement_over_baseline=guarded_improvement,
        candidate_metrics=sorted(
            candidate_reports,
            key=lambda report: (
                report["metrics"]["mae"],
                report["metrics"]["rmse"],
            ),
        ),
        walk_forward_folds=fold_reports,
        per_stock_validation=per_stock_validation,
        runtime_by_stock=runtime_by_stock,
        model_by_stock=model_by_stock,
        blend_alpha_by_stock=blend_alpha_by_stock,
        model_prediction_modes=model_prediction_modes,
        residual_abs_p90_ratio=residual_ratio,
        prediction_interval_abs_p90_by_stock=prediction_interval_abs_p90_by_stock,
        prediction_interval_coverage_by_stock=prediction_interval_coverage_by_stock,
        quality_gates=quality_gates | {"release_status": release_status},
    )


def load_foreign_ownership_quantity_points(path: Path) -> list[ForeignOwnershipQuantityPoint]:
    rows: list[ForeignOwnershipQuantityPoint] = []
    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            stock_code = _required(row, "stock_code").zfill(6)
            base_date = date.fromisoformat(_required(row, "base_date"))
            quantity = int(_required(row, "foreign_owned_quantity"))
            limit_quantity = int(_required(row, "foreign_limit_quantity"))
            rows.append(
                ForeignOwnershipQuantityPoint(
                    stock_code=stock_code,
                    base_date=base_date,
                    foreign_owned_quantity=quantity,
                    foreign_limit_quantity=limit_quantity,
                )
            )
    return sorted(rows, key=lambda point: (point.stock_code, point.base_date))


def _load_restricted_stock_codes(path: Path | None) -> set[str] | None:
    if path is None:
        return None
    if not path.exists():
        raise ValueError(f"Restricted foreign ownership stock code file not found: {path}")
    codes: set[str] = set()
    with path.open(newline="", encoding="utf-8") as csv_file:
        sample = csv_file.read(2048)
        csv_file.seek(0)
        if "stock_code" in sample.splitlines()[0]:
            reader = csv.DictReader(csv_file)
            for row in reader:
                stock_code = _required(row, "stock_code").zfill(6)
                if stock_code.isdigit():
                    codes.add(stock_code)
        else:
            for line in csv_file:
                stock_code = line.split(",", 1)[0].strip().zfill(6)
                if stock_code.isdigit():
                    codes.add(stock_code)
    if not codes:
        raise ValueError(f"Restricted foreign ownership stock code file is empty: {path}")
    return codes


def _candidate_models() -> dict[str, CandidateModel]:
    return {
        "ridge_delta_ratio": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=True)),
                    ("scale", StandardScaler(with_mean=False)),
                    ("model", Ridge(alpha=2.0)),
                ]
            ),
            target_mode=PREDICTION_MODE_DELTA_RATIO,
            prediction_mode=PREDICTION_MODE_DELTA_RATIO,
        ),
        "hist_gradient_boosting_delta_ratio": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        HistGradientBoostingRegressor(
                            learning_rate=0.04,
                            max_iter=240,
                            max_leaf_nodes=15,
                            l2_regularization=1.0,
                            min_samples_leaf=20,
                            random_state=42,
                        ),
                    ),
                ]
            ),
            target_mode=PREDICTION_MODE_DELTA_RATIO,
            prediction_mode=PREDICTION_MODE_DELTA_RATIO,
        ),
        "hist_gradient_boosting_delta_ratio_sensitive": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        HistGradientBoostingRegressor(
                            learning_rate=0.03,
                            max_iter=360,
                            max_leaf_nodes=31,
                            l2_regularization=0.2,
                            min_samples_leaf=8,
                            random_state=43,
                        ),
                    ),
                ]
            ),
            target_mode=PREDICTION_MODE_DELTA_RATIO,
            prediction_mode=PREDICTION_MODE_DELTA_RATIO,
        ),
        "extra_trees_delta_ratio": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        ExtraTreesRegressor(
                            n_estimators=240,
                            max_depth=10,
                            min_samples_leaf=4,
                            max_features=0.7,
                            random_state=44,
                            n_jobs=-1,
                        ),
                    ),
                ]
            ),
            target_mode=PREDICTION_MODE_DELTA_RATIO,
            prediction_mode=PREDICTION_MODE_DELTA_RATIO,
        ),
        "ridge_log_delta_ratio": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=True)),
                    ("scale", StandardScaler(with_mean=False)),
                    ("model", Ridge(alpha=3.0)),
                ]
            ),
            target_mode=PREDICTION_MODE_LOG_DELTA_RATIO,
            prediction_mode=PREDICTION_MODE_LOG_DELTA_RATIO,
        ),
        "hist_gradient_boosting_log_delta_ratio": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        HistGradientBoostingRegressor(
                            loss="absolute_error",
                            learning_rate=0.025,
                            max_iter=320,
                            max_leaf_nodes=15,
                            l2_regularization=1.0,
                            min_samples_leaf=20,
                            random_state=94,
                        ),
                    ),
                ]
            ),
            target_mode=PREDICTION_MODE_LOG_DELTA_RATIO,
            prediction_mode=PREDICTION_MODE_LOG_DELTA_RATIO,
            sample_weight_mode="inverse_target",
        ),
        "delta_quantity_ridge": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=True)),
                    ("scale", StandardScaler(with_mean=False)),
                    ("model", Ridge(alpha=30.0)),
                ]
            ),
            target_mode=PREDICTION_MODE_DELTA_QUANTITY,
            prediction_mode=PREDICTION_MODE_DELTA_QUANTITY,
        ),
        "delta_quantity_hist_gradient": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        HistGradientBoostingRegressor(
                            learning_rate=0.03,
                            max_iter=260,
                            max_leaf_nodes=31,
                            l2_regularization=0.4,
                            min_samples_leaf=10,
                            random_state=51,
                        ),
                    ),
                ]
            ),
            target_mode=PREDICTION_MODE_DELTA_QUANTITY,
            prediction_mode=PREDICTION_MODE_DELTA_QUANTITY,
        ),
        "delta_quantity_hist_absolute_mape_weighted": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        HistGradientBoostingRegressor(
                            loss="absolute_error",
                            learning_rate=0.02,
                            max_iter=300,
                            max_leaf_nodes=15,
                            l2_regularization=1.0,
                            min_samples_leaf=20,
                            random_state=91,
                        ),
                    ),
                ]
            ),
            target_mode=PREDICTION_MODE_DELTA_QUANTITY,
            prediction_mode=PREDICTION_MODE_DELTA_QUANTITY,
            sample_weight_mode="inverse_target",
        ),
        "delta_quantity_extra_trees": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        ExtraTreesRegressor(
                            n_estimators=260,
                            max_depth=12,
                            min_samples_leaf=4,
                            max_features=0.75,
                            random_state=52,
                            n_jobs=-1,
                        ),
                    ),
                ]
            ),
            target_mode=PREDICTION_MODE_DELTA_QUANTITY,
            prediction_mode=PREDICTION_MODE_DELTA_QUANTITY,
        ),
        "target_quantity_extra_trees": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        ExtraTreesRegressor(
                            n_estimators=260,
                            max_depth=12,
                            min_samples_leaf=4,
                            max_features=0.75,
                            random_state=53,
                            n_jobs=-1,
                        ),
                    ),
                ]
            ),
            target_mode=PREDICTION_MODE_TARGET_QUANTITY,
            prediction_mode=PREDICTION_MODE_TARGET_QUANTITY,
        ),
        "residual_stale_guarded_extra_trees": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        ExtraTreesRegressor(
                            n_estimators=260,
                            max_depth=12,
                            min_samples_leaf=4,
                            max_features=0.75,
                            random_state=61,
                            n_jobs=-1,
                        ),
                    ),
                ]
            ),
            target_mode=(
                PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_STALE_GUARDED_MEAN_DELTA_20
            ),
            prediction_mode=(
                PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_STALE_GUARDED_MEAN_DELTA_20
            ),
        ),
        "residual_stale_guarded_hist_gradient": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        HistGradientBoostingRegressor(
                            learning_rate=0.03,
                            max_iter=260,
                            max_leaf_nodes=31,
                            l2_regularization=0.4,
                            min_samples_leaf=10,
                            random_state=62,
                        ),
                    ),
                ]
            ),
            target_mode=(
                PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_STALE_GUARDED_MEAN_DELTA_20
            ),
            prediction_mode=(
                PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_STALE_GUARDED_MEAN_DELTA_20
            ),
        ),
        "residual_stale_guarded_hist_gradient_deep": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        HistGradientBoostingRegressor(
                            learning_rate=0.02,
                            max_iter=420,
                            max_leaf_nodes=63,
                            l2_regularization=0.2,
                            min_samples_leaf=8,
                            random_state=73,
                        ),
                    ),
                ]
            ),
            target_mode=(
                PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_STALE_GUARDED_MEAN_DELTA_20
            ),
            prediction_mode=(
                PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_STALE_GUARDED_MEAN_DELTA_20
            ),
        ),
        "residual_stale_guarded_hist_gradient_smooth": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        HistGradientBoostingRegressor(
                            learning_rate=0.02,
                            max_iter=300,
                            max_leaf_nodes=15,
                            l2_regularization=1.5,
                            min_samples_leaf=25,
                            random_state=74,
                        ),
                    ),
                ]
            ),
            target_mode=(
                PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_STALE_GUARDED_MEAN_DELTA_20
            ),
            prediction_mode=(
                PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_STALE_GUARDED_MEAN_DELTA_20
            ),
        ),
        "residual_stale_guarded_hist_absolute_deep": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        HistGradientBoostingRegressor(
                            loss="absolute_error",
                            learning_rate=0.03,
                            max_iter=360,
                            max_leaf_nodes=31,
                            l2_regularization=0.2,
                            min_samples_leaf=8,
                            random_state=81,
                        ),
                    ),
                ]
            ),
            target_mode=(
                PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_STALE_GUARDED_MEAN_DELTA_20
            ),
            prediction_mode=(
                PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_STALE_GUARDED_MEAN_DELTA_20
            ),
        ),
        "residual_stale_guarded_hist_absolute_smooth": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        HistGradientBoostingRegressor(
                            loss="absolute_error",
                            learning_rate=0.02,
                            max_iter=300,
                            max_leaf_nodes=15,
                            l2_regularization=1.5,
                            min_samples_leaf=25,
                            random_state=82,
                        ),
                    ),
                ]
            ),
            target_mode=(
                PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_STALE_GUARDED_MEAN_DELTA_20
            ),
            prediction_mode=(
                PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_STALE_GUARDED_MEAN_DELTA_20
            ),
        ),
        "residual_stale_guarded_hist_absolute_mape_weighted": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        HistGradientBoostingRegressor(
                            loss="absolute_error",
                            learning_rate=0.02,
                            max_iter=320,
                            max_leaf_nodes=15,
                            l2_regularization=1.2,
                            min_samples_leaf=20,
                            random_state=92,
                        ),
                    ),
                ]
            ),
            target_mode=(
                PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_STALE_GUARDED_MEAN_DELTA_20
            ),
            prediction_mode=(
                PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_STALE_GUARDED_MEAN_DELTA_20
            ),
            sample_weight_mode="inverse_target",
        ),
        "residual_stale_guarded_extra_trees_deep": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        ExtraTreesRegressor(
                            n_estimators=360,
                            max_depth=18,
                            min_samples_leaf=2,
                            max_features=0.9,
                            random_state=71,
                            n_jobs=-1,
                        ),
                    ),
                ]
            ),
            target_mode=(
                PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_STALE_GUARDED_MEAN_DELTA_20
            ),
            prediction_mode=(
                PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_STALE_GUARDED_MEAN_DELTA_20
            ),
        ),
        "residual_median_extra_trees": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        ExtraTreesRegressor(
                            n_estimators=260,
                            max_depth=12,
                            min_samples_leaf=4,
                            max_features=0.75,
                            random_state=63,
                            n_jobs=-1,
                        ),
                    ),
                ]
            ),
            target_mode=PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_MEDIAN_MULTI_DELTA,
            prediction_mode=(PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_MEDIAN_MULTI_DELTA),
        ),
        "residual_median_extra_trees_deep": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        ExtraTreesRegressor(
                            n_estimators=360,
                            max_depth=18,
                            min_samples_leaf=2,
                            max_features=0.9,
                            random_state=75,
                            n_jobs=-1,
                        ),
                    ),
                ]
            ),
            target_mode=PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_MEDIAN_MULTI_DELTA,
            prediction_mode=(PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_MEDIAN_MULTI_DELTA),
        ),
        "residual_median_hist_gradient_deep": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        HistGradientBoostingRegressor(
                            learning_rate=0.02,
                            max_iter=420,
                            max_leaf_nodes=63,
                            l2_regularization=0.2,
                            min_samples_leaf=8,
                            random_state=76,
                        ),
                    ),
                ]
            ),
            target_mode=PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_MEDIAN_MULTI_DELTA,
            prediction_mode=(PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_MEDIAN_MULTI_DELTA),
        ),
        "residual_median_hist_absolute_deep": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        HistGradientBoostingRegressor(
                            loss="absolute_error",
                            learning_rate=0.03,
                            max_iter=360,
                            max_leaf_nodes=31,
                            l2_regularization=0.2,
                            min_samples_leaf=8,
                            random_state=83,
                        ),
                    ),
                ]
            ),
            target_mode=PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_MEDIAN_MULTI_DELTA,
            prediction_mode=(PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_MEDIAN_MULTI_DELTA),
        ),
        "residual_median_hist_absolute_smooth": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        HistGradientBoostingRegressor(
                            loss="absolute_error",
                            learning_rate=0.02,
                            max_iter=300,
                            max_leaf_nodes=15,
                            l2_regularization=1.5,
                            min_samples_leaf=25,
                            random_state=84,
                        ),
                    ),
                ]
            ),
            target_mode=PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_MEDIAN_MULTI_DELTA,
            prediction_mode=(PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_MEDIAN_MULTI_DELTA),
        ),
        "residual_median_hist_absolute_mape_weighted": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        HistGradientBoostingRegressor(
                            loss="absolute_error",
                            learning_rate=0.02,
                            max_iter=320,
                            max_leaf_nodes=15,
                            l2_regularization=1.2,
                            min_samples_leaf=20,
                            random_state=93,
                        ),
                    ),
                ]
            ),
            target_mode=PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_MEDIAN_MULTI_DELTA,
            prediction_mode=(PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_MEDIAN_MULTI_DELTA),
            sample_weight_mode="inverse_target",
        ),
        "residual_median_hist_gradient": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        HistGradientBoostingRegressor(
                            learning_rate=0.03,
                            max_iter=260,
                            max_leaf_nodes=31,
                            l2_regularization=0.4,
                            min_samples_leaf=10,
                            random_state=64,
                        ),
                    ),
                ]
            ),
            target_mode=PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_MEDIAN_MULTI_DELTA,
            prediction_mode=(PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_MEDIAN_MULTI_DELTA),
        ),
        "residual_micro_hist_absolute_deep": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        HistGradientBoostingRegressor(
                            loss="absolute_error",
                            learning_rate=0.03,
                            max_iter=360,
                            max_leaf_nodes=31,
                            l2_regularization=0.2,
                            min_samples_leaf=8,
                            random_state=95,
                        ),
                    ),
                ]
            ),
            target_mode=PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_MICRO_MEDIAN_DELTA_3,
            prediction_mode=PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_MICRO_MEDIAN_DELTA_3,
        ),
        "residual_micro_hist_absolute_smooth": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        HistGradientBoostingRegressor(
                            loss="absolute_error",
                            learning_rate=0.02,
                            max_iter=300,
                            max_leaf_nodes=15,
                            l2_regularization=1.5,
                            min_samples_leaf=25,
                            random_state=96,
                        ),
                    ),
                ]
            ),
            target_mode=PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_MICRO_MEDIAN_DELTA_3,
            prediction_mode=PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_MICRO_MEDIAN_DELTA_3,
        ),
        "residual_micro_hist_absolute_mape_weighted": RegressionCandidate(
            estimator=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        HistGradientBoostingRegressor(
                            loss="absolute_error",
                            learning_rate=0.02,
                            max_iter=320,
                            max_leaf_nodes=15,
                            l2_regularization=1.2,
                            min_samples_leaf=20,
                            random_state=97,
                        ),
                    ),
                ]
            ),
            target_mode=PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_MICRO_MEDIAN_DELTA_3,
            prediction_mode=PREDICTION_MODE_RESIDUAL_PREFIX + RUNTIME_POLICY_MICRO_MEDIAN_DELTA_3,
            sample_weight_mode="inverse_target",
        ),
        "hurdle_hist_gradient_delta_ratio": HurdleCandidate(
            classifier=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        HistGradientBoostingClassifier(
                            learning_rate=0.04,
                            max_iter=160,
                            max_leaf_nodes=15,
                            l2_regularization=1.0,
                            min_samples_leaf=20,
                            random_state=42,
                        ),
                    ),
                ]
            ),
            regressor=Pipeline(
                [
                    ("features", DictVectorizer(sparse=False)),
                    (
                        "model",
                        HistGradientBoostingRegressor(
                            learning_rate=0.04,
                            max_iter=180,
                            max_leaf_nodes=15,
                            l2_regularization=1.0,
                            min_samples_leaf=6,
                            random_state=42,
                        ),
                    ),
                ]
            ),
        ),
    }


def _fit_model(
    model: CandidateModel,
    samples: list[ForeignOwnershipQuantityFeatureSample],
    *,
    max_model_training_samples: int,
) -> Pipeline | ForeignOwnershipQuantityHurdleDeltaModel:
    fit_samples = _fit_sample_window(samples, max_model_training_samples)
    if isinstance(model, HurdleCandidate):
        return _fit_hurdle_model(model, fit_samples)
    features = [sample.features for sample in fit_samples]
    targets = _training_targets(fit_samples, model.target_mode)
    sample_weights = _training_sample_weights(fit_samples, model.sample_weight_mode)
    if sample_weights is None:
        model.estimator.fit(features, targets)
    else:
        model.estimator.fit(features, targets, model__sample_weight=sample_weights)
    return model.estimator


def _training_targets(
    samples: list[ForeignOwnershipQuantityFeatureSample],
    target_mode: str,
) -> list[float]:
    if target_mode.startswith(PREDICTION_MODE_RESIDUAL_PREFIX):
        base_policy = target_mode.removeprefix(PREDICTION_MODE_RESIDUAL_PREFIX)
        return [
            float(
                sample.target_quantity
                - runtime_policy_quantity(
                    sample.previous_quantity,
                    sample.features,
                    base_policy,
                )
            )
            for sample in samples
        ]
    if target_mode == PREDICTION_MODE_DELTA_QUANTITY:
        return [float(sample.target_quantity - sample.previous_quantity) for sample in samples]
    if target_mode == PREDICTION_MODE_TARGET_QUANTITY:
        return [float(sample.target_quantity) for sample in samples]
    if target_mode == PREDICTION_MODE_LOG_DELTA_RATIO:
        return [
            log(max(1.0, float(sample.target_quantity)) / max(1.0, sample.previous_quantity))
            for sample in samples
        ]
    return [sample.target_delta_ratio for sample in samples]


def _training_sample_weights(
    samples: list[ForeignOwnershipQuantityFeatureSample],
    sample_weight_mode: str | None,
) -> list[float] | None:
    if sample_weight_mode is None:
        return None
    if sample_weight_mode != "inverse_target":
        raise ValueError(f"Unsupported sample weight mode: {sample_weight_mode}")

    # MAPE는 작은 수량 종목의 상대오차가 크게 작용하므로 역수 가중치를 둔다.
    raw_weights = [1.0 / max(1.0, float(sample.target_quantity)) for sample in samples]
    mean_weight = sum(raw_weights) / max(1, len(raw_weights))
    return [min(20.0, max(0.05, weight / mean_weight)) for weight in raw_weights]


def _candidate_prediction_mode(model: CandidateModel) -> str:
    if isinstance(model, HurdleCandidate):
        return PREDICTION_MODE_DELTA_RATIO
    return model.prediction_mode


def _fit_sample_window(
    samples: list[ForeignOwnershipQuantityFeatureSample],
    max_model_training_samples: int,
) -> list[ForeignOwnershipQuantityFeatureSample]:
    if max_model_training_samples <= 0 or len(samples) <= max_model_training_samples:
        return samples
    step = len(samples) / max_model_training_samples
    return [samples[int(index * step)] for index in range(max_model_training_samples)]


def _fit_hurdle_model(
    candidate: HurdleCandidate,
    samples: list[ForeignOwnershipQuantityFeatureSample],
) -> ForeignOwnershipQuantityHurdleDeltaModel:
    train_samples, validation_samples = _inner_validation_split(samples)
    classifier_features = [sample.features for sample in train_samples]
    classifier_targets = [_changed_target(sample) for sample in train_samples]
    if len(set(classifier_targets)) < 2:
        classifier = ConstantChangeProbabilityClassifier(float(classifier_targets[0]))
    else:
        candidate.classifier.fit(classifier_features, classifier_targets)
        classifier = candidate.classifier

    changed_train_samples = [sample for sample in train_samples if _changed_target(sample) == 1]
    regressor_samples = changed_train_samples or train_samples
    candidate.regressor.fit(
        [sample.features for sample in regressor_samples],
        [sample.target_delta_ratio for sample in regressor_samples],
    )

    best_threshold = _select_hurdle_threshold(
        classifier,
        candidate.regressor,
        validation_samples,
    )
    return ForeignOwnershipQuantityHurdleDeltaModel(
        change_classifier=classifier,
        change_regressor=candidate.regressor,
        probability_threshold=best_threshold,
    )


def _inner_validation_split(
    samples: list[ForeignOwnershipQuantityFeatureSample],
) -> WalkForwardFold:
    unique_dates = sorted({sample.sample_date for sample in samples})
    validation_date_count = max(10, len(unique_dates) // 5)
    validation_dates = set(unique_dates[-validation_date_count:])
    train_samples = [sample for sample in samples if sample.sample_date not in validation_dates]
    validation_samples = [sample for sample in samples if sample.sample_date in validation_dates]
    if not train_samples or not validation_samples:
        split_index = max(1, int(len(samples) * 0.8))
        return samples[:split_index], samples[split_index:]
    return train_samples, validation_samples


def _select_hurdle_threshold(
    classifier: Pipeline | ConstantChangeProbabilityClassifier,
    regressor: Pipeline,
    validation_samples: list[ForeignOwnershipQuantityFeatureSample],
) -> float:
    if not validation_samples:
        return 0.5
    best_threshold = HURDLE_THRESHOLD_CANDIDATES[0]
    best_mae = float("inf")
    actual = [sample.target_quantity for sample in validation_samples]
    for threshold in HURDLE_THRESHOLD_CANDIDATES:
        hurdle_model = ForeignOwnershipQuantityHurdleDeltaModel(
            change_classifier=classifier,
            change_regressor=regressor,
            probability_threshold=threshold,
        )
        predicted_delta_ratios = hurdle_model.predict(
            [sample.features for sample in validation_samples]
        )
        predicted = [
            blended_model_prediction(sample, delta_ratio, 1.0)
            for sample, delta_ratio in zip(
                validation_samples,
                predicted_delta_ratios,
                strict=True,
            )
        ]
        mae = regression_metrics(actual, predicted)["mae"]
        if mae < best_mae:
            best_threshold = threshold
            best_mae = mae
    return best_threshold


def _changed_target(sample: ForeignOwnershipQuantityFeatureSample) -> int:
    return int(sample.target_quantity != sample.previous_quantity)


def _walk_forward_folds(
    samples: list[ForeignOwnershipQuantityFeatureSample],
) -> list[WalkForwardFold]:
    unique_dates = sorted({sample.sample_date for sample in samples})
    if len(unique_dates) < 60:
        raise ValueError("Foreign ownership quantity walk-forward validation needs 60+ dates")
    test_window = max(10, len(unique_dates) // 12)
    first_test_index = max(30, int(len(unique_dates) * 0.55))
    starts = list(range(first_test_index, len(unique_dates) - test_window + 1, test_window))
    starts = starts[-max(MIN_WALK_FORWARD_FOLDS, min(6, len(starts))) :]
    folds: list[WalkForwardFold] = []
    for start in starts:
        test_dates = set(unique_dates[start : start + test_window])
        train_cutoff = unique_dates[start]
        train_samples = [sample for sample in samples if sample.sample_date < train_cutoff]
        test_samples = [sample for sample in samples if sample.sample_date in test_dates]
        if train_samples and test_samples:
            folds.append((train_samples, test_samples))
    if len(folds) < MIN_WALK_FORWARD_FOLDS:
        raise ValueError(
            "Foreign ownership quantity walk-forward validation produced too few folds"
        )
    return folds


def _mean_metrics(metric_list: list[dict[str, float]]) -> dict[str, float]:
    if not metric_list:
        return {"mae": 0.0, "rmse": 0.0, "mape": 0.0}
    return {
        key: sum(metrics[key] for metrics in metric_list) / len(metric_list)
        for key in ("mae", "rmse", "mape")
    }


def _baseline_metrics_from_folds(folds: list[WalkForwardFold]) -> dict[str, float]:
    actual: list[int] = []
    predicted: list[int] = []
    for _, test_samples in folds:
        actual.extend(sample.target_quantity for sample in test_samples)
        predicted.extend(baseline_prediction(sample) for sample in test_samples)
    return regression_metrics(actual, predicted)


def _model_metrics_from_fold_predictions(
    folds: list[WalkForwardFold],
    selected_fold_predictions: list[list[float]],
    blend_alpha: float,
) -> dict[str, float]:
    actual: list[int] = []
    predicted: list[int] = []
    for (_, test_samples), predicted_delta_ratios in zip(
        folds,
        selected_fold_predictions,
        strict=True,
    ):
        for sample, predicted_delta_ratio in zip(
            test_samples,
            predicted_delta_ratios,
            strict=True,
        ):
            actual.append(sample.target_quantity)
            predicted.append(blended_model_prediction(sample, predicted_delta_ratio, blend_alpha))
    return regression_metrics(actual, predicted)


def _quantity_prediction(
    sample: ForeignOwnershipQuantityFeatureSample,
    raw_prediction: float,
    blend_alpha: float,
    prediction_mode: str,
) -> int:
    if prediction_mode.startswith(PREDICTION_MODE_RESIDUAL_PREFIX):
        base_policy = prediction_mode.removeprefix(PREDICTION_MODE_RESIDUAL_PREFIX)
        return _clip_quantity(
            runtime_policy_quantity(
                sample.previous_quantity,
                sample.features,
                base_policy,
            )
            + blend_alpha * raw_prediction
        )
    if prediction_mode == PREDICTION_MODE_DELTA_QUANTITY:
        return _clip_quantity(sample.previous_quantity + blend_alpha * raw_prediction)
    if prediction_mode == PREDICTION_MODE_TARGET_QUANTITY:
        return _clip_quantity(
            sample.previous_quantity + blend_alpha * (raw_prediction - sample.previous_quantity)
        )
    if prediction_mode == PREDICTION_MODE_LOG_DELTA_RATIO:
        return _clip_quantity(
            sample.previous_quantity * exp(_clip_log_delta(blend_alpha * raw_prediction))
        )
    return blended_model_prediction(sample, raw_prediction, blend_alpha)


def _clip_quantity(value: float) -> int:
    return max(0, int(round(value)))


def _clip_log_delta(value: float) -> float:
    return max(-0.5, min(0.5, value))


def _stock_routed_model_metrics(
    folds: list[WalkForwardFold],
    fold_predictions_by_model: dict[tuple[str, int], list[float]],
    model_by_stock: dict[str, str],
    blend_alpha_by_stock: dict[str, float],
    fallback_model_name: str,
    fallback_blend_alpha: float,
    model_prediction_modes: dict[str, str],
) -> dict[str, float]:
    actual: list[int] = []
    predicted: list[int] = []
    for fold_index, (_, test_samples) in enumerate(folds, start=1):
        for sample_index, sample in enumerate(test_samples):
            model_name = model_by_stock.get(sample.stock_code, fallback_model_name)
            blend_alpha = blend_alpha_by_stock.get(
                sample.stock_code,
                fallback_blend_alpha,
            )
            raw_prediction = fold_predictions_by_model[(model_name, fold_index)][sample_index]
            actual.append(sample.target_quantity)
            predicted.append(
                _quantity_prediction(
                    sample,
                    raw_prediction,
                    blend_alpha,
                    model_prediction_modes.get(
                        model_name,
                        PREDICTION_MODE_DELTA_RATIO,
                    ),
                )
            )
    return regression_metrics(actual, predicted)


def _quality_gates(
    *,
    observation_count: int,
    stock_count: int,
    history_days: int,
    fold_count: int,
    baseline_metrics: dict[str, float],
    guarded_metrics: dict[str, float],
    minimum_promotable_stock_count: int,
    minimum_promotable_history_days: int,
    minimum_promotable_observations: int,
    restricted_universe_applied: bool,
) -> dict[str, Any]:
    failures: list[str] = []
    if not restricted_universe_applied:
        failures.append("restricted_universe_not_applied")
    if stock_count < minimum_promotable_stock_count:
        failures.append("insufficient_stock_count")
    if history_days < minimum_promotable_history_days:
        failures.append("insufficient_history_days")
    if observation_count < minimum_promotable_observations:
        failures.append("insufficient_observation_count")
    if fold_count < MIN_WALK_FORWARD_FOLDS:
        failures.append("insufficient_walk_forward_folds")
    if guarded_metrics["mae"] >= baseline_metrics["mae"]:
        failures.append("does_not_beat_persistence_baseline")
    return {
        "status": "pass" if not failures else "fail",
        "failures": failures,
        "minimum_training_samples": MIN_TRAINING_SAMPLES,
        "minimum_walk_forward_folds": MIN_WALK_FORWARD_FOLDS,
        "minimum_promotable_stock_count": minimum_promotable_stock_count,
        "actual_stock_count": stock_count,
        "minimum_promotable_history_days": minimum_promotable_history_days,
        "actual_history_days": history_days,
        "minimum_promotable_observations": minimum_promotable_observations,
        "actual_observation_count": observation_count,
        "beats_persistence_baseline": guarded_metrics["mae"] < baseline_metrics["mae"],
        "restricted_universe_applied": restricted_universe_applied,
    }


def _estimate_stock_routed_residual_ratio(
    models_by_name: dict[str, Pipeline | ForeignOwnershipQuantityHurdleDeltaModel],
    samples: list[ForeignOwnershipQuantityFeatureSample],
    model_by_stock: dict[str, str],
    blend_alpha_by_stock: dict[str, float],
    fallback_model_name: str,
    fallback_blend_alpha: float,
    model_prediction_modes: dict[str, str],
) -> float:
    actual = [sample.target_quantity for sample in samples]
    predicted = [0 for _ in samples]
    sample_indexes_by_model: dict[str, list[int]] = {}
    for sample_index, sample in enumerate(samples):
        model_name = model_by_stock.get(sample.stock_code, fallback_model_name)
        sample_indexes_by_model.setdefault(model_name, []).append(sample_index)

    for model_name, sample_indexes in sample_indexes_by_model.items():
        model = models_by_name[model_name]
        raw_predictions = [
            float(value)
            for value in model.predict(
                [samples[sample_index].features for sample_index in sample_indexes]
            )
        ]
        prediction_mode = model_prediction_modes.get(
            model_name,
            PREDICTION_MODE_DELTA_RATIO,
        )
        for sample_index, raw_prediction in zip(
            sample_indexes,
            raw_predictions,
            strict=True,
        ):
            sample = samples[sample_index]
            blend_alpha = blend_alpha_by_stock.get(
                sample.stock_code,
                fallback_blend_alpha,
            )
            predicted[sample_index] = _quantity_prediction(
                sample,
                raw_prediction,
                blend_alpha,
                prediction_mode,
            )
    return residual_abs_p90_ratio(actual, predicted)


def _guarded_runtime_metrics(
    folds: list[WalkForwardFold],
    runtime_by_stock: dict[str, str],
    model_by_stock: dict[str, str],
    blend_alpha_by_stock: dict[str, float],
    fold_predictions_by_model: dict[tuple[str, int], list[float]],
    fallback_model_name: str,
    fallback_blend_alpha: float,
    model_prediction_modes: dict[str, str],
) -> dict[str, float]:
    actual: list[int] = []
    predicted: list[int] = []
    for fold_index, (_, test_samples) in enumerate(folds, start=1):
        for sample_index, sample in enumerate(test_samples):
            actual.append(sample.target_quantity)
            runtime_policy = runtime_by_stock.get(sample.stock_code, RUNTIME_POLICY_ML)
            if runtime_policy != RUNTIME_POLICY_ML:
                predicted.append(
                    runtime_policy_quantity(
                        sample.previous_quantity,
                        sample.features,
                        runtime_policy,
                    )
                )
                continue
            model_name = model_by_stock.get(sample.stock_code, fallback_model_name)
            blend_alpha = blend_alpha_by_stock.get(
                sample.stock_code,
                fallback_blend_alpha,
            )
            raw_prediction = fold_predictions_by_model[(model_name, fold_index)][sample_index]
            predicted.append(
                _quantity_prediction(
                    sample,
                    raw_prediction,
                    blend_alpha,
                    model_prediction_modes.get(
                        model_name,
                        PREDICTION_MODE_DELTA_RATIO,
                    ),
                )
            )
    return regression_metrics(actual, predicted)


def _per_stock_validation(
    folds: list[WalkForwardFold],
    fold_predictions_by_model: dict[tuple[str, int], list[float]],
    model_prediction_modes: dict[str, str],
) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    candidate_model_names = sorted({model_name for model_name, _ in fold_predictions_by_model})
    for fold_index, (_, test_samples) in enumerate(folds, start=1):
        for sample_index, sample in enumerate(test_samples):
            default_bucket: dict[str, Any] = {
                "actual": [],
                "previous": [],
                "model_predictions": {},
            }
            default_bucket.update(
                {policy: [] for policy in RUNTIME_POLICIES if policy != RUNTIME_POLICY_ML}
            )
            bucket = grouped.setdefault(sample.stock_code, default_bucket)
            bucket["actual"].append(sample.target_quantity)
            bucket["previous"].append(sample.previous_quantity)
            for policy in RUNTIME_POLICIES:
                if policy == RUNTIME_POLICY_ML:
                    continue
                bucket[policy].append(
                    runtime_policy_quantity(
                        sample.previous_quantity,
                        sample.features,
                        policy,
                    )
                )
            model_predictions = bucket["model_predictions"]
            for model_name in candidate_model_names:
                raw_prediction = fold_predictions_by_model[(model_name, fold_index)][sample_index]
                prediction_mode = model_prediction_modes.get(
                    model_name,
                    PREDICTION_MODE_DELTA_RATIO,
                )
                for blend_alpha in BLEND_ALPHA_CANDIDATES:
                    prediction_key = _model_prediction_key(model_name, blend_alpha)
                    model_predictions.setdefault(prediction_key, []).append(
                        _quantity_prediction(
                            sample,
                            raw_prediction,
                            blend_alpha,
                            prediction_mode,
                        )
                    )

    reports: list[dict[str, Any]] = []
    for stock_code, values in grouped.items():
        actual = values["actual"]
        baseline = values[RUNTIME_POLICY_BASELINE]
        policy_metrics = {
            policy: regression_metrics(actual, values[policy])
            for policy in RUNTIME_POLICIES
            if policy != RUNTIME_POLICY_ML
        }
        model_prediction_metrics = {
            prediction_key: regression_metrics(actual, predictions)
            for prediction_key, predictions in values["model_predictions"].items()
        }
        baseline_metrics = policy_metrics[RUNTIME_POLICY_BASELINE]
        best_ml_key = _select_mape_guarded_ml_key(
            model_prediction_metrics,
            baseline_metrics,
        )
        best_ml_model, best_ml_blend_alpha = _parse_model_prediction_key(best_ml_key)
        policy_metrics[RUNTIME_POLICY_ML] = model_prediction_metrics[best_ml_key]
        model_metrics = policy_metrics[RUNTIME_POLICY_ML]
        recommended_runtime = _select_mape_guarded_runtime(
            policy_metrics,
            baseline_metrics,
        )
        recommended_predictions = (
            values[recommended_runtime]
            if recommended_runtime != RUNTIME_POLICY_ML
            else values["model_predictions"][best_ml_key]
        )
        absolute_errors = sorted(
            abs(actual_quantity - predicted_quantity)
            for actual_quantity, predicted_quantity in zip(
                actual,
                recommended_predictions,
                strict=True,
            )
        )
        interval_index = min(
            len(absolute_errors) - 1,
            max(0, int(len(absolute_errors) * 0.9)),
        )
        prediction_interval = max(1, int(absolute_errors[interval_index]))
        interval_coverage = sum(error <= prediction_interval for error in absolute_errors) / max(
            1, len(absolute_errors)
        )
        median_previous = sorted(values["previous"])[len(values["previous"]) // 2]
        changed_transition_count = sum(
            1
            for actual_quantity, baseline_quantity in zip(actual, baseline, strict=True)
            if actual_quantity != baseline_quantity
        )
        reports.append(
            {
                "stock_code": stock_code,
                "sample_count": len(actual),
                "changed_transition_count": changed_transition_count,
                "changed_transition_rate": changed_transition_count / len(actual)
                if actual
                else 0.0,
                "baseline_metrics": baseline_metrics,
                "model_metrics": model_metrics,
                "runtime_policy_metrics": policy_metrics,
                "best_ml_model": best_ml_model,
                "best_ml_blend_alpha": best_ml_blend_alpha,
                "mae_improvement_over_baseline": (
                    (baseline_metrics["mae"] - policy_metrics[recommended_runtime]["mae"])
                    / baseline_metrics["mae"]
                    if baseline_metrics["mae"] > 0
                    else 0.0
                ),
                "recommended_runtime": recommended_runtime,
                "prediction_interval_abs_p90_quantity": prediction_interval,
                "prediction_interval_coverage": interval_coverage,
                "prediction_interval_width_ratio": prediction_interval / max(1, median_previous),
            }
        )
    return sorted(
        reports,
        key=lambda report: (
            report["recommended_runtime"] == "ml",
            report["mae_improvement_over_baseline"],
        ),
        reverse=True,
    )


def _model_prediction_key(model_name: str, blend_alpha: float) -> str:
    return f"{model_name}|{blend_alpha:.6f}"


def _select_mape_guarded_ml_key(
    model_prediction_metrics: dict[str, dict[str, float]],
    baseline_metrics: dict[str, float],
) -> str:
    mape_safe_keys = [
        prediction_key
        for prediction_key, metrics in model_prediction_metrics.items()
        if metrics["mape"] <= baseline_metrics["mape"]
    ]
    candidate_keys = mape_safe_keys or list(model_prediction_metrics)
    return min(
        candidate_keys,
        key=lambda prediction_key: (
            _normalized_metric_score(
                model_prediction_metrics[prediction_key],
                baseline_metrics,
            ),
            model_prediction_metrics[prediction_key]["mae"],
            model_prediction_metrics[prediction_key]["rmse"],
        ),
    )


def _select_mape_guarded_runtime(
    policy_metrics: dict[str, dict[str, float]],
    baseline_metrics: dict[str, float],
) -> str:
    candidate_policies = [policy for policy in policy_metrics if policy != RUNTIME_POLICY_BASELINE]
    mape_safe_policies = [
        policy
        for policy in candidate_policies
        if policy_metrics[policy]["mape"] <= baseline_metrics["mape"]
    ]
    selectable_policies = mape_safe_policies or candidate_policies
    return min(
        selectable_policies,
        key=lambda policy: (
            _normalized_metric_score(policy_metrics[policy], baseline_metrics),
            policy_metrics[policy]["mae"],
            policy_metrics[policy]["rmse"],
        ),
    )


def _normalized_metric_score(
    metrics: dict[str, float],
    baseline_metrics: dict[str, float],
) -> float:
    return (
        metrics["mae"] / max(1.0, baseline_metrics["mae"])
        + metrics["rmse"] / max(1.0, baseline_metrics["rmse"])
        + metrics["mape"] / max(0.000001, baseline_metrics["mape"])
    )


def _parse_model_prediction_key(prediction_key: str) -> tuple[str, float]:
    model_name, blend_alpha = prediction_key.rsplit("|", 1)
    return model_name, float(blend_alpha)


def _improvement_over_baseline(
    baseline_metrics: dict[str, float],
    model_metrics: dict[str, float],
) -> dict[str, float]:
    return {
        key: (
            (baseline_metrics[key] - model_metrics[key]) / baseline_metrics[key]
            if baseline_metrics[key] > 0
            else 0.0
        )
        for key in ("mae", "rmse", "mape")
    }


def _log_training(message: str) -> None:
    # 장시간 학습에서 병목 위치를 확인한다.
    print(f"[foreign-ownership-train] {message}", file=sys.stderr, flush=True)


def _required(row: dict[str, str], key: str) -> str:
    value = row.get(key)
    if value is None or value.strip() == "":
        raise ValueError(f"Missing required CSV column value: {key}")
    return value.strip()
