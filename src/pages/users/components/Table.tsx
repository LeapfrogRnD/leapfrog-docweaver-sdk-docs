import { UserListItem } from '@/types/user.type';
import { UserTableRow } from './TableRow';
import { UsePaginationReturn } from '@/hooks/usePagination';
import { DataTable, StatusFilterConfig } from '@/components/DataTable';
import { User } from '@/context/AuthContext';

interface UserTableProps {
  currentUser: User | null;
  users: UserListItem[];
  search?: string;
  onSearchChange?: (value: string) => void;
  statusFilter?: StatusFilterConfig;
  pagination?: UsePaginationReturn;
  isLoading?: boolean;
  actionInProgress?: string | null;

  onResend?: (id: string) => void;
  onBlock?: (id: string) => void;
  onUnblock?: (id: string) => void;
  onDelete?: (id: string) => void;
}

export function UserTable({
  currentUser,
  users,
  search = '',
  onSearchChange,
  statusFilter,
  pagination,
  actionInProgress,
  isLoading,
  onResend = () => {},
  onBlock = () => {},
  onUnblock = () => {},
  onDelete = () => {},
}: UserTableProps) {
  return (
    <DataTable<UserListItem>
      title="Users & Invitations"
      data={users}
      columns={['Name', 'Email Address', 'Role', 'Status', 'Last Activity', 'Actions']}
      search={search}
      pagination={pagination}
      onSearch={onSearchChange}
      statusFilter={statusFilter}
      isLoading={isLoading}
      emptyMessage=""
      renderRow={(user) => {
        const canManage = (currentUser?.role?.length ?? 0) > (user?.role?.length ?? 0);
        return (
          <UserTableRow
            canManage={canManage}
            key={user.id}
            user={user}
            actionInProgress={actionInProgress}
            onResend={onResend}
            onBlock={onBlock}
            onUnblock={onUnblock}
            onDelete={onDelete}
          />
        );
      }}
    />
  );
}
