import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2 } from 'lucide-react';

import { SidePanel, Button } from '@/components/ui';
import { Form } from '@/components/ui/form';
import { Pipeline, PipelineCreateRequest, PipelineUpdateRequest } from '@/types/pipeline.type';
import { pipelineSchema, PipelineFormData } from '@/schemas/pipeline.schema';
import {
  useCreatePipeline,
  useUpdatePipeline,
  useGetPipelineConfigs,
} from '@/queries/pipeline.query';
import { useToast } from '@/context/ToastContext';
import FormSelect from '@/components/ui/FormSelect';
import { WatchedInput } from '@/components/ui/WatchedInput';
import cn from 'clsx';

interface PipelineModalProps {
  isOpen: boolean;
  setIsOpen?: (isOpen: boolean) => void;
  setEditingPipeline?: (pipeline: Pipeline | null) => void;
  onClose: () => void;
  pipeline: Pipeline | null;
}

export function PipelineModal({
  isOpen,
  onClose,
  pipeline,
  setIsOpen,
  setEditingPipeline,
}: PipelineModalProps) {
  const { data: configs, isLoading: isLoadingConfigs } = useGetPipelineConfigs();

  // Derive flat option maps from the API response for FormSelect
  const ocrProviderOptions = Object.fromEntries(
    (configs?.ocr_providers ?? []).map((p) => [p.value, p.label])
  );
  const vlmProviderOptions = Object.fromEntries(
    (configs?.vlm_providers ?? []).map((p) => [p.value, p.label])
  );
  const llmProviderOptions = Object.fromEntries(
    (configs?.llm_providers ?? []).map((p) => [p.value, p.label])
  );

  const getLlmModelOptions = (providerValue: string) =>
    Object.fromEntries(
      (configs?.llm_providers.find((p) => p.value === providerValue)?.models ?? []).map((m) => [
        m.value,
        m.label,
      ])
    );

  const getVlmModelOptions = (providerValue: string) =>
    Object.fromEntries(
      (configs?.vlm_providers.find((p) => p.value === providerValue)?.models ?? []).map((m) => [
        m.value,
        m.label,
      ])
    );

  const defaultLlmProvider = configs?.llm_providers[0]?.value ?? '';
  const defaultLlmModel = configs?.llm_providers[0]?.models[0]?.value ?? '';
  const defaultOcrProvider = configs?.ocr_providers[0]?.value ?? '';
  const defaultParsingMethod = configs?.parsing_methods?.[0]?.value ?? '';

  const createModeDefaults = (): PipelineFormData => ({
    name: '',
    description: null,
    ocr_provider: defaultOcrProvider,
    parsing_method: defaultParsingMethod,
    vlm_model_provider: null,
    vlm_model: null,
    llm_model_provider: defaultLlmProvider,
    llm_model: defaultLlmModel,
  });

  // 1. Initialize the form methods
  const form = useForm<PipelineFormData>({
    resolver: zodResolver(pipelineSchema),
    shouldUnregister: false,
    defaultValues: {
      name: '',
      description: null,
      ocr_provider: defaultOcrProvider,
      parsing_method: defaultParsingMethod,
      vlm_model_provider: null,
      vlm_model: null,
      llm_model_provider: defaultLlmProvider,
      llm_model: defaultLlmModel,
    },
  });

  // Re-apply defaults once configs load (form was created before data arrived)
  useEffect(() => {
    if (configs && !pipeline) {
      form.reset(createModeDefaults());
    }
  }, [configs]); // eslint-disable-line react-hooks/exhaustive-deps

  // Destructure for easier access
  const {
    handleSubmit,
    reset,
    watch,
    setValue,
    control,
    register,
    formState: { isSubmitting },
  } = form;

  // Watch values for conditional logic
  const selectedLlmProvider = watch('llm_model_provider');
  const selectedLlmModel = watch('llm_model');
  const selectedOcrProvider = watch('ocr_provider');
  const selectedVlmProvider = watch('vlm_model_provider');
  const pipelineName = watch('name');

  const { showToast } = useToast();
  const createMutation = useCreatePipeline();
  const updateMutation = useUpdatePipeline();
  const isLoading = isSubmitting || createMutation.isPending || updateMutation.isPending;

  // Sync form with pipeline data when editing
  useEffect(() => {
    if (isOpen && pipeline) {
      reset({
        name: pipeline.name,
        description: pipeline.description || '',
        ocr_provider: String(pipeline.ocr_provider || ''),
        parsing_method: String(pipeline.parsing_method || ''),
        llm_model_provider: String(pipeline.llm_model_provider || ''),
        llm_model: String(pipeline.llm_model || ''),
        vlm_model_provider: pipeline.vlm_model_provider || null,
        vlm_model: pipeline.vlm_model || null,
      });
    } else if (isOpen && !pipeline) {
      reset(createModeDefaults());
    }
  }, [pipeline, isOpen, reset]); // eslint-disable-line react-hooks/exhaustive-deps

  // Handle cascading dropdown logic for LLM
  useEffect(() => {
    if (selectedLlmProvider) {
      const availableModels = getLlmModelOptions(selectedLlmProvider);
      if (selectedLlmModel && !Object.keys(availableModels).includes(selectedLlmModel)) {
        setValue('llm_model', Object.keys(availableModels)[0] ?? '');
      }
    }
  }, [selectedLlmProvider]); // eslint-disable-line react-hooks/exhaustive-deps

  // Handle cascading dropdown logic for VLM
  useEffect(() => {
    if (selectedVlmProvider) {
      const availableModels = getVlmModelOptions(selectedVlmProvider);
      const currentVlmModel = watch('vlm_model');
      if (!Object.keys(availableModels).includes(currentVlmModel || '')) {
        setValue('vlm_model', Object.keys(availableModels)[0] ?? '');
      }
    }
  }, [selectedVlmProvider]); // eslint-disable-line react-hooks/exhaustive-deps

  const onSubmit = async (data: PipelineFormData) => {
    try {
      const payload = {
        ...data,
        description: data.description || null,
        parsing_method: 'layout_conserved',
      };
      if (pipeline) {
        await updateMutation.mutateAsync({
          id: pipeline.id,
          request: payload as PipelineUpdateRequest,
        });
        showToast('Pipeline updated', 'success');
      } else {
        await createMutation.mutateAsync(payload as PipelineCreateRequest);
        showToast('Pipeline created', 'success');
      }
      onClose();
      setIsOpen?.(false);
      setEditingPipeline?.(null);
    } catch (error: any) {
      showToast(error.message || 'Failed to save', 'error');
    }
  };

  return (
    <SidePanel
      isOpen={isOpen}
      onClose={onClose}
      title={pipeline ? 'Edit Pipeline' : 'Create New Pipeline'}
      size="xl"
    >
      {/* 2. WRAP EVERYTHING IN THE FORM PROVIDER */}
      <Form {...form}>
        {isLoadingConfigs ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="w-6 h-6 animate-spin text-[#038e43]" />
          </div>
        ) : (
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 pb-20">
            {/* Basic Settings */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">Basic Settings</h3>
              <WatchedInput
                control={control}
                name="name" // Matches schema key
                label="Pipeline Name"
                placeholder="Name that describes the pipeline"
                required={true}
              />

              <div className="space-y-1.5">
                <label className="text-sm font-medium text-gray-700">Description (Optional)</label>
                <textarea
                  {...register('description')}
                  placeholder="Briefly describe the purpose of this pipeline..."
                  className={cn(
                    'w-full px-4 py-2 text-sm bg-gray-50 border border-gray-200 rounded-md outline-none transition-all',
                    'focus:ring-2 focus:ring-green-600 focus:border-transparent resize-none min-h-[100px]'
                  )}
                  rows={3}
                />
              </div>
            </div>

            {/* OCR Provider */}
            <div className="space-y-4 pt-4 border-t">
              <h3 className="text-lg font-semibold text-gray-900">OCR Provider</h3>
              <FormSelect
                control={control}
                name="ocr_provider"
                label="OCR Provider"
                options={ocrProviderOptions}
              />
            </div>

            {/* VLM Settings (Conditional) */}
            {selectedOcrProvider === 'vlm' && (
              <div className="space-y-4 pt-4 border-t animate-in fade-in slide-in-from-top-2">
                <h3 className="text-lg font-semibold text-gray-900">Vision Language Model</h3>
                <div className="grid grid-cols-2 gap-4">
                  <FormSelect
                    control={control}
                    name="vlm_model_provider"
                    label="VLM Provider"
                    options={vlmProviderOptions}
                  />
                  <FormSelect
                    control={control}
                    name="vlm_model"
                    label="VLM Model"
                    options={getVlmModelOptions(selectedVlmProvider ?? '')}
                  />
                </div>
              </div>
            )}

            {/* LLM Settings */}
            <div className="space-y-4 pt-4 border-t">
              <h3 className="text-lg font-semibold text-gray-900">Language Model</h3>
              <div className="grid grid-cols-2 gap-4">
                <FormSelect
                  control={control}
                  name="llm_model_provider"
                  label="LLM Provider"
                  options={llmProviderOptions}
                />
                <FormSelect
                  control={control}
                  name="llm_model"
                  label="LLM Model"
                  options={getLlmModelOptions(selectedLlmProvider ?? '')}
                />
              </div>
            </div>

            {/* Sticky Actions Footer */}
            <div className="flex gap-3 pt-4 pb-2 border-t sticky bottom-0 bg-white z-10 mt-8">
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                className="flex-1"
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={isLoading || !pipelineName?.trim()}
                className="flex-1 bg-[#038e43] hover:bg-[#027a39]"
              >
                {isLoading ? (
                  <span className="flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Saving...
                  </span>
                ) : pipeline ? (
                  'Update Pipeline'
                ) : (
                  'Create Pipeline'
                )}
              </Button>
            </div>
          </form>
        )}
      </Form>
    </SidePanel>
  );
}
