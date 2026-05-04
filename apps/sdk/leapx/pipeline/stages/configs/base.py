from pydantic_settings import BaseSettings

from leapx.common.cache.cache_config import CacheConfig
from leapx.services.credentials.base import Credential


class BlockConfig(BaseSettings):
    cache_config: CacheConfig | None = None
    credential: Credential | None = None
