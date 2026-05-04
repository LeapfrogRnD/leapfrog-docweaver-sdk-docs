import asyncio

from collections.abc import AsyncIterator

from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:

    db_manager = request.app.state.db_manager

    if hasattr(db_manager, "is_initialized") and not db_manager.is_initialized():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database manager not initialized. Application is still starting up.",
        )

    async with db_manager.get_session() as session:
        yield session
