import { TextareaHTMLAttributes } from 'react';
import clsx from 'clsx';

interface TextAreaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string | null;
  variant?: 'primary' | 'secondary';
  className?: string;
  containerClassName?: string;
}

export function TextArea({
  label,
  error,
  variant = 'primary',
  className = '',
  containerClassName = '',
  ...props
}: TextAreaProps) {
  const baseStyles =
    'w-full p-3 rounded-lg text-sm transition-all duration-200 outline-none border focus:ring-1 disabled:opacity-50 disabled:cursor-not-allowed placeholder:text-gray-400';

  const variantStyles = {
    primary:
      'bg-[#f9fafb] border-[rgba(0,0,0,0.1)] focus:border-[#038e43] focus:ring-[#038e43] text-[#111]',
    secondary:
      'bg-white border-[rgba(0,0,0,0.1)] focus:border-[#038e43] focus:ring-[#038e43] text-[#111]',
  };

  const errorStyles = error ? 'border-[#e7000b] focus:border-[#e7000b] focus:ring-[#e7000b]' : '';

  return (
    <div className={clsx('flex flex-col gap-1.5 w-full', containerClassName)}>
      {label && (
        <label className="text-xs font-bold text-[#111] uppercase tracking-wide">{label}</label>
      )}

      <textarea
        className={clsx(baseStyles, variantStyles[variant], errorStyles, 'resize-none', className)}
        {...props}
      />

      {error && <span className="text-[10px] font-medium text-[#e7000b]">{error}</span>}
    </div>
  );
}
