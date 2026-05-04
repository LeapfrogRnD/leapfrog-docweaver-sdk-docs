import { useState, useRef } from "react";

export function useFilePreview() {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [previewMime, setPreviewMime] = useState<string | null>(null);
  const previewUrlRef = useRef<string | null>(null);

  const setPreview = (url: string | null, mime: string | null) => {
    if (previewUrlRef.current) {
      URL.revokeObjectURL(previewUrlRef.current);
    }
    previewUrlRef.current = url;
    setPreviewUrl(url);
    setPreviewMime(mime);
  };

  return { previewUrl, previewMime, setPreview };
}
