---
sidebar_position: 2
---

# Tracing

LeapX supports distributed tracing via OpenTelemetry for monitoring pipeline execution across services.

## Overview

Tracing helps you:
- Monitor pipeline performance
- Debug slow stages
- Track requests across services
- Identify bottlenecks

## Setup

### Install Dependencies

LeapX includes OpenTelemetry dependencies:

```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp
```

### Configure Tracing

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Setup tracer provider
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317"))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
```

## Environment Variables

```bash
# OTLP Exporter
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_SERVICE_NAME=leapx

# Optional
OTEL_TRACES_SAMPLER=always_on
```

## Trace Structure

LeapX creates spans for each pipeline stage:

```
Pipeline Execution
├── OCR Stage
│   ├── Document Loading
│   └── OCR API Call
├── Parser Stage
│   └── Text Processing
└── LLM Extraction Stage
    ├── Schema Preparation
    └── LLM API Call
```

## Viewing Traces

### Jaeger

```bash
docker run -d --name jaeger \
  -p 16686:16686 \
  -p 4317:4317 \
  jaegertracing/all-in-one:latest
```

Access UI at: `http://localhost:16686`

### Other Backends

LeapX traces work with any OpenTelemetry-compatible backend:
- Jaeger
- Zipkin
- Datadog
- New Relic
- Grafana Tempo

## Next Steps

- [Logging](./logging.md) - Application logging
- [Langfuse](./langfuse.md) - LLM-specific observability
