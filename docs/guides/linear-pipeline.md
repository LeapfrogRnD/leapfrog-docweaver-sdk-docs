---
sidebar_position: 1
---

# Linear Pipeline Guide

The linear pipeline is the most common way to use LeapX. It creates a sequential processing workflow where each stage depends on the previous one.

## Basic Usage

```python
from leapx import linear_pipeline
from pydantic import BaseModel, Field

class MySchema(BaseModel):
    title: str = Field(..., description="Document title")

pipeline = linear_pipeline(
    json_schema=MySchema.model_json_schema(),
    additional_instructions="Extract the document title.",
)

result = await pipeline.async_run("document.pdf")
```

## Default Stages

By default, `linear_pipeline` creates three stages:

```
OCR → Parser → LLM Extraction
```

## Customizing Stages

### Specify Explicit Stages

```python
from leapx.pipeline.stages.layers import Stage

pipeline = linear_pipeline(
    json_schema=schema,
    additional_instructions=instructions,
    stages=[Stage.OCR, Stage.PARSER, Stage.LLM_EXTRACTION],
)
```

### Extraction Only

Skip OCR and Parser for text input:

```python
from leapx import InputType

pipeline = linear_pipeline(
    json_schema=schema,
    additional_instructions=instructions,
    stages=[Stage.LLM_EXTRACTION],
)

result = await pipeline.async_run("Your text here", input_type=InputType.TEXT)
```

## Configuration Options

### LLM Configuration

```python
pipeline = linear_pipeline(
    json_schema=schema,
    additional_instructions=instructions,
    llm_model="anthropic.claude-3-sonnet-20240229-v1:0",
    temperature=0.0,
    max_tokens="30000",
)
```

### OCR Configuration

```python
from leapx.common.types.providers import OCRProviderType

pipeline = linear_pipeline(
    json_schema=schema,
    additional_instructions=instructions,
    ocr_provider=OCRProviderType.AWS_TEXTRACT,
)
```

### Parser Configuration

```python
from leapx.common.types.providers import ParsingMethod

pipeline = linear_pipeline(
    json_schema=schema,
    additional_instructions=instructions,
    parser=ParsingMethod.LAYOUT_CONSERVED,
)
```

## Complete Example

```python
import asyncio
import json
from pathlib import Path
from pydantic import BaseModel, Field
from leapx import linear_pipeline
from leapx.pipeline.stages.layers import Stage
from leapx.common.cache.cache_config import CacheConfig

class InvoiceData(BaseModel):
    invoice_number: str = Field(..., description="Invoice number")
    vendor: str = Field(..., description="Vendor name")
    total: float = Field(..., description="Total amount")
    items: list[str] = Field(default=[], description="List of items")

async def extract_invoice(file_path: str):
    pipeline = linear_pipeline(
        json_schema=InvoiceData.model_json_schema(),
        additional_instructions="Extract invoice information accurately.",
        stages=[Stage.OCR, Stage.PARSER, Stage.LLM_EXTRACTION],
        max_tokens="30000",
        temperature=0.0,
        ocr_cache_config=CacheConfig(enabled=True),
        llm_cache_config=CacheConfig(enabled=True),
    )
    
    result = await pipeline.async_run(file_path)
    
    # Save result
    Path("result.json").write_text(
        json.dumps(result, indent=2),
        encoding="utf-8"
    )
    
    return result

if __name__ == "__main__":
    asyncio.run(extract_invoice("invoice.pdf"))
```

## Next Steps

- [DAG Pipeline](./dag-pipeline.md) - Complex pipeline workflows
- [Caching](./caching.md) - Improve performance with caching
- [Error Handling](./error-handling.md) - Handle errors gracefully
