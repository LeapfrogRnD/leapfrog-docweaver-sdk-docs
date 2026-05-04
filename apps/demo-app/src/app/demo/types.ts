import type { ElementType, DragEvent } from 'react';

export interface ProcessingMetadata {
  llm_model: string;
  llm_model_provider: string;
  [key: string]: unknown;
}

export interface BackendOCRResponse {
  task_type: string;
  pipeline_id: number;
  page_count: number;
  processing_metadata: ProcessingMetadata;
  results: Array<Record<string, unknown>>;
}

export type BackendOCRResponseEnvelope = { data: BackendOCRResponse };

export type BackendOCRResponseAny = BackendOCRResponse | BackendOCRResponseEnvelope;

export interface OCRResult {
  structuredFields: Array<{ key: string; value: string; confidence: number }>;
  processingTime: number;
  rawResponse: BackendOCRResponse;
}

export interface DocumentSample {
  id: string;
  type: string;
  name: string;
  icon: ElementType;
  preview: string;
  mimeType?: string;
  result: OCRResult;
}

export type WorkflowType = 'extraction' | 'summarization' | 'classification';

export interface ExtractorField {
  name: string;
  type: 'string' | 'float' | 'int' | 'boolean' | 'array' | 'object';
  description: string;
  required?: boolean;
}

export interface ExtractionJsonSchema {
  extractors: ExtractorField[];
}

export interface ClassificationField {
  name: string;
  description: string;
}

export interface ClassificationCategory {
  category: string;
  fields: ClassificationField[];
}

export type ClassificationJsonSchema = ClassificationCategory[];

export type WorkflowJsonSchema = ExtractionJsonSchema | ClassificationJsonSchema | null;

export interface Workflow {
  id: string;
  title: string;
  subtitle: string;
  icon: ElementType;
  workflowType: WorkflowType;
  pipelineId: number;
  jsonSchema: WorkflowJsonSchema;
  additionalInstruction?: string;
  documents: DocumentSample[];
}

export interface OCRUploadPayload {
  file: File;
  workflowType: WorkflowType;
  pipelineId: number;
  jsonSchema: WorkflowJsonSchema;
  additionalInstruction?: string;
  previewUrl?: string;
}

export interface DemoVariantProps {
  workflows: Workflow[];
  selectedWorkflow: Workflow | null;
  onWorkflowSelect: (workflow: Workflow) => void;
  selectedDocument: DocumentSample | null;
  isProcessing: boolean;
  zoomLevel: number;
  copiedField: string | null;
  copiedJson: boolean;
  uploadedFile: File | null;
  uploadError: string | null;
  isDragging: boolean;
  onDocumentSelect: (doc: DocumentSample) => void;
  onFileUpload: (file: File, workflowType: WorkflowType, pipelineId: number, jsonSchema: WorkflowJsonSchema, additionalInstruction?: string, previewUrl?: string) => void;
  onDragOver: (e: DragEvent) => void;
  onDragLeave: () => void;
  onDrop: (e: DragEvent) => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onCopyField: (key: string, value: string) => void;
  onCopyJson: () => void;
  onDownloadJson: () => void;
  variant?: 'light' | 'dark';
}
