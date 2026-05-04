import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  getAllTasks,
  getTaskById,
  createOrUpdateTaskName,
  updateTaskConfiguration,
  executeTask,
  duplicateTask,
  generatePresignedUrl,
  confirmDocUpload,
  deleteTask,
  getTaskStats,
  deleteTaskFiles,
  getTaskResults,
} from '@/services/task.service';
import {
  TaskNameRequest,
  TaskConfigurationRequest,
  PresignedUrlRequest,
  ConfirmDocUploadRequest,
  TaskListFilterParams,
  type TaskStatsResponse,
} from '@/types/task.type';

// Query keys
export const taskKeys = {
  all: ['tasks'] as const,
  lists: () => [...taskKeys.all, 'list'] as const,
  list: (page: number, pageSize: number, filters?: TaskListFilterParams) =>
    [...taskKeys.lists(), { page, pageSize, filters }] as const,
  details: () => [...taskKeys.all, 'detail'] as const,
  detail: (id: number) => [...taskKeys.details(), id] as const,
  stats: () => [...taskKeys.all, 'stats'] as const,
};

// Get all tasks with pagination and filters
export const useGetTasks = (
  page: number = 1,
  pageSize: number = 25,
  filters?: TaskListFilterParams
) => {
  return useQuery({
    queryKey: taskKeys.list(page, pageSize, filters),
    queryFn: () => getAllTasks(page, pageSize, filters),
    // Poll fast when there are active tasks, slow when everything is idle
    refetchInterval: (query) => {
      const tasks = query.state.data?.data;
      if (!tasks) return 5_000;
      const hasActive = tasks.some((t) => t.status === 'processing' || t.status === 'queued');
      return hasActive ? 3_000 : 60_000;
    },
  });
};

// Get single task by ID
export const useGetTask = (id: number) => {
  return useQuery({
    queryKey: taskKeys.detail(id),
    queryFn: () => getTaskById(id),
    enabled: !!id,
  });
};

// Create or update task name mutation
export const useCreateOrUpdateTaskName = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: TaskNameRequest) => createOrUpdateTaskName(request),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
    },
  });
};

// Generate presigned URL mutation
export const useGeneratePresignedUrl = () => {
  return useMutation({
    mutationFn: ({ taskId, request }: { taskId: number; request: PresignedUrlRequest }) =>
      generatePresignedUrl(taskId, request),
  });
};

// Confirm document upload mutation
export const useConfirmDocUpload = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ taskId, request }: { taskId: number; request: ConfirmDocUploadRequest }) =>
      confirmDocUpload(taskId, request),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: taskKeys.detail(variables.taskId) });
    },
  });
};

// Update task configuration mutation
export const useUpdateTaskConfiguration = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ taskId, request }: { taskId: number; request: TaskConfigurationRequest }) =>
      updateTaskConfiguration(taskId, request),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: taskKeys.detail(variables.taskId) });
    },
  });
};

// Execute task mutation
export const useExecuteTask = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: number) => executeTask(taskId),
    onSuccess: (data, taskId) => {
      // Write fresh processing/queued counts from the execute response directly
      // into the stats cache so all components update instantly.
      // The poller overwrites this naturally on the next cycle.
      queryClient.setQueryData<TaskStatsResponse>(taskKeys.stats(), (prev) =>
        prev ? { ...prev, processing: data.processing, queued: data.queued } : prev
      );
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: taskKeys.detail(taskId) });
    },
  });
};

// Duplicate task mutation
export const useDuplicateTask = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: number) => duplicateTask(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
    },
  });
};

// Delete task mutation
export const useDeleteTask = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (taskId: number) => deleteTask(taskId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
      queryClient.invalidateQueries({ queryKey: taskKeys.stats() });
    },
  });
};

// Delete task files mutation
export const useDeleteTaskFiles = () => {
  return useMutation({
    mutationFn: (taskId: number) => deleteTaskFiles(taskId),
    onSuccess: () => {},
  });
};

// Get task statistics
export const useGetTaskStats = () => {
  return useQuery({
    queryKey: taskKeys.stats(),
    queryFn: () => getTaskStats(),
    // Poll fast while tasks are actively processing/queued, slow when idle
    refetchInterval: (query) => {
      const stats = query.state.data;
      if (!stats) return 5_000;
      return stats.processing > 0 || stats.queued > 0 ? 3_000 : 60_000;
    },
  });
};

// Get task results
export const useGetTaskResults = (taskId: number) => {
  return useQuery({
    queryKey: [...taskKeys.all, 'results', taskId],
    queryFn: () => getTaskResults(taskId),
    enabled: !!taskId,
  });
};
