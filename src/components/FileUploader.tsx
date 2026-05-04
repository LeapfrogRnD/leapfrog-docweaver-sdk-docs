import { Upload, FileText } from 'lucide-react';
import { useCallback } from 'react';
import clsx from 'clsx';
import { useToast } from '@/context/ToastContext';

interface FileUploaderProps {
  onFileSelect: (file: File) => void;
  accept?: string;
  maxSize?: number;
  disabled?: boolean;
}

export function FileUploader({
  onFileSelect,
  accept = '.pdf,.jpg,.jpeg,.png',
  maxSize = 30 * 1024 * 1024, // 40MB
  disabled = false,
}: FileUploaderProps) {
  const { showToast } = useToast();

  const validateAndSelectFile = useCallback(
    (file: File) => {
      const validTypes = accept.split(',').map((t) => t.trim());
      const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
      const fileType = file.type;

      const isValidType = validTypes.some((type) => {
        if (type.startsWith('.')) {
          return fileExtension === type;
        }
        return fileType.startsWith(type.replace('*', ''));
      });

      if (!isValidType) {
        showToast(`Invalid file type. Please upload ${accept}`, 'error');
        return;
      }

      onFileSelect(file);
    },
    [maxSize, accept, onFileSelect]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      if (disabled) return;

      const file = e.dataTransfer.files[0];
      if (file) {
        validateAndSelectFile(file);
      }
    },
    [disabled, validateAndSelectFile]
  );

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      validateAndSelectFile(file);
    }
  };

  return (
    <div
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      className={clsx(
        'border-2 border-dashed border-primary-ivory rounded-xl',
        'flex flex-col items-center justify-center p-12',
        'transition-all duration-200',
        !disabled && 'hover:border-primary-brand hover:bg-gray-50/50 cursor-pointer',
        disabled && 'opacity-50 cursor-not-allowed'
      )}
    >
      <Upload className="w-12 h-12 text-gray-400 mb-4" />
      <div className="text-center">
        <label className="cursor-pointer">
          <span className="text-primary-brand font-medium hover:underline">Click to upload</span>
          <span className="text-primary-black ml-1">or drag and drop</span>
          <input
            type="file"
            className="hidden"
            accept={accept}
            onChange={handleFileInput}
            disabled={disabled}
          />
        </label>
      </div>
      <p className="text-xs text-gray-500 mt-2">
        PDF, JPG, JPEG or PNG (max {maxSize / (1024 * 1024)}MB)
      </p>
    </div>
  );
}

interface UploadedFileDisplayProps {
  file: File;
  onRemove: () => void;
}

export function UploadedFileDisplay({ file, onRemove }: UploadedFileDisplayProps) {
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="flex items-center gap-3 p-4 bg-gray-50 rounded-lg border border-gray-200">
      <div className="flex-shrink-0 w-10 h-10 bg-primary-brand/10 rounded-lg flex items-center justify-center">
        <FileText className="w-5 h-5 text-primary-brand" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-primary-black truncate">{file.name}</p>
        <p className="text-xs text-gray-500">
          {formatFileSize(file.size)} • {file.type || 'Unknown type'}
        </p>
      </div>
      <button
        onClick={onRemove}
        className="flex-shrink-0 text-red-500 hover:text-red-700 text-sm font-medium"
      >
        Remove
      </button>
    </div>
  );
}
