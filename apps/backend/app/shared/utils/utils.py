import json
import re
import uuid
from datetime import datetime

from app.shared.exceptions.validation_exceptions import (
    InvalidJSONError,
)


def get_llm_provider(llm_model: str) -> str:
    """
    Determine LLM provider based on model name.

    Args:
        llm_model: Name of the LLM model

    Returns:
        Provider name ('openai' or 'bedrock')
    """
    from app.shared.constants.app_constants import LLMProviderType

    if "gpt" in llm_model.lower():
        return LLMProviderType.OPENAI
    return LLMProviderType.BEDROCK


def parse_json(data: str, field_name: str) -> dict:
    """Parse JSON string with proper error handling."""
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        raise InvalidJSONError(detail=f"{field_name}: {e!s}") from e


def generate_unique_filename(extension: str = ".pdf") -> tuple[str, str]:
    """Generate a unique filename with timestamp. Returns (filename, unique_id)."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}{extension}", unique_id


def to_snake_case(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", "_", text)
    text = text.lower()
    return re.sub(r"[^\w_]", "", text)
