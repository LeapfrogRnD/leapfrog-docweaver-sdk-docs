import {
  Task,
  TaskListItem,
  TaskDetail,
  TaskResponse,
  TaskListResponse,
  TaskDetailResponse,
  TaskStatus,
  TaskType,
  TaskResultResponse,
  TaskExecuteResponse,
} from '@/types/task.type';
import { OcrResult, PageResult } from '@/types/types';
import { formatDate } from '@/utils';

/**
 * Maps task list response from backend to frontend format
 */
export const mapTaskListResponse = (task: TaskListResponse): TaskListItem => {
  return {
    id: task.id,
    name: task.name,
    status: task.status as TaskStatus,
    task_type: task.task_type ? (task.task_type as TaskType) : null,
    task_rank: task.task_rank,
    created_by: task.created_by,
    created_by_fullname: task.created_by_fullname,
    created_at: formatDate(task.created_at, true),
    updated_at: formatDate(task.updated_at, true),
  };
};

/**
 * Maps task response from backend to frontend Task format
 */
export const mapTaskResponse = (response: TaskResponse): Task => {
  return {
    id: response.id,
    name: response.name,
    status: response.status as TaskStatus,
    additional_instruction: response.additional_instruction,
    task_type: response.task_type ? (response.task_type as TaskType) : null,
    file_key: response.file_key,
    json_schema: response.json_schema,
    pipeline_id: response.pipeline_id,
    created_by: response.created_by,
    created_at: new Date(response.created_at),
    updated_at: response.updated_at ? new Date(response.updated_at) : null,
  };
};

export const mapTaskExecuteResponse = (response: TaskExecuteResponse): TaskExecuteResponse => {
  return {
    processing: response.processing,
    queued: response.queued,
  };
};

/**
 * Maps task detail response from backend to frontend format
 */
export const mapTaskDetailResponse = (response: TaskDetailResponse): TaskDetail => {
  return {
    id: response.id,
    name: response.name,
    status: response.status as TaskStatus,
    additional_instruction: response.additional_instruction,
    task_type: response.task_type ? (response.task_type as TaskType) : null,
    file_key: response.file_key,
    file_metadata: response.file_metadata,
    json_schema: response.json_schema,
    pipeline_id: response.pipeline_id,
    pipeline_name: response.pipeline_name,
    document_preview_url: response.document_preview_url,
    failed_remarks: response.failed_remarks,
    created_by: response.created_by,
    created_at: response.created_at,
    updated_at: response.updated_at,
    // Ensure enable_context is always a boolean (coerce null/undefined to false)
    enable_context: !!response.enable_context,
    file_status: response.file_status,
  };
};

/**
 * Maps task result response from backend to frontend OcrResult format
 */
export const mapTaskResultResponse = (response: TaskResultResponse): OcrResult => {
  // Extract text from result array if available
  const extractedText = response.result?.length
    ? response.result.map((item) => JSON.stringify(item)).join('\n')
    : 'No extracted text available';

  // Always provide a non-null structuredData value; prefer array form
  const structuredData = response.result ?? [];

  // Create pages from result array
  const pages: PageResult[] =
    response.result?.map((item, index) => ({
      pageNumber: index + 1,
      text: JSON.stringify(item),
      fields: item as Record<string, unknown>,
    })) || [];

  return {
    id: response.id.toString(),
    task_name: response.name,
    task_type: response.task_type as string,
    documentId: response.id.toString(),
    documentName: response?.file_metadata?.file_name || 'Unknown Document',
    status: response.status,
    updatedAt: formatDate(response.updated_at, true),
    extractedText,
    structuredData,
    pages,
  };
};
