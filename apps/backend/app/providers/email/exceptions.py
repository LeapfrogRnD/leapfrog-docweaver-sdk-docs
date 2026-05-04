from app.shared.exceptions.base import AppException


class SesClientError(AppException):
    """General failure when communicating with SES."""

    status_code: int = 400
    error_code: str = "email_send_failed"
    message: str = "We couldn't send the email right now. Please try again later."


class SesUnverifiedEmailError(AppException):
    """Specific error for SES Sandbox unverified recipients."""

    status_code: int = 400
    error_code: str = "email_unverified"
    message: str = "This email address is not verified in our mailing system's sandbox."


class SesSystemError(AppException):
    """Critical/Unexpected failure in the email subsystem."""

    status_code: int = 500
    error_code: str = "email_system_critical"
    message: str = "An internal system error occurred while sending the email."
