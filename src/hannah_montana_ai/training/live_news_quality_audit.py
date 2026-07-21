from __future__ import annotations

import json
import re
from collections import Counter
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol, cast

from hannah_montana_ai.domain.schemas import (
    AlertAnalysisRequest,
    AlertAnalysisResponse,
    IntelligenceEventRequest,
    IntelligenceEventResponse,
    StockCandidate,
)
from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.services.feature_contracts import IntelligenceEventService
from hannah_montana_ai.services.rule_engine import FinancialRuleEngine
from hannah_montana_ai.training.collector import (
    ProviderCollectionStatus,
    RawCollectionResult,
    collect_naver_news,
)
from hannah_montana_ai.training.live_news_evaluation import (
    DEFAULT_LIVE_NEWS_INTENTS,
    LiveNewsQuery,
    build_live_news_queries,
)
from hannah_montana_ai.training.stock_universe import StockUniverseEntry, normalize_stock_term
from hannah_montana_ai.training.weak_labeler import RawCollectedAlert

LIVE_NEWS_QUALITY_AUDIT_ROW_SCHEMA_VERSION = "live-news-quality-audit-row/v1"
LIVE_NEWS_QUALITY_AUDIT_REPORT_SCHEMA_VERSION = "live-news-quality-audit-report/v1"
STOCK_ATTRIBUTION_CONTEXT_TERMS = ("연구원", "애널리스트", "리서치", "센터장")
SHORT_STOCK_MEDIA_CONTEXT_TERMS = (
    "biz",
    "medianet",
    "sbsi",
    "뉴스",
    "스포츠",
    "기자",
    "앵커",
    "에따르면",
    "보도",
    "방송보도",
    "드라마",
    "금토드라마",
    "금토극",
    "그것이알고싶다",
    "사옥",
    "제작발표회",
    "sidebyside",
    "사이드바이사이드",
)
FINANCIAL_RELEVANCE_TERMS = (
    "주가",
    "주식",
    "증시",
    "상장",
    "공시",
    "계약",
    "공급",
    "수주",
    "매출",
    "영업이익",
    "실적",
    "투자",
    "지분",
    "인수",
    "매각",
    "배당",
    "증권",
    "거래",
    "금융",
    "코스피",
    "코스닥",
    "KOSPI",
    "KOSDAQ",
)
SUMMARY_HALLUCINATION_TERMS = (
    "golden electric group",
    "electronicstronics",
    "investor impact is better than expected",
    "korean basis on a korean scale",
    "more orders placed on the market",
    "reported event",
    "market sentiment and investor positioning",
    "the next disclosure and market reaction",
    "as the story develops",
    "samsung exosphate",
)
TRANSLATED_CONTENT_HALLUCINATION_TERMS = (
    "kb semaphore",
    "newhan bank",
    "nhan bank",
    "korean exporters",
    "highest bidder",
)
TRANSLATION_CRITICAL_FLAG_PREFIXES = (
    "QWEN_TRANSLATION_SEMANTIC_MISMATCH",
    "QWEN_TRANSLATION_META_OR_REFUSAL_TEXT",
    "QWEN_TRANSLATION_REPEATED_TRANSLATION_PHRASE",
    "QWEN_TRANSLATION_SOURCE_TERM_MISSING",
    "QWEN_TRANSLATION_HANGUL_REMAINS",
    "QWEN_TRANSLATION_LOCAL_TRANSLATION_PROVIDER_ERROR",
)


class AnalyzerLike(Protocol):
    model: Any

    def analyze(self, request: AlertAnalysisRequest) -> AlertAnalysisResponse:
        ...


class EventBuilderLike(Protocol):
    def build_response(self, request: IntelligenceEventRequest) -> IntelligenceEventResponse:
        ...


@dataclass(frozen=True)
class ArticleContent:
    content: str
    canonical_url: str
    image_urls: list[str]
    source_license_policy: str


@dataclass(frozen=True)
class LiveNewsQualityAuditBatch:
    rows: list[dict[str, Any]]
    report: dict[str, Any]


NewsCollector = Callable[..., RawCollectionResult]
ArticleContentFetcher = Callable[[str, str], ArticleContent | None]


