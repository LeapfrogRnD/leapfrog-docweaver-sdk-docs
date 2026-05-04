---
sidebar_position: 4
---

# JSON Schema

LeapFrog DocWeaver uses JSON Schema (via Pydantic models) to define the structure of data you want to extract. This guide covers how to create effective extraction schemas.

## Defining Schemas with Pydantic

The recommended way to define schemas is using Pydantic models:

```python
from pydantic import BaseModel, Field

class InvoiceData(BaseModel):
    invoice_number: str = Field(..., description="The invoice number")
    total_amount: float = Field(..., description="Total amount due")
    due_date: str = Field(None, description="Payment due date")

# Convert to JSON Schema
schema = InvoiceData.model_json_schema()
```

## Field Descriptions

**Always provide descriptions** - they guide the LLM extraction:

```python
class PersonInfo(BaseModel):
    #  Good - clear description
    full_name: str = Field(..., description="The person's full legal name")
    
    #  Bad - no description
    age: int
```

## Required vs Optional Fields

```python
class DocumentData(BaseModel):
    # Required field (no default value)
    title: str = Field(..., description="Document title")
    
    # Optional field (has default None)
    author: str = Field(None, description="Author if available")
    
    # Optional with default value
    page_count: int = Field(default=1, description="Number of pages")
```

## Complex Schemas

### Nested Objects

```python
class Address(BaseModel):
    street: str = Field(..., description="Street address")
    city: str = Field(..., description="City name")
    zip_code: str = Field(..., description="ZIP/Postal code")

class Company(BaseModel):
    name: str = Field(..., description="Company name")
    address: Address = Field(..., description="Company address")
```

### Lists/Arrays

```python
class LineItem(BaseModel):
    description: str = Field(..., description="Item description")
    quantity: int = Field(..., description="Quantity ordered")
    unit_price: float = Field(..., description="Price per unit")

class Invoice(BaseModel):
    invoice_number: str = Field(..., description="Invoice number")
    line_items: list[LineItem] = Field(..., description="List of items")
```

### Enums and Literals

```python
from typing import Literal
from enum import Enum

class DocumentType(str, Enum):
    INVOICE = "invoice"
    RECEIPT = "receipt"
    CONTRACT = "contract"

class Document(BaseModel):
    doc_type: DocumentType = Field(..., description="Type of document")
    # Or using Literal
    status: Literal["draft", "final", "archived"] = Field(..., description="Document status")
```

## Using Raw JSON Schema

You can also use raw JSON Schema dictionaries:

```python
schema = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "Document title"
        },
        "pages": {
            "type": "integer",
            "description": "Number of pages"
        }
    },
    "required": ["title"]
}

pipeline = linear_pipeline(
    json_schema=schema,
    additional_instructions="Extract document info",
)
```

## Type Mapping

The schema generator handles various JSON Schema types:

| JSON Schema Type | Python Type |
|-----------------|-------------|
| `string` | `str` |
| `integer` | `int` |
| `number` | `float` |
| `boolean` | `bool` |
| `array` | `list[T]` |
| `object` | Nested model or `dict` |

### Format Handling

Special string formats are converted to appropriate Python types:

| Format | Python Type |
|--------|-------------|
| `date-time` | `datetime` |
| `date` | `date` |
| `time` | `time` |
| `email` | `str` |
| `uri` | `AnyUrl` |
| `uuid` | `UUID` |

## Best Practices

### 1. Be Specific with Descriptions

```python
# ✅ Good
amount: float = Field(..., description="Total invoice amount in USD, including tax")

# ❌ Vague
amount: float = Field(..., description="Amount")
```

### 2. Use Appropriate Types

```python
# ✅ Good - specific types
invoice_date: date = Field(..., description="Invoice date")
total: Decimal = Field(..., description="Total amount")

# ❌ Bad - overly generic
invoice_date: str = Field(..., description="Invoice date")
total: str = Field(..., description="Total amount")
```

### 3. Handle Missing Data

```python
class RobustSchema(BaseModel):
    # Make fields optional if they might not exist
    optional_field: str = Field(None, description="May not be present")
    
    # Provide defaults where appropriate
    status: str = Field(default="unknown", description="Document status")
```

## Next Steps

- [Quick Start](../getting-started/quickstart.md) - See schemas in action
- [Extractor Service](../services/extractor.md) - How extraction works
