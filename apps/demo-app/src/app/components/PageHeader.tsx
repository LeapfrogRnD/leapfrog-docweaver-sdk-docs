import { LucideIcon } from "lucide-react";

interface PageHeaderProps {
  icon: LucideIcon;
  title: string;
  description: string;
  actions?: React.ReactNode;
}

export default function PageHeader({
  icon: Icon,
  title,
  description,
  actions,
}: PageHeaderProps) {
  return (
    <div className="bg-zinc-900/60 border-b border-border bg-card">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <Icon className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="font-semibold text-gray-100">{title}</h1>
              <p className="text-sm text-muted-foreground">{description}</p>
            </div>
          </div>
          {actions && <div className="flex items-center gap-2 ">{actions}</div>}
        </div>
      </div>
    </div>
  );
}
