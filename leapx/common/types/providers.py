from enum import Enum


class OCRProviderType(str, Enum):
    AWS_TEXTRACT = "aws_textract"
    AZURE = "azure_document_intelligence"


class VLMProviderType(str, Enum):
    BEDROCK = "bedrock"


class LLMProviderType(str, Enum):
    BEDROCK = "bedrock"
    OPENAI = "openai"


class ParsingMethod(str, Enum):
    """
    Available parsing methods for layout preservation.

    Each method represents a different strategy for converting OCR DataFrame
    to formatted text while preserving document layout.
    """

    LAYOUT_CONSERVED = "layout_conserved"
    """Basic layout preservation with fixed pixel-to-char ratio."""

    LAYOUT_CONSERVED_ADVANCE = "layout_conserved_advance"
    """Advanced layout preservation with dynamic spacing and overlap detection."""

    # Future methods (TODO)
    # """LLM-based parsing with structured output."""
    #
    # """Vision-Language Model based parsing."""

    def __str__(self) -> str:
        """Return the string value of the enum."""
        return self.value


class BedrockModel(Enum):
    claude_4_5 = "bedrock/us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    llama_3_2_1b = "bedrock/us.meta.llama3-2-1b-instruct-v1:0"
    qwen3 = "bedrock/qwen.qwen3-32b-v1:0"


class OpenAIModel(Enum):
    gpt_4_1_nano = "gpt-4.1-nano"


class BedrockVLMModel(Enum):
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
