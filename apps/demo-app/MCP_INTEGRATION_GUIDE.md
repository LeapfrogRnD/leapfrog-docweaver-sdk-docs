# DocWeaver MCP — End-to-End Integration Guide

This guide walks you through the complete journey of connecting any AI client to DocWeaver's document intelligence capabilities. It covers the "why" and "how" at a conceptual level, then provides concrete steps for each stage.

---

## How It All Fits Together

DocWeaver exposes document intelligence (extraction, summarization, classification) through the [Model Context Protocol (MCP)](https://spec.modelcontextprotocol.io/). This means any MCP-aware AI agent — Claude, GitHub Copilot, Cursor, or your own custom agent — can call DocWeaver tools using natural language.

```
                                                    ┌──────────────────────┐
  ┌──────────────────┐     MCP (HTTP/SSE)           │  DocWeaver MCP Server│
  │  AI Client       │ ───────────────────────────► │  (FastMCP, port 8000)│
  │  Claude / Copilot│ ◄─────────────────────────── │                      │
  │  Cursor / Custom │     Tool results              └──────────┬───────────┘
  └──────────────────┘                                          │ REST + X-API-Key
                                                                ▼
                                              ┌────────────────────────────────┐
                                              │  DocWeaver Backend             │
                                              │  (FastAPI, port 8001)          │
                                              │  ┌──────────┐ ┌─────────────┐ │
                                              │  │ Workflows │ │ OAuth Server│ │
                                              │  └──────────┘ └─────────────┘ │
                                              └────────────────────────────────┘
```

The MCP server is a **thin bridge**: it receives tool calls from AI clients, translates them into backend API requests (workflow creation + job polling), and streams results back.

---

## Stage 1 — Choose Your Authentication Strategy

Before writing a single line of config, decide which authentication path fits your use case.

```
Are you building for production?
│
├─ NO  ──► Use Static Token auth (fastest, no backend setup needed beyond the API key)
│
└─ YES ──► Will end users log in via a browser (Claude, Cursor, VS Code OAuth flow)?
           │
           ├─ YES ──► OAuth 2.0 with the DocWeaver Backend as the authorization server
           │          (requires registering an OAuth client — see Stage 2)
           │
           └─ NO  ──► JWT Verification (bring your own authorization server)
```

| Mode | Use case | Setup complexity |
|------|----------|-----------------|
| `static` | Local dev, internal tools, CI pipelines | Low — one env var |
| `jwt` | Custom auth infrastructure, service-to-service | Medium — JWKS endpoint |
| `oauth2` | End-user AI clients (Claude, Copilot, Cursor) | Higher — OAuth client registration |

---

## Stage 2 — Prepare the Backend

The DocWeaver backend (`leap-doc-weaver-be`) must be running and accessible before the MCP server can do anything useful.

### 2.1 Obtain an API Key

Every request from the MCP server to the backend carries an `X-API-Key` header. Obtain this key from your backend administrator or generate one in the admin UI.

This key goes into the MCP server's environment:

```env
BACKEND_API_URL=https://your-backend.example.com
X_API_KEY=<your-api-key>
```

### 2.2 Register an OAuth Client

You must register a client application with the backend **before** launching the MCP server. This registration yields the `client_id` that your AI client will use throughout the OAuth flow.

#### Option A — Dynamic Registration via API (RFC 7591)

Any HTTP client can register. No authentication required for the `/register` endpoint.

```http
POST https://your-backend.example.com/register
Content-Type: application/json

{
  "client_name": "my-mcp-client",
  "redirect_uris": ["https://mcp.example.com/oauth/callback"],
  "scope": "mcp:read mcp:write"
}
```

**Response:**
```json
{
  "client_id": "gX2_Kf8mZqLpTrVwNyO0sEuD",
  "client_secret": null,
  "client_name": "my-mcp-client",
  "redirect_uris": ["https://mcp.example.com/oauth/callback"],
  "scope": "mcp:read mcp:write"
}
```

Save the `client_id`. It is needed in the OAuth authorization flow and should be configured in the AI client.

> **Note:** DocWeaver uses public clients (no `client_secret`). Authentication is instead secured by PKCE (Proof Key for Code Exchange, RFC 7636).

#### Option B — Admin API (manage existing clients)

| Action | Request |
|--------|---------|
| List all clients | `GET /clients?page=1&page_size=25` |
| Update a client | `PUT /clients/{client_id}` with `{ "redirect_uris": [...], "scope": "..." }` |
| Deactivate a client | `DELETE /clients/{client_id}` |

Example — update redirect URIs for an existing client:
```http
PUT https://your-backend.example.com/clients/gX2_Kf8mZqLpTrVwNyO0sEuD
Content-Type: application/json

{
  "redirect_uris": [
    "https://mcp.example.com/oauth/callback",
    "http://localhost:8000/oauth/callback"
  ]
}
```

---

## Stage 3 — Configure and Start the MCP Server

### 3.1 Install

```bash
cd leap_docweaver_mcp
uv sync
```

### 3.2 Create `.env`

```env
BACKEND_API_URL=https://your-backend.example.com
X_API_KEY=your-api-key

MCP_AUTH_ENABLED=true
MCP_AUTH_MODE=jwt
MCP_JWT_JWKS_URI=https://your-backend.example.com/auth/jwks
MCP_JWT_ISSUER=https://your-backend.example.com
MCP_JWT_AUDIENCE=docweaver-mcp           # optional, omit if not set on token
MCP_REQUIRED_SCOPES=mcp:read,mcp:write
MCP_RESOURCE_SERVER_BASE_URL=https://mcp.example.com
MCP_AUTHORIZATION_SERVER_URL=https://your-backend.example.com

DEFAULT_PORT=8000
```

### 3.3 Start

```bash
uv run python server.py
# Server is ready at http://0.0.0.0:8000/mcp
```

---

## Stage 4 — Connect Your AI Client

The MCP endpoint is always: `http://<host>:<port>/mcp`

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "docweaver": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

No `Authorization` header is needed. Claude detects the `WWW-Authenticate` challenge and launches the browser login flow automatically using the `client_id` registered in Stage 2.

### VS Code (GitHub Copilot Agent Mode)

Add to `.vscode/mcp.json` or user `settings.json`:

```json
{
  "mcp": {
    "servers": {
      "docweaver": {
        "type": "http",
        "url": "http://localhost:8000/mcp"
      }
    }
  }
}
```

### Cursor

In Settings → MCP Servers:

```json
{
  "mcpServers": {
    "docweaver": {
      "url": "http://localhost:8000/mcp",
      "type": "streamable-http"
    }
  }
}
```

Cursor will follow the OAuth 2.0 redirect and prompt the user to log in via browser.

### Custom Python Client

For programmatic access, complete the OAuth flow to obtain an access token first, then pass it as a Bearer header:

```python
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

async with streamablehttp_client(
    url="http://localhost:8000/mcp",
    headers={"Authorization": "Bearer <oauth-access-token>"},
) as (read, write, _):
    async with ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool(
            "extract_custom_data",
            {
                "base64_data": "<base64-encoded-pdf>",
                "file_name": "invoice.pdf",
                "field_definitions": [
                    {"name": "invoice_number", "type": "string"},
                    {"name": "total_amount", "type": "number"},
                ],
            },
        )
```

---

## Stage 5 — OAuth 2.0 Full Flow (End-User Login)

When an end-user AI client (Claude, Cursor, VS Code) connects without a pre-shared token, the following flow happens automatically. Understanding it helps you debug auth issues and configure `redirect_uris` correctly.

```
 AI Client                  MCP Server              Backend (Auth Server)      Browser / User
    │                           │                          │                        │
    │── GET /mcp ───────────────►│                          │                        │
    │◄─ 401 WWW-Authenticate ───│                          │                        │
    │   (resource_metadata_uri) │                          │                        │
    │                           │                          │                        │
    │── GET /.well-known/oauth-protected-resource/mcp ────►│                        │
    │◄─ { authorization_servers, jwks_uri, scopes } ───────│                        │
    │                           │                          │                        │
    │── GET /.well-known/oauth-authorization-server ───────►│                        │
    │◄─ { authorization_endpoint, token_endpoint, ... } ───│                        │
    │                           │                          │                        │
    │── POST /register (once) ─────────────────────────────►│                        │
    │◄─ { client_id } ─────────────────────────────────────│                        │
    │                           │                          │                        │
    │── Redirect user ──────────────────────────────────────────────────────────────►│
    │   GET /authorize?client_id=...&code_challenge=...     │                     User logs in
    │                           │                          │◄──────────────────────│
    │◄──────────────────────────────────────────────────────────────────────────────│
    │   redirect_uri?code=<auth-code>                       │                        │
    │                           │                          │                        │
    │── POST /token ────────────────────────────────────────►│                        │
    │   { grant_type, code, client_id, code_verifier }      │                        │
    │◄─ { access_token (RS256 JWT), refresh_token } ────────│                        │
    │                           │                          │                        │
    │── GET /mcp ───────────────►│                          │                        │
    │   Authorization: Bearer <JWT>                         │                        │
    │◄─ Tool list / responses ──│                          │                        │
```

### Key points

- The `client_id` from `POST /register` must match what the AI client sends during `/authorize`.
- PKCE (`code_challenge` + `code_verifier`) is mandatory — no `client_secret` is used.
- Access tokens are short-lived RS256 JWTs (signed with the backend's RSA private key). The MCP server verifies them using the `GET /auth/jwks` endpoint.
- Refresh tokens can be exchanged for new access tokens using `POST /token` with `grant_type=refresh_token`.

---

## What Happens When a Tool Is Called

Understanding the internal lifecycle helps when you need to tune performance or debug timeouts.

```
AI Client calls: extract_custom_data({ file_name, base64_data, field_definitions })
                                             │
                               MCP Server receives tool call
                                             │
                         ┌───────────────────▼──────────────────────┐
                         │ 1. Validate inputs (base64 XOR s3_url,    │
                         │    vlm params when ocr_provider=vlm)      │
                         └───────────────────┬──────────────────────┘
                                             │
                         ┌───────────────────▼──────────────────────┐
                         │ 2. Resolve workflow name                  │
                         │    Default params → reuse named workflow  │
                         │    Custom params  → hash → unique name    │
                         └───────────────────┬──────────────────────┘
                                             │
                         ┌───────────────────▼──────────────────────┐
                         │ 3. GET /api/workflows/?search=<name>      │
                         │    Found? → reuse it                      │
                         │    Not found? → POST /api/workflows/      │
                         │    (JIT workflow creation)                │
                         └───────────────────┬──────────────────────┘
                                             │
                         ┌───────────────────▼──────────────────────┐
                         │ 4. POST /api/integrations/               │
                         │    (file upload or s3_file_uri)           │
                         │    → returns job_id (Ticket ID)           │
                         └───────────────────┬──────────────────────┘
                                             │
                         ┌───────────────────▼──────────────────────┐
                         │ 5. Poll GET /api/integrations/{job_id}    │
                         │    until status = completed | failed      │
                         └───────────────────┬──────────────────────┘
                                             │
                               Return structured result to AI Client
```

---

## Available Tools at a Glance

| Tool | What it does | Needs a document? |
|------|--------------|-------------------|
| `get_configs` | Lists available OCR providers, LLM providers, and models | No |
| `extract_custom_data` | Extracts named fields (invoice number, total, etc.) per a JSON schema | Yes |
| `summarize_document` | Produces a prose summary of the document | Yes |
| `classify_document` | Assigns document to named categories (severity, type, priority, etc.) | Yes |
| `check_job_status` | Returns the result of any previously submitted job by Ticket ID | No |
| `list_job_history` | Lists recent jobs — useful for recovering a lost Ticket ID | No |

> **Recommended starting sequence:** `get_configs` → pick providers → call a processing tool → `check_job_status` if the job is still running.

Documents can be supplied as:
- **Base64-encoded content** (`base64_data`) — suitable for files already in memory
- **S3 URI** (`s3_url`) — e.g. `s3://my-bucket/docs/invoice.pdf` — suitable for files stored in S3

---

## Quick Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `401 Bearer token not found` | Client did not complete OAuth login flow | Re-trigger the OAuth flow so the client obtains a fresh access token |
| `Unknown or inactive client` | `client_id` not registered or deactivated | Register via `POST /register` or re-activate via `PUT /clients/{client_id}` |
| `Invalid redirect_uri` | URI not in client's registered list | Add it via `PUT /clients/{client_id}` with updated `redirect_uris` |
| `JWT auth requires JWKS_URI or PUBLIC_KEY` | `MCP_JWT_JWKS_URI` not set | Set `MCP_JWT_JWKS_URI` to `https://your-backend.example.com/auth/jwks` |
| Backend 401 on tool calls | Wrong or missing `X_API_KEY` | Verify `X_API_KEY` matches backend expectation |
| Job stuck in `processing` | Backend worker slow/down | Call `check_job_status` to poll; check backend worker logs |
