import type {
  OCRResult,
  BackendOCRResponse,
  BackendOCRResponseAny,
  OCRUploadPayload,
} from "../types";

// Access Vite env in a way that won't fail type-checking in stricter TS configs.
import { OCR_API_URL } from "@/app/constants/api";
/** Keys to skip when building the structuredFields table */
const SKIP_KEYS = new Set(["pg_no"]);

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

type BackendOCRResponseLike = {
  task_type: string;
  pipeline_id: number;
  page_count: number;
  processing_metadata: Record<string, unknown>;
  results: Array<Record<string, unknown>>;
};

function isBackendOCRResponseLike(value: unknown): value is BackendOCRResponseLike {
  return (
    isObject(value) &&
    typeof (value as any).task_type === "string" &&
    typeof (value as any).pipeline_id === "number" &&
    typeof (value as any).page_count === "number" &&
    isObject((value as any).processing_metadata) &&
    Array.isArray((value as any).results)
  );
}

function normalizeBackendResponse(raw: BackendOCRResponseAny): BackendOCRResponse {
  // Wrapped shape: { data: { ... } }
  if (isObject(raw) && "data" in raw) {
    const data = (raw as Record<string, unknown>).data;
    if (isBackendOCRResponseLike(data)) {
      return data as unknown as BackendOCRResponse;
    }
  }

  // Unwrapped shape: { results: [...] }
  if (isBackendOCRResponseLike(raw)) {
    return raw as unknown as BackendOCRResponse;
  }

  throw new Error(
    "Unexpected OCR API response shape. Expected {results:[...]} or {data:{results:[...]}}"
  );
}

/**
 * Convert a raw backend result page (one element of `results[]`) into
 * flat key/value pairs for the "Extracted Data" panel.
 */
function pageToFields(
  page: Record<string, unknown>
): Array<{ key: string; value: string; confidence: number }> {
  return Object.entries(page)
    .filter(([k]) => !SKIP_KEYS.has(k))
    .map(([k, v]) => {
      const isMissing =
        v === null ||
        v === undefined ||
        v === "" ||
        (typeof v === "string" &&
          ["<UNKNOWN>", "UNKNOWN", "N/A", "NA", "NULL"].includes(v.trim().toUpperCase()));

      return {
        key: k.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
        value: isMissing
          ? "Missing"
          : typeof v === "object"
          ? JSON.stringify(v)
          : String(v),
        confidence: 1,
      };
    });
}

/** Map the normalized backend response to the OCRResult shape used by the UI */
function mapBackendResponse(raw: BackendOCRResponse): OCRResult {
  const allFields = raw.results.flatMap(pageToFields);

  return {
    structuredFields: allFields,
    processingTime: 0,
    rawResponse: raw,
  };
}

export async function uploadDocumentForOCR(
  payload: OCRUploadPayload
): Promise<OCRResult> {
  const formData = new FormData();
  formData.append("file", payload.file);
  formData.append("task_type", payload.workflowType);
  formData.append("pipeline_id", String(payload.pipelineId));
  formData.append("json_schema", JSON.stringify(payload.jsonSchema ?? {}));

  if (payload.additionalInstruction) {
    formData.append("additional_instructions", payload.additionalInstruction);
  }

  const response = await fetch(`${OCR_API_URL}/api/process-now/`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`OCR API error ${response.status}: ${errorText}`);
  }

  const json = (await response.json()) as BackendOCRResponseAny;
  const raw = normalizeBackendResponse(json);
  return mapBackendResponse(raw);
}