def build_live_news_quality_audit_batch(
    *,
    stock_universe: Sequence[StockUniverseEntry],
    stock_universe_path: Path,
    output_path: Path,
    stock_sample_size: int = 30,
    max_news_per_query: int = 3,
    intents: Sequence[str] = DEFAULT_LIVE_NEWS_INTENTS,
    seed: int = 20260622,
    sleep_seconds: float = 0.2,
    max_retries: int = 2,
    sample_limit: int | None = None,
    analyzer: AnalyzerLike | None = None,
    event_builder: EventBuilderLike | None = None,
    news_collector: NewsCollector = collect_naver_news,
    content_fetcher: ArticleContentFetcher | None = None,
    require_query_stock_match: bool = False,
    generated_at: datetime | None = None,
) -> LiveNewsQualityAuditBatch:
    timestamp = (generated_at or datetime.now(UTC)).isoformat()
    created_analyzer = analyzer or AlertAnalyzer()
    effective_analyzer: AnalyzerLike = cast(AnalyzerLike, created_analyzer)
    effective_event_builder = event_builder
    if effective_event_builder is None and analyzer is None:
        effective_event_builder = IntelligenceEventService(cast(AlertAnalyzer, created_analyzer))
    queries = build_live_news_queries(
        stock_universe,
        stock_sample_size=stock_sample_size,
        intents=intents,
        seed=seed,
    )
    rows: list[dict[str, Any]] = []
    statuses: list[ProviderCollectionStatus] = []
    seen_hashes: set[str] = set()
    filtered_query_stock_absent_count = 0

    uses_event_builder = effective_event_builder is not None
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
            full_content = (
                content_fetcher(alert.original_url, alert.title) if content_fetcher else None
            )
            if require_query_stock_match and not _stock_text_matched(
                alert,
                live_query.sampled_stock_name,
                full_content=full_content,
            ):
                filtered_query_stock_absent_count += 1
                continue
            if require_query_stock_match and not _has_financial_context(
                alert,
                full_content=full_content,
            ):
                continue
            rows.append(
                _build_quality_row(
                    alert=alert,
                    full_content=full_content,
                    live_query=live_query,
                    analyzer=effective_analyzer,
                    event_builder=effective_event_builder,
                    generated_at=timestamp,
                )
            )
            if sample_limit is not None and len(rows) >= sample_limit:
                return _build_batch(
                    rows=rows,
                    statuses=statuses,
                    generated_at=timestamp,
                    model_version=str(effective_analyzer.model.version),
                    stock_universe_path=stock_universe_path,
                    output_path=output_path,
                    requested_stock_sample_size=stock_sample_size,
                    selected_stock_count=len(
                        {query.sampled_stock_code for query in queries}
                    ),
                    query_count=len(queries),
                    filtered_query_stock_absent_count=filtered_query_stock_absent_count,
                    uses_event_builder=uses_event_builder,
                )

    return _build_batch(
        rows=rows,
        statuses=statuses,
        generated_at=timestamp,
        model_version=str(effective_analyzer.model.version),
        stock_universe_path=stock_universe_path,
        output_path=output_path,
        requested_stock_sample_size=stock_sample_size,
        selected_stock_count=len({query.sampled_stock_code for query in queries}),
        query_count=len(queries),
        filtered_query_stock_absent_count=filtered_query_stock_absent_count,
        uses_event_builder=uses_event_builder,
    )


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
    filtered_query_stock_absent_count: int,
    uses_event_builder: bool,
) -> LiveNewsQualityAuditBatch:
    return LiveNewsQualityAuditBatch(
        rows=rows,
        report=build_live_news_quality_audit_report(
            rows=rows,
            statuses=statuses,
            generated_at=generated_at,
            model_version=model_version,
            stock_universe_path=stock_universe_path,
            output_path=output_path,
            requested_stock_sample_size=requested_stock_sample_size,
            selected_stock_count=selected_stock_count,
            query_count=query_count,
            filtered_query_stock_absent_count=filtered_query_stock_absent_count,
            uses_event_builder=uses_event_builder,
        ),
    )


