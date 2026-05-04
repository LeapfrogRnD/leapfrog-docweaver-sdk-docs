import {
  ApiKey,
  ApiKeyResponse,
  ApiKeyListResponse,
  ApiKeyIntegration,
} from '@/types/api-key.type';
import { formatDate } from '@/utils';

/**
 * Maps API key list response from backend to frontend format
 */
export const mapApiKeyListResponse = (key: ApiKeyListResponse): ApiKey => {
  return {
    id: key.id,
    secret_name: key.secret_name,
    secret_value: key.secret_value,
    created_by: key.created_by,
    is_active: key.is_active,
    last_used_at: formatDate(key.last_used_at),
    created_at: formatDate(key.created_at),
  };
};

/**
 * Maps API key creation response from backend to frontend format
 */
export const mapApiKeyCreateResponse = (response: ApiKeyResponse): ApiKey => {
  return {
    id: response.id,
    secret_name: response.secret_name,
    secret_value: response.secret_value,
    webhook_url: response.webhook_url == 'None' ? undefined : response.webhook_url, // Handle "None" string from backend
    created_by: 0, // Will be set by backend based on current user
    is_active: response.is_active,
    last_used_at: null,
    created_at: new Date().toLocaleString(),
  };
};

/**
 * Maps array of API key list responses to array of ApiKey models
 */
export const mapApiKeyListResponsesToApiKeys = (responses: ApiKeyListResponse[]): ApiKey[] => {
  return responses.map(mapApiKeyListResponse);
};

/**
 * Maps API key integration list response from backend to frontend format
 */
export const mapApiKeyIntegrationListResponse = (key: ApiKeyIntegration): ApiKeyIntegration => {
  return {
    job_id: key.job_id,
    name: key.name,
    status: key.status,
    type: key.type,
    rank: key.rank,
    created_at: formatDate(key.created_at, true),
  };
};
