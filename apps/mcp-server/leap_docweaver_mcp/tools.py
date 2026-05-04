import json
import logging
import re
from typing import Any

import httpx
from fastmcp import FastMCP

from leap_docweaver_mcp.schemas import (
    ClassifierToolSchema, 
    ExtractorToolSchema, 
    SummarizerToolSchema
)

from leap_docweaver_mcp.client import call_with_client
from leap_docweaver_mcp.config import (
    McpWorkflowName,
    WorkflowType,
)
from leap_docweaver_mcp.services import (
    build_tool_response, 
    get_or_create_workflow, 
    resolve_workflow_name, 
    run_integration_workflow, 
    validate_tool_inputs)

logger = logging.getLogger("docweaver-mcp")

async def extract_custom_data(params: ExtractorToolSchema) -> str:
    """
    USE THIS TOOL WHEN: The user wants to extract specific structured fields or data points
    from a document (e.g. invoice number, dates, totals, names, addresses, line items,
    or any custom fields described in natural language).

    DO NOT use summarize_document or classify_document for extraction tasks.
    If user asks for extraction but also wants a summary or classification, call this tool first to get the
    structured data, then call the other tools with that data as context for enhanced results.

    additional instructions only are used for defining instruction not for fields to extract 
     
    INPUT REQUIREMENTS:
    - Provide EITHER `s3_url` (e.g. 's3://bucket/path/file.pdf') OR `base64_data` (raw
      base64-encoded file bytes). Exactly one must be supplied — never both, never neither.
    - `field_definitions`: list of dicts describing the fields to extract. Each dict should
      have a 'name' and 'description' key. Omit to use server defaults.
    - `additional_instructions`: free-text instructions to guide extraction (e.g. 'Focus on
      line items only'). Omit to use server defaults.
    - `file_name`: original filename including extension (e.g. 'invoice.pdf'). Used for
      format hints. Defaults to 'upload.pdf'.
    - `llm_model_provider`, `llm_model`, `ocr_provider`: call get_configs first to discover
      valid values. Omit to use server defaults.
    - When `ocr_provider` is 'vlm', BOTH `vlm_model_provider` and `vlm_model` are REQUIRED.

    OUTPUT: Extracted fields as a JSON object, or a job ID if processing is asynchronous.
    If a job ID is returned, use check_job_status(job_id) to retrieve the final result.
    """
    error = validate_tool_inputs(params.base64_data, params.s3_url, params.ocr_provider, params.vlm_model_provider, params.vlm_model)
    if error:
        return error

    progress = params.context.info.progress if params.context and hasattr(params.context, "info") else None
    cfg = resolve_workflow_name(
        McpWorkflowName.MCP_EXTRACT,
        params.llm_model_provider,
        params.llm_model,
        params.ocr_provider,
        params.vlm_model_provider,
        params.vlm_model,
    )

    async def _run(client: httpx.AsyncClient) -> str:
        wf_name = await get_or_create_workflow(
            client,
            WorkflowType.EXTRACTION,
            cfg.name,
            params.field_definitions,
            params.additional_instructions,
            llm_model_provider=cfg.llm_provider,
            llm_model=cfg.llm_model,
            ocr_provider=cfg.ocr,
            vlm_model_provider=cfg.vlm_provider,
            vlm_model=cfg.vlm_model,
        )
        job_id, outcome = await run_integration_workflow(
            client,
            wf_name,
            params.file_name,
            base64_data=params.base64_data,
            s3_url=params.s3_url,
            fields=params.field_definitions,
            additional_instructions=params.additional_instructions,
            progress_callback=progress,
        )
        return build_tool_response(outcome, job_id=job_id)

    return await call_with_client(_run)


