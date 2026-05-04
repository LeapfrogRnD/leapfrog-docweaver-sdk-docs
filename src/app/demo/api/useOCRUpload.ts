import { useMutation } from "@tanstack/react-query";
import { FileText } from "lucide-react";
import { uploadDocumentForOCR } from "./ocrApi";
import type { DocumentSample, OCRUploadPayload } from "../types";

export function useOCRUpload(
  onSuccess: (doc: DocumentSample) => void,
  onError?: (error: Error) => void
) {
  return useMutation({
    mutationFn: (payload: OCRUploadPayload) => uploadDocumentForOCR(payload),
    onSuccess: (result, payload) => {
      const preview = payload.previewUrl ?? URL.createObjectURL(payload.file);
      const doc: DocumentSample = {
        id: "uploaded",
        type: "Uploaded Document",
        name: payload.file.name,
        icon: FileText,
        preview,
        mimeType: payload.file.type,
        result,
      };
      onSuccess(doc);
    },
    onError: (error: Error) => {
      onError?.(error);
    },
  });
}
