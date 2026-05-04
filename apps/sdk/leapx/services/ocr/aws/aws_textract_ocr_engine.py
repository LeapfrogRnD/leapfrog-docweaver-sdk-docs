import boto3

from leapx.common.observability import observe
from leapx.common.observability.logger import logger
from leapx.common.types.providers import OCRProviderType
from leapx.services.credentials.ocr.aws_config import AwsOcrCredential
from leapx.services.layout_parser.structures.ocr_data import OCRData
from leapx.services.ocr.aws.aws_textract_facade import get_aws_textract_facade
from leapx.services.ocr.base.ocr_engine import OCREngine
from leapx.services.ocr.base.ocr_facade import OCRFacadeInterface
from leapx.services.ocr.engine_factory import register_ocr_engine


@register_ocr_engine(OCRProviderType.AWS_TEXTRACT)
class AwsTextractOCREngine(OCREngine):
    """
    OCR Engine for AWS Textract

    This class provides an implementation of the OCREngine interface
    for Amazon Textract service. It handles document
    analysis, text extraction, and credential management for AWS Textract service.

    Attributes:
        access_key_id: AWS access key ID
        secret_access_key: AWS secret access key
        region_name: AWS region name
        client: AWS Textract client instance
        facade: OCR facade interface for processing operations
    """

    def __init__(self, facade: OCRFacadeInterface | None = None):
        """
        Initialize the AWS Textract OCR Engine.

        Args:
            facade: Optional OCRFacadeInterface instance. If None,
                   a default AWS Textract facade will be created.
        """
        super().__init__()
        self.access_key_id: str | None = None
        self.secret_access_key: str | None = None
        self.region_name: str | None = None
        self.client: boto3.client | None = None
        self.facade: OCRFacadeInterface = facade or get_aws_textract_facade()

    def configure(self, credential: AwsOcrCredential) -> bool:
        """
        Configure the AWS Textract service connection.

        Sets up the access credentials and region for communicating
        with AWS Textract service.

        Args:
            credential: AwsOcrCredential

        Returns:
            bool: True if configuration was successful
        """
        self.credential = credential

        self.is_configured = True
        logger.info(
            "AWS Textract OCR Engine configured", region=self.credential.region_name
        )

        return True

    def initialize(self, credential: AwsOcrCredential) -> bool:
        """
        Initialize the AWS Textract client and configure the facade.

        Performs full initialization including configuration, credential
        validation, and facade setup. This method should be called
        before attempting to extract text from documents.

        Args:
            credential: Credential class

        Returns:
            bool: True if initialization was successful, False otherwise
        """
        self.configure(credential=credential if credential else AwsOcrCredential())
        self.client = boto3.client(
            "textract",
            aws_access_key_id=self.credential.access_key_id,
            aws_secret_access_key=self.credential.secret_access_key,
            aws_session_token=self.credential.session_token,
            region_name=self.credential.region_name,
        )
        self.facade.set_client(self.client)
        return True

    @observe(
        name="aws_textract.extract_text",
        capture_input=True,
        capture_output=False,
    )
    async def extract_text(self, input_data: str | bytes) -> list[OCRData]:
        """
        Extract text from a document using AWS Textract.

        Processes the input document through the AWS Textract facade asynchronously
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
                "Text extraction completed",
            )
        except Exception as e:
            logger.error(
                "AWS Textract extraction failed",
                error=str(e),
            )
            raise
        return results
