import { useState, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { ApiKey } from '@/types/api-key.type';
import { TableRow, TableCell } from '@/components/ui';
import { Switch } from '@/components/ui/Switch';
import { Copy, Trash2, Edit, List, RefreshCcw, MoreVertical } from 'lucide-react';
import { useToast } from '@/context/ToastContext';
import { maskApiKey, formatDate } from '@/utils';
import { useNavigate } from 'react-router-dom';

interface ApiKeyTableRowProps {
  apiKey: ApiKey;
  onDelete: (id: number) => void;
  onEdit: (id: number) => void;
  onRegenerate: (id: number) => void;
  onToggleStatus: (id: number) => void;
  canManage: boolean;
  openMenuId: number | null;
  onToggleMenu: (id: number | null) => void;
}

export function ApiKeyTableRow({
  apiKey,
  onDelete,
  onEdit,
  onRegenerate,
  onToggleStatus,
  canManage,
  openMenuId,
  onToggleMenu,
}: ApiKeyTableRowProps) {
  const [isCopied, setIsCopied] = useState<boolean>(false);
  const [menuPos, setMenuPos] = useState<{ top: number; left: number } | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const popoverRef = useRef<HTMLDivElement>(null);
  const isMenuOpen = openMenuId === apiKey.id;
  const MENU_HEIGHT = 130; // approx px for 3 items
  const MENU_WIDTH = 176;

  const { showToast } = useToast();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isMenuOpen) return;

    const handleClickOutside = (e: MouseEvent) => {
      if (
        menuRef.current &&
        !menuRef.current.contains(e.target as Node) &&
        triggerRef.current &&
        !triggerRef.current.contains(e.target as Node) &&
        popoverRef.current &&
        !popoverRef.current.contains(e.target as Node)
      ) {
        onToggleMenu(apiKey.id);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isMenuOpen]);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(apiKey.secret_value);
    setIsCopied(true);
    showToast('API key copied to clipboard', 'success');
    setTimeout(() => setIsCopied(false), 2000);
  };

  const onViewIntegrations = (id: number) => {
    navigate(`/api-keys/${id}/integrations`);
  };

  return (
    <TableRow>
      <TableCell>
        <h3 className="text-sm font-medium text-[#111] tracking-[-0.15px]">{apiKey.secret_name}</h3>
      </TableCell>
      <TableCell>
        <code className="text-xs font-mono text-[#111] bg-[#f3f4f6] px-2 py-1 rounded">
          {maskApiKey(apiKey.secret_value)}
        </code>
      </TableCell>
      <TableCell>
        <div className="flex items-center gap-3">
          <Switch
            checked={apiKey.is_active}
            onCheckedChange={() => canManage && onToggleStatus(apiKey.id)}
            disabled={!canManage}
          />
        </div>
      </TableCell>
      <TableCell>
        <span className="text-sm text-[#6a7282] tracking-[-0.15px]">
          {formatDate(apiKey.created_at)}
        </span>
      </TableCell>
      <TableCell>
        <span className="text-sm text-[#6a7282] tracking-[-0.15px]">
          {apiKey.last_used_at ? formatDate(apiKey.last_used_at) : 'Never'}
        </span>
      </TableCell>
      <TableCell align="right">
        <div className="flex gap-2 justify-start">
          <button
            onClick={(e) => {
              e.stopPropagation();
              copyToClipboard();
            }}
            className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-gray-100 transition-colors"
            title={isCopied ? 'Copied!' : 'Copy to clipboard'}
          >
            <Copy className={`w-4 h-4 ${isCopied ? 'text-[#038e43]' : 'text-[#6b7280]'}`} />
          </button>

          <div ref={menuRef}>
            {canManage && (
              <button
                ref={triggerRef}
                onClick={(e) => {
                  e.stopPropagation();

                  if (!isMenuOpen && triggerRef.current) {
                    const rect = triggerRef.current.getBoundingClientRect();

                    const spaceBelow = window.innerHeight - rect.bottom;
                    const top =
                      spaceBelow < MENU_HEIGHT ? rect.top - MENU_HEIGHT - 4 : rect.bottom + 4;

                    const left = Math.max(8, rect.right - MENU_WIDTH);

                    setMenuPos({ top, left });
                  }

                  onToggleMenu(apiKey.id);
                }}
                className={`w-8 h-8 rounded-lg flex items-center justify-center 
               ${isMenuOpen ? 'bg-gray-200' : 'hover:bg-gray-100'}`}
              >
                <MoreVertical
                  className={`w-4 h-4 ${isMenuOpen ? 'text-gray-700' : 'text-gray-500'}`}
                />
              </button>
            )}

            {isMenuOpen &&
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
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleMenu(apiKey.id);
                      onEdit(apiKey.id);
                    }}
                    className="flex items-center gap-2 w-full px-4 py-2.5 text-sm text-[#374151] hover:bg-gray-50 transition-colors"
                  >
                    <Edit className="w-4 h-4 text-[#6b7280]" />
                    Edit
                  </button>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleMenu(apiKey.id);
                      onViewIntegrations(apiKey.id);
                    }}
                    className="flex items-center gap-2 w-full px-4 py-2.5 text-sm text-[#374151] hover:bg-gray-50 transition-colors"
                  >
                    <List className="w-4 h-4 text-[#6b7280]" />
                    Integrations
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleMenu(apiKey.id);
                      onRegenerate(apiKey.id);
                    }}
                    className="flex items-center gap-2 w-full px-4 py-2.5 text-sm text-[#374151] hover:bg-gray-50 transition-colors"
                  >
                    <RefreshCcw className="w-4 h-4 text-[#6b7280]" />
                    Regenerate
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleMenu(apiKey.id);
                      onDelete(apiKey.id);
                    }}
                    className="flex items-center gap-2 w-full px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                    Delete
                  </button>
                </div>,
                document.body
              )}
          </div>
        </div>
      </TableCell>
    </TableRow>
  );
}
