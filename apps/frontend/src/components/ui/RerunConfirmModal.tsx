import { AlertCircle, Settings, RotateCw, X, Lock } from 'lucide-react';
import { Modal } from './Modal';
import { useNavigate } from 'react-router-dom';

interface RerunConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onRerunWithSameSettings: () => void;
  onChangeSettings: () => void;
  taskName?: string;
  isOwnedByCurrentUser?: boolean;
}

export function RerunConfirmModal({
  isOpen,
  onClose,
  onRerunWithSameSettings,
  onChangeSettings,
  taskName,
  isOwnedByCurrentUser = true,
}: RerunConfirmModalProps) {
  const navigate = useNavigate();
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <div className="bg-white rounded-[14px] w-full max-w-md overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[rgba(0,0,0,0.1)]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#fef3c7] rounded-[10px] flex items-center justify-center">
              <AlertCircle className="w-5 h-5 text-[#d97706]" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-[#111] tracking-[-0.4395px]">
                Re-run OCR Processing
              </h2>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-[#f9fafb] transition-colors"
          >
            <X className="w-4 h-4 text-[#6b7280]" />
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-6 space-y-4">
          <p className="text-sm text-[#6b7280] leading-relaxed">
            {taskName ? (
              <>
                You are about to re-run OCR processing for{' '}
                <span className="font-medium text-[#111]">"{taskName}"</span>.
              </>
            ) : (
              'You are about to re-run OCR processing for this task.'
            )}
          </p>

          {!isOwnedByCurrentUser ? (
            <div className="flex items-start gap-3 p-4 bg-[#fef2f2] border border-[#fecaca] rounded-[10px]">
              <div className="w-8 h-8 bg-[#fee2e2] rounded-lg flex items-center justify-center flex-shrink-0">
                <Lock className="w-4 h-4 text-[#dc2626]" />
              </div>
              <div>
                <h3 className="text-sm font-medium text-[#dc2626] mb-1">Permission Denied</h3>
                <p className="text-xs text-[#6b7280] leading-relaxed">
                  You can only re-run tasks that you created. This task belongs to another user.
                </p>
              </div>
            </div>
          ) : (
            <>
              <p className="text-sm text-[#6b7280] leading-relaxed">Would you like to:</p>

              {/* Options */}
              <div className="space-y-3">
                {/* Re-run with same settings */}
                <button
                  onClick={() => {
                    onRerunWithSameSettings();
                    onClose();
                    navigate('/tasks');
                  }}
                  className="w-full p-4 bg-white border border-[rgba(0,0,0,0.1)] rounded-[10px] hover:border-[#038e43] hover:bg-[#f0fdf4] transition-all text-left group"
                >
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-[#f3f4f6] group-hover:bg-[#dcfce7] rounded-lg flex items-center justify-center flex-shrink-0 transition-colors">
                      <RotateCw className="w-4 h-4 text-[#6b7280] group-hover:text-[#038e43]" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-sm font-medium text-[#111] mb-1">
                        Re-run with same settings
                      </h3>
                      <p className="text-xs text-[#6b7280] leading-relaxed">
                        Process the document again using the current pipeline and extraction
                        settings
                      </p>
                    </div>
                  </div>
                </button>

                {/* Change settings */}
                <button
                  onClick={() => {
                    onChangeSettings();
                    onClose();
                  }}
                  className="w-full p-4 bg-white border border-[rgba(0,0,0,0.1)] rounded-[10px] hover:border-[#038e43] hover:bg-[#f0fdf4] transition-all text-left group"
                >
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-[#f3f4f6] group-hover:bg-[#dcfce7] rounded-lg flex items-center justify-center flex-shrink-0 transition-colors">
                      <Settings className="w-4 h-4 text-[#6b7280] group-hover:text-[#038e43]" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-sm font-medium text-[#111] mb-1">
                        Change settings before re-running
                      </h3>
                      <p className="text-xs text-[#6b7280] leading-relaxed">
                        Modify the pipeline, extraction mode, or other settings before processing
                      </p>
                    </div>
                  </div>
                </button>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-2 px-6 py-4 border-t border-[rgba(0,0,0,0.1)]">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-[#111] hover:bg-[#f9fafb] rounded-lg transition-colors"
          >
            {isOwnedByCurrentUser ? 'Cancel' : 'Close'}
          </button>
        </div>
      </div>
    </Modal>
  );
}
