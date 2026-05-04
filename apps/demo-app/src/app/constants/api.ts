export const OCR_API_URL =
  (import.meta as unknown as { env?: Record<string, string | undefined> }).env
    ?.VITE_OCR_API_URL ?? "http://localhost:8000";