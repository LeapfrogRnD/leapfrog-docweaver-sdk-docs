import io
import uuid
from pathlib import Path
from typing import Final
from urllib.parse import urlparse

import pypdf

from leapx.common.exceptions.base import InvalidS3UriError, S3ReadError
from leapx.common.utils.s3_client import get_s3_client

# File type magic number constants
PDF_MAGIC_BYTES: Final[bytes] = b"%PDF"
PNG_MAGIC_BYTES: Final[bytes] = b"\x89PNG\r\n\x1a\n"
JPG_MAGIC_BYTES: Final[bytes] = b"\xff\xd8\xff"


def is_pdf(data: str | Path | bytes) -> tuple[bool, bytes]:
    """Check if data represents a PDF file.

    Args:
        data: File path (str or Path) or bytes to check.

    Returns:
        Tuple of (is_pdf, file_bytes) where is_pdf is True if data is a PDF.
    """

    file_bytes = read_file_to_bytes(data) if isinstance(data, str | Path) else data
    return file_bytes.startswith(PDF_MAGIC_BYTES), file_bytes


def is_image(data: str | Path | bytes) -> tuple[bool, bytes]:
    """Check if data represents a supported image format (PNG or JPG).

    Args:
        data: File path (str or Path) or bytes to check.

    Returns:
        Tuple of (is_image, file_bytes) where is_image is True if data is a PNG or JPG.
    """

    file_bytes = read_file_to_bytes(data) if isinstance(data, str | Path) else data
    is_png = file_bytes.startswith(PNG_MAGIC_BYTES)
    is_jpg = file_bytes.startswith(JPG_MAGIC_BYTES)

    return is_png or is_jpg, file_bytes


def load_pdf(file_path: str | bytes) -> pypdf.PdfReader:
    """Load PDF from file path or bytes."""
    if isinstance(file_path, bytes):
        return pypdf.PdfReader(io.BytesIO(file_path))
    return pypdf.PdfReader(file_path)


def create_chunk_pdf(
    reader: pypdf.PdfReader,
    start_page: int,
    end_page: int,
) -> bytes:
    """Create PDF bytes for a range of pages."""
    writer = pypdf.PdfWriter()
    for page_num in range(start_page, end_page):
        writer.add_page(reader.pages[page_num])

    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def generate_id() -> str:
    """Generate unique chunk ID."""
    return str(uuid.uuid4())[:8]


def read_file_to_bytes(file_path: str | Path) -> bytes:
    """
    Read a file from either S3 or local file system and return its content as bytes.

    Args:
        file_path: Either an S3 URI (s3://bucket/key) or a local file path

    Returns:
        bytes: The file content as bytes

    Raises:
        ValueError: If the file path format is invalid
        FileNotFoundError: If the local file doesn't exist
        Exception: If there's an error reading from S3

    Examples:
        >>> # Read from local file
        >>> content = read_file_to_bytes("/path/to/file.pdf")

        >>> # Read from S3
        >>> content = read_file_to_bytes("s3://my-bucket/documents/file.pdf")
    """
    file_path_str = str(file_path)

    if file_path_str.startswith("s3://"):
        return _read_from_s3(file_path_str)
    return _read_from_local(file_path_str)


def _read_from_s3(s3_uri: str) -> bytes:
    """
    Read a file from S3 using the centralized S3 client.

    Args:
        s3_uri: S3 URI in format s3://bucket/key

    Returns:
        bytes: The file content as bytes
    """
    parsed = urlparse(s3_uri)
    bucket = parsed.netloc
    key = parsed.path.lstrip("/")

    if not bucket or not key:
        raise InvalidS3UriError(s3_uri=s3_uri)
    s3_client = get_s3_client()
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        return response["Body"].read()
    except Exception as err:
        raise S3ReadError(s3_uri=s3_uri) from err


def _read_from_local(file_path: str) -> bytes:
    """
    Read a file from local file system.

    Args:
        file_path: Local file path

    Returns:
        bytes: The file content as bytes
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")  # noqa: TRY003

    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")  # noqa: TRY003

    return path.read_bytes()
