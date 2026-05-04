import { ElementType } from 'react';
import clsx from 'clsx';

interface StatCardProps {
  title: string;
  value: string | number | undefined;
  subtitle: string;
  icon?: ElementType;
  iconBgColor?: string;
  iconColor?: string;
  valueColor?: string;
}

export function StatCard({
  title,
  value,
  subtitle,
  icon,
  iconBgColor = 'bg-blue-50',
  iconColor = 'text-[#3b82f6]',
  valueColor = 'text-black',
}: StatCardProps) {
  const IconComp = icon as ElementType | undefined;

  return (
    <div key={title} className="bg-white border border-[rgba(0,0,0,0.1)] rounded-[14px] p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs text-[#4a5565] mb-1">{title}</p>
          <p className={clsx('text-xl font-semibold', valueColor)}>{value}</p>
          <p className="text-2xl font-semibold">{subtitle}</p>
        </div>
        <div
          className={clsx(
            'w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0',
            iconBgColor
          )}
        >
          {IconComp ? <IconComp className={clsx('w-6 h-6', iconColor)} /> : null}
        </div>
      </div>
    </div>
  );
}
