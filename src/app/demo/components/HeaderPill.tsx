import { Loader2, Check } from "lucide-react";
import type { DocumentSample } from "../types";
import React from "react";
interface HeaderPillProps {
  source: "workflow" | "upload";
  isProcessing: boolean;
  processingSource: "workflow" | "upload" | null;
  openPanel: "workflow" | "upload" | null;
  selectedDocument: DocumentSample | null;
  pendingDoc: DocumentSample | null;
  pendingFile: File | null;
}

export function HeaderPill({
  source,
  isProcessing,
  processingSource,
  openPanel,
  selectedDocument,
  pendingDoc,
  pendingFile,
}: HeaderPillProps) {
  const hasPending =
    source === "workflow" ? pendingDoc !== null : pendingFile !== null;
  const hasResult = !!selectedDocument;
  const isOpen = openPanel === source;

  if (isProcessing && processingSource === source) {
    return (
      <div 
      style={{
        padding:'0px 20px 10px 42px'
      }}>
      <span
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "4px",
          padding: "2px 8px",
          borderRadius: "100px",
          backgroundColor: "rgba(3,142,67,0.12)",
          border: "1px solid rgba(74,222,128,0.22)",
          fontSize: "10px",
          fontWeight: 500,
          color: "#4ADE80",
        }}
      >
        <Loader2
          style={{ width: "9px", height: "9px" }}
          className="animate-spin"
        />
        Running
      </span>
      </div>
    );
  }

  if (isOpen && hasResult && !hasPending) {
    return (
      <div
      style={{
        padding:'0px 20px 10px 42px'
      }}>
      <span
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "4px",
          padding: "2px 8px",
          borderRadius: "100px",
          backgroundColor: "rgba(3,142,67,0.10)",
          border: "1px solid rgba(74,222,128,0.20)",
          fontSize: "10px",
          fontWeight: 500,
          color: "#4ADE80",
        }}
      >
        <Check style={{ width: "9px", height: "9px" }} />
        Done
      </span>
      </div>
    );
  }

  if (hasPending) {
    return (
      <div style={{
        padding:'0px 20px 10px 42px'
      }}>
          
        </div>
    );
  }

  return null;
}
