from enum import Enum, StrEnum


class FileConstants:
    """File-related constants."""

    MAX_FILE_SIZE_MB = 10
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    MAX_PAGES = 30
    ALLOWED_EXTENSIONS = {".pdf"}  # noqa: RUF012
    DEFAULT_CONTENT_TYPE = "application/pdf"


class TaskTypes:
    """Supported task types."""

    EXTRACTION = "extraction"
    CLASSIFICATION = "classification"
    SUMMARIZATION = "summarization"
    BOTH = "both"


class RunTypes:
    """Supported run types."""

    API_WORKFLOW = "api_workflow"
    TASK_WORKFLOW = "task_workflow"


class StorageMode:
    """Storage mode options."""

    LOCAL = "local"
    S3 = "s3"


class Roles(StrEnum):
    """User roles."""

    USER = "user"
    ADMIN = "admin"


class RolesClass:
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    USER = "user"

    HIERARCHY = [USER, ADMIN, SUPERADMIN]

    @classmethod
    def rank(cls, role: str) -> int:
        try:
            return cls.HIERARCHY.index(role)
        except ValueError:
            return -1


class OCRProviderType(StrEnum):
    AWS_TEXTRACT = "aws_textract"
    AZURE = "azure_document_intelligence"
    VLM = "vlm"


class VLMProviderType(StrEnum):
    BEDROCK = "bedrock"


class LLMProviderType(StrEnum):
    BEDROCK = "bedrock"
    OPENAI = "openai"


class ParsingMethod(StrEnum):
    LAYOUT_CONSERVED = "layout_conserved"


class BedrockModel(StrEnum):
    claude_4_5 = "bedrock/us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    llama_3_2_1b = "bedrock/us.meta.llama3-2-1b-instruct-v1:0"
    qwen3 = "bedrock/qwen.qwen3-32b-v1:0"


class OpenAIModel(StrEnum):
    gpt_4_1_nano = "gpt-4.1-nano"


class BedrockVLMModel(StrEnum):
    bedrock = "bedrock/qwen.qwen3-vl-235b-a22b"
    anthropic = "bedrock/global.anthropic.claude-sonnet-4-5-20250929-v1:0"


LLMModel = BedrockModel | OpenAIModel
VLMModel = BedrockVLMModel

LLM_MODEL_GROUPS: dict[LLMProviderType, type[Enum]] = {
    LLMProviderType.BEDROCK: BedrockModel,
    LLMProviderType.OPENAI: OpenAIModel,
}

VLM_MODEL_GROUPS: dict[VLMProviderType, type[Enum]] = {
    VLMProviderType.BEDROCK: BedrockVLMModel
}

# Human-readable labels for providers and models
OCR_PROVIDER_LABELS: dict[OCRProviderType, str] = {
    OCRProviderType.AWS_TEXTRACT: "AWS Textract",
    OCRProviderType.AZURE: "Azure OCR",
    OCRProviderType.VLM: "VLM OCR",
}

LLM_PROVIDER_LABELS: dict[LLMProviderType, str] = {
    LLMProviderType.BEDROCK: "Bedrock",
    LLMProviderType.OPENAI: "OpenAI",
}

VLM_PROVIDER_LABELS: dict[VLMProviderType, str] = {
    VLMProviderType.BEDROCK: "Bedrock VLM",
}

PARSING_METHOD_LABELS: dict[ParsingMethod, str] = {
    ParsingMethod.LAYOUT_CONSERVED: "Layout Conserved"
}

BEDROCK_MODEL_LABELS: dict[BedrockModel, str] = {
    BedrockModel.claude_4_5: "Anthropic Claude Sonnet 4.5",
    BedrockModel.llama_3_2_1b: "Meta LLaMA 3 2.1B Instruct",
    BedrockModel.qwen3: "Qwen 3 32B",
}

OPENAI_MODEL_LABELS: dict[OpenAIModel, str] = {
    OpenAIModel.gpt_4_1_nano: "GPT-4.1 Nano",
}

BEDROCK_VLM_MODEL_LABELS: dict[BedrockVLMModel, str] = {
    BedrockVLMModel.bedrock: "Qwen 3 VL 235B",
    BedrockVLMModel.anthropic: "Anthropic Claude Sonnet 4.5 VLM",
}


class TaskStatus(StrEnum):
    """Task status options."""

    DRAFT = "draft"
    READY = "ready"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileUploadStatus(StrEnum):
    "File upload status"

    PENDING = "pending"
    UPLOADED = "uploaded"
    FAILED = "failed"


class Actions(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    GET = "GET"
    REGENERATE = "regenerate"
    TOGGLE = "toggle"


UPLOAD_PRESIGNED_URL_EXPIRATION_SECONDS = 300
DOWNLOAD_PRESIGNED_URL_EXPIRATION_SECONDS = 1800
DEFAULT_CONTENT_TYPE = "application/pdf"

S3_URI_REGEX = r"^s3://[a-z0-9.-]+(/[a-zA-Z0-9._-]+)+(\.[a-zA-Z0-9]+)?$"
