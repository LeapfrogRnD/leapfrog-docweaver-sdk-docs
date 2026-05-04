import os

from dotenv import load_dotenv
from enum import Enum

load_dotenv()

BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8001")
X_API_KEY = os.getenv("X_API_KEY", "").strip()

DEFAULT_PORT = int(os.getenv("DEFAULT_PORT", "8000"))
MCP_AUTH_ENABLED = os.getenv("MCP_AUTH_ENABLED", "true").strip().lower() in {
	"1",
	"true",
	"yes",
	"on",
}
MCP_RESOURCE_SERVER_BASE_URL = os.getenv("MCP_RESOURCE_SERVER_BASE_URL", "").strip()
MCP_AUTHORIZATION_SERVER_URL = os.getenv("MCP_AUTHORIZATION_SERVER_URL", "").strip()
MCP_ACCESS_TOKEN = os.getenv("MCP_ACCESS_TOKEN", "").strip()
MCP_CLIENT_ID = os.getenv("MCP_CLIENT_ID", "docweaver-mcp-client").strip() or "docweaver-mcp-client"
MCP_REQUIRED_SCOPES = [
	scope.strip()
	for scope in os.getenv("MCP_REQUIRED_SCOPES", "openid,profile,email,mcp:read,mcp:write").split(",")
	if scope.strip()
]

# JWT verification — used when MCP_AUTH_MODE=jwt
# Provide either MCP_JWT_JWKS_URI (remote key rotation) or MCP_JWT_PUBLIC_KEY (static PEM)
MCP_AUTH_MODE = os.getenv("MCP_AUTH_MODE", "static").strip().lower()  # "static" | "jwt"

_DEFAULT_JWKS_BASE_URL = (
	MCP_AUTHORIZATION_SERVER_URL
	or os.getenv("MCP_JWT_ISSUER", "").strip()
	or BACKEND_API_URL
)
MCP_JWT_JWKS_URI = os.getenv("MCP_JWT_JWKS_URI", _DEFAULT_JWKS_BASE_URL + "/auth/jwks").strip()

MCP_JWT_PUBLIC_KEY = os.getenv("MCP_JWT_PUBLIC_KEY", "").strip()
MCP_JWT_ISSUER = os.getenv("MCP_JWT_ISSUER", "").strip() or None
MCP_JWT_AUDIENCE = os.getenv("MCP_JWT_AUDIENCE", "").strip() or None
MCP_JWT_ALGORITHM = os.getenv("MCP_JWT_ALGORITHM", "RS256").strip()

DEFAULT_LLM = "bedrock/qwen.qwen3-32b-v1:0"
DEFAULT_LLM_PROVIDER = "bedrock"
DEFAULT_OCR = "aws_textract"
VLM_OCR_PROVIDER = "vlm"

DEFAULT_CLASSIFICATION_ADDITIONAL_INSTRUCTIONS = "Classify the specified fields from the document and return them in a JSON format matching the schema."
DEFAULT_EXTRACTION_ADDITIONAL_INSTRUCTIONS = "Extract the specified fields from the document and return them in a JSON format matching the schema."

DEFAULT_CLASSIFICATION_FIELD_DEFINITIONS = [
	{
		"category": "severity",
		"fields": [
			{
				"name": "High Severity",
				"description": "The issue critically affects the system and requires immediate attention.",
			},
			{
				"name": "Medium Severity",
				"description": "The issue affects functionality but does not completely block the system.",
			},
			{
				"name": "Low Severity",
				"description": "The issue has minimal impact on the system and can be addressed later.",
			},
		],
	},
	{
		"category": "priority",
		"fields": [
			{
				"name": "Urgent",
				"description": "The request needs immediate attention.",
			},
			{
				"name": "Normal",
				"description": "The request should be handled in the normal workflow.",
			},
			{
				"name": "Low Priority",
				"description": "The request can be handled later with minimal urgency.",
			},
		],
	},
]

DEFAULT_EXTRACTION_FIELD_DEFINITIONS = [{"name": "total", "type": "number"}, {"name": "vendor", "type": "string"}]
class WorkflowType(str, Enum):
	EXTRACTION = "extraction"
	SUMMARIZATION = "summarization"
	CLASSIFICATION = "classification"

class McpWorkflowName(str, Enum):
	MCP_SUMMARIZE = "mcp_summarize"
	MCP_CLASSIFY = "mcp_classify"
	MCP_EXTRACT = "mcp_extract"


