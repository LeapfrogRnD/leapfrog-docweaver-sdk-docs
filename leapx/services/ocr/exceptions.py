from leapx.common.exceptions import LeapXError
from leapx.common.types.providers import OCRProviderType
from leapx.services.ocr.base.ocr_engine import OCREngine


class OCREngineError(LeapXError):
    """Base OCR engine exception."""


class InvalidOCREngineError(OCREngineError):
    """Raised when a class registered as OCR engine is invalid."""

    def __init__(self, engine_class: type):
        self.engine_class = engine_class
        super().__init__(f"{engine_class.__name__} is not a valid OCREngine subclass.")


class UnknownOCREngineError(OCREngineError):
    """Raised when an unknown OCR provider is requested."""

    def __init__(self, provider: OCRProviderType):
        self.provider = provider
        super().__init__(f"Unknown OCR provider: {provider}")


class OCREngineInitializationError(OCREngineError):
    """Raised when engine initialization fails."""

    def __init__(self, provider: OCRProviderType, engine_class: type[OCREngine]):
        self.provider = provider
        self.engine_class = engine_class
        super().__init__(
            f"OCR engine {engine_class.__name__} failed to initialize for {provider}"
        )
