"""Factory for creating generator service instances.

This module provides a factory implementation for creating different types
of generator services with support for custom implementations and service registration.
"""

from enum import Enum
from typing import ClassVar

from leapx.common.observability.logger import logger
from leapx.services.generator.base_generator import GeneratorInterface
from leapx.services.generator.exceptions.generator_exceptions import (
    GeneratorCreationError,
    GeneratorError,
)
from leapx.services.generator.generator_service import GeneratorService


class GeneratorProvider(str, Enum):
    """Enumeration of available generator types."""

    LITE_LLM = "lite_llm"


class GeneratorFactory:
    """
    Factory for creating generator service instances.

    Implements the Factory pattern with a registration system,
    allowing new generator implementations to be registered dynamically
    without modifying existing code (Open/Closed Principle).

    """

    _registry: ClassVar[dict[str, type[GeneratorInterface]]] = {
        GeneratorProvider.LITE_LLM.value: GeneratorService,
    }

    @classmethod
    def create(
        cls,
        provider: str | GeneratorProvider = GeneratorProvider.LITE_LLM,
    ) -> GeneratorInterface:
        """
        Create a generator service instance.

        Args:
            provider: Type of generator to create (default: LITE_LLM)

        Returns:
            Instantiated generator service

        Raises:
            GeneratorNotRegisteredError: If no generator registered for type
            GeneratorCreationError: If generator creation fails
        """
        # Convert enum to string if necessary
        generator_type = (
            provider.value if isinstance(provider, GeneratorProvider) else provider
        )

        if generator_type not in cls._registry:
            available = ", ".join(cls._registry.keys())
            raise GeneratorError(
                generator_type, 
                {"available_providers": available},
                )

        generator_class = cls._registry[generator_type]

        try:
            generator = generator_class()
        except Exception as e:
            logger.exception(
                "Failed to create generator service",
                generator_type=generator_type,
                error=str(e),
            )
            raise GeneratorCreationError(generator_type, e) from e

        logger.info(
            "Created generator service",
            generator_type=generator_type,
            generator_class=generator_class.__name__,
        )
        return generator
