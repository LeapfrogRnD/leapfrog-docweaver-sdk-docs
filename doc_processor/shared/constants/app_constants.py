from enum import StrEnum


class LLMProviders:
    """Supported LLM providers."""

    OPENAI = "openai"
    BEDROCK = "bedrock"


class TaskStatus(StrEnum):
    """Task status options."""

    DRAFT = "draft"
    READY = "ready"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskTypes:
    """Supported task types."""

    EXTRACTION = "extraction"
    CLASSIFICATION = "classification"
    SUMMARIZATION = "summarization"
    BOTH = "both"


class RunTypes:
    """Supported run types."""

    API_WORKFLOW = "api_workflow"
    TASK_WORKFLOW = "task_workflow"
