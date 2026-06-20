import json
import logging
from hashlib import sha256
from typing import Literal

from hannah_montana_ai.domain.schemas import AlertAnalysisRequest, AlertAnalysisResponse

AnalysisOutcome = Literal["success", "failure"]


class AnalysisAuditLogger:
    def __init__(self) -> None:
        self.logger = logging.getLogger("hannah_montana_ai.audit.analysis")

    def record_success(
        self,
        request: AlertAnalysisRequest,
        response: AlertAnalysisResponse,
        latency_ms: float,
    ) -> None:
        self._record(
            request=request,
            outcome="success",
            latency_ms=latency_ms,
            model_version=response.model_version,
            stock_code=response.stock_code,
            event_tags=response.event_tags,
            sentiment=response.sentiment,
            importance=response.importance,
            event_confidence=response.event_confidence,
            sentiment_confidence=response.sentiment_confidence,
            importance_confidence=response.importance_confidence,
            stock_match_confidence=response.stock_match_confidence,
            failure_reason=None,
        )

    def record_failure(
        self,
        request: AlertAnalysisRequest,
        latency_ms: float,
        failure_reason: str,
    ) -> None:
        self._record(
            request=request,
            outcome="failure",
            latency_ms=latency_ms,
            model_version=None,
            stock_code=None,
            event_tags=[],
            sentiment=None,
            importance=None,
            event_confidence=None,
            sentiment_confidence=None,
            importance_confidence=None,
            stock_match_confidence=None,
            failure_reason=failure_reason,
        )

    def _record(
        self,
        request: AlertAnalysisRequest,
        outcome: AnalysisOutcome,
        latency_ms: float,
        model_version: str | None,
        stock_code: str | None,
        event_tags: list[str],
        sentiment: str | None,
        importance: str | None,
        event_confidence: float | None,
        sentiment_confidence: float | None,
        importance_confidence: float | None,
        stock_match_confidence: float | None,
        failure_reason: str | None,
    ) -> None:
        payload: dict[str, object] = {
            "event": "analysis_audit",
            "outcome": outcome,
            "source_type": request.source_type,
            "title_hash": self._hash(request.title),
            "snippet_hash": self._hash(request.snippet),
            "original_url_hash": self._hash(str(request.original_url)),
            "stock_universe_size": len(request.stock_universe),
            "latency_ms": round(max(latency_ms, 0.0), 3),
        }
        if model_version is not None:
            payload["model_version"] = model_version
        if stock_code is not None:
            payload["stock_code"] = stock_code
        if event_tags:
            payload["event_tags"] = list(event_tags)
        if sentiment is not None:
            payload["sentiment"] = sentiment
        if importance is not None:
            payload["importance"] = importance
        if event_confidence is not None:
            payload["event_confidence"] = event_confidence
        if sentiment_confidence is not None:
            payload["sentiment_confidence"] = sentiment_confidence
        if importance_confidence is not None:
            payload["importance_confidence"] = importance_confidence
        if stock_match_confidence is not None:
            payload["stock_match_confidence"] = stock_match_confidence
        if failure_reason is not None:
            payload["failure_reason"] = failure_reason

        self.logger.info(json.dumps(payload, ensure_ascii=False, sort_keys=True))

    def _hash(self, value: str) -> str:
        return sha256(value.encode("utf-8")).hexdigest()
