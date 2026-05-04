import * as React from 'react';
import {
  Button,
  Pagination,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  Skeleton,
} from './ui';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/Select';
import { Plus } from 'lucide-react';
import { UsePaginationReturn } from '@/hooks/usePagination';
import { TableControls } from './ui/TableControls';

export interface StatusFilterConfig {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  options: { label: string; value: string }[];
}

interface DataTableProps<T> {
  title?: React.ReactNode;
  description?: React.ReactNode;
  data: T[];
  columns: string[];
  search?: string;
  filters?: any;
  onSearch?: (value: string) => void;
  statusFilter?: StatusFilterConfig;
  primaryAction?: {
    label: string;
    onClick: () => void;
    icon?: React.ReactNode;
  };
  renderRow: (item: T, index: number) => React.ReactNode;
  isLoading?: boolean;
  emptyMessage?: React.ReactNode;
  hasActiveFilters?: boolean;
  currentPage?: number;
  totalPages?: number;
  pagination?: UsePaginationReturn;
  onPageChange?: (page: number) => void;
}

export function DataTable<T>({
  title,
  description,
  data,
  columns,
  search,
  onSearch,
  filters,
  statusFilter,
  primaryAction,
  renderRow,
  isLoading,
  emptyMessage,
  hasActiveFilters,
  pagination,
}: DataTableProps<T>) {
  const [isSearching, setIsSearching] = React.useState(false);
  const hasSearchQuery = Boolean(search?.trim());
  const hasStatusFilterApplied = Boolean(statusFilter?.value && statusFilter.value !== 'all');
  const shouldShowFilterHint = hasActiveFilters ?? (hasSearchQuery || hasStatusFilterApplied);

  return (
    <div className="w-full space-y-5 p-2">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div className="space-y-1">
          {title && <h2 className="text-xl font-semibold tracking-tight text-gray-900">{title}</h2>}
          {description && <p className="text-sm text-muted-foreground">{description}</p>}
        </div>

        <div className="flex items-center">
          {primaryAction && (
            <Button
              onClick={primaryAction.onClick}
              className="bg-[#038e43] hover:bg-[#027235] text-white shadow-sm"
            >
              {primaryAction.icon || <Plus className="mr-2 h-4 w-4" />}
              {primaryAction.label}
            </Button>
          )}
        </div>
      </div>

      <TableControls
        search={search}
        onSearchChange={onSearch}
        setIsSearching={setIsSearching}
        isSearching={isSearching}
        filters={
          statusFilter || filters ? (
            <>
              {statusFilter && (
                <Select value={statusFilter.value} onValueChange={statusFilter.onChange}>
                  <SelectTrigger className="h-9 w-[160px] text-sm">
                    <SelectValue placeholder={statusFilter.placeholder ?? 'Filter by status'} />
                  </SelectTrigger>
                  <SelectContent>
                    {statusFilter.options.map((opt) => (
                      <SelectItem key={opt.value} value={opt.value}>
                        {opt.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
              {filters}
            </>
          ) : undefined
        }
        hasActions={Boolean(statusFilter || filters || primaryAction)}
      />

      <div className="rounded-xl bg-card text-card-foreground shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader className="bg-muted/50">
              <TableRow className="hover:bg-transparent">
                {columns.map((column, i) => (
                  <TableHead key={i} className="text-2xl h-11">
                    {column}
                  </TableHead>
                ))}
              </TableRow>
            </TableHeader>

            <TableBody>
              {isLoading ? (
                Array.from({ length: Math.min(5, 5) }).map((_, rIdx) => (
                  <TableRow key={`s-${rIdx}`}>
                    {columns.map((_, cIdx) => (
                      <TableCell key={cIdx} className="px-6 py-4">
                        <Skeleton
                          className="h-4"
                          width={cIdx === 0 ? '80%' : cIdx === columns.length - 1 ? '60px' : '70%'}
                        />
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              ) : data.length > 0 ? (
                data.map((item, index) => renderRow(item, index))
              ) : (
                <TableRow>
                  <TableCell
                    colSpan={columns.length}
                    className="h-32 text-center text-muted-foreground"
                  >
                    {emptyMessage || (
                      <div className="flex flex-col items-center justify-center space-y-1">
                        <p className="font-medium text-gray-900">No results found</p>
                        {shouldShowFilterHint && (
                          <p className="text-sm text-gray-500">
                            Try adjusting your search or filters.
                          </p>
                        )}
                      </div>
                    )}
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>

        {/* Pagination Footer */}
        {pagination && (
          <Pagination
            metadata={pagination.metadata}
            currentPage={pagination.page}
            pageSize={pagination.pageSize}
            onPageChange={pagination.setPage}
            onPageSizeChange={pagination.setPageSize}
          />
        )}
      </div>
    </div>
  );
}
