"""API workflow service for business logic."""

from app.core.api_workflows.repository import ApiWorkflowsRepository
from app.core.api_workflows.schemas import (
    ApiWorkFlowCreateRequest,
    ApiWorkFlowListResponse,
    ApiWorkFlowResponse,
    ApiWorkFlowUpdateRequest,
)
from app.core.common.schema import PaginationMetadata, PaginationParams
from app.core.common.service import BaseService
from app.core.pipelines.schemas import BasePipelineRequest
from app.shared.constants.app_constants import OCRProviderType, TaskTypes
from app.shared.exceptions.common import BadRequestException
from app.shared.utils.schema_converters import (
    convert_classification_schema_to_json_schema,
    convert_extraction_schema_to_json_schema,
)


class ApiWorkFlowService(BaseService):
    """Service for API workflow-related business logic."""

    def __init__(self, repository: ApiWorkflowsRepository):
        super().__init__()
        self.repository = repository

    def _build_pipeline_config(self, request: ApiWorkFlowCreateRequest) -> dict:
        """Build pipeline_config dict from request pipeline fields."""
        pipeline_fields = set(BasePipelineRequest.model_fields)
        return {
            k: v
            for k, v in request.model_dump().items()
            if k in pipeline_fields and v is not None
        }

    def _build_response(self, api_workflow) -> ApiWorkFlowResponse:
        """Construct ApiWorkFlowResponse from DB model, exposing batch_size from pipeline_config."""
        pipeline_config = getattr(api_workflow, "pipeline_config", None) or {}
        task_metadata = (
            pipeline_config.get("task_metadata")
            if isinstance(pipeline_config, dict)
            else None
        )
        return ApiWorkFlowResponse.model_validate(
            {
                "id": api_workflow.id,
                "name": api_workflow.name,
                "workflow_type": api_workflow.workflow_type,
                "pipeline_config": pipeline_config,
                "additional_instruction": api_workflow.additional_instruction,
                "json_schema": api_workflow.json_schema,
                "task_metadata": task_metadata,
                "created_at": api_workflow.created_at,
            }
        )

    async def create_api_workflow(
        self, request: ApiWorkFlowCreateRequest, api_key_id: int
    ) -> ApiWorkFlowResponse:
        """Create a new API workflow."""
        self._validate_payload(request)
        await self.repository.check_workflow_name_exists(request.name)
        pipeline_config = self._build_pipeline_config(request)
        formatted_json_schema = {}
        if request.workflow_type == TaskTypes.EXTRACTION:
            formatted_json_schema = convert_extraction_schema_to_json_schema(
                request.json_schema
            )
        if request.workflow_type == TaskTypes.CLASSIFICATION:
            formatted_json_schema = convert_classification_schema_to_json_schema(
                request.json_schema
            )
        api_workflow = await self.repository.create_api_workflow(
            {
                "name": request.name,
                "workflow_type": request.workflow_type,
                "pipeline_config": pipeline_config,
                "additional_instruction": request.additional_instruction,
                "json_schema": request.json_schema,
                "formatted_json_schema": formatted_json_schema,
                "api_key_id": api_key_id,
            }
        )
        return self._build_response(api_workflow)

    async def get_all_api_workflows(
        self, api_key_id: int, page_params: PaginationParams
    ) -> tuple[list[ApiWorkFlowListResponse], PaginationMetadata]:
        """Get all API workflows for an API key."""
        api_workflows, meta = await self.repository.get_all_api_workflows(
            api_key_id, page_params
        )
        return [
            ApiWorkFlowListResponse(
                id=wf.id,
                name=wf.name,
                workflow_type=wf.workflow_type,
                task_metadata=(
                    (wf.pipeline_config or {}).get("task_metadata")
                    if isinstance(wf.pipeline_config, dict)
                    else None
                ),
                created_at=wf.created_at,
            )
            for wf in api_workflows
        ], meta

    async def get_api_workflow(
        self, workflow_id: int, api_key_id: int
    ) -> ApiWorkFlowResponse:
        """Get an API workflow by ID scoped to API key."""
        api_workflow = await self.repository.get_api_workflow_by_id(
            workflow_id, api_key_id
        )
        return self._build_response(api_workflow)

    async def update_api_workflow(
        self,
        request: ApiWorkFlowUpdateRequest,
        workflow_id: int,
        api_key_id: int,
    ) -> ApiWorkFlowResponse:
        """Update an API workflow."""
        self._validate_payload(request)
        await self.repository.get_api_workflow_by_id(workflow_id, api_key_id)
        await self.repository.check_workflow_name_exists(request.name, workflow_id)

        pipeline_config = self._build_pipeline_config(request)

        formatted_json_schema = {}
        if request.workflow_type == TaskTypes.EXTRACTION:
            formatted_json_schema = convert_extraction_schema_to_json_schema(
                request.json_schema
            )
        if request.workflow_type == TaskTypes.CLASSIFICATION:
            formatted_json_schema = convert_classification_schema_to_json_schema(
                request.json_schema
            )
        api_workflow = await self.repository.update_api_workflow(
            workflow_id,
            {
                "name": request.name,
                "workflow_type": request.workflow_type,
                "pipeline_config": pipeline_config,
                "additional_instruction": request.additional_instruction,
                "json_schema": request.json_schema,
                "formatted_json_schema": formatted_json_schema,
                "api_key_id": api_key_id,
            },
        )
        return self._build_response(api_workflow)

    async def delete_api_workflow(
        self, workflow_id: int, api_key_id: int, user_id: int | None = None
    ) -> None:
        """Soft delete an API workflow."""
        await self.repository.get_api_workflow_by_id(workflow_id, api_key_id)
        await self.repository.delete_api_workflow(workflow_id, user_id)

    def _validate_payload(
        self, request: ApiWorkFlowCreateRequest | ApiWorkFlowUpdateRequest
    ) -> None:
        if (
            request.workflow_type in [TaskTypes.EXTRACTION, TaskTypes.CLASSIFICATION]
            and not request.json_schema
        ):
            raise BadRequestException(
                f"json_schema is required for workflow type {request.workflow_type}"
            )
        if (
            request.ocr_provider == OCRProviderType.VLM.value
            and not request.vlm_model_provider
        ):
            raise BadRequestException(
                "vlm_model_provider is required when ocr_provider is vlm"
            )

        if request.ocr_provider == OCRProviderType.VLM.value and not request.vlm_model:
            raise BadRequestException("vlm_model is required when ocr_provider is vlm")
