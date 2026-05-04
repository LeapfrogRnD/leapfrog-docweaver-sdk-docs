import { File } from 'lucide-react';
import { TaskDetail } from '@/types/task.type';
import { formatFileSize } from '@/utils';

interface DocumentInformationCardProps {
  task: TaskDetail;
}

export function DocumentInformationCard({ task }: DocumentInformationCardProps) {
  // Extract filename from file_key if available
  return (
    <div className="bg-white border border-[rgba(0,0,0,0.1)] rounded-[14px] p-6 mb-6">
      <h2 className="text-lg font-semibold text-[#111] mb-4 flex items-center gap-2">
        <File className="w-5 h-5 text-[#038e43]" />
        Document Information
      </h2>
      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className="block text-xs font-medium text-[#6b7280] mb-1">File Name</label>
          <p className="text-sm font-medium text-[#111]">
            {task.file_metadata?.file_name || 'No document uploaded'}
          </p>
        </div>
        <div>
          <label className="block text-xs font-medium text-[#6b7280] mb-1">File Size</label>
          <p className="text-sm font-medium text-[#111]">
            {formatFileSize(task.file_metadata?.file_size as number)}
          </p>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-6 mt-4">
        <div>
          {task.document_preview_url && (
            <div className="col-span-2">
              <a
                href={task.document_preview_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-3 py-2 bg-[#038e43] text-white text-sm font-medium rounded-lg hover:bg-[#027235] transition-colors"
              >
                <File className="w-4 h-4" />
                View Document
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
