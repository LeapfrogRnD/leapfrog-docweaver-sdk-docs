from typing import Annotated

from fastapi import Depends, Request

from app.providers.queues.base import QueueProvider
from app.providers.storage.base import StorageInterface


async def get_queue_provider(
    request: Request,
) -> QueueProvider:
    """Get queue instance based on configuration."""
    return request.app.state.queue_provider


QueueProviderDep = Annotated[StorageInterface, Depends(get_queue_provider)]
