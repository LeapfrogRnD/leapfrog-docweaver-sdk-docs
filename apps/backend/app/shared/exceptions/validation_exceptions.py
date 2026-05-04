"""Validation-related exceptions."""

from app.shared.constants.error_codes import ErrorCodes
from app.shared.constants.error_messages import ErrorMessages
from app.shared.constants.http_status import HTTPStatus
from app.shared.exceptions.base import AppException


class ValidationException(AppException):
    """Base exception for validation errors."""

    status_code = HTTPStatus.BAD_REQUEST


class InvalidFileTypeError(ValidationException):
    """Raised when file type is not allowed."""

    error_code = ErrorCodes.INVALID_FILE_TYPE
    message = ErrorMessages.INVALID_FILE_TYPE


class FileSizeExceededError(ValidationException):
    """Raised when file size exceeds the limit."""

    error_code = ErrorCodes.FILE_SIZE_EXCEEDED
    status_code = HTTPStatus.PAYLOAD_TOO_LARGE

    def __init__(self, max_size_mb: int | None = None):
        from app.shared.constants.app_constants import FileConstants

        max_size = max_size_mb or FileConstants.MAX_FILE_SIZE_MB
        message = ErrorMessages.FILE_SIZE_EXCEEDED.format(max_size=max_size)
        super().__init__(message=message)


class PageLimitExceededError(ValidationException):
    """Raised when PDF has too many pages."""

    error_code = ErrorCodes.PAGE_LIMIT_EXCEEDED

    def __init__(self, max_pages: int | None = None):
        from app.shared.constants.app_constants import FileConstants

        pages = max_pages or FileConstants.MAX_PAGES
        message = ErrorMessages.PAGE_LIMIT_EXCEEDED.format(max_pages=pages)
        super().__init__(message=message)


class EmptyFileError(ValidationException):
    """Raised when uploaded file is empty."""

    error_code = ErrorCodes.EMPTY_FILE
    message = ErrorMessages.EMPTY_FILE


class FileReadError(ValidationException):
    """Raised when file cannot be read."""

    error_code = ErrorCodes.FILE_READ_FAILED
    message = ErrorMessages.FILE_READ_FAILED


class InvalidTaskTypeError(ValidationException):
    """Raised when task type is invalid."""

    error_code = ErrorCodes.INVALID_TASK_TYPE

    def __init__(self, expected: str, actual: str):
        message = ErrorMessages.INVALID_TASK_TYPE.format(expected=expected, actual=actual)
        super().__init__(message=message)


class InvalidConfigError(ValidationException):
    """Raised when configuration is invalid."""

    error_code = ErrorCodes.INVALID_CONFIG
    message = ErrorMessages.INVALID_CONFIG


class InvalidSchemaError(ValidationException):
    """Raised when schema is invalid."""

    error_code = ErrorCodes.INVALID_SCHEMA
    message = ErrorMessages.INVALID_SCHEMA


class InvalidJSONError(ValidationException):
    """Raised when JSON parsing fails."""

    error_code = ErrorCodes.INVALID_JSON

    def __init__(self, detail: str):
        message = ErrorMessages.INVALID_JSON.format(detail=detail)
        super().__init__(message=message, detail=detail)


class MissingRequiredFieldError(ValidationException):
    """Raised when a required field is missing."""

    error_code = ErrorCodes.MISSING_REQUIRED_FIELD

    def __init__(self, field_name: str):
        message = f"Required field '{field_name}' is missing."
        super().__init__(message=message)
