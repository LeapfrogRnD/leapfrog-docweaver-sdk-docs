"""Progress tracking for pipeline execution."""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from leapx.pipeline.core.schemas.progress_tracker import (
    ChunkProgress,
    PipelineProgress,
    TaskProgress,
    TaskStatus,
)


class ProgressTracker:
    """Tracks and persists pipeline progress to a JSON file."""

    TASK_OCR = "ocr"
    TASK_LAYOUT_PARSING = "parser"  # Match StageName.parser
    TASK_EXTRACTION = "extraction"

    def __init__(
        self, output_dir: str = "/tmp/pipeline_results", pipeline_id: str | None = None
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pipeline_id = pipeline_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.progress_file = self.output_dir / f"progress_{self.pipeline_id}.json"
        self.progress: PipelineProgress | None = None

    def _now(self) -> str:
        """Get current timestamp as ISO string."""
        return datetime.now().isoformat()

    def _calculate_duration(self, started_at: str | None) -> float | None:
        """Calculate duration in seconds from start time to now."""
        if not started_at:
            return None
        start = datetime.fromisoformat(started_at)
        return (datetime.now() - start).total_seconds()

    def _save(self) -> None:
        """Save progress to JSON file."""
        if self.progress:
            with self.progress_file.open("w") as f:
                json.dump(self.progress.model_dump(), f, indent=2, default=str)

    def _normalize_task_name(self, task_name: str | Enum) -> str:
        """Convert task name to string, handling Enum values."""
        if isinstance(task_name, Enum):
            return task_name.value
        return task_name

    def start_pipeline(self, total_chunks: int) -> None:
        """Initialize pipeline progress tracking."""
        self.progress = PipelineProgress(
            pipeline_id=self.pipeline_id,
            total_chunks=total_chunks,
            status=TaskStatus.IN_PROGRESS,
            started_at=self._now(),
        )
        self._save()

    def start_chunk(self, chunk_index: int, chunk_id: str) -> None:
        """Mark a chunk as started."""
        if not self.progress:
            return

        self.progress.chunks[chunk_index] = ChunkProgress(
            chunk_id=chunk_id,
            chunk_index=chunk_index,
            status=TaskStatus.IN_PROGRESS,
            started_at=self._now(),
            tasks={
                self.TASK_OCR: TaskProgress(task_name=self.TASK_OCR),
                self.TASK_LAYOUT_PARSING: TaskProgress(
                    task_name=self.TASK_LAYOUT_PARSING
                ),
                self.TASK_EXTRACTION: TaskProgress(task_name=self.TASK_EXTRACTION),
            },
        )
        self._save()

    def start_task(self, chunk_index: int, task_name: str | Enum) -> None:
        """Mark a task as started."""
        if not self.progress or chunk_index not in self.progress.chunks:
            return

        task_key = self._normalize_task_name(task_name)
        chunk = self.progress.chunks[chunk_index]
        if task_key in chunk.tasks:
            chunk.tasks[task_key].status = TaskStatus.IN_PROGRESS
            chunk.tasks[task_key].started_at = self._now()
        self._save()

    def complete_task(
        self,
        chunk_index: int,
        task_name: str | Enum,
        metadata: dict[str, Any] | None = None,
        output: None = None,
    ) -> None:
        """Mark a task as completed."""
        if not self.progress or chunk_index not in self.progress.chunks:
            return

        task_key = self._normalize_task_name(task_name)
        chunk = self.progress.chunks[chunk_index]
        if task_key in chunk.tasks:
            task = chunk.tasks[task_key]
            task.status = TaskStatus.COMPLETED
            task.completed_at = self._now()
            task.duration_seconds = self._calculate_duration(task.started_at)
            if metadata:
                task.metadata = metadata

        self.output_result = output
        self._save()

    def fail_task(self, chunk_index: int, task_name: str | Enum, error: str) -> None:
        """Mark a task as failed."""
        if not self.progress or chunk_index not in self.progress.chunks:
            return

        task_key = self._normalize_task_name(task_name)
        chunk = self.progress.chunks[chunk_index]
        if task_key in chunk.tasks:
            task = chunk.tasks[task_key]
            task.status = TaskStatus.FAILED
            task.completed_at = self._now()
            task.duration_seconds = self._calculate_duration(task.started_at)
            task.error = error
        self._save()

    def complete_chunk(self, chunk_index: int) -> None:
        """Mark a chunk as completed."""
        if not self.progress or chunk_index not in self.progress.chunks:
            return

        chunk = self.progress.chunks[chunk_index]
        chunk.status = TaskStatus.COMPLETED
        chunk.completed_at = self._now()
        chunk.duration_seconds = self._calculate_duration(chunk.started_at)
        self._save()

    def fail_chunk(self, chunk_index: int, error: str) -> None:
        """Mark a chunk as failed."""
        if not self.progress or chunk_index not in self.progress.chunks:
            return

        chunk = self.progress.chunks[chunk_index]
        chunk.status = TaskStatus.FAILED
        chunk.completed_at = self._now()
        chunk.duration_seconds = self._calculate_duration(chunk.started_at)
        chunk.error = error
        self._save()

    def complete_pipeline(self) -> None:
        """Mark pipeline as completed."""
        if not self.progress:
            return

        self.progress.status = TaskStatus.COMPLETED
        self.progress.completed_at = self._now()
        self.progress.duration_seconds = self._calculate_duration(
            self.progress.started_at
        )
        self._save()

    def fail_pipeline(self, error: str) -> None:
        """Mark pipeline as failed."""
        if not self.progress:
            return

        self.progress.status = TaskStatus.FAILED
        self.progress.completed_at = self._now()
        self.progress.duration_seconds = self._calculate_duration(
            self.progress.started_at
        )
        self.progress.chunks[-1] = ChunkProgress(
            chunk_id="pipeline_error",
            chunk_index=-1,
            status=TaskStatus.FAILED,
            error=error,
        )
        self._save()

    def get_progress(self) -> dict[str, Any] | None:
        """Get current progress as dictionary."""
        if self.progress:
            return self.progress.model_dump()
        return None
