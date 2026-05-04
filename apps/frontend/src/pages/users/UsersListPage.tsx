import { useState } from 'react';
import { Users, Plus } from 'lucide-react';
import { useToast } from '@/context/ToastContext';
import { RegisterUserModal } from './RegisterUserPage';
import { UserTable } from './components/Table';
import { usePagination } from '@/hooks/usePagination';
import { ConfirmDialog, StatsSkeleton } from '@/components/ui';
import { PageHeader } from '@/components';
import {
  useGetUsers,
  useBlockUser,
  useUnblockUser,
  useDeleteUser,
  useResendVerificationEmail,
  useGetUserStats,
} from '@/queries/user.query';
import UserStatsComponent from './components/Stat';
import { UserListItem, UserStatus } from '@/types/user.type';
import { useAuth } from '@/context/AuthContext';

export default function UsersListPage() {
  const { showToast } = useToast();
  const pagination = usePagination();

  const [actionInProgress, setActionInProgress] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [search, setSearch] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<UserStatus | 'all'>('all');
  const [deleteConfirm, setDeleteConfirm] = useState<{
    isOpen: boolean;
    user: UserListItem | null;
  }>({
    isOpen: false,
    user: null,
  });

  const { data: usersData, isLoading } = useGetUsers(pagination.page, pagination.pageSize, {
    search,
    status: statusFilter !== 'all' ? statusFilter : null,
  });

  const { data: userStats, isLoading: isStatsLoading } = useGetUserStats();

  const users = usersData?.data || [];
  if (usersData?.metadata && pagination.metadata !== usersData.metadata) {
    pagination.setMetadata(usersData.metadata);
  }

  const blockUserMutation = useBlockUser();
  const unblockUserMutation = useUnblockUser();
  const deleteUserMutation = useDeleteUser();
  const resendEmailMutation = useResendVerificationEmail();

  const handleMutation = async (
    mutation: any,
    userId: string,
    actionKey: string,
    successMessage: string,
    errorMessage: string
  ) => {
    setActionInProgress(`${actionKey}-${userId}`);

    try {
      const result = await mutation.mutateAsync(userId);

      if (result?.success) {
        showToast(result.message || successMessage, 'success');
      } else {
        showToast(result?.message || errorMessage, 'error');
      }
    } catch (err: any) {
      // Try to extract a helpful server message from common error shapes (axios/fetch/custom)
      const serverMessage =
        err?.response?.data?.message ||
        err?.response?.data?.detail ||
        err?.response?.data?.error ||
        err?.message ||
        errorMessage;
      showToast(serverMessage, 'error');
    } finally {
      setActionInProgress(null);
    }
  };

  const handleDeleteUser = (id: string) => {
    const userToDelete = users.find((user) => user.id === Number(id));
    if (!userToDelete) return;

    setDeleteConfirm({ isOpen: true, user: userToDelete });
  };

  const confirmDelete = async () => {
    if (!deleteConfirm.user) return;

    setActionInProgress(`delete-${deleteConfirm.user.id}`);

    try {
      const result = await deleteUserMutation.mutateAsync(String(deleteConfirm.user.id));

      if (result?.success) {
        showToast(result.message || 'User deleted', 'success');
      } else {
        showToast(result?.message || 'Failed to delete user', 'error');
      }
      setDeleteConfirm({ isOpen: false, user: null });
    } catch (err: any) {
      // Extract server error message if available (supports axios-like and other shapes)
      const serverMessage =
        err?.response?.data?.message ||
        err?.response?.data?.detail ||
        err?.response?.data?.error ||
        err?.message ||
        'Failed to delete user';
      showToast(serverMessage, 'error');
    } finally {
      setActionInProgress(null);
    }
  };

  const cancelDelete = () => {
    setDeleteConfirm({ isOpen: false, user: null });
  };

  const { user: currentUser } = useAuth();
  return (
    <div className="flex-1 bg-[#f9fafb] overflow-auto min-h-screen mx-auto">
      <PageHeader
        icon={<Users className="w-6 h-6" />}
        title="Users"
        description="Manage user accounts and permissions"
        actions={
          <button
            onClick={() => setIsModalOpen(true)}
            className="h-9 px-2 sm:px-3 bg-[#038e43] text-white text-xs sm:text-sm font-medium rounded-lg flex items-center gap-1 sm:gap-2 hover:bg-[#027235] flex-shrink-0 w-full sm:w-auto justify-center"
          >
            <Plus className="w-4 h-4" />
            <span className="hidden sm:inline">Register New User</span>
            <span className="sm:hidden">Register User</span>
          </button>
        }
      />

      <div className="px-4 sm:px-8 pt-8 pb-6">
        {isStatsLoading ? (
          <StatsSkeleton cards={4} />
        ) : (
          <UserStatsComponent userStats={userStats} />
        )}

        <div>
          <UserTable
            currentUser={currentUser}
            users={users}
            search={search}
            onSearchChange={(value: string) => {
              setSearch(value);
              pagination.setPage(1);
            }}
            statusFilter={{
              value: statusFilter,
              onChange: (val) => {
                setStatusFilter(val as UserStatus | 'all');
                pagination.setPage(1);
              },
              placeholder: 'All Status',
              options: [
                { label: 'All Status', value: 'all' },
                { label: 'Active', value: UserStatus.ACTIVE },
                { label: 'Pending', value: UserStatus.PENDING },
                { label: 'Blocked', value: UserStatus.BLOCKED },
              ],
            }}
            isLoading={isLoading}
            actionInProgress={actionInProgress}
            pagination={pagination}
            onResend={(id) =>
              handleMutation(
                resendEmailMutation,
                id,
                'resend',
                'Verification email sent',
                'Failed to resend verification email'
              )
            }
            onBlock={(id) =>
              handleMutation(blockUserMutation, id, 'block', 'User blocked', 'Failed to block user')
            }
            onUnblock={(id) =>
              handleMutation(
                unblockUserMutation,
                id,
                'unblock',
                'User unblocked',
                'Failed to unblock user'
              )
            }
            onDelete={handleDeleteUser}
          />
        </div>
      </div>

      {/* Register User Modal */}
      <RegisterUserModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        // onSuccess={handleModalSuccess}
      />

      <ConfirmDialog
        iconExist={false}
        isOpen={deleteConfirm.isOpen}
        onClose={cancelDelete}
        onConfirm={confirmDelete}
        title="Delete User"
        description={
          deleteConfirm.user ? (
            <>
              Are you sure you want to delete the user <strong>"{deleteConfirm.user.email}"</strong>
              ? This action cannot be undone.
            </>
          ) : (
            'Are you sure you want to delete this user?'
          )
        }
        confirmText="Delete User"
        cancelText="Cancel"
        variant="danger"
        isLoading={deleteUserMutation.isPending}
      />
    </div>
  );
}
