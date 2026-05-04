import type { PaginatedResponse } from '@/types/types';

export const mapPaginatedResponse = <T, R>(mapper: (item: T) => R) => {
  return (response: PaginatedResponse<T>): PaginatedResponse<R> => ({
    data: response.data.map(mapper),
    metadata: response.metadata,
  });
};

export const defaultPaginatedResponse = <T>(): PaginatedResponse<T> => ({
  data: [],
  metadata: {
    page: 1,
    page_size: 10,
    total_items: 0,
    total_pages: 0,
    total: 0,
  },
});
