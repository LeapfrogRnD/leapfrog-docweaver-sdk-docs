import os
from abc import abstractmethod
from typing import Any, ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from leapx.common.observability.tracer.providers import ObservabilityProvider


class BaseProviderSettings(BaseSettings):
    """Base class for provider settings with common configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        populate_by_name=True,
        extra="ignore",
        env_ignore_empty=True,
    )

    @property
    @abstractmethod
    def required_key(self) -> str:
        """
        The key field name that must be present for this provider
        to be configured.
        """
        pass

    def is_configured(self) -> bool:
        """Check if all required settings are configured."""
        # Check if tracing_enabled field exists and is True
        tracing_enabled = getattr(self, "tracing_enabled", True)
        if not tracing_enabled:
            return False

        # Get the value of the required key field
        required_value = getattr(self, self.required_key, None)
        return bool(required_value)

    def to_dict(self) -> dict[str, Any]:
        """Convert to configuration dictionary, excluding None values."""
        return {k: v for k, v in self.model_dump().items() if v is not None}


class LangfuseSettings(BaseProviderSettings):
    """Langfuse provider settings."""

    secret_key: str | None = Field(default=None, alias="LANGFUSE_SECRET_KEY")
    public_key: str | None = Field(default=None, alias="LANGFUSE_PUBLIC_KEY")
    host: str = Field(default="https://cloud.langfuse.com", alias="LANGFUSE_BASE_URL")
    tracing_enabled: bool = Field(default=True, alias="LANGFUSE_TRACING_ENABLED")

    @property
    def required_key(self) -> str:
        """Langfuse requires the secret_key to be configured."""
        return "secret_key"


class LangsmithSettings(BaseProviderSettings):
    """Langsmith provider settings."""

    api_key: str | None = Field(default=None, alias="LANGSMITH_API_KEY")
    project: str = Field(default="default", alias="LANGSMITH_PROJECT")
    endpoint: str = Field(
        default="https://api.smith.langchain.com", alias="LANGSMITH_ENDPOINT"
    )
    tracing_enabled: bool = Field(default=True, alias="LANGSMITH_TRACING")

    @property
    def required_key(self) -> str:
        """Langsmith requires the api_key to be configured."""
        return "api_key"


class DatadogSettings(BaseProviderSettings):
    """Datadog provider settings."""

    api_key: str | None = Field(default=None, alias="DD_API_KEY")
    site: str = Field(default="datadoghq.com", alias="DD_SITE")
    service: str = Field(default="leapx", alias="DD_SERVICE")
    env: str = Field(default="production", alias="DD_ENV")
    tracing_enabled: bool = Field(default=True, alias="DD_TRACE_ENABLED")

    @property
    def required_key(self) -> str:
        """Datadog requires the api_key to be configured."""
        return "api_key"


class OpenTelemetrySettings(BaseProviderSettings):
    """OpenTelemetry provider settings."""

    endpoint: str | None = Field(default=None, alias="OTEL_EXPORTER_OTLP_ENDPOINT")
    service_name: str = Field(default="leapx", alias="OTEL_SERVICE_NAME")
    headers: str | None = Field(default=None, alias="OTEL_EXPORTER_OTLP_HEADERS")
    tracing_enabled: bool = Field(default=True, alias="OTEL_TRACING_ENABLED")

    @property
    def required_key(self) -> str:
        """OpenTelemetry requires the endpoint to be configured."""
        return "endpoint"


class ProviderConfig:
    """Configuration for observability providers."""

    # Settings class mappings for each provider
    PROVIDER_SETTINGS: ClassVar[
        dict[ObservabilityProvider, type[BaseProviderSettings]]
    ] = {
        ObservabilityProvider.LANGFUSE: LangfuseSettings,
        ObservabilityProvider.LANGSMITH: LangsmithSettings,
        ObservabilityProvider.DATADOG: DatadogSettings,
        ObservabilityProvider.OPENTELEMETRY: OpenTelemetrySettings,
    }

    @classmethod
    def detect_provider(cls) -> ObservabilityProvider:
        """
        Auto-detect which observability provider is configured.

        Returns:
            ObservabilityProvider: The first detected provider or NONE
        """
        explicit = os.getenv("OBSERVABILITY_PROVIDER", "").strip().lower()
        if explicit:
            try:
                provider = ObservabilityProvider(explicit)
            except ValueError:
                provider = None
            else:
                if cls.is_provider_enabled(provider):
                    return provider
                return ObservabilityProvider.NONE

        for provider, settings_class in cls.PROVIDER_SETTINGS.items():
            settings = settings_class()
            if settings.is_configured():
                return provider

        return ObservabilityProvider.NONE

    @classmethod
    def is_provider_enabled(cls, provider: ObservabilityProvider) -> bool:
        """
        Check if a specific provider is enabled.

        Args:
            provider: The provider to check

        Returns:
            bool: True if the provider is properly configured
        """
        if provider == ObservabilityProvider.NONE:
            return False

        settings_class = cls.PROVIDER_SETTINGS.get(provider)
        if not settings_class:
            return False

        settings = settings_class()
        return settings.is_configured()

    @classmethod
    def get_provider_config(cls, provider: ObservabilityProvider) -> dict[str, Any]:
        """
        Get configuration for a specific provider.

        Args:
            provider: The provider to get config for

        Returns:
            dict: Configuration dictionary for the provider
        """
        settings_class = cls.PROVIDER_SETTINGS.get(provider)
        if not settings_class:
            return {}

        settings = settings_class()
        return settings.to_dict()
