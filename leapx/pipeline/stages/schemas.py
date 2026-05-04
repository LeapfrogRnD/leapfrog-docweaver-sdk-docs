from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, TypeVar

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class StageType(Enum):
    """Stage execution type."""

    CPU = "cpu"
    IO = "io"
    ASYNC = "async"


class TaskStatus(Enum):
    """Status of stage / Chunk"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class StageName(Enum):
    """Existing Stage name"""

    parser = "parser"
    extraction = "extraction"
    ocr = "ocr"
    generation = "generation"
    vlm = "vlm"


@dataclass
class StageResult[OutputT]:
    """Result from a stage execution."""

    stage_name: str
    data: OutputT
    success: bool = True
    error: Exception | None = None


@dataclass
class StageExecutionResult:
    """Detailed result of a single stage execution with timing and metadata."""

    stage_id: str
    stage_type: str
    status: TaskStatus = TaskStatus.PENDING
    output_data: dict[str, Any] | None = None
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class StageOutput:
    """Output produced by a stage."""

    data: dict[str, Any]
    metadata: dict = field(default_factory=dict)
    skip_remaining: bool = False
    context: dict[str, Any] = field(default_factory=dict)

    @property
    def stage_definition(self) -> str:
        """
        Human-readable description of this stage output (chunk).

        Useful for logging, debugging, tracing, or UI display.
        """
        data_keys = list(self.data.keys())
        metadata_keys = list(self.metadata.keys())
        has_context = bool(self.context)

        return (
            f"StageOutput("
            f"data_keys={data_keys}, "
            f"metadata_keys={metadata_keys}, "
            f"skip_remaining={self.skip_remaining}, "
            f"has_context={has_context}"
            f")"
        )
