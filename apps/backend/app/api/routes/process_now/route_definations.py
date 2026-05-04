PROCESS_DEF = """
        Upload a binary document and receive structured extraction, classification, or
        summarisation results **within the same HTTP response** — no polling required.

        ### When to use this endpoint
        - Quick, low-latency one-off documents where you need an immediate answer.
        - Integration tests / prototyping before wiring up the full async workflow.

        ### When **not** to use this endpoint
        - Documents > 10 MB or > 30 pages — use the async `/integrations/` endpoint instead.
        - High-throughput batch processing — prefer the queue-backed workflow.

        ### Pipeline resolution
        Supply **exactly one** of:
        | Field | Description |
        |---|---|
        | `pipeline_id` | ID of a previously saved, active pipeline |
        | `pipeline_config` | Inline JSON with OCR / VLM / LLM provider settings |

        ### Task types & required schema shapes
        | task_type | json_schema must contain |
        |---|---|
        | `extraction` | `{"extractors": [{"name": "...", "type": "..."}]}` |
        | `classification` | `{"classifiers": [{"category": "...", "fields": [...]}]}` |
        | `summarization` | `{}` or `{"fields": ["aspect1", "aspect2"]}` |

        ### Timeout
        Processing is capped at **120 seconds** (server-side).
        If the limit is exceeded the server returns **429** — retry with the async API.
        """


PROCESS_RES = {
    200: {"description": "Document processed successfully."},
    400: {"description": "Validation error — bad request body or invalid schema."},
    404: {"description": "Referenced pipeline_id not found."},
    413: {"description": "File size exceeds 10 MB limit."},
    422: {"description": "Unprocessable entity — Pydantic validation failure."},
    429: {
        "description": "Processing timed out — document too large for sync processing."
    },
    500: {"description": "Internal error during pipeline execution."},
}
