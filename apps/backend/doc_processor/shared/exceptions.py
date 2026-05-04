"""Validation-related exceptions."""

from shared.constants.app_error_codes import WorkerStatus
from shared.constants.error_codes import ErrorCodes
from shared.constants.error_messages import ErrorMessages

"""Base exception class for the application."""


class AppException(Exception):  # noqa: N818
    """Base exception for all application errors."""

    error_code: str = ErrorCodes.UNKNOWN_ERROR
    message: str = ErrorMessages.UNKNOWN_ERROR
    status_code: int = WorkerStatus.FAILED

    def __init__(self, message: str | None = None, detail: str | None | dict = None):
        self.message = message or self.__class__.message
        self.detail = detail
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convert exception to dictionary for API response."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "detail": self.detail,
        }


class ValidationException(AppException):
    """Base exception for validation errors."""

    status_code = WorkerStatus.SERVICE_UNAVAILABLE


class InvalidFileTypeError(ValidationException):
    """Raised when file type is not allowed."""

    error_code = ErrorCodes.INVALID_FILE_TYPE
    message = ErrorMessages.INVALID_FILE_TYPE


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
