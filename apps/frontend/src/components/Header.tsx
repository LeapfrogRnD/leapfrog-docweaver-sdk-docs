import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui';
import { FileText, LogOut } from 'lucide-react';
import { PROJECT_NAME } from '@/constants/project.constants';

export function Header() {
  const { user, logout } = useAuth();

  if (!user) return null;

  return (
    <header className="bg-white/80 backdrop-blur-sm border-b border-primary-ivory shadow-sm sticky top-0 z-40">
      <div className="px-8 py-6 flex items-center justify-between">
        {/* Logo and User Info */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-brand rounded-xl shadow-lg flex items-center justify-center">
            <FileText className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-medium text-primary-black">{PROJECT_NAME}</h1>
            <p className="text-sm text-[#666]">{user.email}</p>
          </div>
        </div>

        {/* Logout Button */}
        <Button variant="secondary" onClick={logout} icon={<LogOut className="w-4 h-4" />}>
          Logout
        </Button>
      </div>
    </header>
  );
}
