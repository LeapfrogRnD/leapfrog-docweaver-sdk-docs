import asyncio
import base64
import hashlib
import json
import logging
import re
from typing import Any

import httpx

from leap_docweaver_mcp.schemas import WorkflowConfig

from leap_docweaver_mcp.config import (
    DEFAULT_LLM, 
    DEFAULT_LLM_PROVIDER, 
    DEFAULT_OCR, 
    VLM_OCR_PROVIDER, 
    McpWorkflowName, 
    WorkflowType
)

logger = logging.getLogger("docweaver-mcp")

def resolve_workflow_name(
    base_name: McpWorkflowName,
    llm_model_provider: str | None,
    llm_model: str | None,
    ocr_provider: str | None,
    vlm_model_provider: str | None = None,
    vlm_model: str | None = None,
) -> WorkflowConfig:
    """Resolve the effective workflow name and infra parameters.

    Uses a deterministic hashed name when any param deviates from the defaults so that
    different configurations map to distinct, reusable workflows.
    """
    effective_provider = llm_model_provider or DEFAULT_LLM_PROVIDER
    effective_model = llm_model or DEFAULT_LLM
    effective_ocr = ocr_provider or DEFAULT_OCR
    effective_vlm_provider = vlm_model_provider
    effective_vlm_model = vlm_model

    is_custom = (
        (llm_model_provider is not None and llm_model_provider != DEFAULT_LLM_PROVIDER)
        or (llm_model is not None and llm_model != DEFAULT_LLM)
        or (ocr_provider is not None and ocr_provider != DEFAULT_OCR)
        or vlm_model_provider is not None
        or vlm_model is not None
    )

    if is_custom:
        key = (
            f"{base_name.value}|{effective_provider}|{effective_model}"
            f"|{effective_ocr}"
            f"|{effective_vlm_provider or ''}|{effective_vlm_model or ''}"
        )
        suffix = hashlib.md5(key.encode()).hexdigest()[:12]
        name = f"{base_name.value}_{suffix}"
    else:
        name = base_name.value

    return WorkflowConfig(
        name=name,
        llm_provider=effective_provider,
        llm_model=effective_model,
        ocr=effective_ocr,
        vlm_provider=effective_vlm_provider,
        vlm_model=effective_vlm_model,
    )

async def get_or_create_workflow(
    client: httpx.AsyncClient,
    workflow_type: WorkflowType,
    workflow_name: str,
    fields: list[dict[str, Any]] | None,
    additional_instruction: str | None,
    llm_model_provider: str = DEFAULT_LLM_PROVIDER,
    llm_model: str = DEFAULT_LLM,
    ocr_provider: str = DEFAULT_OCR,
    vlm_model_provider: str | None = None,
    vlm_model: str | None = None,
) -> str:
    """Return an existing workflow matching the given name/config, or create one."""
    
    logger.info("Searching for workflow: %s", workflow_name)
    search_res = await client.get("/api/workflows/", params={"search": workflow_name})
    if search_res.status_code == 200:
        existing_wfs = search_res.json().get("data", [])
        if any(wf["name"] == workflow_name for wf in existing_wfs):
            logger.info("Using existing workflow: %s", workflow_name)
            return workflow_name

    logger.info("Workflow '%s' not found. Creating JIT workflow...", workflow_name)
    payload: dict[str, Any] = {
        "name": workflow_name,
        "workflow_type": workflow_type.value,
        "ocr_provider": ocr_provider,
        "llm_model_provider": llm_model_provider,
        "llm_model": llm_model,
    }

    if additional_instruction is not None:
         payload["additional_instruction"] = additional_instruction

    if ocr_provider == VLM_OCR_PROVIDER:
        payload["vlm_model_provider"] = vlm_model_provider
        payload["vlm_model"] = vlm_model
    if workflow_type in (WorkflowType.EXTRACTION, WorkflowType.CLASSIFICATION) and fields is not None:
        payload["json_schema"] = fields

    create_res = await client.post("/api/workflows/", json=payload)
    create_res.raise_for_status()
    return workflow_name


