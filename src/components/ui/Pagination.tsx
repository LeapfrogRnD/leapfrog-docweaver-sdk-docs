import { ChevronLeft, ChevronRight } from 'lucide-react';
import { PaginationMetadata } from '@/types/types';

interface PaginationProps {
  metadata: PaginationMetadata | null;
  currentPage: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (pageSize: number) => void;
  pageSizeOptions?: number[];
}

export function Pagination({
  metadata,
  currentPage,
  pageSize,
  onPageChange,
  onPageSizeChange,
  pageSizeOptions = [5, 10, 25, 50, 100],
}: PaginationProps) {
  if (!metadata || metadata.total === 0) {
    return null;
  }
  const { total_items, total_pages } = metadata;
  const startItem = (currentPage - 1) * pageSize + 1;
  const endItem = Math.min(currentPage * pageSize, total_items);

  const canGoPrev = currentPage > 1;
  const canGoNext = currentPage < total_pages;

  // Generate page numbers to display
  const getPageNumbers = () => {
    const pages: (number | string)[] = [];
    const maxVisible = 5;

    if (total_pages <= maxVisible) {
      // Show all pages if total is small
      for (let i = 1; i <= total_pages; i++) {
        pages.push(i);
      }
    } else {
      // Always show first page
      pages.push(1);

      if (currentPage > 3) {
        pages.push('...');
      }

      // Show pages around current page
      const start = Math.max(2, currentPage - 1);
      const end = Math.min(total_pages - 1, currentPage + 1);

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }

      if (currentPage < total_pages - 2) {
        pages.push('...');
      }

      // Always show last page
      if (total_pages > 1) {
        pages.push(total_pages);
      }
    }

    return pages;
  };

  return (
    <div className="flex items-center justify-between px-4 py-3 bg-white">
      {/* Page size selector and info */}
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <span className="text-sm text-[#6b7280]">Rows per page:</span>
          <select
            value={pageSize}
            onChange={(e) => onPageSizeChange(Number(e.target.value))}
            className="h-8 px-2 pr-8 text-sm border border-[rgba(0,0,0,0.1)] rounded-lg bg-white text-[#111] focus:outline-none focus:ring-2 focus:ring-[#038e43] focus:ring-opacity-20"
          >
            {pageSizeOptions.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>

        <div className="text-sm text-[#6b7280]">
          Showing <span className="font-medium text-[#111]">{startItem}</span> to{' '}
          <span className="font-medium text-[#111]">{endItem}</span> of{' '}
          <span className="font-medium text-[#111]">{total_items}</span> results
        </div>
      </div>

      {/* Page navigation */}
      <div className="flex items-center gap-2">
        {/* Previous button */}
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={!canGoPrev}
          className="h-8 w-8 flex items-center justify-center rounded-lg border border-[rgba(0,0,0,0.1)] hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-white transition-colors"
          title="Previous page"
        >
          <ChevronLeft className="w-4 h-4 text-[#6b7280]" />
        </button>

        {/* Page numbers */}
        <div className="flex items-center gap-1">
          {getPageNumbers().map((page, index) => {
            if (page === '...') {
              return (
                <span key={`ellipsis-${index}`} className="px-2 text-[#6b7280]">
                  ...
                </span>
              );
            }

            const pageNum = page as number;
            const isActive = pageNum === currentPage;

            return (
              <button
                key={pageNum}
                onClick={() => onPageChange(pageNum)}
                className={`h-8 min-w-[32px] px-2 flex items-center justify-center rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-[#038e43] text-white'
                    : 'text-[#111] hover:bg-gray-50 border border-[rgba(0,0,0,0.1)]'
                }`}
              >
                {pageNum}
              </button>
            );
          })}
        </div>

        {/* Next button */}
        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={!canGoNext}
          className="h-8 w-8 flex items-center justify-center rounded-lg border border-[rgba(0,0,0,0.1)] hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-white transition-colors"
          title="Next page"
        >
          <ChevronRight className="w-4 h-4 text-[#6b7280]" />
        </button>
      </div>
    </div>
  );
}
