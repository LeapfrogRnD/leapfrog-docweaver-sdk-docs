import { useWatch, Control, FieldValues, Path } from 'react-hook-form';
import { FormField, FormItem, FormControl, FormMessage } from './form';
import cn from 'clsx';
import { Input } from './Input';
interface WatchedInputProps<T extends FieldValues> {
  control: Control<T>;
  name: Path<T>;
  label: string;
  placeholder?: string;
  required?: boolean;
}

export function WatchedInput<T extends FieldValues>({
  control,
  name,
  label,
  placeholder,
  required,
}: WatchedInputProps<T>) {
  const value = useWatch({
    control,
    name,
  });

  return (
    <FormField
      control={control}
      name={name}
      render={({ field, fieldState }) => {
        // Only show the "Required" error if the user has interacted with the field (isDirty)
        // OR if the form has been submitted/validated (invalid)
        const isActuallyEmpty = !value || value.toString().trim() === '';
        const shouldShowError =
          required && isActuallyEmpty && (fieldState.isDirty || fieldState.isTouched);

        // Final error state (combines live watch + Zod schema errors)
        const hasError = !!fieldState.error || shouldShowError;

        return (
          <FormItem className="space-y-1.5">
            <label
              className={cn(
                'text-sm font-medium transition-colors flex items-center gap-1',
                'text-gray-700'
              )}
            >
              {label}
              {required && <span className="text-red-500">*</span>}
            </label>

            <FormControl>
              <Input
                {...field}
                placeholder={placeholder}
                className={cn(
                  'bg-gray-50 border-gray-200 transition-all focus:ring-2',
                  hasError
                    ? 'border-red-500 bg-red-50 focus:ring-red-500'
                    : 'focus:ring-green-600 focus:border-transparent'
                )}
              />
            </FormControl>

            {/* Only show warning text if there's an actual interaction or error */}
            {shouldShowError && (
              <p className="text-xs font-medium text-red-600">This field is required</p>
            )}

            {/* Standard FormMessage for Zod schema errors */}
            <FormMessage className="text-xs text-red-600" />
          </FormItem>
        );
      }}
    />
  );
}
