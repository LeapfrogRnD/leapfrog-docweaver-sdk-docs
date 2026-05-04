"""Pipeline response builder."""

from dataclasses import is_dataclass
from typing import Any

from pydantic import BaseModel

from leapx.pipeline.core.config import PipelineConfig
from leapx.pipeline.stages.constants import (
    COMBINED_TEXT,
    EXTRACTION_RESPONSE,
    OCR_DATA_LIST,
)
from leapx.pipeline.stages.layers import Stage
from leapx.pipeline.stages.schemas import StageName
from leapx.services.chunking.schemas import ChunkMetaData, ChunkResult
from leapx.services.extractor.schemas import ExtractionResponse
from leapx.services.layout_parser.utils.view_conversion import ocrdata_to_view


class PipelineResponseBuilder:
    """Builds standardized pipeline responses.

    Wraps serialization and metadata construction for chunk-level results,
    ensuring a consistent output contract across pipeline runs.

    Args:
        config: Pipeline configuration used to enrich metadata.
    """

    def __init__(self, config: PipelineConfig):
        self.config = config

    def build(
        self,
        index: int,
        chunk: ChunkResult,
        stage_outputs: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build the pipeline response for a single chunk.

        Args:
            index: Chunk index.
            chunk: Chunk information and metadata.
            stage_outputs: Dict mapping stage IDs to their output data.

        Returns:
            A dictionary with chunk-level results, metadata, and stage info.
        """
        stage_outputs = stage_outputs or {}
        stage_results = self._build_stage_results(stage_outputs)
        return {
            "chunk_index": index,
            "chunk_id": chunk.metadata.chunk_id,
            "page_numbers": {
                "start": chunk.metadata.start_page,
                "end": chunk.metadata.end_page,
            },
            "total_pages": chunk.metadata.end_page - chunk.metadata.start_page,
            **stage_results,
        }

    def build_final_result(
        self,
        results: list,
        stages: list[Stage],
    ):
        """Build the pipeline response for final result.

        Args:
            results: Prepared result for each chunk.
            stages: Requested stages to run in pipeline.

        Returns:
            A dictionary with chunk-level results, and stage used.
        """
        return {
            "pipeline_results": results,
            "pipeline_stages": self._normalize_stage_names(stages=stages),
        }

    def _normalize_stage_names(self, stages: list) -> list[str]:
        """Convert stage names to string values.

        Args:
            stages: List of stage names (may be StageName enum or str).

        Returns:
            List of string stage names.
        """
        return [
            stage.name.value if isinstance(stage.name, StageName) else stage
            for stage in stages
        ]

    def _build_stage_results(self, stage_outputs: dict[str, Any]) -> dict[str, Any]:
        """Build serialized stage results from outputs.

        Applies special transformations for known stage types.

        Args:
            stage_outputs: Dict mapping stage IDs to their outputs.

        Returns:
            Dict with serialized stage results.
        """
        results = {}
        for stage_id, output in stage_outputs.items():
            stage_name = stage_id.value if isinstance(stage_id, StageName) else stage_id
            if stage_name == StageName.ocr.value:
                ocr_data_list = (
                    output.get(OCR_DATA_LIST, []) if isinstance(output, dict) else []
                )
                results[stage_name] = (
                    ocrdata_to_view(ocr_data_list) if ocr_data_list else []
                )
            elif stage_name == StageName.parser:
                combined_text = (
                    output.get(COMBINED_TEXT, "") if isinstance(output, dict) else ""
                )
                results[stage_name] = combined_text
            elif stage_name == StageName.extraction or EXTRACTION_RESPONSE in output:
                results[stage_name] = self._serialize(output[EXTRACTION_RESPONSE])
            else:
                results[stage_name] = self._serialize(output)
        return results

    def _serialize(self, data: Any) -> Any:  # noqa:PLR0911
        """Serialize heterogeneous data to a JSON-compatible form.

        Handles:
            - None
            - List (recursive)
            - ExtractionResponse (special handling for data + metadata)
            - Pydantic BaseModel
            - dataclass
            - Objects with .model_dump method
            - Dict/other types (passthrough)

        Args:
            data: Any object to serialize.

        Returns:
            JSON-serializable representation of the input.
        """
        if data is None:
            return None
        if isinstance(data, list):
            return [self._serialize(item) for item in data]

        if isinstance(data, ExtractionResponse):
            return {
                "data": self._serialize(data.data),
                "metadata": data.metadata,
            }

        if (
            hasattr(data, "data")
            and hasattr(data, "metadata")
            and not isinstance(data, BaseModel)
        ):
            return {
                "data": self._serialize(data.data),
                "metadata": self._serialize(data.metadata),
            }

        if isinstance(data, BaseModel):
            return data.model_dump(mode="json")

        if hasattr(data, "model_dump"):
            return data.model_dump(mode="json")

        if is_dataclass(data):
            return data.to_json()
        return data

    def _build_metadata(self, chunk: ChunkMetaData) -> dict[str, Any]:
        """Build response metadata from a chunk metadata object.

        Args:
            chunk: Chunk metadata instance.

        Returns:
            Metadata mapping with model and generation settings.
        """
        total_pages = chunk.page_count
        return {
            "model": (
                self.config.llm_extraction_config.model.value
                if hasattr(self.config.llm_extraction_config.model, "value")
                else str(self.config.llm_extraction_config.model)
            ),
            "temperature": self.config.llm_extraction_config.temperature,
            "max_tokens": self.config.llm_extraction_config.max_tokens,
            "total_pages": total_pages,
        }
