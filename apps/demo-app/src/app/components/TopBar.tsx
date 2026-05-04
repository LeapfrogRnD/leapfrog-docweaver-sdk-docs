import React from 'react';
import { ArrowLeft, X, FileCode } from 'lucide-react';
import { PROJECTNAME, PROJECT_SUBTITLE } from '../constants/name';
import logo from '@/assets/h-logo.svg';

interface TopBarProps {
  // Basic branding
  title?: string;
  subtitle?: string;
  showLogo?: boolean;
  
  // Navigation
  onBack?: () => void;
  backLabel?: string;
  
  // Actions
  onClose?: () => void;
  actions?: React.ReactNode;
  
  // Styling variants
  variant?: 'light' | 'dark' | 'glass';
  
  // Custom logo/icon
  icon?: React.ReactNode;
  
  // External links (for integration guide)
  externalLinks?: Array<{
    href: string;
    label: string;
    icon?: React.ReactNode;
    external?: boolean;
    onClick?: (e: React.MouseEvent<HTMLAnchorElement>) => void;
  }>;
}

export default function TopBar({
  title = PROJECTNAME,
  subtitle = PROJECT_SUBTITLE,
  showLogo = true,
  onBack,
  backLabel = "Back",
  onClose,
  actions,
  variant = 'light',
  icon,
  externalLinks = []
}: TopBarProps) {
  const isDark = variant === 'dark';
  const isGlass = variant === 'glass';
  
  // Base styles for different variants
  const getContainerStyles = () => {
    if (isDark) {
      return {
        backgroundColor: 'rgba(255,255,255,0.04)',
        borderColor: 'rgba(255,255,255,0.09)',
        boxShadow: '0 2px 16px rgba(0,0,0,0.35)',
      };
    }
    if (isGlass) {
      return {
        backgroundColor: 'rgba(255,255,255,0.85)',
        borderColor: 'rgba(0,0,0,0.08)',
        boxShadow: '0 2px 16px rgba(0,0,0,0.04)',
      };
    }
    return {
      backgroundColor: 'rgb(9, 9, 11)', // zinc-900
      borderColor: 'rgba(255,255,255,0.10)',
    };
  };

  const getTextStyles = () => {
    if (isDark || variant === 'light') {
      return {
        title: isDark ? 'var(--color-primary-white)' : 'rgb(243, 244, 246)', // gray-100
        subtitle: isDark ? 'rgba(148,163,184,0.55)' : 'rgb(156, 163, 175)' // gray-400
      };
    }
    return {
      title: 'var(--color-primary-black)',
      subtitle: '#71717A'
    };
  };

  const textStyles = getTextStyles();
  const containerStyles = getContainerStyles();

  return (
    <div 
      className={`border-b ${isGlass ? '' : 'backdrop-blur-xl'} sticky top-0 z-10`}
      style={{
        ...containerStyles,
        backdropFilter: isGlass ? 'blur(20px)' : 'blur(12px)'
      }}
    >
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Left Side */}
          <div className="flex items-center gap-3">
            {/* Back Button */}
            {onBack && (
              <button
                onClick={onBack}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg transition-all text-sm ${
                  isDark 
                    ? 'text-slate-400/85 hover:text-white hover:bg-white/10' 
                    : variant === 'glass'
                    ? 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    : 'text-gray-400 hover:text-gray-100 hover:bg-gray-800'
                }`}
              >
                <ArrowLeft className="w-4 h-4" />
                {backLabel}
              </button>
            )}
            
            {/* Logo + Title Section */}
            <div className="flex items-center gap-3">
              {/* Logo/Icon */}
              {showLogo && (
                <div >
                  {icon || (
                    <img 
                      src={logo} 
                      alt={title}
                      className="w-40 auto object-contain"
                      style={{ cursor: "pointer" }}
                      onClick={() => {
                        window.history.pushState({}, "", "/");
                        window.dispatchEvent(new PopStateEvent("popstate"));
                      }}
                    />
                  )}
                </div>
              )}
              
              {/* Title and Subtitle */}
              {/* <div>
                <h1 
                  className="text-lg font-semibold"
                  style={{ color: textStyles.title }}
                >
                  {title}
                </h1>
                <p 
                  className="text-sm"
                  style={{ color: textStyles.subtitle }}
                >
                  {subtitle}
                </p>
              </div> */}
            </div>
          </div>

          {/* Right Side */}
          <div className="flex items-center gap-1">
            {/* Nav Links */}
            {externalLinks.map((link, index) => (
              <a 
                key={index}
                href={link.href}
                target={link.external ? "_blank" : undefined}
                rel={link.external ? "noopener noreferrer" : undefined}
                onClick={link.onClick}
                className={`flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-lg transition-all duration-200 ease-in-out no-underline ${
                  isDark 
                    ? 'text-slate-400 hover:text-white hover:bg-white/[0.07]'
                    : variant === 'glass'
                    ? 'text-gray-500 hover:text-gray-900 hover:bg-gray-100/70'
                    : 'text-gray-400 hover:text-gray-100 hover:bg-gray-800'
                }`}
              >
                {link.icon}
                {link.label}
              </a>
            ))}
            
            {/* Custom Actions */}
            {actions && (
              <>
                {externalLinks.length > 0 && (
                  <span className={`w-px h-4 mx-2 ${isDark ? 'bg-white/10' : variant === 'glass' ? 'bg-gray-200' : 'bg-gray-700'}`} />
                )}
                {actions}
              </>
            )}
            
            {/* Close Button */}
            {onClose && (
              <button 
                onClick={onClose}
                className={`flex items-center gap-2 text-sm px-3 py-1.5 rounded-lg border transition-all duration-200 ease-in-out ${
                  isDark 
                    ? 'text-slate-400/85 bg-white/5 border-white/10 hover:bg-white/10 hover:text-white'
                    : variant === 'glass'
                    ? 'text-gray-600 bg-white/50 border-gray-200 hover:bg-white hover:text-gray-900'
                    : 'text-gray-400 bg-gray-800 border-gray-700 hover:bg-gray-700 hover:text-gray-100'
                }`}
                aria-label="Close"
                title="Close (Esc)"
              >
                <X className="w-3 h-3" />
                Close
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}