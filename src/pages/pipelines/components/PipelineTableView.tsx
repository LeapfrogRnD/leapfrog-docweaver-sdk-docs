import * as React from 'react';
import { Pipeline } from '@/types/pipeline.type';
import { TableRow, TableCell } from '@/components/ui';
import { Edit, Trash2, Copy, MoreVertical } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';
import { createPortal } from 'react-dom';
import {
  getOcrProviderLabel,
  getLlmProviderLabel,
  getLlmModelLabel,
  getVlmModelLabel,
  formatDate,
} from '@/utils';
import { Switch } from '@/components/ui/Switch';
import { DataTable, StatusFilterConfig } from '@/components/DataTable';
import { UsePaginationReturn } from '@/hooks/usePagination';

interface PipelineTableViewProps {
  pipelines: Pipeline[];
  onEdit: (pipeline: Pipeline) => void;
  onDelete: (id: number) => void;
  onDuplicate: (id: number) => void;
  onToggleStatus: (id: number) => void;
  user: { id: number; role: string | null } | null;
  isLoading?: boolean;
  search?: string;
  pagination?: UsePaginationReturn;
  onSearch?: (value: string) => void;
  statusFilter?: StatusFilterConfig;
  openMenuId: number | null;
  setOpenMenuId: React.Dispatch<React.SetStateAction<number | null>>;
}

export function PipelineTableView({
  pipelines,
  onEdit,
  onDelete,
  onDuplicate,
  onToggleStatus,
  user,
  isLoading,
  search,
  onSearch,
  statusFilter,
  pagination,
  openMenuId,
  setOpenMenuId,
}: PipelineTableViewProps) {
  const columns = ['Name', 'LLM Provider', 'OCR Provider', 'Last Updated', 'Status', 'Actions'];
  return (
    <DataTable<Pipeline>
      title="Available Pipelines"
      data={pipelines}
      columns={columns}
      isLoading={isLoading}
      search={search}
      onSearch={onSearch}
      statusFilter={statusFilter}
      pagination={pagination}
      renderRow={(pipeline) => {
        const isOwnedByUser = user && pipeline.created_by === user.id;
        const isSuperUser = user && user.role === 'superadmin';
        const canManage = isOwnedByUser || isSuperUser;

        return (
          <TableRow key={pipeline.id}>
            {/* Pipeline Name */}
            <TableCell>
              <div className="flex flex-col">
                <span className="text-sm font-semibold text-[#101828]">{pipeline.name}</span>
                {pipeline.description && (
                  <p className="text-xs text-[#6a7282] line-clamp-1">{pipeline.description}</p>
                )}
              </div>
            </TableCell>

            {/* LLM Provider */}
            <TableCell>
              <div className="flex flex-col">
                <span className="text-sm text-[#101828]">
                  {getLlmProviderLabel(pipeline.llm_model_provider)}
                </span>
                <span className="text-xs text-[#6a7282]">
                  {getLlmModelLabel(pipeline.llm_model_provider, pipeline.llm_model)}
                </span>
              </div>
            </TableCell>

            {/* OCR Provider */}
            <TableCell>
              <div className="flex flex-col">
                <span className="text-sm text-[#101828]">
                  {getOcrProviderLabel(pipeline.ocr_provider)}
                </span>
                {pipeline.ocr_provider === 'vlm' && pipeline.vlm_model && (
                  <span className="text-xs text-[#6a7282]">
                    {getVlmModelLabel(pipeline.vlm_model_provider, pipeline.vlm_model)}
                  </span>
                )}
              </div>
            </TableCell>

            {/* Date */}
            <TableCell>
              <span className="text-sm text-[#6a7282]">
                {formatDate(pipeline.updated_at || pipeline.created_at, true)}
              </span>
            </TableCell>

            {/* Status */}
            <TableCell>
              {!pipeline.is_default ? (
                <div className="flex items-center gap-3">
                  <Switch
                    checked={pipeline.is_active}
                    onCheckedChange={() => canManage && onToggleStatus(pipeline.id)}
                    disabled={!canManage}
                  />
                </div>
              ) : (
                <span className="text-xs text-[#9ca3af] font-medium">Default</span>
              )}
            </TableCell>

            {/* Actions */}
            <TableCell className="text-right">
              {!pipeline.is_default && (
                <PipelineActions
                  pipeline={pipeline}
                  canManage={!!canManage}
                  onEdit={onEdit}
                  onDelete={onDelete}
                  onDuplicate={onDuplicate}
                  openMenuId={openMenuId}
                  setOpenMenuId={setOpenMenuId}
                />
              )}
            </TableCell>
          </TableRow>
        );
      }}
    />
  );
}
/**
 * Sub-component for Row Actions (Popover logic)
 */
