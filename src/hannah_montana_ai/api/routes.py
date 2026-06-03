from functools import lru_cache

from fastapi import APIRouter, HTTPException, status

from hannah_montana_ai.domain.schemas import AlertAnalysisRequest, AlertAnalysisResponse
from hannah_montana_ai.services.analyzer import AlertAnalyzer
from hannah_montana_ai.services.model import ModelArtifactError

router = APIRouter(tags=["analysis"])


@lru_cache
def get_analyzer() -> AlertAnalyzer:
    return AlertAnalyzer()


@router.post("/alerts/analyze", response_model=AlertAnalysisResponse)
def analyze_alert(request: AlertAnalysisRequest) -> AlertAnalysisResponse:
    try:
        analyzer = get_analyzer()
    except ModelArtifactError as exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML model artifact is unavailable",
        ) from exception
    return analyzer.analyze(request)
