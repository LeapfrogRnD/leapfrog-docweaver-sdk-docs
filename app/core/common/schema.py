from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.db.models import UserStatus
from app.shared.constants.app_constants import TaskStatus


class GenericResponse[T](BaseModel):
    data: T


class PaginationMetadata(BaseModel):
    page: int = Field(..., description="Current page number", ge=1)
    page_size: int = Field(..., description="Number of items per page", ge=1, le=100)
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")


class GenericListResponse[T](BaseModel):
    metadata: PaginationMetadata
    data: list[T]


class DataResultStatus(StrEnum):
    active = "active"
    inactive = "inactive"
    all = "all"
class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=25, ge=1, le=100, description="Items per page")
    query: str | None = Field(default=None, description="Search query")
    search: str | None = Field(default=None, description="filter")
    status: DataResultStatus | TaskStatus | UserStatus = Field(default=DataResultStatus.all, description="Filter by  status")


class RequestModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)


class OrmResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
