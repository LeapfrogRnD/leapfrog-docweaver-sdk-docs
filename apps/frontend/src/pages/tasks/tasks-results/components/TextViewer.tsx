import { useState, useEffect } from 'react';
import { FileText } from 'lucide-react';
import { Spinner } from '@/components/ui';

interface TextViewerProps {
  fileUrl?: string;
}

export function TextViewer({ fileUrl }: TextViewerProps) {
  const [text, setText] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchText = async () => {
      if (!fileUrl) {
        setError('No file URL provided');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await fetch(fileUrl);

        if (!response.ok) {
          throw new Error(`Failed to fetch text file: ${response.statusText}`);
        }

        const textContent = await response.text();
        setText(textContent);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load text file');
        console.error('Error loading text file:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchText();
  }, [fileUrl]);

  if (!fileUrl) {
    return (
      <div className="aspect-[8.5/11] bg-gray-100 rounded-lg border border-gray-200 flex items-center justify-center">
        <div className="text-center text-gray-400">
          <FileText className="w-16 h-16 mx-auto mb-4" />
          <p className="text-sm">No Text File</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="aspect-[8.5/11] bg-gray-100 rounded-lg border border-gray-200 flex items-center justify-center">
        <div className="text-center">
          <Spinner size="lg" className="mx-auto mb-4" />
          <p className="text-sm text-gray-600">Loading text file...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="aspect-[8.5/11] bg-gray-100 rounded-lg border border-gray-200 flex items-center justify-center">
        <div className="text-center max-w-md p-6">
          <div className="text-red-600 font-semibold mb-2">Error Loading Text File</div>
          <div className="text-sm text-gray-600 mb-4">{error}</div>
          <div className="text-xs text-gray-500 bg-gray-100 p-3 rounded font-mono break-all">
            URL: {fileUrl}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Text Content Area */}
      <div className="aspect-[8.5/11] bg-gray-100 rounded-lg border border-gray-200 overflow-hidden">
        <div className="w-full h-full p-8 bg-white shadow-inner overflow-auto">
          <pre className="whitespace-pre-wrap text-sm font-mono text-gray-800 leading-relaxed">
            {text || 'Empty file'}
          </pre>
        </div>
      </div>

      {/* Info */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <FileText className="w-4 h-4" />
          <span>Text Document</span>
        </div>
        <span className="text-sm text-gray-600">
          {text.split('\n').length} lines • {text.length} characters
        </span>
      </div>
    </div>
  );
}
