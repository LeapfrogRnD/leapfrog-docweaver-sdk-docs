from app.shared.constants.error_codes import ErrorCodes
from app.shared.constants.error_messages import ErrorMessages
from app.shared.constants.http_status import HTTPStatus
from app.shared.exceptions.base import AppException


class NotFoundException(AppException):
    """Exception for HTTP 404 Not Found errors."""

    status_code = HTTPStatus.NOT_FOUND
    error_code = ErrorCodes.NOT_FOUND

class PipelineConflictException(AppException):
    "Exception for Http 409 Found Errors"
    status_code = HTTPStatus.CONFLICT
    error_code=ErrorCodes.PIPELINE_CONFLICT
    message=ErrorMessages.PIPELINE_INACTIVE

class UnauthorizedException(AppException):
    """Exception for HTTP 401 Unauthorized errors."""

    status_code = HTTPStatus.UNAUTHORIZED
    error_code = ErrorCodes.UNAUTHORIZED


class ForbiddenException(AppException):
    """Exception for HTTP 403 Forbidden errors."""

    status_code = HTTPStatus.FORBIDDEN
    error_code = ErrorCodes.FORBIDDEN


class BadRequestException(AppException):
    """Exception for HTTP 400 Bad Request errors."""

    status_code = HTTPStatus.BAD_REQUEST
    error_code = ErrorCodes.BAD_REQUEST


class ToomanyRequestException(AppException):
    """Exception for HTTP 429 Too Many Requests errors."""

    status_code = HTTPStatus.TOO_MANY_REQUESTS
    error_code = ErrorCodes.TOO_MANY_REQUESTS


class ServerErrorException(AppException):
    """Exception for HTTP 500 Internal Server Error."""

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    error_code = ErrorCodes.INTERNAL_ERROR