def build_live_news_quality_audit_report(
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
    filtered_query_stock_absent_count: int = 0,
    uses_event_builder: bool = False,
) -> dict[str, Any]:
    finding_counts = Counter[str](
        finding for row in rows for finding in row["quality_findings"]
    )
    emitted_count = len(rows)
    passed_count = sum(1 for row in rows if row["quality_status"] == "pass")
    query_relevant_rows = [
        row for row in rows if "QUERY_STOCK_ABSENT" not in row["quality_findings"]
    ]
    query_relevant_pass_count = sum(
        1 for row in query_relevant_rows if row["quality_status"] == "pass"
    )
    average_score = (
        round(sum(float(row["quality_score"]) for row in rows) / emitted_count, 4)
        if emitted_count
        else 0.0
    )
    stock_matched_count = sum(1 for row in rows if row["sampled_stock_model_matched"])
    full_content_count = sum(1 for row in rows if row["content_availability"] == "FULL_TEXT")
    low_quality_rows = sorted(
        rows,
        key=lambda row: (float(row["quality_score"]), str(row["content_hash"])),
    )[:10]

    return {
        "schema_version": LIVE_NEWS_QUALITY_AUDIT_REPORT_SCHEMA_VERSION,
        "row_schema_version": LIVE_NEWS_QUALITY_AUDIT_ROW_SCHEMA_VERSION,
        "generated_at": generated_at,
        "model_version": model_version,
        "stock_universe_path": _path_for_report(stock_universe_path),
        "output_path": _path_for_report(output_path),
        "requested_stock_sample_size": requested_stock_sample_size,
        "selected_stock_count": selected_stock_count,
        "query_count": query_count,
        "filtered_query_stock_absent_count": filtered_query_stock_absent_count,
        "emitted_row_count": emitted_count,
        "quality_pass_count": passed_count,
        "quality_pass_rate": round(passed_count / emitted_count, 6) if emitted_count else 0.0,
        "query_relevant_row_count": len(query_relevant_rows),
        "query_relevant_quality_pass_count": query_relevant_pass_count,
        "query_relevant_quality_pass_rate": (
            round(query_relevant_pass_count / len(query_relevant_rows), 6)
            if query_relevant_rows
            else 0.0
        ),
        "average_quality_score": average_score,
        "full_content_count": full_content_count,
        "full_content_rate": round(full_content_count / emitted_count, 6)
        if emitted_count
        else 0.0,
        "sampled_stock_model_match_count": stock_matched_count,
        "sampled_stock_model_match_rate": round(stock_matched_count / emitted_count, 6)
        if emitted_count
        else 0.0,
        "quality_finding_counts": dict(sorted(finding_counts.items())),
        "provider_status_totals": _provider_status_totals(statuses),
        "worst_rows": [_compact_worst_row(row) for row in low_quality_rows],
        "policy": {
            "llm_usage": "event_response_path" if uses_event_builder else "disabled",
            "description": (
                "최신 뉴스 품질 감사는 전문 정제, 금융 ML 분류, What/Why/Impact "
                "요약, 영어 번역까지 실제 이벤트 응답 품질을 관측한다."
            ),
        },
    }


