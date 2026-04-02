---
sidebar_position: 5
---

# Performance Optimization

This guide covers techniques to optimize LeapX pipeline performance.

## Caching Strategies

### Enable All Caches

The most impactful optimization is enabling caching:

```python
from leapx.common.cache.cache_config import CacheConfig

pipeline = linear_pipeline(
    json_schema=schema,
    additional_instructions=instructions,
    ocr_cache_config=CacheConfig(enabled=True),
    llm_cache_config=CacheConfig(enabled=True),
)
```

### Use SQLite for Production

SQLite caches are more efficient for production workloads:

```python
cache = CacheConfig(
    enabled=True,
    cache_type="sqlite",
    cache_dir="/var/cache/leapx",
)
```

## Model Selection

### Choose the Right Model

| Model | Speed | Cost | Accuracy |
|-------|-------|------|----------|
| Claude 3 Haiku | Fast | Low | Good |
| Claude 3 Sonnet | Medium | Medium | Excellent |
| Claude 3 Opus | Slow | High | Best |

```python
# For high-volume, simpler extractions
pipeline = linear_pipeline(
    json_schema=schema,
    additional_instructions=instructions,
    llm_model="anthropic.claude-3-haiku-20240307-v1:0",
)

# For complex extractions requiring high accuracy
pipeline = linear_pipeline(
    json_schema=schema,
    additional_instructions=instructions,
    llm_model="anthropic.claude-3-sonnet-20240229-v1:0",
)
```

## Token Optimization

### Optimize instructions

Keep instructions concise but specific:

```python
# ✅ Good - concise and specific
instructions = "Extract invoice number, date, total. Format dates as YYYY-MM-DD."

# ❌ Bad - verbose
instructions = """
You are a helpful assistant that extracts information from documents.
Please carefully read the provided text and extract the following fields:
- The invoice number, which is usually at the top of the document
- The date of the invoice
- The total amount
...
"""
```

### Set Appropriate Token Limits

```python
# Match token limit to expected output size
pipeline = linear_pipeline(
    json_schema=simple_schema,
    additional_instructions=instructions,
    max_tokens="1000",  # Small schema
)

pipeline = linear_pipeline(
    json_schema=complex_schema,
    additional_instructions=instructions,
    max_tokens="30000",  # Large/nested schema
)
```

## Async Processing

### Process Multiple Documents

```python
import asyncio

async def process_documents(file_paths: list[str]):
    pipeline = linear_pipeline(
        json_schema=schema,
        additional_instructions=instructions,
    )
    
    # Process concurrently
    tasks = [pipeline.async_run(path) for path in file_paths]
    results = await asyncio.gather(*tasks)
    
    return results
```

## Skip Unnecessary Stages

### Text Input Optimization

When you already have text, skip OCR:

```python
from leapx.pipeline.stages.layers import Stage

# Only extraction - no OCR/Parser overhead
pipeline = linear_pipeline(
    json_schema=schema,
    additional_instructions=instructions,
    stages=[Stage.LLM_EXTRACTION],
)

result = await pipeline.async_run(text, input_type=InputType.TEXT)
```

## Monitoring Performance

### Log Timing

```python
import time
from loguru import logger

start = time.time()
result = await pipeline.async_run(document)
duration = time.time() - start

logger.info(f"Extraction completed in {duration:.2f}s")
```

## Performance Benchmarks

Typical performance for a 1-page document:

| Stage | Duration |
|-------|----------|
| OCR (uncached) | 2-5s |
| OCR (cached) | under 50ms |
| Parser | 50-200ms |
| LLM Extraction (uncached) | 1-3s |
| LLM Extraction (cached) | under 50ms |

## Next Steps

- [Caching Guide](./caching.md) - Detailed caching documentation
- [Tracing](../observability/tracing.md) - Performance monitoring
