"""Base exception class for the application."""

from app.shared.constants.error_codes import ErrorCodes
from app.shared.constants.error_messages import ErrorMessages
from app.shared.constants.http_status import HTTPStatus


class AppException(Exception):  # noqa: N818
    """Base exception for all application errors."""

    error_code: str = ErrorCodes.UNKNOWN_ERROR
    message: str = ErrorMessages.UNKNOWN_ERROR
    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR

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
