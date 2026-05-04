import { useState, useEffect, useMemo } from 'react';
import { OcrResult } from '@/types/types';
import { DataView } from './DataView';

interface ExtractedDataViewProps {
  result: OcrResult;
  currentPage: number;
  onEditedDataChange?: (data: Record<string, any>) => void;
  isLoading?: boolean;
}

export function ExtractedView({
  result,
  currentPage,
  onEditedDataChange,
  isLoading = false,
}: ExtractedDataViewProps) {
  // Normalize structuredData: if it's an array, convert to an object keyed by page index
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

  // CRITICAL: Sync local state when external data (result) changes
  useEffect(() => {
    setEditedData(initialData);
  }, [initialData]);

  const updateValue = (key: string, value: any) => {
    const pageKey = (currentPage - 1).toString();

    setEditedData((prev) => {
      const newData = {
        ...prev,
        [pageKey]: {
          ...(prev[pageKey] || {}),
          [key]: value,
        },
      };
      onEditedDataChange?.(newData);
      return newData;
    });
  };

  const pageData = (editedData[(currentPage - 1).toString()] as Record<string, any>) || {};

  return (
    <DataView
      data={pageData}
      rawText={result.extractedText}
      onValueChange={updateValue}
      title="Extracted Data"
      isLoading={isLoading}
    />
  );
}
