"""Configuration for OCR disk cache."""

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class CacheProviderType(str, Enum):
    """Supported cache types."""

    SQLITE = "sqlite"
    FILE = "file"


class CacheConfig(BaseModel):
    """
    Configuration for OCR disk cache.

    Attributes:
        enabled: Enable/disable caching (default: True)
        ttl: Time-to-live in seconds (default: 7 days, 0 = no expiration)
        size_limit: Maximum cache size in bytes (default: 5GB)
        eviction_policy: Cache eviction policy (default: least-recently-used)
    """

    enabled: bool = Field(
        default=True,
        description="Enable/disable caching",
    )

    provider: CacheProviderType = Field(
        default=CacheProviderType.SQLITE,
        description="Cache storage provider",
    )

    ttl: int = Field(
        default=604800,  # 7 days in seconds
        description="Time-to-live in seconds (0 = no expiration)",
    )
    size_limit: int = Field(
        default=5 * 1024 * 1024 * 1024,  # 5GB
        description="Maximum cache size in bytes",
    )
    eviction_policy: Literal["least-recently-used", "least-recently-stored"] = Field(
        default="least-recently-used",
        description="Cache eviction policy",
    )
