import { useState } from 'react';
import { Plus, ChevronDown } from 'lucide-react';
import { ExtractionFieldFormData } from '@/schemas/task.schema';
import { Input } from '@/components/ui/Input';
import { TextArea } from '@/components/ui/TextArea';

export function ExtractionForm({ onAdd }: { onAdd: (field: ExtractionFieldFormData) => void }) {
  const [field, setField] = useState<ExtractionFieldFormData>({
    name: '',
    type: 'Text',
    description: '',
  });

  const handleAdd = () => {
    if (!field.name.trim()) return;
    onAdd(field);
    setField({ name: '', type: 'Text', description: '' });
  };

  return (
    <div className="border border-[rgba(0,0,0,0.1)] rounded-[14px] p-4 space-y-4 bg-white">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-1">
          <label className="text-xs font-medium text-[#111]">Field to extract </label>
          <Input
            value={field.name}
            onChange={(e) => setField({ ...field, name: e.target.value })}
            placeholder="Enter the field name"
          />
        </div>
        <div className="space-y-1">
          <label className="text-xs font-medium text-[#111]">Type</label>
          <div className="relative">
            <select
              value={field.type}
              onChange={(e) => setField({ ...field, type: e.target.value as any })}
              className="w-full h-9 px-3 bg-[#f9fafb] rounded-lg text-sm appearance-none outline-none"
            >
              <option value="Text">Text</option>
              <option value="Number">Number</option>
              <option value="Date">Date</option>
              <option value="Boolean">Boolean</option>
            </select>
            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          </div>
        </div>
      </div>

      <TextArea
        label="Description"
        placeholder="Optional description for this field"
        rows={2}
        variant="secondary"
        value={field.description}
        onChange={(e) => setField({ ...field, description: e.target.value })}
      />

      <button
        onClick={handleAdd}
        disabled={!field.name}
        className="flex items-center gap-2 bg-[#007e40] text-white px-4 py-2 rounded-lg text-sm hover:bg-[#027235] disabled:opacity-50"
      >
        <Plus className="w-4 h-4" /> Add Extraction Field
      </button>
    </div>
  );
}
