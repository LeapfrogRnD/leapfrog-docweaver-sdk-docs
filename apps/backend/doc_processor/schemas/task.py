"""Pydantic schemas for tasks."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class TaskTypeEnum(str, Enum):
    """Task types."""

    CLASSIFICATION = "classification"
    EXTRACTION = "extraction"
    BOTH = "both"


class TaskStatusEnum(str, Enum):
    """Task statuses."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskSchema(BaseModel):
    """Task schema for processing."""

    id: int
    user_id: int
    task_type: TaskTypeEnum
    status: TaskStatusEnum
    document_path: str
    document_name: str
    priority: int = 0
    retry_count: int = 0
    max_retries: int = 3
    worker_id: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: dict | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
