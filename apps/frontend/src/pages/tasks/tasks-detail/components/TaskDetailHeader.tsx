import { ArrowLeft, Clock, ListTodo, RotateCw } from 'lucide-react';
import { TaskDetail, TaskStatus } from '@/types/task.type';
import { useAuth } from '@/context/AuthContext';
import { Roles } from '@/types/types';
import { PageHeader } from '@/components';

interface TaskDetailHeaderProps {
  onBack: () => void;
  task: TaskDetail;
  isReprocessing: boolean;
  onRerunClick: () => void;
}

export function TaskDetailHeader({
  onBack,
  task,
  isReprocessing,
  onRerunClick,
}: TaskDetailHeaderProps) {
  const { user } = useAuth();
  const getRunButton = () => {
    if (
      [TaskStatus.FAILED, TaskStatus.COMPLETED, TaskStatus.READY].includes(task.status) &&
      (task.created_by === user?.id || user?.role === Roles.Admin)
    ) {
      return (
        <button
          onClick={onRerunClick}
          disabled={isReprocessing}
          className="h-9 px-4 bg-[#038e43] text-white text-sm font-medium rounded-lg flex items-center gap-2 hover:bg-[#027235] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          title={isReprocessing ? 'Processing...' : 'Re-run task processing'}
        >
          {isReprocessing ? (
            <Clock className="w-4 h-4 animate-spin" />
          ) : (
            <RotateCw className="w-4 h-4" />
          )}
          {isReprocessing ? 'Processing...' : 'Re-run Task'}
        </button>
      );
    }
  };
  return (
    <PageHeader
      icon={<ListTodo className="w-6 h-6" />}
      title="Task Details"
      description="View task configuration and status"
      actions={
        <>
          <button
            onClick={onBack}
            className="w-9 h-9 flex items-center justify-center rounded-lg border border-[rgba(0,0,0,0.1)] hover:bg-[#f3f4f6] transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-[#6b7280]" />
          </button>
          {getRunButton()}
        </>
      }
    />
  );
}
