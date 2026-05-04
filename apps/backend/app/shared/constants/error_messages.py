"""Human-readable error messages."""


class ErrorMessages:
    """User-friendly error messages for API responses."""

    # File Validation
    INVALID_FILE_TYPE = (
        "Only PDF files are allowed. Please upload a file with .pdf extension."
    )
    FILE_SIZE_EXCEEDED = "File size exceeds the maximum allowed limit of {max_size}MB."
    PAGE_LIMIT_EXCEEDED = "PDF has too many pages. Maximum {max_pages} pages allowed."
    EMPTY_FILE = "Uploaded file is empty."
    FILE_READ_FAILED = "Failed to read the uploaded file."

    # Configuration
    INVALID_CONFIG = "Invalid configuration format provided."
    INVALID_SCHEMA = "Invalid schema format provided."
    MISSING_CONFIG = "Configuration is required."
    MISSING_SCHEMA = "Schema is required."
    INVALID_TASK_TYPE = "Invalid task_type. Expected '{expected}', got '{actual}'."
    INVALID_JSON = "Invalid JSON format: {detail}"

    # Processing
    OCR_PROCESSING_FAILED = "OCR processing failed."
    EXTRACTION_FAILED = "Data extraction failed."
    CLASSIFICATION_FAILED = "Document classification failed."
    PIPELINE_EXECUTION_FAILED = "Pipeline execution failed."

    # Storage
    STORAGE_UPLOAD_FAILED = "Failed to upload file to storage."
    STORAGE_DELETE_FAILED = "Failed to delete file from storage."
    STORAGE_NOT_FOUND = "File not found in storage."

    # Generic
    INTERNAL_ERROR = "An unexpected error occurred."
    UNKNOWN_ERROR = "An unknown error occurred."

    # CSRF
    CSRF_TOKEN_INVALID = "CSRF token validation failed. Please refresh the page and try again."  # noqa: S105
    CSRF_TOKEN_MISSING = (
        "CSRF token is missing. Please refresh the page and try again."  # noqa: S105
    )

    # User Specific
    BLOCKED_ACCOUNT = (
        "Account Restricted: Please contact  Support Team for further assistance."
    )
    INACTIVE_ACCOUNT = "This account is currently inactive. Please verify your email address or contact support for reactivation."
    NOT_SETUP = "Account setup is incomplete. Please complete your profile to proceed."
    SUSPICIOUS_ACTIVITY = "This account has been temporarily locked due to unusual activity. Please reset your password or contact support."
    WRONG_PASSWORD = "The password provided is incorrect. Please verify your credentials and try again."
    USER_NOT_FOUND = "No account is associated with the provided credentials."
    EXPIRED_PASSWORD = (
        "Your password has expired. Please reset your password to regain access."
    )
    TOO_MANY_ATTEMPTS = "Access temporarily restricted due to multiple unsuccessful attempts. Please try again later or reset your password."
    EMAIL_NOT_VERIFIED = "Email verification is required. Please check your inbox and verify your email address."
    SESSION_EXPIRED = "Your session has expired. Please sign in again to continue."
    INSUFFICIENT_PERMISSIONS = (
        "You do not have the required permissions to perform this action."
    )
    INVALID_PERMISSION_FOR_SELF = "You cannot delete your own account"
    INVALID_CREDENTIALS = (
        "The credentials provided are invalid. Please verify and try again."
    )
    INVALID_TOKEN = "The provided token is invalid."
    TOKEN_EXPIRED = "The token has expired. Please request a new one."
    TOKEN_NOT_FOUND = "The requested token could not be found."
    PROFILE_NOT_SETUP = (
        "User profile setup is incomplete. Please complete your profile to proceed."
    )
    INVALID_RESET_TOKEN = (
        "The password reset token is invalid or has expired. Please request a new one."
    )
    PIPELINE_INACTIVE = "Cannot execute workflow with an inactive pipeline"
