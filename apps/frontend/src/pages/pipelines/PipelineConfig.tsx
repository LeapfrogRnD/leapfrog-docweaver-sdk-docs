import { useState } from 'react';
import { ConfirmDialog, StatsSkeleton } from '@/components/ui';
import { PageHeader } from '@/components';
import { PipelineStatsCards } from './components/PipelineStatsCards';
import { PipelineTableView } from './components/PipelineTableView';
import { PipelineModal } from './components/PipelineModal';
import { Plus, Settings } from 'lucide-react';
import { Pipeline } from '@/types/pipeline.type';
import {
  useGetPipelines,
  useDeletePipeline,
  useDuplicatePipeline,
  useTogglePipelineStatus,
  useGetPipelineStats,
} from '@/queries/pipeline.query';
import { useToast } from '@/context/ToastContext';
import { usePagination } from '@/hooks/usePagination';
import { useAuth } from '@/context/AuthContext';

export function PipelineConfigPage() {
  const [openMenuId, setOpenMenuId] = useState<number | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPipeline, setEditingPipeline] = useState<Pipeline | null>(null);
  const [search, setSearch] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [deleteConfirm, setDeleteConfirm] = useState<{
    isOpen: boolean;
    pipeline: Pipeline | null;
  }>({
    isOpen: false,
    pipeline: null,
  });

  const { showToast } = useToast();
  const { user } = useAuth();
  const pagination = usePagination();

  // Queries
  const {
    data: pipelinesData,
    isLoading,
    error,
  } = useGetPipelines(pagination.page, pagination.pageSize, statusFilter, search);

  const { data: statsData, isLoading: isloadingStats } = useGetPipelineStats();
  const deleteMutation = useDeletePipeline();
  const duplicateMutation = useDuplicatePipeline();
  const toggleStatusMutation = useTogglePipelineStatus();

  // Update pagination metadata when data changes
  if (pipelinesData?.metadata && pagination.metadata !== pipelinesData.metadata) {
    pagination.setMetadata(pipelinesData.metadata);
  }

  const pipelines = pipelinesData?.data || [];

  const handleCreate = () => {
    setEditingPipeline(null);
    setIsModalOpen(true);
  };

  const handleEdit = (pipeline: Pipeline) => {
    setEditingPipeline(pipeline);
    setIsModalOpen(true);
  };

  const handleDelete = async (id: number) => {
    const pipelineToDelete = pipelines.find((p) => p.id === id);
    if (!pipelineToDelete) return;

    setDeleteConfirm({ isOpen: true, pipeline: pipelineToDelete });
  };

  const confirmDelete = async () => {
    if (!deleteConfirm.pipeline) return;

    try {
      await deleteMutation.mutateAsync(deleteConfirm.pipeline.id);
      showToast('Pipeline deleted successfully', 'success');
      setDeleteConfirm({ isOpen: false, pipeline: null });
    } catch (error) {
      showToast(error instanceof Error ? error.message : 'Failed to delete pipeline', 'error');
    }
  };

  const cancelDelete = () => {
    setDeleteConfirm({ isOpen: false, pipeline: null });
  };

  const handleDuplicate = async (id: number) => {
    try {
      await duplicateMutation.mutateAsync(id);
      showToast('Pipeline duplicated successfully', 'success');
    } catch (error) {
      showToast(error instanceof Error ? error.message : 'Failed to duplicate pipeline', 'error');
    }
  };

  const handleToggleStatus = async (id: number) => {
    try {
      await toggleStatusMutation.mutateAsync(id);
      showToast('Pipeline status updated successfully', 'success');
    } catch (error) {
      showToast(
        error instanceof Error ? error.message : 'Failed to toggle pipeline status',
        'error'
      );
    }
  };

  // Calculate stats
  const totalPipelines = statsData?.total || 0;
  const lastUpdated = statsData?.last_updated || '';
  if (error) {
    return (
      <div className="bg-[#f9fafb] min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600">Error loading pipelines: {error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 bg-[#f9fafb] overflow-auto mx-auto min-h-screen">
      <PageHeader
        icon={<Settings className="w-6 h-6" />}
        title="Pipeline Settings"
        description="Create and manage custom OCR extraction pipelines"
        actions={
          <button
            onClick={handleCreate}
            className="h-9 px-2 sm:px-3 bg-[#038e43] text-white text-xs sm:text-sm font-medium rounded-lg flex items-center gap-1 sm:gap-2 hover:bg-[#027235] transition-colors flex-shrink-0 w-full sm:w-auto justify-center"
          >
            <Plus className="w-4 h-4" />
            <span className="hidden sm:inline">Create New Pipeline</span>
            <span className="sm:hidden">Create</span>
          </button>
        }
      />

      {/* Content */}
      <div className="px-4 sm:px-8 pt-8 pb-12">
        {/* Stats Cards */}
        {isloadingStats ? (
          <StatsSkeleton cards={2} />
        ) : (
          <PipelineStatsCards totalPipelines={totalPipelines} lastUpdated={lastUpdated} />
        )}

        {/* All Pipelines Section */}
        <div className="space-y-4">
          <PipelineTableView
            pipelines={pipelines}
            onEdit={handleEdit}
            onDelete={handleDelete}
            onDuplicate={handleDuplicate}
            onToggleStatus={handleToggleStatus}
            user={user}
            isLoading={isLoading}
            search={search}
            onSearch={(val) => {
              setSearch(val);
              pagination.setPage(1);
            }}
            statusFilter={{
              value: statusFilter,
              onChange: (val) => {
                setStatusFilter(val);
                pagination.setPage(1);
              },
              placeholder: 'All Status',
              options: [
                { label: 'All Status', value: 'all' },
                { label: 'Active', value: 'active' },
                { label: 'Inactive', value: 'inactive' },
              ],
            }}
            openMenuId={openMenuId}
            setOpenMenuId={setOpenMenuId}
            pagination={pagination}
          />
        </div>
      </div>

      {/* Pipeline Modal */}
      <PipelineModal
        isOpen={isModalOpen}
        setIsOpen={setIsModalOpen}
        setEditingPipeline={setEditingPipeline}
        onClose={() => {
          setIsModalOpen(false);
          setEditingPipeline(null);
        }}
        pipeline={editingPipeline}
      />

      {/* Confirm Dialog */}
      <ConfirmDialog
        iconExist={false}
        isOpen={deleteConfirm.isOpen}
        onClose={cancelDelete}
        onConfirm={confirmDelete}
        title="Delete Pipeline"
        description={
          deleteConfirm.pipeline ? (
            <>
              Are you sure you want to delete the pipeline{' '}
              <strong>"{deleteConfirm.pipeline.name}"</strong>? This action cannot be undone and may
              affect any active processes using this pipeline.
            </>
          ) : (
            'Are you sure you want to delete this pipeline?'
          )
        }
        confirmText="Delete Pipeline"
        cancelText="Cancel"
        variant="danger"
        isLoading={deleteMutation.isPending}
      />
    </div>
  );
}
