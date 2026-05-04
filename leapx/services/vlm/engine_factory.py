# ruff: noqa: TRY003

from typing import Any

from leapx.common.observability.logger import logger
from leapx.pipeline.stages.constants import HTML, VLM_EXTRACTION_PROMPTS
from leapx.services.vlm.vlm_extractor_service import VLMExtractorService


class VLMEngineFactory:
    """
    Factory for creating VLM extractor service instances.
    Supports multiple providers and configurations.
    """

    @staticmethod
    def create_engine(
        model_id: str | None = None,
        credential: dict[str, Any] | None = None,
        region: str | None = None,
        extraction_method: str | None = None,
        extraction_prompt: dict[str, str] | None = None,
    ) -> VLMExtractorService:
        """
        Return a VLMExtractorService instance.

        Raises:
            ValueError: If required parameters are missing.
            RuntimeError: If creation of VLMExtractorService fails.
        """
        # extraction prompt is required for the VLM stage
        prompts = (
            extraction_prompt
            if extraction_prompt is not None
            else VLM_EXTRACTION_PROMPTS.copy()
        )

        try:
            # Validate credential and extract region
            if credential is None:
                logger.warning(
                    "No credentials provided, defaulting region to 'us-east-1'",
                    context="VLMEngineFactory",
                )
                region_name = region or "us-east-1"
            else:
                region_name = credential.get("region_name", region or "us-east-1")
            # Set default extraction method
            extraction_method = extraction_method or HTML
            # Validate required parameters
            if not model_id:
                raise ValueError(  # noqa: TRY301
                    "model_id must be provided to create VLMExtractorService"
                )
            # Initialize the extractor service
            return VLMExtractorService(
                model_id=model_id,
                region=region_name,
                extraction_type=extraction_method,
                extraction_prompt=prompts,
            )

        except ValueError as ve:
            logger.error(
                f"Value error in VLMEngineFactory.create_engine: {ve}",
                context="VLMEngineFactory",
                error_type=type(ve).__name__,
            )
            raise

        except Exception as e:
            logger.error(
                f"Failed to create VLMExtractorService: {e}",
                context="VLMEngineFactory",
                error_type=type(e).__name__,
            )
            raise RuntimeError("VLMEngineFactory failed to create engine") from e
