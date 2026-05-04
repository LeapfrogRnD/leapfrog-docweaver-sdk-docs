import { useState, useCallback } from 'react';

interface ConfirmOptions {
  title: string;
  description: string | React.ReactNode;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'warning' | 'info' | 'success';
  onConfirm: () => void | Promise<void>;
  onCancel?: () => void;
}

interface ConfirmDialogState {
  isOpen: boolean;
  isLoading: boolean;
  options: ConfirmOptions | null;
}

export function useConfirmDialog() {
  const [state, setState] = useState<ConfirmDialogState>({
    isOpen: false,
    isLoading: false,
    options: null,
  });

  const confirm = useCallback((options: ConfirmOptions) => {
    setState({
      isOpen: true,
      isLoading: false,
      options,
    });
  }, []);

  const handleConfirm = useCallback(async () => {
    if (!state.options) return;

    setState((prev) => ({ ...prev, isLoading: true }));

    try {
      await state.options.onConfirm();
      setState({ isOpen: false, isLoading: false, options: null });
    } catch (error) {
      // Let the calling code handle the error
      setState((prev) => ({ ...prev, isLoading: false }));
      throw error;
    }
  }, [state.options]);

  const handleCancel = useCallback(() => {
    state.options?.onCancel?.();
    setState({ isOpen: false, isLoading: false, options: null });
  }, [state.options]);

  return {
    confirm,
    isOpen: state.isOpen,
    isLoading: state.isLoading,
    options: state.options,
    handleConfirm,
    handleCancel,
  };
}
