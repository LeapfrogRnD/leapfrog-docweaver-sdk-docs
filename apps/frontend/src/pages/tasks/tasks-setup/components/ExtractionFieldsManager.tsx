import { FileText } from 'lucide-react';
import { SchemaManager } from './SchemaManager';
import { ExtractionForm } from './ExtractionForm';

export function ExtractionFieldsManager({
  extractionFields,
  setExtractionFields,
  handleData,
}: any) {
  return (
    <SchemaManager
      title="Extraction Fields"
      items={extractionFields}
      setItems={setExtractionFields}
      requiredFields={['name', 'type']}
      emptyIcon={<FileText className="w-8 h-8 opacity-20" />}
      renderItemPreview={(item) => (
        <div>
          <span className="text-sm font-medium">{item.name}</span>
          <p className="text-xs text-gray-500">{item.type}</p>
        </div>
      )}
      handleData={handleData}
      type="extraction"
      renderForm={(addItem) => <ExtractionForm onAdd={addItem} />}
    />
  );
}
