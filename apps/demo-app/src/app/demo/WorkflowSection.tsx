import React, { useState, useEffect } from 'react';
import type { Workflow, DocumentSample } from './types';

interface WorkflowSectionProps {
  workflows: Workflow[];
  selectedWorkflow: Workflow | null;
  selectedDocument: DocumentSample | null;
  uploadedFile: File | null;
  isProcessing: boolean;
  onWorkflowSelect: (w: Workflow) => void;
  onDocumentSelect: (doc: DocumentSample) => void;
  variant: 'dark';
  compact?: boolean;
}

export default function WorkflowSection({
  workflows,
  selectedWorkflow,
  selectedDocument,
  uploadedFile,
  isProcessing,
  onWorkflowSelect,
  onDocumentSelect,
  compact,
}: WorkflowSectionProps) {
  
  // LOCAL STATE: This ensures the UI highlights IMMEDIATELY when clicked, 
  // without waiting for the "run" or the parent prop to change.
  const [localSelectedId, setLocalSelectedId] = useState<string | number | null>(null);

  // Sync local state if the parent prop changes (e.g., when a workflow finishes)
  useEffect(() => {
    if (selectedDocument) {
      setLocalSelectedId(selectedDocument.id);
    }
  }, [selectedDocument]);

  // Fallback for group highlighting
  const activeWorkflowId = selectedWorkflow?.id || workflows[0]?.id;

  if (compact) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {workflows.map((workflow) => {
          const Icon = workflow.icon;
          const isSelectedGroup = activeWorkflowId === workflow.id;

          return (
            <div key={workflow.id} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              
              {/* Workflow Header (Static Text) */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '4px 0' }}>
                <div style={{ color: isSelectedGroup ? '#4ADE80' : '#475569' }}>
                  <Icon size={14} />
                </div>
                <span style={{
                  fontSize: '11px',
                  fontWeight: 600,
                  textTransform: 'uppercase',
                  letterSpacing: '0.06em',
                  color: isSelectedGroup ? '#F8FAFC' : '#475569',
                }}>
                  {workflow.title}
                </span>
              </div>

              {/* Document List */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                {workflow.documents.map((doc) => {
                  const DocIcon = doc.icon;
                  
                  // HIGHLIGHT LOGIC: Check local state first for instant feedback, then the prop
                  const isDocSelected = localSelectedId === doc.id || selectedDocument?.id === doc.id;
                  
                  return (
                    <button
                      key={doc.id}
                      type="button"
                      disabled={isProcessing}
                      onClick={() => {
                        if (!isProcessing) {
                          setLocalSelectedId(doc.id); // 1. Instant local highlight
                          onWorkflowSelect(workflow); // 2. Update parent group
                          onDocumentSelect(doc);      // 3. Trigger parent logic
                        }
                      }}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        width: '100%',
                        padding: '10px 12px',
                        borderRadius: '8px',
                        cursor: isProcessing ? 'not-allowed' : 'pointer',
                        textAlign: 'left',
                        transition: 'all 0.1s ease-out',
                        
                        // Styles
                        backgroundColor: isDocSelected 
                          ? 'rgba(3, 142, 67, 0.25)' 
                          : 'transparent',
                        border: `1px solid ${isDocSelected 
                          ? 'rgba(74, 222, 128, 0.5)' 
                          : 'rgba(255, 255, 255, 0.04)'}`,
                      }}
                    >
                      <DocIcon size={14} style={{ 
                        color: isDocSelected ? '#4ADE80' : '#64748B' 
                      }} />
                      
                      <span style={{
                        fontSize: '12px',
                        fontWeight: isDocSelected ? 600 : 400,
                        flex: 1,
                        color: isDocSelected ? '#FFFFFF' : '#94A3B8',
                      }}>
                        {doc.type}
                      </span>

                      {isDocSelected && (
                        <div style={{
                          width: '6px',
                          height: '6px',
                          borderRadius: '50%',
                          backgroundColor: '#4ADE80',
                          boxShadow: '0 0 10px #4ADE80'
                        }} />
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    );
  }

  return null; 
}