import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  getAllApiKeys,
  createApiKey,
  deleteApiKey,
  updatePipeline,
  getApiKeyById,
  getAllApiKeysIntegrations,
  getApiKeyIntegrationStats,
  regenerateApiSecret,
  toggleApiKeyStatus,
} from '@/services/api-key.service';
import { ApiKeyCreateRequest, ApiKeyUpdateRequest } from '@/types/api-key.type';

// Query keys
export const apiKeyKeys = {
  all: ['apiKeys'] as const,
  lists: () => [...apiKeyKeys.all, 'list'] as const,
  list: (page: number, pageSize: number, status: string, search: string) =>
    [...apiKeyKeys.lists(), { page, pageSize, status, search }] as const,
  details: () => [...apiKeyKeys.all, 'detail'] as const,
  detail: (id: number) => [...apiKeyKeys.details(), id] as const,
};

export const apiKeyIntegrationKeys = {
  all: ['apiKeysIntegrations'] as const,
  lists: () => [...apiKeyIntegrationKeys.all, 'list'] as const,
  list: (page: number, pageSize: number) =>
    [...apiKeyIntegrationKeys.lists(), { page, pageSize }] as const,
  details: () => [...apiKeyIntegrationKeys.all, 'detail'] as const,
  detail: (id: number) => [...apiKeyIntegrationKeys.details(), id] as const,
  stats: () => [...apiKeyIntegrationKeys.all, 'stats'] as const,
};

export const useGetApiKeys = (
  page: number = 1,
  pageSize: number = 25,
  status: string = 'all',
  search: string = ''
) => {
  return useQuery({
    queryKey: apiKeyKeys.list(page, pageSize, status, search),
    queryFn: () => getAllApiKeys(page, pageSize, status, search),
  });
};

export const useCreateApiKey = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: ApiKeyCreateRequest) => createApiKey(request),
    onSuccess: () => {
      // Invalidate all API key queries to refetch the data
      queryClient.invalidateQueries({ queryKey: apiKeyKeys.lists() });
    },
  });
};

export const useUpdateApiKey = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, request }: { id: number; request: ApiKeyUpdateRequest }) =>
      updatePipeline(id, request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: apiKeyKeys.lists() });
    },
  });
};

// Delete API key mutation
export const useDeleteApiKey = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => deleteApiKey(id),
    onSuccess: () => {
      // Invalidate all API key queries to refetch the data
      queryClient.invalidateQueries({ queryKey: apiKeyKeys.lists() });
    },
  });
};

export const useGetApiKeyById = (id: number) => {
  return useQuery({
    queryKey: apiKeyKeys.detail(id),
    queryFn: () => getApiKeyById(id),
    enabled: !!id,
  });
};

export const useRegenerateApiSecret = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => regenerateApiSecret(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: apiKeyKeys.lists() });
    },
  });
};

export const useToggleApiKeyStatus = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => toggleApiKeyStatus(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: apiKeyKeys.lists() });
      queryClient.invalidateQueries({ queryKey: apiKeyKeys.detail(id) });
    },
  });
};

export const useGetApiKeyIntegrations = (
  keyid: number,
  page: number = 1,
  pageSize: number = 25,
  status: string = 'all',
  search: string = ''
) => {
  return useQuery({
    queryKey: [...apiKeyIntegrationKeys.list(page, pageSize), { status, search }],
    queryFn: () => getAllApiKeysIntegrations(keyid, page, pageSize, status, search),
  });
};

// Get task statistics
export const useGetApiKeyIntegrationStats = (keyid: number) => {
  return useQuery({
    queryKey: apiKeyIntegrationKeys.stats(),
    queryFn: () => getApiKeyIntegrationStats(keyid),
  });
};
