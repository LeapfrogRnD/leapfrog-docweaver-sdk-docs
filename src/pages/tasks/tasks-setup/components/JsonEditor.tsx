import { Upload } from 'lucide-react';
interface JsonEditorProps {
  value: string;
  onChange: (val: string) => void;
  error: string | null;
}

export function JsonEditor({ value, onChange, error }: JsonEditorProps) {
  const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => onChange(ev.target?.result as string);
    reader.readAsText(file);
  };

  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-xs font-mono text-gray-500">raw_schema.json</span>
        <label className="text-xs text-green-700 cursor-pointer flex items-center gap-1">
          <Upload className="w-3 h-3" /> Upload{' '}
          <input type="file" className="hidden" onChange={handleUpload} />
        </label>
      </div>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full min-h-[300px] p-3 bg-gray-900 text-green-400 font-mono text-xs rounded-lg focus:ring-2 focus:ring-green-500"
        spellCheck={false}
      />
      {error && <p className="text-red-500 text-xs italic">{error}</p>}
    </div>
  );
}
