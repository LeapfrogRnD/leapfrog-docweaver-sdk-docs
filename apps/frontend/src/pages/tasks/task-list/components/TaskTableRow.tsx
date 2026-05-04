import { Edit, Play, Copy, Trash2, Clock2, MoreVertical, Eye } from 'lucide-react';
import { TaskListItem, TaskStatus } from '@/types/task.type';
import { TaskStatusBadge } from './TaskStatusBadge';
import { TableRow, TableCell } from '@/components/ui/Table';
import { useNavigate } from 'react-router-dom';
import { useDuplicateTask, useExecuteTask } from '@/queries/task.query';
import { useToast } from '@/context/ToastContext';
import { useTaskStore } from '@/store';
import { useAuth } from '@/context/AuthContext';
import { ConfirmDialog } from '@/components/ui';
import { useState, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';

interface TaskTableRowProps {
  task: TaskListItem;
  totalProcessingTasks?: number;
  onDelete: (task: TaskListItem) => void;
  openMenuId: number | null;
  setOpenMenuId: React.Dispatch<React.SetStateAction<number | null>>;
}

export function TaskTableRow({
  task,
  totalProcessingTasks,
  onDelete,
  openMenuId,
  setOpenMenuId,
}: TaskTableRowProps) {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const { clearTaskCreation } = useTaskStore();
  const { user } = useAuth();
  const [menuPos, setMenuPos] = useState<{ top: number; left: number } | null>(null);
  const [isConfirmOpen, setIsConfirmOpen] = useState(false);
  const [pendingDuplicateTaskId, setPendingDuplicateTaskId] = useState<number | null>(null);

  const menuRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const popoverRef = useRef<HTMLDivElement>(null);

  const MENU_HEIGHT = 140;
  const MENU_WIDTH = 160;

  const isOpen = openMenuId === task.id;

  const handleToggleMenu = (e?: React.MouseEvent) => {
    e?.stopPropagation();

    if (!isOpen && triggerRef.current) {
      const rect = triggerRef.current.getBoundingClientRect();
      const spaceBelow = window.innerHeight - rect.bottom;

      const top = spaceBelow < MENU_HEIGHT ? rect.top - MENU_HEIGHT - 4 : rect.bottom + 4;

      const left = rect.right - MENU_WIDTH;

      setMenuPos({ top, left });
    }

    setOpenMenuId((prev) => (prev === task.id ? null : task.id));
  };

  // Close on outside click
  useEffect(() => {
    if (!isOpen) return;

    const handleClickOutside = (e: MouseEvent) => {
      if (
        menuRef.current &&
        !menuRef.current.contains(e.target as Node) &&
        triggerRef.current &&
        !triggerRef.current.contains(e.target as Node) &&
        popoverRef.current &&
        !popoverRef.current.contains(e.target as Node)
      ) {
        setOpenMenuId(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen, setOpenMenuId]);

  const isOwner = user?.id === task.created_by || user?.role == 'superadmin';
  const isSuperUser = user?.role == 'superadmin';
  const isAdmin = user?.role == 'admin';
  const canEdit = isOwner;
  const canDelete = isOwner;
  const canRun = isOwner && task.status !== 'draft';

  const isProcessingOrQueued = [TaskStatus.PROCESSING, TaskStatus.QUEUED].includes(task.status);

  const executeTaskMutation = useExecuteTask();
  const duplicateTaskMutation = useDuplicateTask();

  const handleView = (taskId: number) => {
    if (task.status === TaskStatus.COMPLETED) {
      navigate(`/tasks/${taskId}/result`);
      return;
    }
    navigate(`/tasks/${taskId}`);
  };

  const handleEdit = (taskId: number) => {
    clearTaskCreation();
    navigate(`/tasks/${taskId}/edit`);
  };

  const handleRun = async (taskId: number) => {
    try {
      await executeTaskMutation.mutateAsync(taskId);
      showToast('Task execution started', 'success');
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : typeof error === 'string'
            ? error
            : 'Failed to execute task';
      showToast(message, 'error');
    }
  };

  const handleCopy = (taskId: number) => {
    setOpenMenuId(null);
    setPendingDuplicateTaskId(taskId);
    setIsConfirmOpen(true);
  };

  const handleConfirmDuplicate = async () => {
    if (pendingDuplicateTaskId === null) return;
    try {
      await duplicateTaskMutation.mutateAsync(pendingDuplicateTaskId);
      showToast('Task duplicated', 'success');
    } catch {
      showToast('Failed to duplicate task', 'error');
    } finally {
      setIsConfirmOpen(false);
      setPendingDuplicateTaskId(null);
    }
  };

  const handleDelete = () => {
    setOpenMenuId(null);
    onDelete(task);
  };

  return (
    <TableRow className="hover:bg-gray-50">
      <TableCell>
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-[#101828] truncate">{task.name}</span>
        </div>
      </TableCell>
      <TableCell>
        {task.task_type ? (
          <span className="px-2 py-1 text-xs font-medium text-[#111] bg-[#f3f4f6] rounded-lg capitalize">
            {task.task_type}
          </span>
        ) : (
          <span className="text-xs text-[#6b7280]">-</span>
        )}
      </TableCell>
      <TableCell className="min-w-0">
        <TaskStatusBadge status={task.status} />
      </TableCell>
      <TableCell>
        <span className="text-xs">
          {isProcessingOrQueued && typeof task.task_rank === 'number'
            ? `${task.task_rank}/${totalProcessingTasks || 0}`
            : '-'}
        </span>
      </TableCell>
      <TableCell>
        <span className="text-sm text-[#4a5565]">{task.created_by_fullname || '-'}</span>
      </TableCell>
      <TableCell>
        <span className="text-sm text-[#4a5565]">{task.updated_at}</span>
      </TableCell>
      <TableCell>
        <div className="flex items-center gap-1">
          {/* Run / spinner — owner only */}
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleView(task.id);
            }}
            className="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-gray-100"
          >
            <Eye className="w-4 h-4 text-gray-500" />
          </button>
          {canRun && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                if (!isProcessingOrQueued) handleRun(task.id);
              }}
              className="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-gray-100"
            >
              {isProcessingOrQueued ? (
                <Clock2 className="w-4 h-4 animate-spin text-blue-600" />
              ) : (
                <Play className="w-4 h-4 text-gray-500" />
              )}
            </button>
          )}

          {/* Menu */}
          {((isOwner && !isProcessingOrQueued) ||
            isSuperUser ||
            (isAdmin && !isProcessingOrQueued)) && (
            <div ref={menuRef}>
              <button
                ref={triggerRef}
                onClick={handleToggleMenu}
                onMouseDown={(e) => e.stopPropagation()}
                aria-expanded={isOpen}
                className={`w-9 h-9 flex items-center justify-center rounded-lg transition-colors
                  hover:bg-gray-100
                  ${isOpen ? 'bg-gray-200' : ''}`}
                title="More actions"
              >
                <MoreVertical className="w-4 h-4 text-gray-500" />
              </button>

              {isOpen &&
                menuPos &&
                createPortal(
                  <div
                    ref={popoverRef}
                    style={{
                      position: 'fixed',
                      top: menuPos.top,
                      left: menuPos.left,
                      width: MENU_WIDTH,
                      zIndex: 9999,
                    }}
                    className="bg-white border border-[rgba(0,0,0,0.1)] rounded-xl shadow-lg overflow-hidden"
                  >
                    {canEdit && !isProcessingOrQueued && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setOpenMenuId(null);
                          handleEdit(task.id);
                        }}
                        className="flex items-center gap-2 w-full px-4 py-2.5 text-sm text-[#374151] hover:bg-gray-50 transition-colors"
                      >
                        <Edit className="w-4 h-4 text-[#6b7280]" />
                        Edit
                      </button>
                    )}

                    {(!isProcessingOrQueued || isSuperUser) && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleCopy(task.id);
                        }}
                        className="flex items-center gap-2 w-full px-4 py-2.5 text-sm text-[#374151] hover:bg-gray-50 transition-colors"
                      >
                        <Copy className="w-4 h-4 text-[#6b7280]" />
                        Duplicate
                      </button>
                    )}

                    {canDelete && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete();
                        }}
                        className="flex items-center gap-2 w-full px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                        Delete
                      </button>
                    )}
                  </div>,
                  document.body
                )}
            </div>
          )}
        </div>
      </TableCell>

      <ConfirmDialog
        iconExist={false}
        isOpen={isConfirmOpen}
        onClose={() => setIsConfirmOpen(false)}
        onConfirm={handleConfirmDuplicate}
        title="Duplicate task?"
        description="Are you sure?"
        confirmText="Duplicate"
        variant="info"
        isLoading={duplicateTaskMutation.status === 'pending'}
      />
    </TableRow>
  );
}
