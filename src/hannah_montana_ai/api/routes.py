from functools import lru_cache
from time import perf_counter

from fastapi import APIRouter, Header

from hannah_montana_ai.api.common import ApiResponse, success_response
from hannah_montana_ai.api.exceptions import ApiException, ErrorCode
from hannah_montana_ai.core.config import get_settings
from hannah_montana_ai.domain.schemas import (
    AlertAnalysisRequest,
    AlertAnalysisResponse,
    ForeignOwnershipQuantityRetrainRequest,
    ForeignOwnershipQuantityRetrainResponse,
    ForeignOwnershipTimeseriesPredictionRequest,
    ForeignOwnershipTimeseriesPredictionResponse,
    GlobalPeerMatchRequest,
    GlobalPeerMatchResponse,
    IntelligenceEventRequest,
    IntelligenceEventResponse,
    KoreanFinancialTermExplainRequest,
    KoreanFinancialTermExplainResponse,
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
from hannah_montana_ai.services.foreign_ownership import (
    ForeignOwnershipTimeseriesPredictionService,
)
from hannah_montana_ai.services.foreign_ownership_model_maintenance import (
    ForeignOwnershipModelMaintenanceService,
)
from hannah_montana_ai.services.global_peer_explainer import GlobalPeerExplanationGenerator
from hannah_montana_ai.services.global_peer_matcher import GlobalPeerMatcher
from hannah_montana_ai.services.korean_financial_terms import (
    KoreanFinancialTermExplanationService,
    build_openai_term_provider_from_settings,
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
def get_foreign_ownership_prediction_service() -> ForeignOwnershipTimeseriesPredictionService:
    return ForeignOwnershipTimeseriesPredictionService()


@lru_cache
def get_foreign_ownership_model_maintenance_service() -> ForeignOwnershipModelMaintenanceService:
    return ForeignOwnershipModelMaintenanceService()


@lru_cache
def get_global_peer_matcher() -> GlobalPeerMatcher:
    settings = get_settings()
    return GlobalPeerMatcher(
        settings.global_peer_model_path,
        explainer=GlobalPeerExplanationGenerator.from_settings(settings),
    )


@lru_cache
def get_korean_financial_term_service() -> KoreanFinancialTermExplanationService:
    settings = get_settings()
    return KoreanFinancialTermExplanationService(
        seed_path=settings.korean_financial_terms_seed_path,
        model_version=settings.korean_financial_term_model_version,
        provider=build_openai_term_provider_from_settings(settings),
    )


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
    "/market/foreign-ownership/predict",
    response_model=ApiResponse[ForeignOwnershipTimeseriesPredictionResponse],
)
def predict_foreign_ownership(
    request: ForeignOwnershipTimeseriesPredictionRequest,
) -> ApiResponse[ForeignOwnershipTimeseriesPredictionResponse]:
    return success_response(get_foreign_ownership_prediction_service().predict(request))


@router.post(
    "/market/foreign-ownership/model/retrain",
    response_model=ApiResponse[ForeignOwnershipQuantityRetrainResponse],
)
def retrain_foreign_ownership_quantity_model(
    request: ForeignOwnershipQuantityRetrainRequest,
    x_hannah_ai_maintenance_token: str | None = Header(default=None),
) -> ApiResponse[ForeignOwnershipQuantityRetrainResponse]:
    _verify_maintenance_token(x_hannah_ai_maintenance_token)
    try:
        response = get_foreign_ownership_model_maintenance_service().retrain(
            request,
            reload_model=True,
        )
    except ValueError as exception:
        raise ApiException(ErrorCode.INVALID_REQUEST, str(exception)) from exception
    if response.promoted:
        get_foreign_ownership_prediction_service.cache_clear()
    return success_response(response)


@router.post(
    "/market/global-peers/match",
    response_model=ApiResponse[GlobalPeerMatchResponse],
)
def match_global_peer(request: GlobalPeerMatchRequest) -> ApiResponse[GlobalPeerMatchResponse]:
    try:
        matcher = get_global_peer_matcher()
    except ModelArtifactError as exception:
        raise ApiException(
            ErrorCode.MODEL_UNAVAILABLE,
            "Global peer model artifact is unavailable",
        ) from exception
    return success_response(matcher.match(request))


@router.post(
    "/korean-financial-terms/explain",
    response_model=ApiResponse[KoreanFinancialTermExplainResponse],
)
def explain_korean_financial_term(
    request: KoreanFinancialTermExplainRequest,
) -> ApiResponse[KoreanFinancialTermExplainResponse]:
    return success_response(get_korean_financial_term_service().explain(request))


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


def _verify_maintenance_token(header_token: str | None) -> None:
    expected_token = get_settings().foreign_ownership_maintenance_token
    if not expected_token:
        return
    if header_token != expected_token:
        raise ApiException(ErrorCode.UNAUTHORIZED, "Invalid Hannah AI maintenance token")
