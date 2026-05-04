"""Task API routes for multi-step form."""

from fastapi import APIRouter, Body, Depends

from app.api.dependencies.auth import get_current_user
from app.api.routes.tasks.dependencies import TaskServiceDep
from app.core.common.schema import GenericListResponse, GenericResponse, PaginationParams
from app.core.tasks.schemas import (
    ConfirmDocUploadRequest,
    PresignedUrlRequest,
    PresignedUrlResponse,
    TaskConfigurationRequest,
    TaskDetailResponse,
    TaskExecuteResponse,
    TaskListFilterParams,
    TaskListResponse,
    TaskNameRequest,
    TaskResponse,
    TaskResultResponse,
    TaskStatsResponse,
)
from app.db.models import User

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/stats", response_model=GenericResponse[TaskStatsResponse])
async def get_task_stats(
    task_service: TaskServiceDep,
    _: User = Depends(get_current_user),
):
    """
    Get task statistics.

    Returns statistics for all tasks including:
    - Total number of tasks
    - Number of tasks in draft status
    - Number of tasks in ready status
    - Number of tasks in processing status
    - Number of tasks in completed status
    - Number of tasks in failed status
    """
    stats = await task_service.get_task_stats()
    return GenericResponse[TaskStatsResponse](data=stats)


@router.get("/", response_model=GenericListResponse[TaskListResponse])
async def get_all_tasks(
    task_service: TaskServiceDep,
    pagination_params: PaginationParams = Depends(),
    filter_params: TaskListFilterParams = Depends(),
    _: User = Depends(get_current_user),
):
    """
    Get all tasks with filters and pagination.

    Returns all tasks irrespective of roles with:
    - Filter by task status
    - Filter by task name (partial match)
    - Pagination support
    """
    tasks, metadata = await task_service.get_all_tasks(pagination_params, filter_params)
    return GenericListResponse[TaskListResponse](data=tasks, metadata=metadata)


@router.post("/", response_model=GenericResponse[TaskResponse])
async def create_or_update_task_name(
    request: TaskNameRequest,
    task_service: TaskServiceDep,
    user: User = Depends(get_current_user),
):
    """
    Step 1: Create a new task or update existing task name.

    - If task_id is not provided in request: Creates a new task with DRAFT status
    - If task_id is provided in request: Updates the existing task's name
    """
    task = await task_service.create_or_update_task_name(request, user)
    return GenericResponse[TaskResponse](data=task)


@router.post("/{task_id}/presigned-url", response_model=GenericResponse[PresignedUrlResponse])
async def generate_presigned_upload_url(
    request: PresignedUrlRequest,
    task_id: int,
    task_service: TaskServiceDep,
    user: User = Depends(get_current_user),
):
    """
    Generate a presigned URL for uploading a file to S3.
    """
    data = await task_service.generate_presigned_upload_url(
        task_id=task_id,
        payload=request,
        user=user,
    )

    return GenericResponse[PresignedUrlResponse](data=data)


@router.post("/{task_id}/document-confirm", response_model=GenericResponse[str])
async def confirm_doc_upload(
    request: ConfirmDocUploadRequest,
    task_id: int,
    task_service: TaskServiceDep,
    user: User = Depends(get_current_user),
):
    """
    Generate a presigned URL for uploading a file to S3.
    """
    await task_service.confirm_doc_upload(
        task_id=task_id,
        file_key=request.file_key,
        user=user,
    )

    return GenericResponse[str](data="confirmed successfully")


@router.delete("/{task_id}/delete-files", response_model=GenericResponse[str])
async def delete_files(
    task_id: int,
    task_service: TaskServiceDep,
    user: User = Depends(get_current_user),
):
    """
    Generate a presigned URL for uploading a file to S3.
    """
    await task_service.delete_task_file(
        task_id=task_id,
        user=user,
    )

    return GenericResponse[str](data="confirmed successfully")


@router.put("/{task_id}/configuration", response_model=GenericResponse[TaskResponse])
async def update_task_configuration(
    task_id: int,
    request: TaskConfigurationRequest,
    task_service: TaskServiceDep,
    user: User = Depends(get_current_user),
):
    """
    Step 3: Update task with configuration settings.

    Updates the task with system prompt, task type, JSON schema, and pipeline,
    and sets task status to READY.
    """
    task = await task_service.update_task_configuration(task_id, request, user)
    return GenericResponse[TaskResponse](data=task)


@router.post("/{task_id}/execute", response_model=GenericResponse[TaskExecuteResponse])
async def execute(
    task_id: int,
    task_service: TaskServiceDep,
    user: User = Depends(get_current_user),
):
    """
    Execute the task.
    """
    execution = await task_service.execute_task(task_id, user)
    return GenericResponse[TaskExecuteResponse](data=execution)


@router.get("/{task_id}", response_model=GenericResponse[TaskDetailResponse])
async def get_task_detail(
    task_id: int,
    task_service: TaskServiceDep,
    user: User = Depends(get_current_user),
):
    """
    Get task details with presigned URL for document preview.

    Returns complete task information including a presigned URL that can be used
    to preview/download the uploaded document. The URL is valid for 1 hour.
    """
    task_detail = await task_service.get_task_detail(task_id, user)
    return GenericResponse[TaskDetailResponse](data=task_detail)


@router.get("/{task_id}/results", response_model=GenericResponse[TaskResultResponse])
async def get_task_result(
    task_id: int,
    task_service: TaskServiceDep,
    user: User = Depends(get_current_user),
):
    """
    Get task details with presigned URL for document preview.

    Returns complete task information including a presigned URL that can be used
    to preview/download the uploaded document. The URL is valid for 1 hour.
    """
    task_detail = await task_service.get_task_results(task_id, user)
    return GenericResponse[TaskResultResponse](data=task_detail)


@router.post("/{task_id}/duplicate", response_model=GenericResponse[TaskResponse])
async def duplicate_task(
    task_id: int,
    task_service: TaskServiceDep,
    user: User = Depends(get_current_user),
):
    """
    Duplicate an existing task with a new name.

    Creates a copy of the specified task including:
    - System prompt
    - Task type
    - JSON schema
    - Pipeline configuration
    - File path and metadata

    The duplicated task will have a DRAFT status and can be modified independently.
    """
    task = await task_service.duplicate_task(task_id, user)
    return GenericResponse[TaskResponse](data=task)


@router.delete("/{task_id}", response_model=GenericResponse[str])
async def delete_task(
    task_id: int,
    task_service: TaskServiceDep,
    user: User = Depends(get_current_user),
):
    """
    Delete a task.

    Deletes the specified task. Only the task owner or admin can delete a task.
    Tasks that are currently being processed (QUEUED or PROCESSING status) cannot be deleted.
    """
    await task_service.delete_task(task_id, user)
    return GenericResponse[str](data="Task deleted successfully")


@router.put("/upload/tasks/{task_id}/{file_key:path}")
async def upload_file_raw(
    task_id: int,
    file_key: str,
    task_service: TaskServiceDep,
    body: bytes = Body(...),
    user: User = Depends(get_current_user),
) -> GenericResponse[str]:
    """
    Upload a file directly to the task.

    This endpoint allows uploading a file directly to the server for a specific task.
    The file will be stored using the provided file_key.
    """
    await task_service.upload_file(
        task_id=task_id,
        file_key=file_key,
        file=body,
        user=user,
    )

    return GenericResponse[str](data="File uploaded successfully")
