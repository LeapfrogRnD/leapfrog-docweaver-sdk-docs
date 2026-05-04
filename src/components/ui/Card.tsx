import { ReactNode } from 'react';
import clsx from 'clsx';

interface CardProps {
  children: ReactNode;
  className?: string;
  variant?: 'default' | 'bordered';
}

export function Card({ children, className = '', variant = 'default' }: CardProps) {
  return (
    <div
      className={clsx(
        'bg-white rounded-2xl',
        variant === 'default' && 'border border-primary-ivory shadow-sm',
        variant === 'bordered' && 'border border-[rgba(0,0,0,0.1)]',
        className
      )}
    >
      {children}
    </div>
  );
}

interface CardHeaderProps {
  children: ReactNode;
  className?: string;
}

export function CardHeader({ children, className = '' }: CardHeaderProps) {
  return <div className={clsx('px-6 py-4', className)}>{children}</div>;
}

interface CardTitleProps {
  children: ReactNode;
  className?: string;
}

export function CardTitle({ children, className = '' }: CardTitleProps) {
  return (
    <h3 className={clsx('text-base font-medium text-primary-black', className)}>{children}</h3>
  );
}

interface CardDescriptionProps {
  children: ReactNode;
  className?: string;
}

export function CardDescription({ children, className = '' }: CardDescriptionProps) {
  return <p className={clsx('text-base text-[#666] mt-2', className)}>{children}</p>;
}

interface CardContentProps {
  children: ReactNode;
  className?: string;
}

export function CardContent({ children, className = '' }: CardContentProps) {
  return <div className={clsx('px-6 pb-6', className)}>{children}</div>;
}
