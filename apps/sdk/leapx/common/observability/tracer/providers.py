"""Observability provider configuration and detection."""

from enum import Enum


class ObservabilityProvider(str, Enum):
    """Supported observability providers."""

    LANGFUSE = "langfuse"
    LANGSMITH = "langsmith"
    DATADOG = "datadog"
    OPENTELEMETRY = "opentelemetry"
    NONE = "none"
