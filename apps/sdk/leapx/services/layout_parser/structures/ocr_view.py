from pydantic import BaseModel


class OCRDataView(BaseModel):
    """Safe view of OCRData for Pydantic"""

    df: list[dict]
    metadata: dict
