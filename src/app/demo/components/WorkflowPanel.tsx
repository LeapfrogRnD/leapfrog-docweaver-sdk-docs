import React from "react";

import { ChevronDown, Loader2, Sparkles } from "lucide-react";
import WorkflowSection from "../WorkflowSection";
import { HeaderPill } from "./HeaderPill";
import { accordionCard, accordionSep, stepBadge, runBtn } from "./styles";
import type { DocumentSample, Workflow } from "../types";

interface WorkflowPanelProps {
  isOpen: boolean;
  onToggle: () => void;
  workflows: Workflow[];
  selectedWorkflow: Workflow | null;
  onWorkflowSelect: (wf: Workflow) => void;
  wsSelectedDoc: DocumentSample | null;
  pendingDoc: DocumentSample | null;
  pendingFile: File | null;
  uploadedFile: File | null;
  isProcessing: boolean;
  processingSource: "workflow" | "upload" | null;
  openPanel: "workflow" | "upload" | null;
  selectedDocument: DocumentSample | null;
  canRunWorkflow: boolean;
  onDocumentSelect: (doc: DocumentSample) => void;
  onRun: () => void;
}

export function WorkflowPanel({
  isOpen,
  onToggle,
  workflows,
  selectedWorkflow,
  onWorkflowSelect,
  wsSelectedDoc,
  pendingDoc,
  pendingFile,
  uploadedFile,
  isProcessing,
  processingSource,
  openPanel,
  selectedDocument,
  canRunWorkflow,
  onDocumentSelect,
  onRun,
}: WorkflowPanelProps) {
  return (
    <div style={accordionCard(isOpen)}>
      <button
        onClick={onToggle}
        style={{
          width: "100%",
          display: "flex",
          alignItems: "center",
          gap: "10px",
          padding: "14px 16px",
          background: "none",
          border: "none",
          cursor: "pointer",
          textAlign: "left",
        }}
        onMouseEnter={(e) => {
          if (!isOpen)
            e.currentTarget.style.backgroundColor = "rgba(255,255,255,0.025)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = "transparent";
        }}
      >
          <div style={stepBadge}>01</div>
        <span
            style={{
              flex: 1,
              fontSize: "13px",
              fontWeight: 500,
              letterSpacing: "-0.01em",
            color: isOpen ? "rgba(226,232,240,0.90)" : "rgba(148,163,184,0.72)",
              transition: "color 0.18s",
            }}
          >
            Use a Sample Workflow
        </span>
        
        <ChevronDown
          style={{
            width: "14px",
            height: "14px",
            flexShrink: 0,
            marginLeft: "4px",
            color: "rgba(148,163,184,0.40)",
            transform: isOpen ? "rotate(180deg)" : "rotate(0deg)",
            transition: "transform 0.22s cubic-bezier(0.4,0,0.2,1)",
          }}
        />
      </button>

      <div
        style={{
          maxHeight: isOpen ? "660px" : "0px",
          opacity: isOpen ? 1 : 0,
          overflow: "hidden",
          transition:
            "max-height 0.26s cubic-bezier(0.4,0,0.2,1), opacity 0.20s cubic-bezier(0.4,0,0.2,1)",
        }}
      >
        <HeaderPill
          source="workflow"
          isProcessing={isProcessing}
          processingSource={processingSource}
          openPanel={openPanel}
          selectedDocument={selectedDocument}
          pendingDoc={pendingDoc}
          pendingFile={pendingFile}
        />
        {/* <div style={accordionSep} /> */}
        <div style={{ padding: "16px" }}>
          <WorkflowSection
            workflows={workflows}
            selectedWorkflow={selectedWorkflow}
            selectedDocument={wsSelectedDoc}
            uploadedFile={pendingFile || uploadedFile}
            isProcessing={isProcessing}
            onWorkflowSelect={onWorkflowSelect}
            onDocumentSelect={onDocumentSelect}
            variant="dark"
            compact
          />

          <div
            style={{
              marginTop: "16px",
              paddingTop: "14px",
              borderTop: "1px solid rgba(255,255,255,0.06)",
            }}
          >
            {isProcessing && processingSource === "workflow" ? (
              <div
                className="flex items-center justify-center gap-2.5 py-2.5 rounded-full"
                style={{
                  backgroundColor: "rgba(3,142,67,0.10)",
                  border: "1px solid rgba(74,222,128,0.20)",
                }}
              >
                <Loader2
                  className="animate-spin"
                  style={{ width: "14px", height: "14px", color: "#4ADE80" }}
                />
                <span
                  style={{
                    color: "rgba(74,222,128,0.85)",
                    fontSize: "13px",
                    fontWeight: 500,
                    letterSpacing: "-0.01em",
                  }}
                >
                  Analysing…
                </span>
              </div>
            ) : (
              <>
                {!canRunWorkflow && (
                  <p
                    style={{
                      textAlign: "center",
                      fontSize: "11px",
                      letterSpacing: "-0.01em",
                      color: "rgba(255,255,255,0.22)",
                      marginBottom: "10px",
                    }}
                  >
                    Select a workflow and document to run
                  </p>
                )}
                <button
                  onClick={canRunWorkflow ? onRun : undefined}
                  className="active:scale-95"
                  style={runBtn(canRunWorkflow)}
                  onMouseEnter={(e) => {
                    if (!canRunWorkflow) return;
                    e.currentTarget.style.boxShadow =
                      "0 6px 28px rgba(3,142,67,0.42), 0 1px 0 rgba(255,255,255,0.12) inset";
                    e.currentTarget.style.transform = "translateY(-1px)";
                  }}
                  onMouseLeave={(e) => {
                    if (!canRunWorkflow) return;
                    e.currentTarget.style.boxShadow =
                      "0 4px 18px rgba(3,142,67,0.28), 0 1px 0 rgba(255,255,255,0.10) inset";
                    e.currentTarget.style.transform = "translateY(0)";
                  }}
                >
                  <Sparkles
                    style={{
                      width: "14px",
                      height: "14px",
                      opacity: canRunWorkflow ? 1 : 0.28,
                    }}
                  />
                  Run Workflow Analysis
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
