import { ReactNode } from 'react';
import clsx from 'clsx';

interface TableProps {
  children: ReactNode;
  className?: string;
  variant?: 'card' | 'plain';
}

export function Table({ children, className = '', variant = 'card' }: TableProps) {
  return (
    <div
      className={clsx(
        'overflow-x-auto',
        variant === 'card' &&
          'bg-white rounded-[14px] border border-[rgba(0,0,0,0.1)] overflow-hidden',
        className
      )}
    >
      <table className="w-full min-w-full">{children}</table>
    </div>
  );
}

interface TableHeaderProps {
  children: ReactNode;
  className?: string;
}

export function TableHeader({ children, className = '' }: TableHeaderProps) {
  return (
    <thead className={clsx('bg-[#f9fafb] border-b border-[rgba(0,0,0,0.1)]', className)}>
      {children}
    </thead>
  );
}

interface TableBodyProps {
  children: ReactNode;
  className?: string;
}

export function TableBody({ children, className = '' }: TableBodyProps) {
  return <tbody className={clsx('divide-y divide-[rgba(0,0,0,0.1)]', className)}>{children}</tbody>;
}

interface TableRowProps {
  children: ReactNode;
  className?: string;
  onClick?: () => void;
}

export function TableRow({ children, className = '', onClick }: TableRowProps) {
  return (
    <tr
      className={clsx(
        'hover:bg-[#f9fafb] transition-colors',
        onClick && 'cursor-pointer',
        className
      )}
      onClick={onClick}
    >
      {children}
    </tr>
  );
}

interface TableHeadProps {
  children: ReactNode;
  className?: string;
  align?: 'left' | 'center' | 'right';
}

export function TableHead({ children, className = '', align = 'left' }: TableHeadProps) {
  return (
    <th
      className={clsx(
        'px-6 py-3 text-xs font-medium text-[#6b7280] uppercase tracking-wider',
        align === 'left' && 'text-left',
        align === 'center' && 'text-center',
        align === 'right' && 'text-right',
        className
      )}
    >
      {children}
    </th>
  );
}

interface TableCellProps {
  children: ReactNode;
  className?: string;
  align?: 'left' | 'center' | 'right';
  colSpan?: number;
}

export function TableCell({ children, className = '', align = 'left', colSpan }: TableCellProps) {
  return (
    <td
      colSpan={colSpan}
      className={clsx(
        'px-6 py-4',
        align === 'left' && 'text-left',
        align === 'center' && 'text-center',
        align === 'right' && 'text-right',
        className
      )}
    >
      {children}
    </td>
  );
}
