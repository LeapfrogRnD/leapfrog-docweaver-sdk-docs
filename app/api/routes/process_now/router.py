"""
Process-Now API router.

Single synchronous endpoint: POST /process-now/
Accepts multipart/form-data with:
  - file          (binary document — PDF / JPEG / PNG )
  - task_type     (extraction | classification | summarization)
  - json_schema   (JSON string)
  - pipeline_id   OR pipeline_config (JSON string)   — exactly one required
  - additional_instruction (optional)

Processes the document inline (no background worker) and returns the result
within the same HTTP request, subject to a configurable timeout.
"""

from fastapi import APIRouter, status

from app.api.routes.process_now.dependencies import ProcessNowServiceDep
from app.api.routes.process_now.route_definations import PROCESS_DEF, PROCESS_RES
from app.api.routes.process_now.validator import ValidatedProcessNowDep
from app.core.common.schema import GenericResponse
from app.core.process_now.schemas import ProcessNowResponse

router = APIRouter(
    prefix="/process-now",
    tags=["Process Now (Synchronous)"],
    include_in_schema=False,
)


@router.post(
    "/",
    response_model=GenericResponse[ProcessNowResponse],
    status_code=status.HTTP_200_OK,
    summary="Process a document synchronously",
    description=PROCESS_DEF,
    responses=PROCESS_RES,
)
async def process_now(
    validated: ValidatedProcessNowDep,
    service: ProcessNowServiceDep,
) -> GenericResponse[ProcessNowResponse]:
    """
    **Synchronous document processing.**

    Processes the uploaded document through the full LeapFrog DocWeaver pipeline
    (OCR → parsing → LLM extraction / classification / summarisation)
    and returns structured results immediately.
    """
    request, file_bytes, filename, content_type = validated

    result = await service.process(
        request=request,
        file_bytes=file_bytes,
        filename=filename,
        content_type=content_type,
    )
    return GenericResponse[ProcessNowResponse](data=result)
