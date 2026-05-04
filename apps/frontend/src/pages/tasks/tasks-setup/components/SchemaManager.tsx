import { useState, useEffect, ReactNode } from 'react';
import { Layout, Code2, Trash2 } from 'lucide-react';
import { formatJson, validateSchemaJson } from '@/services/task-json.service';
import { TextArea } from '@/components/ui/TextArea';
import schemaData from '@/../data/schema_templates.json';

interface SchemaManagerProps<T> {
  title: string;
  items: T[];
  setItems: (items: T[]) => void;
  requiredFields: (keyof T)[];
  renderForm: (addItem: (item: T) => void) => ReactNode;
  renderItemPreview: (item: T) => ReactNode;
  emptyIcon: ReactNode;
  handleData: (template: any) => void;
  type: string;
}

export function SchemaManager<T>({
  items,
  setItems,
  requiredFields,
  renderForm,
  renderItemPreview,
  emptyIcon,
  handleData,
  type,
}: SchemaManagerProps<T>) {
  const [viewMode, setViewMode] = useState<'visual' | 'json'>('visual');
  const [jsonInput, setJsonInput] = useState(formatJson(items));
  const [error, setError] = useState<string | null>(null);
  const [selectedTemplateId, setSelectedTemplateId] = useState<string | null>(null);
  const filteredSchemaData = schemaData.filter((item) => item.type === type);
  useEffect(() => {
    setJsonInput(formatJson(items));
  }, [items]);

  const handleJsonChange = (val: string) => {
    setJsonInput(val);
    const result = validateSchemaJson<T>(val, requiredFields);
    if (result.isValid && result.data) {
      setItems(result.data);
      setError(null);
    } else {
      setError(result.error || 'Invalid JSON');
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex gap-1 bg-[#f9fafb] p-1 border rounded-lg">
          <button
            onClick={() => setViewMode('visual')}
            className={`px-3 py-1.5 rounded text-xs flex items-center gap-1.5 ${viewMode === 'visual' ? 'bg-white shadow-sm text-[#007e40]' : 'text-gray-500'}`}
          >
            <Layout className="w-3.5 h-3.5" /> Visual
          </button>
          <button
            onClick={() => setViewMode('json')}
            className={`px-3 py-1.5 rounded text-xs flex items-center gap-1.5 ${viewMode === 'json' ? 'bg-white shadow-sm text-[#007e40]' : 'text-gray-500'}`}
          >
            <Code2 className="w-3.5 h-3.5" /> JSON
          </button>
        </div>
      </div>
      {viewMode === 'visual' ? (
        renderForm((newItem) => setItems([...items, newItem]))
      ) : (
        <div className="space-y-3">
          <label className="text-xs text-[#111] tracking-wide">Sample Templates</label>
          {/* Sample template pills */}
          {filteredSchemaData.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {filteredSchemaData.map((tpl) => {
                const isSelected = selectedTemplateId === tpl.id;
                return (
                  <button
                    key={tpl.id}
                    type="button"
                    onClick={() => {
                      const next = isSelected ? null : tpl.id;
                      setSelectedTemplateId(next);
                      if (next) {
                        handleData(tpl);
                      }
                    }}
                    className={`px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all ${
                      isSelected
                        ? 'bg-[#f3f4f6] border-[#d1d5db] text-[#374151]'
                        : 'bg-white border-[#e5e7eb] text-[#374151] hover:bg-[#f3f4f6] hover:border-[#d1d5db]'
                    }`}
                  >
                    {tpl.label}
                  </button>
                );
              })}
            </div>
          )}
          <label className="text-xs text-[#111] tracking-wide pt-2 block">JSON Configuration</label>
          <TextArea
            value={jsonInput}
            onChange={(e) => {
              setSelectedTemplateId(null);
              handleJsonChange(e.target.value);
            }}
            error={error}
            variant="primary"
            className="min-h-[250px] font-mono"
            placeholder='{ "key": "value" }'
          />
        </div>
      )}
      {/* Shared Real-time Preview List */}
      <div className="border border-dashed border-gray-300 rounded-xl p-4 min-h-[100px]">
        {items.length === 0 ? (
          <div className="flex flex-col items-center py-4 text-gray-400">
            {emptyIcon}
            <p className="text-xs mt-2">No entries yet</p>
          </div>
        ) : (
          <div className="space-y-2">
            {items.map((item, idx) => (
              <div
                key={idx}
                className="flex justify-between items-start p-3 bg-gray-50 border rounded-lg"
              >
                <div className="flex-1">{renderItemPreview(item)}</div>
                <button onClick={() => setItems(items.filter((_, i) => i !== idx))}>
                  <Trash2 className="w-4 h-4 text-gray-400 hover:text-red-500" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
