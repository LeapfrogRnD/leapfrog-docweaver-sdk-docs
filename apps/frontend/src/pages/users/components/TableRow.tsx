import { RefreshCw, UserPlus, ShieldOff, Shield, Trash2 } from 'lucide-react';
import { TableRow, TableCell } from '@/components/ui/Table';
import { UserListItem } from '@/types/user.type';

interface UserTableRowProps {
  canManage: boolean;
  user: UserListItem;
  actionInProgress?: string | null;
  onResend: (id: string) => void;
  onBlock: (id: string) => void;
  onUnblock: (id: string) => void;
  onDelete: (id: string) => void;
}

export function UserTableRow({
  canManage,
  user,
  actionInProgress,
  onResend,
  onBlock,
  onUnblock,
  onDelete,
}: UserTableRowProps) {
  return (
    <TableRow>
      <TableCell>
        <div>
          <p className="text-sm font-medium text-[#101828]">
            {(user as any).full_name || (user as any).fullName}
          </p>
          {(user as any).company && (
            <p className="text-xs text-[#6a7282]">{(user as any).company}</p>
          )}
        </div>
      </TableCell>

      <TableCell>
        <span className="text-sm text-[#101828]">{(user as any).email}</span>
      </TableCell>

      <TableCell>
        <span
          className={`px-2 py-1 text-xs font-medium rounded-lg capitalize ${
            ((user as any).role || '').toLowerCase() === 'admin'
              ? 'text-[#155dfc] bg-[#dbeafe] border border-[#93c5fd]'
              : 'text-[#111] bg-[#f3f4f6] border border-[#e5e7eb]'
          }`}
        >
          {(user as any).role || '-'}
        </span>
      </TableCell>

      <TableCell>
        {(user as any).status === 'active' ? (
          <span className="px-2 py-1 text-xs font-medium text-[#016630] bg-[#dcfce7] border border-[#7bf1a8] rounded-lg">
            Active
          </span>
        ) : (user as any).status === 'blocked' ? (
          <span className="px-2 py-1 text-xs font-medium text-[#e7000b] bg-[#fee2e2] border border-[#fca5a5] rounded-lg">
            Blocked
          </span>
        ) : (user as any).status === 'pending' || (user as any).status === 'invited' ? (
          <span className="px-2 py-1 text-xs font-medium text-[#d97706] bg-[#fef3c7] border border-[#fbbf24] rounded-lg">
            Pending
          </span>
        ) : (
          <span className="text-xs text-[#6b7280]">Unknown</span>
        )}
      </TableCell>

      <TableCell>
        <span className="text-sm text-[#4a5565]">
          {(user as any).created_at || (user as any).memberSince || '-'}
        </span>
      </TableCell>

      <TableCell>
        <div className=" flex items-center justify-start gap-1">
          {(user as any).status === 'pending' && (
            <button
              onClick={() => onResend((user as any).id)}
              disabled={actionInProgress === `resend-${(user as any).id}`}
              className="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-gray-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              title="Resend verification email"
            >
              {actionInProgress === `resend-${(user as any).id}` ? (
                <RefreshCw className="w-4 h-4 text-[#155dfc] animate-spin" />
              ) : (
                <UserPlus className="w-4 h-4 text-[#6b7280]" />
              )}
            </button>
          )}

          {(user as any).status === 'active' && canManage && (
            <button
              onClick={() => onBlock((user as any).id)}
              className="px-3 py-1.5 text-xs font-medium text-[#e7000b] hover:bg-gray-100 rounded-lg transition-colors flex items-center gap-1.5"
              title="Block user"
            >
              <ShieldOff className="w-3.5 h-3.5" />
            </button>
          )}

          {(user as any).status === 'blocked' && canManage && (
            <button
              onClick={() => onUnblock((user as any).id)}
              className="px-3 py-1.5 text-xs font-medium text-[#00a63e] hover:bg-gray-100 rounded-lg transition-colors flex items-center gap-1.5"
              title="Unblock user"
            >
              <Shield className="w-3.5 h-3.5" />
            </button>
          )}
          {canManage && (
            <button
              onClick={() => onDelete((user as any).id)}
              className="w-9 h-9 flex items-center justify-center rounded-lg hover:bg-gray-100 transition-colors"
              title="Delete user"
            >
              <Trash2 className="w-f4 h-4 text-[#6b7280]" />
            </button>
          )}
        </div>
      </TableCell>
    </TableRow>
  );
}
