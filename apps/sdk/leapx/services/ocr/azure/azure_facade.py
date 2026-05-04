import asyncio

from azure.ai.documentintelligence import DocumentIntelligenceClient

from leapx.common.observability import observe
from leapx.services.layout_parser.structures.ocr_data import OCRData
from leapx.services.ocr.azure.standardizer import (
    AzureStandardizer,
)
from leapx.services.ocr.base.ocr_facade import OCRFacadeInterface


class AzureFacade(OCRFacadeInterface):
    """
    Azure Document Intelligence Facade
    Handles client creation and document analysis
    Handles call to third party service.
    """

    def __init__(
        self, client: DocumentIntelligenceClient | None = None, model_id="prebuilt-read"
    ):
        self.client = client
        self.model_id = model_id

    def set_client(self, client: DocumentIntelligenceClient):
        self.client = client

    @observe(
        name="azure_facade.process_document_async",
        capture_input=False,
        capture_output=False,
    )
    async def process_document(self, file_bytes: bytes) -> list[OCRData]:
        """Async process the document and return standardized OCRData results"""
        analyze_request = {"base64Source": file_bytes}
        poller = await asyncio.to_thread(self._call_azure_api, analyze_request)
        result = await asyncio.to_thread(self._wait_for_result, poller)
        return AzureStandardizer.standardize_ocr_output(result)

    @observe(name="azure_api.begin_analyze", capture_input=False, capture_output=False)
    def _call_azure_api(self, analyze_request: dict):
        """Call Azure Document Intelligence API and return poller"""
        return self.client.begin_analyze_document(self.model_id, analyze_request)

    @observe(
        name="azure_api.wait_for_result", capture_input=False, capture_output=False
    )
    def _wait_for_result(self, poller):
        """Wait for Azure polling to complete and return result"""
        return poller.result()


def get_azure_facade() -> AzureFacade:
    return AzureFacade()
