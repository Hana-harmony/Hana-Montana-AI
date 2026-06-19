from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, cast

from hannah_montana_ai.domain.schemas import (
    Importance,
    IntelligenceEventRequest,
    IntelligenceEventResponse,
    Sentiment,
    SourceType,
)
from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.services.feature_contracts import IntelligenceEventService

TRANSLATION_SAMPLE_REPORT_SCHEMA_VERSION = "translation-sample-report/v1"
DEFAULT_TRANSLATION_SAMPLE_LIMIT_PER_SOURCE = 5


@dataclass(frozen=True)
class TranslationGoldSample:
    source_type: SourceType
    text: str
    tags: list[str]
    sentiment: Sentiment
    importance: Importance
    source_url: str
    provider: str
    stock_code: str | None = None
    stock_name: str | None = None
    review_note: str = ""


def build_translation_sample_report(
    *,
    news_gold_path: Path,
    disclosure_gold_path: Path,
    sample_limit_per_source: int = DEFAULT_TRANSLATION_SAMPLE_LIMIT_PER_SOURCE,
    analyzer: AlertAnalyzer | None = None,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    timestamp = (generated_at or datetime.now(UTC)).isoformat()
    effective_analyzer = analyzer or AlertAnalyzer()
    service = IntelligenceEventService(effective_analyzer)
    samples = [
        *_load_gold_samples(
            news_gold_path,
            source_type="NEWS",
            provider="naver-news",
            sample_limit=sample_limit_per_source,
        ),
        *_load_gold_samples(
            disclosure_gold_path,
            source_type="DISCLOSURE",
            provider="opendart",
            sample_limit=sample_limit_per_source,
        ),
    ]
    rows = [
        _build_translation_sample_row(
            sample=sample,
            response=service.build_response(_request_from_sample(sample)),
        )
        for sample in samples
    ]

    return {
        "schema_version": TRANSLATION_SAMPLE_REPORT_SCHEMA_VERSION,
        "generated_at": timestamp,
        "news_gold_path": _report_path(news_gold_path),
        "disclosure_gold_path": _report_path(disclosure_gold_path),
        "sample_limit_per_source": sample_limit_per_source,
        "sample_count": len(rows),
        "summary": _summary(rows),
        "external_translation_boundary": {
            "deepl": "Hana-OmniLens-API live adapter",
            "papago": "legacy provider, not called by Hannah-Montana-AI",
            "join_key": "external_translation_join_key",
        },
        "rows": rows,
    }


def report_to_json(report: dict[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2) + "\n"


def _load_gold_samples(
    path: Path,
    *,
    source_type: SourceType,
    provider: str,
    sample_limit: int,
) -> list[TranslationGoldSample]:
    samples: list[TranslationGoldSample] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        payload = json.loads(line)
        samples.append(
            TranslationGoldSample(
                source_type=source_type,
                text=str(payload["text"]),
                tags=[str(tag) for tag in payload["tags"]],
                sentiment=cast(Sentiment, payload["sentiment"]),
                importance=cast(Importance, payload["importance"]),
                source_url=str(payload["source_url"]),
                provider=provider,
                stock_code=payload.get("stock_code"),
                stock_name=payload.get("stock_name"),
                review_note=str(payload.get("review_note", "")),
            )
        )
        if len(samples) >= sample_limit:
            break
    return samples


def _request_from_sample(sample: TranslationGoldSample) -> IntelligenceEventRequest:
    stock_universe: list[dict[str, Any]] = []
    if sample.stock_code and sample.stock_name:
        stock_universe.append(
            {
                "stock_code": sample.stock_code,
                "stock_name": sample.stock_name,
                "stock_name_en": sample.stock_name,
            }
        )
    return IntelligenceEventRequest.model_validate(
        {
            "source_type": sample.source_type,
            "title": sample.text,
            "snippet": "",
            "original_url": sample.source_url,
            "provider": sample.provider,
            "published_at": "",
            "target_language": "en",
            "stock_universe": stock_universe,
        }
    )


def _build_translation_sample_row(
    *,
    sample: TranslationGoldSample,
    response: IntelligenceEventResponse,
) -> dict[str, Any]:
    comparison = _comparison(sample, response)
    return {
        "sample_id": _sample_id(sample),
        "external_translation_join_key": _sample_id(sample),
        "source_type": sample.source_type,
        "provider": sample.provider,
        "original_url": sample.source_url,
        "original_text": sample.text,
        "expected": {
            "tags": sample.tags,
            "sentiment": sample.sentiment,
            "importance": sample.importance,
            "stock_code": sample.stock_code,
            "stock_name": sample.stock_name,
            "review_note": sample.review_note,
        },
        "translation": {
            "provider": response.translation_provider,
            "model_version": response.translation_model_version,
            "status": response.translation_status,
            "translated_title": response.translated_title,
            "translated_summary": response.translated_summary,
            "glossary_terms": [
                term.model_dump(mode="json") for term in response.glossary_terms
            ],
            "quality_flags": response.translation_quality_flags,
        },
        "ai_analysis": {
            "model_version": response.model_version,
            "stock_code": response.stock_code,
            "stock_name": response.stock_name,
            "event_tags": response.event_tags,
            "sentiment": response.sentiment,
            "importance": response.importance,
            "summary": response.summary,
            "duplicate_key": response.duplicate_key,
        },
        "comparison": comparison,
        "review_findings": _review_findings(comparison, response),
    }


def _comparison(
    sample: TranslationGoldSample,
    response: IntelligenceEventResponse,
) -> dict[str, Any]:
    missing_tags = sorted(set(sample.tags) - set(response.event_tags))
    extra_tags = sorted(set(response.event_tags) - set(sample.tags))
    return {
        "expected_tags_missing_from_ai": missing_tags,
        "ai_extra_tags": extra_tags,
        "sentiment_match": response.sentiment == sample.sentiment,
        "importance_match": response.importance == sample.importance,
        "stock_match": (
            sample.stock_code is None
            or response.stock_code == sample.stock_code
            or sample.stock_code in response.related_stocks
        ),
    }


def _review_findings(
    comparison: dict[str, Any],
    response: IntelligenceEventResponse,
) -> list[str]:
    findings: list[str] = []
    if response.translation_status == "SOURCE_LANGUAGE_FALLBACK":
        findings.append("SOURCE_LANGUAGE_FALLBACK_REVIEW_REQUIRED")
    findings.extend(flag for flag in response.translation_quality_flags if "REVIEW" in flag)
    if response.news_disclosure_type == "DISCLOSURE" and not response.glossary_terms:
        findings.append("DISCLOSURE_GLOSSARY_CANDIDATE_REVIEW_REQUIRED")
    if comparison["expected_tags_missing_from_ai"]:
        findings.append("EVENT_TAG_REVIEW_REQUIRED")
    if not comparison["sentiment_match"]:
        findings.append("SENTIMENT_REVIEW_REQUIRED")
    if not comparison["importance_match"]:
        findings.append("IMPORTANCE_REVIEW_REQUIRED")
    if not comparison["stock_match"]:
        findings.append("STOCK_MAPPING_REVIEW_REQUIRED")
    return list(dict.fromkeys(findings))


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    quality_flags = Counter[str](
        flag
        for row in rows
        for flag in row["translation"]["quality_flags"]
    )
    review_findings = Counter[str](
        finding
        for row in rows
        for finding in row["review_findings"]
    )
    return {
        "source_type_counts": dict(Counter(row["source_type"] for row in rows)),
        "translation_status_counts": dict(
            Counter(row["translation"]["status"] for row in rows)
        ),
        "quality_flag_counts": dict(quality_flags),
        "review_finding_counts": dict(review_findings),
        "glossary_applied_count": sum(
            1 for row in rows if row["translation"]["glossary_terms"]
        ),
        "ai_analysis_clean_match_count": sum(
            1
            for row in rows
            if not row["comparison"]["expected_tags_missing_from_ai"]
            and row["comparison"]["sentiment_match"]
            and row["comparison"]["importance_match"]
            and row["comparison"]["stock_match"]
        ),
    }


def _sample_id(sample: TranslationGoldSample) -> str:
    return sha256(
        f"{sample.source_type}:{sample.text}:{sample.source_url}".encode()
    ).hexdigest()


def _report_path(path: Path) -> str:
    resolved_path = path.resolve()
    try:
        return str(resolved_path.relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)
