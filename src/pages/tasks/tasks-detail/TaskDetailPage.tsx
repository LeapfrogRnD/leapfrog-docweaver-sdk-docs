import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FileText } from 'lucide-react';
import { useGetTask, useExecuteTask } from '@/queries/task.query';
import { TaskStatus, TaskType } from '@/types/task.type';
import { RerunConfirmModal } from '@/components/ui/RerunConfirmModal';
import { Skeleton } from '@/components/ui';
import { useAuth } from '@/context/AuthContext';
import {
  TaskDetailHeader,
  TaskInformationCard,
  DocumentInformationCard,
  PipelineConfigurationCard,
  ExtractionFieldsCard,
  ClassificationDetailsCard,
  StatusMessageCard,
} from './components';

export default function TaskDetailPage() {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();
  const [showRerunConfirm, setShowRerunConfirm] = useState(false);

  const { user } = useAuth();

  // Convert taskId to number for API call
  const taskIdNumber = taskId ? parseInt(taskId, 10) : 0;

  // API hooks
  const { data: task, isLoading, error, refetch } = useGetTask(taskIdNumber);

  const executeTaskMutation = useExecuteTask();

  useEffect(() => {
    if (!taskId || isNaN(taskIdNumber)) {
      navigate('/tasks');
      return;
    }
  }, [taskId, taskIdNumber, navigate]);

  const handleBack = () => {
    navigate('/tasks');
  };

  const handleRerunClick = () => {
    setShowRerunConfirm(true);
  };

  const handleChangeSettings = () => {
    if (taskId) {
      navigate(`/tasks/edit/${taskId}`);
    }
  };

  const handleRerunWithSameSettings = async () => {
    if (!taskIdNumber || !task) {
      console.error('Missing taskId or task data');
      return;
    }

    try {
      await executeTaskMutation.mutateAsync(taskIdNumber);
      refetch();
      setShowRerunConfirm(false);
    } catch (error) {
      console.error('Task execution failed:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex-1 bg-[#f9fafb] overflow-auto">
        {/* Header Skeleton */}
        <div className="bg-white border-b border-[rgba(0,0,0,0.1)] px-8 py-6">
          <div className="max-w-5xl mx-auto">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <Skeleton variant="circular" width={40} height={40} />
                <div className="space-y-2">
                  <Skeleton className="h-8 w-64" />
                  <Skeleton className="h-4 w-32" />
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <Skeleton className="h-10 w-24" />
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Skeleton */}
        <div className="px-8 pt-8 pb-6 max-w-5xl mx-auto space-y-6">
          {/* Status Message Card Skeleton */}
          <div className="bg-white border border-[rgba(0,0,0,0.1)] rounded-[14px] p-6">
            <div className="flex items-center space-x-3">
              <Skeleton variant="circular" width={24} height={24} />
              <div className="flex-1 space-y-2">
                <Skeleton className="h-5 w-48" />
                <Skeleton className="h-4 w-96" />
              </div>
            </div>
          </div>

          {/* Task Information Card Skeleton */}
          <div className="bg-white border border-[rgba(0,0,0,0.1)] rounded-[14px] p-6">
            <div className="space-y-4">
              <Skeleton className="h-6 w-40" />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-5 w-48" />
                </div>
                <div className="space-y-3">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-5 w-40" />
                </div>
                <div className="space-y-3">
                  <Skeleton className="h-4 w-28" />
                  <Skeleton className="h-5 w-36" />
                </div>
                <div className="space-y-3">
                  <Skeleton className="h-4 w-20" />
                  <Skeleton className="h-5 w-32" />
                </div>
              </div>
            </div>
          </div>

          {/* Document Information Card Skeleton */}
          <div className="bg-white border border-[rgba(0,0,0,0.1)] rounded-[14px] p-6">
            <div className="space-y-4">
              <Skeleton className="h-6 w-44" />
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-3">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-5 w-24" />
                </div>
                <div className="space-y-3">
                  <Skeleton className="h-4 w-28" />
                  <Skeleton className="h-5 w-20" />
                </div>
                <div className="space-y-3">
                  <Skeleton className="h-4 w-36" />
                  <Skeleton className="h-5 w-32" />
                </div>
              </div>
            </div>
          </div>

          {/* Pipeline Configuration Card Skeleton */}
          <div className="bg-white border border-[rgba(0,0,0,0.1)] rounded-[14px] p-6">
            <div className="space-y-4">
              <Skeleton className="h-6 w-48" />
              <div className="space-y-4">
                <div className="space-y-2">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-20 w-full" />
                </div>
                <div className="space-y-2">
                  <Skeleton className="h-4 w-28" />
                  <Skeleton className="h-16 w-full" />
                </div>
              </div>
            </div>
          </div>

          {/* Extraction Fields Card Skeleton */}
          <div className="bg-white border border-[rgba(0,0,0,0.1)] rounded-[14px] p-6">
            <div className="space-y-4">
              <Skeleton className="h-6 w-36" />
              <div className="space-y-3">
                {Array.from({ length: 4 }).map((_, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 border border-gray-200 rounded-lg"
                  >
                    <div className="flex-1 space-y-2">
                      <Skeleton className="h-4 w-32" />
                      <Skeleton className="h-3 w-48" />
                    </div>
                    <Skeleton className="h-8 w-16" />
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Classification Categories Card Skeleton */}
          <div className="bg-white border border-[rgba(0,0,0,0.1)] rounded-[14px] p-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Skeleton className="h-6 w-48" />
                <Skeleton className="h-10 w-32" />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Array.from({ length: 6 }).map((_, index) => (
                  <div key={index} className="p-4 border border-gray-200 rounded-lg">
                    <div className="space-y-3">
                      <Skeleton className="h-5 w-24" />
                      <Skeleton className="h-4 w-32" />
                      <Skeleton className="h-3 w-20" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !task) {
    return (
      <div className="flex-1 bg-[#f9fafb] flex items-center justify-center">
        <div className="text-center">
          <FileText className="w-16 h-16 text-[#6b7280] mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-[#111] mb-2">Task Not Found</h2>
          <p className="text-sm text-[#6b7280] mb-4">
            {error ? `Error: ${error}` : 'Unable to find the task details.'}
          </p>
          <button
            onClick={handleBack}
            className="px-4 py-2 bg-[#038e43] text-white text-sm font-medium rounded-lg hover:bg-[#027235] transition-colors"
          >
            Back to Tasks
          </button>
        </div>
      </div>
    );
  }

  const isReprocessing = executeTaskMutation.isPending || task.status === TaskStatus.PROCESSING;

  return (
    <div className="flex-1 bg-[#f9fafb] overflow-auto min-h-screen mx-auto">
      {/* Processing Overlay */}
      {/* <ProcessingOverlay isReprocessing={isReprocessing} task={task} /> */}

      <TaskDetailHeader
        onBack={handleBack}
        task={task}
        isReprocessing={isReprocessing}
        onRerunClick={handleRerunClick}
      />

      {/* Main Content */}
      <div className="px-8 pt-8 pb-6 max-w-5xl mx-auto space-y-6">
        <StatusMessageCard task={task} />

        <TaskInformationCard task={task} />

        <DocumentInformationCard task={task} />

        <PipelineConfigurationCard task={task} />

        {task.task_type === TaskType.EXTRACTION && <ExtractionFieldsCard task={task} />}
        {task.task_type === TaskType.CLASSIFICATION && <ClassificationDetailsCard task={task} />}
      </div>

      <RerunConfirmModal
        isOpen={showRerunConfirm}
        onClose={() => setShowRerunConfirm(false)}
        onRerunWithSameSettings={handleRerunWithSameSettings}
        onChangeSettings={handleChangeSettings}
        taskName={task?.name}
        isOwnedByCurrentUser={task?.created_by === user?.id}
      />
    </div>
  );
}
