import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2 } from 'lucide-react';

import { SidePanel, Input, Button } from '@/components/ui';
import { Form } from '@/components/ui/form'; // Import Shadcn Form
import { WatchedInput } from '@/components/ui/WatchedInput';
import { ApiKeyFormData, apiKeySchema } from '@/schemas/api-keys.schema';
import { ApiKey, ApiKeyCreateRequest, ApiKeyUpdateRequest } from '@/types/api-key.type';
import { useCreateApiKey, useUpdateApiKey } from '@/queries/api-key.query';
import { useToast } from '@/context/ToastContext';
import AlertBanner from '@/components/infoStep';

interface ApiKeyModalProps {
  isOpen: boolean;
  apiKey?: ApiKey | null;
  onClose: () => void;
  onSave: () => void;
}

export function ApiKeyModal({ isOpen, onClose, apiKey, onSave }: ApiKeyModalProps) {
  const form = useForm<ApiKeyFormData>({
    resolver: zodResolver(apiKeySchema),
    mode: 'onChange',
    defaultValues: { name: '', webhook_url: '' },
  });

  const {
    register,
    handleSubmit,
    reset,
    control,
    formState: { errors, isValid, isDirty, isSubmitting },
  } = form;

  const createMutation = useCreateApiKey();
  const updateMutation = useUpdateApiKey();
  const { showToast } = useToast();

  const isLoading = isSubmitting || createMutation.isPending || updateMutation.isPending;

  useEffect(() => {
    if (apiKey && isOpen) {
      reset({
        name: apiKey.secret_name,
        webhook_url: apiKey.webhook_url || '',
      });
    } else if (isOpen) {
      reset({ name: '', webhook_url: '' });
    }
  }, [apiKey, isOpen, reset]);

  const onSubmit = async (data: ApiKeyFormData) => {
    try {
      const cleanWebhookUrl: string | undefined =
        data.webhook_url?.trim() === '' ? undefined : data.webhook_url;

      if (apiKey) {
        const request: ApiKeyUpdateRequest = {
          secret_name: data.name,
          webhook_url: cleanWebhookUrl,
        };
        await updateMutation.mutateAsync({ id: apiKey.id, request });
        showToast('API key updated successfully', 'success');
      } else {
        const request: ApiKeyCreateRequest = {
          secret_name: data.name,
          webhook_url: cleanWebhookUrl,
        };
        await createMutation.mutateAsync(request);
        showToast('API key created successfully', 'success');
      }
      onSave();
      handleClose();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Action failed';
      showToast(errorMessage, 'error');
    }
  };
  const handleClose = () => {
    reset();
    onClose();
  };

  return (
    <SidePanel
      isOpen={isOpen}
      onClose={handleClose}
      title={apiKey ? 'Update API Key' : 'Create New API Key'}
      size="md"
    >
      <Form {...form}>
        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col h-full space-y-8 p-1">
          <div className="space-y-6 flex-1">
            {/* API Key Name with Live Watching */}
            <WatchedInput
              control={control}
              name="name"
              label="API Key Name"
              placeholder="e.g., Production API Key"
              required={true}
            />

            {/* Webhook URL (Standard Input as it's optional) */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-gray-700">
                Webhook URL <span className="text-gray-400 font-normal">(Optional)</span>
              </label>
              <Input
                {...register('webhook_url')}
                placeholder="e.g., https://example.com/webhook"
                error={errors.webhook_url?.message}
                className="bg-gray-50 border-gray-200 focus:ring-green-600 transition-all"
              />
              <p className="text-[11px] text-gray-500 uppercase tracking-tight font-semibold">
                Must be a <span className="text-primary-brand font-mono">POST</span> endpoint.
              </p>
            </div>

            <AlertBanner
              variant="note"
              title="Key Permissions"
              description={
                <ul className="mt-2 ml-4 list-disc text-xs text-gray-500 leading-relaxed space-y-1">
                  <li>Keys grant full access to the associated project.</li>
                  <li>Keep your keys secure and never share them publicly.</li>
                  <li>Use descriptive names to track usage effectively.</li>
                </ul>
              }
            />
          </div>

          {/* Sticky Actions Footer */}
          <div className="flex gap-3 pt-6 border-t bg-white sticky bottom-0">
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
              className="flex-1"
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              className="flex-1 bg-[#038e43] text-white hover:bg-[#027235]"
              disabled={isLoading || !isValid || (apiKey ? !isDirty : false)}
            >
              {isLoading ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Processing...
                </span>
              ) : apiKey ? (
                'Update Key'
              ) : (
                'Create Key'
              )}
            </Button>
          </div>
        </form>
      </Form>
    </SidePanel>
  );
}
