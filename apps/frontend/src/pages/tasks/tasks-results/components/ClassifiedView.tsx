import { useEffect, useMemo, useState } from 'react';
import { OcrResult } from '@/types/types';
import { DataView } from './DataView';

interface ClassifiedDataViewProps {
  result: OcrResult;
  currentPage: number;
  onEditedDataChange?: (data: Record<string, unknown>) => void;
  isLoading?: boolean;
}

export function ClassifiedView({
  result,
  currentPage,
  onEditedDataChange,
  isLoading = false,
}: ClassifiedDataViewProps) {
  const initialData = useMemo(() => {
    if (Array.isArray(result.structuredData)) {
      return (result.structuredData as Record<string, unknown>[]).reduce<Record<string, unknown>>(
        (acc, item, idx) => {
          acc[idx.toString()] = item as Record<string, unknown>;
          return acc;
        },
        {}
      );
    }
    return { '0': (result.structuredData as Record<string, unknown>) || {} };
  }, [result.structuredData]);

  const [editedData, setEditedData] = useState<Record<string, unknown>>(initialData);

  useEffect(() => {
    setEditedData(initialData);
  }, [initialData]);

  const updateValue = (key: string, value: any) => {
    const pageKey = (currentPage - 1).toString();

    setEditedData((prev) => {
      const newData = {
        ...prev,
        [pageKey]: {
          ...((prev[pageKey] as Record<string, unknown>) || {}),
          [key]: value,
        },
      };
      onEditedDataChange?.(newData);
      return newData;
    });
  };

  const pageData = (editedData[(currentPage - 1).toString()] as Record<string, unknown>) || {};

  return (
    <DataView
      data={pageData}
      rawText={result.extractedText}
      onValueChange={updateValue}
      title={`Classified Data`}
      emptyMessage="No classification data for this page."
      isLoading={isLoading}
    />
  );
}
