"""Parser factory for creating layout parser instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from leapx.common.observability.logger import logger
from leapx.services.layout_parser.exceptions.layout_parser_exceptions import (
    ParserNotRegisteredError,
    ParserRegistrationError,
)
from leapx.services.layout_parser.parsers.base_parser import BaseLayoutParser

if TYPE_CHECKING:
    from leapx.common.types.providers import ParsingMethod
    from leapx.pipeline.stages.configs.parser_config import ParserConfig


class ParserFactory:
    """
    Factory for creating layout parser instances.

    Implements the Factory pattern with a registration system,
    allowing new parsers to be registered dynamically without
    modifying existing code (Open/Closed Principle).

    Usage:
        >>> # Register a parser
        >>> ParserFactory.register(ParsingMethod.LAYOUT_CONSERVED,
        LayoutConservedParser)
        >>>
        >>> # Create parser instance
        >>> parser = ParserFactory.create(ParsingMethod.LAYOUT_CONSERVED, config=config)
        >>> text = parser.parse(df)

    Class Attributes:
        _registry: Dictionary mapping ParsingMethod to parser classes
    """

    _registry: dict[ParsingMethod, type[BaseLayoutParser]] = {}  # noqa: RUF012

    @classmethod
    def register(
        cls,
        method: ParsingMethod,
        parser_class: type[BaseLayoutParser],
        override: bool = False,
    ) -> None:
        """
        Register a parser class for a parsing method.

        Args:
            method: ParsingMethod enum value
            parser_class: Parser class (must extend BaseLayoutParser)
            override: Allow overriding existing registration (default: False)

        Raises:
            ParserRegistrationError: If parser already registered and override=False
                                    or if parser_class doesn't extend BaseLayoutParser
        """
        # Validate parser class
        if not issubclass(parser_class, BaseLayoutParser):
            raise ParserRegistrationError(  # noqa: TRY003
                f"Parser class {parser_class.__name__} must extend BaseLayoutParser"
            )

        # Check for existing registration
        if method in cls._registry and not override:
            existing = cls._registry[method].__name__
            raise ParserRegistrationError(  # noqa: TRY003
                f"Parser already registered for {method}: {existing}. "
                f"Use override=True to replace."
            )

        cls._registry[method] = parser_class
        logger.info(f"Registered parser: {method} -> {parser_class.__name__}")

    @classmethod
    def unregister(cls, method: ParsingMethod) -> None:
        """
        Unregister a parser.

        Args:
            method: ParsingMethod to unregister

        Raises:
            ParserNotRegisteredError: If method not registered
        """
        if method not in cls._registry:
            raise ParserNotRegisteredError(f"No parser registered for {method}")  # noqa: TRY003

        parser_name = cls._registry[method].__name__
        del cls._registry[method]
        logger.info(f"Unregistered parser: {method} -> {parser_name}")

    @classmethod
    def create(
        cls,
        method: ParsingMethod,
        config: ParserConfig | None = None,
    ) -> BaseLayoutParser:
        """
        Create parser instance for given method.

        Args:
            method: ParsingMethod enum value
            config: Optional configuration object

        Returns:
            Instantiated parser object

        Raises:
            ParserNotRegisteredError: If no parser registered for method
        """
        if method not in cls._registry:
            available = ", ".join(str(m) for m in cls._registry)
            raise ParserNotRegisteredError(  # noqa: TRY003
                f"No parser registered for {method}. Available: {available}"
            )

        parser_class = cls._registry[method]
        parser = parser_class(config=config)

        logger.debug(f"Created parser: {method} -> {parser_class.__name__}")
        return parser

    @classmethod
    def list_available(cls) -> list[ParsingMethod]:
        """
        Get list of available parsing methods.

        Returns:
            List of registered ParsingMethod values
        """
        return list(cls._registry.keys())

    @classmethod
    def is_registered(cls, method: ParsingMethod) -> bool:
        """
        Check if parsing method is registered.

        Args:
            method: ParsingMethod to check

        Returns:
            True if registered, False otherwise
        """
        return method in cls._registry

    @classmethod
    def get_parser_class(cls, method: ParsingMethod) -> type[BaseLayoutParser]:
        """
        Get registered parser class for method.

        Args:
            method: ParsingMethod to look up

        Returns:
            Parser class (not instantiated)

        Raises:
            ParserNotRegisteredError: If method not registered
        """
        if method not in cls._registry:
            raise ParserNotRegisteredError(f"No parser registered for {method}")  # noqa: TRY003

        return cls._registry[method]

    @classmethod
    def clear_registry(cls) -> None:
        """
        Clear all registered parsers.

        Useful for testing or resetting the factory state.
        """
        cls._registry.clear()
        logger.warning("Cleared parser registry")
