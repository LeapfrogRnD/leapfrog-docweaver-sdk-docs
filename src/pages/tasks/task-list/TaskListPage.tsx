import { useState } from 'react';
import { ListTodo, Plus, RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useGetTasks, useDeleteTask, useGetTaskStats } from '@/queries/task.query';
import { TaskListItem, TaskStatus } from '@/types/task.type';
import { TaskStatsCards } from './components/TaskStatsCards';
import { usePagination } from '@/hooks/usePagination';
import { ConfirmDialog, StatsSkeleton } from '@/components/ui';
import { useToast } from '@/context/ToastContext';
import { useTaskStore } from '@/store';
import clsx from 'clsx';
import { PageHeader } from '@/components';

import { TaskTableRow } from './components/TaskTableRow';
import { DataTable } from '@/components/DataTable';

export function TaskListPage() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<TaskStatus | 'all'>('all');
  const [openMenuId, setOpenMenuId] = useState<number | null>(null);

  const [deleteConfirm, setDeleteConfirm] = useState<{
    isOpen: boolean;
    task: TaskListItem | null;
  }>({
    isOpen: false,
    task: null,
  });

  const pagination = usePagination();
  const deleteTaskMutation = useDeleteTask();

  const {
    data: taskStats,
    isLoading: isStatsLoading,
    refetch: refetchTasksStats,
  } = useGetTaskStats();

  const {
    data: tasksData,
    isLoading,
    error,
    refetch: refetchTasks,
  } = useGetTasks(pagination.page, pagination.pageSize, {
    search: searchQuery,
    status: statusFilter !== 'all' ? statusFilter : null,
  });

  const { clearTaskCreation } = useTaskStore();

  if (tasksData?.metadata && pagination.metadata !== tasksData.metadata) {
    pagination.setMetadata(tasksData.metadata);
  }

  const totalProcessingTasks = (taskStats?.processing || 0) + (taskStats?.queued || 0);
  const tasks = tasksData?.data || [];

  const handleCreateTask = () => {
    clearTaskCreation();
    navigate('/tasks/create');
  };

  const handleRefresh = async () => {
    try {
      setIsRefreshing(true);
      await Promise.all([refetchTasks(), refetchTasksStats()]);
    } finally {
      setIsRefreshing(false);
    }
  };

  const confirmDelete = async () => {
    if (!deleteConfirm.task) return;
    try {
      await deleteTaskMutation.mutateAsync(deleteConfirm.task.id);
      showToast('Task deleted successfully', 'success');
      setDeleteConfirm({ isOpen: false, task: null });
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Failed to delete task', 'error');
    }
  };

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">Failed to load tasks</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-[#038e43] text-white rounded-lg hover:bg-[#027a3a]"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const columns = ['Task Name', 'Type', 'Status', 'Rank', 'Created By', 'Updated At', 'Actions'];

  return (
    <div className="flex-1 bg-[#f9fafb] overflow-auto min-h-screen mx-auto">
      <PageHeader
        icon={<ListTodo className="w-6 h-6" />}
        title="Task Management"
        description="Manage your OCR document processing tasks"
        actions={
          <>
            <button
              onClick={handleRefresh}
              className="h-9 px-3 bg-white border border-[#d1d5db] rounded-lg hover:bg-gray-50 transition-colors"
            >
              <RefreshCw className={clsx('w-4 h-4', isRefreshing && 'animate-spin')} />
            </button>
            <button
              onClick={handleCreateTask}
              className="h-9 px-2 sm:px-3 bg-[#038e43] text-white text-xs sm:text-sm font-medium rounded-lg flex items-center gap-1 sm:gap-2 hover:bg-[#027235] transition-colors flex-shrink-0 w-full sm:w-auto justify-center"
            >
              <Plus className="w-4 h-4" />
              <span className="hidden sm:inline">Create New Task</span>
              <span className="sm:hidden">Create</span>
            </button>
          </>
        }
      />

      <div className="px-4 sm:px-8 pt-8 pb-6">
        {/* Stats Section */}
        {isStatsLoading ? (
          <StatsSkeleton cards={4} />
        ) : (
          taskStats && <TaskStatsCards taskStats={taskStats} />
        )}

        <div className="mt-8">
          <DataTable<TaskListItem>
            title="Recent Tasks"
            description="A list of your recent document processing tasks and their current status."
            data={tasks}
            columns={columns}
            isLoading={isLoading || isRefreshing}
            pagination={pagination}
            search={searchQuery}
            onSearch={(val) => {
              setSearchQuery(val);
              pagination.setPage(1);
            }}
            statusFilter={{
              value: statusFilter,
              onChange: (val) => {
                setStatusFilter(val as TaskStatus | 'all');
                pagination.setPage(1);
              },
              placeholder: 'All Status',
              options: [
                { label: 'All Status', value: 'all' },
                { label: 'Draft', value: TaskStatus.DRAFT },
                { label: 'Ready', value: TaskStatus.READY },
                { label: 'Queued', value: TaskStatus.QUEUED },
                { label: 'Processing', value: TaskStatus.PROCESSING },
                { label: 'Completed', value: TaskStatus.COMPLETED },
                { label: 'Failed', value: TaskStatus.FAILED },
              ],
            }}
            renderRow={(task) => (
              <TaskTableRow
                key={task.id}
                task={task}
                onDelete={(t) => setDeleteConfirm({ isOpen: true, task: t })}
                totalProcessingTasks={totalProcessingTasks}
                openMenuId={openMenuId}
                setOpenMenuId={setOpenMenuId}
              />
            )}
          />
        </div>

        {/* Delete Confirmation */}
        <ConfirmDialog
          iconExist={false}
          isOpen={deleteConfirm.isOpen}
          onClose={() => setDeleteConfirm({ isOpen: false, task: null })}
          onConfirm={confirmDelete}
          title="Delete Task"
          description={
            deleteConfirm.task && (
              <>
                Are you sure you want to delete <strong>"{deleteConfirm.task.name}"</strong>? This
                action is permanent.
              </>
            )
          }
          confirmText="Delete Task"
          variant="danger"
          isLoading={deleteTaskMutation.isPending}
        />
      </div>
    </div>
  );
}
