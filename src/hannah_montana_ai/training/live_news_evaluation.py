from __future__ import annotations

import json
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, Protocol, cast

from hannah_montana_ai.domain.schemas import AlertAnalysisRequest, AlertAnalysisResponse
from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.training.collector import (
    ProviderCollectionStatus,
    RawCollectionResult,
    collect_naver_news,
)
from hannah_montana_ai.training.stock_universe import StockUniverseEntry, normalize_stock_term
from hannah_montana_ai.training.weak_labeler import RawCollectedAlert

LIVE_NEWS_EVALUATION_ROW_SCHEMA_VERSION = "live-news-evaluation-row/v2"
LIVE_NEWS_EVALUATION_REPORT_SCHEMA_VERSION = "live-news-evaluation-report/v2"
LIVE_NEWS_MONITORING_STATUS_SCHEMA_VERSION = "live-news-monitoring-status/v1"
DEFAULT_LIVE_NEWS_INTENTS = ("주가", "실적", "공시", "수주", "전망")
LIVE_NEWS_CONFIDENCE_FIELDS = (
    "event_confidence",
    "sentiment_confidence",
    "importance_confidence",
    "stock_match_confidence",
)


class FinancialModel(Protocol):
    version: str

    def event_tag_probabilities(self, text: str, source_type: str) -> dict[str, float]:
        ...

    def sentiment_probabilities(self, text: str) -> dict[str, float]:
        ...

    def importance_probabilities(self, text: str, source_type: str) -> dict[str, float]:
        ...


class AnalyzerLike(Protocol):
    model: FinancialModel

    def analyze(self, request: AlertAnalysisRequest) -> AlertAnalysisResponse:
        ...


NewsCollector = Callable[..., RawCollectionResult]


@dataclass(frozen=True)
class LiveNewsQuery:
    query: str
    sampled_stock_code: str
    sampled_stock_name: str
    intent: str


@dataclass(frozen=True)
class LiveNewsEvaluationBatch:
    rows: list[dict[str, Any]]
    report: dict[str, Any]


def build_live_news_queries(
    stock_universe: Sequence[StockUniverseEntry],
    *,
    stock_sample_size: int,
    intents: Sequence[str] = DEFAULT_LIVE_NEWS_INTENTS,
    seed: int = 20260613,
) -> list[LiveNewsQuery]:
    sampled_stocks = _sample_stocks(stock_universe, stock_sample_size, seed)
    queries = [
        LiveNewsQuery(
            query=f"{stock.stock_name} {intent}",
            sampled_stock_code=stock.stock_code,
            sampled_stock_name=stock.stock_name,
            intent=intent,
        )
        for stock in sampled_stocks
        for intent in intents
        if stock.stock_name
    ]
    return list(dict.fromkeys(queries))


def build_live_news_evaluation_batch(
    *,
    stock_universe: Sequence[StockUniverseEntry],
    stock_universe_path: Path,
    output_path: Path,
    stock_sample_size: int = 20,
    max_news_per_query: int = 3,
    intents: Sequence[str] = DEFAULT_LIVE_NEWS_INTENTS,
    seed: int = 20260613,
    sleep_seconds: float = 0.2,
    max_retries: int = 2,
    sample_limit: int | None = None,
    analyzer: AnalyzerLike | None = None,
    news_collector: NewsCollector = collect_naver_news,
    generated_at: datetime | None = None,
) -> LiveNewsEvaluationBatch:
    timestamp = (generated_at or datetime.now(UTC)).isoformat()
    effective_analyzer: AnalyzerLike = analyzer or cast(AnalyzerLike, AlertAnalyzer())
    queries = build_live_news_queries(
        stock_universe,
        stock_sample_size=stock_sample_size,
        intents=intents,
        seed=seed,
    )
    rows: list[dict[str, Any]] = []
    statuses: list[ProviderCollectionStatus] = []
    seen_hashes: set[str] = set()

    for live_query in queries:
        result = news_collector(
            max_per_query=max_news_per_query,
            sleep_seconds=sleep_seconds,
            max_retries=max_retries,
            queries=(live_query.query,),
        )
        statuses.append(result.status)
        for alert in result.alerts:
            if alert.content_hash in seen_hashes:
                continue
            seen_hashes.add(alert.content_hash)
            rows.append(
                _build_row(
                    alert=alert,
                    live_query=live_query,
                    analyzer=effective_analyzer,
                    generated_at=timestamp,
                )
            )
            if sample_limit is not None and len(rows) >= sample_limit:
                return _build_batch(
                    rows=rows,
                    statuses=statuses,
                    generated_at=timestamp,
                    model_version=effective_analyzer.model.version,
                    stock_universe_path=stock_universe_path,
                    output_path=output_path,
                    requested_stock_sample_size=stock_sample_size,
                    selected_stock_count=len({query.sampled_stock_code for query in queries}),
                    query_count=len(queries),
                )

    return _build_batch(
        rows=rows,
        statuses=statuses,
        generated_at=timestamp,
        model_version=effective_analyzer.model.version,
        stock_universe_path=stock_universe_path,
        output_path=output_path,
        requested_stock_sample_size=stock_sample_size,
        selected_stock_count=len({query.sampled_stock_code for query in queries}),
        query_count=len(queries),
    )


