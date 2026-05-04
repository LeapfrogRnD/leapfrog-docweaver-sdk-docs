interface Step {
  number: number;
  label: string;
  active: boolean;
  description: string;
}

interface TaskFormStepperProps {
  currentStep: number;
  steps: Step[];
}

export function TaskFormStepper({ steps }: TaskFormStepperProps) {
  return (
    <div className="bg-white border-b border-[#e5e7eb] px-8 py-4">
      <div className="flex items-center justify-between max-w-2xl mx-auto">
        {steps.map((step, index) => (
          <div key={step.number} className="flex items-center flex-1">
            <div className="flex items-center gap-2">
              <div
                className={`w-[24px] h-[22px] rounded-lg flex items-center justify-center text-xs font-medium ${
                  step.active ? 'bg-[#038e43] text-white' : 'bg-[#e5e7eb] text-[#4a5565]'
                }`}
              >
                {step.number}
              </div>
              <span
                className={`text-sm font-medium tracking-[-0.1504px] ${
                  step.active ? 'text-[#038e43]' : 'text-[#4a5565]'
                }`}
              >
                {step.label}
              </span>
            </div>
            {index < steps.length - 1 && <div className="flex-1 h-[2px] bg-[#e5e7eb] mx-4" />}
          </div>
        ))}
      </div>
    </div>
  );
}
