"""
Integration API router.

Asynchronous endpoints for data integrations:
  - POST /integrations/     — Create integration job
  - GET /integrations/{id}  — Poll integration status

Integrations run asynchronously in background. Poll for status using job ID.
Integration jobs process documents through workflows and return structured results.
"""

from fastapi import APIRouter, status

from app.api.dependencies.api_key import ValidateApiKeyDep
from app.api.routes.integration_apis.dependencies import IntegrationServiceDep
from app.api.routes.integration_apis.descriptions import (
    CREATE_INTEGRATION_DESCRIPTION,
    POLL_INTEGRATION_DESCRIPTION,
)
from app.api.routes.integration_apis.validator import ValidatedIntegrationRequestDep
from app.core.common.schema import GenericResponse
from app.core.integration_apis.schemas import (
    IntegrationResponse,
    PollIntegrationResponse,
)

router = APIRouter(prefix="/integrations")

@router.post(
    "/",
    response_model=GenericResponse[IntegrationResponse],
    status_code=status.HTTP_200_OK,
    summary="Create integration job",
    description=CREATE_INTEGRATION_DESCRIPTION,
    responses={
        200: {
            "description": "Integration job created successfully.",
        },
        400: {
            "description": "Bad request - validation errors.",
            "content": {
                "application/json": {
                    "examples": {
                        "missing_file": {
                            "summary": "Missing file input",
                            "value": {"detail": "Either s3_file_uri or file must be provided"},
                        },
                        "invalid_file_type": {
                            "summary": "Invalid file format",
                            "value": {
                                "detail": "Invalid file type. Allowed types: PDF and images (JPG, JPEG, PNG)"
                            },
                        },
                        "file_too_large": {
                            "summary": "File size exceeded",
                            "value": {
                                "detail": "File size exceeds the maximum allowed size of 10MB"
                            },
                        },
                        "too_many_pages": {
                            "summary": "PDF page limit exceeded",
                            "value": {"detail": "PDF exceeds the maximum allowed page count of 30"},
                        },
                    }
                }
            },
        },
        401: {"description": "Invalid or missing API key."},
        422: {"description": "Validation error in request body."},
        500: {"description": "Internal error during job creation."},
    },
)
async def integrate(
    api_key: ValidateApiKeyDep,
    request: ValidatedIntegrationRequestDep,
    integration_service: IntegrationServiceDep,
):
    """
    Create integration job for asynchronous document processing.

    Validates file input, queues the integration job with specified workflow,
    and returns tracking information for monitoring progress.
    """
    data = await integration_service.create_integration(request, api_key)
    return GenericResponse[IntegrationResponse](data=data)


@router.get(
    "/{integration_job_id}",
    response_model=GenericResponse[PollIntegrationResponse],
    status_code=status.HTTP_200_OK,
    summary="Poll integration status",
    description=POLL_INTEGRATION_DESCRIPTION,
    responses={
        200: {
            "description": "Status retrieved successfully.",
        },
        401: {"description": "Invalid or missing API key."},
        404: {"description": "Integration job not found or expired."},
        500: {"description": "Internal error retrieving status."},
    },
)
async def poll(
    integration_job_id: str,
    api_key: ValidateApiKeyDep,
    integration_service: IntegrationServiceDep,
):
    """
    Poll integration job status and retrieve results.

    Returns current status and structured extraction results when job completes.
    Use this endpoint to monitor job progress and retrieve processed data.
    """
    data = await integration_service.poll_integration_task(integration_job_id, api_key)
    return GenericResponse[PollIntegrationResponse](data=data)
