import { apiClient, getErrorMessage } from '@/lib/client';
import {
  Task,
  TaskListItem,
  TaskDetail,
  TaskNameRequest,
  TaskConfigurationRequest,
  PresignedUrlRequest,
  PresignedUrlResponse,
  ConfirmDocUploadRequest,
  TaskResponse,
  TaskListResponse,
  TaskDetailResponse,
  TaskListFilterParams,
  TaskStatsResponse,
  TaskResultResponse,
  TaskExecuteResponse,
} from '@/types/task.type';
import {
  mapTaskListResponse,
  mapTaskResponse,
  mapTaskDetailResponse,
  mapTaskExecuteResponse,
} from '@/mappers/task.mapper';
import { PaginatedResponse, GenericResponse, PaginationMetadata } from '@/types/types';
import { mapPaginatedResponse } from '@/mappers/common.mapper';
import { DEFAULT_PAGE_SIZE } from '@/constants/pagination.constants';

// Get all tasks with pagination and filters
export const getAllTasks = async (
  page: number = 1,
  pageSize: number = DEFAULT_PAGE_SIZE,
  filters?: TaskListFilterParams
): Promise<{ data: TaskListItem[]; metadata: PaginationMetadata }> => {
  try {
    const response = await apiClient.get<PaginatedResponse<TaskListResponse>>('/tasks/', {
      params: {
        page,
        page_size: pageSize,
        ...(filters?.status && { status: filters.status }),
        ...(filters?.search && { search: filters.search }),
      },
    });
    return mapPaginatedResponse(mapTaskListResponse)(response.data);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// Get task by ID
export const getTaskById = async (id: number): Promise<TaskDetail> => {
  try {
    const response = await apiClient.get<GenericResponse<TaskDetailResponse>>(`/tasks/${id}`);
    return mapTaskDetailResponse(response.data.data);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// Create or update task name (Step 1)
export const createOrUpdateTaskName = async (request: TaskNameRequest): Promise<Task> => {
  try {
    const response = await apiClient.post<GenericResponse<TaskResponse>>('/tasks/', request);

    return mapTaskResponse(response.data.data);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// Generate presigned URL for file upload (Step 2)
export const generatePresignedUrl = async (
  taskId: number,
  request: PresignedUrlRequest
): Promise<PresignedUrlResponse> => {
  try {
    const response = await apiClient.post<GenericResponse<PresignedUrlResponse>>(
      `/tasks/${taskId}/presigned-url`,
      request
    );

    return response.data.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// Confirm document upload
export const confirmDocUpload = async (
  taskId: number,
  request: ConfirmDocUploadRequest
): Promise<string> => {
  try {
    const response = await apiClient.post<GenericResponse<string>>(
      `/tasks/${taskId}/document-confirm`,
      request
    );

    return response.data.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// Update task configuration (Step 3)
export const updateTaskConfiguration = async (
  taskId: number,
  request: TaskConfigurationRequest
): Promise<Task> => {
  try {
    const response = await apiClient.put<GenericResponse<TaskResponse>>(
      `/tasks/${taskId}/configuration`,
      request
    );

    return mapTaskResponse(response.data.data);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// Execute task
export const executeTask = async (taskId: number): Promise<TaskExecuteResponse> => {
  try {
    const response = await apiClient.post<GenericResponse<TaskExecuteResponse>>(
      `/tasks/${taskId}/execute`
    );
    return mapTaskExecuteResponse(response.data.data);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// Duplicate a task
export const duplicateTask = async (taskId: number): Promise<Task> => {
  try {
    const response = await apiClient.post<GenericResponse<TaskResponse>>(
      `/tasks/${taskId}/duplicate`
    );

    return mapTaskResponse(response.data.data);
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// Delete a task
export const deleteTask = async (taskId: number): Promise<string> => {
  try {
    const response = await apiClient.delete<GenericResponse<string>>(`/tasks/${taskId}`);

    return response.data.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// Delete a task
export const deleteTaskFiles = async (taskId: number): Promise<string> => {
  try {
    const response = await apiClient.delete<GenericResponse<string>>(
      `/tasks/${taskId}/delete-files`
    );

    return response.data.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// Get task statistics
export const getTaskStats = async (): Promise<TaskStatsResponse> => {
  try {
    const response = await apiClient.get<GenericResponse<TaskStatsResponse>>('/tasks/stats');
    return response.data.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

// Get task results
export const getTaskResults = async (taskId: number): Promise<TaskResultResponse> => {
  try {
    const response = await apiClient.get<GenericResponse<TaskResultResponse>>(
      `/tasks/${taskId}/results`
    );
    return response.data.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};
