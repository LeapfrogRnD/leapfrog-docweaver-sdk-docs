# ruff: noqa: TRY003

import base64
from collections.abc import Mapping

import fitz
from litellm import acompletion

from leapx.common.observability.logger import logger
from leapx.pipeline.stages.constants import HTML, MARKDOWN


class VLMExtractorService:
    """
    VLM extractor that relies on externally supplied prompts.
    """

    SUPPORTED_METHODS = (HTML, MARKDOWN)

    def __init__(
        self,
        model_id: str,
        extraction_prompt: Mapping[str, str],
        region: str = "us-east-1",
        extraction_type: str = HTML,
    ):
        self.model_id = model_id
        self.region = region
        self.prompts = extraction_prompt
        self.extraction_method = extraction_type

        # Log initialization
        logger.info(
            "Initialized VLMExtractorService",
            model_id=self.model_id,
            region=self.region,
            extraction_method=self.extraction_method,
        )

    async def extract_multi_page(self, pdf_bytes: bytes) -> list[str]:
        outputs: list[str] = []
        method = self._normalized_method()

        try:
            with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                for i, page in enumerate(doc):
                    try:
                        pix = page.get_pixmap()
                        page_bytes = pix.tobytes("png")
                        content = await self.extract(page_bytes)

                        if method == MARKDOWN:
                            outputs.append(f"\n\n## Page {i + 1}\n\n{content}")
                        else:
                            outputs.append(
                                f"<section id='page-{i + 1}'>{content}</section>"
                            )
                    except Exception as e:
                        logger.warning(
                            f"Extraction failed for page {i + 1}: {e}",
                            page=i + 1,
                            method=method,
                        )
                        outputs.append(self._error_block(i + 1, str(e), method))
        except Exception as e:
            logger.error("Failed to open PDF", error=str(e))
            raise RuntimeError("Failed to open PDF") from e

        logger.info(
            "Completed multi-page extraction", total_pages=len(outputs), method=method
        )

        return outputs

    async def extract(self, content: bytes | str) -> str:
        is_text = isinstance(content, str)
        prompt = self._get_prompt()

        messages = self._build_messages(content=content, prompt=prompt, is_text=is_text)

        try:
            response = await acompletion(
                model=self.model_id,
                messages=messages,
                max_tokens=3000,
                temperature=0,
                aws_region_name=self.region,
            )
        except Exception as e:
            logger.error(
                "VLM completion failed",
                error=str(e),
                model=self.model_id,
                region=self.region,
            )
            raise RuntimeError("VLM completion failed") from e

        try:
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error("Invalid VLM response format", response=response, error=str(e))
            raise RuntimeError("Invalid VLM response format") from e

    def _normalized_method(self) -> str:
        method = (self.extraction_method or "").lower()
        if method not in self.SUPPORTED_METHODS:
            logger.warning(
                f"Unsupported extraction method '{method}', defaulting to 'html'"
            )
            method = HTML
        return method

    def _get_prompt(self) -> str:
        method = self._normalized_method()
        prompt = self.prompts.get(method) or self.prompts.get(HTML)

        if not prompt:
            logger.error("No valid extraction prompt found", method=method)
            raise RuntimeError(
                "No valid extraction prompt found (html fallback missing)"
            )

        return prompt.strip()

    def _build_messages(self, content: bytes | str, prompt: str, is_text: bool):
        if is_text:
            return [
                {
                    "role": "user",
                    "content": f"{prompt}\n\nDocument Content:\n{content}",
                }
            ]

        try:
            encoded = base64.b64encode(content).decode("utf-8")
        except Exception as e:
            logger.error("Image base64 encoding failed", error=str(e))
            raise RuntimeError("Image base64 encoding failed") from e

        return [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{encoded}"},
                    },
                ],
            }
        ]

    def _error_block(self, page: int, error: str, method: str) -> str:
        if method == MARKDOWN:
            return f"\n\n## Page {page}\n\n**Extraction failed:** {error}"

        return f"<section id='page-{page}'><p><strong>Extraction failed:</strong> {error}</p></section>"
