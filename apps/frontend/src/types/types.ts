import { TaskStatus } from './task.type';

export interface User {
  email: string;
  name: string;
}

export interface Document {
  id: string;
  name: string;
  size: number;
  type: string;
  file: File;
  uploadedAt: Date;
}

export interface PipelineConfig {
  useDefaultPipeline: boolean;
  documentClassification: boolean;
  customFields?: string[];
  selectedPipelineId?: string;
}

export interface Pipeline {
  id: string;
  name: string;
  description: string;
  isDefault: boolean;
  ocrProvider: 'tesseract' | 'google-cloud-vision' | 'aws-textract' | 'azure' | 'abbyy' | 'custom';
  parsingMethod: 'rule-based' | 'template-matching' | 'ml' | 'llm-based' | 'hybrid';
  llmModel:
    | 'gpt-4'
    | 'gpt-3.5'
    | 'claude-3-opus'
    | 'claude-3-sonnet'
    | 'claude-3-haiku'
    | 'gemini-pro'
    | 'llama-3'
    | 'custom';
  systemPrompt?: string;
  extractionFields: ExtractionField[];
  classification?: Classification;
  settings: PipelineSettings;
  createdAt: Date;
  updatedAt: Date;
}

export interface ExtractionField {
  id: string;
  key: string;
  title: string;
  type:
    | 'text'
    | 'number'
    | 'date'
    | 'email'
    | 'phone'
    | 'currency'
    | 'boolean'
    | 'select'
    | 'multi-select';
  required: boolean;
  description?: string;
  options?: string[];
}

export interface Classification {
  key: string;
  title: string;
  description: string;
}

export interface PipelineSettings {
  enableClassification: boolean;
  enableConfidenceScore: boolean;
  confidenceThreshold: number;
  language: string;
  outputFormat: 'json' | 'csv' | 'xml';
}

export interface OcrResult {
  id: string;
  task_name: string;
  task_type: string;
  documentId: string;
  documentName: string;
  status: TaskStatus;
  extractedText: string;
  structuredData: Record<string, unknown> | Record<string, unknown>[];
  pages?: PageResult[];
  rawText?: string;
  updatedAt: string;
}

export interface PageResult {
  pageNumber: number;
  text: string;
  fields: Record<string, unknown>;
}

export interface Toast {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
}

export interface UserProfile {
  id: string;
  fullName: string;
  email: string;
  company?: string;
  phoneNumber?: string;
  accountStatus: 'Active' | 'Inactive';
  memberSince: Date;
  plan: string;
  passwordLastChanged: Date | null;
  twoFactorEnabled: boolean;
}

export enum Roles {
  Admin = 'admin',
  User = 'user',
  Superadmin = 'superadmin',
}

export const RoleRank: Record<Roles, number> = {
  [Roles.User]: 1,
  [Roles.Admin]: 2,
  [Roles.Superadmin]: 3,
};

export interface GenericResponse<T> {
  data: T;
  message?: string;
}

export interface PaginationMetadata {
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  total_items: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  metadata: PaginationMetadata;
}
