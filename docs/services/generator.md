# LLM Generation Stage

The generation stage uses a configured LLM provider to convert parsed or raw text into structured outputs (summaries, extraction results, or other generated content). It supports multiple LLM providers and can operate in a context-aware mode to include information from previous chunks.

## Supported Providers

- AWS Bedrock
- OpenAI
- Anthropic
- Azure OpenAI

(The actual available providers depend on which Generator implementations are enabled in the project.)

## What it does

- Accepts parsed text (from layout parsing / parser stages) or direct text chunks.
- Builds a GenerationRequest containing system prompt and user instructions, model selection and generation parameters.
- Optionally includes context from previous chunks to create context-aware prompts.
- Sends the request to the configured generator service and returns the generation response.

## Key Features

- Context-aware generation: when enabled, previous parsing and generation outputs are appended to the user prompt to provide continuity across chunks.
- Stage-level prompt: system prompt can be customized per-stage via additional instruction parameter.
- Runtime config overrides: generation settings may be overridden at runtime when invoking the stage (response_model is handled separately).
- LLM rate/usage limiting: the stage can integrate with a PoolManager to enforce LLM usage limits.
- Graceful cleanup: generator services that expose a close method are closed when the stage is closed.

## Configuration

Typical options passed when creating a pipeline or stage:

- llm_provider: provider identifier (e.g., "bedrock", "openai", "anthropic").
- llm_model: model identifier for the provider.
- additional_instructions: Optional instructions for llm model.
- user_prompt: Base user prompt; the stage injects the parsed text as the content.
- max_tokens: Maximum tokens to request from the model.
- temperature, top_p, etc.: Model-specific generation parameters.
- enable_context: If true, previous chunk context will be included in prompts.
- use_llm_limit: If true, the stage uses the PoolManager to run generation with limits.

Example (using the project helper API):

```python
from leapx import linear_pipeline

pipeline = linear_pipeline(
    json_schema=schema,
    stages=[Stage.PARSER, Stage.LLM_GENERATION],
    enable_context=True,
    llm_provider="bedrock",
    llm_model="bedrock/us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    additional_instructions="You are an assistant that extracts fields from text.",
    max_tokens=30000,
)
```

You can also pass runtime overrides when invoking the stage; the stage applies them except for the response_model which is handled differently by the pipeline.

## Context-aware prompt construction

When previous chunk context is available the stage will build an enhanced prompt that includes:

- Previous generation results (if present)
- The current chunk text

This preserves continuity for multi-chunk documents and improves extraction/summary consistency across pages.

## Output format

The stage returns a structured StageOutput containing:

- data.generation_response: The raw generation response payload from the provider (model output).
- data.input_text_length: Number of characters in the input text used for generation.
- metadata.has_context: Whether previous-chunk context was included.
- context: The context information (previous parsed texts, previous generation outputs, previous chunk index).

## Errors

- MissingInputForGenerationError: Raised when no text input could be found for generation (neither chunk text nor parsed layout content).

## Best practices

- Enable context only when feeding the pipeline with chunked inputs that need continuity.
- Use stage or runtime additional instructions overrides to adapt generated outputs without changing the base pipeline configuration.
- Prefer using a PoolManager or provider-side rate limiting to avoid overuse and throttling.
- Persist or cache generation results if reproducibility or cost control is important.

## Next steps

- See the Layout Parser docs to learn how parsing output is structured (used as input to generation).
- See the Extractor Service docs for examples of building JSON-schema extraction prompts and handling model responses.
