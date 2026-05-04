import { Plus } from 'lucide-react';
import { useState } from 'react';
import { ClassificationCategoryFormData } from '@/schemas/task.schema';

interface VisualEditorProps {
  onAddCategory: (cat: ClassificationCategoryFormData) => void;
}

export function VisualEditor({ onAddCategory }: VisualEditorProps) {
  const [currentCategory, setCurrentCategory] = useState({ category: '', fields: [] as any[] });
  const [currentField, setCurrentField] = useState({
    name: '',
    title: '',
    description: '',
    example: '',
  });

  const handleAddField = () => {
    if (!currentField.name || !currentField.title) return;
    setCurrentCategory((prev) => ({ ...prev, fields: [...prev.fields, currentField] }));
    setCurrentField({ name: '', title: '', description: '', example: '' });
  };

  return (
    <div className="border border-gray-200 rounded-[14px] p-4 space-y-4">
      <input
        placeholder="Category Name"
        className="w-full h-9 px-3 bg-gray-50 rounded-lg text-sm"
        value={currentCategory.category}
        onChange={(e) => setCurrentCategory({ ...currentCategory, category: e.target.value })}
      />

      <div className="grid grid-cols-2 gap-2 border-t pt-4">
        <input
          placeholder="Field Name"
          className="h-8 px-2 bg-gray-50 text-sm"
          value={currentField.name}
          onChange={(e) =>
            setCurrentField({ ...currentField, name: e.target.value.replace(/\s/g, '_') })
          }
        />
        <input
          placeholder="Field Title"
          className="h-8 px-2 bg-gray-50 text-sm"
          value={currentField.title}
          onChange={(e) => setCurrentField({ ...currentField, title: e.target.value })}
        />
      </div>

      <button onClick={handleAddField} className="text-xs text-green-700 flex items-center gap-1">
        <Plus className="w-3 h-3" /> Add Field to "{currentCategory.category || '...'}"
      </button>

      <button
        onClick={() => {
          onAddCategory(currentCategory);
          setCurrentCategory({ category: '', fields: [] });
        }}
        disabled={!currentCategory.category || currentCategory.fields.length === 0}
        className="w-full bg-[#007e40] text-white py-2 rounded-lg text-sm disabled:opacity-50"
      >
        Save Category
      </button>
    </div>
  );
}
