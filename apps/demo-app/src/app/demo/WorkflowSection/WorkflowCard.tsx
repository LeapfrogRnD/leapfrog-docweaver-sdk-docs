import React from "react";
import WorkflowCard from "./WorkflowCard";
import DocumentPills from "./DocumentPills";
import type { Workflow, DocumentSample } from "../types";

interface Props {
  workflows: Workflow[];
  selectedWorkflow: Workflow | null;
  selectedDocument: DocumentSample | null;
  uploadedFile: File | null;
  isProcessing: boolean;
  onWorkflowSelect: (w: Workflow) => void;
  onDocumentSelect: (doc: DocumentSample) => void;
}

export default function WorkflowSection({
  workflows,
  selectedWorkflow,
  selectedDocument,
  uploadedFile,
  isProcessing,
  onWorkflowSelect,
  onDocumentSelect,
}: Props) {

  return (
    <div className="space-y-5">

      {/* Section header */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-green-600/10 border border-green-600/30">
          <span className="w-1.5 h-1.5 rounded-full bg-green-500"/>
          <span className="text-xs text-green-400 font-medium">
            Sample Workflows
          </span>
        </div>

        <div className="flex-1 h-px bg-white/10"/>
      </div>

      {/* Workflow Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">

        {workflows.map((workflow) => (
          <WorkflowCard
            key={workflow.id}
            workflow={workflow}
            selected={selectedWorkflow?.id === workflow.id}
            disabled={isProcessing}
            onClick={() => onWorkflowSelect(workflow)}
          />
        ))}

      </div>

      {/* Documents */}
      {selectedWorkflow && (
        <DocumentPills
          workflow={selectedWorkflow}
          selectedDocument={selectedDocument}
          uploadedFile={uploadedFile}
          isProcessing={isProcessing}
          onSelect={onDocumentSelect}
        />
      )}

    </div>
  );
}