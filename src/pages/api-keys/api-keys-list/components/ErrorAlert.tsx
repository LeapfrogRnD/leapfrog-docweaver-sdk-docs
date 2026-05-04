import { AlertCircle } from 'lucide-react';

interface ErrorAlertProps {
  message: string;
}

export function ErrorAlert({ message }: ErrorAlertProps) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-[10px] p-4">
      <div className="flex gap-3">
        <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
        <div>
          <h3 className="text-sm font-medium text-red-800 tracking-[-0.5px] mb-1">Error</h3>
          <p className="text-sm text-red-700 tracking-[-0.15px]">{message}</p>
        </div>
      </div>
    </div>
  );
}
