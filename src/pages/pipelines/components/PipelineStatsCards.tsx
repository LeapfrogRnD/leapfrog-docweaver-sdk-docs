import { formatDate } from '@/utils';
import { FileText, Calendar } from 'lucide-react';
import { StatCard } from '@/components/StatCard';

interface PipelineStatsCardsProps {
  totalPipelines: number;
  lastUpdated: string;
}

export function PipelineStatsCards({ totalPipelines, lastUpdated }: PipelineStatsCardsProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 mb-6">
      <StatCard
        title="Total Pipelines"
        value={totalPipelines}
        subtitle={''}
        icon={FileText}
        iconBgColor="bg-blue-50"
        iconColor={'text-[#2563eb]'}
      />

      <StatCard
        title="Last Updated"
        value={formatDate(lastUpdated)}
        subtitle={''}
        icon={Calendar}
        iconBgColor="bg-green-50"
        iconColor={'text-[#00a63e]'}
      />
    </div>
  );
}
