import { FileText } from 'lucide-react';
import { TaskStatusBadge } from '@/pages/tasks/task-list/components/TaskStatusBadge';
import { TableRow, TableCell } from '@/components/ui/Table';
import { ApiKeyIntegration } from '@/types/api-key.type';

interface IntegrationTableRowProps {
  integration: ApiKeyIntegration;
  totalProcessingIntegrations?: number;
}

export function IntegrationTableRow({ integration }: IntegrationTableRowProps) {
  return (
    <TableRow>
      <TableCell>
        <div className="flex items-center gap-3">
          <FileText className="w-5 h-5 text-[#038e43]" />
          <span className="text-sm font-medium text-[#101828]">{integration.job_id}</span>
        </div>
      </TableCell>
      <TableCell>
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-[#101828]">{integration.name}</span>
        </div>
      </TableCell>
      <TableCell>
        {integration.type ? (
          <span className="px-2 py-1 text-xs font-medium text-[#111] bg-[#f3f4f6] rounded-lg capitalize">
            {integration.type}
          </span>
        ) : (
          <span className="text-xs text-[#6b7280]">-</span>
        )}
      </TableCell>
      <TableCell>
        <TaskStatusBadge status={integration.status} />
      </TableCell>
      <TableCell>
        <span className="text-sm text-[#4a5565]">{integration.created_at}</span>
      </TableCell>
    </TableRow>
  );
}
