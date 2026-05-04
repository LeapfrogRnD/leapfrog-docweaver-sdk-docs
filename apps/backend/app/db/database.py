"""Database configuration and session management."""

from asyncio import current_task
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base

from app.config.settings import Settings
from app.logger import logger

Base = declarative_base()

_DB_NOT_INITIALIZED_MSG = "Database not initialized. Call initialize() first."


class DatabaseManager:
    """Manages database engine and session lifecycle."""

    def __init__(self):
        self._engine: AsyncEngine | None = None
        self._session_maker: async_sessionmaker[AsyncSession] | None = None
        self._scoped_session: async_scoped_session[AsyncSession] | None = None
        self._settings: Settings | None = None

    async def initialize(self, settings: Settings) -> None:
        """Initialize database engine and session maker with connection verification."""
        if self._engine is not None:
            logger.warning("Database already initialized")
            return

        self._settings = settings
        self._engine = create_async_engine(
            settings.db_url,
            echo=settings.db_echo,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
        )

        await self.health_check()

        self._session_maker = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

        self._scoped_session = async_scoped_session(
            self._session_maker,
            scopefunc=current_task,
        )

    async def health_check(self) -> None:
        """Check if database connection is healthy.

        Raises:
            RuntimeError: If database is not initialized
            Exception: If database connection fails
        """
        if self._engine is None:
            raise RuntimeError(_DB_NOT_INITIALIZED_MSG)

        try:
            async with self._engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            await self._engine.dispose()
            self._engine = None
            raise

    @property
    def engine(self) -> AsyncEngine:
        """Get database engine.

        Raises:
            RuntimeError: If database is not initialized
        """
        if self._engine is None:
            raise RuntimeError(_DB_NOT_INITIALIZED_MSG)
        return self._engine

    @property
    def session_maker(self) -> async_sessionmaker[AsyncSession]:
        """Get session maker.

        Raises:
            RuntimeError: If database is not initialized
        """
        if self._session_maker is None:
            raise RuntimeError(_DB_NOT_INITIALIZED_MSG)
        return self._session_maker

    @property
    def scoped_session(self) -> async_scoped_session[AsyncSession]:
        """Get scoped session factory.

        Raises:
            RuntimeError: If database is not initialized
        """
        if self._scoped_session is None:
            raise RuntimeError(_DB_NOT_INITIALIZED_MSG)
        return self._scoped_session

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session context manager.

        Usage:
            async with db_manager.session() as session:
                result = await session.execute(query)

        Yields:
            AsyncSession: Database session
        """
        session = self.scoped_session()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
            await self.scoped_session.remove()

    async def close(self) -> None:
        """Close database connections and cleanup."""
        if self._scoped_session:
            await self._scoped_session.remove()

        if self._engine:
            logger.info("Closing database connections...")
            await self._engine.dispose()
            self._engine = None
            self._session_maker = None
            self._scoped_session = None
            self._settings = None
            logger.info("Database connections closed")

    def is_initialized(self) -> bool:
        """Check if database is initialized."""
        return self._engine is not None