async def summarize_document(params: SummarizerToolSchema) -> str:
    """
    USE THIS TOOL WHEN: The user wants a natural-language summary, overview.

    DO NOT use extract_custom_data or classify_document for summarization tasks.

    INPUT REQUIREMENTS:
    - Provide EITHER `s3_url` (e.g. 's3://bucket/path/file.pdf') OR `base64_data` (raw
      base64-encoded file bytes). Exactly one must be supplied — never both, never neither.
    - `additional_instructions`: optional free-text to focus or constrain the summary
      (e.g. 'Summarize only the financial section', 'Extract the purpose of the document').
      Omit for a general summary.
    - `file_name`: original filename including extension (e.g. 'report.pdf'). Defaults to
      'upload.pdf'.
    - `llm_model_provider`, `llm_model`, `ocr_provider`: call get_configs first to discover
      valid values. Omit to use server defaults.
    - When `ocr_provider` is 'vlm', BOTH `vlm_model_provider` and `vlm_model` are REQUIRED.

    OUTPUT: A plain-text or markdown summary of the document, or a job ID if processing is
    asynchronous. If a job ID is returned, use check_job_status(job_id) to retrieve the result.
    """
    error = validate_tool_inputs(params.base64_data, params.s3_url, params.ocr_provider, params.vlm_model_provider, params.vlm_model)
    if error:
        return error

    progress = params.context.info.progress if params.context and hasattr(params.context, "info") else None
    cfg = resolve_workflow_name(
        McpWorkflowName.MCP_SUMMARIZE,
        params.llm_model_provider,
        params.llm_model,
        params.ocr_provider,
        params.vlm_model_provider,
        params.vlm_model,
    )

    async def _run(client: httpx.AsyncClient) -> str:
        wf_name = await get_or_create_workflow(
            client,
            WorkflowType.SUMMARIZATION,
            cfg.name,
            None,
            params.additional_instructions,
            llm_model_provider=cfg.llm_provider,
            llm_model=cfg.llm_model,
            ocr_provider=cfg.ocr,
            vlm_model_provider=cfg.vlm_provider,
            vlm_model=cfg.vlm_model,
        )
        job_id, outcome = await run_integration_workflow(
            client,
            wf_name,
            params.file_name,
            base64_data=params.base64_data,
            s3_url=params.s3_url,
            additional_instructions=params.additional_instructions,
            progress_callback=progress,
        )
        return build_tool_response(outcome, job_id=job_id)

    return await call_with_client(_run)


async def classify_document(params: ClassifierToolSchema) -> str:
    """
    USE THIS TOOL WHEN: The user wants to categorize or label a document (or content within
    it) into predefined classes, types, or categories — e.g. invoice vs. receipt, severity
    level, document type, priority, sentiment, or any custom taxonomy.

    DO NOT use extract_custom_data or summarize_document for classification tasks.

    INPUT REQUIREMENTS:
    - Provide EITHER `s3_url` (e.g. 's3://bucket/path/file.pdf') OR `base64_data` (raw
      base64-encoded file bytes). Exactly one must be supplied — never both, never neither.
    - `field_definitions`: list of category dicts, each with a 'category' key and a 'fields'
      list of candidate labels (each with 'name' and 'description'). Omit to use server
      defaults (severity + priority categories).
    - `additional_instructions`: optional free-text to refine classification behaviour.
      Omit to use server defaults.
    - `file_name`: original filename including extension. Defaults to 'upload.pdf'.
    - `llm_model_provider`, `llm_model`, `ocr_provider`: call get_configs first to discover
      valid values. Omit to use server defaults.
    - When `ocr_provider` is 'vlm', BOTH `vlm_model_provider` and `vlm_model` are REQUIRED.

    OUTPUT: Classification result as a JSON object mapping each category to the matched label,
    or a job ID if processing is asynchronous. If a job ID is returned, use
    check_job_status(job_id) to retrieve the final result.
    """
    error = validate_tool_inputs(params.base64_data, params.s3_url, params.ocr_provider, params.vlm_model_provider, params.vlm_model)
    if error:
        return error

    progress = params.context.info.progress if params.context and hasattr(params.context, "info") else None
    cfg = resolve_workflow_name(
        McpWorkflowName.MCP_CLASSIFY,
        params.llm_model_provider,
        params.llm_model,
        params.ocr_provider,
        params.vlm_model_provider,
        params.vlm_model,
    )

    async def _run(client: httpx.AsyncClient) -> str:
        wf_name = await get_or_create_workflow(
            client,
            WorkflowType.CLASSIFICATION,
            cfg.name,
            params.field_definitions,
            params.additional_instructions,
            llm_model_provider=cfg.llm_provider,
            llm_model=cfg.llm_model,
            ocr_provider=cfg.ocr,
            vlm_model_provider=cfg.vlm_provider,
            vlm_model=cfg.vlm_model,
        )
        job_id, outcome = await run_integration_workflow(
            client,
            wf_name,
            params.file_name,
            base64_data=params.base64_data,
            s3_url=params.s3_url,
            fields=params.field_definitions,
            additional_instructions=params.additional_instructions,
            progress_callback=progress,
        )
        return build_tool_response(outcome, job_id=job_id)

    return await call_with_client(_run)


