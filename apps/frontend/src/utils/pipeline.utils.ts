import {
  OCR_PROVIDER,
  LLM_PROVIDER,
  LLM_MODELS,
  PARSING_METHOD,
  VLM_MODELS,
} from '@/constants/pipeline.constants';

/**
 * Get the display label for OCR provider
 */
export const getOcrProviderLabel = (ocrProvider: string | null): string => {
  if (!ocrProvider) return 'N/A';
  return OCR_PROVIDER[ocrProvider as keyof typeof OCR_PROVIDER] || ocrProvider;
};

/**
 * Get the display label for LLM provider
 */
export const getLlmProviderLabel = (llmProvider: string | null): string => {
  if (!llmProvider) return 'N/A';
  return LLM_PROVIDER[llmProvider as keyof typeof LLM_PROVIDER] || llmProvider;
};

/**
 * Get the display label for LLM model
 */
export const getLlmModelLabel = (llmProvider: string | null, llmModel: string | null): string => {
  if (!llmProvider || !llmModel) return 'N/A';

  const models = LLM_MODELS[llmProvider as keyof typeof LLM_MODELS];
  if (!models) return llmModel;

  return models[llmModel as keyof typeof models] || llmModel;
};

/**
 * Get the display label for parsing method
 */
export const getParsingMethodLabel = (parsingMethod: string | null): string => {
  if (!parsingMethod) return 'N/A';
  return PARSING_METHOD[parsingMethod as keyof typeof PARSING_METHOD] || parsingMethod;
};

/**
 * Get the display label for VLM model
 */
export const getVlmModelLabel = (vlmProvider: string | null, vlmModel: string | null): string => {
  if (!vlmProvider || !vlmModel) return 'N/A';

  const models = VLM_MODELS[vlmProvider as keyof typeof VLM_MODELS];
  if (!models) return vlmModel;

  return models[vlmModel as keyof typeof models] || vlmModel;
};
