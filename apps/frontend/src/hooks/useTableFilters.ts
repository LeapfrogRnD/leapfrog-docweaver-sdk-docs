import { useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import qs from 'query-string';

export function useTableFilters(defaults: Record<string, any> = {}) {
  const [searchParams, setSearchParams] = useSearchParams();

  const filters = useMemo(() => {
    const params = Object.fromEntries(searchParams.entries());

    return {
      ...defaults,
      ...params,
    };
  }, [searchParams, defaults]);

  const updateFilters = (newFilters: Record<string, any>) => {
    const merged = {
      ...filters,
      ...newFilters,
    };

    Object.keys(merged).forEach((key) => {
      if (!merged[key]) delete merged[key];
    });

    setSearchParams(qs.stringify(merged));
  };

  return {
    filters,
    updateFilters,
  };
}
