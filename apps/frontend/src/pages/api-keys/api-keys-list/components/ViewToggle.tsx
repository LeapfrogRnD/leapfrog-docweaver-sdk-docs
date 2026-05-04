import { LayoutGrid, List } from 'lucide-react';

interface ViewToggleProps {
  viewMode: 'card' | 'table';
  onViewModeChange: (mode: 'card' | 'table') => void;
}

export function ViewToggle({ viewMode, onViewModeChange }: ViewToggleProps) {
  return (
    <div className="flex gap-0 bg-white rounded-lg border border-[rgba(0,0,0,0.1)] overflow-hidden">
      <button
        onClick={() => onViewModeChange('card')}
        className={`w-9 h-9 flex items-center justify-center transition-colors ${
          viewMode === 'card' ? 'bg-[#f3f4f6]' : 'bg-white hover:bg-[#f9fafb]'
        }`}
        title="Card view"
      >
        <LayoutGrid className="w-4 h-4 text-[#6b7280]" />
      </button>
      <button
        onClick={() => onViewModeChange('table')}
        className={`w-9 h-9 flex items-center justify-center transition-colors ${
          viewMode === 'table' ? 'bg-[#f3f4f6]' : 'bg-white hover:bg-[#f9fafb]'
        }`}
        title="Table view"
      >
        <List className="w-4 h-4 text-[#6b7280]" />
      </button>
    </div>
  );
}
