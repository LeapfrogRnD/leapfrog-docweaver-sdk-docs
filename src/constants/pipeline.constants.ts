export const OCR_PROVIDER = {
  aws_textract: 'AWS Textract',
  azure_document_intelligence: 'Azure OCR',
  vlm: 'VLM OCR',
};

export const LLM_PROVIDER = {
  bedrock: 'Bedrock',
  openai: 'OpenAI',
};

export const LLM_MODELS = {
  bedrock: {
    'bedrock/us.anthropic.claude-sonnet-4-5-20250929-v1:0': 'Anthropic Claude Sonnet 4.5',
    'bedrock/us.meta.llama3-2-1b-instruct-v1:0': 'Meta LLaMA 3 2.1B Instruct',
    'bedrock/qwen.qwen3-32b-v1:0': 'Qwen 3 32B',
  },
  openai: {
    'gpt-4.1-nano': 'GPT-4.1 Nano',
  },
};

export const VLM_PROVIDER = {
  bedrock: 'Bedrock VLM',
};

export const VLM_MODELS = {
  bedrock: {
    'bedrock/qwen.qwen3-vl-235b-a22b': 'Qwen 3 VL 235B',
    'bedrock/global.anthropic.claude-sonnet-4-5-20250929-v1:0': 'Anthropic Claude Sonnet 4.5 VLM',
  },
};

export const PARSING_METHOD = {
  layout_conserved: 'Layout Conserved',
  layout_conserved_advance: 'Layout Conserved Advanced',
};
