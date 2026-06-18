from enum import Enum


class ErrorCode(Enum):
    INVALID_REQUEST = (400, "COMMON_001", "Invalid request")
    VALIDATION_FAILED = (422, "COMMON_002", "Request validation failed")
    INTERNAL_SERVER_ERROR = (500, "COMMON_999", "Internal server error")
    MODEL_UNAVAILABLE = (503, "AI_001", "AI model is unavailable")

    def __init__(self, status: int, code: str, message: str) -> None:
        self.status = status
        self.code = code
        self.message = message


class ApiException(Exception):
    def __init__(self, error_code: ErrorCode, message: str | None = None) -> None:
        self.error_code = error_code
        self.message = message or error_code.message
        super().__init__(self.message)
