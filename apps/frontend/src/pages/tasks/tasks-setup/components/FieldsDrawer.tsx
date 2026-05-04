import { motion, AnimatePresence } from 'framer-motion';
import { X, FileText, Tag } from 'lucide-react';
import { ExtractionFieldsManager } from './ExtractionFieldsManager';
import { ClassificationCategoriesManager } from './ClassificationCategoriesManager';

interface FieldsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  type: 'extraction' | 'classification';
  extractionFields: any[];
  setExtractionFields: (items: any[]) => void;
  classificationCategories: any[];
  setClassificationCategories: (items: any[]) => void;
  handleData: (template: any) => void;
}

export function FieldsDrawer({
  isOpen,
  onClose,
  type,
  extractionFields,
  setExtractionFields,
  classificationCategories,
  setClassificationCategories,
  handleData,
}: FieldsDrawerProps) {
  const title = type === 'extraction' ? 'Extraction Fields' : 'Classification Categories';
  const Icon = type === 'extraction' ? FileText : Tag;
  const count = type === 'extraction' ? extractionFields.length : classificationCategories.length;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/40 backdrop-blur-[2px] z-[98]"
          />

          {/* Drawer */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 h-full w-[520px] bg-white shadow-2xl z-[99] flex flex-col"
          >
            {/* Header */}
            <div className="px-6 py-5 border-b border-[#e5e7eb] bg-[#f9fafb] flex items-center justify-between flex-shrink-0">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 bg-[#dcfce7] rounded-[10px] flex items-center justify-center">
                  <Icon className="w-5 h-5 text-[#038e43]" />
                </div>
                <div>
                  <h3 className="text-base font-semibold text-[#101828]">{title}</h3>
                  <p className="text-xs text-[#6b7280]">
                    {count} {count === 1 ? 'entry' : 'entries'} configured
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={onClose}
                className="p-2 hover:bg-gray-200 rounded-full transition-colors"
              >
                <X className="w-5 h-5 text-[#6b7280]" />
              </button>
            </div>

            {/* Scrollable body — reuse existing managers */}
            <div className="flex-1 overflow-y-auto px-6 py-5">
              {type === 'extraction' ? (
                <ExtractionFieldsManager
                  extractionFields={extractionFields}
                  setExtractionFields={setExtractionFields}
                  handleData={handleData}
                />
              ) : (
                <ClassificationCategoriesManager
                  classificationCategories={classificationCategories}
                  setClassificationCategories={setClassificationCategories}
                  handleData={handleData}
                />
              )}
            </div>

            {/* Footer */}
            <div className="px-6 py-4 border-t border-[#e5e7eb] bg-[#f9fafb] flex-shrink-0">
              <button
                type="button"
                onClick={onClose}
                className="w-full py-2.5 bg-[#038e43] hover:bg-[#027235] text-white text-sm font-semibold rounded-xl transition-colors"
              >
                Done — {count} {count === 1 ? 'entry' : 'entries'} saved
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
