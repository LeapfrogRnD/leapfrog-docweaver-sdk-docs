"""Base repository with common database operations."""

from math import ceil

from sqlalchemy import Select, Sequence, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.schema import PaginationMetadata, PaginationParams
from app.logger import logger


class BaseRepository:
    def __init__(self) -> None:
        self.logger = logger

    async def paginate(
        self,
        session: AsyncSession,
        query: Select,
        params: PaginationParams,
        get_all: bool = False,
    ) -> tuple[Sequence, PaginationMetadata]:
        """
        Paginate a SQLAlchemy query asynchronously.

        Args:
            session: AsyncSession instance
            query: SQLAlchemy Select statement
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            Tuple of (items, page_info)
        """
        page_size = params.page_size
        page = params.page

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total_items = total_result.scalar() or 0

        total_pages = ceil(total_items / page_size) if total_items > 0 else 1
        offset = (page - 1) * page_size

        paginated_query = query.limit(page_size).offset(offset)
        result = await session.execute(paginated_query)

        items = result.all() if get_all else result.scalars().all()

        page_info = PaginationMetadata(
            page=page,
            page_size=page_size,
            total_items=total_items,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        )

        return items, page_info
