from __future__ import annotations

import json
from collections import Counter
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, cast

from hannah_montana_ai.training.dataset import load_labeled_alerts
from hannah_montana_ai.training.stock_universe import (
    DEFAULT_NEWS_INTENTS,
    StockUniverseEntry,
    StockUniverseMatcher,
    build_stock_news_queries,
    load_stock_universe,
)
from hannah_montana_ai.training.weak_labeler import RawCollectedAlert

STOCK_COLLECTION_SHARD_ROW_SCHEMA_VERSION = "stock-collection-shard-row/v1"
STOCK_COLLECTION_SHARD_REPORT_SCHEMA_VERSION = "stock-collection-shard-report/v1"


@dataclass(frozen=True)
class StockCollectionShardRow:
    schema_version: str
    stock_code: str
    stock_name: str
    stock_name_en: str
    market: str
    dart_corp_code: str
    collection_priority: int
    priority_bucket: str
    shard_index: int
    shard_size: int
    raw_match_count: int
    candidate_count: int
    training_gold_count: int
    evaluation_gold_count: int
    naver_queries: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StockCollectionShardPlanResult:
    rows: list[StockCollectionShardRow]
    report: dict[str, Any]


def build_stock_collection_shard_plan(
    stock_universe_path: Path,
    raw_alert_path: Path,
    candidate_path: Path,
    training_paths: Sequence[Path],
    evaluation_paths: Sequence[Path],
    shard_size: int = 100,
    intents: Sequence[str] = DEFAULT_NEWS_INTENTS,
    stock_limit: int | None = None,
) -> StockCollectionShardPlanResult:
    universe = load_stock_universe(stock_universe_path)
    raw_counter = _raw_stock_counter(raw_alert_path, universe)
    candidate_counter = _jsonl_stock_counter(candidate_path)
    training_counter = _labeled_stock_counter(training_paths)
    evaluation_counter = _labeled_stock_counter(evaluation_paths)

    planned_stocks = [
        stock
        for stock in universe
        if _needs_collection(stock, candidate_counter, training_counter, evaluation_counter)
    ]
    planned_stocks.sort(
        key=lambda stock: (
            _collection_priority(stock, raw_counter, candidate_counter),
            stock.stock_code,
        )
    )
    if stock_limit is not None:
        planned_stocks = planned_stocks[:stock_limit]

    rows = [
        _to_plan_row(
            stock=stock,
            index=index,
            shard_size=shard_size,
            intents=intents,
            raw_counter=raw_counter,
            candidate_counter=candidate_counter,
            training_counter=training_counter,
            evaluation_counter=evaluation_counter,
        )
        for index, stock in enumerate(planned_stocks)
    ]
    report = _build_report(
        stock_universe_path=stock_universe_path,
        raw_alert_path=raw_alert_path,
        candidate_path=candidate_path,
        training_paths=training_paths,
        evaluation_paths=evaluation_paths,
        universe=universe,
        rows=rows,
        raw_counter=raw_counter,
        candidate_counter=candidate_counter,
        training_counter=training_counter,
        evaluation_counter=evaluation_counter,
        shard_size=shard_size,
        intents=intents,
        stock_limit=stock_limit,
    )
    return StockCollectionShardPlanResult(rows=rows, report=report)


