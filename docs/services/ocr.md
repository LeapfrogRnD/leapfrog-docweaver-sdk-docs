---
sidebar_position: 1
---

# OCR Service

The OCR (Optical Character Recognition) service converts documents and images to text. LeapX supports multiple OCR providers.

## Supported Providers

| Provider | Description | Best For |
|----------|-------------|----------|
| AWS Textract | Amazon's OCR service | High accuracy, tables, forms |
| Azure Document Intelligence | Microsoft's OCR service | Complex layouts, handwriting |

## Configuration

### AWS Textract (Default)

```python
from leapx import linear_pipeline
from leapx.common.types.providers import OCRProviderType
from leapx.services.credentials.ocr.aws_config import AwsOcrCredential

pipeline = linear_pipeline(
    json_schema=schema,
    system_prompt=prompt,
    ocr_provider=OCRProviderType.AWS_TEXTRACT,
    ocr_credential=AwsOcrCredential(
        aws_access_key_id="YOUR_KEY",
        aws_secret_access_key="YOUR_SECRET",
        region_name="us-east-1",
    ),
)
```

### Azure Document Intelligence

```python
from leapx.common.types.providers import OCRProviderType

pipeline = linear_pipeline(
    json_schema=schema,
    system_prompt=prompt,
    ocr_provider=OCRProviderType.AZURE,
)
```

## Environment Variables

### AWS Textract

```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
```

### Azure Document Intelligence

```bash
AZURE_OCR_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_OCR_API_KEY=your_key
```

## OCR Output

The OCR stage produces structured output including:

- Raw text content
- Page information
- Word/line bounding boxes (provider-dependent)
- Table structures (if detected)
- Form fields (if detected)

## Caching OCR Results

OCR is often the most expensive operation. Enable caching to avoid redundant calls:

```python
from leapx.common.cache.cache_config import CacheConfig

pipeline = linear_pipeline(
    json_schema=schema,
    system_prompt=prompt,
    ocr_cache_config=CacheConfig(
        enabled=True,
        cache_type="sqlite",
        cache_dir="./cache/ocr",
    ),
)
```

## Provider Comparison

| Feature | AWS Textract | Azure Doc Intelligence |
|---------|-------------|----------------------|
| Table extraction | ✅ Excellent | ✅ Excellent |
| Form detection | ✅ Good | ✅ Excellent |
| Handwriting | ⚠️ Limited | ✅ Good |
| Multi-language | ✅ Good | ✅ Excellent |
| Pricing | Per page | Per page |

## Next Steps

- [Extractor Service](./extractor.md) - LLM extraction
- [Layout Parser](./layout-parser.md) - Text structuring
- [Configuration](../getting-started/configuration.md) - Full setup guide
