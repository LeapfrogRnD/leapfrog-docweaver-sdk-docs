---
sidebar_position: 2
---

# Installation

## Requirements

- **Python**: 3.12 or higher
- **Package Manager**: pip or uv (recommended)

## Install via uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package manager that we recommend for LeapX:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add leapx to your project
uv add leapx
```

## Install from Source

For development or to get the latest features:

```bash
# Clone the repository
git clone https://github.com/your-org/leapx.git
cd leapx

# Install with uv
uv sync

# Or with pip
pip install -e .
```

## Dependencies

LeapFrog DocWeaver automatically installs the following key dependencies:

| Package | Purpose |
|---------|---------|
| `pydantic` | Schema validation and data models |
| `instructor` | Structured LLM outputs |
| `litellm` | Unified LLM API interface |
| `boto3` | AWS services (Textract, Bedrock) |
| `azure-ai-documentintelligence` | Azure OCR support |
| `pymupdf` | PDF processing |
| `loguru` | Logging |
| `langfuse` | LLM observability |
| `opentelemetry-*` | Distributed tracing |

## Verify Installation

```python
import leapx
print(leapx.__version__)
```

You can also verify the installation by running a simple test:

```python
from leapx import linear_pipeline, InputType
from leapx.pipeline.stages.layers import Stage

# Create a minimal pipeline
pipeline = linear_pipeline(
    json_schema={"type": "object", "properties": {"test": {"type": "string"}}},
    additional_instructions="Extract test data.",
    stages=[Stage.LLM_EXTRACTION],
)

print("LeapX installed successfully!")
```

## Troubleshooting

### Python Version Issues

If you encounter version errors:

```bash
# Check your Python version
python --version

# Use pyenv to install Python 3.12+
pyenv install 3.12
pyenv local 3.12
```

### Dependency Conflicts

If you have dependency conflicts:

```bash
# Create a fresh virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# Install leapx
pip install leapx
```

### AWS/Azure SDK Issues

For cloud provider SDK issues:

```bash
# Reinstall AWS SDK
pip install --upgrade boto3 botocore

# Reinstall Azure SDK
pip install --upgrade azure-ai-documentintelligence
```

## Next Steps

- [Configuration](./configuration.md) - Set up your credentials
- [Quick Start](./quickstart.md) - Create your first pipeline
