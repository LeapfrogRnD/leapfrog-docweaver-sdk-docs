import { motion, AnimatePresence } from 'framer-motion';
import { X, Plus } from 'lucide-react';

interface Template {
  id: string | number;
  label: string;
  data: any;
}

interface TemplateSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  templates: Template[];
  onSelect: (template: Template) => void;
  title?: string;
  subtitle?: string;
}

export function TemplateSidebar({
  isOpen,
  onClose,
  templates,
  onSelect,
  title = 'JSON Templates',
  subtitle = 'Preview and inject sample structures',
}: TemplateSidebarProps) {
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
            className="fixed inset-0 bg-black/40 backdrop-blur-[2px] z-[99]"
          />

          {/* Slide-out Panel */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 h-full w-[450px] bg-white shadow-2xl z-[100] flex flex-col"
          >
            {/* Header */}
            <div className="p-6 border-b flex justify-between items-center bg-[#f9fafb]">
              <div>
                <h3 className="text-lg font-bold text-[#101828]">{title}</h3>
                <p className="text-xs text-[#6b7280]">{subtitle}</p>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-gray-200 rounded-full transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Template List */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {templates.map((tpl) => (
                <div
                  key={tpl.id}
                  className="group border border-[#e5e7eb] rounded-xl overflow-hidden bg-white shadow-sm hover:border-[#038e43] transition-all"
                >
                  <div className="px-4 py-3 bg-[#f9fafb] border-b flex justify-between items-center">
                    <span className="text-sm font-semibold text-[#101828]">{tpl.label}</span>
                    <button
                      onClick={() => onSelect(tpl)}
                      className="flex items-center gap-1.5 text-xs font-bold bg-[#038e43] text-white px-3 py-1.5 rounded-lg hover:shadow-lg active:scale-95 transition-all"
                    >
                      <Plus className="w-3 h-3" /> Add to List
                    </button>
                  </div>

                  {/* JSON Preview Area */}
                  <div className="p-4 bg-[#1e1e1e] relative">
                    <div className="absolute top-2 right-2 text-[10px] text-gray-500 font-mono uppercase">
                      JSON Preview
                    </div>
                    <pre className="text-[11px] leading-relaxed font-mono text-green-400 overflow-x-auto custom-scrollbar">
                      {JSON.stringify(tpl.data, null, 2)}
                    </pre>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
