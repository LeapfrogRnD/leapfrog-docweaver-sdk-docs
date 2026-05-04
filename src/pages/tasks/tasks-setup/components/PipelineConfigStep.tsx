import { useMemo, useState } from 'react';
import { useFormContext, useController, useWatch } from 'react-hook-form';
import { FileText, Plus, Tag, AlignLeft, Settings2, ChevronRight, Lightbulb } from 'lucide-react';

import { useGetPipelines } from '@/queries/pipeline.query';
import { TaskCreationFlowFormData } from '@/schemas/task.schema';
import promptData from '@/../data/user_instruction_templates.json';
import { PipelineModal } from '@/pages/pipelines/components/PipelineModal';
import { SelectionCard } from '@/components/SelectionComponent';
import { TextArea } from '@/components/ui/TextArea';
import { AdditionalRequirements } from './AdditionalRequirements';
import AlertBanner from '@/components/infoStep';
import { FieldsDrawer } from './FieldsDrawer';

export function PipelineConfigStep({
  editingDraftId,
  isCreatePipelineOpen,
  setIsCreatePipelineOpen,
}: any) {
  const { control, register, setValue, getValues } = useFormContext<TaskCreationFlowFormData>();
  const [isFieldsDrawerOpen, setIsFieldsDrawerOpen] = useState(false);

  const taskType = useWatch({ control, name: 'taskType' });
  const additionalInstruction = useWatch({ control, name: 'additionalInstruction' });
  const pipelineId = useWatch({ control, name: 'pipelineId' });

  const {
    field: { value: extractionFields = [], onChange: setExtractionFields },
  } = useController({ name: 'extractionFields', control, defaultValue: [] });

  const {
    field: { value: classificationCategories = [], onChange: setClassificationCategories },
  } = useController({ name: 'classificationCategories', control, defaultValue: [] });

  const filteredTemplates = useMemo(() => {
    return promptData.filter((item: any) => item.type === 'global' || item.type === taskType);
  }, [taskType]);

  const { data: pipelinesData, isLoading: isPipelinesLoading } = useGetPipelines(1, 50, 'active');
  const availablePipelines = useMemo(() => {
    const list = pipelinesData?.data || [];
    return [...list.filter((p: any) => p.is_default), ...list.filter((p: any) => !p.is_default)];
  }, [pipelinesData]);

  const handleTaskTypeSelect = (type: 'extraction' | 'classification' | 'summarization') => {
    setValue('taskType', type);
    if (type !== 'extraction') setExtractionFields([]);
    if (type !== 'classification') setClassificationCategories([]);
  };

  const handleToggleInstruction = (instruction: string) => {
    const currentVal = getValues('additionalInstruction')?.trim() || '';
    const isPresent = currentVal.includes(instruction);
    if (isPresent) {
      const updatedValue = currentVal
        .replace(new RegExp(`(\\n?- )?${instruction}`, 'g'), '')
        .trim();
      setValue('additionalInstruction', updatedValue);
    } else {
      const updatedValue = currentVal ? `${currentVal}\n- ${instruction}` : instruction;
      setValue('additionalInstruction', updatedValue);
    }
  };

  const handleAddFromJson = (template: any) => {
    if (template.type === 'extraction') {
      if (taskType !== 'extraction') {
        setValue('taskType', 'extraction');
      }
      setExtractionFields([...template.data]);
    } else if (template.type === 'classification') {
      if (taskType !== 'classification') {
        setValue('taskType', 'classification');
      }
      setClassificationCategories([...template.data]);
    }
  };

  return (
    <div className="w-full px-8 py-6">
      <div className="space-y-8">
        {editingDraftId && (
          <AlertBanner
            title="Editing Draft"
            variant="info"
            description="Modify pipeline settings and fields below."
          />
        )}

        <div className="flex justify-between items-end">
          <div>
            <h2 className="text-xl font-semibold text-[#101828]">Configure Pipeline</h2>
            <p className="text-sm text-[#4a5565]">Choose how documents should be processed</p>
          </div>
        </div>

        {/* Two-column layout: Pipeline sidebar + Main content */}
        <div className="flex gap-0 items-start">
          {/* Left: Pipeline Selection */}
          <div className="w-72 flex-shrink-0 space-y-3 sticky top-0 pr-6 border-r border-[#e5e7eb]">
            <label className="block text-sm font-medium text-[#111]">
              Select Pipeline Type <span className="text-red-500">*</span>
            </label>
            <p className="text-sm text-[#4a5565]">
              Choose a pre-configured pipeline or create your own.
            </p>
            <div className="flex flex-col gap-2 max-h-[calc(100vh-280px)] overflow-y-auto pr-1">
              <button
                type="button"
                onClick={() => setIsCreatePipelineOpen(true)}
                className="w-full text-left px-3 py-2.5 rounded-[10px] border-2 border-dashed border-[rgba(0,0,0,0.15)] bg-white hover:border-[#038e43] transition-all flex items-center gap-2 text-[#6b7280] hover:text-[#038e43]"
              >
                <div
                  className={`w-9 h-9 rounded-[10px] flex items-center justify-center flex-shrink-0 bg-[#f3f4f6] text-[#6b7280]`}
                >
                  <Plus className="w-3.5 h-3.5 flex-shrink-0" />
                </div>
                <div>
                  <span className="text-sm font-medium mt-2 block ml-1">Create New</span>
                  <p className="text-xs text-[#6b7280] truncate ml-1 mt-0.5">
                    Define a custom pipeline
                  </p>
                </div>
              </button>
              {isPipelinesLoading
                ? Array.from({ length: 4 }).map((_, i) => (
                    <div
                      key={i}
                      className="flex items-center gap-3 p-3 rounded-[10px] border border-[rgba(0,0,0,0.08)] animate-pulse"
                    >
                      <div className="w-9 h-9 rounded-[10px] bg-[#f3f4f6] flex-shrink-0" />
                      <div className="flex-1 space-y-2">
                        <div className="h-3 bg-[#f3f4f6] rounded w-3/4" />
                        <div className="h-2.5 bg-[#f3f4f6] rounded w-1/2" />
                      </div>
                    </div>
                  ))
                : availablePipelines.map((pipeline: any) => (
                    <SelectionCard
                      icon={FileText}
                      key={pipeline.id}
                      title={pipeline.name}
                      description={pipeline.description}
                      isActive={pipelineId === pipeline.id}
                      onClick={() => setValue('pipelineId', pipeline.id)}
                      badge={
                        pipeline.is_default ? (
                          <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-[#dcfce7] text-[#038e43]">
                            Default
                          </span>
                        ) : undefined
                      }
                    />
                  ))}
            </div>
          </div>

          {/* Right: Main content */}
          <div className="flex-1 min-w-0 space-y-8 pl-8">
            {/* Task Type Selection */}
            <div className="space-y-3">
              <label className="block text-sm font-medium text-[#111]">
                Selct Task Type <span className="text-red-500">*</span>
              </label>
              <div className="grid grid-cols-3 gap-3">
                <SelectionCard
                  variant="vertical"
                  title="Extraction"
                  description="Get fields"
                  icon={FileText}
                  isActive={taskType === 'extraction'}
                  onClick={() => handleTaskTypeSelect('extraction')}
                />
                <SelectionCard
                  variant="vertical"
                  title="Classification"
                  description="Categorize"
                  icon={Tag}
                  isActive={taskType === 'classification'}
                  onClick={() => handleTaskTypeSelect('classification')}
                />
                <SelectionCard
                  variant="vertical"
                  title="Summarize"
                  description="Overview"
                  icon={AlignLeft}
                  isActive={taskType === 'summarization'}
                  onClick={() => handleTaskTypeSelect('summarization')}
                />
              </div>
            </div>

            {/* Additional Instructions */}
            <div className="space-y-3">
              <label className="block text-sm font-medium text-[#111]">
                Additional Instruction Set
              </label>
              <TextArea
                {...register('additionalInstruction')}
                placeholder="Enter Additional instruction for model"
                rows={4}
                variant="secondary"
              />
              <div className="flex flex-wrap gap-2">
                {filteredTemplates.map((item: any) => {
                  const isActive = additionalInstruction?.includes(item.text);
                  return (
                    <button
                      key={item.label}
                      type="button"
                      onClick={() => handleToggleInstruction(item.text)}
                      className={`px-3 py-1 text-[11px] font-semibold rounded-full border transition-all ${isActive ? 'bg-[#038e43] border-[#038e43] text-white' : 'bg-white border-[#e5e7eb] text-[#374151]'}`}
                    >
                      {isActive ? '×' : '+'} {item.label}
                    </button>
                  );
                })}
              </div>
            </div>

            <AdditionalRequirements />

            {/* Fields drawer trigger — shown for extraction & classification */}
            {(taskType === 'extraction' || taskType === 'classification') && (
              <button
                type="button"
                onClick={() => setIsFieldsDrawerOpen(true)}
                className={`w-full flex items-center justify-between p-4 rounded-[14px] transition-all border group ${
                  (taskType === 'extraction' ? extractionFields : classificationCategories).length >
                  0
                    ? 'bg-white border-[#038e43]'
                    : 'bg-white border-[rgba(0,0,0,0.1)] hover:border-[#038e43]'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-9 h-9 rounded-[10px] flex items-center justify-center flex-shrink-0 ${
                      (taskType === 'extraction' ? extractionFields : classificationCategories)
                        .length > 0
                        ? 'bg-[#dcfce7] text-[#038e43]'
                        : 'bg-[#f3f4f6] text-[#6b7280]'
                    }`}
                  >
                    {taskType === 'extraction' ? (
                      <FileText className="w-4 h-4" />
                    ) : (
                      <Tag className="w-4 h-4" />
                    )}
                  </div>
                  <div className="text-left">
                    <p
                      className={`text-sm font-medium tracking-[-0.4395px] ${
                        (taskType === 'extraction' ? extractionFields : classificationCategories)
                          .length > 0
                          ? 'text-[#038e43]'
                          : 'text-[#101828]'
                      }`}
                    >
                      {taskType === 'extraction' ? (
                        <p>
                          Extraction Fields <span className="text-red-500">*</span>
                        </p>
                      ) : (
                        <p>
                          Classification Fields <span className="text-red-500">*</span>
                        </p>
                      )}
                    </p>
                    <p className="text-xs text-[#6b7280] mt-0.5">
                      {taskType === 'extraction'
                        ? extractionFields.length > 0
                          ? `${extractionFields.length} field${extractionFields.length !== 1 ? 's' : ''} configured`
                          : 'No fields added yet — click to configure'
                        : classificationCategories.length > 0
                          ? `${classificationCategories.length} categor${classificationCategories.length !== 1 ? 'ies' : 'y'} configured`
                          : 'No categories added yet — click to configure'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="flex items-center gap-1 text-xs text-[#6b7280] font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                    <Settings2 className="w-3.5 h-3.5" />
                    Configure
                  </div>
                  <ChevronRight className="w-4 h-4 text-[#9ca3af] group-hover:text-[#038e43] transition-colors" />
                </div>
              </button>
            )}

            <AlertBanner
              variant="note"
              icon={<Lightbulb className="w-4 h-4" />}
              title="Pipeline Processing"
              description={
                <p className="text-[#6b7280]">
                  The selected pipeline will automatically process your documents and extract
                  relevant information. Processing time varies based on document size and
                  complexity.
                </p>
              }
            />
          </div>
        </div>
      </div>

      <PipelineModal
        isOpen={isCreatePipelineOpen}
        onClose={() => setIsCreatePipelineOpen(false)}
        pipeline={null}
      />

      {(taskType === 'extraction' || taskType === 'classification') && (
        <FieldsDrawer
          isOpen={isFieldsDrawerOpen}
          onClose={() => setIsFieldsDrawerOpen(false)}
          type={taskType}
          extractionFields={extractionFields}
          setExtractionFields={setExtractionFields}
          classificationCategories={classificationCategories}
          setClassificationCategories={setClassificationCategories}
          handleData={handleAddFromJson}
        />
      )}
    </div>
  );
}
