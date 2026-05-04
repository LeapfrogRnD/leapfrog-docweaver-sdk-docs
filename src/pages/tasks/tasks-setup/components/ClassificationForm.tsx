import { useState } from 'react';
import { Plus } from 'lucide-react';
import { ClassificationCategoryFormData } from '@/schemas/task.schema';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui';
import { TextArea } from '@/components/ui/TextArea';

export function ClassificationForm({
  onAdd,
}: {
  onAdd: (cat: ClassificationCategoryFormData) => void;
}) {
  const [categoryName, setCategoryName] = useState('');
  const [fields, setFields] = useState<any[]>([]);
  const [currentField, setCurrentField] = useState({
    name: '',
    description: '',
    example: '',
  });

  const addFieldToCategory = () => {
    if (!currentField.name) return;
    setFields([...fields, currentField]);
    setCurrentField({ name: '', description: '', example: '' });
  };

  const submitCategory = () => {
    if (!categoryName || fields.length === 0) return;
    onAdd({ category: categoryName, fields });
    setCategoryName('');
    setFields([]);
  };

  return (
    <div className="border border-[rgba(0,0,0,0.1)] rounded-[14px] p-4 space-y-4 bg-white">
      <div className="space-y-1">
        <label className="text-xs font-bold text-[#111]">Category Name</label>

        <Input
          value={categoryName}
          onChange={(e) => setCategoryName(e.target.value)}
          placeholder="Enter the name of category"
          className="w-full pl-4 pr-8 h-9"
        />
      </div>

      <div className="bg-gray-50 p-3 rounded-lg space-y-2">
        <p className="text-[10px] font-bold uppercase text-gray-400">Add Fields to Category</p>
        <div className="grid grid-cols-1 gap-2">
          <Input
            value={currentField.name}
            onChange={(e) => setCurrentField({ ...currentField, name: e.target.value })}
            placeholder="Enter the category type to classify"
          />

          <TextArea
            label="Description"
            placeholder="Enter Additional description to explain category type"
            rows={2}
            variant="secondary"
            value={currentField.description}
            onChange={(e) => setCurrentField({ ...currentField, description: e.target.value })}
          />
          <TextArea
            label="Example"
            placeholder="Enter example for this tyoe"
            rows={2}
            variant="secondary"
            value={currentField.example}
            onChange={(e) => setCurrentField({ ...currentField, example: e.target.value })}
          />
        </div>

        <Button variant="primary" onClick={addFieldToCategory} icon={<Plus className="w-3 h-3" />}>
          Add Field to List ({fields.length})
        </Button>
      </div>

      <Button
        variant="primary"
        onClick={submitCategory}
        className="w-full bg-[#007e40] text-white py-2 rounded-lg text-sm hover:bg-[#027235] disabled:opacity-50"
      >
        Save Full Category
      </Button>
    </div>
  );
}
