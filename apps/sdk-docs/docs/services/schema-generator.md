---
sidebar_position: 4
---

# Schema Generator Service

The Schema Generator dynamically converts JSON Schema definitions into Pydantic models at runtime.

## Overview

This service enables LeapX to work with JSON Schema dictionaries directly, without requiring pre-defined Pydantic models.

## Basic Usage

```python
from leapx.services.schema_generator import generate_model

# JSON Schema definition
json_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Person's name"},
        "age": {"type": "integer", "description": "Person's age"}
    },
    "required": ["name"]
}

# Generate Pydantic model
PersonModel = generate_model(json_schema)

# Use the model
person = PersonModel(name="John", age=30)
```

## Type Resolution

The schema generator handles JSON Schema types:

| JSON Schema | Python Type |
|-------------|-------------|
| `string` | `str` |
| `integer` | `int` |
| `number` | `float` |
| `boolean` | `bool` |
| `array` | `list[T]` |
| `object` | Nested Pydantic model |
| `null` | `None` |

## Format Handling

Special string formats are mapped to Python types:

```python
schema = {
    "type": "object",
    "properties": {
        "created_at": {"type": "string", "format": "date-time"},
        "birth_date": {"type": "string", "format": "date"},
        "meeting_time": {"type": "string", "format": "time"},
        "website": {"type": "string", "format": "uri"},
        "id": {"type": "string", "format": "uuid"},
    }
}
```

| Format | Python Type |
|--------|-------------|
| `date-time` | `datetime` |
| `date` | `date` |
| `time` | `time` |
| `uri` | `AnyUrl` |
| `uuid` | `UUID` |
| `email` | `str` |

## Complex Schemas

### Nested Objects

```python
schema = {
    "type": "object",
    "properties": {
        "company": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "address": {"type": "string"}
            }
        }
    }
}
```

### Arrays

```python
schema = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "price": {"type": "number"}
                }
            }
        }
    }
}
```

### Enums

```python
schema = {
    "type": "object",
    "properties": {
        "status": {
            "enum": ["pending", "approved", "rejected"]
        }
    }
}
```

### Union Types

```python
schema = {
    "type": "object",
    "properties": {
        "value": {
            "type": ["string", "integer", "null"]
        }
    }
}
```

## Reference Resolution

The generator handles `$ref` references:

```python
schema = {
    "type": "object",
    "properties": {
        "billing": {"$ref": "#/$defs/Address"},
        "shipping": {"$ref": "#/$defs/Address"}
    },
    "$defs": {
        "Address": {
            "type": "object",
            "properties": {
                "street": {"type": "string"},
                "city": {"type": "string"}
            }
        }
    }
}
```

## Error Handling

The generator raises specific exceptions:

```python
from leapx.services.schema_generator.exceptions import (
    JsonSchemaTypeError,
    ReferenceError,
)

try:
    model = generate_model(invalid_schema)
except JsonSchemaTypeError as e:
    print(f"Type error: {e}")
except ReferenceError as e:
    print(f"Reference error: {e}")
```

## Next Steps

- [JSON Schema](../concepts/json-schema.md) - Schema best practices
- [Extractor Service](./extractor.md) - Using generated models
