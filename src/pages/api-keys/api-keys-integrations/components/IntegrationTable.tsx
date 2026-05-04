import { DataTable, StatusFilterConfig } from '@/components/DataTable';
import { IntegrationTableRow } from './IntegrationTableRow';
import { UsePaginationReturn } from '@/hooks/usePagination';
import { ApiKeyIntegration } from '@/types/api-key.type';

interface IntegrationTableProps {
  integrations: ApiKeyIntegration[];
  totalProcessingIntegrations?: number;
  pagination: UsePaginationReturn;
  isLoading?: boolean;
  search?: string;
  onSearch?: (value: string) => void;
  statusFilter?: StatusFilterConfig;
}

export function IntegrationTable({
  integrations,
  pagination,
  isLoading,
  totalProcessingIntegrations,
  search,
  onSearch,
  statusFilter,
}: IntegrationTableProps) {
  const columns = ['Job Id', 'Name', 'Type', 'Status', 'Created At'];

  return (
    <DataTable<ApiKeyIntegration>
      title="Integrations"
      data={integrations}
      columns={columns}
      isLoading={isLoading}
      search={search}
      onSearch={onSearch}
      statusFilter={statusFilter}
      pagination={pagination}
      renderRow={(integration) => (
        <IntegrationTableRow
          key={integration.job_id}
          integration={integration}
          totalProcessingIntegrations={totalProcessingIntegrations}
        />
      )}
    />
  );
}
