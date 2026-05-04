"""Queue provider factory for dynamic initialization."""

from typing import ClassVar

from app.config.settings import Settings
from app.logger import logger
from app.providers.queues.base import QueueProvider
from app.providers.queues.sqs_queue import SQSQueue


class QueueProviderFactory:
    """Factory class for creating queue provider instances."""

    _providers: ClassVar[dict[str, type[QueueProvider]]] = {"sqs": SQSQueue}

    @classmethod
    def create(cls, settings: Settings) -> QueueProvider | None:
        """
        Create and initialize the appropriate queue provider based on settings.
        """
        queue_type = settings.queue_provider.lower().strip()

        if not queue_type or queue_type == "none":
            logger.info("No queue provider configured")
            return None

        provider_class = cls._providers.get(queue_type)

        if provider_class is None:
            supported = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unsupported queue provider: '{queue_type}'. "
                f"Supported providers: {supported}, none"
            )

        try:
            return provider_class(settings=settings).initialize()

        except Exception as e:
            logger.error(
                "Failed to initialize queue provider",
                provider_type=queue_type,
                error=str(e),
            )
            raise

    @classmethod
    def register_provider(cls, name: str, provider_class: type[QueueProvider]) -> None:
        """
        Register a new queue provider type.
        """
        cls._providers[name.lower()] = provider_class
        logger.info(f"Registered queue provider: {name}")

    @classmethod
    def get_supported_providers(cls) -> list[str]:
        """
        Get list of supported queue provider types.

        Returns:
            List of supported provider names
        """
        return list(cls._providers.keys())
