import { useFormContext } from 'react-hook-form';
import { TaskCreationFlowFormData } from '@/schemas/task.schema';
import AlertBanner from '@/components/infoStep';
import { WatchedInput } from '@/components/ui/WatchedInput';

interface TaskInfoStepProps {
  editingDraftId: string | null;
}

export function TaskInfoStep({ editingDraftId }: TaskInfoStepProps) {
  const {
    control, // Use control instead of register for WatchedInput
  } = useFormContext<TaskCreationFlowFormData>();

  return (
    <div className="space-y-6">
      {editingDraftId && (
        <AlertBanner
          variant="info"
          title="Editing Draft"
          description="Changes will be saved when you click Save for later"
        />
      )}

      <div className="space-y-4">
        <div className="space-y-1.5">
          <h2 className="text-lg font-semibold text-gray-900">Task Information</h2>
        </div>

        {/* We replace the manual label, input, and error logic with WatchedInput.
            The internal useWatch will handle the red border and "Required" 
            warning automatically based on the 'required' prop.
        */}
        <div className="ml-1">
          <WatchedInput
            control={control}
            name="taskName"
            label="Task Name"
            placeholder="e.g., Q1 2026 Invoice Processing"
            required={true}
          />
        </div>
      </div>

      <AlertBanner
        variant="guidance"
        title="Quick Tip"
        description={`Use descriptive names like "Monthly Expense Reports - Jan 2026" or "Customer Contract Review" to easily track your tasks.`}
      />
    </div>
  );
}
