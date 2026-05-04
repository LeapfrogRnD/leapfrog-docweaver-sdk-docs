"""Pipeline service for business logic."""

from app.config.settings import Settings
from app.core.common.schema import PaginationMetadata, PaginationParams
from app.core.common.service import BaseService
from app.core.pipelines.repository import PipelineRepository
from app.core.pipelines.schemas import (
    LLMProviderOption,
    ModelOption,
    PipelineConfigsResponse,
    PipelineCreateRequest,
    PipelineResponse,
    PipelineUpdateRequest,
    ProviderOption,
    StatsResponse,
    VLMProviderOption,
)
from app.db.models import Pipeline, User
from app.shared.constants.app_constants import (
    BEDROCK_MODEL_LABELS,
    BEDROCK_VLM_MODEL_LABELS,
    LLM_PROVIDER_LABELS,
    OCR_PROVIDER_LABELS,
    OPENAI_MODEL_LABELS,
    PARSING_METHOD_LABELS,
    VLM_PROVIDER_LABELS,
    BedrockModel,
    BedrockVLMModel,
    LLMProviderType,
    OCRProviderType,
    OpenAIModel,
    ParsingMethod,
    VLMProviderType,
)
from app.shared.exceptions.common import BadRequestException, NotFoundException


class PipelineService(BaseService):
    """Service for pipeline-related business logic."""

    def __init__(self, repository: PipelineRepository):
        super().__init__()
        self.repository = repository

    async def create_pipeline(
        self, request: PipelineCreateRequest, current_user: User
    ) -> PipelineResponse:
        """Create a new pipeline."""
        pipeline_data = request.model_dump()
        pipeline_data["created_by"] = current_user.id

        pipeline = await self.repository.create_pipeline(pipeline_data)
        return PipelineResponse.model_validate(pipeline)

    async def get_stats(self) -> StatsResponse:
        """Get stats for pipeline"""
        stats = await self.repository.get_stats()
        count, date = stats
        return StatsResponse(total=count, last_updated=date.strftime("%Y-%m-%d %H:%M:%S"))

    def get_configs(self, config: Settings) -> PipelineConfigsResponse:
        """
        Build the available pipeline configuration options.

        Azure OCR is included only when both azure_ocr_endpoint and azure_ocr_api_key
        are set.  OpenAI LLM is included only when openai_api_key is set.
        """
        return PipelineConfigsResponse(
            ocr_providers=self._build_ocr_providers(config),
            llm_providers=self._build_llm_providers(config),
            vlm_providers=self._build_vlm_providers(),
            parsing_methods=self._build_parsing_methods(),
        )

    def _build_ocr_providers(self, config: Settings) -> list[ProviderOption]:
        providers = [OCRProviderType.AWS_TEXTRACT, OCRProviderType.VLM]
        if config.azure_ocr_endpoint and config.azure_ocr_api_key:
            providers.insert(1, OCRProviderType.AZURE)
        return [ProviderOption(value=p, label=OCR_PROVIDER_LABELS[p]) for p in providers]

    def _build_llm_providers(self, config: Settings) -> list[LLMProviderOption]:
        available: dict = {LLMProviderType.BEDROCK: (BedrockModel, BEDROCK_MODEL_LABELS)}
        if config.openai_api_key:
            available[LLMProviderType.OPENAI] = (OpenAIModel, OPENAI_MODEL_LABELS)
        return [
            LLMProviderOption(
                value=provider,
                label=LLM_PROVIDER_LABELS[provider],
                models=[ModelOption(value=m.value, label=labels[m]) for m in model_enum],
            )
            for provider, (model_enum, labels) in available.items()
        ]

    def _build_vlm_providers(self) -> list[VLMProviderOption]:
        return [
            VLMProviderOption(
                value=VLMProviderType.BEDROCK,
                label=VLM_PROVIDER_LABELS[VLMProviderType.BEDROCK],
                models=[
                    ModelOption(value=m.value, label=BEDROCK_VLM_MODEL_LABELS[m])
                    for m in BedrockVLMModel
                ],
            )
        ]

    def _build_parsing_methods(self) -> list[ProviderOption]:
        return [
            ProviderOption(value=m.value, label=PARSING_METHOD_LABELS[m])
            for m in ParsingMethod
        ]

    async def get_pipeline_by_id(
        self, pipeline_id: int, current_user: User
    ) -> PipelineResponse:
        """Get pipeline by ID."""
        pipeline = await self.repository.get_pipeline_by_id(pipeline_id)
        if not pipeline:
            raise NotFoundException("Pipeline not found")
        self._validate_pipeline_permission(pipeline, current_user, "fetch")

        return PipelineResponse.model_validate(pipeline)

    async def get_all_pipelines(
        self, params: PaginationParams, current_user: User
    ) -> tuple[list[PipelineResponse], PaginationMetadata]:
        """Get all pipelines with pagination."""
        pipelines, meta = await self.repository.get_all_pipelines(params, current_user)
        return [
            PipelineResponse.model_validate(pipeline) for pipeline in pipelines
        ], meta

    async def update_pipeline(
        self, pipeline_id: int, request: PipelineUpdateRequest, current_user: User
    ) -> PipelineResponse:
        """Update pipeline by ID."""
        pipeline = await self._get_pipeline_or_raise(pipeline_id)

        self._validate_pipeline_permission(pipeline, current_user, "update")
        self._validate_not_default_pipeline(pipeline, "update")

        update_data = request.model_dump(exclude_unset=True)
        pipeline = await self.repository.update_pipeline(pipeline_id, update_data)

        if not pipeline:
            raise NotFoundException("Pipeline not found")

        return PipelineResponse.model_validate(pipeline)

    async def delete_pipeline(self, pipeline_id: int, current_user: User) -> None:
        """Delete pipeline by ID."""
        pipeline = await self._get_pipeline_or_raise(pipeline_id)

        self._validate_pipeline_permission(pipeline, current_user, "delete")
        self._validate_not_default_pipeline(pipeline, "delete")
        await self._validate_active_pipeline(pipeline, "delete")

        success = await self.repository.delete_pipeline(pipeline_id, current_user.id)
        if not success:
            raise NotFoundException("Pipeline not found")

    async def toggle_pipeline_status(
        self, pipeline_id: int, current_user: User
    ) -> PipelineResponse:
        pipeline_before_toggle = await self._get_pipeline_or_raise(pipeline_id)

        if not pipeline_before_toggle:
            raise NotFoundException("Pipeline not found")

        self._validate_pipeline_permission(
            pipeline_before_toggle, current_user, "toggle status"
        )
        self._validate_not_default_pipeline(pipeline_before_toggle, "toggle status")

        pipeline = await self.repository.toggle_pipeline_status(pipeline_id)

        return PipelineResponse.model_validate(pipeline)

    async def duplicate_pipeline(
        self, pipeline_id: int, current_user: User
    ) -> PipelineResponse:
        """Duplicate an existing pipeline with a new name."""
        await self._get_pipeline_or_raise(pipeline_id)

        # self._validate_pipeline_permission(pipeline, current_user, "duplicate")

        new_pipeline = await self.repository.duplicate_pipeline(
            pipeline_id, current_user.id
        )

        if not new_pipeline:
            raise NotFoundException("Original pipeline not found")

        return PipelineResponse.model_validate(new_pipeline)

    def _validate_pipeline_permission(
        self, pipeline: Pipeline, current_user: User, action: str
    ) -> None:
        """Validate that user has permission to perform action on pipeline."""
        if current_user.is_superuser:
            return

        if pipeline.created_by != current_user.id:
            raise BadRequestException(
                f"You can only {action} pipelines that you created"
            )

    def _validate_not_default_pipeline(self, pipeline: Pipeline, action: str) -> None:
        """Validate that the pipeline is not a default pipeline for destructive operations."""
        if pipeline.is_default:
            raise BadRequestException(f"Cannot {action} default pipelines")

    async def _validate_active_pipeline(self, pipeline: Pipeline, action: str) -> None:
        """Validate the pipeline is user by other task or not for destructibe operations"""
        if await self.repository.task_exists(pipeline.id):
            raise BadRequestException(
                f"Cannot {action} the pipeline while it is being used by existing tasks."
            )

    async def _get_pipeline_or_raise(self, pipeline_id: int) -> Pipeline:
        """Get pipeline by ID or raise NotFoundException."""
        pipeline = await self.repository.get_pipeline_by_id(pipeline_id)
        if not pipeline:
            raise NotFoundException("Pipeline not found")
        return pipeline
