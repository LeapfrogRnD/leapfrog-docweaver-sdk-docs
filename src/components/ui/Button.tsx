import { ReactNode } from 'react';
import clsx from 'clsx';

interface ButtonProps {
  children: ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'none';
  disabled?: boolean;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
  icon?: ReactNode;
}

export function Button({
  children,
  onClick,
  variant = 'primary',
  disabled = false,
  type = 'button',
  className = '',
  icon,
}: ButtonProps) {
  const baseStyles =
    'inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all duration-200 shadow-sm';

  const variantStyles = {
    primary:
      'bg-primary-brand text-white hover:bg-[#027235] active:bg-[#026129] disabled:opacity-50 disabled:cursor-not-allowed',
    secondary:
      'bg-[#fafafa] text-primary-black border border-primary-ivory hover:bg-gray-100 active:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed',
    outline:
      'bg-transparent text-primary-black border border-primary-ivory hover:bg-gray-50 active:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed',
    none: 'bg-transparent text-primary-black hover:bg-gray-50 active:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={clsx(baseStyles, variantStyles[variant], className)}
    >
      {icon && <span className="shrink-0">{icon}</span>}
      {children}
    </button>
  );
}
