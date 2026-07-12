from __future__ import annotations

from datetime import date, timedelta


def temporal_split(
    effective_trade_date: str,
    *,
    validation_start: date,
    test_start: date,
    embargo_days: int = 7,
) -> str:
    current = date.fromisoformat(effective_trade_date)
    validation_embargo = validation_start - timedelta(days=embargo_days)
    test_embargo = test_start - timedelta(days=embargo_days)
    if validation_embargo <= current < validation_start or test_embargo <= current < test_start:
        return "EMBARGO"
    if current >= test_start:
        return "TEST"
    if current >= validation_start:
        return "VALIDATION"
    return "TRAIN"
