import { useState } from "react";
import type { DragEvent } from "react";
import { BookOpen, FileCode } from "lucide-react";
import { workflows } from "./workflowData";
import type {
  DocumentSample,
  Workflow,
  WorkflowType,
  WorkflowJsonSchema,
} from "./types";
import DemoPage from "./DemoPage";
import { useOCRUpload } from "./api/useOCRUpload";
import { PDFDocument } from "pdf-lib";
import { PROJECT_SUBTITLE, PROJECTNAME } from "../constants/name";
import { Footer } from "./components/Footer";
import TopBar from "../components/TopBar";
import mcp from '@/assets/mcp.png';


const MAX_FILE_SIZE_MB = 5;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;
const ALLOWED_TYPES = /^(image\/(png|jpeg)|application\/pdf)$/;

const ApplicationGuide =
  (import.meta as unknown as { env?: Record<string, string | undefined> }).env
    ?.VITE_APP_GUIDE_URL ??
  "https://leapx-marketplace-cf-template.s3.us-east-1.amazonaws.com/Leapfrog+DocWeaver+User+Manual.pdf";

export default function DemoPageController() {
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(
    null
  );
  const [selectedDocument, setSelectedDocument] =
    useState<DocumentSample | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(70);
  const [copiedField, setCopiedField] = useState<string | null>(null);
  const [copiedJson, setCopiedJson] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const ocrUpload = useOCRUpload(
    (doc) => {
      setSelectedDocument(doc);
      setIsProcessing(false);
      setZoomLevel(100);
    },
    (error) => {
      setIsProcessing(false);
      setUploadError(error.message);
    }
  );

  const handleWorkflowSelect = (workflow: Workflow) => {
    setSelectedWorkflow(workflow);
    setSelectedDocument(null);
    setUploadedFile(null);
  };

  const handleDocumentSelect = async (doc: DocumentSample) => {
    setUploadError(null);
    setUploadedFile(null);

    setIsProcessing(true);
    try {
      await new Promise((r) => setTimeout(r, 350));
    } finally {
      setSelectedDocument(doc);
      setIsProcessing(false);
      setZoomLevel(100);
    }
  };

  const handleFileUpload = async (
    file: File,
    workflowType: WorkflowType,
    pipelineId: number,
    jsonSchema: WorkflowJsonSchema,
    additionalInstruction?: string,
    previewUrl?: string
  ) => {
    setUploadError(null);

    if (!ALLOWED_TYPES.test(file.type)) {
      setUploadError("Only PNG, JPG, and PDF files are supported.");
      return;
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
      setUploadError(
        `File size ${(file.size / (1024 * 1024)).toFixed(
          1
        )} MB exceeds the ${MAX_FILE_SIZE_MB} MB limit.`
      );
      return;
    }

    if (file.type === "application/pdf") {
      try {
        const arrayBuffer = await file.arrayBuffer();
        const pdfDoc = await PDFDocument.load(arrayBuffer);
        if (pdfDoc.getPageCount() > 1) {
          setUploadError(
            `PDF has ${pdfDoc.getPageCount()} pages. Maximum allowed is 1 page.`
          );
          return;
        }
      } catch {
        setUploadError("Failed to read PDF. Please upload a valid PDF file.");
        return;
      }
    }

    setIsProcessing(true);
    setUploadedFile(file);
    ocrUpload.mutate({
      file,
      workflowType,
      pipelineId,
      jsonSchema,
      additionalInstruction,
      previewUrl,
    });
  };

  const handleDragOver = (e: DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => setIsDragging(false);

  const handleDrop = (e: DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    // Drop without workflow context is no longer supported from controller level;
    // file drops are handled inside DemoPage which knows the selected workflow.
  };

  const handleZoomIn = () => setZoomLevel((prev) => Math.min(prev + 25, 200));
  const handleZoomOut = () => setZoomLevel((prev) => Math.max(prev - 25, 50));

  const handleCopyField = (key: string, value: string) => {
    navigator.clipboard.writeText(value);
    setCopiedField(key);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const handleCopyJson = () => {
    const jsonData = selectedDocument?.result.rawResponse ?? {};
    navigator.clipboard.writeText(JSON.stringify(jsonData, null, 2));
    setCopiedJson(true);
    setTimeout(() => setCopiedJson(false), 2000);
  };

  const handleDownloadJson = () => {
    const jsonData = selectedDocument?.result.rawResponse ?? {};
    const blob = new Blob([JSON.stringify(jsonData, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${selectedDocument?.id || "document"}-extracted.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const variantProps = {
    workflows,
    selectedWorkflow,
    onWorkflowSelect: handleWorkflowSelect,
    selectedDocument,
    isProcessing,
    zoomLevel,
    copiedField,
    copiedJson,
    uploadedFile,
    uploadError,
    isDragging,
    onDocumentSelect: handleDocumentSelect,
    onFileUpload: handleFileUpload,
    onDragOver: handleDragOver,
    onDragLeave: handleDragLeave,
    onDrop: handleDrop,
    onZoomIn: handleZoomIn,
    onZoomOut: handleZoomOut,
    onCopyField: handleCopyField,
    onCopyJson: handleCopyJson,
    onDownloadJson: handleDownloadJson,
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-gray-200">
      <TopBar
        title={PROJECTNAME}
        subtitle={PROJECT_SUBTITLE}
        variant="dark"
        showLogo={true}
        externalLinks={[
          {
            href: "/integration-guide",
            label: "Integration Guide",
            icon: <FileCode className="w-3.5 h-3.5" />,
            onClick: (e) => {
              e.preventDefault();
              window.history.pushState({}, "", "/integration-guide");
              window.dispatchEvent(new PopStateEvent("popstate"));
            },
          },
          {
            href: "/mcp-guide",
            label: "MCP Guide",
            icon: <img src={mcp} alt="MCP Guide" className="w-3.5 h-3.5" />,
            onClick: (e) => {
              e.preventDefault();
              window.history.pushState({}, "", "/mcp-guide");
              window.dispatchEvent(new PopStateEvent("popstate"));
            },
          },
        ]}
      />

      <DemoPage {...variantProps} variant="dark" />

      <Footer />
    </div>
  );
}
