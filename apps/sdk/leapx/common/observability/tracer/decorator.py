"""Custom observability decorator with multi-provider support and environment checks."""

import functools
import inspect
from collections.abc import Callable
from importlib import import_module
from typing import Any

from leapx.common.observability.logger import logger
from leapx.common.observability.tracer.config import ProviderConfig
from leapx.common.observability.tracer.providers import (
    ObservabilityProvider,
)
from leapx.common.observability.tracer.utils import create_trace_decorator


class ObservabilityDecorator:
    """Manages observability decorators with environment-based provider detection."""

    _active_provider: ObservabilityProvider | None = None
    _provider_decorator: Callable | None = None
    _initialized = False

    @classmethod
    def initialize(cls) -> None:
        """Initialize the observability provider based on environment variables."""
        if cls._initialized:
            return

        cls._active_provider = ProviderConfig.detect_provider()
        cls._initialized = True

        if cls._active_provider != ObservabilityProvider.NONE:
            logger.info(
                f"Observability provider detected: {cls._active_provider.value}"
            )
            cls._provider_decorator = cls._get_provider_decorator(cls._active_provider)
        else:
            logger.info("No observability provider configured - tracing disabled")
            cls._provider_decorator = None

    @classmethod
    def _get_provider_decorator(
        cls, provider: ObservabilityProvider
    ) -> Callable | None:
        """
        Get the decorator function for the specified provider.

        Args:
            provider: The observability provider to use

        Returns:
            The provider's decorator function or None
        """
        try:
            provider_map: dict[ObservabilityProvider, Callable[[], Callable]] = {
                ObservabilityProvider.LANGFUSE: cls._get_langfuse_decorator,
                ObservabilityProvider.LANGSMITH: cls._get_langsmith_decorator,
                ObservabilityProvider.DATADOG: cls._get_datadog_decorator,
                ObservabilityProvider.OPENTELEMETRY: cls._get_opentelemetry_decorator,
            }

            factory = provider_map.get(provider)
            return factory() if factory else None
        except ImportError as e:
            logger.warning(
                f"Failed to import {provider.value} - tracing disabled",
                error=str(e),
            )
        return None

    @classmethod
    def _get_langfuse_decorator(cls) -> Callable:
        """Get Langfuse observe decorator."""
        from langfuse import observe as langfuse_observe

        return langfuse_observe

    @classmethod
    def _get_langsmith_decorator(cls) -> Callable:
        """
        Get LangSmith traceable decorator using dynamic import to avoid
        hard import failures.
        """
        try:
            langsmith = import_module("langsmith")
        except ModuleNotFoundError as e:
            raise ImportError from e
        return langsmith.traceable

    @classmethod
    def _get_datadog_decorator(cls) -> Callable:
        """
        Get Datadog trace decorator using dynamic import to avoid
        hard import failures.
        """
        try:
            ddtrace = import_module("ddtrace")
        except ModuleNotFoundError as e:
            raise ImportError from e

        return create_trace_decorator(ddtrace.tracer, default_service="leapx")

    @classmethod
    def _get_opentelemetry_decorator(cls) -> Callable:
        """Get OpenTelemetry trace decorator."""
        from opentelemetry import trace

        tracer = trace.get_tracer(__name__)
        return create_trace_decorator(tracer)

    @classmethod
    def get_decorator(cls) -> Callable:
        """
        Get the active observability decorator.

        Returns:
            The active provider's decorator or a no-op decorator
        """
        if not cls._initialized:
            cls.initialize()

        return (
            cls._provider_decorator if cls._provider_decorator else cls._noop_decorator
        )

    @staticmethod
    def _noop_decorator(**_kwargs):
        """No-op decorator when no observability provider is configured."""

        def decorator(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **func_kwargs):
                return await func(*args, **func_kwargs)

            @functools.wraps(func)
            def sync_wrapper(*args, **func_kwargs):
                return func(*args, **func_kwargs)

            return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

        return decorator


def observe(
    *,
    name: str | None = None,
    capture_input: bool = True,
    capture_output: bool = True,
    as_type: str | None = None,
    **kwargs: Any,
) -> Callable:
    """
    Universal observability decorator that works with multiple providers.

    This decorator automatically detects the configured observability provider
    (Langfuse, LangSmith, Datadog, OpenTelemetry) based on environment variables
    and applies the appropriate tracing. If no provider is configured, it acts
    as a no-op decorator.
    """
    decorator_func = ObservabilityDecorator.get_decorator()

    # Build kwargs for the provider decorator
    provider_kwargs = {
        "capture_input": capture_input,
        "capture_output": capture_output,
    }

    if name:
        provider_kwargs["name"] = name

    if as_type:
        provider_kwargs["as_type"] = as_type

    provider_kwargs.update(kwargs)

    return decorator_func(**provider_kwargs)


def get_active_provider() -> ObservabilityProvider:
    """
    Get the currently active observability provider.

    Returns:
        The active ObservabilityProvider
    """
    if not ObservabilityDecorator._initialized:
        ObservabilityDecorator.initialize()
    return ObservabilityDecorator._active_provider or ObservabilityProvider.NONE
