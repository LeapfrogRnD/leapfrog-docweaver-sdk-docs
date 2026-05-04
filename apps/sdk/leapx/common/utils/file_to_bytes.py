import io
from pathlib import Path

from pypdf import PdfReader


def convert_to_bytes(file_path: str) -> bytes:
    """convert the file into bytes"""
    with Path(file_path).open("rb") as file_instance:
        return file_instance.read()


def is_pdf_blank(pdf_bytes: bytes) -> bool:
    """
    Check if the byte for the chunk is empty works only for pdf .
    Args:
        chunk_bytes(bytes): chunk data in bytes

    Returns: True/ False
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))

    for page in reader.pages:
        text = page.extract_text()
        if text and text.strip():
            return False

        resources = page.get("/Resources")
        if resources:
            xobjects = resources.get("/XObject")
            if xobjects:
                return False

    return True
