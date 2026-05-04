import { useState, useCallback } from 'react';
import { PaginationMetadata } from '@/types/types';
import { DEFAULT_PAGE_SIZE } from '@/constants/pagination.constants';

interface UsePaginationOptions {
  initialPage?: number;
  initialPageSize?: number;
}

export interface UsePaginationReturn {
  page: number;
  pageSize: number;
  metadata: PaginationMetadata | null;
  setPage: (page: number) => void;
  setPageSize: (pageSize: number) => void;
  setMetadata: (metadata: PaginationMetadata) => void;
  nextPage: () => void;
  prevPage: () => void;
  goToPage: (page: number) => void;
  canGoPrev: boolean;
  canGoNext: boolean;
  reset: () => void;
}

export function usePagination(options: UsePaginationOptions = {}): UsePaginationReturn {
  const { initialPage = 1, initialPageSize = DEFAULT_PAGE_SIZE } = options;

  const [page, setPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [metadata, setMetadata] = useState<PaginationMetadata | null>(null);

  const canGoPrev = page > 1;
  const canGoNext = metadata ? page < metadata.total_pages : false;

  const nextPage = useCallback(() => {
    if (canGoNext) {
      setPage((prev) => prev + 1);
    }
  }, [canGoNext]);

  const prevPage = useCallback(() => {
    if (canGoPrev) {
      setPage((prev) => prev - 1);
    }
  }, [canGoPrev]);

  const goToPage = useCallback(
    (newPage: number) => {
      if (metadata && newPage >= 1 && newPage <= metadata.total_pages) {
        setPage(newPage);
      }
    },
    [metadata]
  );

  const handleSetPageSize = useCallback((newPageSize: number) => {
    setPageSize(newPageSize);
    setPage(1); // Reset to first page when page size changes
  }, []);

  const reset = useCallback(() => {
    setPage(initialPage);
    setPageSize(initialPageSize);
    setMetadata(null);
  }, [initialPage, initialPageSize]);

  return {
    page,
    pageSize,
    metadata,
    setPage,
    setPageSize: handleSetPageSize,
    setMetadata,
    nextPage,
    prevPage,
    goToPage,
    canGoPrev,
    canGoNext,
    reset,
  };
}
