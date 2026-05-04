"""Helpers for configuring observability-related SDKs."""

import functools
from collections.abc import Callable
from typing import Any

from leapx.common.observability.tracer.providers import ObservabilityProvider


def set_litellm_callbacks() -> list[str]:
    """Set LiteLLM callbacks based on the active observability provider."""
    # Lazy import to avoid circular dependency
    from leapx.common.observability.tracer.decorator import (
        get_active_provider,
    )

    provider = get_active_provider()

    provider_to_callbacks: dict[ObservabilityProvider, list[str]] = {
        ObservabilityProvider.LANGFUSE: ["langfuse_otel"],
        ObservabilityProvider.LANGSMITH: ["langsmith"],
    }
    return provider_to_callbacks.get(provider, [])


def create_trace_decorator(tracer: Any, default_service: str | None = None) -> Callable:
    """
    Create a trace decorator from a tracer object.

    Args:
        tracer: The tracer object that provides tracing context
        default_service: Default service name for the trace (optional)

    Returns:
        A decorator function that applies tracing
    """

    def trace_decorator(**kwargs):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **func_kwargs):
                span_name = kwargs.get("name", func.__name__)
                service = kwargs.get("service", default_service)

                # Handle different tracer APIs
                if hasattr(tracer, "trace"):
                    # Datadog-style API
                    context_kwargs = {"name": span_name}
                    if service:
                        context_kwargs["service"] = service
                    context_manager = tracer.trace(**context_kwargs)
                else:
                    # OpenTelemetry-style API
                    context_manager = tracer.start_as_current_span(span_name)

                with context_manager:
                    return func(*args, **func_kwargs)

            return wrapper

        return decorator

    return trace_decorator
