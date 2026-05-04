"""API key repository for database operations."""

from sqlalchemy import exists, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload, with_loader_criteria

from app.core.common.repository import BaseRepository
from app.core.common.schema import DataResultStatus, PaginationMetadata, PaginationParams
from app.db.models import ApiKey, ApiKeySecrets, User
from app.shared.exceptions.common import BadRequestException, NotFoundException
from app.shared.exceptions.user_exceptions import InsufficientPermissionsError


class ApiKeyRepository(BaseRepository):
    """Repository for API key-related database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_api_key(self, api_key_data: dict) -> ApiKey:
        """Create a new API key."""
        api_key = ApiKey(**api_key_data)
        self.session.add(api_key)
        await self.session.flush()
        return api_key

    async def create_api_key_secret(self, api_key_secret: dict) -> ApiKey:
        """Create a new API key."""
        api_key_secrets = ApiKeySecrets(**api_key_secret)
        self.session.add(api_key_secrets)
        await self.session.flush()
        return api_key_secrets

    async def get_api_key_by_id(
        self, api_key_id: int, user: User | None
    ) -> ApiKey | None:
        """Get API key by ID for a specific user."""
        stmt = select(ApiKey).where(ApiKey.id == api_key_id)
        if user is not None and not user.is_superuser:
            stmt = stmt.where(ApiKey.created_by == user.id)

        result = await self.session.execute(stmt)
        api_key = result.scalar_one_or_none()
        if not api_key and not user:
            raise NotFoundException("API key not found")
        if user and not api_key:
            raise InsufficientPermissionsError
        return api_key

    async def get_api_key_secret_value(self, secret_value: str) -> ApiKeySecrets | None:
        """Get API key by secret value."""
        stmt = (
            select(ApiKeySecrets)
            .options(joinedload(ApiKeySecrets.api_key))
            .where(ApiKeySecrets.secret_value == secret_value)
            .execution_options(include_deleted=True)
        )
        result = await self.session.execute(stmt)
        secret = result.scalar_one_or_none()
        if not secret:
            raise BadRequestException("Invalid API key")

        if secret.revoked_at is not None:
            raise BadRequestException("API key has been revoked")

        if secret.api_key.is_deleted:
            raise BadRequestException("The API key has been deleted")

        if secret.api_key.is_active is False:
            raise BadRequestException("The API key is inactive")
        return secret

    async def get_all_api_keys(
        self, params: PaginationParams
    ) -> tuple[list[ApiKey], PaginationMetadata]:
        """Get all API keys for a specific user."""
        stmt = (
            select(ApiKey)
            .options(
                selectinload(ApiKey.user).load_only(User.first_name, User.last_name)
            )
            .options(
                selectinload(ApiKey.api_key_secrets).load_only(
                    ApiKeySecrets.secret_value, ApiKeySecrets.created_at
                )
            )
            .options(
                with_loader_criteria(
                    ApiKeySecrets,
                    ApiKeySecrets.revoked_at.is_(None),
                    include_aliases=True,
                )
            )
            .order_by(ApiKey.created_at.desc())
        )
        if params.status != DataResultStatus.all:
            is_active = params.status == DataResultStatus.active
            stmt = stmt.where(ApiKey.is_active == is_active)

        if params.search:
            stmt = stmt.where(ApiKey.secret_name.ilike(f"%{params.search}%"))

        api_keys, meta = await self.paginate(self.session, stmt, params)

        return api_keys, meta

    async def delete_api_key(self, api_key_id: int, user: User) -> bool:
        """Delete an API key by ID for a specific user."""
        api_key = await self.get_api_key_by_id(api_key_id, user)

        api_key.soft_delete(user.id)
        self.session.add(api_key)

        await self.revoke_api_key_secrets(api_key_id, user.id)
        await self.session.flush()

    async def revoke_api_key_secrets(self, api_key_id: int, user_id: int) -> None:
        """Revoke all secrets for an API key."""
        select_stmt = select(ApiKeySecrets).where(
            ApiKeySecrets.api_key_id == api_key_id
        )
        result = await self.session.execute(select_stmt)
        api_key_secrets = result.scalars().all()
        for secret in api_key_secrets:
            secret.revoked_at = secret.created_at
            secret.revoked_by = user_id
            self.session.add(secret)
        await self.session.flush()

    async def update_api_key(self, key_id: int, payload: dict) -> ApiKey:
        smt = (
            update(ApiKey)
            .where(ApiKey.id == key_id)
            .values(**payload)
            .returning(ApiKey)
        )
        result = await self.session.execute(smt)
        return result.scalar_one()

    async def toggle_api_key_status(self, api_key_id: int, user: User) -> ApiKey:
        """Toggle the is_active status of an API key."""
        api_key = await self.get_api_key_by_id(api_key_id, user)
        api_key.is_active = not api_key.is_active
        await self.session.commit()
        await self.session.refresh(api_key)
        return api_key

    async def api_key_name_exists(
        self, secret_name: str, api_key_id: int | None = None
    ) -> bool:
        """Check if an API workflow with the same name already exists"""
        stmt = select(
            exists().where(
                (func.lower(ApiKey.secret_name) == secret_name.lower().strip())
                & (ApiKey.id != api_key_id if api_key_id else True)
                & (ApiKey.deleted_at.is_(None))
            )
        )
        result = await self.session.execute(stmt)
        if result.scalar():
            raise BadRequestException("API key with this name already exists")
