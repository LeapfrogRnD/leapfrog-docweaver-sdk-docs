---
sidebar_position: 3
---

# Layout Parser Service

The Layout Parser processes raw OCR output and structures the text while preserving document layout.

## Parsing Methods

| Method | Description |
|--------|-------------|
| `LAYOUT_CONSERVED` | Preserves original document layout and structure |

## Configuration

```python
from leapx import linear_pipeline
from leapx.common.types.providers import ParsingMethod

pipeline = linear_pipeline(
    json_schema=schema,
    system_prompt=prompt,
    parser=ParsingMethod.LAYOUT_CONSERVED,
)
```

## What the Parser Does

1. **Text Structuring**: Organizes raw OCR text into logical sections
2. **Layout Preservation**: Maintains document structure (headers, paragraphs, lists)
3. **Noise Reduction**: Cleans up OCR artifacts
4. **Normalization**: Standardizes whitespace and formatting

## Parser Output

The parser transforms raw OCR output into clean, structured text:

**Before (Raw OCR):**
```
I N V O I C E
Invoice   Number:   INV-001
D  a  t  e:  2024-01-15
```

**After (Parsed):**
```
INVOICE
Invoice Number: INV-001
Date: 2024-01-15
```

## When to Use Different Methods

### LAYOUT_CONSERVED

Best for:
- Documents with complex layouts
- Forms and tables
- Multi-column documents

```python
parser=ParsingMethod.LAYOUT_CONSERVED
```

## Integration with Pipeline

The parser runs after OCR and before LLM extraction:

```
OCR → Parser → LLM Extraction
      ^^^^^^
      Layout Parser
```

## Next Steps

- [OCR Service](./ocr.md) - Input to the parser
- [Extractor Service](./extractor.md) - Uses parser output
- [Generator Service](./generator.md) - LLM generation based on parsed text
- [Stages](../concepts/stages.md) - Pipeline stage details
