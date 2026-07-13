from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import replace
from statistics import fmean, pstdev

from hannah_montana_ai.training.k_fnspid.schema import DailyPrice, MarketImpact


def build_market_impacts(
    document_entities: list[tuple[str, str, str]],
    prices: list[DailyPrice],
) -> list[MarketImpact]:
    by_stock: dict[str, list[DailyPrice]] = defaultdict(list)
    index_by_stock_date: dict[tuple[str, str], int] = {}
    by_market_date: dict[tuple[str, str], list[float]] = defaultdict(list)
    for price in prices:
        by_stock[price.stock_code].append(price)
    for rows in by_stock.values():
        rows.sort(key=lambda row: row.trade_date)
        for index, row in enumerate(rows):
            index_by_stock_date[(row.stock_code, row.trade_date)] = index
        for previous, current in zip(rows, rows[1:], strict=False):
            if previous.adjusted_close > 0:
                by_market_date[(current.market, current.trade_date)].append(
                    current.adjusted_close / previous.adjusted_close - 1
                )

    market_returns = {key: fmean(values) for key, values in by_market_date.items() if values}
    impacts: list[MarketImpact] = []
    impact_by_stock_date: dict[tuple[str, str], MarketImpact] = {}
    for document_id, stock_code, effective_date in document_entities:
        cache_key = (stock_code, effective_date)
        cached = impact_by_stock_date.get(cache_key)
        if cached is not None:
            impacts.append(replace(cached, document_id=document_id))
            continue
        rows = by_stock.get(stock_code, [])
        index = index_by_stock_date.get((stock_code, effective_date), -1)
        if index < 1:
            impact = _missing_impact(document_id, stock_code, effective_date)
            impacts.append(impact)
            impact_by_stock_date[cache_key] = impact
            continue
        abnormal = {
            horizon: _abnormal_return(rows, index, horizon, market_returns) for horizon in (1, 3, 5)
        }
        volume_z = _zscore(
            math.log1p(rows[index].volume),
            [math.log1p(row.volume) for row in rows[max(0, index - 60) : index]],
        )
        current_range = _range_ratio(rows[index])
        previous_ranges = [_range_ratio(row) for row in rows[max(0, index - 20) : index]]
        volatility = (
            current_range / fmean(previous_ranges)
            if previous_ranges and fmean(previous_ranges) > 0
            else None
        )
        score = _materiality(abnormal[1], abnormal[3], volume_z, volatility)
        impact = MarketImpact(
            document_id=document_id,
            stock_code=stock_code,
            effective_trade_date=effective_date,
            abnormal_return_1d=abnormal[1],
            abnormal_return_3d=abnormal[3],
            abnormal_return_5d=abnormal[5],
            abnormal_volume_z=volume_z,
            volatility_shock=volatility,
            materiality_score=score,
            market_direction_1d=_direction(abnormal[1]),
            importance=_importance(score),
            label_confidence=0.9 if abnormal[5] is not None else 0.72,
            confounded=False,
        )
        impacts.append(impact)
        impact_by_stock_date[cache_key] = impact
    return impacts


def _abnormal_return(
    rows: list[DailyPrice],
    index: int,
    horizon: int,
    market_returns: dict[tuple[str, str], float],
) -> float | None:
    end_index = index + horizon - 1
    if index < 1 or end_index >= len(rows) or rows[index - 1].adjusted_close <= 0:
        return None
    stock_return = rows[end_index].adjusted_close / rows[index - 1].adjusted_close - 1
    benchmark = 1.0
    for offset in range(horizon):
        benchmark *= 1 + market_returns.get(
            (rows[index].market, rows[index + offset].trade_date), 0.0
        )
    return round(stock_return - (benchmark - 1), 8)


def _zscore(value: float, history: list[float]) -> float | None:
    if len(history) < 20:
        return None
    deviation = pstdev(history)
    return round((value - fmean(history)) / deviation, 8) if deviation > 0 else 0.0


def _range_ratio(price: DailyPrice) -> float:
    return (
        (price.high_price - price.low_price) / price.close_price if price.close_price > 0 else 0.0
    )


def _materiality(
    one_day: float | None,
    three_day: float | None,
    volume_z: float | None,
    volatility: float | None,
) -> float | None:
    if one_day is None:
        return None
    raw = (
        0.5 * min(abs(one_day) / 0.1, 1.0)
        + 0.2 * min(abs(three_day or 0.0) / 0.15, 1.0)
        + 0.15 * min(abs(volume_z or 0.0) / 4.0, 1.0)
        + 0.15 * min(max((volatility or 1.0) - 1.0, 0.0) / 4.0, 1.0)
    )
    return round(min(raw, 1.0), 8)


def _direction(value: float | None) -> str:
    if value is None:
        return "UNKNOWN"
    if value > 0.01:
        return "UP"
    if value < -0.01:
        return "DOWN"
    return "FLAT"


def _importance(score: float | None) -> str:
    if score is None:
        return "UNKNOWN"
    if score >= 0.75:
        return "CRITICAL"
    if score >= 0.45:
        return "HIGH"
    if score >= 0.2:
        return "MEDIUM"
    return "LOW"


def _missing_impact(document_id: str, stock_code: str, effective_date: str) -> MarketImpact:
    return MarketImpact(
        document_id=document_id,
        stock_code=stock_code,
        effective_trade_date=effective_date,
        abnormal_return_1d=None,
        abnormal_return_3d=None,
        abnormal_return_5d=None,
        abnormal_volume_z=None,
        volatility_shock=None,
        materiality_score=None,
        market_direction_1d="UNKNOWN",
        importance="UNKNOWN",
        label_confidence=0.0,
        confounded=True,
    )
