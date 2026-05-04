from pydantic import BaseModel, Field


class TaskMetadata(BaseModel):
    enable_context: bool | None = Field(
        False,
        description="Whether to enable context when processing tasks",
        example=False,
    )
    batch_size: int | None = Field(
        None, description="Batch size for processing", example=1
    )
