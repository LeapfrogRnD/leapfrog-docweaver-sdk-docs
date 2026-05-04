import clsx from 'clsx';

interface SwitchProps {
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
  label?: string;
  disabled?: boolean;
}

export function Switch({ checked, onCheckedChange, label, disabled = false }: SwitchProps) {
  const handleToggle = () => {
    if (!disabled) {
      onCheckedChange(!checked);
    }
  };

  return (
    <div className="flex items-center justify-between w-full">
      {label && <label className="text-sm font-medium text-primary-black">{label}</label>}

      <button
        type="button"
        role="switch"
        aria-checked={checked}
        disabled={disabled}
        onClick={handleToggle}
        className={clsx(
          'relative inline-flex h-[18px] w-8 rounded-full transition-all duration-200 shadow-sm',
          checked ? 'bg-primary-brand' : 'bg-gray-300',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      >
        <span
          className={clsx(
            'inline-block h-4 w-4 rounded-full bg-white transition-transform duration-200 shadow',
            checked ? 'translate-x-[15px]' : 'translate-x-[1px]',
            'translate-y-[1px]'
          )}
        />
      </button>
    </div>
  );
}
