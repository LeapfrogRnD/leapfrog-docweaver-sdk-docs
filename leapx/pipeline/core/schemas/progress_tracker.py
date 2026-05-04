from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Status of a pipeline task."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskProgress(BaseModel):
    """Progress information for a single task."""

    task_name: str
    status: TaskStatus = TaskStatus.PENDING
    started_at: str | None = None
    completed_at: str | None = None
    duration_seconds: float | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ChunkProgress(BaseModel):
    """Progress information for a chunk."""

    chunk_id: str
    chunk_index: int
    status: TaskStatus = TaskStatus.PENDING
    tasks: dict[str, TaskProgress] = Field(default_factory=dict)
    started_at: str | None = None
    completed_at: str | None = None
    duration_seconds: float | None = None
    error: str | None = None


class PipelineProgress(BaseModel):
    """Overall pipeline progress."""

    pipeline_id: str
    total_chunks: int
    status: TaskStatus = TaskStatus.PENDING
    started_at: str | None = None
    completed_at: str | None = None
    duration_seconds: float | None = None
    chunks: dict[int, ChunkProgress] = Field(default_factory=dict)