def _build_quality_row(
    *,
    alert: RawCollectedAlert,
    full_content: ArticleContent | None,
    live_query: LiveNewsQuery,
    analyzer: AnalyzerLike,
    event_builder: EventBuilderLike | None,
    generated_at: str,
) -> dict[str, Any]:
    content = full_content.content if full_content else ""
    request = IntelligenceEventRequest(
        source_type=alert.source_type,
        title=alert.title,
        snippet=alert.snippet,
        content=content,
        image_urls=full_content.image_urls[:10] if full_content else [],
        canonical_url=full_content.canonical_url if full_content else alert.original_url,
        source_license_policy=full_content.source_license_policy
        if full_content
        else "NAVER_SEARCH_SNIPPET_ONLY",
        original_url=cast(Any, alert.original_url),
        provider=alert.provider,
        published_at=alert.published_at,
        stock_universe=[
            StockCandidate(
                stock_code=live_query.sampled_stock_code,
                stock_name=live_query.sampled_stock_name,
                stock_name_en=live_query.sampled_stock_name,
            )
        ],
    )
    response = (
        event_builder.build_response(request)
        if event_builder is not None
        else analyzer.analyze(request)
    )
    sampled_stock_primary_matched = response.stock_code == live_query.sampled_stock_code
    sampled_stock_related_matched = live_query.sampled_stock_code in response.related_stocks
    sampled_stock_text_matched = _stock_text_matched(
        alert,
        live_query.sampled_stock_name,
        full_content=full_content,
    )
    findings = _quality_findings(
        alert=alert,
        response=response,
        full_content=full_content,
        sampled_stock_text_matched=sampled_stock_text_matched,
        sampled_stock_model_matched=(
            sampled_stock_primary_matched or sampled_stock_related_matched
        ),
        requires_english_output=event_builder is not None,
    )
    score = _quality_score(findings)

    return {
        "schema_version": LIVE_NEWS_QUALITY_AUDIT_ROW_SCHEMA_VERSION,
        "generated_at": generated_at,
        "review_status": "auto_quality_audit",
        "sampled_stock_code": live_query.sampled_stock_code,
        "sampled_stock_name": live_query.sampled_stock_name,
        "query_intent": live_query.intent,
        "query": live_query.query,
        "source_type": alert.source_type,
        "provider": alert.provider,
        "published_at": alert.published_at,
        "title": alert.title,
        "snippet": alert.snippet,
        "content_excerpt": content[:500],
        "original_url": alert.original_url,
        "canonical_url": full_content.canonical_url if full_content else alert.original_url,
        "content_hash": alert.content_hash,
        "content_availability": "FULL_TEXT" if full_content else "SUMMARY_ONLY",
        "source_license_policy": full_content.source_license_policy
        if full_content
        else "NAVER_SEARCH_SNIPPET_ONLY",
        "model_version": response.model_version,
        "predicted_stock_code": response.stock_code,
        "predicted_stock_name": response.stock_name,
        "stock_match_confidence": response.stock_match_confidence,
        "related_stocks": response.related_stocks,
        "sampled_stock_primary_matched": sampled_stock_primary_matched,
        "sampled_stock_related_matched": sampled_stock_related_matched,
        "sampled_stock_model_matched": (
            sampled_stock_primary_matched or sampled_stock_related_matched
        ),
        "sampled_stock_text_matched": sampled_stock_text_matched,
        "summary_lines": response.summary_lines.model_dump(mode="json"),
        "translation_status": getattr(response, "translation_status", ""),
        "translation_provider": getattr(response, "translation_provider", ""),
        "translation_quality_flags": getattr(response, "translation_quality_flags", []),
        "translated_summary": getattr(response, "translated_summary", ""),
        "translated_content_excerpt": getattr(response, "translated_content", "")[:500],
        "predicted_event_tags": response.event_tags,
        "event_confidence": response.event_confidence,
        "predicted_sentiment": response.sentiment,
        "sentiment_confidence": response.sentiment_confidence,
        "predicted_importance": response.importance,
        "importance_confidence": response.importance_confidence,
        "quality_findings": findings,
        "quality_score": score,
        "quality_status": "pass" if score >= 80 and not _has_critical_finding(findings) else "fail",
    }


