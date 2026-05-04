import { StatCard } from '@/components';
import { IntegrationStatsResponse } from '@/types/api-key.type';
import { FileText, CheckCircle2, Clock, XCircle } from 'lucide-react';

interface TaskStatsCardsProps {
  integrationStats: IntegrationStatsResponse;
}

export function IntegrationStatsCards({ integrationStats }: TaskStatsCardsProps) {
  const stats = [
    {
      label: 'Total Tasks',
      value: integrationStats.total,
      icon: FileText,
      color: '#7c3aed',
      iconBg: 'bg-purple-50',
      iconColor: 'text-[#7c3aed]',
    },
    {
      label: 'Processing',
      value: integrationStats.processing,
      icon: Clock,
      color: '#155dfc',
      iconBg: 'bg-blue-50',
      iconColor: 'text-[#155dfc]',
    },
    {
      label: 'Completed',
      value: integrationStats.completed,
      icon: CheckCircle2,
      color: '#00a63e',
      iconBg: 'bg-green-50',
      iconColor: 'text-[#00a63e]',
    },
    {
      label: 'Failed',
      value: integrationStats.failed,
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
      ))}{' '}
    </div>
  );
}