async def poll_until_complete(
    client: httpx.AsyncClient,
    job_id: str,
    progress_callback=None,
) -> dict[str, Any]:
    """Poll integration status until it completes, fails, or times out."""
    max_wait_seconds = 20
    interval = 15
    elapsed = 0

    while elapsed < max_wait_seconds:
        if progress_callback:
            await progress_callback(elapsed, max_wait_seconds)

        response = await client.get(f"/api/integrations/{job_id}")
        response.raise_for_status()
        job_data = response.json().get("data", {})
        status = job_data.get("status")

        if status == "completed":
            return {"status": "success", "result": job_data.get("result")}
        if status == "failed":
            return {
                "status": "failed",
                "error": job_data.get("failed_remarks", "Unspecified backend error"),
            }

        logger.info("Job %s status: %s. Waiting %ss...", job_id, status, interval)
        await asyncio.sleep(interval)
        elapsed += interval

    return {"status": "timeout", "job_id": job_id}


async def run_integration_workflow(
    client: httpx.AsyncClient,
    workflow_name: str,
    file_name: str,
    base64_data: str | None = None,
    s3_url: str | None = None,
    fields: list[dict[str, Any]] | None = None,
    additional_instructions: str | None = None,
    progress_callback=None,
) -> tuple[str, dict[str, Any]]:
    """Trigger an integration job and wait for completion status."""
    if not base64_data and not s3_url:
        raise ValueError("Either base64_data or s3_url must be provided.")

    if base64_data:
        try:
            file_bytes = base64.b64decode(base64_data)
        except Exception as exc:
            raise ValueError(f"Failed to decode base64 data. {str(exc)}") from exc
        files = {"file": (file_name, file_bytes)}
        form_data = {"workflow_name": workflow_name}
        source = file_name
    else:
        files = None
        form_data = {"workflow_name": workflow_name, "s3_file_uri": s3_url}
        source = s3_url
    
    metadata: dict[str, Any] = {}
    if fields is not None:
        metadata["json_schema"] = fields
    if additional_instructions is not None:
        metadata["additional_instruction"] = additional_instructions
    if metadata:
        form_data["metadata"] = json.dumps(metadata)

    logger.info(
        "Triggering integration for %s via workflow %s",
        source,
        workflow_name,
    )
    trigger_res = await client.post("/api/integrations/", data=form_data, files=files)

    if trigger_res.is_error:
         raise ValueError(
             f"Integration trigger request failed with status {trigger_res.status_code}: {trigger_res.text}"
         )

    try:
        response_data = trigger_res.json()
    except Exception as exc:
        raise ValueError(f"Failed to parse integration trigger response. {str(exc)}") from exc

    job_id = response_data.get("data", {}).get("integration_job_id")
    if not job_id:
        raise ValueError("Integration trigger response missing integration_job_id")

    outcome = await poll_until_complete(client, job_id, progress_callback)
    return job_id, outcome


def build_tool_response(
    outcome: dict[str, Any],
    job_id: str | None = None,
    timeout_label: str = "JOB_ID",
    timeout_lookup_tool: str = "check_job_status",
    failure_prefix: str = "Processing Failed",
) -> str:
    """Build a consistent string response from a workflow outcome payload."""
    status = outcome.get("status")

    if status == "success":
        return json.dumps(outcome.get("result"), indent=2)

    if status == "timeout":
        response_job_id = job_id or outcome.get("job_id")
        return (
            "The document is still processing in the background. "
            f"{timeout_label}: {response_job_id}. You can check results later using '{timeout_lookup_tool}'."
        )

    if status == "failed":
        return f"{failure_prefix}: {outcome.get('error', 'Unknown error')}"
    
    return f"{failure_prefix}: Unknown status"

def validate_tool_inputs(
    base64_data: str | None,
    s3_url: str | None,
    ocr_provider: str | None,
    vlm_model_provider: str | None,
    vlm_model: str | None,
) -> str | None:
    """Validate common tool inputs. Returns an error string, or None if valid."""
    if not base64_data and not s3_url:
        return "Error: Either base64_data or s3_url must be provided."
    
    S3_URI_PATTERN = re.compile(r"^s3://[^/]+/.+")
    if s3_url and not S3_URI_PATTERN.match(s3_url):
        return (
            "Error: Invalid S3 URI format. Expected 's3://bucket/key'. "
            "Example: s3://my-bucket/documents/invoice.pdf"
        )

    if ocr_provider == VLM_OCR_PROVIDER:
        if not vlm_model_provider:
            return "Error: vlm_model_provider is required when ocr_provider is 'vlm'."
        if not vlm_model:
            return "Error: vlm_model is required when ocr_provider is 'vlm'."

    return None
