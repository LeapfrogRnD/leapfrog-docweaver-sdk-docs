from abc import ABC, abstractmethod

from leapx.services.extractor.schemas import ExtractionRequest, ExtractionResponse


class ExtractorInterface(ABC):
    """Abstract interface for extraction services"""

    @abstractmethod
    async def extract(self, request: ExtractionRequest) -> ExtractionResponse:
        """
        Extract structured data using the provided prompts and response model

        Args:
            request: ExtractionRequest containing system prompt, user prompt,
            and response model

        Returns:
            ExtractionResponse with extracted data or error information
        """
        pass

    @abstractmethod
    def validate_request(self, request: ExtractionRequest) -> tuple[bool, str | None]:
        """
        Validate the extraction request before processing

        Args:
            request: ExtractionRequest to validate

        Returns:
            Tuple of (is_valid, error_message). If valid, error_message is None.
            If invalid, error_message contains the specific validation error.
        """
        pass
