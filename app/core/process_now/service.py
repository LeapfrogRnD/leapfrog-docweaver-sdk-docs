"""Process-now service — synchronous inline document processing (no worker queue)."""

import asyncio
import uuid
from typing import Any

from app.config.settings import Settings
from app.core.common.service import BaseService
from app.core.pipelines.repository import PipelineRepository
from app.core.process_now.exceptions import (
    DocumentProcessingException,
    InactivePipelineException,
    ProcessingTimeoutException,
    UnsupportedTaskTypeException,
)
from app.core.process_now.schemas import (
    SUPPORTED_TASK_TYPES,
    ProcessNowRequest,
    ProcessNowResponse,
)
from app.providers.storage.base import StorageInterface
from app.shared.constants.app_constants import LLMProviderType, TaskTypes
from app.shared.exceptions.common import NotFoundException
from app.shared.utils.schema_converters import (
    convert_classification_schema_to_json_schema,
    convert_extraction_schema_to_json_schema,
)

# Maximum wall-clock seconds we will wait for the LeapFrog DocWeaver pipeline to finish
# before returning a 429 so the caller can fall back to the async flow.
DEFAULT_PROCESSING_TIMEOUT_SECONDS = 120


class ProcessNowService(BaseService):
    """
    Executes document processing synchronously within the HTTP request lifetime.

    Flow
    ----
    1. Validate & resolve the pipeline configuration (DB lookup or inline config).
    2. Upload the binary file to storage under a temporary key.
    3. Build the LeapFrog DocWeaver pipeline kwargs exactly as the worker does.
    4. Call the appropriate LeapFrog DocWeaver SDK method under an asyncio timeout.
    5. Format and return results — then clean up the temp file.

    No job-run records are written; this is a pure stateless, fire-and-respond call.
    """

    def __init__(
        self,
        pipeline_repository: PipelineRepository,
        storage: StorageInterface,
        settings: Settings,
        timeout_seconds: int = DEFAULT_PROCESSING_TIMEOUT_SECONDS,
    ):
        super().__init__()
        self.pipeline_repository = pipeline_repository
        self.storage = storage
        self.settings = settings
        self.timeout_seconds = timeout_seconds

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    async def process(
        self,
        request: ProcessNowRequest,
        file_bytes: bytes,
        filename: str,
        content_type: str,
    ) -> ProcessNowResponse:
        """
        Synchronously process *file_bytes* and return structured results.

        Parameters
        ----------
        request:      Validated ProcessNowRequest (task_type, json_schema, pipeline source).
        file_bytes:   Raw bytes of the uploaded document.
        filename:     Original filename (used to derive the extension).
        content_type: MIME type of the file.
        """
        if request.task_type not in SUPPORTED_TASK_TYPES:
            raise UnsupportedTaskTypeException(request.task_type, SUPPORTED_TASK_TYPES)

        # 1. Resolve pipeline config ----------------------------------------
        execution_config, resolved_pipeline_id = await self._resolve_pipeline_config(
            request
        )

        # 2. Convert user-facing json_schema to the LeapFrog DocWeaver internal schema ----
        formatted_schema = self._convert_schema(request.task_type, request.json_schema)
        execution_config["formatted_json_schema"] = formatted_schema
        if request.additional_instructions:
            execution_config["additional_instructions"] = (
                request.additional_instructions
            )
        else:
            execution_config["additional_instructions"]="Task: Please provide consise summary of the data"

        # 3. Upload temp file to storage -------------------------------------
        file_key = await self._upload_temp_file(file_bytes, filename, content_type)

        # 4. Build the document path the LeapFrog DocWeaver SDK understands ---------------
        document_path = self._build_document_path(file_key)

        # 5. Run inline with timeout -----------------------------------------
        try:
            raw_results = await self._run_with_timeout(
                request.task_type, document_path, execution_config
            )
        finally:
            # Always clean up the temp file, even on error
            await self._cleanup_temp_file(file_key)

        # 6. Format and return -----------------------------------------------
        results = self._format_results(request.task_type, raw_results)

        return ProcessNowResponse(
            task_type=request.task_type,
            pipeline_id=resolved_pipeline_id,
            results=results,
            page_count=len(raw_results),
            processing_metadata={
                "llm_model": execution_config.get("llm_model"),
                "llm_model_provider": execution_config.get("llm_model_provider"),
                "ocr_provider": execution_config.get("ocr_provider"),
                "parsing_method": execution_config.get("parsing_method"),
                "timeout_seconds": self.timeout_seconds,
                "additional_instructions": execution_config.get(
                    "additional_instructions"
                ),
            },
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _resolve_pipeline_config(
        self, request: ProcessNowRequest
    ) -> tuple[dict[str, Any], int | None]:
        """
        Return (execution_config_dict, resolved_pipeline_id).

        If pipeline_id is given, load the Pipeline row and validate it is active.
        If pipeline_config is given, use it directly.
        """
        if request.pipeline_id is not None:
            pipeline = await self.pipeline_repository.get_pipeline_by_id(
                request.pipeline_id
            )
            if not pipeline:
                raise NotFoundException(f"Pipeline {request.pipeline_id} not found.")
            if not pipeline.is_active:
                raise InactivePipelineException(request.pipeline_id)

            config = {
                "ocr_provider": pipeline.ocr_provider,
                "parsing_method": pipeline.parsing_method,
                "vlm_model_provider": pipeline.vlm_model_provider,
                "vlm_model": pipeline.vlm_model,
                "llm_model_provider": pipeline.llm_model_provider,
                "llm_model": pipeline.llm_model,
            }
            return config, pipeline.id

        # Inline config path
        cfg = request.pipeline_config
        config = {
            "ocr_provider": cfg.ocr_provider,
            "parsing_method": cfg.parsing_method,
            "vlm_model_provider": cfg.vlm_model_provider,
            "vlm_model": cfg.vlm_model,
            "llm_model_provider": cfg.llm_model_provider,
            "llm_model": cfg.llm_model,
        }
        return config, None

    def _convert_schema(
        self, task_type: str, json_schema: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Convert the user-facing schema to the LeapFrog DocWeaver internal format."""
        if task_type == TaskTypes.EXTRACTION:
            return convert_extraction_schema_to_json_schema(json_schema)
        if task_type == TaskTypes.CLASSIFICATION:
            return convert_classification_schema_to_json_schema(json_schema)
        # Summarization does not use a structured schema
        return None

    async def _upload_temp_file(
        self, file_bytes: bytes, filename: str, content_type: str
    ) -> str:
        """Upload file to storage under a unique temp key and return the key."""
        ext = filename.rsplit(".", 1)[-1] if "." in filename else "pdf"
        file_key = f"process_now/tmp/{uuid.uuid4()}.{ext}"
        try:
            await self.storage.upload(
                content=file_bytes,
                filename=file_key,
                content_type=content_type,
            )
        except Exception as exc:
            raise DocumentProcessingException(
                f"Failed to upload document to temporary storage: {exc}"
            ) from exc
        return file_key

    def _build_document_path(self, file_key: str) -> str:
        """Return the absolute local path the LeapFrog DocWeaver SDK expects."""
        from pathlib import Path

        return str(Path(self.settings.local_storage_path) / file_key)

    @staticmethod
    def _get_llm_provider(llm_model: str | None) -> str:
        """
        Derive the provider string the LeapFrog DocWeaver SDK expects from the model name.
        Mirrors the same helper in doc_processor/utils/provider.py.
        """
        if llm_model and "gpt" in llm_model.lower():
            return LLMProviderType.OPENAI  # "openai"
        return LLMProviderType.BEDROCK  # "bedrock"

    @staticmethod
    def _normalize_provider(provider: Any) -> str | None:
        """Return a LeapFrog DocWeaver-compatible provider string (or None)."""
        if provider is None:
            return None
        provider_str = str(provider).strip().lower()
        return provider_str or None

    async def _run_with_timeout(
        self,
        task_type: str,
        document_path: str,
        execution_config: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Dispatch to the LeapFrog DocWeaver linear_pipeline and enforce a hard timeout."""
        try:
            from leapx import Stage, linear_pipeline
        except ImportError as exc:
            raise DocumentProcessingException(
                f"LeapFrog DocWeaver SDK is not installed: {exc}"
            ) from exc

        ocr_provider = execution_config.get("ocr_provider")
        llm_model = execution_config.get("llm_model")
        use_generation = task_type == TaskTypes.SUMMARIZATION

        # Prefer explicit provider from config; fall back to deriving from model name.
        configured_llm_provider = self._normalize_provider(
            execution_config.get("llm_model_provider")
        )
        llm_provider = configured_llm_provider or (
            self._get_llm_provider(llm_model) if llm_model else None
        )

        # Build stage list — mirrors doc_processor/utils/provider.py build_pipeline_kwargs
        stages = (
            [Stage.VLM_PARSER] if ocr_provider == "vlm" else [Stage.OCR, Stage.PARSER]
        )
        stages.append(Stage.LLM_GENERATION if use_generation else Stage.LLM_EXTRACTION)

        batch_size = 1

        pipeline_kwargs: dict[str, Any] = {
            "json_schema": execution_config.get("formatted_json_schema"),
            "additional_instructions": execution_config.get("additional_instructions"),
            "llm_model": llm_model,
            "llm_provider": llm_provider,
            "stages": stages,
            "max_tokens": 30000,
            "chunking_config": {"batch_size": batch_size},
            "llm_cache_config": {"enabled": False},
            "ocr_cache_config": {"enabled": False},
            "enable_context": True,
        }

        if ocr_provider and ocr_provider != "vlm":
            pipeline_kwargs["ocr_provider"] = ocr_provider

        pipeline = linear_pipeline(**pipeline_kwargs)

        try:
            result = await asyncio.wait_for(
                pipeline.async_run(input_data=document_path),
                timeout=self.timeout_seconds,
            )
        except TimeoutError as exc:
            raise ProcessingTimeoutException(self.timeout_seconds) from exc
        except Exception as exc:
            raise DocumentProcessingException(str(exc)) from exc

        raw_items = result.get("pipeline_results", [])
        result_key = "generation" if use_generation else "extraction"
        return [
            {"result": item.get(result_key, {}), "pages": item.get("page_numbers", {})}
            for item in raw_items
        ]

    async def _cleanup_temp_file(self, file_key: str) -> None:
        """Best-effort deletion of the temporary storage file."""
        try:
            await self.storage.delete(file_key)
        except Exception as exc:
            self.logger.warning(
                f"process_now: failed to delete temp file '{file_key}': {exc}"
            )

    def _format_results(
        self, task_type: str, raw_results: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Normalise raw LeapFrog DocWeaver pipeline_results into the ProcessNowResponse shape.

        Mirrors the formatting logic in TaskService.get_task_results and
        IntegrationService.poll_integration_task.
        """
        formatted: list[dict[str, Any]] = []

        for item in raw_results:
            pg_no = item.get("pages", {}).get("start", 0) + 1
            if task_type == TaskTypes.SUMMARIZATION:
                formatted.append(
                    {
                        "pg_no": pg_no,
                        "summary": item.get("result", {}).get(
                            "generation_response", {}
                        ),
                    }
                )
            else:
                result_data = item.get("result", {})
                # Strip internal telemetry key added by the SDK
                result_data.pop("input_text_length", None)
                data = result_data.get("data", result_data)
                formatted.append({"pg_no": pg_no, **data})

        return formatted
