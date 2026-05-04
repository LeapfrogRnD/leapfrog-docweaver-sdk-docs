from app.shared.constants.http_status import HTTPStatus
from app.shared.exceptions.base import AppException


class QueueException(AppException):
    """Base exception for storage errors."""

    status_code = HTTPStatus.INTERNAL_SERVER_ERROR


class QueueError(QueueException):
    """Base exception for queue operations."""


class QueueSendError(QueueException):
    """Exception raised when sending a message fails."""


class QueueReceiveError(QueueException):
    """Exception raised when receiving messages fails."""


class QueueDeleteError(QueueException):
    """Exception raised when deleting a message fails."""
