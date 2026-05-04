from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.db_session import get_db_session
from app.core.api_keys.repository import ApiKeyRepository
from app.db.models import ApiKeySecrets
from app.shared.exceptions.common import NotFoundException


async def validate_api_key(
    api_key: str = Header(..., alias="X-API-Key"),
    session: AsyncSession = Depends(get_db_session),
) -> ApiKeySecrets:
    """
    Validate API key from header and return the corresponding ApiKey object.
     Raises an exception if the API key is invalid.
    """
    if not api_key:
        raise NotFoundException("API key is required")
    api_key_repo = ApiKeyRepository(session)
    return await api_key_repo.get_api_key_secret_value(api_key.strip())


ValidateApiKeyDep = Annotated[ApiKeySecrets, Depends(validate_api_key)]
