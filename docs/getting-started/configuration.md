---
sidebar_position: 4
---

# Configuration

LeapX requires configuration for OCR providers and LLM services. This guide covers all configuration options.

## Environment Variables

Create a `.env` file in your project root:

```bash
# AWS Credentials (for Textract OCR and Bedrock LLM)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# Azure Credentials (for Document Intelligence OCR)
AZURE_OCR_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OCR_API_KEY=your_key

# Langfuse (for LLM observability)
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

## OCR Provider Configuration

### AWS Textract (Default)

```python
from leapx import linear_pipeline
from leapx.common.types.providers import OCRProviderType
from leapx.services.credentials.ocr.aws_config import AwsOcrCredential

pipeline = linear_pipeline(
    json_schema=MySchema.model_json_schema(),
    system_prompt="Extract data",
    ocr_provider=OCRProviderType.AWS_TEXTRACT,
    ocr_credential=AwsOcrCredential(
        aws_access_key_id="your_key",
        aws_secret_access_key="your_secret",
        region_name="us-east-1",
    ),
)
```

### Azure Document Intelligence

```python
from leapx.common.types.providers import OCRProviderType

pipeline = linear_pipeline(
    json_schema=MySchema.model_json_schema(),
    system_prompt="Extract data",
    ocr_provider=OCRProviderType.AZURE,
)
```

## LLM Provider Configuration

### AWS Bedrock (Default)

```python
from leapx.services.credentials.bedrock_config import BedrockCredential

pipeline = linear_pipeline(
    json_schema=MySchema.model_json_schema(),
    system_prompt="Extract data",
    llm_provider_credential=BedrockCredential(
        aws_access_key_id="your_key",
        aws_secret_access_key="your_secret",
        region_name="us-east-1",
    ),
    llm_model="anthropic.claude-3-sonnet-20240229-v1:0",
)
```

### Model Selection

```python
pipeline = linear_pipeline(
    json_schema=MySchema.model_json_schema(),
    system_prompt="Extract data",
    llm_model="anthropic.claude-3-sonnet-20240229-v1:0",
    temperature=0.0,
    max_tokens="30000",
)
```

## Cache Configuration

Enable caching to avoid redundant OCR and LLM calls:

```python
from leapx.common.cache.cache_config import CacheConfig

# OCR Cache
ocr_cache = CacheConfig(
    enabled=True,
    cache_type="sqlite",  # or "file"
    cache_dir="./cache/ocr",
)

# LLM Cache
llm_cache = CacheConfig(
    enabled=True,
    cache_type="sqlite",
    cache_dir="./cache/llm",
)

pipeline = linear_pipeline(
    json_schema=MySchema.model_json_schema(),
    system_prompt="Extract data",
    ocr_cache_config=ocr_cache,
    llm_cache_config=llm_cache,
)
```

## Parser Configuration

```python
from leapx.common.types.providers import ParsingMethod

pipeline = linear_pipeline(
    json_schema=MySchema.model_json_schema(),
    system_prompt="Extract data",
    parser=ParsingMethod.LAYOUT_CONSERVED,  # Preserves document layout
)
```

## Context Management Configuration

```python
from leapx.common.types.providers import ParsingMethod

pipeline = linear_pipeline(
    json_schema=MySchema.model_json_schema(),
    system_prompt="Extract data",
    parser=ParsingMethod.LAYOUT_CONSERVED,  
    enable_context=True,   #preserves the context of previous page content , result to the next page
)
```


## Full Configuration Example

```python
from leapx import linear_pipeline
from leapx.common.cache.cache_config import CacheConfig
from leapx.common.types.providers import OCRProviderType, ParsingMethod
from leapx.services.credentials.bedrock_config import BedrockCredential
from leapx.services.credentials.ocr.aws_config import AwsOcrCredential

pipeline = linear_pipeline(
    # Schema & Prompt
    json_schema=MySchema.model_json_schema(),
    system_prompt="Extract the required information accurately.",
    
    # OCR Configuration
    ocr_provider=OCRProviderType.AWS_TEXTRACT,
    ocr_credential=AwsOcrCredential(),
    ocr_cache_config=CacheConfig(enabled=True),
    
    # Parser Configuration
    parser=ParsingMethod.LAYOUT_CONSERVED,
    
    # LLM Configuration
    llm_model="anthropic.claude-3-sonnet-20240229-v1:0",
    llm_provider_credential=BedrockCredential(),
    llm_cache_config=CacheConfig(enabled=True),
    temperature=0.0,
    max_tokens="30000",
    # Context Status
    enable_context=True,
)
```

## Next Steps

- [Pipeline Overview](../concepts/pipeline-overview.md) - Learn about the pipeline architecture
- [OCR Service](../services/ocr.md) - Deep dive into OCR options
- [Caching Guide](../guides/caching.md) - Advanced caching strategies
