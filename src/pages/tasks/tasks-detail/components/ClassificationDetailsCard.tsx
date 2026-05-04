import { Tag } from 'lucide-react';
import { TaskDetail } from '@/types/task.type';

interface ClassificationDetailsCardProps {
  task: TaskDetail;
}

export function ClassificationDetailsCard({ task }: ClassificationDetailsCardProps) {
  if (!task?.json_schema) {
    return null;
  }

  // json_schema is an array of { category, fields: [{ name, description }] } for classification tasks
  const categories = Array.isArray(task.json_schema) ? task.json_schema : [];

  if (categories.length === 0) {
    return null;
  }

  return (
    <div className="bg-white border border-[rgba(0,0,0,0.1)] rounded-[14px] p-6 mb-6">
      <h2 className="text-lg font-semibold text-[#111] mb-4 flex items-center gap-2">
        <Tag className="w-5 h-5 text-[#038e43]" />
        Classification ({categories.length})
      </h2>
      <div className="space-y-4">
        {categories.map((cat: any, catIndex: number) => (
          <div key={catIndex} className="border border-[rgba(0,0,0,0.1)] rounded-lg p-4">
            <h3 className="text-sm font-semibold text-[#111] capitalize mb-3">{cat.category}</h3>
            <div className="space-y-2">
              {(cat.fields || []).map((field: any, fieldIndex: number) => (
                <div
                  key={fieldIndex}
                  className="flex items-start gap-3 bg-[#f9fafb] rounded-lg px-3 py-2"
                >
                  <span className="text-sm font-medium text-[#111] min-w-[140px]">
                    {field.name}
                  </span>
                  {field.description && (
                    <span className="text-sm text-[#6b7280]">{field.description}</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
