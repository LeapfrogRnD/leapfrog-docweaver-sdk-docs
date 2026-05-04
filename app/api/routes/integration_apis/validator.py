import re
from typing import Annotated

from fastapi import Depends, File, Form, UploadFile
from pypdf import PdfReader

from app.core.integration_apis.schemas import IntegrationRequest
from app.shared.constants.app_constants import S3_URI_REGEX, FileConstants
from app.shared.exceptions.common import BadRequestException

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
}


def get_validated_integration_request(
    s3_file_uri: str = Form(None, description="S3 URI of the file to integrate with"),
    file: UploadFile = File(None, description="file to integrate with"),
    workflow_name: str = Form(..., description="Name of the workflow to execute"),
) -> IntegrationRequest:

    if (not s3_file_uri and not file) or (s3_file_uri and file):
        raise BadRequestException("Either s3_file_uri or file must be provided")

    if s3_file_uri and not re.match(S3_URI_REGEX, s3_file_uri):
        raise BadRequestException("Invalid S3 URI format")

    # Validate file if provided
    if file:
        _validate_file_type(file)
        _validate_file_size(file)
        _validate_pdf_page_count(file)

    return IntegrationRequest(s3_file_uri=s3_file_uri, file=file, workflow_name=workflow_name)


def _validate_file_type(file: UploadFile) -> None:
    """Validate that the uploaded file is a PDF or an image."""
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise BadRequestException(
            f"Invalid file type. Allowed types: PDF and images (JPG, JPEG, PNG). Got: {file.content_type}"
        )


def _validate_file_size(file: UploadFile) -> None:
    """Validate that the file size does not exceed the maximum allowed size."""
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > FileConstants.MAX_FILE_SIZE_BYTES:
        raise BadRequestException(
            f"File size exceeds the maximum allowed size of {FileConstants.MAX_FILE_SIZE_MB}MB. "
            f"Got: {file_size / (1024 * 1024):.2f}MB. Please use a smaller file or provide an S3 URI for larger files."
        )


def _validate_pdf_page_count(file: UploadFile) -> None:
    """Validate that the PDF does not exceed the maximum allowed page count."""
    if file.content_type == "application/pdf":
        try:
            pdf_reader = PdfReader(file.file)
            page_count = len(pdf_reader.pages)
            file.file.seek(0)

            if page_count > FileConstants.MAX_PAGES:
                raise BadRequestException(  # noqa: TRY301
                    f"PDF exceeds the maximum allowed page count of {FileConstants.MAX_PAGES}. "
                    f"Got: {page_count} pages"
                )
        except Exception as e:
            file.file.seek(0)
            raise BadRequestException(f"Failed to read PDF file: {e!s}") from e


ValidatedIntegrationRequestDep = Annotated[
    IntegrationRequest, Depends(get_validated_integration_request)
]
