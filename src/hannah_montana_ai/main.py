from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from hannah_montana_ai.api.common import FieldErrorDetail, error_response
from hannah_montana_ai.api.exceptions import ApiException, ErrorCode
from hannah_montana_ai.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Hannah-Montana-AI",
        version="0.1.0",
        docs_url="/docs",
        redoc_url=None,
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

    app.include_router(
        router,
        prefix="/api/v1",
    )
    return app


app = create_app()
