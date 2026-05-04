"""Storage-related exceptions."""

from app.shared.constants.error_codes import ErrorCodes
from app.shared.constants.error_messages import ErrorMessages
from app.shared.constants.http_status import HTTPStatus
from app.shared.exceptions.base import AppException


class StorageException(AppException):
    """Base exception for storage errors."""

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR


class StorageUploadError(StorageException):
    """Raised when file upload fails."""

    error_code = ErrorCodes.STORAGE_UPLOAD_FAILED
    message = ErrorMessages.STORAGE_UPLOAD_FAILED


class StorageDeleteError(StorageException):
    """Raised when file deletion fails."""

    error_code = ErrorCodes.STORAGE_DELETE_FAILED
    message = ErrorMessages.STORAGE_DELETE_FAILED


class StorageNotFoundError(StorageException):
    """Raised when file is not found in storage."""

    error_code = ErrorCodes.STORAGE_NOT_FOUND
    message = ErrorMessages.STORAGE_NOT_FOUND
    status_code = HTTPStatus.NOT_FOUND
