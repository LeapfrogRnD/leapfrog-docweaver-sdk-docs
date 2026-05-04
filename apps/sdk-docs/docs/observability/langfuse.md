---
sidebar_position: 3
---

# Langfuse Integration

[Langfuse](https://langfuse.com) provides LLM-specific observability for tracking prompts, completions, costs, and performance.

## Setup

### Environment Variables

```bash
LANGFUSE_PUBLIC_KEY=your_public_key
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com  # or self-hosted URL
```

### Installation

Langfuse is included in LeapX dependencies:

```bash
pip install langfuse
```

## Features

Langfuse tracks:

- **Prompts**: System prompts and user inputs
- **Completions**: LLM responses
- **Latency**: Response times per request
- **Tokens**: Input/output token counts
- **Costs**: Estimated API costs
- **Scores**: Quality metrics

## Viewing Data

Access the Langfuse dashboard at:
- Cloud: `https://cloud.langfuse.com`
- Self-hosted: Your configured URL

## Dashboard Views

### Traces

View individual extraction requests with:
- Full prompt/response pairs
- Token usage
- Latency breakdown
- Error details

### Analytics

Aggregate metrics:
- Request volume over time
- Average latency trends
- Cost analysis
- Error rates

## Best Practices

1. **Use meaningful trace names** for easy filtering
2. **Add metadata** to traces for debugging
3. **Monitor costs** to optimize model selection
4. **Set up alerts** for error rate spikes

## Next Steps

- [Logging](./logging.md) - Application logging
- [Tracing](./tracing.md) - Distributed tracing
- [Extractor Service](../services/extractor.md) - LLM configuration
