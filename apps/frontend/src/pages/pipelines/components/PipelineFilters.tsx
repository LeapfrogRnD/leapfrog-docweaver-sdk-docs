import { LayoutGrid, List } from 'lucide-react';

interface PipelineFiltersProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  statusFilter: string;
  onStatusFilterChange: (status: string) => void;
  viewMode: 'card' | 'table';
  onViewModeChange: (mode: 'card' | 'table') => void;
}

export function PipelineFilters({
  //   searchQuery,
  //   onSearchChange,
  //   statusFilter,
  //   onStatusFilterChange,
  viewMode,
  onViewModeChange,
}: PipelineFiltersProps) {
  return (
    <div className="flex items-center justify-between">
      {/* Search */}
      <div className="flex items-center gap-2 w-[216px]">
        {/* <Search className="w-4 h-4 text-[#6b7280]" />
        <input
          type="text"
          placeholder="Search pipelines..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="flex-1 h-9 px-3 bg-[#f9fafb] border-0 rounded-lg text-sm text-[#111] placeholder:text-[#6b7280] tracking-[-0.15px] focus:outline-none focus:ring-2 focus:ring-[#038e43]"
        /> */}
      </div>

      <div className="flex items-center gap-3">
        {/* Status Filter */}
        <div className="relative">
          {/* <select
            value={statusFilter}
            onChange={(e) => onStatusFilterChange(e.target.value)}
            className="h-9 pl-3 pr-8 bg-[#f9fafb] border-0 rounded-lg text-sm font-medium text-[#111] tracking-[-0.15px] cursor-pointer appearance-none focus:outline-none focus:ring-2 focus:ring-[#038e43]"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
          <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#6b7280] pointer-events-none" /> */}
        </div>

        {/* View Toggle */}
        <div className="flex bg-[#f3f4f6] rounded-lg">
          <button
            onClick={() => onViewModeChange('card')}
            className={`w-9 h-9 rounded-lg flex items-center justify-center transition-colors ${
              viewMode === 'card' ? 'bg-white shadow-sm' : 'bg-transparent hover:bg-white/50'
            }`}
          >
            <LayoutGrid className="w-4 h-4 text-[#111]" />
          </button>
          <button
            onClick={() => onViewModeChange('table')}
            className={`w-9 h-9 rounded-lg flex items-center justify-center transition-colors ${
              viewMode === 'table' ? 'bg-white shadow-sm' : 'bg-transparent hover:bg-white/50'
            }`}
          >
            <List className="w-4 h-4 text-[#111]" />
          </button>
        </div>
      </div>
    </div>
  );
}