def build_live_news_evaluation_report(
    *,
    rows: Sequence[dict[str, Any]],
    statuses: Sequence[ProviderCollectionStatus],
    generated_at: str,
    model_version: str,
    stock_universe_path: Path,
    output_path: Path,
    requested_stock_sample_size: int,
    selected_stock_count: int,
    query_count: int,
) -> dict[str, Any]:
    primary_matched_count = sum(1 for row in rows if row["sampled_stock_primary_matched"])
    related_matched_count = sum(1 for row in rows if row["sampled_stock_related_matched"])
    matched_count = sum(1 for row in rows if row["sampled_stock_model_matched"])
    null_stock_count = sum(1 for row in rows if row["predicted_stock_code"] is None)
    emitted_count = len(rows)
    raw_collected_count = sum(status.collected_count for status in statuses)

    return {
        "schema_version": LIVE_NEWS_EVALUATION_REPORT_SCHEMA_VERSION,
        "row_schema_version": LIVE_NEWS_EVALUATION_ROW_SCHEMA_VERSION,
        "generated_at": generated_at,
        "model_version": model_version,
        "stock_universe_path": str(stock_universe_path),
        "output_path": str(output_path),
        "requested_stock_sample_size": requested_stock_sample_size,
        "selected_stock_count": selected_stock_count,
        "query_count": query_count,
        "raw_collected_count": raw_collected_count,
        "emitted_row_count": emitted_count,
        "provider_status_totals": _provider_status_totals(statuses),
        "predicted_stock_null_count": null_stock_count,
        "sampled_stock_primary_match_count": primary_matched_count,
        "sampled_stock_related_match_count": related_matched_count,
        "sampled_stock_model_match_count": matched_count,
        "sampled_stock_model_match_rate": (
            round(matched_count / emitted_count, 6) if emitted_count else 0.0
        ),
        "event_top_label_distribution": dict(Counter(row["event_top_label"] for row in rows)),
        "sentiment_distribution": dict(Counter(row["predicted_sentiment"] for row in rows)),
        "importance_distribution": dict(Counter(row["predicted_importance"] for row in rows)),
        "confidence_summary": _confidence_summary(rows),
        "evaluation_policy": {
            "status": "unlabeled_live_smoke",
            "f1_available": False,
            "description": (
                "실시간 뉴스 배치는 라벨 없는 운영 표본이다. final_* 라벨을 채워 gold로 "
                "승격하기 전까지 F1이 아니라 drift, confidence, 종목 매칭 점검에만 쓴다."
            ),
        },
    }


