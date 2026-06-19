from functools import lru_cache
from time import perf_counter

from fastapi import APIRouter

from hannah_montana_ai.api.common import ApiResponse, success_response
from hannah_montana_ai.api.exceptions import ApiException, ErrorCode
from hannah_montana_ai.domain.schemas import (
    AlertAnalysisRequest,
    AlertAnalysisResponse,
    IntelligenceEventRequest,
    IntelligenceEventResponse,
    StockOrderStatusRequest,
    StockOrderStatusResponse,
    TaxDocumentVerificationRequest,
    TaxDocumentVerificationResponse,
    TaxRefundStatusRequest,
    TaxRefundStatusResponse,
)
from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.services.audit import AnalysisAuditLogger
from hannah_montana_ai.services.feature_contracts import (
    IntelligenceEventService,
    StockOrderStatusService,
    TaxDocumentVerificationService,
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


@lru_cache
def get_tax_document_verification_service() -> TaxDocumentVerificationService:
    return TaxDocumentVerificationService()


@router.post(
    "/alerts/analyze",
    response_model=ApiResponse[AlertAnalysisResponse],
    summary="Analyze Korean stock news or disclosure alert",
    responses={
        422: {"description": "COMMON_002 validation failure"},
        500: {"description": "COMMON_999 unexpected server error"},
        503: {"description": "AI_001 model unavailable"},
    },
)
def analyze_alert(request: AlertAnalysisRequest) -> ApiResponse[AlertAnalysisResponse]:
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
        raise ApiException(
            ErrorCode.MODEL_UNAVAILABLE,
            "ML model artifact is unavailable",
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
    return success_response(response)


@router.post(
    "/stocks/order-status",
    response_model=ApiResponse[StockOrderStatusResponse],
)
def stock_order_status(request: StockOrderStatusRequest) -> ApiResponse[StockOrderStatusResponse]:
    return success_response(get_stock_order_status_service().build_response(request))


@router.post(
    "/intelligence/events",
    response_model=ApiResponse[IntelligenceEventResponse],
)
def build_intelligence_event(
    request: IntelligenceEventRequest,
) -> ApiResponse[IntelligenceEventResponse]:
    try:
        analyzer = get_analyzer()
    except ModelArtifactError as exception:
        raise ApiException(
            ErrorCode.MODEL_UNAVAILABLE,
            "ML model artifact is unavailable",
        ) from exception
    return success_response(IntelligenceEventService(analyzer).build_response(request))


@router.post(
    "/tax/refund-status",
    response_model=ApiResponse[TaxRefundStatusResponse],
)
def tax_refund_status(request: TaxRefundStatusRequest) -> ApiResponse[TaxRefundStatusResponse]:
    return success_response(get_tax_refund_status_service().build_response(request))


@router.post(
    "/tax/documents/verify",
    response_model=ApiResponse[TaxDocumentVerificationResponse],
)
def tax_document_verify(
    request: TaxDocumentVerificationRequest,
) -> ApiResponse[TaxDocumentVerificationResponse]:
    return success_response(get_tax_document_verification_service().build_response(request))


def _elapsed_ms(started_at: float) -> float:
    return (perf_counter() - started_at) * 1000
