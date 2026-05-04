from abc import ABC, abstractmethod

from leapx.services.generator.schemas import GenerationRequest, GenerationResponse


class GeneratorInterface(ABC):
    """Abstract interface for generation services"""

    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """
        Summarize the input text based on the provided generation request.
        Args:
            request: GenerationRequest containing prompts, model config, and response model
        Returns:
            GenerationResponse containing the generated data and metadata
        """

        pass

    @abstractmethod
    def validate_request(self, request: GenerationRequest) -> tuple[bool, str | None]:
        """
        Validate the generation request before processing

        Args:
            request: GenerationRequest to validate

        Returns:
            Tuple of (is_valid, error_message). If valid, error_message is None.
            If invalid, error_message contains the specific validation error.
        """
        pass
