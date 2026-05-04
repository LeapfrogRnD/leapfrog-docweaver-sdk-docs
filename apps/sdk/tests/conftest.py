from unittest.mock import Mock, patch

import pandas as pd
import pytest
from pydantic import BaseModel

from leapx.services.credentials.bedrock_config import BedrockCredential
from leapx.services.credentials.ocr.azure_config import AzureOcrCredential
from leapx.services.extractor.schemas import ExtractionResponse
from leapx.services.layout_parser.structures.ocr_data import OCRData


# Sample schema for testing
class InvoiceSchema(BaseModel):
    invoice_number: str
    total_amount: float
    vendor_name: str


@pytest.fixture(scope="session", autouse=True)
def _mock_cache_factory():
    """Automatically mock CacheFactory to prevent initialization."""
    mock_cache = Mock()
    mock_cache.is_enabled = False

    with patch(
        "leapx.common.cache.cache_factory.CacheFactory.create_cache",
        return_value=mock_cache,
    ):
        yield


@pytest.fixture
def mock_ocr_credential():
    """Fixture for Azure OCR credentials."""
    return AzureOcrCredential(
        endpoint="https://test.cognitiveservices.azure.com/", api_key="test_api_key"
    )


@pytest.fixture
def mock_llm_credential():
    """Fixture for Bedrock LLM credentials."""
    return BedrockCredential(
        access_key_id="test_access_key",
        secret_access_key="test_secret_key",
        region_name="us-east-1",
    )


@pytest.fixture
def mock_ocr_data():
    """Fixture for mock OCR data."""
    df = pd.DataFrame(
        {
            "x0": [0.0, 10.0, 20.0],
            "y0": [0.0, 0.0, 10.0],
            "x2": [8.0, 18.0, 35.0],
            "y2": [10.0, 10.0, 20.0],
            "value": ["Invoice", "Number", "12345"],
            "page": [0, 0, 0],
            "confidence": [0.95, 0.98, 0.99],
        }
    )
    return [OCRData(df=df, metadata={"page_number": 1})]


@pytest.fixture
def mock_extraction_response():
    """Fixture for mock extraction response."""
    invoice_data = InvoiceSchema(
        invoice_number="INV-12345", total_amount=1250.50, vendor_name="Test Vendor Inc."
    )
    return ExtractionResponse(data=invoice_data, metadata={"model": "claude-4.5"})
