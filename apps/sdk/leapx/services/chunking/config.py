# config for chunking technique
from pydantic import BaseModel, Field

from leapx.services.chunking.schemas import ChunkingMethod


class ChunkingConfig(BaseModel):
    """Configuration for PDF chunking.

    Args:
        method: Chunking technique to use.
        batch_size: Number of pages per chunk (must be >= 1).
    """

    method: ChunkingMethod = ChunkingMethod.BATCH_WISE
    batch_size: int = Field(default=5, ge=1, description="pages per batch")
