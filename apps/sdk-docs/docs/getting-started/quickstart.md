---
sidebar_position: 3
---

# Quick Start

This guide will help you create your first document extraction pipeline in minutes.

## Prerequisites

Before you begin, make sure you have:

1. ✅ [Installed LeapX](./installation.md)
2. ✅ [Configured credentials](./configuration.md) for OCR and LLM providers

## Basic Example

Here's a complete example that extracts document information from a PDF:

```python
import asyncio
from pydantic import BaseModel, Field
from leapx import linear_pipeline, InputType

# 1. Define your extraction schema
class DocumentInfo(BaseModel):
    title: str = Field(..., description="The title of the document")
    author: str = Field(None, description="The author if available")

# 2. Create the pipeline
async def extract_document():
    pipeline = linear_pipeline(
        json_schema=DocumentInfo.model_json_schema(),
        additional_instructions="Extract the document information from the OCR text.",
    )
    
    # 3. Run extraction
    result = await pipeline.async_run("path/to/your/document.pdf")
    
    return result

# 4. Execute
if __name__ == "__main__":
    result = asyncio.run(extract_document())
    print(result)
```

## Step-by-Step Breakdown

### Step 1: Define Your Schema

Use Pydantic models to define what data you want to extract. Field descriptions are crucial - they guide the LLM extraction:

```python
from pydantic import BaseModel, Field

class InvoiceData(BaseModel):
    invoice_number: str = Field(..., description="The invoice number")
    total_amount: float = Field(..., description="Total amount due")
    due_date: str = Field(None, description="Payment due date in YYYY-MM-DD format")
    vendor_name: str = Field(..., description="Name of the vendor/supplier")
```

:::tip Field Descriptions Matter
Always provide clear, specific descriptions for each field. The LLM uses these descriptions to understand what to extract.
:::

### Step 2: Create a Pipeline

The `linear_pipeline` factory creates a standard OCR → Parser → LLM extraction pipeline:

```python
from leapx import linear_pipeline
from leapx.pipeline.stages.layers import Stage

pipeline = linear_pipeline(
    json_schema=InvoiceData.model_json_schema(),
    additional_instructions="Extract invoice details from the document.",
    stages=[Stage.OCR, Stage.PARSER, Stage.LLM_EXTRACTION],  # Optional: explicit stages
    max_tokens="30000",
)
```

### Step 3: Run the Pipeline

```python
# From a file path
result = await pipeline.async_run("invoice.pdf")

# From text directly (skips OCR)
result = await pipeline.async_run(
    "Invoice #12345\nTotal: $500.00",
    input_type=InputType.TEXT
)
```

## Working with Text Input

If you already have text (not a document), you can skip OCR for better performance:

```python
from leapx import linear_pipeline, InputType
from leapx.pipeline.stages.layers import Stage

pipeline = linear_pipeline(
    json_schema=MySchema.model_json_schema(),
    additional_instructions="Extract the required fields.",
    stages=[Stage.LLM_EXTRACTION],  # Only extraction, no OCR/Parser
)

result = await pipeline.async_run(
    "Your text content here...",
    input_type=InputType.TEXT
)
```

## Complete Invoice Extraction Example

Here's a full working example for invoice extraction:

```python
import asyncio
import json
from pathlib import Path
from pydantic import BaseModel, Field
from leapx import linear_pipeline
from leapx.common.cache.cache_config import CacheConfig

# Define the extraction schema
class LineItem(BaseModel):
    description: str = Field(..., description="Item description")
    quantity: int = Field(..., description="Quantity ordered")
    unit_price: float = Field(..., description="Price per unit")
    total: float = Field(..., description="Line item total")

class Invoice(BaseModel):
    invoice_number: str = Field(..., description="Invoice number/ID")
    invoice_date: str = Field(..., description="Invoice date in YYYY-MM-DD format")
    vendor_name: str = Field(..., description="Vendor/supplier company name")
    vendor_address: str = Field(None, description="Vendor address")
    subtotal: float = Field(..., description="Subtotal before tax")
    tax: float = Field(None, description="Tax amount")
    total: float = Field(..., description="Total amount due")
    line_items: list[LineItem] = Field(default=[], description="List of line items")

async def extract_invoice(file_path: str) -> dict:
    # Create pipeline with caching enabled
    pipeline = linear_pipeline(
        json_schema=Invoice.model_json_schema(),
        additional_instructions="""
        Extract all invoice information from the document.
        Be precise with numbers and dates.
        Format dates as YYYY-MM-DD.
        If a field is not found, use null.
        """,
        max_tokens="30000",
        temperature=0.0,
        ocr_cache_config=CacheConfig(enabled=True),
        llm_cache_config=CacheConfig(enabled=True),
    )
    
    # Run extraction
    result = await pipeline.async_run(file_path)
    
    return result

async def main():
    # Extract from a PDF
    result = await extract_invoice("invoice.pdf")
    
    # Print result
    print(json.dumps(result, indent=2))
    
    # Save to file
    Path("extraction_result.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

if __name__ == "__main__":
    asyncio.run(main())
```