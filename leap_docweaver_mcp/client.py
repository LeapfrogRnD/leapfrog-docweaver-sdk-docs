from collections.abc import Callable
import logging
from typing import Awaitable

import httpx
from httpx import RequestNotRead

from .config import BACKEND_API_URL, X_API_KEY

logger = logging.getLogger("docweaver-mcp")


async def _get_api_client() -> httpx.AsyncClient:
    """Return an async HTTP client with standard headers and logging hooks."""
    headers = {
        "X-API-Key": X_API_KEY,
        "X-Client-Source": "mcp-server",
        "Accept": "application/json",
    }

    async def log_request(request: httpx.Request) -> None:
        logger.info("Request: %s %s", request.method, request.url)
        logger.info("Headers: %s", request.headers)
        logger.info("Full url: %s", request.url)
        try:
            body = request.content
        except RequestNotRead:
            logger.info("Body: <streaming request body omitted>")
            return

        if body:
            preview = body[:2000] if isinstance(body, (bytes, bytearray)) else str(body)[:2000]
            logger.info("Body: %s", preview)

    async def log_response(response: httpx.Response) -> None:
        logger.info("Response: %s %s", response.status_code, response.url)
        try:
            body = await response.aread()
            body_preview = body.decode(errors="replace")[:2000]
            logger.info("Response Body: %s", body_preview)
        except Exception as exc:  # pragma: no cover
            logger.warning("Failed to log response body: %s", exc)

    return httpx.AsyncClient(
        base_url=BACKEND_API_URL,
        headers=headers,
        timeout=120.0,
        event_hooks={
            "request": [log_request],
            "response": [log_response],
        },
    )


async def call_with_client(
    handler: Callable[[httpx.AsyncClient], Awaitable[str]],
) -> str:
    """Run handler with a managed API client, returning any exception as an error string."""
    async with await _get_api_client() as client:
        try:
            return await handler(client)
        except httpx.HTTPStatusError as exc:
            error_detail = exc.response.text
            logger.error("HTTP error %s for %s: %s", exc.response.status_code, exc.request.url, error_detail)
            return f"Error {exc.response.status_code}: {error_detail}"
        except Exception as exc:
            logger.error("Tool error: %s", str(exc))
            return f"Error: {str(exc)}"