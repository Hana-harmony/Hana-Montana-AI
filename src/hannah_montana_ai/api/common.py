from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class FieldErrorDetail(BaseModel):
    field: str
    reason: str


class ApiResponse[T](BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    success: bool
    status: int
    code: str
    message: str
    data: T | None = None
    errors: list[FieldErrorDetail] | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


def success_response[T](data: T) -> ApiResponse[T]:
    return ApiResponse(success=True, status=200, code="COMMON_000", message="OK", data=data)


def error_response(
    *,
    status: int,
    code: str,
    message: str,
    errors: list[FieldErrorDetail] | None = None,
) -> ApiResponse[None]:
    return ApiResponse(
        success=False,
        status=status,
        code=code,
        message=message,
        errors=errors,
    )
