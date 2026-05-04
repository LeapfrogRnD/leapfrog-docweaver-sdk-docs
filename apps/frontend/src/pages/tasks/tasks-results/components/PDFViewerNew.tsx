// src/components/PdfViewer.tsx

'use client';

import { useState, useMemo, useEffect, useRef } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button, Skeleton } from '@/components/ui';
// Import the main components
import { Document, Page, pdfjs } from 'react-pdf';

// Import the CSS for the annotation and text layers
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';

// --- Worker Setup ---
// Keep worker version aligned with runtime PDF.js API version.
pdfjs.GlobalWorkerOptions.workerSrc = `https://unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

// --- Component Props Interface ---
interface PdfViewerProps {
  fileUrl?: string;
  fileBytes?: string; // Base64 encoded PDF bytes
  onPageChange?: (page: number) => void;
  onPageRenderStatusChange?: (isRendered: boolean, page: number) => void;
}

// Create a PDF loading skeleton component
function PdfLoadingSkeleton() {
  return (
    <div className="flex items-center justify-center h-full">
      <div className="w-full max-w-md space-y-4 p-4">
        {/* Header area skeleton */}
        <div className="space-y-3">
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
        </div>

        {/* Main content area skeleton */}
        <div className="space-y-3">
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-3 w-5/6" />
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-3 w-4/5" />
        </div>

        {/* Another paragraph */}
        <div className="space-y-3 mt-6">
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-3 w-3/4" />
          <Skeleton className="h-3 w-full" />
        </div>

        {/* Footer area */}
        <div className="space-y-2 mt-8">
          <Skeleton className="h-3 w-2/3" />
          <Skeleton className="h-3 w-1/2" />
        </div>

        {/* Loading text */}
        <div className="text-center mt-6">
          <Skeleton className="h-4 w-32 mx-auto mb-2" />
        </div>
      </div>
    </div>
  );
}

export function PdfViewer({
  fileUrl,
  fileBytes,
  onPageChange,
  onPageRenderStatusChange,
}: PdfViewerProps) {
  const [numPages, setNumPages] = useState<number | null>(null);
  const [pageNumber, setPageNumber] = useState<number>(1);
  const [error, setError] = useState<string | null>(null);
  const onPageRenderStatusChangeRef = useRef(onPageRenderStatusChange);

  useEffect(() => {
    onPageRenderStatusChangeRef.current = onPageRenderStatusChange;
  }, [onPageRenderStatusChange]);

  // Keep options stable to prevent unnecessary Document re-initialization.
  const options = useMemo(() => ({}), []);

  // Convert base64 to data URL for react-pdf
  const pdfSource = useMemo(() => {
    if (fileBytes) {
      // If we have file bytes, create a data URL
      return `data:application/pdf;base64,${fileBytes}`;
    } else if (fileUrl) {
      // Otherwise use the file URL
      return fileUrl;
    }
    return null;
  }, [fileBytes, fileUrl]);

  useEffect(() => {
    onPageRenderStatusChangeRef.current?.(false, pageNumber);
  }, [pageNumber, pdfSource]);

  /**
   * This function is called when the document is successfully loaded.
   */
  function onDocumentLoadSuccess({ numPages }: { numPages: number }): void {
    setNumPages(numPages);
    setPageNumber(1);
    if (onPageChange) onPageChange(1);
    setError(null);
  }

  /**
   * This function is called when the document fails to load.
   */
  function onDocumentLoadError(error: Error): void {
    console.error('PDF loading error:', error);
    setError(error.message);
    onPageRenderStatusChangeRef.current?.(true, pageNumber);
  }

  // --- Navigation Functions ---
  function goToPrevPage() {
    setPageNumber((prevPageNumber) => {
      const newPageNumber = Math.max(prevPageNumber - 1, 1);
      if (onPageChange) onPageChange(newPageNumber);
      return newPageNumber;
    });
  }

  function goToNextPage() {
    setPageNumber((prevPageNumber) => {
      const newPageNumber = numPages ? Math.min(prevPageNumber + 1, numPages) : prevPageNumber;
      if (onPageChange) onPageChange(newPageNumber);
      return newPageNumber;
    });
  }

  // Check if fileUrl or fileBytes is provided
  if (!pdfSource) {
    return (
      <div className="aspect-[8.5/11] bg-gray-100 rounded-lg border border-gray-200 flex items-center justify-center overflow-hidden">
        <div className="w-full h-full p-8 bg-white shadow-inner overflow-auto">
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <svg className="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
              />
            </svg>
            <p className="text-sm">No PDF File</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Page Controls */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-500 text-sm">Uploaded document preview</p>
        </div>

        <div className="flex items-center">
          <Button
            variant="outline"
            onClick={goToPrevPage}
            className={`px-2 py-1 ${pageNumber <= 1 ? 'invisible' : ''}`}
          >
            <ChevronLeft className="w-4 h-4" />
          </Button>

          <span className="text-sm text-gray-600 mx-4">
            {pageNumber} of {numPages || '--'}
          </span>

          <Button
            variant="outline"
            onClick={goToNextPage}
            className={`px-2 py-1 ${!numPages || pageNumber >= numPages ? 'invisible' : ''}`}
          >
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>
      </div>
      {/* PDF Preview Area */}
      <div className="aspect-[8.5/11] bg-gray-100 rounded-lg border border-gray-200 flex items-center justify-center overflow-hidden">
        <div className="w-full h-full p-8 bg-white shadow-inner overflow-auto">
          <Document
            file={pdfSource}
            onLoadSuccess={onDocumentLoadSuccess}
            onLoadError={onDocumentLoadError}
            options={options}
            loading={<PdfLoadingSkeleton />}
            error={
              <div className="flex items-center justify-center h-full">
                <div className="text-center max-w-md">
                  <div className="text-red-600 font-semibold mb-2">Error: Failed to load PDF</div>
                  <div className="text-sm text-gray-600 mb-4">
                    {error || 'The PDF file could not be loaded. Please check the file URL.'}
                  </div>
                  {!fileBytes && (
                    <div className="text-xs text-gray-500 bg-gray-100 p-3 rounded font-mono break-all">
                      URL: {pdfSource}
                    </div>
                  )}
                  <div className="mt-4 text-sm text-gray-600">
                    <p className="font-semibold mb-2">Possible issues:</p>
                    <ul className="text-left list-disc list-inside space-y-1">
                      <li>File URL is incorrect or inaccessible</li>
                      <li>CORS policy blocking the request</li>
                      <li>File server is not running</li>
                      <li>File has been moved or deleted</li>
                    </ul>
                  </div>
                </div>
              </div>
            }
          >
            {/* We only render the current page */}
            <Page
              pageNumber={pageNumber}
              width={500}
              devicePixelRatio={1}
              renderAnnotationLayer={false}
              renderTextLayer={false}
              loading={<PdfLoadingSkeleton />}
              onRenderSuccess={() => onPageRenderStatusChangeRef.current?.(true, pageNumber)}
              onRenderError={() => onPageRenderStatusChangeRef.current?.(true, pageNumber)}
            />
          </Document>
        </div>
      </div>
    </div>
  );
}
