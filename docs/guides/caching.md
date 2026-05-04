---
sidebar_position: 3
---

# Caching Guide

LeapFrog DocWeaver provides built-in caching to avoid redundant OCR and LLM calls. This significantly improves performance and reduces costs when processing the same documents multiple times.

## Cache Types

| Type | Description | Best For |
|------|-------------|----------|
| SQLite | Database-backed cache | Production, persistent storage |
| File | File system cache | Development, simple setups |

## Enabling Caching

### Basic Configuration

```python
from leapx import linear_pipeline
from leapx.common.cache.cache_config import CacheConfig

pipeline = linear_pipeline(
    json_schema=schema,
    additional_instructions=instructions,
    ocr_cache_config=CacheConfig(enabled=True),
    llm_cache_config=CacheConfig(enabled=True),
)
```

### Custom Cache Directory

```python
ocr_cache = CacheConfig(
    enabled=True,
    cache_type="sqlite",
    cache_dir="./cache/ocr",
)

llm_cache = CacheConfig(
    enabled=True,
    cache_type="sqlite",
    cache_dir="./cache/llm",
)
```

## Cache Configuration Options

```python
from leapx.common.cache.cache_config import CacheConfig

cache_config = CacheConfig(
    enabled=True,           # Enable/disable caching
    cache_type="sqlite",    # "sqlite" or "file"
    cache_dir="./cache",    # Cache storage directory
)
```

## What Gets Cached

### OCR Cache

- **Key**: Document hash (based on file content)
- **Value**: Raw OCR output
- **Benefit**: Avoids expensive OCR API calls

### LLM Cache

- **Key**: Hash of (text content + schema + prompt)
- **Value**: Extraction result
- **Benefit**: Avoids LLM API calls for identical inputs

## Cache Architecture

```
┌─────────────────────────────────────────┐
│              Cache Layer                │
├─────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    │
│  │ Cache Facade│ <- │Cache Factory│    │
│  └──────┬──────┘    └─────────────┘    │
│         │                               │
│  ┌──────┴──────┐                        │
│  │Cache Manager│                        │
│  └──────┬──────┘                        │
│         │                               │
│  ┌──────┴──────────────────────┐       │
│  │   SQLite   │     File       │       │
│  │   Cache    │    Cache       │       │
│  └─────────────────────────────┘       │
└─────────────────────────────────────────┘
```

## Using the Cache Directly

```python
from leapx.common.cache.cache_facade import CacheFacade
from leapx.common.cache.cache_config import CacheConfig

# Create cache instance
cache = CacheFacade(CacheConfig(enabled=True))

# Store value
await cache.set("my_key", {"data": "value"})

# Retrieve value
result = await cache.get("my_key")

# Check if key exists
exists = await cache.exists("my_key")

# Delete key
await cache.delete("my_key")
```

## Cache Invalidation

### Manual Invalidation

```python
# Clear specific cache entry
await cache.delete("document_hash_123")

# Clear all cache (implementation specific)
# For SQLite: delete the .db file
# For File: delete the cache directory
```

### Automatic Invalidation

Caches are automatically invalidated when:
- Document content changes (different hash)
- Schema changes (for LLM cache)
- System prompt changes (for LLM cache)

## Best Practices

### 1. Enable Caching in Production

```python
# Always enable for production
cache_config = CacheConfig(
    enabled=True,
    cache_type="sqlite",
    cache_dir="/var/cache/leapx",
)
```

### 2. Disable During Development

```python
# Disable when testing schema changes
cache_config = CacheConfig(enabled=False)
```

### 3. Separate OCR and LLM Caches

```python
# Use different directories for easy management
ocr_cache = CacheConfig(cache_dir="./cache/ocr")
llm_cache = CacheConfig(cache_dir="./cache/llm")
```

### 4. Monitor Cache Size

```bash
# Check cache size
du -sh ./cache/
```

## Performance Impact

| Scenario | Without Cache | With Cache |
|----------|--------------|------------|
| First document | ~5-10s | ~5-10s |
| Same document again | ~5-10s | under 100ms |
| Similar document | ~5-10s | ~3-5s (partial hit) |

## Next Steps

- [Configuration](../getting-started/configuration.md) - Full configuration options
- [Performance](./performance.md) - Optimization tips