def build_live_news_monitoring_status(
    *,
    live_report: dict[str, Any],
    release_report: dict[str, Any],
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    timestamp = (generated_at or datetime.now(UTC)).isoformat()
    live_model_version = str(live_report.get("model_version") or "")
    release_model_version = str(release_report.get("model_version") or "")
    checks = {
        "report_schema_current": (
            live_report.get("schema_version") == LIVE_NEWS_EVALUATION_REPORT_SCHEMA_VERSION
        ),
        "row_schema_current": (
            live_report.get("row_schema_version") == LIVE_NEWS_EVALUATION_ROW_SCHEMA_VERSION
        ),
        "model_version_current": (
            bool(live_model_version)
            and bool(release_model_version)
            and live_model_version == release_model_version
        ),
        "confidence_summary_present": _confidence_summary_present(live_report),
        "emitted_rows_present": int(live_report.get("emitted_row_count") or 0) > 0,
    }
    stale = not (
        checks["report_schema_current"]
        and checks["row_schema_current"]
        and checks["model_version_current"]
    )
    overall_status = "pass" if all(checks.values()) else "stale" if stale else "attention"

    return {
        "schema_version": LIVE_NEWS_MONITORING_STATUS_SCHEMA_VERSION,
        "generated_at": timestamp,
        "overall_status": overall_status,
        "checks": checks,
        "live_report": {
            "schema_version": live_report.get("schema_version"),
            "row_schema_version": live_report.get("row_schema_version"),
            "generated_at": live_report.get("generated_at"),
            "model_version": live_model_version,
            "emitted_row_count": int(live_report.get("emitted_row_count") or 0),
            "sampled_stock_model_match_rate": live_report.get(
                "sampled_stock_model_match_rate"
            ),
        },
        "current_release": {
            "schema_version": release_report.get("schema_version"),
            "model_version": release_model_version,
        },
        "required_action": _monitoring_required_action(overall_status),
        "policy": {
            "confidence_usage": "observe_only",
            "description": (
                "confidence 값은 운영 품질 관측과 downstream 노출 정책 입력으로만 제공하며 "
                "Hannah가 신뢰도 기반 자동 차단 여부를 결정하지 않는다."
            ),
        },
    }


def rows_to_jsonl(rows: Sequence[dict[str, Any]]) -> str:
    return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)


