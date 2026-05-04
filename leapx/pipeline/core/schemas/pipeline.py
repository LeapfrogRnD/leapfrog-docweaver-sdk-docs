from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from leapx.pipeline.core.response_builder import PipelineResponseBuilder
from leapx.pipeline.stages.schemas import StageExecutionResult, TaskStatus
from leapx.services.chunking.schemas import ChunkResult


class ChunkContextProcessor(BaseModel):
    """Context for processing a chunk with intermediate stage results storage."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    chunk_index: int
    chunk: ChunkResult
    total_chunks: int
    response_builder: PipelineResponseBuilder
    stage_results: dict[str, StageExecutionResult] = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    skip_remaining: bool = False
    previous_output: list = []
    previous_chunk_context: dict | None = None

    def get_stage_output(self, stage_id: str) -> dict | None:
        """Get output from a completed stage.

        Args:
            stage_id: The stage identifier to retrieve output from.

        Returns:
            The stage output data if completed, None otherwise.
        """
        result = self.stage_results.get(stage_id)
        if result and result.status == TaskStatus.COMPLETED:
            return result.output_data
        return None

    def set_stage_result(  # noqa: PLR0913
        self,
        stage_id: str,
        stage_type: str,
        output_data: dict | None = None,
        status: TaskStatus = TaskStatus.COMPLETED,
        metadata: dict | None = None,
        previous_output: list | None = None,
        error: str | None = None,
    ) -> None:
        """Store a stage result.

        Args:
            stage_id: str .
            stage_type: The stage class name.
            output_data: The output data produced by the stage.
            status: The execution status.
            metadata: Optional metadata about the execution.
            previous_output: list of previous output,
            error: Optional error message if failed.
        """
        result = self.stage_results.get(stage_id)

        if not result:
            result = StageExecutionResult(stage_id=stage_id, stage_type=stage_type)
            self.stage_results[stage_id] = result

        result.status = status
        result.output_data = output_data
        result.error = error
        result.completed_at = datetime.now()
        result.previous_outputs = previous_output
        if metadata:
            result.metadata.update(metadata)
