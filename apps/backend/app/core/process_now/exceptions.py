"""Process-now domain exceptions."""

from app.shared.constants.error_codes import ErrorCodes
from app.shared.constants.http_status import HTTPStatus
from app.shared.exceptions.base import AppException


class ProcessingTimeoutException(AppException):
    """Raised when synchronous processing exceeds the allowed time budget."""

    status_code = HTTPStatus.TOO_MANY_REQUESTS  # 429 — caller should retry async
    error_code = "ERR_PROCESSING_TIMEOUT"

    def __init__(self, timeout_seconds: int):
        super().__init__(
            message=f"Document processing did not complete within the {timeout_seconds}s time limit. "
            "Consider using the async integration API for large documents."
        )


class UnsupportedTaskTypeException(AppException):
    """Raised when an unrecognised task type is requested."""

    status_code = HTTPStatus.BAD_REQUEST
    error_code = ErrorCodes.INVALID_TASK_TYPE

    def __init__(self, task_type: str, valid_types: list[str]):
        super().__init__(
            message=f"Unsupported task type '{task_type}'. Must be one of: {', '.join(valid_types)}."
        )


class InactivePipelineException(AppException):
    """Raised when the referenced pipeline is inactive."""

    status_code = HTTPStatus.BAD_REQUEST
    error_code = ErrorCodes.BAD_REQUEST

    def __init__(self, pipeline_id: int):
        super().__init__(message=f"Pipeline {pipeline_id} is inactive and cannot be used.")


class DocumentProcessingException(AppException):
    """Raised when the LeapFrog DocWeaver SDK itself fails during inline processing."""

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    error_code = ErrorCodes.PIPELINE_EXECUTION_FAILED

    def __init__(self, detail: str):
        super().__init__(
            message="Document processing failed during inline execution.",
            detail=detail,
        )
