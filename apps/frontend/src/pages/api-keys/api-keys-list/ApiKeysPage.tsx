import { useEffect, useState } from 'react';
import { ConfirmDialog } from '@/components/ui';
import { ApiKey } from '@/types/api-key.type';
import { useToast } from '@/context/ToastContext';
import { usePagination } from '@/hooks/usePagination';
import {
  useGetApiKeys,
  useDeleteApiKey,
  useGetApiKeyById,
  useRegenerateApiSecret,
  useToggleApiKeyStatus,
} from '@/queries/api-key.query';
import { ApiKeyModal, ApiKeysHeader, SecurityAlert, ErrorAlert, ApiKeysTable } from './components';

export function ApiKeysPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedApiKeyId, setSelectedApiKeyId] = useState<number | null>(null);
  const [editingApiKey, setEditingApiKey] = useState<ApiKey | null>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<{ isOpen: boolean; apiKey: ApiKey | null }>({
    isOpen: false,
    apiKey: null,
  });
  const [regenerateConfirm, setRegenerateConfirm] = useState<{
    isOpen: boolean;
    apiKey: ApiKey | null;
  }>({
    isOpen: false,
    apiKey: null,
  });

  const { showToast } = useToast();
  const pagination = usePagination();
  const [statusFilter, setStatusFilter] = useState('all');
  const [search, setSearch] = useState('');

  // React Query hooks
  const { data, isLoading, error } = useGetApiKeys(
    pagination.page,
    pagination.pageSize,
    statusFilter,
    search
  );
  const { data: apiKey } = useGetApiKeyById(selectedApiKeyId!);

  const deleteMutation = useDeleteApiKey();
  const regenerateMutation = useRegenerateApiSecret();
  const toggleMutation = useToggleApiKeyStatus();

  // Update pagination metadata when data changes
  if (data?.metadata && pagination.metadata !== data.metadata) {
    pagination.setMetadata(data.metadata);
  }

  const apiKeys = data?.data ?? [];
  const errorMessage = error
    ? error instanceof Error
      ? error.message
      : 'Failed to load API keys'
    : null;

  const handleDeleteKey = async (id: number) => {
    const apiKeyToDelete = apiKeys.find((key) => key.id === id);
    if (!apiKeyToDelete) return;

    setDeleteConfirm({ isOpen: true, apiKey: apiKeyToDelete });
  };

  const handleRegenerateKey = async (id: number) => {
    const apiKeyToRegenerate = apiKeys.find((key) => key.id === id);
    if (!apiKeyToRegenerate) return;

    setRegenerateConfirm({ isOpen: true, apiKey: apiKeyToRegenerate });
  };

  const handleEditKey = async (apiKeyId: number) => {
    setSelectedApiKeyId(apiKeyId);
  };

  useEffect(() => {
    if (apiKey) {
      setEditingApiKey(apiKey as ApiKey);
      setIsModalOpen(true);
    }
  }, [apiKey]);

  const confirmDelete = async () => {
    if (!deleteConfirm.apiKey) return;

    try {
      await deleteMutation.mutateAsync(deleteConfirm.apiKey.id);
      showToast('API key deleted successfully', 'success');
      setDeleteConfirm({ isOpen: false, apiKey: null });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete API key';
      showToast(errorMessage, 'error');
    }
  };

  const confirmRegenerate = async () => {
    if (!regenerateConfirm.apiKey) return;

    try {
      await regenerateMutation.mutateAsync(regenerateConfirm.apiKey.id);
      showToast('API Key Secret re-generated successfully', 'success');
      setRegenerateConfirm({ isOpen: false, apiKey: null });
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Failed to re-generate API Key Secret';
      showToast(errorMessage, 'error');
    }
  };

  const cancelDelete = () => {
    setDeleteConfirm({ isOpen: false, apiKey: null });
  };

  const cancelRegenerate = () => {
    setRegenerateConfirm({ isOpen: false, apiKey: null });
  };

  const handleToggleStatus = async (id: number) => {
    try {
      await toggleMutation.mutateAsync(id);
      showToast('API key status updated successfully', 'success');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to toggle API key status';
      showToast(errorMessage, 'error');
    }
  };

  return (
    <div className="bg-[#f9fafb] min-h-screen">
      <div className="mx-auto">
        <ApiKeysHeader
          onCreateClick={() => {
            setIsModalOpen(true);
            setEditingApiKey(null);
          }}
        />

        {/* Main Content */}
        <div className="px-8 pt-8 pb-12">
          <div className="space-y-6">
            {errorMessage && <ErrorAlert message={errorMessage} />}
            {deleteMutation.error && (
              <ErrorAlert
                message={
                  deleteMutation.error instanceof Error
                    ? deleteMutation.error.message
                    : 'Failed to delete API key'
                }
              />
            )}

            <SecurityAlert />

            {/* API Keys List */}
            <div>
              <ApiKeysTable
                isLoading={isLoading}
                apiKeys={apiKeys}
                onDelete={handleDeleteKey}
                onEdit={handleEditKey}
                onRegenerate={handleRegenerateKey}
                onToggleStatus={handleToggleStatus}
                search={search}
                pagination={pagination}
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
              />
            </div>
          </div>
        </div>
      </div>

      <ApiKeyModal
        isOpen={isModalOpen}
        apiKey={editingApiKey}
        onClose={() => {
          setIsModalOpen(false);
          setEditingApiKey(null);
          setSelectedApiKeyId(null);
        }}
        onSave={() => {
          setIsModalOpen(false);
          setEditingApiKey(null);
          setSelectedApiKeyId(null);
        }}
      />

      <ConfirmDialog
        iconExist={false}
        isOpen={deleteConfirm.isOpen}
        onClose={cancelDelete}
        onConfirm={confirmDelete}
        title="Delete API Key"
        description={
          deleteConfirm.apiKey ? (
            <>
              Are you sure you want to delete the API key{' '}
              <strong>"{deleteConfirm.apiKey.secret_name}"</strong>? This action cannot be undone
              and any applications using this key will immediately lose access.
            </>
          ) : (
            'Are you sure you want to delete this API key?'
          )
        }
        confirmText="Delete Key"
        cancelText="Cancel"
        variant="danger"
        isLoading={deleteMutation.isPending}
      />

      <ConfirmDialog
        iconExist={false}
        isOpen={regenerateConfirm.isOpen}
        onClose={cancelRegenerate}
        onConfirm={confirmRegenerate}
        title="Re-generate API Key secret"
        description={
          regenerateConfirm.apiKey ? (
            <>
              Are you sure you want to re-generate the API key secret{' '}
              <strong>"{regenerateConfirm.apiKey.secret_name}"</strong>? This action cannot be
              undone and any applications using this secret will immediately lose access.
            </>
          ) : (
            'Are you sure you want to re-generate the API key secret?'
          )
        }
        confirmText="Re-generate"
        cancelText="Cancel"
        variant="danger"
        isLoading={regenerateMutation.isPending}
      />
    </div>
  );
}
