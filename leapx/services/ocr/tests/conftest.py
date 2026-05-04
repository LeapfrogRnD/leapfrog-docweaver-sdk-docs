from unittest.mock import AsyncMock, Mock

import pandas as pd
import pytest

from leapx.services.credentials.ocr.azure_config import AzureOcrCredential
from leapx.services.layout_parser.structures.ocr_data import OCRData


@pytest.fixture
def mock_credential():
    """Fixture for Azure OCR credentials."""
    return AzureOcrCredential(
        endpoint="https://test.cognitiveservices.azure.com/", api_key="test_api_key"
    )


@pytest.fixture
def mock_ocr_data():
    """Fixture for mock OCR data response."""
    df = pd.DataFrame(
        {
            "x0": [0.0, 10.0],
            "y0": [0.0, 0.0],
            "x2": [8.0, 18.0],
            "y2": [10.0, 10.0],
            "value": ["Hello", "World"],
            "page": [0, 0],
            "confidence": [0.95, 0.98],
        }
    )
    return [OCRData(df=df, metadata={"page_count": 1})]


@pytest.fixture
def mock_facade():
    """Fixture for mocked OCR facade."""
    facade = Mock()
    facade.set_client = Mock()
    facade.process_document = AsyncMock()
    return facade
