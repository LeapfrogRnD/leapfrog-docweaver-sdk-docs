import { TaskStatus } from './task.type';

export interface ApiKey {
  id: number;
  secret_name: string;
  secret_value: string;
  created_by: number;
  is_active: boolean;
  webhook_url?: string;
  last_used_at: string | null;
  created_at: string;
}

export interface ApiKeyCreateRequest {
  secret_name: string;
  webhook_url?: string;
}

export interface ApiKeyUpdateRequest extends ApiKeyCreateRequest {
  last_used_at?: Date | null;
}

export interface ApiKeyResponse {
  id: number;
  secret_name: string;
  secret_value: string;
  webhook_url?: string;
  is_active: boolean;
}

export interface ApiKeyListResponse {
  id: number;
  secret_name: string;
  secret_value: string;
  created_by: number;
  is_active: boolean;
  last_used_at: string | null;
  created_at: string;
}

export interface ApiKeyIntegration {
  job_id: string;
  name: string;
  status: TaskStatus;
  type?: string;
  rank?: number;
  created_at: string;
}

export interface IntegrationStatsResponse {
  total: number;
  draft: number;
  ready: number;
  processing: number;
  queued: number;
  completed: number;
  failed: number;
}
