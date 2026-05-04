import { apiClient, getErrorMessage } from '@/lib/client';
import {
  Pipeline,
  PipelineConfigsResponse,
  PipelineCreateRequest,
  PipelineUpdateRequest,
  PipelineResponse,
  PipelineListResponse,
  PipelineStatsResponse,
} from '@/types/pipeline.type';
import { mapPipelineListResponse, mapPipelineResponse } from '@/mappers/pipeline.mapper';
import { PaginatedResponse, GenericResponse, PaginationMetadata } from '@/types/types';
import { mapPaginatedResponse } from '@/mappers/common.mapper';
import { DEFAULT_PAGE_SIZE } from '@/constants/pagination.constants';
import { DEFAULT_STATUS } from '@/constants/dataresult.constant';

export const getAllPipelines = async (
  page: number = 1,
  pageSize: number = DEFAULT_PAGE_SIZE,
  status: string = DEFAULT_STATUS,
  search: string = ''
): Promise<{ data: Pipeline[]; metadata: PaginationMetadata }> => {
  try {
    const response = await apiClient.get<PaginatedResponse<PipelineListResponse>>('/pipelines/', {
      params: {
        page,
        page_size: pageSize,
        status: status,
        search: search,
      },
    });
    return mapPaginatedResponse(mapPipelineListResponse)(response.data);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

export const getPipelineById = async (id: number): Promise<Pipeline> => {
  try {
    const response = await apiClient.get<GenericResponse<PipelineResponse>>(`/pipelines/${id}`);
    return mapPipelineResponse(response.data.data);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// Create a new pipeline
export const createPipeline = async (request: PipelineCreateRequest): Promise<Pipeline> => {
  try {
    const response = await apiClient.post<GenericResponse<PipelineResponse>>(
      '/pipelines/',
      request
    );

    // Transform the response using mapper
    return mapPipelineResponse(response.data.data);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// Update a pipeline
export const updatePipeline = async (
  id: number,
  request: PipelineUpdateRequest
): Promise<Pipeline> => {
  try {
    const response = await apiClient.put<GenericResponse<PipelineResponse>>(
      `/pipelines/${id}`,
      request
    );

    return mapPipelineResponse(response.data.data);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// Toggle pipeline status
export const togglePipelineStatus = async (id: number): Promise<Pipeline> => {
  try {
    const response = await apiClient.patch<GenericResponse<PipelineResponse>>(
      `/pipelines/${id}/toggle-status`
    );

    return mapPipelineResponse(response.data.data);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// Duplicate a pipeline
export const duplicatePipeline = async (id: number): Promise<Pipeline> => {
  try {
    const response = await apiClient.post<GenericResponse<PipelineResponse>>(
      `/pipelines/${id}/duplicate`
    );

    return mapPipelineResponse(response.data.data);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// Delete a pipeline
export const deletePipeline = async (id: number): Promise<void> => {
  try {
    await apiClient.delete<GenericResponse<string>>(`/pipelines/${id}`);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// Get pipeline statistics
export const getPipelineStats = async (): Promise<PipelineStatsResponse> => {
  try {
    const response =
      await apiClient.get<GenericResponse<PipelineStatsResponse>>('/pipelines/stats');
    return response.data.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// Get available pipeline configuration options (providers / models)
export const getPipelineConfigs = async (): Promise<PipelineConfigsResponse> => {
  try {
    const response =
      await apiClient.get<GenericResponse<PipelineConfigsResponse>>('/pipelines/configs');
    return response.data.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};
