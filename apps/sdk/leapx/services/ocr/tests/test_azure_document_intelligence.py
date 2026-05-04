from unittest.mock import AsyncMock, patch

import pytest

from leapx.services.layout_parser.structures.ocr_data import OCRData
from leapx.services.ocr.azure.azure_ocr_engine import AzureOCREngine


class TestAzureOCREngine:
    @patch("leapx.services.ocr.azure.azure_ocr_engine.DocumentIntelligenceClient")
    def test_initialize(self, mock_client, mock_credential, mock_facade):
        """Test engine initialization with credentials."""
        engine = AzureOCREngine(facade=mock_facade)

        result = engine.initialize(mock_credential)
        assert result is True
        assert engine.is_configured is True
        mock_client.assert_called_once()
        mock_facade.set_client.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_text_success(
        self, mock_facade, mock_ocr_data, mock_credential
    ):
        """Test successful text extraction from document."""
        from unittest.mock import patch

        mock_facade.process_document = AsyncMock(return_value=mock_ocr_data)
        engine = AzureOCREngine(facade=mock_facade)

        with patch(
            "leapx.services.ocr.azure.azure_ocr_engine.DocumentIntelligenceClient"
        ):
            engine.initialize(mock_credential)
            result = await engine.extract_text("test.pdf")

        assert result is not None
        assert len(result) == 1
        assert isinstance(result[0], OCRData)
        assert result[0].word_count == 2
        mock_facade.process_document.assert_awaited_once_with("test.pdf")

    @pytest.mark.asyncio
    @patch("leapx.services.ocr.azure.azure_ocr_engine.DocumentIntelligenceClient")
    async def test_extract_text_with_bytes(
        self, mock_client, mock_credential, mock_facade, mock_ocr_data
    ):
        """Test text extraction with bytes input."""
        mock_facade.process_document.return_value = mock_ocr_data
        engine = AzureOCREngine(facade=mock_facade)
        engine.initialize(mock_credential)

        document_bytes = b"fake pdf content"
        result = await engine.extract_text(document_bytes)

        assert result is not None
        assert len(result) == 1
        mock_facade.process_document.assert_called_once_with(document_bytes)

    @pytest.mark.asyncio
    @patch("leapx.services.ocr.azure.azure_ocr_engine.DocumentIntelligenceClient")
    async def test_extract_text_failure(
        self, mock_client, mock_credential, mock_facade
    ):
        """Test extraction failure handling."""
        mock_facade.process_document.side_effect = Exception("API Error")
        engine = AzureOCREngine(facade=mock_facade)
        engine.initialize(mock_credential)

        with pytest.raises(Exception, match="API Error"):
            await engine.extract_text("test.pdf")
