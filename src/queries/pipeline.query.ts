import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  getAllPipelines,
  getPipelineById,
  getPipelineConfigs,
  createPipeline,
  updatePipeline,
  togglePipelineStatus,
  duplicatePipeline,
  deletePipeline,
  getPipelineStats,
} from '@/services/pipeline.service';
import { PipelineCreateRequest, PipelineUpdateRequest } from '@/types/pipeline.type';
import { DEFAULT_STATUS } from '@/constants/dataresult.constant';
import { DEFAULT_PAGE_SIZE } from '@/constants/pagination.constants';

// Query keys
export const pipelineKeys = {
  all: ['pipelines'] as const,
  lists: () => [...pipelineKeys.all, 'list'] as const,
  list: (page: number, pageSize: number, status: string, search: string) =>
    [...pipelineKeys.lists(), { page, pageSize, status, search }] as const,
  details: () => [...pipelineKeys.all, 'detail'] as const,
  detail: (id: number) => [...pipelineKeys.details(), id] as const,
  stats: () => [...pipelineKeys.all, 'stats'] as const,
  configs: () => [...pipelineKeys.all, 'configs'] as const,
};

// Get all pipelines with pagination
export const useGetPipelines = (
  page: number = 1,
  pageSize: number = DEFAULT_PAGE_SIZE,
  status: string = DEFAULT_STATUS,
  search: string = ''
) => {
  return useQuery({
    queryKey: pipelineKeys.list(page, pageSize, status, search),
    queryFn: () => getAllPipelines(page, pageSize, status, search),
  });
};

export const useGetPipelineStats = () => {
  return useQuery({
    queryKey: pipelineKeys.stats(),
    queryFn: () => getPipelineStats(),
  });
};

export const useGetPipelineConfigs = () => {
  return useQuery({
    queryKey: pipelineKeys.configs(),
    queryFn: getPipelineConfigs,
    staleTime: 5 * 60 * 1000, // configs don't change at runtime — cache for 5 min
  });
};

// Get single pipeline by ID
export const useGetPipeline = (id: number) => {
  return useQuery({
    queryKey: pipelineKeys.detail(id),
    queryFn: () => getPipelineById(id),
    enabled: !!id,
  });
};

// Create pipeline mutation
export const useCreatePipeline = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: PipelineCreateRequest) => createPipeline(request),
    onSuccess: () => {
      // Invalidate all pipeline queries to refetch the data
      queryClient.invalidateQueries({ queryKey: pipelineKeys.lists() });
      queryClient.invalidateQueries({ queryKey: pipelineKeys.stats() });
    },
  });
};

// Update pipeline mutation
export const useUpdatePipeline = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, request }: { id: number; request: PipelineUpdateRequest }) =>
      updatePipeline(id, request),
    onSuccess: (_, variables) => {
      // Invalidate all pipeline queries to refetch the data
      queryClient.invalidateQueries({ queryKey: pipelineKeys.lists() });
      queryClient.invalidateQueries({ queryKey: pipelineKeys.detail(variables.id) });
    },
  });
};

// Toggle pipeline status mutation
export const useTogglePipelineStatus = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => togglePipelineStatus(id),
    onSuccess: (_, id) => {
      // Invalidate all pipeline queries to refetch the data
      queryClient.invalidateQueries({ queryKey: pipelineKeys.lists() });
      queryClient.invalidateQueries({ queryKey: pipelineKeys.detail(id) });
    },
  });
};

// Duplicate pipeline mutation
export const useDuplicatePipeline = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => duplicatePipeline(id),
    onSuccess: () => {
      // Invalidate all pipeline queries to refetch the data
      queryClient.invalidateQueries({ queryKey: pipelineKeys.lists() });
    },
  });
};

// Delete pipeline mutation
export const useDeletePipeline = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => deletePipeline(id),
    onSuccess: () => {
      // Invalidate all pipeline queries to refetch the data
      queryClient.invalidateQueries({ queryKey: pipelineKeys.lists() });
      queryClient.invalidateQueries({ queryKey: pipelineKeys.stats() });
    },
  });
};
