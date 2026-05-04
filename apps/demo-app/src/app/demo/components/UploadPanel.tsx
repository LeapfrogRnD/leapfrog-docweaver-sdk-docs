import React from "react";

import {
  ChevronDown,
  Upload,
  FileText,
  X,
  Loader2,
  Sparkles,
  AlertCircle,
} from "lucide-react";
import { HeaderPill } from "./HeaderPill";
import { accordionCard, accordionSep, stepBadge, runBtn } from "./styles";
import type { DocumentSample, Workflow } from "../types";

const MAX_FILE_SIZE_MB = 5;

interface UploadPanelProps {
  isOpen: boolean;
  onToggle: () => void;
  workflows: Workflow[];
  uploadWorkflow: Workflow | null;
  onUploadWorkflowSelect: (wf: Workflow | null) => void;
  pendingFile: File | null;
  onFileSelect: (file: File) => void;
  onFileRemove: () => void;
  localDragging: boolean;
  onDragOver: (e: React.DragEvent<HTMLDivElement>) => void;
  onDragLeave: () => void;
  onDrop: (e: React.DragEvent<HTMLDivElement>) => void;
  fileError: string | null;
  isProcessing: boolean;
  processingSource: "workflow" | "upload" | null;
  openPanel: "workflow" | "upload" | null;
  selectedDocument: DocumentSample | null;
  pendingDoc: DocumentSample | null;
  canRunUpload: boolean;
  onRun: () => void;
}

