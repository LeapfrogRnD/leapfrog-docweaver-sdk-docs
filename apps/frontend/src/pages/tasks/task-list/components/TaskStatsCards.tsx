import { TaskStatsResponse } from '@/types/task.type';
import { FileText, CheckCircle2, Clock, XCircle } from 'lucide-react';
import { StatCard } from '@/components/StatCard';

interface TaskStatsCardsProps {
  taskStats: TaskStatsResponse;
}

export function TaskStatsCards({ taskStats }: TaskStatsCardsProps) {
  const stats = [
    {
      label: 'Total Tasks',
      value: taskStats.total,
      icon: FileText,
      color: '#7c3aed',
      iconBg: 'bg-purple-50',
      iconColor: 'text-[#7c3aed]',
    },
    {
      label: 'Processing',
      value: taskStats.processing,
      icon: Clock,
      color: '#155dfc',
      iconBg: 'bg-blue-50',
      iconColor: 'text-[#155dfc]',
    },
    {
      label: 'Completed',
      value: taskStats.completed,
      icon: CheckCircle2,
      color: '#00a63e',
      iconBg: 'bg-green-50',
      iconColor: 'text-[#00a63e]',
    },
    {
      label: 'Failed',
      value: taskStats.failed,
      icon: XCircle,
      color: '#e7000b',
      iconBg: 'bg-red-50',
      iconColor: 'text-[#e7000b]',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-6">
      {stats.map((stat) => (
        <StatCard
          key={stat.label}
          title={stat.label}
          value={stat.value}
          subtitle={''}
          icon={stat.icon}
          iconBgColor={stat.iconBg}
          iconColor={stat.iconColor}
        />
      ))}
    </div>
  );
}
