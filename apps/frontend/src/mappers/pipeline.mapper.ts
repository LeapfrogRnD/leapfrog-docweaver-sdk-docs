import { Pipeline, PipelineResponse, PipelineListResponse } from '@/types/pipeline.type';

/**
 * Maps pipeline list response from backend to frontend format
 */
export const mapPipelineListResponse = (pipeline: PipelineListResponse): Pipeline => {
  return {
    id: pipeline.id,
    name: pipeline.name,
    description: pipeline.description,
    is_active: pipeline.is_active,
    is_default: pipeline.is_default,
    ocr_provider: pipeline.ocr_provider,
    parsing_method: pipeline.parsing_method,
    vlm_model_provider: pipeline.vlm_model_provider,
    vlm_model: pipeline.vlm_model,
    llm_model_provider: pipeline.llm_model_provider || '',
    llm_model: pipeline.llm_model || '',
    created_by: pipeline.created_by,
    created_at: pipeline.created_at,
    updated_at: pipeline.updated_at,
  };
};

/**
 * Maps pipeline creation/update response from backend to frontend format
 */
export const mapPipelineResponse = (response: PipelineResponse): Pipeline => {
  return {
    id: response.id,
    name: response.name,
    description: response.description,
    is_active: response.is_active,
    is_default: response.is_default,
    ocr_provider: response.ocr_provider,
    parsing_method: response.parsing_method,
    vlm_model_provider: response.vlm_model_provider,
    vlm_model: response.vlm_model,
    llm_model_provider: response.llm_model_provider || '',
    llm_model: response.llm_model || '',
    created_by: response.created_by,
    created_at: response.created_at,
    updated_at: response.updated_at,
  };
};

/**
 * Maps array of pipeline list responses to array of Pipeline models
 */
export const mapPipelineListResponsesToPipelines = (
  responses: PipelineListResponse[]
): Pipeline[] => {
  return responses.map(mapPipelineListResponse);
};
