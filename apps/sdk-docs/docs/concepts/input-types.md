---
sidebar_position: 3
---

# Input Types

LeapFrog DocWeaver supports multiple input types for document processing. This guide covers all supported formats and how to use them.

## Supported Input Types

| Type | Description | Use Case |
|------|-------------|----------|
| `FILE` | Path to a document file | PDFs, images on disk |
| `TEXT` | Raw text string | Pre-extracted text, direct input |

## Using Input Types

Import the `InputType` enum:

```python
from leapx import InputType
```

### File Input (Default)

Process documents from the filesystem:

```python
from leapx import linear_pipeline

pipeline = linear_pipeline(
    json_schema=MySchema.model_json_schema(),
    additional_instructions="Extract data",
)

# File path - uses full pipeline (OCR -> Parser -> Extraction)
result = await pipeline.async_run("path/to/document.pdf")
```

### Text Input

Process raw text directly (skips OCR stage):

```python
from leapx import linear_pipeline, InputType
from leapx.pipeline.stages.layers import Stage

# For text input, typically use only extraction stage
pipeline = linear_pipeline(
    json_schema=MySchema.model_json_schema(),
    additional_instructions="Extract data",
    stages=[Stage.LLM_EXTRACTION],
)

text_content = """
Invoice Number: INV-2024-001
Total Amount: $1,500.00
Due Date: January 15, 2025
"""

result = await pipeline.async_run(text_content, input_type=InputType.TEXT)
```

## Supported File Formats

### PDF Documents

```python
result = await pipeline.async_run("document.pdf")
```

- Single and multi-page PDFs
- Scanned documents (processed via OCR)
- Native text PDFs

### Images

```python
result = await pipeline.async_run("document.png")
result = await pipeline.async_run("document.jpg")
```

Supported image formats:
- PNG
- JPEG/JPG
- TIFF
- BMP

## Best Practices

### Choosing the Right Input Type

| Scenario | Recommended Approach |
|----------|---------------------|
| Processing PDF/Image files | Use `FILE` (default) with full pipeline |
| Already have extracted text | Use `TEXT` with extraction-only pipeline |
| Real-time text processing | Use `TEXT` with extraction-only pipeline |

### Optimizing for Text Input

When using text input, skip unnecessary stages:

```python
from leapx.pipeline.stages.layers import Stage

# ❌ Inefficient - includes unnecessary OCR/Parser
pipeline = linear_pipeline(
    json_schema=schema,
    additional_instructions=instructions,
    stages=[Stage.OCR, Stage.PARSER, Stage.LLM_EXTRACTION],
)

# ✅ Efficient - extraction only
pipeline = linear_pipeline(
    json_schema=schema,
    additional_instructions=instructions,
    stages=[Stage.LLM_EXTRACTION],
)

result = await pipeline.async_run(text, input_type=InputType.TEXT)
```

## Next Steps

- [JSON Schema](./json-schema.md) - Define your extraction schema
- [Quick Start](../getting-started/quickstart.md) - Complete examples
