import { ReactNode } from 'react';

interface PageHeaderProps {
  /** Icon element rendered inside the brand-tinted icon box */
  icon: ReactNode;
  /** Main page title */
  title: string;
  /** Short descriptive subtitle shown beneath the title */
  description: string;
  /** Optional action buttons / controls rendered on the right side */
  actions?: ReactNode;
}

/**
 * Global header bar used at the top of every authenticated (sidebar-layout) page.
 *
 * Renders a white bar with a brand icon, title, description and an optional
 * right-hand actions slot (buttons, filters, etc.).
 */
export function PageHeader({ icon, title, description, actions }: PageHeaderProps) {
  return (
    <div className="bg-white border-b border-[rgba(0,0,0,0.1)] px-4 sm:px-8 pt-6 pb-1">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 sm:h-14">
        {/* Icon + title */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-[rgba(3,142,67,0.1)] rounded-[10px] flex items-center justify-center flex-shrink-0">
            <span className="text-[#038e43]">{icon}</span>
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-semibold text-[#111] tracking-[0.0703px]">
              {title}
            </h1>
            <p className="text-xs sm:text-sm text-[#6b7280]">{description}</p>
          </div>
        </div>

        {/* Right-side actions */}
        {actions && <div className="flex items-center gap-2 flex-shrink-0">{actions}</div>}
      </div>
    </div>
  );
}
