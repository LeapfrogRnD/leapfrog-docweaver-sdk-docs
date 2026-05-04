import { TaskStatus } from '@/types/task.type';

interface TaskStatusBadgeProps {
  status: TaskStatus;
}

export function TaskStatusBadge({ status }: TaskStatusBadgeProps) {
  const getStatusConfig = (status: TaskStatus) => {
    switch (status) {
      case TaskStatus.COMPLETED:
        return {
          label: 'Completed',
          textColor: '#166534', // Dark green
          bgColor: '#dcfce7', // Light green
          borderColor: '#86efac', // Green border
        };
      case TaskStatus.PROCESSING:
        return {
          label: 'Processing',
          textColor: '#1e40af', // Dark blue
          bgColor: '#dbeafe', // Light blue
          borderColor: '#93c5fd', // Blue border
        };
      case TaskStatus.FAILED:
        return {
          label: 'Failed',
          textColor: '#991b1b', // Dark red
          bgColor: '#fee2e2', // Light red
          borderColor: '#fca5a5', // Red border
        };
      case TaskStatus.DRAFT:
        return {
          label: 'Draft',
          textColor: '#92400e', // Dark amber
          bgColor: '#fef3c7', // Light amber
          borderColor: '#fcd34d', // Amber border
        };
      case TaskStatus.DOCUMENT_UPLOADED:
        return {
          label: 'Document Uploaded',
          textColor: '#065f46', // Dark teal
          bgColor: '#d1fae5', // Light teal
          borderColor: '#6ee7b7', // Teal border
        };
      case TaskStatus.QUEUED:
        return {
          label: 'Queued',
          textColor: '#7c3aed', // Dark purple
          bgColor: '#ede9fe', // Light purple
          borderColor: '#c4b5fd', // Purple border
        };
      case TaskStatus.DOCUMENT_PENDING:
        return {
          label: 'Document Pending',
          textColor: '#b45309', // Dark orange
          bgColor: '#fed7aa', // Light orange
          borderColor: '#fdba74', // Orange border
        };
      case TaskStatus.READY:
        return {
          label: 'Ready',
          textColor: '#047857', // Dark emerald
          bgColor: '#d1fae5', // Light emerald
          borderColor: '#6ee7b7', // Emerald border
        };
      default:
        return {
          label: status,
          textColor: '#4b5563', // Dark gray
          bgColor: '#f3f4f6', // Light gray
          borderColor: '#d1d5db', // Gray border
        };
    }
  };

  const config = getStatusConfig(status);

  return (
    <span
      className="inline-block px-2 py-1 text-xs font-medium rounded-lg whitespace-nowrap max-w-full truncate"
      style={{
        color: config.textColor,
        backgroundColor: config.bgColor,
        borderColor: config.borderColor,
        borderWidth: '1px',
      }}
      title={config.label}
    >
      {config.label}
    </span>
  );
}
