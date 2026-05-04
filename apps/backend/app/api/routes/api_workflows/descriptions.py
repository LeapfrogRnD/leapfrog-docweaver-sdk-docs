"""
Descriptions for API Workflows endpoints.

This module mirrors the approach used by integration_apis.router where
large endpoint description strings are moved into a separate module
and imported into the router to keep the router file concise.
"""

CREATE_API_WORKFLOW_DESCRIPTION = """
Create new workflow definition for document processing automation.

### Request Schema
```json
{
  "name": "string",
  "workflow_type": "extraction|classification|summarization",
  "additional_instruction": "string (optional)",
  "json_schema": {},
  "pipeline_config": {}
}
```

### Workflow Types & Required Schemas

**1. Extraction (`extraction`)
Extracts structured data from documents.
Required `json_schema`:
```json
[
  {
    "name": "Invoice id",
    "type": "string",
    "description": "Unique identifier"
  },
  {
    "name": "Total Amount",
    "type": "number",
    "description": "Final price"
  },
  {
    "name": "Vendor Name",
    "type": "string",
    "description": "Company name"
  }
]
```

**2. Classification (`classification`)**
Classifies documents into categories.
Required `json_schema`:
```json
[
  {
    "category": "severity",
    "fields": [
      {
        "name": "High Severity",
        "description": "The issue critically affects the system and requires immediate attention."
      },
      {
        "name": "Medium Severity",
        "description": "The issue affects functionality but does not completely block the system."
      },
      {
        "name": "Low Severity",
        "description": "The issue has minimal impact on the system and can be addressed later."
      }
    ]
  },
  {
    "category": "component",
    "fields": [
      {
        "name": "Database",
        "description": "Issues related to database performance, connectivity, or queries."
      },
      {
        "name": "API",
        "description": "Issues related to backend APIs or service endpoints."
      },
      {
        "name": "Frontend",
        "description": "Issues affecting the user interface or client-side functionality."
      }
    ]
  },
  {
    "category": "request_type",
    "fields": [
      {
        "name": "Feature Request",
        "description": "Customer is requesting a new feature or capability."
      },
      {
        "name": "Account Change",
        "description": "Customer needs modifications to their account settings."
      },
      {
        "name": "Information Request",
        "description": "Customer is asking for product or service information."
      }
    ]
  },
  {
    "category": "priority",
    "fields": [
      {
        "name": "Urgent",
        "description": "The request needs immediate attention."
      },
      {
        "name": "Normal",
        "description": "The request should be handled in the normal workflow."
      },
      {
        "name": "Low Priority",
        "description": "The request can be handled later with minimal urgency."
      }
    ]
  }
]
```

**3. Summarization (`summarization`)
Generates document summaries.
Optional `json_schema`:
```json
{
  "fields": ["aspect1", "aspect2"]
}
```

### Response Schema
```json
{
  "data": {
    "id": "integer",
    "name": "string",
    "workflow_type": "string",
    "pipeline_config": {},
    "additional_instruction": "string",
    "json_schema": {},
    "created_at": "datetime"
  }
}
```

### Authentication
Requires valid API key in `X-API-Key` header.
"""

LIST_API_WORKFLOWS_DESCRIPTION = """
Get paginated list of workflows for authenticated API key.

### Response Schema
```json
{
  "data": [
    {
      "id": "integer",
      "name": "string",
      "workflow_type": "string",
      "created_at": "datetime"
    }
  ],
  "metadata": {
    "total": "integer",
    "page": "integer",
    "limit": "integer",
    "total_pages": "integer"
  }
}
```

### Pagination
- Default page size: 10 workflows
- Maximum page size: 100 workflows
- Results ordered by creation date (newest first)
"""

GET_API_WORKFLOW_DESCRIPTION = """
Get detailed workflow information including complete configuration.

### Response Schema
```json
{
  "data": {
    "id": "integer",
    "name": "string",
    "workflow_type": "string",
    "pipeline_config": {},
    "additional_instruction": "string",
    "json_schema": {},
    "created_at": "datetime"
  }
}
```

Returns complete workflow definition including:
- Basic workflow information (name, type, creation date)
- Pipeline configuration settings
- JSON schema for extraction/classification fields
- Additional processing instructions
"""

UPDATE_API_WORKFLOW_DESCRIPTION = """
Update existing workflow configuration.

### Request Schema
Same as create request - only provided fields are updated:
```json
{
  "name": "string (optional)",
  "workflow_type": "string (optional)",
  "additional_instruction": "string (optional)",
  "json_schema": "object (optional)",
  "pipeline_config": "object (optional)"
}
```

### Update Behavior
- Only provided fields are modified
- Omitted fields retain current values
- Schema validation applies to updated workflow_type
- Maintains workflow ID and creation timestamp

### Schema Validation
Same validation rules as create:
- `extraction`: requires `extractors` array with proper structure
- `classification`: requires `classifiers` array with proper structure
- `summarization`: optional schema
"""

DELETE_API_WORKFLOW_DESCRIPTION = """
Soft delete workflow preserving data for potential recovery.

### Delete Behavior
- Workflow marked as deleted but data preserved
- Becomes inaccessible through normal API operations
- Active integrations using this workflow may be affected
- Can be restored within retention period via support

### Response Schema
```json
{
  "data": "string"
}
```

Returns confirmation message of successful deletion.
"""
