"""
Route description strings for integration API endpoints.
This keeps the router module concise and moves large formatted descriptions into a separate file.
"""

CREATE_INTEGRATION_DESCRIPTION = """
Create asynchronous integration job for document processing through workflows.

Accepts either a file upload or S3 URI along with workflow configuration.
Returns `integration_job_id` for polling status and results.

Request Format
Content-Type: multipart/form-data

Required Fields
- workflow_name (string): Name of the workflow to execute

File Input (exactly one required)
- file (binary): Document file to process
- s3_file_uri (string): S3 URI of the file (alternative to file upload)

File Requirements
Supported formats:
- PDF documents
- Images: JPEG, JPG, PNG

Size limits:
- Maximum file size: 10MB for direct upload
- Maximum PDF pages: 30 pages
- For larger files, use s3_file_uri instead

Response Schema
{
"data": {
    "integration_job_id": "string",
    "status": "string"
}
}

Authentication
Requires valid API key in X-API-Key header.
"""

POLL_INTEGRATION_DESCRIPTION = """
Get integration job status, progress, and results.

Status Values
- pending — Job queued, waiting to start
- processing — Job running, document being processed
- completed — Job finished successfully, results available
- failed — Job failed with errors

Response Schema
{
  "data": {
    "integration_job_id": "string",
    "integration_type": "string",
    "status": "string",
    "result": [{"key": "value"}],
    "failed_remarks": "string"
  }
}

Response Fields
- integration_job_id: The job identifier
- integration_type: Type of integration performed
- status: Current job status
- result: Structured extraction results (when completed)
- failed_remarks: Error details (when failed)

Polling Guidelines
- Poll every 5-10 seconds for active jobs
- Results available immediately when status is "completed"
- Jobs expire after 7 days
"""
