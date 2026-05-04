import { Tag } from 'lucide-react';
import { TaskDetail } from '@/types/task.type';

interface ExtractionFieldsCardProps {
  task: TaskDetail;
}

export function ExtractionFieldsCard({ task }: ExtractionFieldsCardProps) {
  if (!task?.json_schema) {
    return null;
  }

  // json_schema is an array of { name, type, description } for extraction tasks
  const schemaArray = Array.isArray(task.json_schema) ? task.json_schema : [];
  const fields = schemaArray.map((item: any) => ({
    name: item.name || '',
    type: item.type || 'string',
    description: item.description || '',
  }));

  if (fields.length === 0) {
    return null;
  }

  return (
    <div className="bg-white border border-[rgba(0,0,0,0.1)] rounded-[14px] p-6 mb-6">
      <h2 className="text-lg font-semibold text-[#111] mb-4 flex items-center gap-2">
        <Tag className="w-5 h-5 text-[#038e43]" />
        Extraction ({fields.length})
      </h2>
      <div className="space-y-3">
        {fields.map((field, index) => (
          <div key={index} className="border border-[rgba(0,0,0,0.1)] rounded-lg p-4">
            <div className="flex items-start justify-between mb-2">
              <h3 className="text-sm font-semibold text-[#111]">{field.name}</h3>
              <span className="px-2 py-1 text-xs font-medium text-[#038e43] bg-[#f0fdf4] rounded">
                {field.type}
              </span>
            </div>
            {field.description && <p className="text-sm text-[#6b7280]">{field.description}</p>}
          </div>
        ))}
      </div>
    </div>
  );
}
