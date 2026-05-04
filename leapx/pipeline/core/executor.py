"""Pipeline execution logic."""

import asyncio
from typing import Any

from leapx.common.observability import observe
from leapx.common.observability.logger import logger
from leapx.pipeline.core.config import PipelineConfig
from leapx.pipeline.core.pool_manager import PoolManager
from leapx.pipeline.core.progress_tracker import ProgressTracker
from leapx.pipeline.core.response_builder import PipelineResponseBuilder
from leapx.pipeline.core.schemas.pipeline import ChunkContextProcessor
from leapx.pipeline.stages.base import BaseStage
from leapx.pipeline.stages.constants import (
    PREVIOUS_STAGE_SKIP_REASON,
    SKIP_REASON,
)
from leapx.pipeline.stages.schemas import TaskStatus
from leapx.services.chunking.schemas import ChunkResult

MULTIPROCESS_CHUNK_THRESHOLD = 20


class PipelineExecutor:
    """Executes pipeline stages dynamically.

    Orchestrates stage execution for each chunk, storing intermediate
    results and supporting flexible stage composition.

    Args:
        stages: List of stage instances to execute in order.
        config: Pipeline configuration instance.
        response_builder: Response builder utility.
        pool_manager: Optional pool manager to control concurrency.
        progress_tracker: Optional progress tracker for reporting.
    """

    def __init__(
        self,
        stages: list[BaseStage],
        config: PipelineConfig,
        response_builder: PipelineResponseBuilder,
        pool_manager: PoolManager | None = None,
        progress_tracker: ProgressTracker | None = None,
    ):
        self.stages = stages
        self.config = config
        self.response_builder = response_builder
        self.pool_manager = pool_manager or PoolManager()
        self.progress_tracker = progress_tracker or ProgressTracker()

    @property
    def stage_ids(self) -> list[str]:
        """Get ordered list of stage IDs."""
        return [stage.stage_id for stage in self.stages]

    async def _execute_stage(
        self,
        ctx: ChunkContextProcessor,
        stage: BaseStage,
        config: dict[str, Any],
    ) -> None:
        """Execute a single stage and update context.

        Args:
            ctx: Chunk processing context to update.
            stage: Stage to execute.
            config: Stage-specific configuration.
        """
        previous_output = {
            stage_id: {"output": result.output_data, "metadata": result.metadata}
            for stage_id, result in ctx.stage_results.items()
            if result.status == TaskStatus.COMPLETED
        }

        if ctx.previous_chunk_context:
            previous_output["_previous_chunk_context"] = ctx.previous_chunk_context

        ctx.set_stage_result(
            stage_id=stage.stage_id,
            stage_type=stage.__class__.__name__,
            status=TaskStatus.RUNNING,
            previous_output=previous_output,
        )

        self.progress_tracker.start_task(ctx.chunk_index, stage.stage_id)

        try:
            output = await stage.execute_dynamic(
                chunk=ctx.chunk,
                previous_output=previous_output,
                config=config,
            )

            ctx.set_stage_result(
                stage_id=stage.stage_id,
                stage_type=stage.__class__.__name__,
                output_data=output.data,
                status=TaskStatus.COMPLETED,
                metadata=output.metadata,
            )

            if output.skip_remaining:
                ctx.skip_remaining = True

            self.progress_tracker.complete_task(
                ctx.chunk_index,
                stage.stage_id,
                output.metadata,
                output,
            )

        except Exception as e:
            ctx.set_stage_result(
                stage_id=stage.stage_id,
                stage_type=stage.__class__.__name__,
                status=TaskStatus.FAILED,
                error=str(e),
            )
            logger.error(
                f"Stage {stage.stage_id} failed",
                error=str(e),
                chunk_index=ctx.chunk_index,
            )
            raise

    def _skip_stage(
        self, ctx: ChunkContextProcessor, stage: BaseStage, reason: str
    ) -> None:
        """Mark a stage as skipped."""
        ctx.set_stage_result(
            stage_id=stage.stage_id,
            stage_type=stage.__class__.__name__,
            status=TaskStatus.SKIPPED,
            metadata={SKIP_REASON: reason},
        )

        logger.info(
            f"Stage {stage.stage_id} skipped",
            reason=reason,
            chunk_index=ctx.chunk_index,
        )

    async def _process_chunk_core(
        self,
        ctx: ChunkContextProcessor,
        stage_config: dict[str, dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Process a single chunk through all stages.

        Args:
            ctx: The chunk processing context.
            stage_config: Optional per-stage configuration overrides.

        Returns:
            Mapping with the chunk index and built result payload.

        Raises:
            Exception: Propagates any unexpected error after marking progress state.
        """
        stage_config = stage_config or {}
        chunk_id = ctx.chunk.metadata.chunk_id
        self.progress_tracker.start_chunk(ctx.chunk_index, chunk_id)
        ctx.status = TaskStatus.RUNNING

        logger.info(
            f"Processing chunk {ctx.chunk_index + 1}/{ctx.total_chunks}",
            chunk_id=chunk_id,
        )

        try:
            for stage in self.stages:
                if ctx.skip_remaining:
                    self._skip_stage(ctx, stage, PREVIOUS_STAGE_SKIP_REASON)
                    continue

                await self._execute_stage(
                    ctx, stage, stage_config.get(stage.stage_id, {})
                )

            ctx.status = TaskStatus.COMPLETED
            self.progress_tracker.complete_chunk(ctx.chunk_index)
        except Exception as e:
            ctx.status = TaskStatus.FAILED
            self.progress_tracker.fail_chunk(ctx.chunk_index, str(e))
            raise
        else:
            return self._build_chunk_response(ctx)

    def _build_chunk_response(self, ctx: ChunkContextProcessor) -> dict[str, Any]:
        """Build final response for a chunk from its execution context.

        Args:
            ctx: Completed chunk processing context.

        Returns:
            Response dictionary for the chunk.
        """

        executed_stages = []
        stage_outputs = {}

        for stage_id, result in ctx.stage_results.items():
            if result.status != TaskStatus.COMPLETED:
                continue

            executed_stages.append(stage_id)

            if result.output_data:
                stage_outputs[stage_id] = result.output_data
        return ctx.response_builder.build(
            index=ctx.chunk_index,
            chunk=ctx.chunk,
            stage_outputs=stage_outputs,
        )

    def _process_chunk_sync(
        self,
        ctx: ChunkContextProcessor,
        stage_config: dict[str, dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Run the async core in a dedicated event loop (for multiprocessing).

        Args:
            ctx: Chunk processing context.
            stage_config: Optional per-stage configuration overrides.

        Returns:
            The result mapping produced by _process_chunk_core.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self._process_chunk_core(ctx, stage_config))
        finally:
            loop.close()

    @observe(capture_input=True, capture_output=True)
    async def execute(
        self,
        chunks: list[ChunkResult],
        stage_config: dict[str, dict[str, Any]] | None = None,
        enable_context: bool = False,
    ) -> dict[str, Any]:
        """Execute the pipeline asynchronously for all chunks.

        Chooses between in-process async concurrency and multi-process execution
        based on the number of chunks. If enable_context is True, processes chunks
        sequentially to maintain context.

        Args:
            chunks: Chunk results to process.
            stage_config: Optional per-stage configuration overrides.
            enable_context: If True, process chunks sequentially with context.

        Returns:
            Aggregated results for all chunks.
        """
        self.progress_tracker.start_pipeline(len(chunks))
        logger.info(
            "Starting pipeline execution",
            total_chunks=len(chunks),
            stages=self.stage_ids,
            enable_context=enable_context,
        )

        try:
            # Create contexts for each chunk
            contexts = [
                ChunkContextProcessor(
                    chunk_index=i,
                    chunk=c,
                    total_chunks=len(chunks),
                    response_builder=self.response_builder,
                )
                for i, c in enumerate(chunks)
            ]
            if enable_context:
                results = await self._execute_sequential_with_context(
                    contexts, stage_config
                )
            elif len(chunks) < MULTIPROCESS_CHUNK_THRESHOLD:
                tasks = [
                    self._process_chunk_core(ctx, stage_config) for ctx in contexts
                ]
                results = await self.pool_manager.run_concurrently(tasks)
            else:
                results = await self.pool_manager.run_in_concurrent_processes(
                    self._process_chunk_sync, [(ctx, stage_config) for ctx in contexts]
                )

        except Exception as e:
            self.progress_tracker.fail_pipeline(str(e))
            raise
        else:
            self.progress_tracker.complete_pipeline()
            logger.info("All chunks processed", total_chunks=len(chunks))
            return self.response_builder.build_final_result(results, self.stages)
        finally:
            await self.pool_manager.close()

    async def _execute_sequential_with_context(
        self,
        contexts: list[ChunkContextProcessor],
        stage_config: dict[str, dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute chunks sequentially, passing context from previous chunks.

        Args:
            contexts: List of chunk processing contexts.
            stage_config: Optional per-stage configuration overrides.

        Returns:
            List of chunk results.
        """
        results = []
        previous_context = None

        for ctx in contexts:
            if previous_context:
                ctx.previous_chunk_context = previous_context

            result = await self._process_chunk_core(ctx, stage_config)
            results.append(result)

            previous_context = self._build_context_for_next_chunk(ctx)

            logger.info(
                f"Completed chunk {ctx.chunk_index + 1}/{len(contexts)} with context",
                chunk_id=ctx.chunk.metadata.chunk_id,
            )

        return results

    def _build_context_for_next_chunk(
        self, ctx: ChunkContextProcessor
    ) -> dict[str, Any]:
        """Build context from current chunk for next chunk.

        Args:
            ctx: Current chunk processing context.

        Returns:
            Context dictionary for next chunk.
        """
        context = {
            "chunk_index": ctx.chunk_index,
            "chunk_id": ctx.chunk.metadata.chunk_id,
            "stages": {},
        }

        # Extract relevant outputs from each stage
        for stage_id, result in ctx.stage_results.items():
            if result.status == TaskStatus.COMPLETED and result.output_data:
                context["stages"][stage_id] = {
                    "output": result.output_data,
                    "metadata": result.metadata,
                }

        return context
