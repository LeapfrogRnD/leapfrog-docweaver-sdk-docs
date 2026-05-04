from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

from leapx.common.observability import observe
from leapx.common.observability.logger import logger
from leapx.common.types.providers import OCRProviderType
from leapx.services.credentials.ocr.azure_config import AzureOcrCredential
from leapx.services.layout_parser.structures.ocr_data import OCRData
from leapx.services.ocr.azure.azure_facade import get_azure_facade
from leapx.services.ocr.base.ocr_engine import OCREngine
from leapx.services.ocr.base.ocr_facade import OCRFacadeInterface
from leapx.services.ocr.engine_factory import register_ocr_engine


@register_ocr_engine(OCRProviderType.AZURE)
class AzureOCREngine(OCREngine):
    """
    OCR Engine for Azure

    This class provides an implementation of the OCREngine interface
    for Microsoft Azure OCR Engine service. It handles document
    analysis, text extraction, and credential management for Azure's OCR service.

    Attributes:
        endpoint: Azure OCR Engine service endpoint URL
        api_key: Authentication key for Azure service
        api_version: API version string for the service
        client: Azure OCR Engine client instance
        facade: OCR facade interface for processing operations
    """

    def __init__(self, facade: OCRFacadeInterface | None = None):
        """
        Initialize the Azure OCR Engine.

        Args:
            facade: Optional OCRFacadeInterface instance. If None,
                   a default Azure facade will be created.
        """
        super().__init__()
        self.endpoint: str | None = None
        self.api_key: str | None = None
        self.api_version: str = ""
        self.client: DocumentIntelligenceClient | None = None
        self.facade: OCRFacadeInterface = facade or get_azure_facade()

    def configure(self, credential: AzureOcrCredential) -> bool:
        """
        Configure the Azure OCR Engine service connection.

        Sets up the endpoint, API key, and creates the client instance
        for communicating with Azure OCR Engine service.

        Args:
            credential: AzureOcrCredential

        Returns:
            bool: True if configuration was successful
        """
        self.credential = credential or AzureOcrCredential()

        self.is_configured = True
        logger.info("Azure OCR Engine configured", endpoint=self.endpoint)

        return True

    def initialize(self, credential: AzureOcrCredential) -> bool:
        """
        Initialize the Azure client and configure the facade.

        Performs full initialization including configuration, credential
        validation, and facade setup. This method should be called
        before attempting to extract text from documents.

        Args:
            credential: Credential class

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        self.configure(credential=credential)
        self.client = DocumentIntelligenceClient(
            endpoint=self.credential.endpoint,
            credential=AzureKeyCredential(self.credential.api_key),
        )
        self.facade.set_client(self.client)
        return True

    @observe(
        name="azure_document_intelligence.extract_text",
        capture_input=True,
        capture_output=False,
    )
    async def extract_text(self, input_data: str | bytes) -> list[OCRData]:
        """
        Extract text from a document using Azure OCR Engine.

        Processes the input document through the Azure facade asynchronously
        and returns standardized OCR data. Includes timing and error handling for
        robust operation.

        Args:
            input_data: Document data as either a string (file path) or bytes

        Returns:
            list[OCRData]: List of OCRData objects, one per page, containing
                          extracted text, layout information, and metadata

        Raises:
            Exception: If extraction fails due to service errors,
                      invalid input, or configuration issues
        """
        results = []
        try:
            results = await self.facade.process_document(input_data)
            logger.info(
                "Async text extraction completed",
                timing_type="wall_clock",
            )
        except Exception as e:
            logger.error(
                "Azure async extraction failed",
                error=str(e),
            )
            raise
        return results
