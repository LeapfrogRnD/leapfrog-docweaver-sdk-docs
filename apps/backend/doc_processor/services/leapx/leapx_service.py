"""LeapX SDK service for document processing."""

from typing import Any

from core.exceptions import LeapXProcessingException
from leapx import linear_pipeline
from schemas.result import LeapXResult
from utils.logger import log
from utils.provider import build_pipeline_kwargs


class LeapXService:
    """Wrapper for LeapX SDK processing."""

    def __init__(self):
        """Initialize LeapX SDK."""
        try:
            import leapx

            self.leapx = leapx
            log.info("LeapX SDK initialized successfully")
        except ImportError as e:
            log.error(f"Failed to import LeapX SDK: {e}")
            raise LeapXProcessingException(f"LeapX SDK not available: {e}") from e

    async def classify_document(
        self, file_path: str, config: dict[str, Any] | None = None
    ) -> LeapXResult:
        """
        Classify pages of a PDF document and return final response.

        Args:
            file_path: s3 url of the pdf file
            config: Classification configuration

        Returns:
            ClassificationResponse ready to be returned by the route
        """
        config = config or {}
        pipeline_kwargs = build_pipeline_kwargs(config)
        classification_pipeline = linear_pipeline(**pipeline_kwargs)
        result = await classification_pipeline.async_run(input_data=file_path)
        return [
            {"result": data["extraction"], "pages": data["page_numbers"]}
            for data in result["pipeline_results"]
        ]

    async def extract_from_document(
        self, file_path: str, config: dict[str, Any] | None = None
    ) -> LeapXResult:
        """Extract data from document using LeapX SDK."""
        config = config or {}
        pipeline_kwargs = build_pipeline_kwargs(config)
        extraction_pipeline = linear_pipeline(**pipeline_kwargs)
        result = await extraction_pipeline.async_run(input_data=file_path)
        return [
            {"result": data["extraction"], "pages": data["page_numbers"]}
            for data in result["pipeline_results"]
        ]

    async def generate_summary(
        self, file_path: str, config: dict[str, Any] | None = None
    ) -> LeapXResult:
        """Generate summary of document using LeapX SDK."""
        config = config or {}
        pipeline_kwargs = build_pipeline_kwargs(config, use_generation=True)
        summarization_pipeline = linear_pipeline(**pipeline_kwargs)
        result = await summarization_pipeline.async_run(input_data=file_path)
        return [
            {"result": data["generation"], "pages": data["page_numbers"]}
            for data in result["pipeline_results"]
        ]


leapx_service = LeapXService()