def _quality_findings(
    *,
    alert: RawCollectedAlert,
    response: AlertAnalysisResponse | IntelligenceEventResponse,
    full_content: ArticleContent | None,
    sampled_stock_text_matched: bool,
    sampled_stock_model_matched: bool,
    requires_english_output: bool = False,
) -> list[str]:
    findings: list[str] = []
    lines = [
        response.summary_lines.what.strip(),
        response.summary_lines.why.strip(),
        response.summary_lines.impact.strip(),
    ]
    line_set = {line for line in lines if line}
    joined_lines = " ".join(lines)

    if full_content is None:
        findings.append("MISSING_FULL_CONTENT")
        if max(
            response.event_confidence,
            response.sentiment_confidence,
            response.importance_confidence,
        ) >= 0.55:
            findings.append("SUMMARY_ONLY_CONFIDENCE_CAPPED")
    if any(not line for line in lines):
        findings.append("SUMMARY_LINE_EMPTY")
    if len(line_set) < len(lines):
        findings.append("SUMMARY_LINE_DUPLICATED")
    if _contains_boilerplate(joined_lines):
        findings.append("SUMMARY_BOILERPLATE")
    if any(term in joined_lines.lower() for term in SUMMARY_HALLUCINATION_TERMS):
        findings.append("SUMMARY_HALLUCINATED_SURFACE")
    if _contains_boilerplate(_quality_content(alert, full_content)):
        findings.append("CONTENT_BOILERPLATE")
    if any(len(line) < 18 for line in lines):
        findings.append("SUMMARY_LINE_TOO_SHORT")
    if response.stock_code is None:
        findings.append("PREDICTED_STOCK_NULL")
    if not sampled_stock_text_matched and not sampled_stock_model_matched:
        findings.append("QUERY_STOCK_ABSENT")
    if sampled_stock_text_matched and not sampled_stock_model_matched:
        findings.append("SAMPLED_STOCK_NOT_MATCHED")
    if response.event_confidence < 0.35:
        findings.append("LOW_EVENT_CONFIDENCE")
    if response.sentiment_confidence < 0.35:
        findings.append("LOW_SENTIMENT_CONFIDENCE")
    if response.importance_confidence < 0.35:
        findings.append("LOW_IMPORTANCE_CONFIDENCE")
    if _is_fallback_line(response.summary_lines.why):
        findings.append("WHY_FALLBACK")
    if _is_fallback_line(response.summary_lines.impact):
        findings.append("IMPACT_FALLBACK")
    if requires_english_output:
        if _contains_hangul(joined_lines):
            findings.append("SUMMARY_LINE_CONTAINS_HANGUL")
        if any(line and not _has_terminal_punctuation(line) for line in lines):
            findings.append("SUMMARY_LINE_NO_TERMINAL_PUNCTUATION")
        if any(line and not _is_single_sentence(line) for line in lines):
            findings.append("SUMMARY_LINE_NOT_ONE_SENTENCE")
        translated_content = getattr(response, "translated_content", "")
        if translated_content and _contains_hangul(translated_content):
            findings.append("TRANSLATED_CONTENT_CONTAINS_HANGUL")
        if _contains_translated_content_hallucinated_surface(translated_content):
            findings.append("TRANSLATED_CONTENT_HALLUCINATED_SURFACE")
        translation_flags = getattr(response, "translation_quality_flags", [])
        if any(
            str(flag).startswith(TRANSLATION_CRITICAL_FLAG_PREFIXES)
            for flag in translation_flags
        ):
            findings.append("TRANSLATION_CRITICAL_REVIEW_FLAG")
        if getattr(response, "translation_status", "") != "TRANSLATED":
            findings.append("TRANSLATION_STATUS_FALLBACK")

    return sorted(set(findings))


def _quality_score(findings: Sequence[str]) -> int:
    penalty = {
        "MISSING_FULL_CONTENT": 8,
        "SUMMARY_ONLY_CONFIDENCE_CAPPED": 6,
        "SUMMARY_LINE_EMPTY": 35,
        "SUMMARY_LINE_DUPLICATED": 22,
        "SUMMARY_BOILERPLATE": 28,
        "SUMMARY_HALLUCINATED_SURFACE": 35,
        "CONTENT_BOILERPLATE": 8,
        "SUMMARY_LINE_TOO_SHORT": 10,
        "PREDICTED_STOCK_NULL": 18,
        "QUERY_STOCK_ABSENT": 15,
        "SAMPLED_STOCK_NOT_MATCHED": 14,
        "LOW_EVENT_CONFIDENCE": 8,
        "LOW_SENTIMENT_CONFIDENCE": 5,
        "LOW_IMPORTANCE_CONFIDENCE": 5,
        "WHY_FALLBACK": 6,
        "IMPACT_FALLBACK": 6,
        "SUMMARY_LINE_CONTAINS_HANGUL": 35,
        "SUMMARY_LINE_NO_TERMINAL_PUNCTUATION": 15,
        "SUMMARY_LINE_NOT_ONE_SENTENCE": 12,
        "TRANSLATED_CONTENT_CONTAINS_HANGUL": 35,
        "TRANSLATED_CONTENT_HALLUCINATED_SURFACE": 35,
        "TRANSLATION_CRITICAL_REVIEW_FLAG": 28,
        "TRANSLATION_STATUS_FALLBACK": 24,
    }
    return max(0, 100 - sum(penalty.get(finding, 0) for finding in findings))


