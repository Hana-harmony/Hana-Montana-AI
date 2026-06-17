from functools import lru_cache
from time import perf_counter

from fastapi import APIRouter, HTTPException, status

from hannah_montana_ai.domain.schemas import (
    AlertAnalysisRequest,
    AlertAnalysisResponse,
    IntelligenceEventRequest,
    IntelligenceEventResponse,
    StockOrderStatusRequest,
    StockOrderStatusResponse,
    TaxRefundStatusRequest,
    TaxRefundStatusResponse,
)
from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.services.audit import AnalysisAuditLogger
from hannah_montana_ai.services.feature_contracts import (
    IntelligenceEventService,
    StockOrderStatusService,
    TaxRefundStatusService,
)
from hannah_montana_ai.services.model import ModelArtifactError

router = APIRouter(tags=["analysis"])


@lru_cache
def get_analyzer() -> AlertAnalyzer:
    return AlertAnalyzer()


@lru_cache
def get_audit_logger() -> AnalysisAuditLogger:
    return AnalysisAuditLogger()


@lru_cache
def get_stock_order_status_service() -> StockOrderStatusService:
    return StockOrderStatusService()


@lru_cache
def get_tax_refund_status_service() -> TaxRefundStatusService:
    return TaxRefundStatusService()


@router.post("/alerts/analyze", response_model=AlertAnalysisResponse)
def analyze_alert(request: AlertAnalysisRequest) -> AlertAnalysisResponse:
    started_at = perf_counter()
    audit_logger = get_audit_logger()
    try:
        analyzer = get_analyzer()
    except ModelArtifactError as exception:
        audit_logger.record_failure(
            request=request,
            latency_ms=_elapsed_ms(started_at),
            failure_reason="model_artifact_unavailable",
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML model artifact is unavailable",
        ) from exception
    try:
        response = analyzer.analyze(request)
    except Exception:
        audit_logger.record_failure(
            request=request,
            latency_ms=_elapsed_ms(started_at),
            failure_reason="analysis_error",
        )
        raise

    audit_logger.record_success(
        request=request,
        response=response,
        latency_ms=_elapsed_ms(started_at),
    )
    return response


@router.post("/stocks/order-status", response_model=StockOrderStatusResponse)
def stock_order_status(request: StockOrderStatusRequest) -> StockOrderStatusResponse:
    return get_stock_order_status_service().build_response(request)


@router.post("/intelligence/events", response_model=IntelligenceEventResponse)
def build_intelligence_event(request: IntelligenceEventRequest) -> IntelligenceEventResponse:
    try:
        analyzer = get_analyzer()
    except ModelArtifactError as exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML model artifact is unavailable",
        ) from exception
    return IntelligenceEventService(analyzer).build_response(request)


@router.post("/tax/refund-status", response_model=TaxRefundStatusResponse)
def tax_refund_status(request: TaxRefundStatusRequest) -> TaxRefundStatusResponse:
    return get_tax_refund_status_service().build_response(request)


def _elapsed_ms(started_at: float) -> float:
    return (perf_counter() - started_at) * 1000
