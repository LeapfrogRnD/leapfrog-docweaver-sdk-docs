import { apiClient, getErrorMessage } from '@/lib/client';
import {
  ApiKey,
  ApiKeyCreateRequest,
  ApiKeyResponse,
  ApiKeyListResponse,
  ApiKeyUpdateRequest,
  ApiKeyIntegration,
  IntegrationStatsResponse,
} from '@/types/api-key.type';
import {
  mapApiKeyListResponse,
  mapApiKeyCreateResponse,
  mapApiKeyIntegrationListResponse,
} from '@/mappers/api-keys.mapper';
import { PaginatedResponse, GenericResponse, PaginationMetadata } from '@/types/types';
import { mapPaginatedResponse } from '@/mappers/common.mapper';
import { DEFAULT_PAGE_SIZE } from '@/constants/pagination.constants';

// Get all API keys with pagination
export const getAllApiKeys = async (
  page: number = 1,
  pageSize: number = DEFAULT_PAGE_SIZE,
  status: string = 'all',
  search: string = ''
): Promise<{ data: ApiKey[]; metadata: PaginationMetadata }> => {
  try {
    const response = await apiClient.get<PaginatedResponse<ApiKeyListResponse>>('/api-keys/', {
      params: {
        page,
        page_size: pageSize,
        status,
        ...(search && { search }),
      },
    });
    return mapPaginatedResponse(mapApiKeyListResponse)(response.data);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// Create a new API key
export const createApiKey = async (request: ApiKeyCreateRequest): Promise<ApiKey> => {
  try {
    const response = await apiClient.post<GenericResponse<ApiKeyResponse>>('/api-keys/', request);

    // Transform the response using mapper
    return mapApiKeyCreateResponse(response.data.data);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// Update a pipeline
export const updatePipeline = async (id: number, request: ApiKeyUpdateRequest): Promise<ApiKey> => {
  try {
    const response = await apiClient.put<GenericResponse<ApiKeyResponse>>(
      `/api-keys/${id}`,
      request
    );

    return mapApiKeyCreateResponse(response.data.data);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// Delete an API key
export const deleteApiKey = async (id: number): Promise<void> => {
  try {
    await apiClient.delete<GenericResponse<string>>(`/api-keys/${id}`);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// Delete an API key
export const getApiKeyById = async (id: number): Promise<ApiKeyResponse> => {
  try {
    const response = await apiClient.get<GenericResponse<ApiKeyResponse>>(`/api-keys/${id}`);
    return mapApiKeyCreateResponse(response.data.data);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

export const regenerateApiSecret = async (id: number): Promise<void> => {
  try {
    await apiClient.post<GenericResponse<string>>(`/api-keys/${id}/regenerate-secret`);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

export const toggleApiKeyStatus = async (id: number): Promise<ApiKey> => {
  try {
    const response = await apiClient.patch<GenericResponse<ApiKeyResponse>>(
      `/api-keys/${id}/toggle-status`
    );
    return mapApiKeyCreateResponse(response.data.data);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// Get all API keys with pagination
export const getAllApiKeysIntegrations = async (
  apiKeyId: number,
  page: number = 1,
  pageSize: number = DEFAULT_PAGE_SIZE,
  status: string = 'all',
  search: string = ''
): Promise<{ data: ApiKeyIntegration[]; metadata: PaginationMetadata }> => {
  try {
    const response = await apiClient.get<PaginatedResponse<ApiKeyIntegration>>(
      `/api-keys/${apiKeyId}/integrations`,
      {
        params: {
          page,
          page_size: pageSize,
          status,
          ...(search && { search }),
        },
      }
    );
    return mapPaginatedResponse(mapApiKeyIntegrationListResponse)(response.data);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

export const getApiKeyIntegrationStats = async (
  apiKeyId: number
): Promise<IntegrationStatsResponse> => {
  try {
    const response = await apiClient.get<GenericResponse<IntegrationStatsResponse>>(
      `/api-keys/${apiKeyId}/integrations/stats`
    );
    return response.data.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};
