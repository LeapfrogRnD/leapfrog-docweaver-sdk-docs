import { useState } from 'react';
import { useFormContext, useController } from 'react-hook-form';
import { ChevronDown } from 'lucide-react';
import AlertBanner from '@/components/infoStep';

export function AdditionalRequirements() {
  const [isOpen, setIsOpen] = useState(false);
  const { control } = useFormContext();

  const {
    field: { value: enableContext = false, onChange: setEnableContext },
  } = useController({ name: 'enableContext', control, defaultValue: false });

  return (
    <div className="border border-[rgba(0,0,0,0.1)] rounded-[14px] bg-white overflow-hidden">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-3.5 hover:bg-[#f9fafb] transition-colors text-left"
      >
        <span className="text-sm font-medium text-[#101828]">Additional Settings</span>
        <ChevronDown
          className={`w-4 h-4 text-[#6b7280] transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
        />
      </button>

      {isOpen && (
        <div className="px-4 pb-4 space-y-4 border-t border-[#e5e7eb]">
          <label className="flex items-start gap-3 mt-4 cursor-pointer group">
            <div className="relative mt-0.5 flex-shrink-0">
              <input
                type="checkbox"
                checked={!!enableContext}
                onChange={(e) => setEnableContext(e.target.checked)}
                className="sr-only"
              />
              <div
                className={`w-9 h-5 rounded-full transition-colors duration-200 ${
                  enableContext ? 'bg-[#038e43]' : 'bg-[#d1d5db]'
                }`}
              />
              <div
                className={`absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform duration-200 ${
                  enableContext ? 'translate-x-4' : ''
                }`}
              />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-medium text-[#101828]">Enable context processing</span>
              <span className="text-xs text-[#6b7280] mt-0.5">
                Maintain document sequence for higher accuracy.
              </span>
            </div>
          </label>

          <AlertBanner
            title=""
            description={
              <p className="text-xs text-[#374151]">
                Enabling this setting ensures the pipeline processes data in a specific order. This
                may increase processing time for large datasets.
              </p>
            }
            variant="note"
          />
        </div>
      )}
    </div>
  );
}