function PipelineActions({
  pipeline,
  onEdit,
  onDelete,
  onDuplicate,
  canManage,
  openMenuId,
  setOpenMenuId,
}: {
  pipeline: Pipeline;
  canManage: boolean;
  onEdit: (p: Pipeline) => void;
  onDelete: (id: number) => void;
  onDuplicate: (id: number) => void;
  openMenuId: number | null;
  setOpenMenuId: React.Dispatch<React.SetStateAction<number | null>>;
}) {
  const [menuPos, setMenuPos] = useState<{ top: number; left: number } | null>(null);
  const triggerRef = useRef<HTMLButtonElement | null>(null);

  const isOpen = openMenuId === pipeline.id;

  const handleToggleMenu = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    e.stopPropagation();

    if (!isOpen && triggerRef.current) {
      const rect = triggerRef.current.getBoundingClientRect();
      const spaceBelow = window.innerHeight - rect.bottom;

      const top = spaceBelow < 120 ? rect.top - 90 : rect.bottom + 4;

      setMenuPos({
        top,
        left: rect.right - 160,
      });
    }

    setOpenMenuId((prev: number | null) => (prev === pipeline.id ? null : pipeline.id));
  };

  useEffect(() => {
    if (!isOpen) return;

    const close = () => setOpenMenuId(null);
    window.addEventListener('click', close);

    return () => window.removeEventListener('click', close);
  }, [isOpen, setOpenMenuId]);

  return (
    <div className="flex items-center justify-start gap-1" onClick={(e) => e.stopPropagation()}>
      <button
        title="Duplicate"
        type="button"
        onClick={(e) => {
          e.stopPropagation();
          onDuplicate(pipeline.id);
        }}
        className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
      >
        <Copy className="w-4 h-4 text-gray-500" />
      </button>

      {canManage && (
        <button
          ref={triggerRef}
          type="button"
          onClick={handleToggleMenu}
          aria-expanded={isOpen}
          className="p-2 rounded-lg transition-colors hover:bg-gray-100 aria-[expanded=true]:bg-gray-100"
        >
          <MoreVertical className="w-4 h-4 text-gray-500" />
        </button>
      )}

      {/* Menu (UNCHANGED except isOpen logic) */}
      {isOpen &&
        menuPos &&
        createPortal(
          <div
            style={{
              position: 'fixed',
              top: menuPos.top,
              left: menuPos.left,
              width: 160,
              zIndex: 9999,
            }}
            className="bg-white border rounded-xl shadow-xl overflow-hidden py-1"
            onClick={(e) => e.stopPropagation()}
            onMouseDown={(e) => e.stopPropagation()}
          >
            <button
              type="button"
              onMouseDown={(e) => e.stopPropagation()}
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                onEdit(pipeline);
                setOpenMenuId(null);
              }}
              className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 text-left"
            >
              <Edit className="w-4 h-4" /> Edit
            </button>

            <button
              type="button"
              onMouseDown={(e) => e.stopPropagation()}
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                onDelete(pipeline.id);
                setOpenMenuId(null);
              }}
              className="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 text-left"
            >
              <Trash2 className="w-4 h-4" /> Delete
            </button>
          </div>,
          document.body
        )}
    </div>
  );
}
