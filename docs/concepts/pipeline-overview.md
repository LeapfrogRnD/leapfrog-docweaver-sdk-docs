---
sidebar_position: 1
---

# Pipeline Overview

LeapX uses a pipeline-based architecture to process documents through multiple stages. This modular design allows for flexibility, caching, and easy customization.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        LeapX Pipeline                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────┐    ┌──────────┐    ┌────────────────────┐         │
│  │  INPUT  │ -> │   OCR    │ -> │      PARSER        │         │
│  │ (PDF/   │    │  Stage   │    │      Stage         │         │
│  │  Image) │    └──────────┘    └────────────────────┘         │
│  └─────────┘          │                   │                     │
│                       v                   v                     │
│               ┌──────────────────────────────────┐              │
│               │       LLM EXTRACTION Stage       │              │
│               │   (Structured Data Extraction)   │              │
│               └──────────────────────────────────┘              │
│                              │                                  │
│                              v                                  │
│                      ┌──────────────┐                           │
│                      │    OUTPUT    │                           │
│                      │  (JSON/Dict) │                           │
│                      └──────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

## Pipeline Types

### Linear Pipeline

Stages execute in sequence, each depending on the previous:

```python
from leapx import linear_pipeline

pipeline = linear_pipeline(
    json_schema=MySchema.model_json_schema(),
    additional_instructions="Extract data",
)
# Automatically creates: OCR -> Parser -> LLM Extraction
```

### DAG Pipeline

For complex workflows with custom dependencies:

```python
from leapx.pipeline.runner import dag_pipeline

pipeline = dag_pipeline(
    json_schema=MySchema.model_json_schema(),
    additional_instructions="Extract data",
    stages=[stage1, stage2, stage3],  # Custom stage configuration
)
```

## Pipeline Components

### 1. Pipeline Factory (`runner.py`)

Factory functions that create pre-configured pipelines:

- `linear_pipeline()` - Creates a standard sequential pipeline
- `dag_pipeline()` - Creates a pipeline with custom stage dependencies

### 2. Pipeline Core (`core/pipeline.py`)

The main `LeapXPipeline` class that:

- Manages stage execution order
- Handles async execution
- Coordinates data flow between stages

### 3. Stages (`stages/`)

Individual processing units:

| Stage | Purpose |
|-------|---------|
| `OCRStage` | Document to text conversion |
| `ParserStage` | Text structuring and layout parsing |
| `LLMExtractionStage` | AI-powered data extraction |

### 4. Error Handler (`core/error_handler.py`)

Centralized error handling for pipeline operations.

## Execution Flow

1. **Input**: Document path or text content
2. **OCR Stage**: Converts document to raw text
3. **Parser Stage**: Structures the text, preserving layout
4. **LLM Extraction**: Extracts structured data using your schema
5. **Output**: Returns extracted data as dictionary

## Stage Dependencies

Stages can declare dependencies on other stages:

```python
from leapx.pipeline.stages.base import BaseStage

# Parser depends on OCR
parser_stage = ParserStage(config=parser_cfg).after(ocr_stage)

# LLM depends on Parser
llm_stage = LLMStage(config=llm_cfg).after(parser_stage)
```

## Async Execution

LeapX is built for async execution:

```python
import asyncio

async def main():
    pipeline = linear_pipeline(...)
    result = await pipeline.async_run("document.pdf")
    return result

asyncio.run(main())
```

## Next Steps

- [Stages](./stages.md) - Detailed stage documentation
- [Linear Pipeline Guide](../guides/linear-pipeline.md) - Using linear pipelines
- [DAG Pipeline Guide](../guides/dag-pipeline.md) - Custom pipeline workflows
