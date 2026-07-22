import logging
import threading
import time
import urllib.parse
import urllib.request
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from hannah_montana_ai.api.common import FieldErrorDetail, error_response
from hannah_montana_ai.api.exceptions import ApiException, ErrorCode
from hannah_montana_ai.api.routes import get_analyzer, router, warm_runtime_dependencies
from hannah_montana_ai.core.config import Settings, get_settings
from hannah_montana_ai.observability import (
    HTTP_DURATION,
    HTTP_REQUESTS,
    configure_observability,
)
from hannah_montana_ai.runtime_workloads import tax_ocr_executor
from hannah_montana_ai.services.model import ModelArtifactError

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    threading.Thread(
        target=_warm_runtime_dependencies,
        name="hannah-runtime-warmup",
        daemon=True,
    ).start()
    try:
        yield
    finally:
        tax_ocr_executor.shutdown()


def _warm_runtime_dependencies() -> None:
    try:
        warm_runtime_dependencies()
    except Exception:
        logger.exception("Runtime dependency warmup failed")


def _translation_provider_ready(settings: Settings) -> bool:
    endpoint = settings.korean_translation_llm_endpoint.rstrip("/")
    if not endpoint:
        return False
    parsed = urllib.parse.urlparse(endpoint)
    if parsed.scheme not in {"http", "https"}:
        return False
    try:
        with urllib.request.urlopen(  # noqa: S310  # nosec B310
            f"{endpoint}/health",
            timeout=2.0,
        ) as response:
            return bool(response.status == 200)
    except (OSError, ValueError):
        return False


def _sentiment_release_ready(settings: Settings) -> bool:
    current = settings.sentiment_release_current_path
    release_required = (
        settings.sentiment_release_required or current.exists() or current.is_symlink()
    )
    if not release_required:
        return True
    try:
        model = get_analyzer().sentiment_transformer
    except ModelArtifactError:
        return False
    return bool(model.enabled and model.release_id)


def create_app() -> FastAPI:
    settings = get_settings()
    configure_observability(settings.discord_webhook_url, settings.runtime_environment)
    app = FastAPI(
        title="Hannah-Montana-AI",
        version="0.1.0",
        docs_url="/docs",
        redoc_url=None,
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def observe_http(request: Request, call_next: RequestResponseEndpoint) -> Response:
        started = time.perf_counter()
        response = await call_next(request)
        route = request.scope.get("route")
        path = getattr(route, "path", "unmatched")
        HTTP_REQUESTS.labels(
            method=request.method,
            path=path,
            status=str(response.status_code),
        ).inc()
        HTTP_DURATION.labels(method=request.method, path=path).observe(
            time.perf_counter() - started
        )
        return response

    @app.exception_handler(ApiException)
    async def api_exception_handler(_request: Request, exception: ApiException) -> JSONResponse:
        error_code = exception.error_code
        return JSONResponse(
            status_code=error_code.status,
            content=error_response(
                status=error_code.status,
                code=error_code.code,
                message=exception.message,
            ).model_dump(mode="json"),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request,
        exception: RequestValidationError,
    ) -> JSONResponse:
        error_code = ErrorCode.VALIDATION_FAILED
        errors = [
            FieldErrorDetail(
                field=".".join(str(part) for part in error["loc"]),
                reason=error["msg"],
            )
            for error in exception.errors()
        ]
        return JSONResponse(
            status_code=error_code.status,
            content=error_response(
                status=error_code.status,
                code=error_code.code,
                message=error_code.message,
                errors=errors,
            ).model_dump(mode="json"),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_request: Request, _exception: Exception) -> JSONResponse:
        error_code = ErrorCode.INTERNAL_SERVER_ERROR
        logger.error(
            "Unhandled request failure",
            exc_info=(type(_exception), _exception, _exception.__traceback__),
        )
        return JSONResponse(
            status_code=error_code.status,
            content=error_response(
                status=error_code.status,
                code=error_code.code,
                message=error_code.message,
            ).model_dump(mode="json"),
        )

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready", tags=["system"])
    def readiness() -> JSONResponse:
        current_settings = get_settings()
        if not _sentiment_release_ready(current_settings):
            return JSONResponse(
                status_code=503,
                content={"status": "not_ready", "dependency": "sentiment_release"},
            )
        if _translation_provider_ready(current_settings):
            return JSONResponse(status_code=200, content={"status": "ready"})
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "dependency": "korean_translation_llm"},
        )

    @app.get("/metrics", include_in_schema=False)
    def metrics() -> Response:
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    app.include_router(
        router,
        prefix="/api/v1",
    )
    return app


app = create_app()