async def check_job_status(job_id: str) -> str:
    """
    USE THIS TOOL WHEN: A previous call to extract_custom_data, summarize_document, or
    classify_document returned a job ID instead of an immediate result (i.e. the document
    is still being processed asynchronously).

    INPUT REQUIREMENTS:
    - `job_id`: the exact job/ticket ID string returned by the originating tool call.
      REQUIRED — do not call this tool without a valid job ID.

    OUTPUT: The completed job result (extracted fields, summary, or classification) as JSON,
    or a status message if the job is still in progress. Poll again if status is pending.
    """
    async def _run(client: httpx.AsyncClient) -> str:
        res = await client.get(f"/api/integrations/{job_id}")
        res.raise_for_status()
        return json.dumps(res.json(), indent=2)

    return await call_with_client(_run)


async def list_job_history() -> str:
    """
    USE THIS TOOL WHEN: The user asks to see past document processing jobs, or when a job ID
    has been lost and needs to be recovered from history.

    DO NOT use this tool to check the status of a known job ID — use check_job_status instead.

    INPUT REQUIREMENTS: None. Takes no parameters.

    OUTPUT: A JSON list of recent document processing jobs, each containing a job ID,
    document name, workflow type, status, and timestamps.
    """
    async def _run(client: httpx.AsyncClient) -> str:
        res = await client.get("/api/integrations/history")
        res.raise_for_status()
        return json.dumps(res.json(), indent=2)

    return await call_with_client(_run)
        
async def get_configs() -> str:
    """
    USE THIS TOOL WHEN: You need to know the valid values for `llm_model_provider`,
    `llm_model`, or `ocr_provider` before calling extract_custom_data, summarize_document,
    or classify_document. Also use this when the user explicitly asks about available
    models or OCR providers.

    RECOMMENDED: Call this tool FIRST before any document processing tool when the user
    specifies a particular model or OCR provider, to validate that the requested option
    is supported.

    INPUT REQUIREMENTS: None. Takes no parameters.

    OUTPUT: A JSON object listing all supported OCR providers (including 'vlm' options
    that require vlm_model_provider and vlm_model), LLM providers, and available LLM
    models. Use these exact string values in subsequent tool calls.
    """
    async def _run(client: httpx.AsyncClient) -> str:
        res = await client.get("/api/integrations/configs")
        res.raise_for_status()
        return json.dumps(res.json(), indent=2)

    return await call_with_client(_run)


def register_tools(mcp: FastMCP) -> None:
    """Register all tool handlers with the MCP server instance."""
    mcp.tool()(extract_custom_data)
    mcp.tool()(summarize_document)
    mcp.tool()(classify_document)
    mcp.tool()(check_job_status)
    mcp.tool()(list_job_history)
    mcp.tool()(get_configs)
