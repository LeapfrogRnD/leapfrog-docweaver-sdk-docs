import { InputHTMLAttributes, ReactNode } from 'react';
import clsx from 'clsx';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: ReactNode;
  error?: string;
}

export function Input({ label, error, className = '', ...props }: InputProps) {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-primary-black mb-2">{label}</label>
      )}
      <input
        className={clsx(
          'w-full px-4 py-2 border border-primary-ivory rounded-lg',
          'focus:outline-none focus:ring-2 focus:ring-primary-brand focus:border-transparent',
          'transition-all duration-200',
          'text-primary-black placeholder:text-gray-400',
          error && 'border-red-500',
          className
        )}
        {...props}
      />
      {error && <p className="mt-1 text-sm text-red-500">{error}</p>}
    </div>
  );
}
