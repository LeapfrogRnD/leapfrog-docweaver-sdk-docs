from abc import ABC, abstractmethod

from leapx.services.layout_parser.structures.ocr_data import OCRData


class OCRFacadeInterface(ABC):
    """Facade interface for provider-specific OCR operations.

    Implementations encapsulate the provider SDK interactions and expose a
    unified API used by OCREngine implementations.
    """

    @abstractmethod
    def process_document(self, file_bytes: bytes) -> list[OCRData]:
        """Process a document and return standardized OCRData per page.

        Args:
            file_bytes: PDF bytes to process.

        Returns:
            List of OCRData objects, one per page.
        """
        pass
