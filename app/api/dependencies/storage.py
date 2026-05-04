from typing import Annotated

from fastapi import Depends, Request

from app.providers.storage.base import StorageInterface


def get_storage(
    request: Request,
) -> StorageInterface:
    """Get storage instance based on configuration."""
    return request.app.state.storage_provider


StorageDep = Annotated[StorageInterface, Depends(get_storage)]
