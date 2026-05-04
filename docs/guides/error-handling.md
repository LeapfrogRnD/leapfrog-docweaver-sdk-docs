---
sidebar_position: 4
---

# Error Handling

This guide covers how to handle errors in LeapFrog DocWeaver pipelines effectively.

## Common Exceptions

### Pipeline Exceptions

```python
from leapx.pipeline.stages.exceptions import MissingStageError

try:
    pipeline = dag_pipeline(stages=[])
except MissingStageError:
    print("Pipeline requires at least one stage")
```

### Schema Exceptions

```python
from leapx.services.schema_generator.exceptions import (
    JsonSchemaTypeError,
    ReferenceError,
)

try:
    model = generate_model(invalid_schema)
except JsonSchemaTypeError as e:
    print(f"Invalid schema type: {e}")
except ReferenceError as e:
    print(f"Invalid reference: {e}")
```

## Error Handling Patterns

### Basic Try-Catch

```python
from leapx.common.exceptions.base import LeapXException

try:
    result = await pipeline.async_run("document.pdf")
except LeapXException as e:
    logger.error(f"Pipeline error: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

### Comprehensive Error Handling

```python
from leapx.common.exceptions.base import LeapXException
from leapx.services.schema_generator.exceptions import (
    JsonSchemaTypeError,
    ReferenceError,
)
from loguru import logger

async def safe_extract(file_path: str):
    try:
        pipeline = linear_pipeline(
            json_schema=schema,
            additional_instructions=instructions,
        )
        result = await pipeline.async_run(file_path)
        return {"success": True, "data": result}
        
    except JsonSchemaTypeError as e:
        logger.error(f"Invalid schema: {e}")
        return {"success": False, "error": "schema_error", "message": str(e)}
        
    except ReferenceError as e:
        logger.error(f"Schema reference error: {e}")
        return {"success": False, "error": "reference_error", "message": str(e)}
        
    except LeapXException as e:
        logger.error(f"Pipeline error: {e}")
        return {"success": False, "error": "pipeline_error", "message": str(e)}
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        return {"success": False, "error": "file_not_found", "message": str(e)}
        
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return {"success": False, "error": "unknown_error", "message": str(e)}
```

## Pipeline Error Handler

LeapX provides a centralized error handler:

```python
from leapx.pipeline.core.error_handler import PipelineErrorHandler

try:
    result = await pipeline.async_run(document)
except Exception as e:
    PipelineErrorHandler.handle_execution_error(e)
```

## Retry Strategies

### Simple Retry

```python
import asyncio

async def extract_with_retry(file_path: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            result = await pipeline.async_run(file_path)
            return result
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### Retry with Different Config

```python
async def extract_with_fallback(file_path: str):
    # Try with primary model
    try:
        pipeline = linear_pipeline(
            json_schema=schema,
            additional_instructions=instructions,
            llm_model="anthropic.claude-3-sonnet-20240229-v1:0",
        )
        return await pipeline.async_run(file_path)
    except Exception as e:
        logger.warning(f"Primary model failed: {e}")
    
    # Fallback to alternative model
    try:
        pipeline = linear_pipeline(
            json_schema=schema,
            additional_instructions=instructions,
            llm_model="anthropic.claude-3-haiku-20240307-v1:0",
        )
        return await pipeline.async_run(file_path)
    except Exception as e:
        logger.error(f"Fallback model also failed: {e}")
        raise
```

## Logging Errors

Use Loguru for consistent error logging:

```python
from loguru import logger

try:
    result = await pipeline.async_run(file_path)
except Exception as e:
    logger.error(f"Extraction failed for {file_path}")
    logger.exception(e)  # Includes full traceback
```

## Best Practices

1. **Always wrap pipeline calls** in try-except blocks
2. **Log errors** with context (file path, schema, etc.)
3. **Use specific exceptions** before generic ones
4. **Implement retries** for transient failures
5. **Provide fallbacks** where possible
6. **Return structured error responses** for API usage

## Next Steps

- [Logging](../observability/logging.md) - Configure logging
- [Tracing](../observability/tracing.md) - Debug with tracing
