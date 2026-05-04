import { useState } from 'react';
import { Eye, EyeOff, Copy, Trash2, Edit, RefreshCw } from 'lucide-react';
import { ApiKey } from '@/types/api-key.type';
import { Card } from '@/components/ui';
import { useToast } from '@/context/ToastContext';
import { maskApiKey } from '../../../../utils';

interface ApiKeyCardProps {
  apiKey: ApiKey;
  onDelete: (id: number) => void;
  onEdit: (id: number) => void;
  onRegenerate: (id: number) => void;
}

export function ApiKeyCard({ apiKey, onDelete, onEdit, onRegenerate }: ApiKeyCardProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [isCopied, setIsCopied] = useState(false);
  const { showToast } = useToast();

  const toggleVisibility = () => {
    setIsVisible(!isVisible);
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(apiKey.secret_value);
    setIsCopied(true);
    showToast('API key copied to clipboard', 'success');
    setTimeout(() => setIsCopied(false), 2000);
  };

  return (
    <Card variant="bordered" className="rounded-[14px] p-6">
      <div className="flex items-start justify-between mb-8">
        <div>
          <h3 className="text-base font-medium text-[#111] tracking-[-0.31px] mb-1">
            {apiKey.secret_name}
          </h3>
          <p className="text-base text-[#6b7280] tracking-[-0.31px]">
            Created: {apiKey.created_at} • Last used:{' '}
            {apiKey.last_used_at ? apiKey.last_used_at : 'Never'}
          </p>
        </div>
        <span
          className={`px-2 h-[22px] text-xs font-medium rounded-lg flex items-center ${
            apiKey.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
          }`}
        >
          {apiKey.is_active ? 'Active' : 'Inactive'}
        </span>
      </div>
      <div>
        <label className="block text-xs font-medium text-[#6b7280] mb-2">API Key</label>
        <div className="flex gap-2">
          <div className="flex-1 bg-[#f3f4f6] border border-[rgba(0,0,0,0.1)] rounded-[10px] px-3 py-2.5 font-mono text-sm text-[#111]">
            {isVisible ? apiKey.secret_value : maskApiKey(apiKey.secret_value)}
          </div>
          <button
            onClick={toggleVisibility}
            className="w-9 h-[38px] bg-white border border-[rgba(0,0,0,0.1)] rounded-lg flex items-center justify-center hover:bg-[#f9fafb] transition-colors"
            title={isVisible ? 'Hide key' : 'Show key'}
          >
            {isVisible ? (
              <Eye className="w-4 h-4 text-[#6b7280]" />
            ) : (
              <EyeOff className="w-4 h-4 text-[#6b7280]" />
            )}
          </button>
          <button
            onClick={() => onEdit(apiKey.id)}
            className="w-9 h-[38px] bg-white border border-[rgba(0,0,0,0.1)] rounded-lg flex items-center justify-center transition-colors"
            title="Edit key"
          >
            <Edit className="w-4 h-4 text-[#6b7280]" />
          </button>
          <button
            onClick={copyToClipboard}
            className="w-9 h-[38px] bg-white border border-[rgba(0,0,0,0.1)] rounded-lg flex items-center justify-center hover:bg-[#f9fafb] transition-colors"
            title={isCopied ? 'Copied!' : 'Copy to clipboard'}
          >
            <Copy className={`w-4 h-4 ${isCopied ? 'text-[#038e43]' : 'text-[#6b7280]'}`} />
          </button>
          <button
            onClick={() => onRegenerate(apiKey.id)}
            className="w-9 h-[38px] bg-white border border-[rgba(0,0,0,0.1)] rounded-lg flex items-center justify-center hover:bg-[#f9fafb] transition-colors"
            title={'Regenerate Secret'}
          >
            <RefreshCw className="w-4 h-4 text-[#6b7280]" />
          </button>
          <button
            onClick={() => onDelete(apiKey.id)}
            className="w-9 h-[38px] bg-white border border-[rgba(0,0,0,0.1)] rounded-lg flex items-center justify-center hover:bg-red-50 transition-colors"
            title="Delete key"
          >
            <Trash2 className="w-4 h-4 text-[#6b7280] hover:text-red-600" />
          </button>
        </div>
      </div>
    </Card>
  );
}
