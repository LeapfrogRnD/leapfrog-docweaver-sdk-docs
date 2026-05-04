import React from 'react';
import { LucideIcon } from 'lucide-react';

interface SelectionCardProps {
  title: string;
  description: string | null;
  icon: LucideIcon;
  isActive?: boolean;
  onClick: () => void;
  variant?: 'vertical' | 'horizontal';
  badge?: React.ReactNode;
}

export function SelectionCard({
  title,
  description,
  icon: Icon,
  isActive,
  onClick,
  variant = 'horizontal',
  badge,
}: SelectionCardProps) {
  const activeClasses = 'bg-[#f0fdf4] border-[#038e43]';
  const inactiveClasses = 'bg-white border-[rgba(0,0,0,0.1)] hover:border-[#038e43]';
  const iconActiveClasses = 'bg-[#dcfce7] text-[#038e43]';
  const iconInactiveClasses = 'bg-[#f3f4f6] text-[#6b7280]';

  if (variant === 'vertical') {
    return (
      <button
        type="button"
        onClick={onClick}
        className={`p-4 rounded-[14px] text-center transition-all border ${
          isActive ? activeClasses : inactiveClasses
        }`}
      >
        <div className="flex flex-col items-center gap-2">
          <Icon className={`w-6 h-6 ${isActive ? 'text-[#038e43]' : 'text-[#6b7280]'}`} />
          <h3
            className={`text-md font-medium tracking-[-0.4395px] ${isActive ? 'text-[#038e43]' : 'text-[#101828]'}`}
          >
            {title}
          </h3>
          {description && <p className="text-xs text-[#4a5565]">{description}</p>}
        </div>
      </button>
    );
  }

  return (
    <button
      type="button"
      onClick={onClick}
      className={`p-4 rounded-[14px] text-left transition-all border ${
        isActive ? activeClasses : inactiveClasses
      }`}
    >
      <div className="flex gap-3">
        <div
          className={`w-9 h-9 rounded-[10px] flex items-center justify-center flex-shrink-0 ${
            isActive ? iconActiveClasses : iconInactiveClasses
          }`}
        >
          <Icon className="w-4 h-4" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-1">
            <span
              className={`text-sm font-medium tracking-[-0.4395px] ${isActive ? 'text-[#038e43]' : 'text-[#101828]'}`}
            >
              {title}
            </span>
            {badge}
          </div>
          {description && (
            <p className="text-xs text-[#6b7280] break-words mt-0.5">{description}</p>
          )}
        </div>
      </div>
    </button>
  );
}
