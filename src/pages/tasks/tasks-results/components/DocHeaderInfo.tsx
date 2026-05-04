import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { OcrResult } from '@/types/types';
import { formatFileSize } from '@/utils';
import { TaskStatusBadge } from '../../task-list/components/TaskStatusBadge';
import { TaskResultResponse } from '@/types/task.type';

interface DocHeaderInfoProps {
  result: OcrResult;
  taskResult: TaskResultResponse | undefined;
}

export function DocHeaderInfo({ result, taskResult }: DocHeaderInfoProps) {
  return (
    <Card className="mb-6">
      <CardHeader className="flex items-center justify-between">
        <CardTitle>Document Information</CardTitle>

        <div className="flex flex-col items-end">
          <div className="flex items-center justify-between gap-2">
            <p className="text-sm text-gray-500 mb-1"> Processed: </p>
            <span className="text-sm mb-1 text-gray-500">{result.updatedAt}</span>
            <TaskStatusBadge status={result.status} />
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-12 gap-6 items-center">
          {/* Name */}
          <div className="col-span-12 sm:col-span-5 lg:col-span-3">
            <div className="p-2">
              <p className="text-sm text-gray-500 mb-1">Name</p>
              <p className="text-sm font-medium truncate">{result.task_name}</p>
            </div>
          </div>

          {/* Type */}
          <div className="col-span-12 sm:col-span-2 lg:col-span-3 relative">
            <div className="absolute left-0 top-1/2 -translate-y-1/2 h-8 w-px bg-gray-200" />
            <div className="ml-7 ">
              <p className="text-sm text-gray-500 mb-1">Type</p>
              <span className="text-sm font-medium text-[#111] capitalize">{result.task_type}</span>
            </div>
          </div>

          {/* File Info */}
          <div className="col-span-12 sm:col-span-5 lg:col-span-4 relative min-w-0">
            <div className="absolute left-0 top-1/2 -translate-y-1/2 h-8 w-px bg-gray-200" />
            <div className="ml-7 ">
              <p className="text-sm text-gray-500 mb-1">File Info</p>
              <p className="text-sm font-medium break-words">{result.documentName}</p>
              <p className="text-xs text-gray-500">
                {formatFileSize(taskResult?.file_metadata?.file_size)}
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
