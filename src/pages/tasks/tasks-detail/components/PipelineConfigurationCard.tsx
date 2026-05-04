import { Settings } from 'lucide-react';
import { TaskDetail } from '@/types/task.type';

interface PipelineConfigurationCardProps {
  task: TaskDetail;
}

export function PipelineConfigurationCard({ task }: PipelineConfigurationCardProps) {
  return (
    <div className="bg-white border border-[rgba(0,0,0,0.1)] rounded-[14px] p-6 mb-6">
      <h2 className="text-lg font-semibold text-[#111] mb-4 flex items-center gap-2">
        <Settings className="w-5 h-5 text-[#038e43]" />
        Pipeline Configuration
      </h2>
      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className="block text-xs font-medium text-[#6b7280] mb-1">Pipeline</label>
          <p className="text-sm font-medium text-[#111]">
            {task.pipeline_name || 'No pipeline assigned'}
          </p>
        </div>
        <div>
          <label className="block text-xs font-medium text-[#6b7280] mb-1">Task Type</label>
          <p className="text-sm font-medium text-[#111] capitalize">{task.task_type || 'N/A'}</p>
        </div>
        {task.additional_instruction && (
          <div className="col-span-2">
            <label className="block text-xs font-medium text-[#6b7280] mb-2">
              Additional Instruction
            </label>
            <div className="bg-[#f9fafb] border border-[rgba(0,0,0,0.1)] rounded-lg p-3">
              <p className="text-sm text-[#111] whitespace-pre-wrap">
                {task.additional_instruction}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