def _has_critical_finding(findings: Sequence[str]) -> bool:
    return any(
        finding
        in {
            "SUMMARY_LINE_EMPTY",
            "SUMMARY_BOILERPLATE",
            "SUMMARY_HALLUCINATED_SURFACE",
            "PREDICTED_STOCK_NULL",
            "QUERY_STOCK_ABSENT",
            "SAMPLED_STOCK_NOT_MATCHED",
            "SUMMARY_LINE_CONTAINS_HANGUL",
            "TRANSLATED_CONTENT_CONTAINS_HANGUL",
            "TRANSLATED_CONTENT_HALLUCINATED_SURFACE",
            "TRANSLATION_CRITICAL_REVIEW_FLAG",
            "TRANSLATION_STATUS_FALLBACK",
        }
        for finding in findings
    )


def _contains_boilerplate(text: str) -> bool:
    return any(keyword in text for keyword in FinancialRuleEngine.boilerplate_keywords)


def _quality_content(
    alert: RawCollectedAlert,
    full_content: ArticleContent | None,
) -> str:
    engine = FinancialRuleEngine()
    if full_content:
        return engine.clean_article_text(full_content.content, alert.title)
    return engine.clean_article_text(alert.text, alert.title)


def _is_fallback_line(text: str) -> bool:
    normalized = text.strip()
    return normalized.startswith("중요도 ") or "최신 시장·기업 이벤트입니다" in normalized


def _contains_hangul(value: str) -> bool:
    return bool(re.search(r"[가-힣]", value))


def _contains_translated_content_hallucinated_surface(value: str) -> bool:
    lowered = value.lower()
    for term in TRANSLATED_CONTENT_HALLUCINATION_TERMS:
        pattern = rf"(?<![a-z]){re.escape(term)}(?![a-z])"
        if re.search(pattern, lowered):
            return True
    return False


def _has_terminal_punctuation(value: str) -> bool:
    return value.rstrip().endswith((".", "!", "?"))


def _is_single_sentence(value: str) -> bool:
    masked = re.sub(r"\b(?:U\.S|U\.K|Co|Inc|Ltd|Corp)\.", "ABBR", value)
    return len(re.findall(r"[.!?](?:\s|$)", masked)) == 1


def _stock_text_matched(
    alert: RawCollectedAlert,
    stock_name: str,
    *,
    full_content: ArticleContent | None = None,
) -> bool:
    normalized_name = normalize_stock_term(stock_name)
    if not normalized_name:
        return False
    text = alert.text
    if full_content:
        text = f"{text} {full_content.content}"
    normalized_text = normalize_stock_term(text)
    start = 0
    while True:
        position = normalized_text.find(normalized_name, start)
        if position < 0:
            return False
        context = normalized_text[
            max(0, position - 24) : position + len(normalized_name) + 24
        ]
        if not _is_stock_attribution_context(context, normalized_name):
            return True
        start = position + len(normalized_name)


def _is_stock_attribution_context(context: str, normalized_name: str) -> bool:
    if any(term in context for term in STOCK_ATTRIBUTION_CONTEXT_TERMS):
        return True
    return (
        normalized_name.isascii()
        and len(normalized_name) <= 3
        and any(term in context for term in SHORT_STOCK_MEDIA_CONTEXT_TERMS)
    )


def _has_financial_context(
    alert: RawCollectedAlert,
    *,
    full_content: ArticleContent | None = None,
) -> bool:
    text = alert.text
    if full_content:
        text = f"{text} {full_content.content[:1200]}"
    return any(term in text for term in FINANCIAL_RELEVANCE_TERMS)


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


def _compact_worst_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "quality_score": row["quality_score"],
        "quality_findings": row["quality_findings"],
        "sampled_stock_name": row["sampled_stock_name"],
        "predicted_stock_name": row["predicted_stock_name"],
        "title": row["title"],
        "original_url": row["original_url"],
        "summary_lines": row["summary_lines"],
        "translation_status": row.get("translation_status", ""),
        "translation_provider": row.get("translation_provider", ""),
    }


def _path_for_report(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)
