from abc import ABC, abstractmethod

from leapx.common.observability.logger import logger
from leapx.services.layout_parser.structures.ocr_data import OCRData


class OCREngine(ABC):
    """Abstract base class for OCR engines.

    Implementations should initialize with provider credentials and expose
    an async extract_text method returning OCRData per page.
    """

    def __init__(self):
        self.is_configured = False
        logger.info(
            "Ocr engine initialized",
            configured=self.is_configured,
        )

    @abstractmethod
    def initialize(self, **kwargs) -> bool:
        """Configure the engine with credentials/settings.

        Returns:
            True if initialization succeeded; False otherwise.
        """
        pass

    @abstractmethod
    async def extract_text(self, input_data: str | bytes) -> list[OCRData]:
        """Extract text into OCRData objects (one per page).

        Args:
            input_data: File path or raw bytes of the document.

        Returns:
            List of OCRData, one per page.
        """
        pass
