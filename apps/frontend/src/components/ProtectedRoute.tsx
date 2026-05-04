import { ReactNode } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { Roles } from '@/types/types';

interface ProtectedRouteProps {
  children: ReactNode;
  allowedRoles?: Roles[];
  layout?: 'sidebar' | 'header';
}

export function ProtectedRoute({
  children,
  allowedRoles,
  layout = 'sidebar',
}: ProtectedRouteProps) {
  const { isAuthenticated, user, isProfileSetup, isProfileVerified } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Check if profile setup is complete
  if (!isProfileVerified) {
    return <Navigate to="/setup-user" replace />;
  }

  if (!isProfileSetup) {
    return <Navigate to="/complete-profile" replace />;
  }

  // Check role-based access if allowedRoles is specified
  if (allowedRoles && allowedRoles.length > 0) {
    const userRole = user?.role as Roles;
    if (!userRole || !allowedRoles.includes(userRole)) {
      return <Navigate to="/tasks" replace />;
    }
  }

  // Render with sidebar layout (main app pages)
  if (layout === 'sidebar') {
    return (
      <div className="flex min-h-screen bg-white">
        <Sidebar />
        <main className="flex-1 ml-64 overflow-auto">{children}</main>
      </div>
    );
  }

  // Render with header layout (alternative pages)
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#f0fdf4]/20 via-[#fafafa] to-[#f0fdf4]/10">
      <Header />
      <main>{children}</main>
    </div>
  );
}

// Semi-protected route for setup pages (only requires authentication, not verification)
interface SemiProtectedRouteProps {
  children: ReactNode;
  requireVerification?: boolean;
}

export function SemiProtectedRoute({
  children,
  requireVerification = false,
}: SemiProtectedRouteProps) {
  const { isAuthenticated, isProfileSetup, isProfileVerified } = useAuth();

  // Always require authentication
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // If verification is required and user is verified, redirect to complete profile or tasks
  if (requireVerification && isProfileVerified) {
    if (!isProfileSetup) {
      return <Navigate to="/complete-profile" replace />;
    }
    return <Navigate to="/tasks" replace />;
  }

  // If this is complete-profile page and user is already setup, redirect to tasks
  if (!requireVerification && isProfileSetup) {
    return <Navigate to="/tasks" replace />;
  }

  // Render without sidebar (setup pages have their own layout)
  return <>{children}</>;
}
