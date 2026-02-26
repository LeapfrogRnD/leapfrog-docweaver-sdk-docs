---
sidebar_position: 1
---

# Introduction

## What is LeapX?

**LeapX Pipeline SDK** is a lightweight, powerful Python SDK designed to extract structured data from documents such as PDFs, images, and text files. It leverages AI-powered parsing and OCR capabilities to identify key information with high accuracy and speed.

## Key Features

- **Automated Text & Data Extraction** - Extract structured data from unstructured documents automatically
- **Multi-Format Support** - Process PDFs, images with format png, jpeg seamlessly
- **Fast & Scalable** - Async-first architecture optimized for performance
- **Pipeline Architecture** - Modular stages (OCR → Parser → LLM Extraction) or as defined by you
- **Flexible Configuration** - Support for multiple OCR, LLM providers, and VLM models
- **Built-in Caching** - SQLite and file-based caching for improved performance
- **Observability** - Integrated logging, tracing, and Opentelemetry support (langfuse, langsmith, etc.)
- **Schema-Driven** - Use Pydantic models or JSON Schema to define extraction targets

## How It Works

LeapX uses a pipeline-based architecture with five main stages:

```
┌─────────┐    ┌─────────┐    ┌────────────────┐
│   OCR   │ -> │ Parser  │ -> │ LLM Extraction │
└─────────┘    └─────────┘    └────────────────┘

┌─────────┐    ┌──────────────────┐
│ VLM     │ -> │ LLM Summarization│
└─────────┘    └──────────────────┘
```

1. **OCR Stage**: Converts document images/PDFs to text using AWS Textract or Azure Document Intelligence
2. **Parser Stage**: Processes and structures the raw OCR output while preserving layout
3. **VLM Extraction Stage**: Uses AI models to extract and parse the data
4. **LLM Extraction Stage**: Uses AI models to extract structured data based on your JSON schema
5. **LLM Summarization Stage**: Uses AI models to summarize the extracted data

## Quick Example

```python
import asyncio
from pydantic import BaseModel, Field
from leapx import linear_pipeline

class InvoiceData(BaseModel):
    invoice_number: str = Field(..., description="The invoice number")
    total_amount: float = Field(..., description="Total amount due")

async def main():
    pipeline = linear_pipeline(
        json_schema=InvoiceData.model_json_schema(),
        system_prompt="Extract invoice information from the document.",
    )
    result = await pipeline.async_run("invoice.pdf")
    print(result)

asyncio.run(main())
```

## Use Cases

- **Document Processing**: Invoice extraction, form processing, contract analysis
- **Data Entry Automation**: Automate manual data entry from scanned documents
- **Content Extraction**: Extract specific fields from large document sets
- **Document Classification**: Categorize and tag documents automatically
- **Healthcare**: Medical record extraction, insurance claim processing
- **Finance**: Receipt processing, financial statement analysis
- **Summarization**: Summary of the document

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     LeapX Pipeline SDK                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────┐  ┌──────────────────────┐│
│  │ linear_pipeline │  │ dag_pipeline │  │  Custom Pipelines    ││
│  └─────────────────┘  └──────────────┘  └──────────────────────┘│
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────┐    ┌──────────┐    ┌────────────────────┐          │
│  │   OCR   │ -> │  Parser  │ -> │   LLM Extraction   │          │
│  │  Stage  │    │   Stage  │    │       Stage        │          │ 
│  └─────────┘    └──────────┘    └────────────────────┘          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Services Layer                             │    │
│  │  OCR | Layout Parser | Extractor | Schema Generator     │    │
│  └─────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Infrastructure                             │    │
│  │  Caching | Logging | Tracing | Error Handling           │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Next Steps

- [Installation Guide](./installation.md) - Get LeapX installed
- [Quick Start](./quickstart.md) - Build your first extraction pipeline
- [Configuration](./configuration.md) - Set up credentials and environment
