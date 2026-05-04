import { useState } from 'react';
import { ArrowLeft, PlugZap2, RefreshCw } from 'lucide-react';
import { IntegrationTable } from './components/IntegrationTable';
import { usePagination } from '@/hooks/usePagination';
import clsx from 'clsx';
import { useParams } from 'react-router-dom';
import { useGetApiKeyIntegrations, useGetApiKeyIntegrationStats } from '@/queries/api-key.query';
import { IntegrationStatsCards } from './components/IntegrationStatsCards';
import { StatsSkeleton } from '@/components/ui';
import { PageHeader } from '@/components';

export function ApiKeysIntegrationPage() {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [statusFilter, setStatusFilter] = useState('all');
  const [search, setSearch] = useState('');
  const { keyId } = useParams<{ keyId: string }>();

  const pagination = usePagination();
  const {
    data: integrationStats,
    isLoading: isStatsLoading,
    refetch: refetchIntegrationStats,
  } = useGetApiKeyIntegrationStats(keyId ? Number(keyId) : 0);
  const {
    data: integrationsData,
    isLoading,
    error,
    refetch: refetchIntegrations,
  } = useGetApiKeyIntegrations(
    keyId ? Number(keyId) : 0,
    pagination.page,
    pagination.pageSize,
    statusFilter,
    search
  );

  if (integrationsData?.metadata && pagination.metadata !== integrationsData.metadata) {
    pagination.setMetadata(integrationsData.metadata);
  }

  const integrations = integrationsData?.data || [];

  const handleRefresh = async () => {
    try {
      setIsRefreshing(true);
      await Promise.all([refetchIntegrations(), refetchIntegrationStats()]);
    } finally {
      setIsRefreshing(false);
    }
  };

  <button
    onClick={handleRefresh}
    className="h-9 px-3 bg-white border border-[#d1d5db] text-sm font-medium rounded-lg flex items-center gap-2 hover:bg-gray-50 transition-colors"
  >
    <RefreshCw className="w-4 h-4" />
    Refresh
  </button>;
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

  return (
    <div className="flex-1 bg-[#f9fafb] overflow-auto min-h-screen mx-auto">
      <PageHeader
        icon={<PlugZap2 className="w-6 h-6" />}
        title="Integrations"
        description="View your API key integrations"
        actions={
          <>
            <button
              type="button"
              onClick={() => window.history.back()}
              className="w-9 h-9 flex items-center justify-center rounded-lg border border-[rgba(0,0,0,0.1)] hover:bg-[#f3f4f6] transition-colors"
            >
              <ArrowLeft className="w-4 h-4 text-[#6b7280]" />
            </button>
            <button
              onClick={handleRefresh}
              className="h-9 px-3 bg-white border border-[#d1d5db] text-sm font-medium rounded-lg flex items-center gap-2 hover:bg-gray-50 transition-colors"
            >
              <RefreshCw className={clsx('w-4 h-4', isRefreshing && 'animate-spin')} />
              Refresh Integrations
            </button>
          </>
        }
      />

      <div className="px-8 pt-8 pb-6">
        {/* Stats Cards */}
        {isStatsLoading ? (
          <StatsSkeleton cards={4} />
        ) : (
          integrationStats && <IntegrationStatsCards integrationStats={integrationStats} />
        )}

        {/* Table */}
        <IntegrationTable
          integrations={integrations}
          pagination={pagination}
          isLoading={isLoading || isRefreshing}
          totalProcessingIntegrations={
            (integrationStats?.queued || 0) + (integrationStats?.processing || 0)
          }
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
              { label: 'Queued', value: 'queued' },
              { label: 'Processing', value: 'processing' },
              { label: 'Completed', value: 'completed' },
              { label: 'Failed', value: 'failed' },
              { label: 'Ready', value: 'ready' },
              { label: 'Draft', value: 'draft' },
            ],
          }}
        />
      </div>
    </div>
  );
}
