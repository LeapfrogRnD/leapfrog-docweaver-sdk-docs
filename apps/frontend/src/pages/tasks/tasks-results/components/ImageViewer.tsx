// src/components/ImageViewer.tsx

import { useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui';

interface ImageViewerProps {
  fileUrl?: string;
  fileBytes?: string; // Base64 encoded image bytes
}

export function ImageViewer({ fileUrl, fileBytes }: ImageViewerProps) {
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Convert base64 to data URL for images
  const imageSource = fileBytes
    ? `data:image/png;base64,${fileBytes}` // Assuming PNG, but can be adjusted
    : fileUrl;

  const handleImageLoad = () => {
    setLoading(false);
    setError(null);
  };

  const handleImageError = () => {
    setLoading(false);
    setError('Failed to load image');
  };

  // Check if fileUrl or fileBytes is provided
  if (!imageSource) {
    return (
      <div className="aspect-[8.5/11] bg-gray-100 rounded-lg border border-gray-200 flex items-center justify-center overflow-hidden">
        <div className="w-full h-full p-8 bg-white shadow-inner overflow-auto">
          <div className="flex flex-col items-center justify-center h-full text-gray-400">
            <svg className="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            <p className="text-sm">No Image File</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Image Preview Area */}
      <div className="aspect-[8.5/11] bg-gray-100 rounded-lg border border-gray-200 flex items-center justify-center overflow-hidden">
        <div className="w-full h-full p-8 bg-white shadow-inner overflow-auto flex items-center justify-center">
          {loading && (
            <div className="flex items-center justify-center h-full">
              <div className="text-gray-600">Loading image...</div>
            </div>
          )}
          {error ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center max-w-md">
                <div className="text-red-600 font-semibold mb-2">Error: Failed to load image</div>
                <div className="text-sm text-gray-600 mb-4">{error}</div>
                {!fileBytes && (
                  <div className="text-xs text-gray-500 bg-gray-100 p-3 rounded font-mono break-all">
                    URL: {imageSource}
                  </div>
                )}
                <div className="mt-4 text-sm text-gray-600">
                  <p className="font-semibold mb-2">Possible issues:</p>
                  <ul className="text-left list-disc list-inside space-y-1">
                    <li>Image URL is incorrect or inaccessible</li>
                    <li>CORS policy blocking the request</li>
                    <li>Image server is not running</li>
                    <li>Image has been moved or deleted</li>
                  </ul>
                </div>
              </div>
            </div>
          ) : (
            <img
              src={imageSource}
              alt="Document Preview"
              className="max-w-full max-h-full object-contain"
              onLoad={handleImageLoad}
              onError={handleImageError}
              style={{ display: loading ? 'none' : 'block' }}
            />
          )}
        </div>
      </div>

      {/* Page Controls (disabled for images) */}
      <div className="flex items-center justify-between">
        <Button variant="outline" disabled className="h-9 opacity-50 cursor-not-allowed">
          <ChevronLeft className="w-4 h-4" />
          Previous
        </Button>

        <span className="text-sm text-gray-600">Page 1 of 1</span>

        <Button variant="outline" disabled className="h-9 opacity-50 cursor-not-allowed">
          Next
          <ChevronRight className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
}
