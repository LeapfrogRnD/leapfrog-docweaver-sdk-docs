import litellm
import instructor
from typing import Any
from litellm import acompletion
from pydantic import BaseModel

from leapx.common.observability.logger import logger
from leapx.common.observability.tracer.decorator import observe
from leapx.common.observability.tracer.utils import set_litellm_callbacks
from leapx.services.extractor.constants import (
    EMPTY_SYSTEM_PROMPT_CONTENT,
    EMPTY_USER_PROMPT_CONTENT,
    INVALID_RESPONSE_MODEL,
)
from leapx.services.generator.base_generator import GeneratorInterface
from leapx.services.generator.exceptions.generator_exceptions import (
    GeneratorValidationError,
)
from leapx.services.generator.schemas import (
    GenerationRequest,
    GenerationResponse,
    UserPrompt,
)


class GeneratorService(GeneratorInterface):
    """ """

    def __init__(self, instructor_client=None) -> None:
        """
        Initialize the GeneratorService.

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

        This method should be called when the GeneratorService is no longer needed
        to ensure that any underlying asynchronous LiteLLM clients are properly
        closed and resources are released.
        """
        if self._instructor_client is not None:
            litellm.close_litellm_async_clients()

    def validate_request(self, request: GenerationRequest) -> tuple[bool, str | None]:
        """
        Validate the generation request.

        Args:
            request: GenerationRequest to validate

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

    @observe(name="generator_service.generate", capture_input=True, capture_output=True)
    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        """
        Generate the summary using the provided prompts and response model.

        This method handles automatic fallback to JSON mode for models that
        don't support tool calling. Validation errors are returned as error
        responses rather than raised, allowing other chunks to continue processing.

        Args:
            request: GenerationRequest containing system prompt, user prompt,
                and response model

        Returns:
            GenerationResponse with generated summary
        """
        try:
            # Validate request - return error response instead of raising
            is_valid, validation_error = self.validate_request(request)
            if not is_valid:
                logger.warning(
                    "Generation validation failed",
                    error=validation_error,
                )
                return GenerationResponse(
                    data="",
                    metadata={
                        "error": validation_error,
                        "status": "validation_failed",
                        "model": request.config.model
                        if hasattr(request, "config")
                        else None,
                    },
                )

            messages = self._prepare_messages(request)
            result = await self._execute_generation_with_fallback(request, messages)
            return self._create_response(result, request)

        except Exception as e:
            logger.exception("Async generation failed", error=str(e))
            # Return error response instead of raising to allow other chunks to continue
            return GenerationResponse(
                data="",
                metadata={
                    "error": str(e),
                    "status": "generation_failed",
                    "error_type": type(e).__name__,
                    "model": request.config.model
                    if hasattr(request, "config")
                    else None,
                },
            )

    # Private helper methods

    def _has_valid_prompt(self, request: GenerationRequest, prompt_attr: str) -> bool:
        """Check if request has a valid prompt attribute with content."""
        return (
            hasattr(request, prompt_attr)
            and hasattr(getattr(request, prompt_attr), "content")
            and bool(getattr(request, prompt_attr).content.strip())
        )

    def _has_valid_response_model(self, request: GenerationRequest) -> bool:
        """Check if request has a valid response model (BaseModel subclass)."""
        try:
            return hasattr(request, "response_model") and issubclass(
                request.response_model, BaseModel
            )
        except TypeError:
            return False

    def _validate_and_log(self, request: GenerationRequest) -> None:
        """
        Validate request and raise exception if invalid.

        Args:
            request: GenerationRequest to validate

        Raises:
           Error: If validation fails
        """
        is_valid, validation_error = self.validate_request(request)
        if not is_valid:
            raise GeneratorValidationError(message=validation_error)

    def _prepare_messages(self, request: GenerationRequest) -> list[dict[str, str]]:
        """
        Prepare messages for the generation request.

        Args:
            request: GenerationRequest instance

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

    async def _execute_generation_with_fallback(
        self, request: GenerationRequest, messages: list[dict[str, str]]
    ) -> Any:
        """
        Execute generation with automatic fallback to JSON mode if needed.

        Args:
            request: GenerationRequest instance
            messages: Prepared messages for the LLM

        Returns:
            Generation result from the LLM

        Raises:
            Exception: If Generation fails even after fallback
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
        self, request: GenerationRequest, messages: list[dict[str, str]]
    ) -> Any:
        """
        Fallback to JSON mode for models that don't support tool calling.

        Args:
            request: GenerationRequest instance
            messages: Prepared messages for the LLM

        Returns:
            Generation result from the LLM using JSON mode
        """
        json_client = instructor.from_litellm(acompletion, mode=instructor.Mode.MD_JSON)
        return await self._call_llm(json_client, request, messages)

    async def _call_llm(
        self,
        client: instructor.Instructor,
        request: GenerationRequest,
        messages: list[dict[str, str]],
    ) -> Any:
        """
        Make the actual LLM API call.

        Args:
            client: Instructor client to use
            request: GenerationRequest instance
            messages: Prepared messages for the LLM

        Returns:
            Generation result from the LLM
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
        self, result: Any, request: GenerationRequest
    ) -> GenerationResponse:
        """
        Create GenerationResponse from the result.

        Args:
            result: The generation result from the LLM
            request: GenerationRequest instance

        Returns:
            GenerationResponse with data and metadata
        """
        # Try to extract data in order of preference: summary, data, or string representation
        if hasattr(result, "summary"):
            data = result.summary
        else:
            data = str(result)
        
        return GenerationResponse(
            data=data,
            metadata={
                "model": request.config.model,
                "temperature": request.config.temperature,
                "max_tokens": request.config.max_tokens,
            },
        )
