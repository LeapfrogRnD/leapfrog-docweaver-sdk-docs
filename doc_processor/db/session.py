"""Database session management - reuses main app's database configuration."""

from config.settings import settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from utils.logger import log

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    poolclass=NullPool if settings.ENVIRONMENT == "test" else None,
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncSession:
    """Get a database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            log.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database connection."""
    try:
        async with engine.begin():
            log.info("Database connection established successfully")
    except Exception as e:
        log.error(f"Failed to connect to database: {e}")
        raise


async def close_db():
    """Close database connection pool."""
    await engine.dispose()
    log.info("Database connection pool closed")
