import { Button } from '@/components/ui';

interface EmptyStateProps {
  onCreateClick: () => void;
}

export function EmptyState({ onCreateClick }: EmptyStateProps) {
  return (
    <div className="bg-white border border-[rgba(0,0,0,0.1)] rounded-[14px] p-12 text-center">
      <div className="w-16 h-16 bg-[#f3f4f6] rounded-full flex items-center justify-center mx-auto mb-4">
        <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none">
          <path
            d="M7 10V7C7 4.79086 8.79086 3 11 3C13.2091 3 15 4.79086 15 7V10"
            stroke="#6b7280"
            strokeWidth="2"
            strokeLinecap="round"
          />
          <path
            d="M5 13C5 11.8954 5.89543 11 7 11H15C16.1046 11 17 11.8954 17 13V19C17 20.1046 16.1046 21 15 21H7C5.89543 21 5 20.1046 5 19V13Z"
            stroke="#6b7280"
            strokeWidth="2"
          />
          <circle cx="11" cy="16" r="1" fill="#6b7280" />
        </svg>
      </div>
      <h3 className="text-lg font-medium text-[#111] mb-2">No API keys yet</h3>
      <p className="text-sm text-[#6b7280] mb-4">
        Create your first API key to start using the OCR API
      </p>
      <Button
        onClick={onCreateClick}
        className="bg-[#038e43] text-white hover:bg-[#027235] h-9 px-4 rounded-lg"
      >
        Create New Key
      </Button>
    </div>
  );
}
