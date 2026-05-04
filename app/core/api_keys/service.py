"""API key service for business logic."""

import secrets

from app.core.api_keys.repository import ApiKeyRepository
from app.core.api_keys.schemas import (
    ApiKeyCreateRequest,
    ApiKeyListResponse,
    ApiKeyResponse,
    ApiKeyUpdateRequest,
)
from app.core.api_workflow_jobs.repository import ApiWorkflowJobsRepository
from app.core.common.schema import PaginationMetadata, PaginationParams
from app.core.common.service import BaseService
from app.core.integration_apis.schemas import IntegrationListResponse, IntegrationStatsResponse
from app.core.task_workflow_job_runs.repository import TaskWorkflowJobRunsRepository
from app.db.models import User
from app.shared.constants.app_constants import Actions, Roles
from app.shared.exceptions.common import BadRequestException, ForbiddenException


class ApiKeyService(BaseService):
    """Service for API key-related business logic."""

    def __init__(
        self,
        repository: ApiKeyRepository,
        api_workflow_jobs_repository: ApiWorkflowJobsRepository,
        task_workflow_run_repository: TaskWorkflowJobRunsRepository,
    ):
        super().__init__()
        self.repository = repository
        self.api_workflow_jobs_repository = api_workflow_jobs_repository
        self.task_workflow_run_repository = task_workflow_run_repository

    async def create_api_key(self, request: ApiKeyCreateRequest, user: User) -> ApiKeyResponse:
        """Create a new API key."""
        self._validate_is_admin(user, Actions.CREATE)

        await self.repository.api_key_name_exists(request.secret_name)

        api_key = await self.repository.create_api_key(
            {
                "secret_name": request.secret_name,
                "webhook_url": str(request.webhook_url),
                "is_active": True,
                "created_by": user.id,
            }
        )

        await self.repository.create_api_key_secret(
            {
                "api_key_id": api_key.id,
                "secret_value": self.generate_secret(),
                "generated_by": user.id,
            }
        )

        return ApiKeyResponse.model_validate(api_key)

    async def get_all_api_keys(
        self, page_params: PaginationParams, user: User
    ) -> tuple[list[ApiKeyListResponse], PaginationMetadata]:
        """Get all API keys"""
        self._validate_is_admin(user, Actions.GET)
        api_keys, meta = await self.repository.get_all_api_keys(page_params)
        return [
            ApiKeyListResponse(
                id=api_key.id,
                secret_name=api_key.secret_name,
                secret_value=(
                    max(api_key.api_key_secrets, key=lambda s: s.created_at).secret_value
                    if api_key.api_key_secrets
                    else None
                ),
                created_by=api_key.created_by,
                is_active=api_key.is_active,
                last_used_at=api_key.last_used_at,
                created_at=api_key.created_at,
            )
            for api_key in api_keys
        ], meta

    async def get_api_key(self, key_id: int, user: User) -> ApiKeyResponse:
        self._validate_is_admin(user, Actions.GET)
        api_key = await self.repository.get_api_key_by_id(key_id, None)
        return ApiKeyResponse.model_validate(api_key)

    async def update_api_key(
        self, request: ApiKeyUpdateRequest, key_id: int, user: User
    ) -> ApiKeyResponse:
        self._validate_is_admin(user, Actions.UPDATE)
        await self.repository.api_key_name_exists(request.secret_name, key_id)
        await self.repository.get_api_key_by_id(key_id, None)

        api_key = await self.repository.update_api_key(
            key_id,
            {
                "secret_name": request.secret_name,
                "webhook_url": str(request.webhook_url),
            },
        )
        return ApiKeyResponse.model_validate(api_key)

    async def delete_api_key(self, api_key_id: int, user: User) -> None:
        """Delete an API key."""
        self._validate_is_admin(user, Actions.DELETE)
        await self.repository.delete_api_key(api_key_id, user)

    async def toggle_api_key_status(self, api_key_id: int, user: User) -> ApiKeyResponse:
        """Toggle the active/inactive status of an API key."""
        self._validate_is_admin(user, Actions.TOGGLE)
        api_key = await self.repository.toggle_api_key_status(api_key_id, user)
        return ApiKeyResponse.model_validate(api_key)

    async def regenerate_api_key_secret(self, api_key_id: int, user: User):
        """Regenerate API key secret."""
        self._validate_is_admin(user, Actions.REGENERATE)

        api_key = await self.repository.get_api_key_by_id(api_key_id, None)

        if not api_key.is_active:
            raise BadRequestException("Cannot regenerate secret for an inactive API key")

        await self.repository.revoke_api_key_secrets(api_key_id, user.id)

        await self.repository.create_api_key_secret(
            {
                "api_key_id": api_key.id,
                "secret_value": self.generate_secret(),
                "generated_by": user.id,
            }
        )

    def _validate_is_admin(self, user: User, action: str) -> bool:
        if user.role != Roles.ADMIN:
            raise ForbiddenException(f"Only admin users can {action} API keys")

    async def get_all_integrations(
        self,
        api_key_id: int,
        params: PaginationParams,
    ) -> tuple[list[IntegrationListResponse], PaginationMetadata]:
        """Get all tasks with filters and pagination, irrespective of roles."""
        (
            integrations,
            metadata,
        ) = await self.api_workflow_jobs_repository.get_all_api_workflow_jobs_by_api_key_id(
            api_key_id=api_key_id,
            params=params,
        )

        return [
            IntegrationListResponse(
                job_id=integrate.api_job_id,
                name=integrate.api_workflow.name if integrate.api_workflow else "N/A",
                status=integrate.lastest_job_run.status if integrate.lastest_job_run else "N/A",
                type=integrate.api_workflow.workflow_type if integrate.api_workflow else "N/A",
                created_at=integrate.created_at,
            )
            for integrate in integrations
            if integrate.lastest_job_run is not None
        ], metadata

    async def get_integration_stats(self, api_key_id: int) -> IntegrationStatsResponse:
        """Get task statistics grouped by status."""
        response = await self.task_workflow_run_repository.get_stats(api_key_id)
        return IntegrationStatsResponse.model_validate(response)

    def generate_secret(self) -> str:
        """Generate a new API key secret value."""
        return f"lpx_{secrets.token_urlsafe(32).replace('_', '').replace('-', '')}"