def write_stock_collection_shard_plan(
    path: Path,
    rows: Sequence[StockCollectionShardRow],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row.to_dict(), ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def write_stock_collection_shard_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_stock_collection_plan_queries(
    plan_path: Path,
    shard_index: int | None = None,
    stock_limit: int | None = None,
) -> list[str]:
    rows = _load_plan_rows(plan_path)
    if shard_index is not None:
        rows = [row for row in rows if int(row["shard_index"]) == shard_index]
    if stock_limit is not None:
        rows = rows[:stock_limit]
    queries = [
        query
        for row in rows
        for query in row.get("naver_queries", [])
        if isinstance(query, str) and query
    ]
    return list(dict.fromkeys(queries))


def _needs_collection(
    stock: StockUniverseEntry,
    candidate_counter: Counter[str],
    training_counter: Counter[str],
    evaluation_counter: Counter[str],
) -> bool:
    return (
        candidate_counter[stock.stock_code] == 0
        and training_counter[stock.stock_code] == 0
        and evaluation_counter[stock.stock_code] == 0
    )


def _collection_priority(
    stock: StockUniverseEntry,
    raw_counter: Counter[str],
    candidate_counter: Counter[str],
) -> int:
    if candidate_counter[stock.stock_code] > 0:
        return 30
    if raw_counter[stock.stock_code] == 0:
        return 10
    return 20


def _priority_bucket(
    stock: StockUniverseEntry,
    raw_counter: Counter[str],
    candidate_counter: Counter[str],
) -> str:
    if candidate_counter[stock.stock_code] > 0:
        return "already_has_candidate"
    if raw_counter[stock.stock_code] == 0:
        return "no_raw_no_candidate"
    return "raw_without_candidate"


def _to_plan_row(
    stock: StockUniverseEntry,
    index: int,
    shard_size: int,
    intents: Sequence[str],
    raw_counter: Counter[str],
    candidate_counter: Counter[str],
    training_counter: Counter[str],
    evaluation_counter: Counter[str],
) -> StockCollectionShardRow:
    return StockCollectionShardRow(
        schema_version=STOCK_COLLECTION_SHARD_ROW_SCHEMA_VERSION,
        stock_code=stock.stock_code,
        stock_name=stock.stock_name,
        stock_name_en=stock.stock_name_en,
        market=stock.market,
        dart_corp_code=stock.dart_corp_code,
        collection_priority=_collection_priority(stock, raw_counter, candidate_counter),
        priority_bucket=_priority_bucket(stock, raw_counter, candidate_counter),
        shard_index=index // shard_size,
        shard_size=shard_size,
        raw_match_count=raw_counter[stock.stock_code],
        candidate_count=candidate_counter[stock.stock_code],
        training_gold_count=training_counter[stock.stock_code],
        evaluation_gold_count=evaluation_counter[stock.stock_code],
        naver_queries=build_stock_news_queries([stock], intents=intents),
    )


def _build_report(
    stock_universe_path: Path,
    raw_alert_path: Path,
    candidate_path: Path,
    training_paths: Sequence[Path],
    evaluation_paths: Sequence[Path],
    universe: Sequence[StockUniverseEntry],
    rows: Sequence[StockCollectionShardRow],
    raw_counter: Counter[str],
    candidate_counter: Counter[str],
    training_counter: Counter[str],
    evaluation_counter: Counter[str],
    shard_size: int,
    intents: Sequence[str],
    stock_limit: int | None,
) -> dict[str, Any]:
    priority_distribution = Counter(row.priority_bucket for row in rows)
    shard_distribution = Counter(row.shard_index for row in rows)
    return {
        "schema_version": STOCK_COLLECTION_SHARD_REPORT_SCHEMA_VERSION,
        "row_schema_version": STOCK_COLLECTION_SHARD_ROW_SCHEMA_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "stock_universe_path": _report_path(stock_universe_path),
        "raw_alert_path": _report_path(raw_alert_path),
        "candidate_path": _report_path(candidate_path),
        "training_paths": [_report_path(path) for path in training_paths],
        "evaluation_paths": [_report_path(path) for path in evaluation_paths],
        "universe_count": len(universe),
        "raw_matched_stock_count": len(raw_counter),
        "candidate_stock_count": len(candidate_counter),
        "training_gold_stock_count": len(training_counter),
        "evaluation_gold_stock_count": len(evaluation_counter),
        "planned_stock_count": len(rows),
        "planned_query_count": sum(len(row.naver_queries) for row in rows),
        "shard_size": shard_size,
        "shard_count": max(shard_distribution) + 1 if shard_distribution else 0,
        "stock_limit": stock_limit,
        "intents": list(intents),
        "priority_distribution": dict(sorted(priority_distribution.items())),
        "shard_distribution": {
            str(shard_index): shard_distribution[shard_index]
            for shard_index in sorted(shard_distribution)
        },
        "next_collection_commands": _next_collection_commands(
            shard_distribution=shard_distribution,
        ),
        "collection_policy": (
            "plan targets stocks without supervised gold, evaluation gold, or "
            "candidate queue rows; collected rows remain raw or review candidates "
            "until human_review_approved"
        ),
    }


def _next_collection_commands(
    shard_distribution: Counter[int],
    max_commands: int = 5,
) -> list[str]:
    return [
        (
            "uv run python scripts/collect_training_data.py "
            "--reuse-existing-raw "
            "--stock-collection-plan data/curation/stock_collection_shard_plan.jsonl "
            f"--stock-collection-plan-shard-index {shard_index}"
        )
        for shard_index in sorted(shard_distribution)[:max_commands]
    ]


def _raw_stock_counter(
    raw_alert_path: Path,
    stock_universe: Sequence[StockUniverseEntry],
) -> Counter[str]:
    matcher = StockUniverseMatcher(stock_universe)
    counter: Counter[str] = Counter()
    for alert in _load_raw_alerts(raw_alert_path):
        stock = matcher.match_raw_alert(alert)
        if stock is not None:
            counter[stock.stock_code] += 1
    return counter


def _jsonl_stock_counter(path: Path) -> Counter[str]:
    counter: Counter[str] = Counter()
    for row in _read_jsonl(path):
        stock_code = row.get("stock_code")
        if isinstance(stock_code, str) and stock_code:
            counter[stock_code] += 1
    return counter


def _labeled_stock_counter(paths: Sequence[Path]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for path in paths:
        if not path.exists():
            continue
        for sample in load_labeled_alerts(path):
            if sample.stock_code:
                counter[sample.stock_code] += 1
    return counter


def _load_raw_alerts(path: Path) -> list[RawCollectedAlert]:
    alerts: list[RawCollectedAlert] = []
    for row in _read_jsonl(path):
        source_type = row.get("source_type")
        if source_type not in {"NEWS", "DISCLOSURE"}:
            continue
        alerts.append(
            RawCollectedAlert(
                source_type=cast(Literal["NEWS", "DISCLOSURE"], source_type),
                title=str(row["title"]),
                snippet=str(row["snippet"]),
                original_url=str(row["original_url"]),
                published_at=str(row["published_at"]),
                provider=str(row["provider"]),
            )
        )
    return alerts


def _load_plan_rows(path: Path) -> list[dict[str, Any]]:
    return _read_jsonl(path)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            payload = json.loads(line)
            if isinstance(payload, dict):
                rows.append(payload)
    return rows


def _report_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)
