import { Plus } from 'lucide-react';
import { PageHeader } from '@/components';

interface ApiKeysHeaderProps {
  onCreateClick: () => void;
}

export function ApiKeysHeader({ onCreateClick }: ApiKeysHeaderProps) {
  return (
    <PageHeader
      icon={
        <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none">
          <path
            d="M7 10V7C7 4.79086 8.79086 3 11 3C13.2091 3 15 4.79086 15 7V10"
            stroke="#038e43"
            strokeWidth="2"
            strokeLinecap="round"
          />
          <path
            d="M5 13C5 11.8954 5.89543 11 7 11H15C16.1046 11 17 13V19C17 20.1046 16.1046 21 15 21H7C5.89543 21 5 19V13Z"
            stroke="#038e43"
            strokeWidth="2"
          />
          <circle cx="11" cy="16" r="1" fill="#038e43" />
        </svg>
      }
      title="API Keys"
      description="Manage your API authentication keys"
      actions={
        <button
          onClick={onCreateClick}
          className="h-9 px-2 sm:px-3 bg-[#038e43] text-white text-xs sm:text-sm font-medium rounded-lg flex items-center gap-1 sm:gap-2 hover:bg-[#027235] transition-colors flex-shrink-0 w-full sm:w-auto justify-center"
        >
          <Plus className="w-4 h-4" />
          <span className="hidden sm:inline">Create New Key</span>
          <span className="sm:hidden">Create Key</span>
        </button>
      }
    />
  );
}
