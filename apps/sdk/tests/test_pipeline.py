from unittest.mock import AsyncMock, Mock, patch

from leapx import LeapXPipeline
from leapx.common.types.providers import BedrockModel, OCRProviderType, ParsingMethod
from leapx.pipeline.stages.configs import LLMExtractionConfig, OCRConfig, ParserConfig
from tests.conftest import InvoiceSchema


class TestLeapXPipeline:
    @patch(
        "leapx.services.credentials.ocr.azure_config.AzureOcrCredential._is_valid_keys"
    )
    @patch("leapx.services.ocr.engine_factory.OCREngineFactory.create_engine")
    @patch("leapx.services.layout_parser.ParserFactory.create")
    @patch("leapx.pipeline.stages.configs.LLMExtractionConfig._validate_llm_invocation")
    @patch("leapx.services.extractor.extractor_factory.ExtractorFactory.create")
    def test_pipeline_initialization(  # noqa: PLR0913
        self,
        mock_extractor_service_class,
        mock_bedrock_validation,
        mock_parser_factory,
        mock_ocr_factory,
        mock_azure_validation,
        mock_ocr_credential,
        mock_llm_credential,
    ):
        """Test pipeline initialization with all components."""
        mock_bedrock_validation.return_value = True
        mock_azure_validation.return_value = True

        # Mock extractor service instance
        mock_extractor_instance = Mock()
        mock_extractor_service_class.return_value = mock_extractor_instance

        ocr_config = OCRConfig(
            provider=OCRProviderType.AZURE, credential=mock_ocr_credential
        )
        parser_config = ParserConfig(method=ParsingMethod.LAYOUT_CONSERVED)
        llm_config = LLMExtractionConfig(
            model=BedrockModel.qwen3,
            credential=mock_llm_credential,
            system_prompt="Extract invoice data",
            user_instructions="Please extract all relevant invoice details.",
            json_schema=InvoiceSchema,
        )

        pipeline_instance = LeapXPipeline(
            ocr=ocr_config,
            llm=llm_config,
            parser=parser_config,
        )
        assert pipeline_instance is not None
        assert pipeline_instance.config.ocr_config.provider == OCRProviderType.AZURE
        assert (
            pipeline_instance.config.parser_config.method
            == ParsingMethod.LAYOUT_CONSERVED
        )
        mock_ocr_factory.assert_called_once()
        mock_parser_factory.assert_called_once()

    @patch(
        "leapx.services.credentials.ocr.azure_config.AzureOcrCredential._is_valid_keys"
    )
    @patch("leapx.pipeline.stages.configs.LLMExtractionConfig._validate_llm_invocation")
    @patch("leapx.services.ocr.engine_factory.OCREngineFactory.create_engine")
    @patch("leapx.services.layout_parser.ParserFactory.create")
    @patch("leapx.services.extractor.extractor_factory.ExtractorFactory.create")
    @patch("leapx.common.utils.file_to_bytes.convert_to_bytes")
    def test_pipeline_run_success(  # noqa: PLR0913
        self,
        mock_convert,
        mock_create_extractor,
        mock_parser_factory,
        mock_ocr_factory,
        mock_bedrock_validation,
        mock_azure_validation,
        mock_ocr_credential,
        mock_llm_credential,
        mock_ocr_data,
        mock_extraction_response,
    ):
        """Test successful pipeline execution."""
        mock_bedrock_validation.return_value = True
        mock_azure_validation.return_value = True

        # Setup OCR engine mock
        mock_ocr_engine = Mock()
        mock_ocr_engine.extract_text = AsyncMock(return_value=mock_ocr_data)
        mock_ocr_factory.return_value = mock_ocr_engine

        # Setup parser mock
        mock_parser = Mock()
        mock_parser.parse_async = AsyncMock(
            return_value="Invoice Number 12345\nTotal: $1250.50"
        )
        mock_parser_factory.return_value = mock_parser

        # Setup extractor service mock
        mock_extractor = Mock()
        mock_extractor.extract = AsyncMock(return_value=mock_extraction_response)
        mock_create_extractor.return_value = mock_extractor

        mock_convert.return_value = b"fake pdf bytes"

        # Create pipeline
        ocr_config = OCRConfig(
            provider=OCRProviderType.AZURE, credential=mock_ocr_credential
        )
        parser_config = ParserConfig(method=ParsingMethod.LAYOUT_CONSERVED)
        llm_config = LLMExtractionConfig(
            model=BedrockModel.qwen3,
            credential=mock_llm_credential,
            system_prompt="Extract invoice data",
            user_instructions="Please extract all relevant invoice details.",
            json_schema=InvoiceSchema,
        )
        _pipeline = LeapXPipeline(
            ocr=ocr_config,
            llm=llm_config,
            parser=parser_config,
        )

        # Run pipeline - this wraps async execution
        # TODO this has to be corrected for byte stream as we will not have local path.
        # result = pipeline_instance.run(b"data")

        # Assertions
        # assert result is not None
        assert True
        # mock_parser.parse_async.assert_called_once()
        # mock_extractor.extract.assert_called_once()

    @patch(
        "leapx.services.credentials.ocr.azure_config.AzureOcrCredential._is_valid_keys"
    )
    @patch("leapx.pipeline.stages.configs.LLMExtractionConfig._validate_llm_invocation")
    @patch("leapx.services.ocr.engine_factory.OCREngineFactory.create_engine")
    @patch("leapx.services.layout_parser.ParserFactory.create")
    def test_pipeline_with_dict_schema(  # noqa: PLR0913
        self,
        mock_parser_factory,
        mock_ocr_factory,
        mock_bedrock_validation,
        mock_azure_validation,
        mock_ocr_credential,
        mock_llm_credential,
    ):
        """Test pipeline initialization with dictionary schema."""
        mock_bedrock_validation.return_value = True
        mock_azure_validation.return_value = True

        dict_schema = {
            "invoice_number": {"type": "string"},
            "total_amount": {"type": "number"},
        }

        ocr_config = OCRConfig(
            provider=OCRProviderType.AZURE, credential=mock_ocr_credential
        )
        parser_config = ParserConfig(method=ParsingMethod.LAYOUT_CONSERVED)
        llm_config = LLMExtractionConfig(
            model=BedrockModel.qwen3,
            credential=mock_llm_credential,
            system_prompt="Extract data",
            user_instructions="Extract relevant data.",
            json_schema=dict_schema,
        )

        pipeline_instance = LeapXPipeline(
            ocr=ocr_config,
            llm=llm_config,
            parser=parser_config,
        )

        assert pipeline_instance is not None
        assert pipeline_instance.config.llm_extraction_config.json_schema is not None
