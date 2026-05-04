import { ApiKey } from '@/types/api-key.type';
import { ApiKeyTableRow } from './ApiKeyTableRow';
import { DataTable, StatusFilterConfig } from '@/components/DataTable';
import { useAuth } from '@/context/AuthContext';
import { useState } from 'react';
import { UsePaginationReturn } from '@/hooks/usePagination';

interface ApiKeysTableProps {
  apiKeys: ApiKey[];
  onDelete: (id: number) => void;
  onEdit: (id: number) => void;
  onRegenerate: (id: number) => void;
  onToggleStatus: (id: number) => void;
  isLoading?: boolean;
  pagination?: UsePaginationReturn;
  search?: string;
  onSearch?: (value: string) => void;
  statusFilter?: StatusFilterConfig;
}

export function ApiKeysTable({
  apiKeys,
  onDelete,
  onEdit,
  onRegenerate,
  onToggleStatus,
  isLoading,
  search,
  onSearch,
  statusFilter,
  pagination,
}: ApiKeysTableProps) {
  const columns = ['Name', 'API Key', 'Status', 'Created', 'Last Used', 'Actions'];
  const [openMenuId, setOpenMenuId] = useState<number | null>(null);
  const { user } = useAuth();

  const handleToggleMenu = (id: number | null) => {
    setOpenMenuId((prev: number | null) => (prev === id ? null : id));
  };
  return (
    <DataTable<ApiKey>
      title="API Keys"
      description="Manage your secret keys to access the API safely."
      data={apiKeys}
      columns={columns}
      isLoading={isLoading}
      search={search}
      onSearch={onSearch}
      statusFilter={statusFilter}
      pagination={pagination}
      renderRow={(apiKey) => {
        const isOwnedByUser = user && apiKey.created_by === user.id;
        const isSuperUser = user && user.role === 'superadmin';
        const canManage = isOwnedByUser || isSuperUser || false;
        return (
          <ApiKeyTableRow
            key={apiKey.id}
            apiKey={apiKey}
            onDelete={onDelete}
            onEdit={onEdit}
            onRegenerate={onRegenerate}
            onToggleStatus={onToggleStatus}
            canManage={canManage}
            openMenuId={openMenuId}
            onToggleMenu={handleToggleMenu}
          />
        );
      }}
    />
  );
}
