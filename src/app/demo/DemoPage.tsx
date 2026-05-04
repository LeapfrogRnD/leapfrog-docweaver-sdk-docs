import React, { useState, useRef, useEffect } from "react";
import { PDFDocument } from "pdf-lib";
import { HeroSection } from "../components/HeroSection";
import { WorkflowPanel } from "./components/WorkflowPanel";
import { UploadPanel } from "./components/UploadPanel";
import { ResultsWorkspace } from "./components/ResultsWorkspace";
import { useFilePreview } from "./hooks/useFilePreview";
import type { DemoVariantProps, DocumentSample } from "./types";
import { PROJECTNAME } from "../constants/name";

const MAX_FILE_SIZE_MB = 5;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;
const ALLOWED_TYPES = /^(image\/(png|jpeg)|application\/pdf)$/;

export default function DemoPage({
  workflows,
  selectedWorkflow,
  onWorkflowSelect,
  selectedDocument,
  isProcessing,
  zoomLevel,
  copiedField,
  uploadedFile,
  onDocumentSelect,
  onFileUpload,
  onZoomIn,
  onZoomOut,
  onCopyField,
}: DemoVariantProps) {
  const [pendingDoc, setPendingDoc] = useState<DocumentSample | null>(null);
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const [localDragging, setLocalDragging] = useState(false);
  const [uploadWorkflow, setUploadWorkflow] = useState<
    (typeof workflows)[0] | null
  >(null);
  const [processingSource, setProcessingSource] = useState<
    "workflow" | "upload" | null
  >(null);
  const [openPanel, setOpenPanel] = useState<"workflow" | "upload" | null>(
    "workflow"
  );
  const [fileError, setFileError] = useState<string | null>(null);

  const { previewUrl, previewMime, setPreview } = useFilePreview();
  const demoRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isProcessing) setProcessingSource(null);
  }, [isProcessing]);

  const canRunWorkflow = pendingDoc !== null && !isProcessing;
  const canRunUpload =
    pendingFile !== null && uploadWorkflow !== null && !isProcessing;

  const wsSelectedDoc = selectedDocument;

  const macWindowShell = (title: string, child: React.ReactNode) => (
    <div className="flex h-[720px] flex-col overflow-hidden rounded-[20px] border border-white/10 bg-white/[0.04] backdrop-blur-[24px] shadow-[0_8px_28px_rgba(0,0,0,0.34),inset_0_1px_0_rgba(255,255,255,0.04)]">
      <div className="flex shrink-0 items-center gap-2.5 border-b border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.06)_0%,rgba(255,255,255,0.02)_100%)] px-3.5 py-2.5">
        <div className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57] shadow-[inset_0_0_0_1px_rgba(0,0,0,0.18)]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e] shadow-[inset_0_0_0_1px_rgba(0,0,0,0.18)]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#28c840] shadow-[inset_0_0_0_1px_rgba(0,0,0,0.18)]" />
        </div>
        <div className="flex-1 pr-6 text-center text-[11px] font-semibold uppercase tracking-[0.06em] text-slate-200/70">
          {title}
        </div>
      </div>
      <div className="min-h-0 flex-1 p-2.5">{child}</div>
    </div>
  );

  const togglePanel = (panel: "workflow" | "upload") => {
    if (openPanel === panel) {
      setOpenPanel(null);
    } else {
      setOpenPanel(panel);
      if (panel === "upload") setPendingDoc(null);
      if (panel === "workflow") {
        setPendingFile(null);
        setFileError(null);
      }
    }
  };

  const handleLocalDocSelect = (doc: DocumentSample) => {
    if (isProcessing) return;
    setPendingDoc(doc);
    setPendingFile(null);
  };

  const validatePdfPages = async (file: File): Promise<boolean> => {
    try {
      const arrayBuffer = await file.arrayBuffer();
      const pdfDoc = await PDFDocument.load(arrayBuffer);
      const numPages = pdfDoc.getPageCount();
      if (numPages > 1) {
        setFileError(`PDF has ${numPages} pages. Maximum allowed is 1 page.`);
        return false;
      }
      return true;
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      if (msg.includes("password") || msg.toLowerCase().includes("encrypted")) {
        setFileError(
          "This PDF is password-protected. Please upload an unlocked PDF."
        );
      } else if (
        msg.includes("Invalid PDF") ||
        msg.includes("Missing PDF") ||
        msg.includes("Unexpected") ||
        msg.includes("startxref")
      ) {
        setFileError(
          "The file appears to be corrupt or is not a valid PDF. Please try a different file."
        );
      } else {
        setFileError(
          "Could not read the PDF. Make sure the file is a valid, unlocked PDF and try again."
        );
      }
      return false;
    }
  };

  const handleLocalFileSelect = async (file: File) => {
    if (isProcessing) return;
    setFileError(null);

    if (!ALLOWED_TYPES.test(file.type)) {
      setFileError("Only PNG, JPG, and PDF files are supported.");
      return;
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
      setFileError(
        `File size ${(file.size / (1024 * 1024)).toFixed(
          1
        )} MB exceeds the ${MAX_FILE_SIZE_MB} MB limit.`
      );
      return;
    }

    if (file.type === "application/pdf") {
      const valid = await validatePdfPages(file);
      if (!valid) return;
    }

    const url = URL.createObjectURL(file);

    setPendingFile(file);
    setPendingDoc(null);
    setPreview(url, file.type);

    console.log("Preview URL:", url);
  };

  const handleLocalDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setLocalDragging(true);
  };
  const handleLocalDragLeave = () => setLocalDragging(false);
  const handleLocalDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setLocalDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) handleLocalFileSelect(f);
  };

  const handleRun = (source: "workflow" | "upload") => {
    if (isProcessing) return;
    setProcessingSource(source);
    if (source === "workflow" && pendingDoc) {
      onDocumentSelect(pendingDoc);
      setPendingDoc(null);
    }
    if (source === "upload" && pendingFile && uploadWorkflow) {
      const stablePreviewUrl = previewUrl
        ? `${previewUrl}#toolbar=0&navpanes=0&scrollbar=0`
        : undefined;

      onFileUpload(
        pendingFile,
        uploadWorkflow.workflowType,
        uploadWorkflow.pipelineId,
        uploadWorkflow.jsonSchema,
        uploadWorkflow.additionalInstruction,
        stablePreviewUrl
      );
      // NOTE: keep pendingFile so the Upload panel continues showing it.
    }
  };

  return (
    <div>
      <HeroSection
        variant="dark"
        onTryDemo={() =>
          demoRef.current?.scrollIntoView({
            behavior: "smooth",
            block: "start",
          })
        }
      />

      <div
        ref={demoRef}
        className="mx-auto max-w-7xl px-6 pb-[var(--footer-height)]"
      >
        <div className="text-center mb-8">
          <h2 className="mb-2 text-[28px] leading-[1.2] tracking-[-0.02em] text-white">
            Try the {PROJECTNAME} Demo
          </h2>
          <p className="text-[15px] tracking-[-0.01em] text-slate-400/70">
            Choose a sample workflow or upload your own document, then run the
            analysis
          </p>
        </div>

        {macWindowShell(
          "",
          <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-5 h-full min-h-0">
            {/* ══ LEFT: Accordion Sidebar ══ */}
            <div className="min-h-0 flex flex-col gap-1.5 border-r border-white/10 pr-2.5">
              <div className="mb-0.5 flex items-center gap-2 px-1 pt-1 pb-2.5">
                <span className="text-[10px] font-semibold uppercase tracking-[0.08em] text-slate-400/40">
                  Input Method
                </span>
                <div className="h-px flex-1 bg-white/[0.06]" />
              </div>

              <WorkflowPanel
                isOpen={openPanel === "workflow"}
                onToggle={() => togglePanel("workflow")}
                workflows={workflows}
                selectedWorkflow={selectedWorkflow}
                onWorkflowSelect={onWorkflowSelect}
                wsSelectedDoc={wsSelectedDoc}
                pendingDoc={pendingDoc}
                pendingFile={pendingFile}
                uploadedFile={uploadedFile}
                isProcessing={isProcessing}
                processingSource={processingSource}
                openPanel={openPanel}
                selectedDocument={selectedDocument}
                canRunWorkflow={canRunWorkflow}
                onDocumentSelect={handleLocalDocSelect}
                onRun={() => handleRun("workflow")}
              />

              <UploadPanel
                isOpen={openPanel === "upload"}
                onToggle={() => togglePanel("upload")}
                workflows={workflows}
                uploadWorkflow={uploadWorkflow}
                onUploadWorkflowSelect={setUploadWorkflow}
                pendingFile={pendingFile}
                onFileSelect={handleLocalFileSelect}
                onFileRemove={() => {
                  setPendingFile(null);
                  setFileError(null);
                  setPreview(null, null);
                }}
                localDragging={localDragging}
                onDragOver={handleLocalDragOver}
                onDragLeave={handleLocalDragLeave}
                onDrop={handleLocalDrop}
                fileError={fileError}
                isProcessing={isProcessing}
                processingSource={processingSource}
                openPanel={openPanel}
                selectedDocument={selectedDocument}
                pendingDoc={pendingDoc}
                canRunUpload={canRunUpload}
                onRun={() => handleRun("upload")}
              />
            </div>

            {/* ══ RIGHT: Results Workspace ══ */}
            <div className="min-h-0 min-w-0 flex-1">
              <ResultsWorkspace
                selectedDocument={wsSelectedDoc}
                isProcessing={isProcessing}
                previewUrl={previewUrl}
                previewMime={previewMime}
                zoomLevel={zoomLevel}
                copiedField={copiedField}
                onZoomIn={onZoomIn}
                onZoomOut={onZoomOut}
                onCopyField={onCopyField}
              />
            </div>
          </div>
        )}
      </div>

      
      <style>{`
          @keyframes fadeSlideIn {
            from { opacity: 0; transform: translateY(8px); }
            to   { opacity: 1; transform: translateY(0);   }
          }
          .skeleton-shimmer {
            background: linear-gradient(90deg, rgba(255,255,255,0.06) 25%, rgba(255,255,255,0.12) 50%, rgba(255,255,255,0.06) 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
          }
          @keyframes shimmer {
            from { background-position: 200% 0; }
            to { background-position: -200% 0; }
          }
        `}</style>
    </div>
  );
}
