---
sidebar_position: 2
---

# Pipeline Stages

Stages are the building blocks of LeapX pipelines. Each stage performs a specific task in the document processing workflow.

## Available Stages

### OCR Stage

Converts documents (PDFs, images) to text using OCR providers.

```python
from leapx.pipeline.stages.layers import Stage

stages = [Stage.OCR, Stage.PARSER, Stage.LLM_EXTRACTION]
```

**Supported Providers:**
- AWS Textract
- Azure Document Intelligence

**Input:** Document file path or bytes  
**Output:** Raw OCR text with positional information

### Parser Stage

Processes raw OCR output and structures the text.

**Parsing Methods:**
- `LAYOUT_CONSERVED` - Preserves document layout and structure

**Input:** Raw OCR output  
**Output:** Structured text ready for extraction

### LLM Extraction Stage

Uses AI models to extract structured data based on your JSON schema.

**Features:**
- Schema-driven extraction
- Support for complex nested structures
- Automatic retry and error handling

**Input:** Parsed text content  
**Output:** Structured data matching your schema

## Stage Configuration

Each stage has its own configuration class:

### OCRConfig

```python
from leapx.pipeline.stages.configs import OCRConfig
from leapx.common.types.providers import OCRProviderType
from leapx.services.credentials.ocr.aws_config import AwsOcrCredential
from leapx.common.cache.cache_config import CacheConfig

ocr_config = OCRConfig(
    provider=OCRProviderType.AWS_TEXTRACT,
    credential=AwsOcrCredential(),
    cache_config=CacheConfig(enabled=True),
)
```

### ParserConfig

```python
from leapx.pipeline.stages.configs import ParserConfig
from leapx.common.types.providers import ParsingMethod

parser_config = ParserConfig(
    method=ParsingMethod.LAYOUT_CONSERVED,
)
```

### LLMExtractionConfig

```python
from leapx.pipeline.stages.configs import LLMExtractionConfig
from leapx.services.credentials.bedrock_config import BedrockCredential
from leapx.services.extractor.extractor_factory import ExtractorProvider

llm_config = LLMExtractionConfig(
    model="anthropic.claude-3-sonnet-20240229-v1:0",
    credential=BedrockCredential(),
    additional_instructions="Extract the data accurately.",
    temperature=0.0,
    max_tokens=30000,
    cache_config=CacheConfig(enabled=True),
    provider=ExtractorProvider.LITE_LLM,
)
```

## Stage Enum

Use the `Stage` enum for easy stage selection:

```python
from leapx.pipeline.stages.layers import Stage

# All available stages
Stage.OCR              # OCR processing
Stage.PARSER           # Text parsing
Stage.LLM_EXTRACTION   # AI extraction
```

## Custom Stage Order

You can customize which stages to include:

```python
from leapx import linear_pipeline
from leapx.pipeline.stages.layers import Stage

# Full pipeline
full_pipeline = linear_pipeline(
    json_schema=schema,
    additional_instructions=instructions,
    stages=[Stage.OCR, Stage.PARSER, Stage.LLM_EXTRACTION],
)

# Extraction only (for pre-processed text)
extraction_only = linear_pipeline(
    json_schema=schema,
    additional_instructions=instructions,
    stages=[Stage.LLM_EXTRACTION],
)
```

## Stage Dependencies

Stages declare their dependencies using the `.after()` method:

```python
from leapx.pipeline.stages.ocr_stage import OCRStage
from leapx.pipeline.stages.parser_stage import ParserStage

ocr_stage = OCRStage(config=ocr_config)
parser_stage = ParserStage(config=parser_config).after(ocr_stage)
```

## Next Steps

- [Input Types](./input-types.md) - Supported input formats
- [JSON Schema](./json-schema.md) - Defining extraction schemas
