import { Clock } from 'lucide-react';
import { TaskDetail } from '@/types/task.type';

interface ProcessingOverlayProps {
  isReprocessing: boolean;
  task: TaskDetail;
}

export function ProcessingOverlay({ isReprocessing, task }: ProcessingOverlayProps) {
  if (!isReprocessing) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-[14px] p-8 max-w-md w-full mx-4 shadow-2xl">
        <div className="text-center">
          <div className="w-16 h-16 bg-[#038e43] rounded-full flex items-center justify-center mx-auto mb-4">
            <Clock className="w-8 h-8 text-white animate-spin" />
          </div>
          <h2 className="text-xl font-semibold text-[#111] mb-2">Processing Task</h2>
          <p className="text-sm text-[#6b7280] mb-4">Please wait while we process your task...</p>
          <div className="bg-[#f3f4f6] rounded-lg p-4 mb-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-[#6b7280]">Task:</span>
              <span className="text-xs font-medium text-[#111]">{task.name || 'N/A'}</span>
            </div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-[#6b7280]">Type:</span>
              <span className="text-xs font-medium text-[#111] capitalize">
                {task.task_type || 'N/A'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-[#6b7280]">Status:</span>
              <span className="text-xs font-medium text-[#155dfc]">Processing...</span>
            </div>
          </div>
          <div className="w-full bg-[#e5e7eb] rounded-full h-2 overflow-hidden">
            <div
              className="h-full bg-[#038e43] rounded-full animate-pulse"
              style={{ width: '60%' }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
}
