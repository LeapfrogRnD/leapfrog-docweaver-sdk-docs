"""Extractor service for structured data extraction using LLM."""

from typing import Any

import instructor
import litellm
from litellm import acompletion
from pydantic import BaseModel

from leapx.common.observability import observe
from leapx.common.observability.logger import logger
from leapx.common.observability.tracer.utils import set_litellm_callbacks
from leapx.services.extractor.base_extractor import ExtractorInterface
from leapx.services.extractor.constants import (
    EMPTY_SYSTEM_PROMPT_CONTENT,
    EMPTY_USER_PROMPT_CONTENT,
    INVALID_RESPONSE_MODEL,
)
from leapx.services.extractor.exceptions.extractor_exceptions import (
    ExtractorValidationError,
)
from leapx.services.extractor.schemas import (
    ExtractionRequest,
    ExtractionResponse,
    UserPrompt,
)


class ExtractorService(ExtractorInterface):
    """
    Concrete implementation of ExtractorInterface using LiteLLM and Instructor.

    This service handles structured data extraction from text using LLMs with
    automatic fallback for models that don't support tool calling.
    """

    def __init__(self, instructor_client=None) -> None:
        """
        Initialize the ExtractorService.

        Args:
            instructor_client: Optional pre-configured instructor client
                for dependency injection and testing
        """
        self._instructor_client = instructor_client

    @property
    def instructor_client(self) -> instructor.Instructor:
        """Lazy initialization of instructor client."""
        if self._instructor_client is None:
            self._instructor_client = instructor.from_litellm(acompletion)
        return self._instructor_client

    def close(self):
        """
        Close any initialized asynchronous LiteLLM clients.

        This method should be called when the ExtractorService is no longer needed
        to ensure that any underlying asynchronous LiteLLM clients are properly
        closed and resources are released.
        """
        if self._instructor_client is not None:
            litellm.close_litellm_async_clients()

    def validate_request(self, request: ExtractionRequest) -> tuple[bool, str | None]:
        """
        Validate the extraction request.

        Args:
            request: ExtractionRequest to validate

        Returns:
            Tuple of (is_valid, error_message). If valid, error_message is None.
        """
        # Validate system prompt
        if not self._has_valid_prompt(request, "system_prompt"):
            return False, EMPTY_SYSTEM_PROMPT_CONTENT

        # Validate user prompt
        if not self._has_valid_prompt(request, "user_prompt"):
            return False, EMPTY_USER_PROMPT_CONTENT

        # Validate response model
        if not self._has_valid_response_model(request):
            return False, INVALID_RESPONSE_MODEL.format(
                type(getattr(request, "response_model", None)).__name__
            )

        return True, None

    @observe(name="extractor_service.extract", capture_input=True, capture_output=True)
    async def extract(self, request: ExtractionRequest) -> ExtractionResponse:
        """
        Extract structured data using the provided prompts and response model.

        This method handles automatic fallback to JSON mode for models that
        don't support tool calling. Validation errors are returned as error
        responses rather than raised, allowing other chunks to continue processing.

        Args:
            request: ExtractionRequest containing system prompt, user prompt,
                and response model

        Returns:
            ExtractionResponse with extracted data or error information
        """
        try:
            # Validate request - return error response instead of raising
            is_valid, validation_error = self.validate_request(request)
            if not is_valid:
                logger.warning(
                    "Extraction validation failed",
                    error=validation_error,
                )
                return ExtractionResponse(
                    data=None,
                    metadata={
                        "error": validation_error,
                        "status": "validation_failed",
                        "model": request.config.model
                        if hasattr(request, "config")
                        else None,
                    },
                )

            messages = self._prepare_messages(request)
            result = await self._execute_extraction_with_fallback(request, messages)
            return self._create_response(result, request)

        except Exception as e:
            logger.exception("Async extraction failed", error=str(e))
            # Return error response instead of raising to allow other chunks to continue
            return ExtractionResponse(
                data=None,
                metadata={
                    "error": str(e),
                    "status": "extraction_failed",
                    "error_type": type(e).__name__,
                    "model": request.config.model
                    if hasattr(request, "config")
                    else None,
                },
            )

    # Private helper methods

    def _has_valid_prompt(self, request: ExtractionRequest, prompt_attr: str) -> bool:
        """Check if request has a valid prompt attribute with content."""
        return (
            hasattr(request, prompt_attr)
            and hasattr(getattr(request, prompt_attr), "content")
            and bool(getattr(request, prompt_attr).content.strip())
        )

    def _has_valid_response_model(self, request: ExtractionRequest) -> bool:
        """Check if request has a valid response model (BaseModel subclass)."""
        try:
            return hasattr(request, "response_model") and issubclass(
                request.response_model, BaseModel
            )
        except TypeError:
            return False

    def _validate_and_log(self, request: ExtractionRequest) -> None:
        """
        Validate request and raise exception if invalid.

        Args:
            request: ExtractionRequest to validate

        Raises:
            ExtractorValidationError: If validation fails
        """
        is_valid, validation_error = self.validate_request(request)
        if not is_valid:
            raise ExtractorValidationError(message=validation_error)

    def _prepare_messages(self, request: ExtractionRequest) -> list[dict[str, str]]:
        """
        Prepare messages for the extraction request.

        Args:
            request: ExtractionRequest instance

        Returns:
            List of message dictionaries for the LLM
        """
        return [
            {"role": "system", "content": request.system_prompt.content},
            {"role": "user", "content": self._build_user_content(request.user_prompt)},
        ]

    def _build_user_content(self, user_prompt: UserPrompt) -> str:
        """
        Build the user content from the user prompt.

        Args:
            user_prompt: UserPrompt instance

        Returns:
            Formatted user content string with optional context
        """
        content = user_prompt.content
        if user_prompt.context:
            content = f"Context: {user_prompt.context}\nocr_text:\n```{content}```"
        return content

    async def _execute_extraction_with_fallback(
        self, request: ExtractionRequest, messages: list[dict[str, str]]
    ) -> Any:
        """
        Execute extraction with automatic fallback to JSON mode if needed.

        Args:
            request: ExtractionRequest instance
            messages: Prepared messages for the LLM

        Returns:
            Extraction result from the LLM

        Raises:
            Exception: If extraction fails even after fallback
        """
        try:
            return await self._call_llm(self.instructor_client, request, messages)
        except Exception as e:
            if self._is_unsupported_tool_choice_error(e):
                logger.warning(
                    "Model does not support tool_choice, falling back to MD_JSON mode",
                    model=request.config.model,
                    error_type=type(e).__name__,
                )
                return await self._fallback_to_json_mode(request, messages)
            raise

    # TODO: Refactor error detection to a more robust mechanism if possible
    def _is_unsupported_tool_choice_error(self, error: Exception) -> bool:
        """
        Check if error is related to unsupported parameters (e.g., tool_choice).

        Args:
            error: Exception to check

        Returns:
            True if this is an unsupported params error
        """
        error_message = str(error).lower()
        return (
            "unsupportedparamserror" in error_message
            or "tool_choice" in error_message
            or "instructor does not support multiple tool calls" in error_message
        )

    async def _fallback_to_json_mode(
        self, request: ExtractionRequest, messages: list[dict[str, str]]
    ) -> Any:
        """
        Fallback to JSON mode for models that don't support tool calling.

        Args:
            request: ExtractionRequest instance
            messages: Prepared messages for the LLM

        Returns:
            Extraction result from the LLM using JSON mode
        """
        json_client = instructor.from_litellm(acompletion, mode=instructor.Mode.MD_JSON)
        return await self._call_llm(json_client, request, messages)

    async def _call_llm(
        self,
        client: instructor.Instructor,
        request: ExtractionRequest,
        messages: list[dict[str, str]],
    ) -> Any:
        """
        Make the actual LLM API call.

        Args:
            client: Instructor client to use
            request: ExtractionRequest instance
            messages: Prepared messages for the LLM

        Returns:
            Extraction result from the LLM
        """
        litellm.callbacks = set_litellm_callbacks()

        return await client.chat.completions.create(
            model=request.config.model,
            response_model=request.response_model,
            messages=messages,
            temperature=request.config.temperature,
            max_tokens=request.config.max_tokens,
        )

    def _create_response(
        self, result: Any, request: ExtractionRequest
    ) -> ExtractionResponse:
        """
        Create ExtractionResponse from the result.

        Args:
            result: The extraction result from the LLM
            request: ExtractionRequest instance

        Returns:
            ExtractionResponse with data and metadata
        """
        return ExtractionResponse(
            data=result,
            metadata={
                "model": request.config.model,
                "temperature": request.config.temperature,
                "max_tokens": request.config.max_tokens,
            },
        )


def create_extractor_service(
    instructor_client: instructor.Instructor | None = None,
) -> ExtractorService:
    """
    Factory function to create an ExtractorService instance.

    Args:
        instructor_client: Optional pre-configured instructor client

    Returns:
        ExtractorService instance
    """
    return ExtractorService(instructor_client)
