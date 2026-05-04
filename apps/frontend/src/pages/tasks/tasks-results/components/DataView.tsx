import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeSanitize from 'rehype-sanitize';
import { TextArea, Input, Skeleton } from '@/components/ui';
import { Copy, Check } from 'lucide-react';
import { formatLabel } from '@/utils';

interface DataViewProps {
  data: Record<string, any>;
  rawText?: string;
  onValueChange: (key: string, value: any) => void;
  title?: string;
  emptyMessage?: string;
  isLoading?: boolean;
}

function DataViewSkeleton() {
  return (
    <div className="space-y-4 animate-pulse">
      {Array.from({ length: 4 }).map((_, index) => (
        <div
          key={index}
          className="flex flex-col gap-3 p-5 bg-[#F3F4F6]/50 border border-gray-100 rounded-2xl"
        >
          <Skeleton className="h-3 w-28" />
          <Skeleton className="h-12 w-full rounded-xl" />
        </div>
      ))}
    </div>
  );
}

export function DataView({
  data = {},
  rawText = '',
  onValueChange,
  title = 'Extracted Data',
  emptyMessage = 'No data available',
  isLoading = false,
}: DataViewProps) {
  const [activeTab, setActiveTab] = useState<'preview' | 'source'>('preview');
  const [copied, setCopied] = useState(false);
  const [localContent, setLocalContent] = useState<string>('');

  const isGenerationMode = Object.prototype.hasOwnProperty.call(data ?? {}, 'generation_response');

  useEffect(() => {
    if (isGenerationMode) {
      setLocalContent(String(data.generation_response ?? ''));
    }
  }, [data.generation_response, isGenerationMode]);

  const handleCopy = () => {
    let textToCopy = '';
    if (isGenerationMode) {
      textToCopy = localContent;
    } else {
      // Export current structured data view (excluding internal pg_no)
      const { ...cleanData } = data;
      textToCopy = JSON.stringify(cleanData, null, 2);
    }

    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex flex-col h-full bg-[#F9FAFB] rounded-[32px] p-8 shadow-sm font-sans overflow-hidden">
      <div className="flex items-center justify-between mb-8">
        <div className="flex flex-col">
          <h3 className="text-xl font-bold text-gray-800">{title}</h3>
          <p className="text-sm text-gray-400 mt-1">Extracted from the document using pipeline</p>
        </div>

        <div className="flex items-center gap-6">
          <button
            onClick={handleCopy}
            className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
          >
            {copied ? <Check className="w-5 h-5 text-green-500" /> : <Copy className="w-5 h-5" />}
          </button>

          <div className="flex items-center gap-3">
            <span className="text-sm font-medium text-gray-700">
              {isGenerationMode ? (activeTab === 'preview' ? 'Preview' : 'Source') : 'Raw Text'}
            </span>
            <button
              onClick={() => setActiveTab(activeTab === 'preview' ? 'source' : 'preview')}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
                activeTab === 'source' ? 'bg-blue-600' : 'bg-gray-200'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-200 ease-in-out ${
                  activeTab === 'source' ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>
      </div>

      {/* ══ CONTENT AREA ══ */}
      <div className="flex-1 overflow-y-auto custom-scrollbar pr-2">
        {isLoading ? (
          <DataViewSkeleton />
        ) : Object.keys(data).length === 0 ? (
          <div className="h-full flex items-center justify-center text-gray-400 italic text-sm py-20">
            {emptyMessage}
          </div>
        ) : (
          <div className="h-full animate-in fade-in duration-300">
            {isGenerationMode ? (
              /* --- MODE A: SUMMARIZATION / GENERATION --- */
              activeTab === 'preview' ? (
                <div className="prose prose-slate max-w-none text-gray-800 leading-relaxed bg-white p-6 rounded-2xl border border-gray-100">
                  <ReactMarkdown rehypePlugins={[rehypeSanitize]}>{localContent}</ReactMarkdown>
                </div>
              ) : (
                <TextArea
                  value={localContent}
                  onChange={(e) => {
                    setLocalContent(e.target.value);
                    onValueChange('generation_response', e.target.value);
                  }}
                  className="w-full h-full font-mono text-sm leading-6 p-5 bg-white border-gray-200 rounded-2xl resize-none min-h-[450px] outline-none focus:ring-2 focus:ring-blue-500/10 transition-all"
                  spellCheck={false}
                />
              )
            ) : /* --- MODE B: STRUCTURED EXTRACTION --- */
            activeTab === 'preview' ? (
              <div className="space-y-4">
                {Object.entries(data)
                  .filter(([key]) => key !== 'pg_no')
                  .map(([key, value]) => (
                    <div
                      key={key}
                      className="flex flex-col gap-2 p-5 bg-[#F3F4F6]/50 border border-gray-100 rounded-2xl"
                    >
                      <label className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
                        {formatLabel(key)}
                      </label>
                      {typeof value === 'string' && value.length > 80 ? (
                        <TextArea
                          value={value ?? ''}
                          onChange={(e) => onValueChange(key, e.target.value)}
                          className="bg-white border-gray-200 text-sm p-4 rounded-xl focus:ring-2 focus:ring-blue-500/10 outline-none"
                          rows={3}
                        />
                      ) : (
                        <Input
                          value={value ?? ''}
                          onChange={(e) => onValueChange(key, e.target.value)}
                          className="bg-white border-gray-200 text-sm h-12 px-4 rounded-xl focus:ring-2 focus:ring-blue-500/10 outline-none w-full transition-all"
                        />
                      )}
                    </div>
                  ))}
              </div>
            ) : (
              /* RAW TEXT VIEW (For Extraction Mode) */
              <div className="rounded-2xl bg-white border border-gray-200 p-8 shadow-inner min-h-full">
                <div className="flex justify-between items-center mb-4 border-b border-gray-100 pb-2">
                  <span className="text-[10px] font-mono text-gray-400 uppercase font-bold">
                    Original OCR Buffer
                  </span>
                </div>
                <pre className="font-mono text-[13px] whitespace-pre-wrap leading-7 text-gray-600">
                  {rawText || JSON.stringify(data, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>

      <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
      `}</style>
    </div>
  );
}
