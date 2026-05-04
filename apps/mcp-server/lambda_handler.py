import asyncio
import json
import logging
from pydantic import ValidationError

from leap_docweaver_mcp.schemas import (
    ClassifierToolSchema,
    ExtractorToolSchema,
    SummarizerToolSchema,
)
from leap_docweaver_mcp.tools import (
    check_job_status,
    classify_document,
    extract_custom_data,
    get_configs,
    list_job_history,
    summarize_document,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def unpack_agentcore_event(event: dict):
    """
    AgentCore wraps the request. This extracts the headers and the 
    actual JSON-RPC body from the event.
    """
    # If coming through AgentCore Gateway
    if "mcp" in event and "gatewayRequest" in event["mcp"]:
        request = event["mcp"]["gatewayRequest"]
        headers = request.get("headers", {})
        body = request.get("body", {})
        
        # Sometimes body is passed as a stringified JSON
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except:
                pass
        return headers, body
    
    # Fallback for direct Lambda testing
    return event.get("headers", {}), event


def get_auth_token(headers: dict) -> str:
    """Extracts token from the correct headers dictionary."""
    # Headers in Gateway are often normalized to lowercase
    auth_header = headers.get("authorization") or headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        raise ValueError("Invalid Bearer token")
    
    return auth_header.split(" ")[1]

# -----------------------------
# HTTP Response Wrapper
# -----------------------------
def http_response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }


# -----------------------------
# JSON-RPC Helpers
# -----------------------------
def rpc_result(event: dict, result) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": event.get("id"),
        "result": result,
    }


def rpc_error(event: dict, message: str, code: int = -32603) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": event.get("id"),
        "error": {
            "code": code,
            "message": message,
        },
    }


# -----------------------------
# Tool Resolver (AgentCore)
# -----------------------------
# FIX 4: Use .get() to avoid KeyError when the key is absent; raise a
# descriptive ValueError instead of an unhandled exception.
def resolve_tool_name(context) -> str:
    """Extract the tool name injected by AgentCore into the Lambda context.

    AgentCore sets ``bedrockAgentCoreToolName`` inside
    ``context.client_context.custom``.  The value may include a namespace
    prefix separated by ``___``; only the suffix after the last delimiter is
    the actual tool name.

    Raises:
        ValueError: if the context structure is missing or the key is absent.
    """
    delimiter = "___"

    try:
        custom = context.client_context.custom
    except AttributeError as exc:
        raise ValueError(
            "Lambda context is missing client_context.custom — "
            "is this being invoked via AgentCore?"
        ) from exc

    # FIX 4: .get() instead of direct key access
    original_tool_name = custom.get("bedrockAgentCoreToolName")
    if not original_tool_name:
        raise ValueError(
            "bedrockAgentCoreToolName not found in context.client_context.custom. "
            f"Available keys: {list(custom.keys())}"
        )

    if delimiter in original_tool_name:
        return original_tool_name.rsplit(delimiter, 1)[1]

    return original_tool_name


# -----------------------------
# Async Dispatcher
# -----------------------------
async def dispatch(tool_name: str, event: dict):
    """Route tool_name to the correct async handler and return its result."""
    if tool_name == "extract_custom_data":
        params = ExtractorToolSchema.model_validate(event)
        return await extract_custom_data(params)

    if tool_name == "summarize_document":
        params = SummarizerToolSchema.model_validate(event)
        return await summarize_document(params)

    if tool_name == "classify_document":
        params = ClassifierToolSchema.model_validate(event)
        return await classify_document(params)

    if tool_name == "check_job_status":
        job_id = event.get("job_id")
        if not job_id:
            raise ValueError("Missing required field: job_id")
        return await check_job_status(job_id)

    if tool_name == "list_job_history":
        return await list_job_history()

    if tool_name == "get_configs":
        return await get_configs()

    raise ValueError(f"Unknown tool: '{tool_name}'")


# FIX 6: Safe async runner that works regardless of whether the Lambda runtime
# already has a running event loop (Python 3.12+).
def _run_async(coro):
    """Run a coroutine safely in both fresh and pre-existing event loops."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Shouldn't happen in standard Lambda but handles frameworks that
            # wrap the handler in an async context (e.g. Mangum, Powertools).
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        # No current event loop — create a fresh one.
        return asyncio.run(coro)


# -----------------------------
# Lambda Handler
# -----------------------------
def handler(event, context):
    logger.info("Event received: %s", json.dumps(event))

    # =====================================================
    # 1. MCP INITIALIZE handshake
    # =====================================================
    if isinstance(event, dict) and event.get("method") == "initialize":
        response = rpc_result(
            event,
            {
                "protocolVersion": event.get("params", {}).get(
                    "protocolVersion", "2024-11-05"
                ),
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "DocWeaver MCP Lambda",
                    "version": "1.0.0",
                },
            },
        )
        return http_response(200, response)

    # =====================================================
    # 2. TOOL NAME RESOLUTION
    # =====================================================
    try:
        tool_name = resolve_tool_name(context)
    except ValueError as exc:
        logger.error("Tool resolution failed: %s", exc)
        return http_response(400, rpc_error(event, f"Tool resolution failed: {exc}", code=-32600))

    logger.info("Tool called: %s", tool_name)

    # =====================================================
    # 3. TOOL EXECUTION
    # =====================================================
    try:
        result = _run_async(dispatch(tool_name, event))
        return http_response(200, rpc_result(event, result))

    except ValidationError as exc:
        logger.warning("Validation error for tool '%s': %s", tool_name, exc)
        return http_response(400, rpc_error(event, f"Validation error: {exc}", code=-32602))

    except ValueError as exc:
        logger.warning("Value error for tool '%s': %s", tool_name, exc)
        return http_response(400, rpc_error(event, str(exc), code=-32602))

    except Exception as exc:
        logger.exception("Unexpected error executing tool '%s'", tool_name)
        return http_response(500, rpc_error(event, str(exc)))