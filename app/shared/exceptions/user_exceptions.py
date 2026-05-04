from app.shared.constants.error_codes import ErrorCodes
from app.shared.constants.error_messages import ErrorMessages
from app.shared.constants.http_status import HTTPStatus
from app.shared.exceptions.base import AppException


class BlockedAccountError(AppException):
    """Raised when a user account is blocked."""

    error_code = ErrorCodes.BLOCKED_ACCOUNT
    status_code = HTTPStatus.FORBIDDEN

    def __init__(self):
        message = ErrorMessages.BLOCKED_ACCOUNT
        super().__init__(message=message)


class InactiveAccountError(AppException):
    """Raised when a user account is inactive."""

    error_code = ErrorCodes.INACTIVE_ACCOUNT
    status_code = HTTPStatus.FORBIDDEN

    def __init__(self):
        message = ErrorMessages.INACTIVE_ACCOUNT
        super().__init__(message=message)


class NotSetupAccountError(AppException):
    """Raised when the account setup is incomplete."""

    error_code = ErrorCodes.NOT_SETUP
    status_code = HTTPStatus.FORBIDDEN

    def __init__(self):
        message = ErrorMessages.NOT_SETUP
        super().__init__(message=message)


class SuspiciousActivityError(AppException):
    """Raised when the account is temporarily locked due to suspicious activity."""

    error_code = ErrorCodes.SUSPICIOUS_ACTIVITY
    status_code = HTTPStatus.FORBIDDEN

    def __init__(self):
        message = ErrorMessages.SUSPICIOUS_ACTIVITY
        super().__init__(message=message)


class WrongPasswordError(AppException):
    """Raised when the entered password is incorrect."""

    error_code = ErrorCodes.WRONG_PASSWORD
    status_code = HTTPStatus.UNAUTHORIZED

    def __init__(self):
        message = ErrorMessages.WRONG_PASSWORD
        super().__init__(message=message)


class UserNotFoundError(AppException):
    """Raised when no account is found with the given email/username."""

    error_code = ErrorCodes.USER_NOT_FOUND
    status_code = HTTPStatus.NOT_FOUND

    def __init__(self):
        message = ErrorMessages.USER_NOT_FOUND
        super().__init__(message=message)


class ExpiredPasswordError(AppException):
    """Raised when the user's password has expired."""

    error_code = ErrorCodes.EXPIRED_PASSWORD
    status_code = HTTPStatus.FORBIDDEN

    def __init__(self):
        message = ErrorMessages.EXPIRED_PASSWORD
        super().__init__(message=message)


class TooManyAttemptsError(AppException):
    """Raised when there are too many unsuccessful login attempts."""

    error_code = ErrorCodes.TOO_MANY_ATTEMPTS
    status_code = HTTPStatus.TOO_MANY_REQUESTS

    def __init__(self):
        message = ErrorMessages.TOO_MANY_ATTEMPTS
        super().__init__(message=message)


class EmailNotVerifiedError(AppException):
    """Raised when the user's email is not verified."""

    error_code = ErrorCodes.EMAIL_NOT_VERIFIED
    status_code = HTTPStatus.FORBIDDEN

    def __init__(self):
        message = ErrorMessages.EMAIL_NOT_VERIFIED
        super().__init__(message=message)


class SessionExpiredError(AppException):
    """Raised when the user's session has expired."""

    error_code = ErrorCodes.SESSION_EXPIRED
    status_code = HTTPStatus.UNAUTHORIZED

    def __init__(self):
        message = ErrorMessages.SESSION_EXPIRED
        super().__init__(message=message)


class InsufficientPermissionsError(AppException):
    """Raised when a user tries to perform an action without required permissions."""

    error_code = ErrorCodes.INSUFFICIENT_PERMISSIONS
    status_code = HTTPStatus.FORBIDDEN

    def __init__(self, message: str = ErrorMessages.INSUFFICIENT_PERMISSIONS):
        super().__init__(message=message)
