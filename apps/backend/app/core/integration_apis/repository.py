from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.repository import BaseRepository


class IntegrationRepository(BaseRepository):
    """Repository for integration-related database operations."""

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session
