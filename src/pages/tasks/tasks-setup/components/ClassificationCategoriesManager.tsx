import { Tag } from 'lucide-react';
import { SchemaManager } from './SchemaManager';
import { ClassificationForm } from './ClassificationForm';

export function ClassificationCategoriesManager({
  classificationCategories,
  setClassificationCategories,
  handleData,
}: any) {
  return (
    <SchemaManager
      title="Classification Categories"
      items={classificationCategories}
      setItems={setClassificationCategories}
      requiredFields={['category', 'fields']}
      emptyIcon={<Tag className="w-8 h-8 opacity-20" />}
      renderItemPreview={(item) => (
        <div>
          <span className="text-sm font-bold text-[#101828]">{item.category}</span>
          <div className="flex flex-wrap gap-1 mt-1">
            {item?.fields?.map((f: any, i: number) => (
              <span key={i} className="text-[10px] bg-white border px-1.5 rounded text-gray-500">
                {f.name}
              </span>
            ))}
          </div>
        </div>
      )}
      type="classification"
      handleData={handleData}
      renderForm={(addItem) => <ClassificationForm onAdd={addItem} />}
    />
  );
}
