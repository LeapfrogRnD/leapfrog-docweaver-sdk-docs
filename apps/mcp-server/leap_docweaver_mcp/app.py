import logging
import json

from fastmcp import FastMCP
from fastmcp.server.auth.middleware import RequireAuthMiddleware as FastMCPRequireAuthMiddleware, logger
from fastmcp.server.auth import JWTVerifier, RemoteAuthProvider, StaticTokenVerifier
from fastmcp.server import http as fastmcp_http
from starlette.types import Send

from .config import (
    MCP_ACCESS_TOKEN,
    MCP_AUTH_ENABLED,
    MCP_AUTH_MODE,
    MCP_AUTHORIZATION_SERVER_URL,
    MCP_CLIENT_ID,
    MCP_JWT_ALGORITHM,
    MCP_JWT_AUDIENCE,
    MCP_JWT_ISSUER,
    MCP_JWT_JWKS_URI,
    MCP_JWT_PUBLIC_KEY,
    MCP_REQUIRED_SCOPES,
    MCP_RESOURCE_SERVER_BASE_URL,
)
from .tools import register_tools

logging.basicConfig(level=logging.INFO)


class DocWeaverRequireAuthMiddleware(FastMCPRequireAuthMiddleware):
    """Customize WWW-Authenticate challenge for better MCP client onboarding."""

    async def _send_auth_error(self, send: Send, status_code: int, error: str, description: str) -> None:
        missing_token = status_code == 401 and error == "invalid_token" and description == "Authentication required"

        challenge_error = error
        challenge_description = description
        if missing_token:
            challenge_error = "invalid_request"
            challenge_description = "Bearer token not found in Authorization header"

        www_auth_parts = ['realm="mcp"']
        if challenge_error:
            www_auth_parts.append(f'error="{challenge_error}"')
        if challenge_description:
            www_auth_parts.append(f'error_description="{challenge_description}"')
        if self.resource_metadata_url:
            www_auth_parts.append(f'resource_metadata="{self.resource_metadata_url}"')

        www_authenticate = f"Bearer {', '.join(www_auth_parts)}"

        body = {
            "error": challenge_error,
            "error_description": challenge_description,
        }
        body_bytes = json.dumps(body).encode()
        logger.info("Sending auth error response: %s", www_authenticate )
        await send(
            {
                "type": "http.response.start",
                "status": status_code,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body_bytes)).encode()),
                    (b"www-authenticate", www_authenticate.encode()),
                ],
            }
        )

        await send(
            {
                "type": "http.response.body",
                "body": body_bytes,
            }
        )


# Ensure FastMCP's HTTP app builder uses the customized challenge response.
fastmcp_http.RequireAuthMiddleware = DocWeaverRequireAuthMiddleware


def _build_token_verifier():
    """Return a token verifier based on MCP_AUTH_MODE."""
    if MCP_AUTH_MODE == "jwt":
        missing = []
        if not MCP_JWT_JWKS_URI and not MCP_JWT_PUBLIC_KEY:
            missing.append("MCP_JWT_JWKS_URI or MCP_JWT_PUBLIC_KEY")
        if missing:
            raise ValueError("JWT auth mode requires: " + ", ".join(missing))
        return JWTVerifier(
            jwks_uri=MCP_JWT_JWKS_URI or None,
            public_key=MCP_JWT_PUBLIC_KEY or None,
            issuer=MCP_JWT_ISSUER,
            audience=MCP_JWT_AUDIENCE,
            algorithm=MCP_JWT_ALGORITHM,
            required_scopes=MCP_REQUIRED_SCOPES or None,
        )

    # default: static single-token mode (dev/testing)
    if not MCP_ACCESS_TOKEN:
        raise ValueError("MCP_AUTH_MODE=static requires MCP_ACCESS_TOKEN to be set")

    return StaticTokenVerifier(
        tokens={
            MCP_ACCESS_TOKEN: {
                "client_id": MCP_CLIENT_ID,
                "scopes": MCP_REQUIRED_SCOPES,
            }
        },
        required_scopes=MCP_REQUIRED_SCOPES,
    )


def _build_auth_provider() -> RemoteAuthProvider | None:
    """Build auth provider that emits RFC-compliant 401 + resource_metadata hints."""
    if not MCP_AUTH_ENABLED:
        return None

    missing = []
    if not MCP_RESOURCE_SERVER_BASE_URL:
        missing.append("MCP_RESOURCE_SERVER_BASE_URL")
    if not MCP_AUTHORIZATION_SERVER_URL:
        missing.append("MCP_AUTHORIZATION_SERVER_URL")
    if missing:
        raise ValueError(
            "MCP auth is enabled but required settings are missing: " + ", ".join(missing)
        )

    return RemoteAuthProvider(
        token_verifier=_build_token_verifier(),
        authorization_servers=[MCP_AUTHORIZATION_SERVER_URL],
        base_url=MCP_RESOURCE_SERVER_BASE_URL,
        scopes_supported=MCP_REQUIRED_SCOPES,
    )


def create_mcp() -> FastMCP:
    """Create and configure the DocWeaver MCP server instance."""
    auth = _build_auth_provider()
    mcp = FastMCP("DocWeaver Orchestrator", auth=auth)
    register_tools(mcp)
    return mcp
