---
sidebar_position: 2
---

# DAG Pipeline Guide

DAG (Directed Acyclic Graph) pipelines allow you to create complex workflows with custom stage dependencies. Use this when you need more control than a linear pipeline provides.

## When to Use DAG Pipelines

- Multiple extraction passes on the same document
- Parallel processing of different document sections
- Custom stage combinations
- Complex dependency graphs

## Basic Usage

```python
from leapx.pipeline.runner import dag_pipeline
from leapx.pipeline.stages.ocr_stage import OCRStage
from leapx.pipeline.stages.parser_stage import ParserStage

# Create stages with dependencies
ocr_stage = OCRStage(config=ocr_config)
parser_stage = ParserStage(config=parser_config).after(ocr_stage)
llm_stage = LLMStage(config=llm_config).after(parser_stage)

pipeline = dag_pipeline(
    json_schema=MySchema.model_json_schema(),
    additional_instructions="Extract data",
    stages=[ocr_stage, parser_stage, llm_stage],
)

result = await pipeline.async_run("document.pdf")
```

## Defining Dependencies

Use the `.after()` method to declare stage dependencies:

```python
# Single dependency
parser_stage = ParserStage(config=cfg).after(ocr_stage)

# Multiple dependencies (stage waits for all)
merge_stage = MergeStage(config=cfg).after(ocr_stage, parser_stage)
```

## Complex Dependency Example

```python
from leapx.pipeline.runner import dag_pipeline

# Create a diamond dependency pattern
#
#       ┌─────────┐
#       │   OCR   │
#       └────┬────┘
#            │
#     ┌──────┴──────┐
#     ▼             ▼
# ┌────────┐   ┌────────┐
# │ Parser │   │ Layout │
# └───┬────┘   └───┬────┘
#     │            │
#     └──────┬─────┘
#            ▼
#     ┌────────────┐
#     │ Extraction │
#     └────────────┘

ocr = OCRStage(config=ocr_cfg)
parser = ParserStage(config=parser_cfg).after(ocr)
layout = LayoutStage(config=layout_cfg).after(ocr)
extraction = LLMStage(config=llm_cfg).after(parser, layout)

pipeline = dag_pipeline(
    json_schema=schema,
    additional_instructions=instructions,
    stages=[ocr, parser, layout, extraction],
)
```

## Stage Configuration

Each stage needs its own configuration:

```python
from leapx.pipeline.stages.configs import (
    OCRConfig,
    ParserConfig,
    LLMExtractionConfig,
)
from leapx.common.types.providers import OCRProviderType, ParsingMethod
from leapx.services.credentials.bedrock_config import BedrockCredential

ocr_cfg = OCRConfig(
    provider=OCRProviderType.AWS_TEXTRACT,
    credential=AwsOcrCredential(),
)

parser_cfg = ParserConfig(
    method=ParsingMethod.LAYOUT_CONSERVED,
)

llm_cfg = LLMExtractionConfig(
    model="anthropic.claude-3-sonnet-20240229-v1:0",
    credential=BedrockCredential(),
    additional_instructions="Extract data accurately.",
    temperature=0.0,
    max_tokens=30000,
)
```

## Error Handling

DAG pipelines use the same error handling as linear pipelines:

```python
from leapx.pipeline.core.error_handler import PipelineErrorHandler

try:
    result = await pipeline.async_run("document.pdf")
except Exception as e:
    PipelineErrorHandler.handle_execution_error(e)
```

## Best Practices

1. **Keep dependencies minimal** - Only add dependencies that are truly required
2. **Validate stage order** - Ensure no circular dependencies
3. **Use caching** - Cache expensive stages like OCR
4. **Test incrementally** - Build and test one stage at a time

## Next Steps

- [Caching](./caching.md) - Cache strategies
- [Error Handling](./error-handling.md) - Handle pipeline errors
- [Pipeline Overview](../concepts/pipeline-overview.md) - Architecture details
