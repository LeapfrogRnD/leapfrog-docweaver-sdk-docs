export interface Pipeline {
  id: number;
  name: string;
  description: string | null;
  is_active: boolean;
  is_default: boolean;
  ocr_provider: string | null;
  parsing_method: string | null;
  vlm_model_provider: string | null;
  vlm_model: string | null;
  llm_model_provider: string;
  llm_model: string;
  created_by: number | null;
  created_at: string;
  updated_at: string | null;
}

export interface PipelineCreateRequest {
  name: string;
  description?: string | null;
  parsing_method?: string | null;
  ocr_provider?: string | null;
  vlm_model_provider?: string | null;
  vlm_model?: string | null;
  llm_model_provider: string;
  llm_model: string;
}

export interface PipelineUpdateRequest {
  name: string;
  description?: string | null;
  parsing_method?: string | null;
  ocr_provider?: string | null;
  vlm_model_provider?: string | null;
  vlm_model?: string | null;
  llm_model_provider: string;
  llm_model: string;
}

export interface PipelineResponse {
  id: number;
  name: string;
  description: string | null;
  is_active: boolean;
  is_default: boolean;
  ocr_provider: string | null;
  parsing_method: string | null;
  vlm_model_provider: string | null;
  vlm_model: string | null;
  llm_model_provider: string | null;
  llm_model: string | null;
  created_by: number | null;
  created_at: string;
  updated_at: string | null;
}

export interface PipelineListResponse {
  id: number;
  name: string;
  description: string | null;
  is_active: boolean;
  is_default: boolean;
  ocr_provider: string | null;
  parsing_method: string | null;
  vlm_model_provider: string | null;
  vlm_model: string | null;
  llm_model_provider: string | null;
  llm_model: string | null;
  created_by: number | null;
  created_at: string;
  updated_at: string | null;
}

export interface PipelineStatsResponse {
  total: number;
  last_updated: string | null;
}

export interface ModelOption {
  value: string;
  label: string;
}

export interface ProviderOption {
  value: string;
  label: string;
}

export interface LLMProviderOption {
  value: string;
  label: string;
  models: ModelOption[];
}

export interface VLMProviderOption {
  value: string;
  label: string;
  models: ModelOption[];
}

export interface PipelineConfigsResponse {
  ocr_providers: ProviderOption[];
  llm_providers: LLMProviderOption[];
  vlm_providers: VLMProviderOption[];
  parsing_methods: ProviderOption[];
}
