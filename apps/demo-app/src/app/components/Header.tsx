import React from 'react';
import { FileText, LogOut, Settings, ArrowLeft } from 'lucide-react';
import { Button } from './ui/button';
import { PROJECTNAME } from '../constants/name';

// Minimal user shape used by the header (types.ts doesn't export a User type)
interface User {
  email: string;
}

interface HeaderProps {
  // For TaskList page
  user?: User;
  onLogout?: () => void;
  onManagePipelines?: () => void;
  
  // For other pages (CreateTask, TaskDetail, PipelineManagement)
  onBack?: () => void;
  title?: string;
  subtitle?: string;
  icon?: React.ReactNode;
  actions?: React.ReactNode;
  step?: 'info' | 'upload' | 'pipeline'; // For CreateTask progress
}

export default function Header({
  user,
  onLogout,
  onManagePipelines,
  onBack,
  title,
  subtitle,
  icon,
  actions,
  step
}: HeaderProps) {
  // Generate subtitle based on step for CreateTask
  const getStepSubtitle = () => {
    if (step === 'info') return 'Step 1: Task Information';
    if (step === 'upload') return 'Step 2: Upload Documents';
    if (step === 'pipeline') return 'Step 3: Configure Pipeline';
    return subtitle;
  };

  return (
    <header className="bg-white border-b border-[#e4e4e7]">
      <div className="max-w-7xl mx-auto px-8 py-4">
        <div className="flex items-center justify-between">
          {/* Left Side */}
          <div className="flex items-center gap-3">
            {/* Back Button for sub-pages */}
            {onBack && (
              <Button variant="ghost" size="icon" onClick={onBack}>
                <ArrowLeft className="w-5 h-5" />
              </Button>
            )}
            
            {/* Logo + Title Section */}
            <div className="flex items-center gap-3">
              {/* Icon/Logo */}
              <div className="w-10 h-10 bg-[#038E43] rounded-xl flex items-center justify-center shadow-md">
                {icon || <FileText className="w-6 h-6 text-white" />}
              </div>
              
              {/* Title and Subtitle */}
              <div>
                <h1 className="text-2xl font-medium text-[#111]">
                  {title || `${PROJECTNAME} - OCR System`}
                </h1>
                <p className="text-sm text-[#666]">
                  {step ? getStepSubtitle() : (subtitle || (user ? user.email : ''))}
                </p>
              </div>
            </div>
          </div>

          {/* Right Side */}
          <div className="flex items-center gap-2">
            {/* Custom Actions (for sub-pages) */}
            {actions}
            
            {/* Main Page Actions (TaskList) */}
            {onManagePipelines && (
              <button
                onClick={onManagePipelines}
                className="flex items-center gap-2 px-4 py-2 bg-white border border-[#e4e4e7] rounded-lg shadow-sm hover:bg-gray-50 transition-colors-smooth"
              >
                <Settings className="w-4 h-4" />
                <span className="text-sm font-medium text-[#09090b]">Pipeline settings</span>
              </button>
            )}
            
            {onLogout && (
              <button
                onClick={onLogout}
                className="flex items-center justify-center p-2 bg-[#007e40] rounded-lg shadow-sm hover:bg-[#006633] transition-colors-smooth"
                title="Logout"
              >
                <LogOut className="w-[18px] h-[18px] text-white" />
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}