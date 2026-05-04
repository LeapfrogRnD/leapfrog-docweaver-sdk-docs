import { FileText } from 'lucide-react';

interface Task {
  id: string;
  title: string;
  subtitle: string;
  status: 'completed' | 'processing' | 'failed';
}

interface RecentActivityCardProps {
  tasks: Task[];
}

export function RecentActivityCard({ tasks }: RecentActivityCardProps) {
  const getStatusBadge = (status: Task['status']) => {
    const styles = {
      completed: 'bg-[#dcfce7] text-[#016630]',
      processing: 'bg-[#fef3c7] text-[#92400e]',
      failed: 'bg-[#fee2e2] text-[#991b1b]',
    };

    const labels = {
      completed: 'completed',
      processing: 'processing',
      failed: 'failed',
    };

    return (
      <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${styles[status]}`}>
        {labels[status]}
      </span>
    );
  };

  return (
    <div className="bg-white border border-gray-200 rounded-2xl">
      <div className="px-6 pt-6 pb-4">
        <h3 className="text-base font-medium text-[#111]">Latest Tasks</h3>
        <p className="text-base text-[#6b7280] mt-1">Your most recent OCR processing tasks</p>
      </div>
      <div className="px-6 pb-6 space-y-3">
        {tasks.length === 0 ? (
          <div className="text-center py-8 text-[#6b7280]">
            <p>No recent tasks</p>
          </div>
        ) : (
          tasks.map((task) => (
            <div
              key={task.id}
              className="border border-gray-200 rounded-lg px-4 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-[#f0fdf4] rounded-lg flex items-center justify-center flex-shrink-0">
                  <FileText className="w-4 h-4 text-primary-brand" />
                </div>
                <div>
                  <p className="text-sm font-medium text-[#111]">{task.title}</p>
                  <p className="text-xs text-[#6b7280]">{task.subtitle}</p>
                </div>
              </div>
              {getStatusBadge(task.status)}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
