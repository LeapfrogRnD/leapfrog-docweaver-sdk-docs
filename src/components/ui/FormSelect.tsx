// src/components/ui/FormSelect.tsx
import { Controller } from 'react-hook-form';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './Select';
import cn from 'clsx';

export default function FormSelect({ control, name, label, options, error }: any) {
  return (
    <div className="w-full">
      <label className="block text-sm font-medium mb-2 text-primary-black">{label}</label>
      <Controller
        name={name}
        control={control}
        render={({ field }) => (
          <Select key={field.value} onValueChange={field.onChange} value={field.value ?? ''}>
            <SelectTrigger className={cn('w-full', error && 'border-red-600 focus:ring-red-600')}>
              <SelectValue placeholder={`Select ${label}`} />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(options).map(([key, value]) => (
                <SelectItem key={key} value={String(key)}>
                  {value as string}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      />
      {/* Validation Error Message */}
      {error && <p className="mt-1 text-sm text-red-600">{error.message}</p>}
    </div>
  );
}
