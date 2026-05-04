import { FileText } from 'lucide-react';
import { TaskDetail, TaskStatus } from '@/types/task.type';
import { formatDate } from '@/utils';
import { TaskStatusBadge } from '../../task-list/components/TaskStatusBadge';

interface TaskInformationCardProps {
  task: TaskDetail;
}

export function TaskInformationCard({ task }: TaskInformationCardProps) {
  return (
    <div className="bg-white border border-[rgba(0,0,0,0.1)] rounded-[14px] p-6 mb-6">
      <h2 className="text-lg font-semibold text-[#111] mb-4 flex items-center gap-2">
        <FileText className="w-5 h-5 text-[#038e43]" />
        Task Information
      </h2>
      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className="block text-xs font-medium text-[#6b7280] mb-1">Task Name</label>
          <p className="text-sm font-medium text-[#111]">{task.name || 'Untitled Task'}</p>
        </div>
        <div>
          <label className="block text-xs font-medium text-[#6b7280] mb-1">Status</label>
          <p className="text-sm font-medium text-[#111] capitalize">
            {' '}
            <TaskStatusBadge status={task.status} />
          </p>
        </div>
        <div>
          <label className="block text-xs font-medium text-[#6b7280] mb-1">Created</label>
          <p className="text-sm font-medium text-[#111]">{formatDate(task.created_at)}</p>
        </div>
        <div>
          <label className="block text-xs font-medium text-[#6b7280] mb-1">Task ID</label>
          <p className="text-sm font-medium text-[#111] font-mono">{task.id}</p>
        </div>
        <div>
          <label className="block text-xs font-medium text-[#6b7280] mb-1">Task Type</label>
          <p className="text-sm font-medium text-[#111] capitalize">{task.task_type || 'N/A'}</p>
        </div>
        <div>
          <label className="block text-xs font-medium text-[#6b7280] mb-1">Last Updated</label>
          <p className="text-sm font-medium text-[#111]">
            {task.updated_at ? formatDate(task.updated_at) : 'Never'}
          </p>
        </div>
        {task.failed_remarks && task.status == TaskStatus.FAILED && (
          <div>
            <label className="block text-xs font-medium text-[#6b7280] mb-1">Failed Remarks</label>
            <p className="text-sm font-medium text-[#111]">
              {task.failed_remarks ? task.failed_remarks : 'N/A'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
