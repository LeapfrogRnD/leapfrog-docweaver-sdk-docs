import { NavLink, useLocation } from 'react-router-dom';
import { Settings, Key, LogOut, UserCog, Users, ListTodo, ChevronDown } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { RoleRank, Roles } from '@/types/types';
import { LucideIcon } from 'lucide-react';
import logo from '@/assets/h-logo.svg';
import { useState } from 'react';

interface SidebarMenuItem {
  to: string;
  icon: LucideIcon;
  label: string;
  roles?: Roles[];
}

export function Sidebar() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const isSetupPage = location.pathname === '/setup-user';
  const [profileOpen, setProfileOpen] = useState(false);

  const setupItems: SidebarMenuItem[] = [
    {
      to: '/setup-user',
      icon: UserCog,
      label: 'Setup User',
    },
  ];

  const sidebarItems: SidebarMenuItem[] = [
    // {
    //   to: '/dashboard',
    //   icon: LayoutDashboard,
    //   label: 'Dashboard',
    // },
    {
      to: '/tasks',
      icon: ListTodo,
      label: 'Task Management',
    },
    {
      to: '/pipelines',
      icon: Settings,
      label: 'Pipeline Settings',
    },
    {
      to: '/api-keys',
      icon: Key,
      label: 'API Keys',
      roles: [Roles.Admin, Roles.Superadmin],
    },
    {
      to: '/users',
      icon: Users,
      label: 'Users',
      roles: [Roles.Admin, Roles.Superadmin],
    },
  ];

  // Use setup items if on setup page, otherwise use regular sidebar items
  const itemsToDisplay = isSetupPage ? setupItems : sidebarItems;

  const filteredItems = itemsToDisplay.filter((item) => {
    if (!item.roles || item.roles.length === 0) return true;
    if (!user?.role) return false;
    const userRank = RoleRank[user.role as Roles];
    const minItemRank = Math.min(...item.roles.map((r) => RoleRank[r]));
    return userRank >= minItemRank;
  });

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-[#09090b] border-r border-[#333] flex flex-col z-30">
      {/* Logo Section */}
      <div className="border-b border-[#333] px-6 py-[18px]">
        <img src={logo} alt="Logo" className="w-[80%] h-auto ml-2" />
      </div>
      {/* Navigation */}
      <nav className="flex-1 px-4 py-4 space-y-1">
        {filteredItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-200 ${
                  isActive ? 'bg-primary-brand text-white' : 'text-white hover:bg-[#333]'
                }`
              }
            >
              <Icon className="w-5 h-5" />
              <span className="text-sm">{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Profile Section */}
      <div className="border-t border-[#333] px-4 py-4 relative">
        {/* Collapsed trigger */}
        <button
          onClick={() => setProfileOpen((prev) => !prev)}
          className="flex items-center justify-between w-full px-3 py-2 rounded-lg hover:bg-[#333] transition-colors"
        >
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-8 h-8 bg-primary-brand rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-sm font-semibold text-white">
                {user?.first_name?.charAt(0).toUpperCase() ||
                  user?.email?.charAt(0).toUpperCase() ||
                  'U'}
              </span>
            </div>
            <span className="text-sm text-white font-medium truncate">
              {user?.first_name && user?.last_name
                ? `${user.first_name} ${user.last_name}`
                : user?.first_name || user?.email || 'User'}
            </span>
          </div>
          <ChevronDown
            className={`w-4 h-4 text-[#9ca3af] flex-shrink-0 transition-transform duration-200 ${profileOpen ? 'rotate-180' : ''}`}
          />
        </button>

        {/* Floating popup panel — anchored above trigger, outside sidebar flow */}
        {profileOpen && (
          <>
            {/* Backdrop to close on outside click */}
            <div className="fixed inset-0 z-10" onClick={() => setProfileOpen(false)} />
            <div className="absolute bottom-2 left-full w-64 z-20 bg-[#1a1a1d] border border-[#333] rounded-xl shadow-2xl overflow-hidden">
              {/* User detail card */}
              <div className="px-4 py-3 border-b border-[#333]">
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 bg-primary-brand rounded-full flex items-center justify-center flex-shrink-0">
                    <span className="text-sm font-semibold text-white">
                      {user?.first_name?.charAt(0).toUpperCase() ||
                        user?.email?.charAt(0).toUpperCase() ||
                        'U'}
                    </span>
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm text-white font-medium truncate">
                      {user?.first_name && user?.last_name
                        ? `${user.first_name} ${user.last_name}`
                        : user?.first_name || user?.email || 'User'}
                    </p>
                    <p className="text-xs text-[#9ca3af] truncate">{user?.email || ''}</p>
                  </div>
                </div>
                {user?.role && (
                  <span className="inline-block mt-2 text-[10px] font-medium px-2 py-0.5 rounded-full bg-primary-brand/20 text-primary-brand uppercase tracking-wide">
                    {user.role}
                  </span>
                )}
              </div>

              <button
                onClick={logout}
                className="flex items-center gap-2 w-full px-4 py-3 text-white hover:bg-[#333] transition-colors"
              >
                <LogOut className="w-4 h-4 text-[#9ca3af]" />
                <span className="text-sm">Log out</span>
              </button>
            </div>
          </>
        )}
      </div>
    </aside>
  );
}
