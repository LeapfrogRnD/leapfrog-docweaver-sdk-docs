import type { LucideIcon } from "lucide-react";

export interface StructuredField {
  key: string;
  value: string;
  confidence: number;
}

export interface OCRResult {
  rawText: string;
  structuredFields: StructuredField[];
  processingTime: number;
}

export interface DocumentSample {
  id: string;
  type: string;
  name: string;

  icon: LucideIcon;
  preview?: string;

  result: OCRResult;
}

export type WorkflowType = 'extraction' | 'summarization' | 'classification';

export interface WorkflowJsonSchema {
  [field: string]: {
    type: string;
    description: string;
  };
}

export interface Workflow {
  id: string;
  title: string;
  subtitle?: string;

  icon: LucideIcon;
  workflowType: WorkflowType;
  jsonSchema: WorkflowJsonSchema;

  documents: DocumentSample[];
}

export interface WorkflowSectionProps {
  workflows: Workflow[];

  selectedWorkflow: Workflow | null;
  selectedDocument: DocumentSample | null;

  uploadedFile: File | null;
  isProcessing: boolean;

  onWorkflowSelect: (workflow: Workflow) => void;
  onDocumentSelect: (doc: DocumentSample) => void;
}

export interface WorkflowCardProps {
  workflow: Workflow;
  selected: boolean;
  disabled?: boolean;

  onClick: () => void;
}

export interface DocumentPillsProps {
  workflow: Workflow;

  selectedDocument: DocumentSample | null;
  uploadedFile: File | null;

  isProcessing: boolean;

  onSelect: (doc: DocumentSample) => void;
}

export interface DemoVariantProps {
  workflows: Workflow[];

  selectedWorkflow: Workflow | null;
  selectedDocument: DocumentSample | null;

  uploadedFile: File | null;
  isDragging: boolean;
  isProcessing: boolean;

  zoomLevel: number;

  copiedField: string | null;
  copiedJson: boolean;

  onWorkflowSelect: (workflow: Workflow) => void;
  onDocumentSelect: (doc: DocumentSample) => void;
  onFileUpload: (file: File, workflowType: WorkflowType, jsonSchema: WorkflowJsonSchema) => void;

  onZoomIn: () => void;
  onZoomOut: () => void;

  onCopyField: (key: string, value: string) => void;
  onCopyJson: () => void;
  onDownloadJson: () => void;

  onDragOver: (e: React.DragEvent) => void;
  onDragLeave: () => void;
  onDrop: (e: React.DragEvent) => void;
}