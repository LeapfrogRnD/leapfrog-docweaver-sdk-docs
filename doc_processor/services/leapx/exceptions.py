from shared.constants.app_error_codes import WorkerStatus
from shared.constants.error_codes import ErrorCodes
from shared.constants.error_messages import ErrorMessages


class ClassificationError(Exception):
    """Raised when document classification fails."""

    error_code = ErrorCodes.CLASSIFICATION_FAILED
    message = ErrorMessages.CLASSIFICATION_FAILED
    status_code = WorkerStatus.INTERNAL_SERVER_ERROR
