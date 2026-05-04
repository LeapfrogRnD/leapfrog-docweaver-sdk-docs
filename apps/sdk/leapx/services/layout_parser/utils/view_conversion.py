from leapx.services.layout_parser.structures.ocr_data import OCRData
from leapx.services.layout_parser.structures.ocr_view import OCRDataView


def ocrdata_to_view(ocr_data_list: list[OCRData]) -> OCRDataView:
    """Convert OCRData → Pydantic-safe OCRDataView"""
    return [
        OCRDataView(
            df=ocr.df.to_dict(orient="records"), metadata=ocr.metadata
        ).model_dump()
        if ocr is not None
        else OCRDataView(df=[], metadata={}).model_dump()
        for ocr in ocr_data_list
    ]
