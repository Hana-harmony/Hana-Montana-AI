import logging
import threading
import urllib.parse
import urllib.request
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from hannah_montana_ai.api.common import FieldErrorDetail, error_response
from hannah_montana_ai.api.exceptions import ApiException, ErrorCode
from hannah_montana_ai.api.routes import router, warm_runtime_dependencies
from hannah_montana_ai.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    threading.Thread(
        target=_warm_runtime_dependencies,
        name="hannah-runtime-warmup",
        daemon=True,
    ).start()
    yield


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


def create_app() -> FastAPI:
    app = FastAPI(
        title="Hannah-Montana-AI",
        version="0.1.0",
        docs_url="/docs",
        redoc_url=None,
        lifespan=lifespan,
    )

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
        if _translation_provider_ready(get_settings()):
            return JSONResponse(status_code=200, content={"status": "ready"})
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "dependency": "korean_translation_llm"},
        )

    app.include_router(
        router,
        prefix="/api/v1",
    )
    return app


app = create_app()
