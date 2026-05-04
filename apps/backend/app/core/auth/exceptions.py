"""Authentication-related exceptions."""

from app.shared.constants.error_codes import ErrorCodes
from app.shared.constants.error_messages import ErrorMessages
from app.shared.constants.http_status import HTTPStatus
from app.shared.exceptions.base import AppException


class InvalidCredentialsError(AppException):
    """Raised when the provided credentials are invalid."""

    error_code = ErrorCodes.INVALID_CREDENTIALS
    status_code = HTTPStatus.UNAUTHORIZED

    def __init__(self, message: str | None = None):
        message = message or ErrorMessages.INVALID_CREDENTIALS
        super().__init__(message=message)


class InvalidTokenError(AppException):
    """Raised when the provided token is invalid."""

    error_code = ErrorCodes.INVALID_TOKEN
    status_code = HTTPStatus.UNAUTHORIZED

    def __init__(self, message: str | None = None):
        message = message or ErrorMessages.INVALID_TOKEN
        super().__init__(message=message)


class TokenExpiredError(AppException):
    """Raised when the token has expired."""

    error_code = ErrorCodes.TOKEN_EXPIRED
    status_code = HTTPStatus.UNAUTHORIZED

    def __init__(self, message: str | None = None):
        message = message or ErrorMessages.TOKEN_EXPIRED
        super().__init__(message=message)


class TokenNotFoundError(AppException):
    """Raised when the requested token could not be found."""

    error_code = ErrorCodes.TOKEN_NOT_FOUND
    status_code = HTTPStatus.UNAUTHORIZED

    def __init__(self, message: str | None = None):
        message = message or ErrorMessages.TOKEN_NOT_FOUND
        super().__init__(message=message)


class UserNotFoundError(AppException):
    """Raised when no account is associated with the provided credentials."""

    error_code = ErrorCodes.USER_NOT_FOUND
    status_code = HTTPStatus.NOT_FOUND

    def __init__(self, message: str | None = None):
        message = message or ErrorMessages.USER_NOT_FOUND
        super().__init__(message=message)


class ProfileNotSetupError(AppException):
    """Raised when the user profile setup is incomplete."""

    error_code = ErrorCodes.PROFILE_NOT_SETUP
    status_code = HTTPStatus.FORBIDDEN

    def __init__(self, message: str | None = None):
        message = message or ErrorMessages.PROFILE_NOT_SETUP
        super().__init__(message=message)


class InvalidResetTokenError(AppException):
    """Raised when the password reset token is invalid or has expired."""

    error_code = ErrorCodes.INVALID_RESET_TOKEN
    status_code = HTTPStatus.BAD_REQUEST

    def __init__(self, message: str | None = None):
        message = message or ErrorMessages.INVALID_RESET_TOKEN
        super().__init__(message=message)