def report_to_json(report: dict[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2) + "\n"


def _build_batch(
    *,
    rows: list[dict[str, Any]],
    statuses: Sequence[ProviderCollectionStatus],
    generated_at: str,
    model_version: str,
    stock_universe_path: Path,
    output_path: Path,
    requested_stock_sample_size: int,
    selected_stock_count: int,
    query_count: int,
) -> LiveNewsEvaluationBatch:
    return LiveNewsEvaluationBatch(
        rows=rows,
        report=build_live_news_evaluation_report(
            rows=rows,
            statuses=statuses,
            generated_at=generated_at,
            model_version=model_version,
            stock_universe_path=stock_universe_path,
            output_path=output_path,
            requested_stock_sample_size=requested_stock_sample_size,
            selected_stock_count=selected_stock_count,
            query_count=query_count,
        ),
    )


def _build_row(
    *,
    alert: RawCollectedAlert,
    live_query: LiveNewsQuery,
    analyzer: AnalyzerLike,
    generated_at: str,
) -> dict[str, Any]:
    request = AlertAnalysisRequest(
        source_type=alert.source_type,
        title=alert.title,
        snippet=alert.snippet,
        original_url=cast(Any, alert.original_url),
    )
    response = analyzer.analyze(request)
    text = alert.text
    event_probabilities = analyzer.model.event_tag_probabilities(text, alert.source_type)
    sentiment_probabilities = analyzer.model.sentiment_probabilities(text)
    importance_probabilities = analyzer.model.importance_probabilities(text, alert.source_type)
    event_top_label, event_top_confidence = _top_label(event_probabilities)
    sentiment_top_label, sentiment_top_confidence = _top_label(sentiment_probabilities)
    importance_top_label, importance_top_confidence = _top_label(importance_probabilities)
    related_stocks = list(response.related_stocks)
    sampled_stock_primary_matched = response.stock_code == live_query.sampled_stock_code
    sampled_stock_related_matched = live_query.sampled_stock_code in related_stocks

    return {
        "schema_version": LIVE_NEWS_EVALUATION_ROW_SCHEMA_VERSION,
        "generated_at": generated_at,
        "review_status": "needs_review",
        "sampled_stock_code": live_query.sampled_stock_code,
        "sampled_stock_name": live_query.sampled_stock_name,
        "query_intent": live_query.intent,
        "query": live_query.query,
        "source_type": alert.source_type,
        "provider": alert.provider,
        "published_at": alert.published_at,
        "title": alert.title,
        "snippet": alert.snippet,
        "original_url": alert.original_url,
        "content_hash": alert.content_hash,
        "model_version": response.model_version,
        "predicted_stock_code": response.stock_code,
        "predicted_stock_name": response.stock_name,
        "stock_match_confidence": response.stock_match_confidence,
        "related_stocks": related_stocks,
        "sampled_stock_primary_matched": sampled_stock_primary_matched,
        "sampled_stock_related_matched": sampled_stock_related_matched,
        "sampled_stock_model_matched": (
            sampled_stock_primary_matched or sampled_stock_related_matched
        ),
        "sampled_stock_text_matched": _stock_text_matched(alert, live_query.sampled_stock_name),
        "predicted_event_tags": response.event_tags,
        "event_probabilities": event_probabilities,
        "event_top_label": event_top_label,
        "event_top_confidence": event_top_confidence,
        "event_confidence": response.event_confidence,
        "predicted_sentiment": response.sentiment,
        "sentiment_probabilities": sentiment_probabilities,
        "sentiment_top_label": sentiment_top_label,
        "sentiment_top_confidence": sentiment_top_confidence,
        "sentiment_confidence": response.sentiment_confidence,
        "predicted_importance": response.importance,
        "importance_probabilities": importance_probabilities,
        "importance_top_label": importance_top_label,
        "importance_top_confidence": importance_top_confidence,
        "importance_confidence": response.importance_confidence,
        "final_stock_code": "",
        "final_tags": [],
        "final_sentiment": "",
        "final_importance": "",
        "reviewer_id": "",
        "reviewed_at": "",
    }


def _sample_stocks(
    stock_universe: Sequence[StockUniverseEntry],
    stock_sample_size: int,
    seed: int,
) -> list[StockUniverseEntry]:
    eligible = [stock for stock in stock_universe if stock.stock_code and stock.stock_name]
    if stock_sample_size >= len(eligible):
        return eligible
    ranked = sorted(
        eligible,
        key=lambda stock: sha256(f"{seed}:{stock.stock_code}".encode()).hexdigest(),
    )
    return ranked[:stock_sample_size]


def _stock_text_matched(alert: RawCollectedAlert, stock_name: str) -> bool:
    normalized_name = normalize_stock_term(stock_name)
    return bool(normalized_name and normalized_name in normalize_stock_term(alert.text))


def _top_label(probabilities: dict[str, float]) -> tuple[str, float]:
    if not probabilities:
        return "", 0.0
    label, probability = max(probabilities.items(), key=lambda item: item[1])
    return label, round(probability, 6)


def _provider_status_totals(statuses: Sequence[ProviderCollectionStatus]) -> dict[str, Any]:
    totals = Counter[str]()
    errors: list[str] = []
    completed = True
    providers = sorted({status.provider for status in statuses})
    for status in statuses:
        totals["attempted_requests"] += status.attempted_requests
        totals["successful_requests"] += status.successful_requests
        totals["rate_limited_requests"] += status.rate_limited_requests
        totals["failed_requests"] += status.failed_requests
        totals["collected_count"] += status.collected_count
        completed = completed and status.completed
        errors.extend(status.errors)

    return {
        "providers": providers,
        "completed": completed,
        "attempted_requests": totals["attempted_requests"],
        "successful_requests": totals["successful_requests"],
        "rate_limited_requests": totals["rate_limited_requests"],
        "failed_requests": totals["failed_requests"],
        "collected_count": totals["collected_count"],
        "errors": errors,
    }


def _confidence_summary(rows: Sequence[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        field: _numeric_summary(
            [
                float(value)
                for row in rows
                if isinstance((value := row.get(field)), (int, float))
                and not isinstance(value, bool)
            ]
        )
        for field in LIVE_NEWS_CONFIDENCE_FIELDS
    }


def _numeric_summary(values: Sequence[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "average": None, "minimum": None, "maximum": None}
    return {
        "count": len(values),
        "average": round(sum(values) / len(values), 6),
        "minimum": round(min(values), 6),
        "maximum": round(max(values), 6),
    }


def _confidence_summary_present(live_report: dict[str, Any]) -> bool:
    summary = live_report.get("confidence_summary")
    if not isinstance(summary, dict):
        return False
    for field in LIVE_NEWS_CONFIDENCE_FIELDS:
        field_summary = summary.get(field)
        if not isinstance(field_summary, dict):
            return False
        if int(field_summary.get("count") or 0) <= 0:
            return False
    return True


def _monitoring_required_action(overall_status: str) -> str:
    if overall_status == "pass":
        return "추가 조치 없음. 최신 release 기준 실시간 뉴스 smoke/drift 리포트가 유효하다."
    if overall_status == "stale":
        return (
            "Naver credential이 있는 운영 환경에서 "
            "scripts/build_live_news_evaluation_batch.py를 재실행한 뒤 "
            "scripts/build_live_news_monitoring_status.py로 최신성 상태를 갱신한다."
        )
    return (
        "리포트는 최신 모델 기준이지만 confidence summary 또는 row 수가 부족하므로 "
        "실시간 뉴스 표본 수집 상태를 확인한다."
    )
