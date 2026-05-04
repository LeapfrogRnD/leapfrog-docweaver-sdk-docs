from leapx.common.exceptions.base import LeapXError


class MissingStageError(LeapXError):
    """Raised when a no stage is provided."""

    def __init__(self):
        super().__init__("Missing Stage is not a valid OCREngine subclass.")


class MissingOCRResultError(LeapXError):
    """Raised when a no stage is provided."""

    def __init__(self):
        super().__init__("Missing Ocr result which is required for parser")


class MissingInputForExtractionError(LeapXError):
    """Raised when input for extraction"""

    def __init__(
        self,
    ):
        super().__init__("Missing input Text for llm extraction ")


class InvalidStageError(LeapXError):
    """Raised when an invalid stage configuration is provided."""

    def __init__(self, message: str):
        super().__init__(message)
