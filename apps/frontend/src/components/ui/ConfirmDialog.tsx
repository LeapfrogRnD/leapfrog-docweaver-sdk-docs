import { ReactNode } from 'react';
import { AlertCircle, AlertTriangle, Info, CheckCircle, X } from 'lucide-react';
import clsx from 'clsx';

interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  description: string | ReactNode;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'warning' | 'info' | 'success';
  isLoading?: boolean;
  iconExist?: boolean;
}

export function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  description,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  variant = 'danger',
  isLoading = false,
  iconExist = true,
}: ConfirmDialogProps) {
  if (!isOpen) return null;

  const variantStyles = {
    danger: {
      iconBg: 'bg-red-50',
      icon: <AlertCircle className="w-5 h-5 text-red-600" />,
      confirmBtn: 'bg-red-600 hover:bg-red-700 text-white',
    },
    warning: {
      iconBg: 'bg-yellow-50',
      icon: <AlertTriangle className="w-5 h-5 text-yellow-600" />,
      confirmBtn: 'bg-yellow-600 hover:bg-yellow-700 text-white',
    },
    info: {
      iconBg: 'bg-green-50',
      icon: <Info className="w-5 h-5 text-green-600" />,
      confirmBtn: 'bg-green-700 hover:bg-green-800 text-white',
    },
    success: {
      iconBg: 'bg-green-50',
      icon: <CheckCircle className="w-5 h-5 text-green-600" />,
      confirmBtn: 'bg-green-600 hover:bg-green-700 text-white',
    },
  };

  const currentVariant = variantStyles[variant];

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget && !isLoading) {
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      onClick={handleBackdropClick}
    >
      <div className="bg-white rounded-[14px] w-full max-w-md mx-4 shadow-2xl transform transition-all">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[rgba(0,0,0,0.1)]">
          <div className="flex items-center gap-3">
            {iconExist ? (
              <div
                className={clsx(
                  'w-10 h-10 rounded-[10px] flex items-center justify-center',
                  currentVariant.iconBg
                )}
              >
                {currentVariant.icon}
              </div>
            ) : (
              ''
            )}
            <h2 className="text-lg font-semibold text-[#111] tracking-[-0.4395px]">{title}</h2>
          </div>
          {!isLoading && (
            <button
              onClick={onClose}
              className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-[#f9fafb] transition-colors"
            >
              <X className="w-4 h-4 text-[#6b7280]" />
            </button>
          )}
        </div>

        {/* Content */}
        <div className="px-6 py-6">
          <div className="text-sm text-[#6b7280] leading-relaxed">{description}</div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-[rgba(0,0,0,0.1)]">
          <button
            onClick={onClose}
            disabled={isLoading}
            className="px-4 py-2 text-sm font-medium text-[#111] hover:bg-[#f9fafb] rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {cancelText}
          </button>
          <button
            onClick={onConfirm}
            disabled={isLoading}
            className={clsx(
              'px-4 py-2 text-sm font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2',
              currentVariant.confirmBtn
            )}
          >
            {isLoading && (
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            )}
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
