import { useState } from 'react';
import { Plus, Tag, X } from 'lucide-react';
import { ClassificationCategoryFormData } from '@/schemas/task.schema';

export function ClassificationCategoriesCard({
  onAdd,
}: {
  onAdd: (cat: ClassificationCategoryFormData) => void;
}) {
  const [categoryName, setCategoryName] = useState('');
  const [fields, setFields] = useState<any[]>([]);
  const [currentField, setCurrentField] = useState({
    name: '',
    title: '',
    description: '',
    example: '',
  });

  const addFieldToCategory = () => {
    if (!currentField.name || !currentField.title) return;
    setFields([...fields, currentField]);
    setCurrentField({ name: '', title: '', description: '', example: '' });
  };

  const removeField = (index: number) => {
    setFields(fields.filter((_, i) => i !== index));
  };

  const submitCategory = () => {
    if (!categoryName || fields.length === 0) return;
    onAdd({ category: categoryName, fields });
    setCategoryName('');
    setFields([]);
  };

  return (
    <div className="bg-white border border-[rgba(0,0,0,0.1)] rounded-[14px] p-6 space-y-6">
      {/* Header aligned with ExtractionFieldsCard style */}
      <h2 className="text-lg font-semibold text-[#111] flex items-center gap-2">
        <Tag className="w-5 h-5 text-[#038e43]" />
        Create Category
      </h2>

      {/* Category Name Input */}
      <div className="space-y-2">
        <label className="text-xs font-bold text-[#111] uppercase tracking-wide">
          Category Name
        </label>
        <input
          value={categoryName}
          onChange={(e) => setCategoryName(e.target.value)}
          placeholder="e.g. Invoice"
          className="w-full h-10 px-3 bg-[#f9fafb] border border-[rgba(0,0,0,0.1)] rounded-lg text-sm outline-none focus:border-[#038e43] transition-colors"
        />
      </div>

      {/* Field Builder Form */}
      <div className="bg-[#fcfcfc] border border-[rgba(0,0,0,0.1)] rounded-xl p-4 space-y-4">
        <p className="text-[10px] font-bold uppercase text-[#6b7280]">Add Field Definition</p>

        <div className="grid grid-cols-2 gap-3">
          <input
            value={currentField.name}
            onChange={(e) =>
              setCurrentField({
                ...currentField,
                name: e.target.value.replace(/\s/g, '_').toLowerCase(),
              })
            }
            placeholder="e.g. Invoice"
            className="w-full h-10 px-3 bg-[#f9fafb] border border-[rgba(0,0,0,0.1)] rounded-lg text-sm outline-none focus:border-[#038e43] transition-colors"
          />

          <input
            placeholder="Display Title (e.g. Total Amount)"
            className="text-sm h-9 px-3 rounded-lg border border-[rgba(0,0,0,0.1)] bg-white outline-none focus:border-[#038e43]"
            value={currentField.title}
            onChange={(e) => setCurrentField({ ...currentField, title: e.target.value })}
          />

          {/* Textareas covering whole line */}
          <textarea
            placeholder="Description (Instructions for extraction...)"
            rows={2}
            className="col-span-2 text-sm p-3 rounded-lg border border-[rgba(0,0,0,0.1)] bg-white outline-none focus:border-[#038e43] resize-none"
            value={currentField.description}
            onChange={(e) => setCurrentField({ ...currentField, description: e.target.value })}
          />
          <textarea
            placeholder="Example value..."
            rows={2}
            className="col-span-2 text-sm p-3 rounded-lg border border-[rgba(0,0,0,0.1)] bg-white outline-none focus:border-[#038e43] resize-none"
            value={currentField.example}
            onChange={(e) => setCurrentField({ ...currentField, example: e.target.value })}
          />
        </div>

        <button
          type="button"
          onClick={addFieldToCategory}
          disabled={!currentField.name || !currentField.title}
          className="w-full py-2 flex items-center justify-center gap-2 text-xs font-bold text-[#038e43] bg-white border border-[#038e43] rounded-lg hover:bg-[#f0fdf4] transition-colors disabled:opacity-40"
        >
          <Plus className="w-4 h-4" /> Add Field
        </button>
      </div>

      {/* List of Added Fields - Matches ExtractionFieldsCard item design */}
      {fields.length > 0 && (
        <div className="space-y-3 pt-2 border-t border-[rgba(0,0,0,0.1)]">
          <p className="text-[10px] font-bold uppercase text-[#6b7280]">
            Fields in this category ({fields.length})
          </p>
          {fields.map((field, index) => (
            <div
              key={index}
              className="border border-[rgba(0,0,0,0.1)] rounded-lg p-4 relative bg-white"
            >
              <button
                onClick={() => removeField(index)}
                className="absolute top-3 right-3 text-gray-400 hover:text-[#e7000b] transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="text-sm font-semibold text-[#111]">{field.title}</h3>
                  <p className="text-xs text-[#6b7280] font-mono mt-1">{field.name}</p>
                </div>
              </div>
              {field.description && (
                <p className="text-xs text-[#6b7280] mt-2 bg-gray-50 p-2 rounded">
                  {field.description}
                </p>
              )}
              {field.example && (
                <p className="text-[10px] text-[#038e43] mt-2 font-medium uppercase tracking-tighter">
                  Example:{' '}
                  <span className="text-gray-600 normal-case font-normal">{field.example}</span>
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      <button
        onClick={submitCategory}
        disabled={!categoryName || fields.length === 0}
        className="w-full bg-[#038e43] text-white py-3 rounded-[10px] text-sm font-bold hover:bg-[#027235] disabled:opacity-50 transition-all shadow-sm shadow-[#038e43]/20"
      >
        Save Full Category
      </button>
    </div>
  );
}
