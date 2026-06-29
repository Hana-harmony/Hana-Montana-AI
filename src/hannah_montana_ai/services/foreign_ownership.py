from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

from hannah_montana_ai.core.config import get_settings
from hannah_montana_ai.domain.schemas import (
    ForeignOwnershipHistoryPoint,
    ForeignOwnershipTimeseriesPredictionRequest,
    ForeignOwnershipTimeseriesPredictionResponse,
)
from hannah_montana_ai.services.foreign_ownership_quantity_model import (
    ForeignOwnershipQuantityModel,
    ForeignOwnershipQuantityModelUnavailableError,
    ForeignOwnershipQuantityPoint,
    ForeignOwnershipQuantityPrediction,
)

FALLBACK_MODEL_VERSION = "hannah-foreign-owned-quantity-persistence-v1"
FALLBACK_UNCERTAINTY_RATE = 0.0005


class ForeignOwnershipTimeseriesPredictionService:
    def __init__(
        self,
        model_path: Path | None = None,
        model: ForeignOwnershipQuantityModel | None = None,
    ) -> None:
        self._model = model
        if self._model is None:
            resolved_model_path = model_path or get_settings().foreign_ownership_quantity_model_path
            try:
                self._model = ForeignOwnershipQuantityModel(resolved_model_path)
            except ForeignOwnershipQuantityModelUnavailableError:
                self._model = None

    def predict(
        self,
        request: ForeignOwnershipTimeseriesPredictionRequest,
    ) -> ForeignOwnershipTimeseriesPredictionResponse:
        history = _sorted_history(request.history)
        model_history = _model_history(request, history)
        prediction = _predict_owned_quantity(request, model_history, self._model)
        trend = _owned_quantity_trend_stats(model_history)
        min_rate = _limit_exhaustion_rate(prediction.lower_quantity, request.foreign_limit_quantity)
        base_rate = _limit_exhaustion_rate(
            prediction.predicted_quantity,
            request.foreign_limit_quantity,
        )
        max_rate = _limit_exhaustion_rate(prediction.upper_quantity, request.foreign_limit_quantity)

        return ForeignOwnershipTimeseriesPredictionResponse(
            stock_code=request.stock_code,
            predicted_foreign_owned_quantity=prediction.predicted_quantity,
            min_foreign_owned_quantity=prediction.lower_quantity,
            max_foreign_owned_quantity=prediction.upper_quantity,
            predicted_foreign_net_acquired_quantity=(
                prediction.predicted_quantity - request.foreign_owned_quantity
            ),
            predicted_foreign_limit_quantity=request.foreign_limit_quantity,
            min_foreign_limit_quantity=request.foreign_limit_quantity,
            max_foreign_limit_quantity=request.foreign_limit_quantity,
            min_foreign_limit_exhaustion_rate=min_rate,
            base_foreign_limit_exhaustion_rate=base_rate,
            max_foreign_limit_exhaustion_rate=max_rate,
            order_impact_rate=0.0,
            intraday_uncertainty_rate=0.0,
            observed_intraday_volume=0,
            trend_daily_change_rate=trend.daily_change_rate,
            history_observation_count=trend.observation_count,
            history_window_days=trend.window_days,
            base_date=request.base_date,
            calculated_at=datetime.now(UTC),
            confidence_level=prediction.confidence_level,
            confidence_score=prediction.confidence_score,
            model_version=prediction.model_version,
            source=prediction.source,
        )


@dataclass(frozen=True)
class _TrendStats:
    daily_change_rate: float
    uncertainty_rate: float
    observation_count: int
    window_days: int


@dataclass(frozen=True)
class _Confidence:
    level: str
    score: float


def _model_history(
    request: ForeignOwnershipTimeseriesPredictionRequest,
    history: list[ForeignOwnershipHistoryPoint],
) -> list[ForeignOwnershipQuantityPoint]:
    points = [
        ForeignOwnershipQuantityPoint(
            stock_code=request.stock_code,
            base_date=point.base_date,
            foreign_owned_quantity=point.foreign_owned_quantity,
            foreign_limit_quantity=point.foreign_limit_quantity,
        )
        for point in history
        if point.foreign_owned_quantity > 0
    ]
    if not points or points[-1].base_date != request.base_date:
        points.append(
            ForeignOwnershipQuantityPoint(
                stock_code=request.stock_code,
                base_date=request.base_date,
                foreign_owned_quantity=request.foreign_owned_quantity,
                foreign_limit_quantity=request.foreign_limit_quantity,
            )
        )
    deduped: dict[date, ForeignOwnershipQuantityPoint] = {}
    for point in points:
        deduped[point.base_date] = point
    return sorted(deduped.values(), key=lambda point: point.base_date)


def _predict_owned_quantity(
    request: ForeignOwnershipTimeseriesPredictionRequest,
    history: list[ForeignOwnershipQuantityPoint],
    model: ForeignOwnershipQuantityModel | None,
) -> ForeignOwnershipQuantityPrediction:
    if model is not None:
        try:
            return model.predict(request.stock_code, history)
        except ForeignOwnershipQuantityModelUnavailableError:
            pass
    latest_quantity = (
        history[-1].foreign_owned_quantity if history else request.foreign_owned_quantity
    )
    band = max(1, round(latest_quantity * FALLBACK_UNCERTAINTY_RATE))
    return ForeignOwnershipQuantityPrediction(
        predicted_quantity=latest_quantity,
        lower_quantity=max(0, latest_quantity - band),
        upper_quantity=latest_quantity + band,
        model_version=FALLBACK_MODEL_VERSION,
        confidence_level="AI_FOREIGN_OWNED_QUANTITY_PERSISTENCE_BASELINE",
        confidence_score=0.58 if len(history) >= 5 else 0.42,
        source="HANNAH_MONTANA_AI_FOREIGN_OWNED_QUANTITY_BASELINE",
    )


def _sorted_history(
    history: list[ForeignOwnershipHistoryPoint],
) -> list[ForeignOwnershipHistoryPoint]:
    return sorted(history, key=lambda point: point.base_date)


def _owned_quantity_trend_stats(history: list[ForeignOwnershipQuantityPoint]) -> _TrendStats:
    if len(history) < 2:
        return _TrendStats(0.0, 0.0, len(history), 0)

    first = history[0]
    last = history[-1]
    window_days = max(1, (last.base_date - first.base_date).days)
    daily_change_rate = _round_rate(
        (last.foreign_owned_quantity - first.foreign_owned_quantity)
        / max(1, first.foreign_owned_quantity)
        * 100
        / window_days
    )
    return _TrendStats(
        daily_change_rate=daily_change_rate,
        uncertainty_rate=0.0,
        observation_count=len(history),
        window_days=window_days,
    )


def _limit_exhaustion_rate(foreign_owned_quantity: int, foreign_limit_quantity: int) -> float:
    if foreign_limit_quantity <= 0:
        return 0.0
    return _round_rate(foreign_owned_quantity * 100 / foreign_limit_quantity)


def _round_rate(value: float) -> float:
    return round(value, 6)
