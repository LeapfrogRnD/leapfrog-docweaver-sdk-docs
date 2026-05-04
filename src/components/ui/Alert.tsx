import type { ReactNode } from 'react';
import clsx from 'clsx';
import { AlertCircle, CheckCircle2, Info, SparkleIcon, TriangleAlert, X } from 'lucide-react';

type AlertVariant = 'info' | 'error' | 'success' | 'warning' | 'guidance' | 'note';

interface AlertProps {
  variant?: AlertVariant;
  icon?: ReactNode;
  className?: string;
  children?: ReactNode;
  onClose?: () => void;
}

interface AlertSubProps {
  children?: ReactNode;
}

const variantStyles: Record<
  AlertVariant,
  { container: string; icon: ReactNode; titleColor: string }
> = {
  info: {
    container: 'bg-blue-50 border-blue-200',
    icon: <Info className="text-blue-600" size={24} />,
    titleColor: 'text-blue-900',
  },
  error: {
    container: 'bg-red-50 border-red-200',
    icon: <AlertCircle className="text-red-700" size={24} />,
    titleColor: 'text-red-900',
  },
  success: {
    container: 'bg-green-50 border-green-200',
    icon: <CheckCircle2 className="text-green-600" size={24} />,
    titleColor: 'text-green-900',
  },
  warning: {
    container: 'bg-amber-50 border-amber-200',
    icon: <TriangleAlert className="text-amber-600" size={24} />,
    titleColor: 'text-amber-900',
  },
  guidance: {
    container: '',
    icon: <SparkleIcon className="text-black" size={24} />,
    titleColor: '',
  },
  note: {
    container: '',
    icon: '',
    titleColor: '',
  },
};

export function Alert({ variant = 'info', icon, className = '', children, onClose }: AlertProps) {
  const cfg = variantStyles[variant];

  return (
    <div
      role="alert"
      className={clsx(
        'flex gap-4 p-4 rounded-xl border items-start transition-colors duration-200',
        cfg.container,
        className
      )}
    >
      <div className="flex-shrink-0 pt-0.5">{icon || cfg.icon}</div>

      <div className="flex flex-col gap-1">{children}</div>

      {/* Close button on the right */}
      {onClose && (
        <button
          type="button"
          onClick={onClose}
          aria-label="Close"
          className="ml-auto -mr-1 text-[#6b7280] hover:text-[#374151] focus:outline-none"
        >
          <X size={16} />
        </button>
      )}
    </div>
  );
}

export function AlertTitle({ children }: AlertSubProps) {
  return <h3 className="font-semibold text-sm md:text-sm leading-tight">{children}</h3>;
}

export function AlertDescription({ children }: AlertSubProps) {
  return <p className="text-[#6b7280] text-xs md:text-xs leading-relaxed">{children}</p>;
}
