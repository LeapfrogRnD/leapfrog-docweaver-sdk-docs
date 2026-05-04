"""Human-readable error messages."""


class ErrorMessages:
    """User-friendly error messages for API responses."""

    # File Validation
    INVALID_FILE_TYPE = "Only PDF files are allowed. Please upload a file with .pdf extension."
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
