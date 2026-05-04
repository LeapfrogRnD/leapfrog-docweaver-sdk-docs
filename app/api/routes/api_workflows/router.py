"""
API Workflow router.

CRUD endpoints for managing API workflows:
  - POST /workflows/           — Create workflow
  - GET /workflows/            — List workflows (paginated)
  - GET /workflows/{id}        — Get workflow by ID
  - PUT /workflows/{id}        — Update workflow
  - DELETE /workflows/{id}     — Soft delete workflow

Workflows define reusable document processing pipelines with extraction,
classification, and summarization capabilities.
"""

from fastapi import APIRouter, Depends, status

from app.api.dependencies.api_key import ValidateApiKeyDep
from app.api.routes.api_workflows.dependencies import ApiWorkFlowServiceDep
from app.api.routes.api_workflows.descriptions import (
    CREATE_API_WORKFLOW_DESCRIPTION,
    DELETE_API_WORKFLOW_DESCRIPTION,
    GET_API_WORKFLOW_DESCRIPTION,
    LIST_API_WORKFLOWS_DESCRIPTION,
    UPDATE_API_WORKFLOW_DESCRIPTION,
)
from app.core.api_workflows.schemas import (
    ApiWorkFlowCreateRequest,
    ApiWorkFlowListResponse,
    ApiWorkFlowResponse,
    ApiWorkFlowUpdateRequest,
)
from app.core.common.schema import (
    GenericListResponse,
    GenericResponse,
    PaginationParams,
)

router = APIRouter(prefix="/workflows")


@router.post(
    "/",
    response_model=GenericResponse[ApiWorkFlowResponse],
    status_code=status.HTTP_200_OK,
    summary="Create API workflow",
    description=CREATE_API_WORKFLOW_DESCRIPTION,
    responses={
        200: {
            "description": "Workflow created successfully.",
        },
        400: {
            "description": "Bad request - validation errors.",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_workflow_type": {
                            "summary": "Invalid workflow type",
                            "value": {
                                "detail": "Invalid workflow type. Must be one of: extraction, classification, summarization"
                            },
                        },
                        "missing_extractors": {
                            "summary": "Missing extractors for extraction",
                            "value": {
                                "detail": "Extraction schema must contain 'extractors' array"
                            },
                        },
                        "missing_classifiers": {
                            "summary": "Missing classifiers for classification",
                            "value": {
                                "detail": "Classification schema must contain 'classifiers' array"
                            },
                        },
                        "invalid_extractor_field": {
                            "summary": "Invalid extractor field",
                            "value": {
                                "detail": "Field at index 0 is missing required keys: name, type"
                            },
                        },
                    }
                }
            },
        },
        401: {"description": "Invalid or missing API key."},
        422: {"description": "Validation error in workflow definition."},
        500: {"description": "Internal error during creation."},
    },
)
async def create_api_workflow(
    api_key: ValidateApiKeyDep,
    workflow_service: ApiWorkFlowServiceDep,
    request: ApiWorkFlowCreateRequest,
):
    """
    Create new API workflow with specified configuration.

    Validates workflow type and schema structure, then creates reusable
    workflow definition for document processing.
    """
    api_workflow = await workflow_service.create_api_workflow(
        request, api_key.api_key_id
    )
    return GenericResponse[ApiWorkFlowResponse](data=api_workflow)


@router.get(
    "/",
    response_model=GenericListResponse[ApiWorkFlowListResponse],
    status_code=status.HTTP_200_OK,
    summary="List API workflows",
    description=LIST_API_WORKFLOWS_DESCRIPTION,
    responses={
        200: {
            "description": "Workflows retrieved successfully.",
        },
        401: {"description": "Invalid or missing API key."},
        422: {"description": "Invalid pagination parameters."},
        500: {"description": "Internal error retrieving workflows."},
    },
)
async def get_api_workflows(
    api_key: ValidateApiKeyDep,
    workflow_service: ApiWorkFlowServiceDep,
    pagination: PaginationParams = Depends(),
):
    """
    List workflows with pagination support.

    Returns summary information for all workflows belonging to
    the authenticated API key with pagination metadata.
    """
    api_workflows, metadata = await workflow_service.get_all_api_workflows(
        api_key.api_key_id, pagination
    )
    return GenericListResponse[ApiWorkFlowListResponse](
        data=api_workflows, metadata=metadata
    )


@router.get(
    "/{workflow_id}",
    response_model=GenericResponse[ApiWorkFlowResponse],
    status_code=status.HTTP_200_OK,
    summary="Get workflow by ID",
    description=GET_API_WORKFLOW_DESCRIPTION,
    responses={
        200: {
            "description": "Workflow details retrieved successfully.",
        },
        401: {"description": "Invalid or missing API key."},
        404: {"description": "Workflow not found."},
        500: {"description": "Internal error retrieving workflow."},
    },
)
async def get_api_workflow(
    api_key: ValidateApiKeyDep,
    workflow_id: int,
    workflow_service: ApiWorkFlowServiceDep,
):
    """
    Get complete workflow details by ID.

    Returns full workflow configuration including schema definitions
    and processing instructions for inspection or modification.
    """
    api_workflow = await workflow_service.get_api_workflow(
        workflow_id, api_key.api_key_id
    )
    return GenericResponse[ApiWorkFlowResponse](data=api_workflow)


@router.put(
    "/{workflow_id}",
    response_model=GenericResponse[ApiWorkFlowResponse],
    status_code=status.HTTP_200_OK,
    summary="Update workflow",
    description=UPDATE_API_WORKFLOW_DESCRIPTION,
    responses={
        200: {
            "description": "Workflow updated successfully.",
        },
        400: {"description": "Invalid update request or schema validation error."},
        401: {"description": "Invalid or missing API key."},
        404: {"description": "Workflow not found."},
        422: {"description": "Validation error in configuration."},
        500: {"description": "Internal error during update."},
    },
)
async def update_api_workflow(
    api_key: ValidateApiKeyDep,
    workflow_id: int,
    workflow_service: ApiWorkFlowServiceDep,
    request: ApiWorkFlowUpdateRequest,
):
    """
    Update existing workflow configuration.

    Applies partial updates to workflow while maintaining schema validation
    and preserving workflow identity and creation history.
    """
    api_workflow = await workflow_service.update_api_workflow(
        request, workflow_id, api_key.api_key_id
    )
    return GenericResponse[ApiWorkFlowResponse](data=api_workflow)


@router.delete(
    "/{workflow_id}",
    response_model=GenericResponse[str],
    status_code=status.HTTP_200_OK,
    summary="Delete workflow",
    description=DELETE_API_WORKFLOW_DESCRIPTION,
    responses={
        200: {
            "description": "Workflow deleted successfully.",
        },
        401: {"description": "Invalid or missing API key."},
        404: {"description": "Workflow not found."},
        500: {"description": "Internal error during deletion."},
    },
)
async def delete_api_workflow(
    api_key: ValidateApiKeyDep,
    workflow_id: int,
    workflow_service: ApiWorkFlowServiceDep,
):
    """
    Soft delete workflow preserving data.

    Marks workflow as deleted while preserving all configuration
    and history data for potential recovery through support.
    """
    await workflow_service.delete_api_workflow(workflow_id, api_key.api_key_id)
    return GenericResponse[str](data="API workflow deleted successfully")
