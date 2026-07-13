from __future__ import annotations

from collections import defaultdict
from typing import Any


def select_unconfounded_representatives(
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    clusters_by_stock_date: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in candidates:
        clusters_by_stock_date[
            (str(row["stock_code"]), str(row["effective_trade_date"]))
        ].add(str(row["event_cluster_id"]))
    unconfounded = [
        row
        for row in candidates
        if len(
            clusters_by_stock_date[
                (str(row["stock_code"]), str(row["effective_trade_date"]))
            ]
        )
        == 1
    ]
    representatives: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in unconfounded:
        key = (
            str(row["event_cluster_id"]),
            str(row["stock_code"]),
            str(row["effective_trade_date"]),
        )
        current = representatives.get(key)
        if current is None or len(str(row["text"])) > len(str(current["text"])):
            representatives[key] = row
    return list(representatives.values())
