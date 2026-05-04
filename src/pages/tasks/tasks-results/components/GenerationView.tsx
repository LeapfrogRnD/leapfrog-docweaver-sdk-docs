import { useEffect, useMemo, useState } from 'react';
import { OcrResult } from '@/types/types';
import { DataView } from './DataView'; // Adjust path as needed

interface GenerationViewProps {
  result: OcrResult;
  currentPage: number;
  onEditedDataChange?: (data: Record<string, any>) => void;
  title?: string;
  emptyMessage?: string;
  isLoading?: boolean;
}

export function GenerationView({
  result,
  currentPage,
  onEditedDataChange,
  title = 'Generated Content',
  emptyMessage = 'No data available',
  isLoading = false,
}: GenerationViewProps) {
  const initialData = useMemo(() => {
    if (Array.isArray(result.structuredData)) {
      return (result.structuredData as Record<string, any>[]).reduce<Record<string, any>>(
        (acc, item, idx) => {
          acc[idx.toString()] = item;
          return acc;
        },
        {}
      );
    }
    return { '0': (result.structuredData as Record<string, any>) || {} };
  }, [result.structuredData]);

  const [editedData, setEditedData] = useState<Record<string, any>>(initialData);

  useEffect(() => {
    setEditedData(initialData);
  }, [initialData]);

  const pageKey = (currentPage - 1).toString();
  const fallbackPageData = Object.values(editedData).find(
    (item: any) => item?.pg_no === currentPage
  );
  const currentPageData = (editedData[pageKey] as Record<string, any>) || fallbackPageData || {};

  const handleValueChange = (key: string, value: any) => {
    const newData = {
      ...editedData,
      [pageKey]: {
        ...(editedData[pageKey] || {}),
        [key]: value,
      },
    };
    setEditedData(newData);
    onEditedDataChange?.(newData);
  };

  return (
    <DataView
      title={`${title}`}
      data={currentPageData || {}}
      onValueChange={handleValueChange}
      emptyMessage={emptyMessage}
      rawText={result.extractedText}
      isLoading={isLoading}
    />
  );
}
