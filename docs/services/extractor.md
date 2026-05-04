---
sidebar_position: 2
---

# Extractor Service

The Extractor service uses LLMs to extract structured data from text based on your JSON schema.

## Overview

The extractor takes parsed text and your schema, then uses an LLM to extract matching data:

```
Parsed Text + JSON Schema + Additional Instructions(Optional) → Structured Data
```

## Providers

### LiteLLM (Default)

LiteLLM provides a unified interface to multiple LLM providers:

```python
from leapx.services.extractor.extractor_factory import ExtractorProvider

pipeline = linear_pipeline(
    json_schema=schema,
    additional_instructions=instructions,
    extractor_provider=ExtractorProvider.LITE_LLM,
)
```

## Configuration

### Model Selection

```python
pipeline = linear_pipeline(
    json_schema=schema,
    additional_instructions=instructions,
    llm_model="anthropic.claude-3-sonnet-20240229-v1:0",
    temperature=0.0,
    max_tokens="30000",
)
```

### Credentials

```python
from leapx.services.credentials.bedrock_config import BedrockCredential

pipeline = linear_pipeline(
    json_schema=schema,
    additional_instructions=instructions,
    llm_provider_credential=BedrockCredential(
        aws_access_key_id="YOUR_KEY",
        aws_secret_access_key="YOUR_SECRET",
        region_name="us-east-1",
    ),
)
```

## Supported Models

The extractor supports any model available through LiteLLM:

| Provider | Example Models |
|----------|---------------|
| AWS Bedrock | `anthropic.claude-3-sonnet-*`, `anthropic.claude-3-haiku-*` |
| OpenAI | `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo` |
| Anthropic | `claude-3-opus`, `claude-3-sonnet` |

## Additional Instrcutions

The instructions guides extraction behavior:

```python
# Good instructions
instructions = """
Extract the invoice information from the OCR text.
Be precise with numbers and dates.
If a field is not found, use null.
"""

# Specific instructions improve accuracy
instructions = """
Extract the following from this medical document:
- Patient name (full legal name)
- Date of birth (YYYY-MM-DD format)
- Diagnosis codes (ICD-10 format)
If information is unclear or missing, use null.
"""
```

## Caching Extractions

Cache LLM results to avoid redundant API calls:

```python
from leapx.common.cache.cache_config import CacheConfig

pipeline = linear_pipeline(
    json_schema=schema,
    additional_instructions=instructions,
    llm_cache_config=CacheConfig(
        enabled=True,
        cache_type="sqlite",
    ),
)
```

## Extractor Architecture

```
┌─────────────────────────────────────────────────┐
│               Extractor Service                 │
├─────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌──────────────────┐   │
│  │ Extractor       │    │ Cached Extractor │   │
│  │ Factory         │ -> │ Service          │   │
│  └─────────────────┘    └────────┬─────────┘   │
│                                  │              │
│                         ┌────────▼─────────┐   │
│                         │ Base Extractor   │   │
│                         │ (LiteLLM)        │   │
│                         └──────────────────┘   │
└─────────────────────────────────────────────────┘
```

## Best Practices

### 1. Use Specific Instructions

```python
# ✅ Good - specific instructions
instructions = "Extract invoice number, date, and total amount. Format dates as YYYY-MM-DD."

# ❌ Bad - vague
instructions = "Extract data."
```

### 2. Set Temperature to 0 for Consistency

```python
pipeline = linear_pipeline(
    json_schema=schema,
    additional_instructions=instructions,
    temperature=0.0,  # Deterministic output
)
```

### 3. Provide Adequate Token Limit

```python
pipeline = linear_pipeline(
    json_schema=schema,
    additional_instructions=instructions,
    max_tokens="30000",  # Enough for complex documents
)
```

## Next Steps

- [JSON Schema](../concepts/json-schema.md) - Define extraction schemas
- [Caching](../guides/caching.md) - Cache strategies
- [Schema Generator](./schema-generator.md) - Dynamic model generation
