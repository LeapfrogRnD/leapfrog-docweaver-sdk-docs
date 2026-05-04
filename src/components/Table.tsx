import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from '@/components/ui/Table';
import { TableSkeleton } from '@/components/ui';
import { TableControls } from '@/components/ui/TableControls';
import { Pagination } from '@/components/ui';
import { UsePaginationReturn } from '@/hooks/usePagination';
import React from 'react';

interface GenericTableProps<T> {
  data: T[];
  rowKey: (item: T) => string | number;
  RowComponent: React.ComponentType<{ item: T }>;
  headers: string[];

  search?: string;
  onSearchChange?: (value: string) => void;
  filters?: React.ReactNode;
  pagination?: UsePaginationReturn;
  isLoading?: boolean;
  emptyText?: string;
}

export function GenericTable<T>({
  data,
  rowKey,
  RowComponent,
  headers,
  search,
  onSearchChange,
  filters,
  pagination,
  isLoading,
  emptyText = 'No data found.',
}: GenericTableProps<T>) {
  if (isLoading) {
    return <TableSkeleton rows={5} columns={headers.length} showHeader={true} />;
  }

  return (
    <>
      {(search || filters) && (
        <TableControls search={search} onSearchChange={onSearchChange} filters={filters} />
      )}

      <div className="bg-white rounded-[14px] border border-[rgba(0,0,0,0.1)] overflow-hidden">
        <Table variant="plain">
          <TableHeader>
            <TableRow>
              {headers.map((header, idx) => (
                <TableHead key={idx}>{header}</TableHead>
              ))}
            </TableRow>
          </TableHeader>

          <TableBody>
            {data.length === 0 ? (
              <TableRow>
                <TableCell colSpan={headers.length} className="text-center py-8 text-gray-400">
                  {emptyText}
                </TableCell>
              </TableRow>
            ) : (
              data.map((item) => <RowComponent key={rowKey(item)} item={item} />)
            )}
          </TableBody>
        </Table>

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
    </>
  );
}