export function UploadPanel({
  isOpen,
  onToggle,
  workflows,
  uploadWorkflow,
  onUploadWorkflowSelect,
  pendingFile,
  onFileSelect,
  onFileRemove,
  localDragging,
  onDragOver,
  onDragLeave,
  onDrop,
  fileError,
  isProcessing,
  processingSource,
  openPanel,
  selectedDocument,
  pendingDoc,
  canRunUpload,
  onRun,
}: UploadPanelProps) {
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
        <div style={stepBadge}>02</div>
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
          Upload Your Document
        </span>
        <HeaderPill
          source="upload"
          isProcessing={isProcessing}
          processingSource={processingSource}
          openPanel={openPanel}
          selectedDocument={selectedDocument}
          pendingDoc={pendingDoc}
          pendingFile={pendingFile}
        />
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
          maxHeight: isOpen ? "720px" : "0px",
          opacity: isOpen ? 1 : 0,
          overflow: "hidden",
          transition:
            "max-height 0.30s cubic-bezier(0.4,0,0.2,1), opacity 0.20s cubic-bezier(0.4,0,0.2,1)",
        }}
      >
        <div style={accordionSep} />
        <div style={{ padding: "16px" }}>
          {/* ── Workflow selector ─────────────────────────────────── */}
          <div style={{ marginBottom: "12px" }}>
            <p
              style={{
                fontSize: "10px",
                fontWeight: 600,
                letterSpacing: "0.07em",
                textTransform: "uppercase",
                color: "rgba(148,163,184,0.40)",
                marginBottom: "6px",
              }}
            >
              Select Processing Workflow
            </p>
            <div
              style={{ display: "flex", flexDirection: "column", gap: "4px" }}
            >
              {workflows.map((wf) => {
                const WfIcon = wf.icon;
                const isSel = uploadWorkflow?.id === wf.id;
                return (
                  <button
                    key={wf.id}
                    onClick={() =>
                      !isProcessing && onUploadWorkflowSelect(isSel ? null : wf)
                    }
                    disabled={isProcessing}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                      padding: "7px 9px",
                      borderRadius: "10px",
                      width: "100%",
                      border: `1px solid ${
                        isSel
                          ? "rgba(74,222,128,0.20)"
                          : "rgba(255,255,255,0.07)"
                      }`,
                      backgroundColor: isSel
                        ? "rgba(3,142,67,0.09)"
                        : "rgba(255,255,255,0.03)",
                      cursor: isProcessing ? "not-allowed" : "pointer",
                      textAlign: "left",
                      transition: "all 0.16s cubic-bezier(0.4,0,0.2,1)",
                    }}
                  >
                    <div
                      style={{
                        width: "22px",
                        height: "22px",
                        borderRadius: "6px",
                        flexShrink: 0,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        backgroundColor: isSel
                          ? "rgba(3,142,67,0.18)"
                          : "rgba(255,255,255,0.06)",
                        border: `1px solid ${
                          isSel
                            ? "rgba(74,222,128,0.24)"
                            : "rgba(255,255,255,0.09)"
                        }`,
                      }}
                    >
                      <WfIcon
                        style={{
                          width: "12px",
                          height: "12px",
                          color: isSel ? "#4ADE80" : "rgba(148,163,184,0.45)",
                        }}
                      />
                    </div>
                    <span
                      style={{
                        flex: 1,
                        fontSize: "12px",
                        fontWeight: 500,
                        letterSpacing: "-0.01em",
                        color: isSel
                          ? "rgba(226,232,240,0.90)"
                          : "rgba(148,163,184,0.65)",
                      }}
                    >
                      {wf.title}
                    </span>
                    {isSel && (
                      <div
                        style={{
                          width: "5px",
                          height: "5px",
                          borderRadius: "50%",
                          backgroundColor: "#4ADE80",
                          flexShrink: 0,
                        }}
                      />
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          <div
            style={{
              height: "1px",
              backgroundColor: "rgba(255,255,255,0.06)",
              marginBottom: "12px",
            }}
          />

          {/* ── Inline error banner ───────────────────────────────── */}
          {fileError && (
            <div
              className="flex items-start gap-2 rounded-[10px] mb-3"
              style={{
                padding: "10px 12px",
                backgroundColor: "rgba(239,68,68,0.10)",
                border: "1px solid rgba(239,68,68,0.25)",
              }}
            >
              <AlertCircle
                style={{
                  width: "14px",
                  height: "14px",
                  color: "#f87171",
                  flexShrink: 0,
                  marginTop: "1px",
                }}
              />
              <p
                style={{ fontSize: "11px", color: "#fca5a5", lineHeight: 1.5 }}
              >
                {fileError}
              </p>
            </div>
          )}

          {/* ── Drop zone / pending file ───────────────────────────── */}
          {pendingFile ? (
            <div
              onDragOver={onDragOver}
              onDragLeave={onDragLeave}
              onDrop={onDrop}
              className="flex items-center gap-3 rounded-[12px] border border-dashed"
              style={{
                borderColor: "rgba(3,142,67,0.35)",
                backgroundColor: "rgba(3,142,67,0.06)",
                padding: "12px 14px",
              }}
            >
              <div
                className="w-9 h-9 rounded-[9px] flex items-center justify-center flex-shrink-0"
                style={{
                  background:
                    "linear-gradient(135deg, rgba(3,142,67,0.80) 0%, rgba(16,185,129,0.70) 100%)",
                  boxShadow: "0 3px 10px rgba(3,142,67,0.22)",
                }}
              >
                <FileText className="h-4 w-4" style={{ color: "#FFFFFF" }} />
              </div>
              <div className="flex-1 min-w-0">
                <p
                  className="truncate"
                  style={{
                    color: "rgba(226,232,240,0.90)",
                    fontWeight: 500,
                    fontSize: "13px",
                  }}
                >
                  {pendingFile.name}
                </p>
                <p
                  style={{
                    color: "rgba(148,163,184,0.60)",
                    fontSize: "11px",
                  }}
                >
                  {(pendingFile.size / 1024).toFixed(1)} KB
                  </p>
                  <button
                    onClick={onFileRemove}
                    disabled={isProcessing}
                    className="inline-flex items-center gap-1"
                    style={{
                      color: isProcessing ? "rgba(74,222,128,0.35)" : "#4ADE80",
                      fontSize: "11px",
                      background: "none",
                      border: "none",
                      padding: 0,
                      cursor: isProcessing ? "not-allowed" : "pointer",
                    }}
                  >
                    <X style={{ width: "10px", height: "10px" }} />
                    Remove
                  </button>
              </div>

            </div>
          ) : (
            <div
              onDragOver={onDragOver}
              onDragLeave={onDragLeave}
              onDrop={onDrop}
              className="relative rounded-[12px] border-2 border-dashed"
              style={{
                borderColor: localDragging
                  ? "rgba(3,142,67,0.50)"
                  : "rgba(255,255,255,0.10)",
                backgroundColor: localDragging
                  ? "rgba(3,142,67,0.07)"
                  : "rgba(255,255,255,0.025)",
                padding: "20px 16px",
                opacity: isProcessing ? 0.45 : 1,
                transition: "all 0.22s cubic-bezier(0.4,0,0.2,1)",
                textAlign: "center",
              }}
            >
              {localDragging && (
                <div
                  className="absolute inset-0 rounded-[10px] pointer-events-none"
                  style={{
                    background:
                      "radial-gradient(ellipse at center, rgba(3,142,67,0.09) 0%, transparent 70%)",
                  }}
                />
              )}
              <div
                className="w-10 h-10 rounded-[10px] flex items-center justify-center mx-auto mb-3 transition-all duration-200"
                style={{
                  background: localDragging
                    ? "rgba(3,142,67,0.18)"
                    : "rgba(255,255,255,0.06)",
                  border: `1px solid ${
                    localDragging
                      ? "rgba(3,142,67,0.32)"
                      : "rgba(255,255,255,0.10)"
                  }`,
                }}
              >
                <Upload
                  className="h-4 w-4"
                  style={{
                    color: localDragging ? "#4ADE80" : "rgba(148,163,184,0.55)",
                  }}
                />
              </div>
              <p
                style={{
                  color: localDragging ? "#4ADE80" : "rgba(226,232,240,0.72)",
                  fontWeight: 500,
                  fontSize: "13px",
                  marginBottom: "3px",
                  transition: "color 0.18s",
                }}
              >
                {localDragging ? "Drop to upload" : "Drag & drop your document"}
              </p>
              <p
                style={{
                  color: "rgba(148,163,184,0.42)",
                  fontSize: "11px",
                  marginBottom: "14px",
                }}
              >
                PNG, JPG · PDF (1 page max) · up to {MAX_FILE_SIZE_MB} MB
              </p>
              <input
                type="file"
                accept=".pdf,.png,.jpg,.jpeg"
                id="file-upload-dark-v2"
                className="hidden"
                disabled={isProcessing}
                onChange={(e) => {
                  const f = e.target.files?.[0];
                  if (f) onFileSelect(f);
                  e.currentTarget.value = "";
                }}
              />
              <button
                onClick={() =>
                  document.getElementById("file-upload-dark-v2")?.click()
                }
                disabled={isProcessing}
                className="transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed"
                style={{
                  padding: "7px 20px",
                  borderRadius: "100px",
                  backgroundColor: "rgba(255,255,255,0.07)",
                  border: "1px solid rgba(255,255,255,0.11)",
                  fontSize: "12px",
                  fontWeight: 500,
                  color: "rgba(226,232,240,0.72)",
                  cursor: "pointer",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = "rgba(3,142,67,0.15)";
                  e.currentTarget.style.borderColor = "rgba(74,222,128,0.28)";
                  e.currentTarget.style.color = "#4ADE80";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor =
                    "rgba(255,255,255,0.07)";
                  e.currentTarget.style.borderColor = "rgba(255,255,255,0.11)";
                  e.currentTarget.style.color = "rgba(226,232,240,0.72)";
                }}
              >
                Browse Files
              </button>
            </div>
          )}

          {/* ── Run button ────────────────────────────────────────── */}
          <div
            style={{
              marginTop: "14px",
              paddingTop: "14px",
              borderTop: "1px solid rgba(255,255,255,0.06)",
            }}
          >
            {isProcessing && processingSource === "upload" ? (
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
                    color: "rgba(74,222,74,0.85)",
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
                {!canRunUpload && (
                  <p
                    style={{
                      textAlign: "center",
                      fontSize: "11px",
                      letterSpacing: "-0.01em",
                      color: "rgba(255,255,255,0.22)",
                      marginBottom: "10px",
                    }}
                  >
                    {!pendingFile && !uploadWorkflow
                      ? "Select a workflow and upload a document"
                      : !uploadWorkflow
                      ? "Select a workflow above"
                      : "Upload a document to run"}
                  </p>
                )}
                <button
                  onClick={canRunUpload ? onRun : undefined}
                  className="active:scale-95"
                  style={runBtn(canRunUpload)}
                  onMouseEnter={(e) => {
                    if (!canRunUpload) return;
                    e.currentTarget.style.boxShadow =
                      "0 6px 28px rgba(3,142,67,0.42), 0 1px 0 rgba(255,255,255,0.12) inset";
                    e.currentTarget.style.transform = "translateY(-1px)";
                  }}
                  onMouseLeave={(e) => {
                    if (!canRunUpload) return;
                    e.currentTarget.style.boxShadow =
                      "0 4px 18px rgba(3,142,67,0.28), 0 1px 0 rgba(255,255,255,0.10) inset";
                    e.currentTarget.style.transform = "translateY(0)";
                  }}
                >
                  <Sparkles
                    style={{
                      width: "14px",
                      height: "14px",
                      opacity: canRunUpload ? 1 : 0.28,
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
