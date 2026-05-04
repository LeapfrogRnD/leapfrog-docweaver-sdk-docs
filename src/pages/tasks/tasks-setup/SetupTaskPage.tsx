import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useForm, FormProvider } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { ArrowLeft, FileText, Save, CheckCircle } from 'lucide-react';
import { PageHeader } from '@/components';

import {
  TaskFormStepper,
  TaskInfoStep,
  DocumentUploadStep,
  PipelineConfigStep,
} from './components';
import { taskCreationFlowSchema, TaskCreationFlowFormData } from '@/schemas/task.schema';
import {
  useCreateOrUpdateTaskName,
  useGeneratePresignedUrl,
  useConfirmDocUpload,
  useUpdateTaskConfiguration,
  useExecuteTask,
  useGetTask,
} from '@/queries/task.query';
import { useTaskStore } from '@/store/taskStore';
import { TaskType } from '@/types/task.type';
import { useToast } from '@/context/ToastContext';
import { SetupTaskSkeleton } from './components/SetupTaskSkeleton';

export function SetupTaskPage() {
  const navigate = useNavigate();
  const { showToast } = useToast();

  const { taskId: editTaskId } = useParams<{ taskId: string }>();
  const [_, setIsProcessing] = useState(false);
  const [originalTaskName, setOriginalTaskName] = useState<string>('');

  // Zustand store
  const {
    currentStep,
    taskId,
    editingDraftId,
    isCreatePipelineOpen,
    formData,
    isEditMode,
    setTaskId,
    setEditingDraftId,
    setIsCreatePipelineOpen,
    setIsEditMode,
    updateFormData,
    clearTaskCreation,
    nextStep,
    previousStep,
    getUploadedFileNames,
    populateEditData,
    isUploadCompleted,
  } = useTaskStore();

  // Fetch task details when in edit mode
  const { data: taskDetail, isLoading: isLoadingTask } = useGetTask(
    editTaskId ? Number(editTaskId) : 0
  );

  // React Hook Form setup with persisted data
  const methods = useForm<TaskCreationFlowFormData>({
    resolver: zodResolver(taskCreationFlowSchema),
    defaultValues: {
      taskName: formData.taskName || '',
      uploadedFiles: [],
      additionalInstruction: formData.additionalInstruction || '',
      taskType: formData.taskType || undefined,
      pipelineId: formData.pipelineId || undefined,
      // persist enableContext across form sessions
      enableContext: typeof formData.enableContext !== 'undefined' ? formData.enableContext : false,
      fileStatus: formData.fileStatus,
      extractionFields: formData.extractionFields || [],
      classificationCategories: formData.classificationCategories || [],
    },
    mode: 'onChange',
  });

  const { watch, setValue, reset } = methods;
  const watchedValues = watch();

  useEffect(() => {
    if (editTaskId && taskDetail && !isEditMode) {
      setIsEditMode(true);
      setTaskId(taskDetail.id);
      setEditingDraftId(String(taskDetail.id));
      setOriginalTaskName(taskDetail.name);

      let extractionFields: any[] = [];
      let classificationCategories: any[] = [];

      if (taskDetail.json_schema) {
        if (taskDetail.task_type === TaskType.EXTRACTION && taskDetail.json_schema) {
          extractionFields = taskDetail.json_schema.map((extractor: any) => ({
            name: extractor.name,
            type: extractor.type,
            title: extractor.title,
            description: extractor.description,
          }));
        } else if (taskDetail.task_type === TaskType.CLASSIFICATION) {
          const classifiers = Array.isArray(taskDetail.json_schema)
            ? taskDetail.json_schema
            : (taskDetail.json_schema.classifiers ?? []);
          classificationCategories = classifiers.map((classifier: any) => ({
            category: classifier.category,
            fields: classifier.fields,
          }));
        }
      }

      // Build file info from task metadata
      const fileInfo = taskDetail.file_metadata
        ? [
            {
              name: taskDetail.file_metadata.file_name,
              size: taskDetail.file_metadata.file_size,
              type: taskDetail.file_metadata.content_type,
            },
          ]
        : [];

      const editData = {
        taskName: taskDetail.name,
        additionalInstruction: taskDetail.additional_instruction || '',
        taskType: taskDetail.task_type || undefined,
        pipelineId: taskDetail.pipeline_id || undefined,
        // map backend flag to form field
        enableContext:
          typeof taskDetail.enable_context !== 'undefined' ? taskDetail.enable_context : false,
        fileStatus: formData.fileStatus,
        extractionFields,
        classificationCategories,
        uploadedFiles: fileInfo,
      };
      populateEditData(editData);

      // Reset form with new values
      reset({
        taskName: taskDetail.name,
        uploadedFiles:
          fileInfo.length > 0 ? [new File([''], fileInfo[0].name, { type: fileInfo[0].type })] : [],
        additionalInstruction: taskDetail.additional_instruction || '',
        taskType: taskDetail.task_type || undefined,
        pipelineId: taskDetail.pipeline_id || undefined,
        enableContext:
          typeof taskDetail.enable_context !== 'undefined' ? taskDetail.enable_context : false,
        extractionFields,
        classificationCategories,
        fileStatus: taskDetail.file_status,
      });
    }
  }, [
    editTaskId,
    taskDetail,
    isEditMode,
    setIsEditMode,
    setTaskId,
    setEditingDraftId,
    populateEditData,
    reset,
    formData.fileStatus,
  ]);

  // Sync form data with store on changes (excluding uploadedFiles which are handled separately)
  useEffect(() => {
    // Don't sync during initial load in edit mode
    if (editTaskId && !isEditMode) return;

    const subscription = watch((value) => {
      const { uploadedFiles: _uploadedFiles, ...otherData } = value as TaskCreationFlowFormData;
      updateFormData(otherData);
    });
    return () => subscription.unsubscribe();
  }, [watch, updateFormData, editTaskId, isEditMode]);

  // Restore form values from store on mount (only for create mode or after edit data is loaded)
  useEffect(() => {
    // Skip restoration if in edit mode and data not yet loaded
    if (editTaskId && !isEditMode) return;

    const restoreFormData = async () => {
      // Only restore if we have persisted data
      if (formData.taskName && !watchedValues.taskName) {
        setValue('taskName', formData.taskName);
      }
      if (formData.additionalInstruction && !watchedValues.additionalInstruction) {
        setValue('additionalInstruction', formData.additionalInstruction);
      }
      if (formData.taskType && !watchedValues.taskType) {
        setValue('taskType', formData.taskType);
      }
      if (formData.pipelineId && !watchedValues.pipelineId) {
        setValue('pipelineId', formData.pipelineId);
      }
      if (
        formData.extractionFields &&
        (!watchedValues.extractionFields || watchedValues.extractionFields.length === 0)
      ) {
        setValue('extractionFields', formData.extractionFields);
      }
      if (
        formData.classificationCategories &&
        (!watchedValues.classificationCategories ||
          watchedValues.classificationCategories.length === 0)
      ) {
        setValue('classificationCategories', formData.classificationCategories);
      }

      // Restore persisted enableContext flag if present
      if (
        typeof formData.enableContext !== 'undefined' &&
        typeof watchedValues.enableContext === 'undefined'
      ) {
        setValue('enableContext', formData.enableContext);
      }

      // Handle uploaded files separately - just show filenames for persistence
      if (!watchedValues.uploadedFiles || watchedValues.uploadedFiles.length === 0) {
        const fileNames = getUploadedFileNames();
        if (fileNames.length > 0) {
          // Create mock File objects just for display purposes
          const mockFiles = fileNames.map(
            (name) => new File([''], name, { type: 'application/octet-stream' })
          );
          setValue('uploadedFiles', mockFiles);
        }
      }
    };

    restoreFormData();
  }, [setValue, getUploadedFileNames, editTaskId, isEditMode]);

  // API mutations
  const createOrUpdateTaskNameMutation = useCreateOrUpdateTaskName();
  const generatePresignedUrlMutation = useGeneratePresignedUrl();
  const confirmDocUploadMutation = useConfirmDocUpload();
  const updateTaskConfigurationMutation = useUpdateTaskConfiguration();
  const executeTaskMutation = useExecuteTask();

  const handleBack = () => {
    if (currentStep === 1) {
      // Clear store data when leaving task creation
      clearTaskCreation();
      navigate('/tasks');
    } else {
      previousStep();
    }
  };

  const handleNext = async () => {
    if (currentStep === 1) {
      await handleStep1Submit();
    } else if (currentStep === 2) {
      await handleStep2Submit();
    } else if (currentStep === 3) {
      await handleStep3Submit();
    }
  };

  // Step 1: Create task with name
  const handleStep1Submit = async () => {
    try {
      if (isEditMode) {
        const hasNameChanged = watchedValues.taskName !== originalTaskName;
        if (hasNameChanged) {
          await createOrUpdateTaskNameMutation.mutateAsync({
            task_id: taskId,
            name: watchedValues.taskName,
          });
        }
      } else {
        const result = await createOrUpdateTaskNameMutation.mutateAsync({
          task_id: taskId,
          name: watchedValues.taskName,
        });
        setTaskId(result.id);
      }

      nextStep();
    } catch (error) {
      console.error('Failed to create/update task:', error);
    }
  };

  // Step 2: Check if file is uploaded and proceed
  const handleStep2Submit = async () => {
    // Get filenames from store instead of full files
    const fileNames = getUploadedFileNames();

    if (!taskId || fileNames.length === 0) {
      console.error('No task ID or files selected');
      return;
    }
    nextStep();
  };

  // Step 3: Configure task and finalize
  const handleStep3Submit = async (shouldExecutePipeline: boolean = true) => {
    if (!taskId) {
      console.error('No task ID found');
      return;
    }

    try {
      if (shouldExecutePipeline) {
        setIsProcessing(true);
      }

      // Build JSON schema based on task type
      let jsonSchema: Record<string, any> = {};

      if (watchedValues.taskType === 'extraction') {
        jsonSchema =
          watchedValues.extractionFields?.map((field) => ({
            name: field.name,
            type: field.type,
            description: field.description,
          })) || [];
      } else if (watchedValues.taskType === 'classification') {
        jsonSchema =
          watchedValues.classificationCategories?.map((category) => ({
            category: category.category,
            fields: category.fields,
          })) || [];
      }

      // Update task configuration
      await updateTaskConfigurationMutation.mutateAsync({
        taskId,
        request: {
          additional_instruction: watchedValues.additionalInstruction,
          task_type: watchedValues.taskType!,
          json_schema: jsonSchema,
          enable_context: watchedValues.enableContext,
          pipeline_id: watchedValues.pipelineId!,
        },
      });

      // Only execute the pipeline if shouldExecutePipeline is true (Create & Process Task)
      if (shouldExecutePipeline) {
        await executeTaskMutation.mutateAsync(taskId);
        showToast('Task configured and executed successfully', 'success');
      } else {
        showToast('Task configuration saved as draft', 'success');
      }

      // Clear store data after successful creation
      clearTaskCreation();
      navigate('/tasks');
    } catch (error) {
      showToast(
        error instanceof Error ? error.message : 'Failed to save task configuration',
        'error'
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSaveDraft = async () => {
    await handleStep3Submit(false); // Save configuration but don't execute pipeline
  };

  const handleCreateAndProcess = async () => {
    await handleStep3Submit(true); // Save configuration and execute pipeline
  };

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return watchedValues.taskName?.trim().length > 0;
      case 2:
        return (
          watchedValues.uploadedFiles?.length > 0 &&
          (isUploadCompleted || watchedValues.fileStatus == 'uploaded')
        );
      case 3:
        return (
          watchedValues.taskType &&
          watchedValues.pipelineId &&
          ((watchedValues.taskType === 'extraction' &&
            (watchedValues.extractionFields?.length || 0) > 0) ||
            (watchedValues.taskType === 'classification' &&
              (watchedValues.classificationCategories?.length || 0) > 0) ||
            watchedValues.taskType === 'summarization')
        );
      default:
        return false;
    }
  };

  const isLoading =
    isLoadingTask ||
    createOrUpdateTaskNameMutation.isPending ||
    generatePresignedUrlMutation.isPending ||
    confirmDocUploadMutation.isPending ||
    updateTaskConfigurationMutation.isPending;

  const steps = [
    { number: 1, label: 'Task Info', active: currentStep >= 1, description: 'Task Information' },
    { number: 2, label: 'Upload', active: currentStep >= 2, description: 'Upload Documents' },
    { number: 3, label: 'Pipeline', active: currentStep >= 3, description: 'Configure Pipeline' },
  ];

  // Show loading state while fetching task in edit mode
  if (editTaskId && isLoadingTask) {
    return <SetupTaskSkeleton />;
  }

  return (
    <FormProvider {...methods}>
      <div className="flex-1 bg-[#f9fafb] min-h-screen relative">
        <PageHeader
          icon={<FileText className="w-6 h-6" />}
          title={isEditMode ? 'Edit Task' : 'Create New Task'}
          description={`Step ${currentStep}: ${steps[currentStep - 1].description}`}
          actions={
            <button
              type="button"
              onClick={handleBack}
              className="w-9 h-9 flex items-center justify-center rounded-lg border border-[rgba(0,0,0,0.1)] hover:bg-[#f3f4f6] transition-colors"
            >
              <ArrowLeft className="w-4 h-4 text-[#6b7280]" />
            </button>
          }
        />

        {/* Stepper */}
        <TaskFormStepper currentStep={currentStep} steps={steps} />

        {/* Content */}
        <div className="px-8 pt-8">
          <div
            className={`bg-white border border-[rgba(0,0,0,0.1)] rounded-[14px] p-6 mx-auto ${currentStep === 3 ? 'max-w-5xl' : 'max-w-3xl'}`}
          >
            {/* Step Content */}
            {currentStep === 1 && <TaskInfoStep editingDraftId={editingDraftId} />}

            {currentStep === 2 && <DocumentUploadStep editingDraftId={editingDraftId} />}

            {currentStep === 3 && (
              <PipelineConfigStep
                editingDraftId={editingDraftId}
                isCreatePipelineOpen={isCreatePipelineOpen}
                setIsCreatePipelineOpen={setIsCreatePipelineOpen}
              />
            )}

            {/* Action Buttons */}
            <div className="border-t border-[#e5e7eb] pt-6 mt-8 flex items-center justify-between">
              <button
                type="button"
                onClick={handleBack}
                disabled={isLoading}
                className="px-4 py-2 bg-white border border-[rgba(0,0,0,0.1)] rounded-lg text-sm font-medium text-[#111] hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Back
              </button>

              {currentStep === 3 ? (
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={handleSaveDraft}
                    disabled={isLoading}
                    className="px-4 py-2 bg-white border border-[rgba(0,0,0,0.1)] rounded-lg text-sm font-medium text-[#111] hover:bg-gray-50 transition-colors flex items-center gap-2 disabled:opacity-50"
                  >
                    <Save className="w-4 h-4" />
                    Mark as Ready
                  </button>
                  <button
                    type="button"
                    onClick={handleCreateAndProcess}
                    disabled={!canProceed() || isLoading}
                    className={`px-4 py-2 rounded-lg text-sm font-medium text-white transition-colors flex items-center gap-2 ${
                      canProceed() && !isLoading
                        ? 'bg-[#038e43] hover:bg-[#027235]'
                        : 'bg-[#038e43] opacity-50 cursor-not-allowed'
                    }`}
                  >
                    <CheckCircle className="w-4 h-4" />
                    {isLoading
                      ? 'Processing...'
                      : isEditMode
                        ? 'Update And Process Task'
                        : 'Create And Process Task'}
                  </button>
                </div>
              ) : (
                <button
                  type="button"
                  onClick={handleNext}
                  disabled={!canProceed() || isLoading}
                  className={`px-4 py-2 rounded-lg text-sm font-medium text-white transition-colors ${
                    canProceed() && !isLoading
                      ? 'bg-[#038e43] hover:bg-[#027235]'
                      : 'bg-[#038e43] opacity-50 cursor-not-allowed'
                  }`}
                >
                  {isLoading ? 'Processing...' : 'Next Step'}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </FormProvider>
  );
}
