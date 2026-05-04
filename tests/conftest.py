"""Shared test fixtures and configuration."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import UploadFile

from app.db.models import (
    ApiKey,
    ApiKeySecrets,
    ApiWorkFlow,
    ApiWorkFlowJob,
    TaskApiWorkFlowJobRun,
)
from app.shared.constants.app_constants import TaskStatus, TaskTypes


@pytest.fixture
def pipeline_config():
    """Default pipeline configuration for tests."""
    return {
        "ocr_provider": "aws_textract",
        "llm_model_provider": "openai",
        "llm_model": "gpt-4.1-nano",
    }


@pytest.fixture
def mock_api_key_secret():
    """Mock API key secret."""
    api_key = MagicMock(spec=ApiKey)
    api_key.id = 1
    api_key.deleted_at = None

    secret = MagicMock(spec=ApiKeySecrets)
    secret.id = 1
    secret.api_key_id = 1
    secret.api_key = api_key
    return secret


@pytest.fixture
def mock_api_workflow():
    """Mock API workflow."""
    workflow = MagicMock(spec=ApiWorkFlow)
    workflow.id = 1
    workflow.name = "test_workflow"
    workflow.workflow_type = TaskTypes.EXTRACTION
    workflow.api_key_id = 1
    workflow.api_key = None
    workflow.pipeline_config = {}
    workflow.json_schema = [
        {
            "name": "test",
            "type": "string",
            "title": "Test",
            "description": "Test field",
        }
    ]
    workflow.formatted_json_schema = {}
    workflow.additional_instruction = None
    workflow.created_at = datetime.now()
    workflow.deleted_at = None
    return workflow


@pytest.fixture
def mock_api_workflow_job():
    """Mock API workflow job."""
    job = MagicMock(spec=ApiWorkFlowJob)
    job.id = 1
    job.api_job_id = "test123"
    job.api_workflow_id = 1
    job.api_secret_id = 1
    job.file_metadata = {"file_path": "s3://bucket/test.pdf"}
    job.created_at = datetime.now()
    return job


@pytest.fixture
def mock_task_workflow_job_run():
    """Mock task workflow job run."""
    run = MagicMock(spec=TaskApiWorkFlowJobRun)
    run.id = 1
    run.status = TaskStatus.QUEUED
    run.job_rank = 1
    run.result = None
    run.failed_remarks = None
    run.created_at = datetime.now()
    return run


@pytest.fixture
def mock_upload_file():
    """Mock FastAPI UploadFile."""
    file_content = b"test file content"
    file = MagicMock(spec=UploadFile)
    file.filename = "test.pdf"
    file.content_type = "application/pdf"
    file.read = AsyncMock(return_value=file_content)
    return file


@pytest.fixture
def extraction_schema():
    """Valid extraction schema."""
    return [
        {
            "name": "invoice_number",
            "type": "string",
            "title": "Invoice Number",
            "description": "The invoice number from the document",
        },
        {
            "name": "total_amount",
            "type": "number",
            "title": "Total Amount",
            "description": "The total amount on the invoice",
        },
    ]


@pytest.fixture
def classification_schema():
    """Valid classification schema."""
    return [
        {
            "category": "document_type",
            "fields": [
                {
                    "name": "invoice",
                    "title": "Invoice",
                    "description": "An invoice document",
                    "example": "Invoice for services rendered",
                },
                {
                    "name": "receipt",
                    "title": "Receipt",
                    "description": "A receipt document",
                    "example": "Receipt for purchase",
                },
            ],
        }
    ]


@pytest.fixture
def summarization_schema():
    """Valid summarization schema (empty)."""
    return {}
