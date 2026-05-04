"""Pipeline text processing utilities."""


class TextProcessor:
    """Handles text combination and normalization for pipeline."""

    @staticmethod
    def normalize_ocr_data(ocr_data_list) -> list:
        """Ensure OCR data is a list."""
        return ocr_data_list if isinstance(ocr_data_list, list) else [ocr_data_list]

    @staticmethod
    def combine_parsed_pages(parsed_pages: list, total_pages: int) -> str:
        """Combine parsed pages into a single text string."""
        combined_parts = []
        for page_data in parsed_pages:
            if total_pages > 1:
                combined_parts.append(f"--- Page {page_data['page_number']} ---")
            combined_parts.append(page_data["text"])
            if total_pages > 1:
                combined_parts.append("")
        return "\n".join(combined_parts)
