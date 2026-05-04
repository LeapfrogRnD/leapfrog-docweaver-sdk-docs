---
sidebar_position: 1
---

# Logging

LeapX uses [Loguru](https://github.com/Delgan/loguru) for logging. This guide covers how to configure and use logging in your LeapX applications.

## Default Configuration

LeapX automatically configures logging with sensible defaults:

- **Info logs**: Written to `info.log`
- **Error logs**: Written to `error.log`
- **Console output**: Colored, formatted output

## Log Levels

| Level | Description |
|-------|-------------|
| `TRACE` | Detailed debugging information |
| `DEBUG` | Debug messages |
| `INFO` | General information |
| `WARNING` | Warning messages |
| `ERROR` | Error messages |
| `CRITICAL` | Critical errors |

## Configuring Logging

```python
from loguru import logger

# Set log level
logger.level("INFO")

# Add custom handler
logger.add(
    "custom.log",
    rotation="10 MB",
    retention="7 days",
    level="DEBUG",
)
```

## Logging in Your Code

```python
from loguru import logger

# Basic logging
logger.info("Processing document")
logger.debug(f"File path: {file_path}")
logger.warning("Large document detected")
logger.error("Failed to process document")

# Structured logging
logger.info("Extraction complete", extra={
    "document": file_path,
    "fields_extracted": 5,
    "duration_ms": 1234,
})
```

## Log File Locations

Default log files are created in the project root:

```
project/
├── info.log      # Info and above
├── error.log     # Errors only
└── ...
```

## Disabling Logs

```python
from loguru import logger

# Remove default handler
logger.remove()

# Or disable specific levels
logger.disable("leapx")
```

## Next Steps

- [Tracing](./tracing.md) - Distributed tracing
- [Langfuse](./langfuse.md) - LLM observability
