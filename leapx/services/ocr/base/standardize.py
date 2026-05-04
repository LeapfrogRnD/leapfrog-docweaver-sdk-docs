from abc import abstractmethod

from leapx.services.layout_parser.structures.ocr_data import OCRData


class BaseOCRStandardizer:
    """
    Standardizes OCR output from different providers to OCRData format.

    This class converts raw OCR results (dictionaries) from various providers
    into the standardized OCRData structure used throughout the system.
    """

    @staticmethod
    def _extract_bbox_from_polygon(
        polygon: list[float],
        dpi: float = 9.0,
    ) -> tuple[float, float, float, float]:
        """
        Extract bounding box coordinates from polygon points.

        Args:
            polygon: List of alternating x, y coordinates [x0, y0, x1, y1, ...]
                    For Azure Document Intelligence, these are in inches.
            dpi: Dots per inch for conversion to pixels (default: 9.0)

        Returns:
            Tuple of (x0, y0, x2, y2) representing the bounding box in pixels
        """
        polygon_side_count = 4
        if not polygon or len(polygon) < polygon_side_count:
            return (0.0, 0.0, 0.0, 0.0)

        x_coords = polygon[0::2]
        y_coords = polygon[1::2]

        if not x_coords or not y_coords:
            return (0.0, 0.0, 0.0, 0.0)

        # Convert from inches to pixels
        x0 = min(x_coords) * dpi
        y0 = min(y_coords) * dpi
        x2 = max(x_coords) * dpi
        y2 = max(y_coords) * dpi

        return (float(x0), float(y0), float(x2), float(y2))

    @abstractmethod
    def standardize_ocr_output(self, raw_output: dict[str, any]) -> list[OCRData]:
        """
        Convenience function to standardize OCR output.

        Args:
            raw_output: Raw output dictionary from OCR provider

        Returns:
            List of OCRData objects, one per page
        """
        pass
