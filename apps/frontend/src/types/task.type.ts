export enum TaskStatus {
  DRAFT = 'draft',
  DOCUMENT_PENDING = 'doc_pending',
  DOCUMENT_UPLOADED = 'doc_uploaded',
  READY = 'ready',
  QUEUED = 'queued',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

export enum TaskType {
  EXTRACTION = 'extraction',
  CLASSIFICATION = 'classification',
}

export interface Task {
  id: number;
  name: string;
  status: TaskStatus;
  additional_instruction: string | null;
  task_type: TaskType | null;
  file_key: string | null;
  json_schema: Record<string, any> | null;
  pipeline_id: number | null;
  created_by: number | null;
  created_at: Date;
  updated_at: Date | null;
}

export interface TaskListItem {
  id: number;
  name: string;
  status: TaskStatus;
  task_type: TaskType | null;
  task_rank: number | null;
  created_by: number | null;
  created_by_fullname: string | null;
  created_at: string;
  updated_at: string;
}

export interface TaskDetail {
  id: number;
  name: string;
  status: TaskStatus;
  additional_instruction: string | null;
  task_type: TaskType | null;
  file_key: string | null;
  file_metadata: {
    file_name: string;
    file_size: number;
    content_type: string;
  } | null;
  json_schema: Record<string, any> | null;
  pipeline_id: number | null;
  pipeline_name: string | null;
  document_preview_url: string | null;
  failed_remarks: string | null;
  created_by: number | null;
  created_at: string;
  updated_at: null | string;
  enable_context: boolean | undefined;
  file_status: string | null | undefined;
}

export interface TaskNameRequest {
  task_id?: number | null;
  name: string;
}

export interface PresignedUrlRequest {
  filename: string;
  file_metadata: {
    file_size: number;
    content_type: string;
  } | null;
}

export interface PresignedUrlResponse {
  url: string;
  file_key: string | null;
}

export interface ConfirmDocUploadRequest {
  file_key: string;
}

export interface TaskConfigurationRequest {
  additional_instruction?: string;
  task_type: string;
  json_schema: Record<string, any>;
  pipeline_id: number;
  enable_context: boolean | undefined;
}

export interface TaskResponse {
  id: number;
  name: string;
  status: TaskStatus;
  additional_instruction: string | null;
  task_type: string | null;
  file_key: string | null;
  json_schema: Record<string, any> | null;
  pipeline_id: number | null;
  created_by: number | null;
  created_at: string;
  updated_at: string | null;
}

export interface TaskExecuteResponse {
  processing: number;
  queued: number;
}

export interface TaskListResponse {
  id: number;
  name: string;
  status: TaskStatus;
  task_type: string | null;
  task_rank: number | null;
  created_by: number | null;
  created_by_fullname: string | null;
  created_at: string;
  updated_at: string;
}

export interface TaskDetailResponse {
  id: number;
  name: string;
  status: TaskStatus;
  additional_instruction: string | null;
  task_type: string | null;
  file_key: string | null;
  file_metadata: {
    file_name: string;
    file_size: number;
    content_type: string;
  } | null;
  json_schema: Record<string, any> | null;
  pipeline_id: number | null;
  pipeline_name: string | null;
  document_preview_url: string | null;
  failed_remarks: string | null;
  created_by: number | null;
  created_at: string;
  updated_at: string | null;
  enable_context: boolean | undefined;
  file_status: string | null | undefined;
}

export interface TaskListFilterParams {
  status?: TaskStatus | null;
  search?: string | null;
}

export interface TaskStatsResponse {
  total: number;
  draft: number;
  ready: number;
  processing: number;
  queued: number;
  completed: number;
  failed: number;
}

export interface TaskResultResponse {
  id: number;
  name: string;
  status: TaskStatus;
  task_type: TaskType | null;
  file_metadata: Record<string, any> | null;
  document_preview_url: string | null;
  result: Record<string, any>[] | null;
  created_by: number | null;
  updated_at: number | null;
}
