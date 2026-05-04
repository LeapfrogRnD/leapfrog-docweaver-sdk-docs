"""Database seeders module."""

from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from app.logger import logger


class BaseSeeder(ABC):
    """Base class for all seeders."""

    @abstractmethod
    async def seed(self, session: AsyncSession) -> None:
        """
        Execute the seeding logic.

        Args:
            session: Database session
        """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the seeder name."""

    @property
    def order(self) -> int:
        """
        Return the execution order (lower numbers run first).
        Default is 100.
        """
        return 100


class SeederRegistry:
    """Registry to manage all seeders."""

    _seeders: list[type[BaseSeeder]] = []  # noqa: RUF012

    @classmethod
    def register(cls, seeder_class: type[BaseSeeder]) -> type[BaseSeeder]:
        """
        Register a seeder class.
        Args:
            seeder_class: Seeder class to register
        Returns:
            The registered seeder class
        """
        cls._seeders.append(seeder_class)
        logger.debug(f"Registered seeder: {seeder_class.__name__}")
        return seeder_class

    @classmethod
    def get_seeders(cls) -> list[type[BaseSeeder]]:
        """
        Get all registered seeders sorted by execution order.
        Returns:
            List of seeder classes sorted by order
        """
        return sorted(cls._seeders, key=lambda s: s().order)

    @classmethod
    def clear(cls) -> None:
        """Clear all registered seeders (useful for testing)."""
        cls._seeders = []


def register_seeder(order: int = 100):
    """
    Decorator to register a seeder with optional execution order.

    Args:
        order: Execution order (lower numbers run first)
    Example:
        @register_seeder(order=1)
        class MySeeder(BaseSeeder):
            ...
    """

    def decorator(seeder_class: type[BaseSeeder]) -> type[BaseSeeder]:
        # Override the order property if specified
        if order != 100:  # noqa: PLR2004
            seeder_class.order = property(lambda self: order)  # type: ignore  # noqa: ARG005
        return SeederRegistry.register(seeder_class)

    return decorator


__all__ = ["BaseSeeder", "SeederRegistry", "register_seeder"]
