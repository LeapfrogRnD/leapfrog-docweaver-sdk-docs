import { Routes, Route, Navigate } from 'react-router-dom';
import { LoginPage } from '@/pages/login/LoginPage';
import { PasswordResetPage } from '@/pages/password-reset/PasswordResetPage';
import { PasswordUpdatePage } from '@/pages/password-reset/PasswordUpdatePage';
import UsersListPage from '@/pages/users/UsersListPage';
import { ProtectedRoute, SemiProtectedRoute } from '@/components/ProtectedRoute';
import { Roles } from '@/types/types';
import { SetupPage } from '@/pages/setup-user/SetupUser';
import { CompleteProfilePage } from '@/pages/setup-user/CompleteProfile';
import { SetupTaskPage } from '@/pages/tasks/tasks-setup/SetupTaskPage';
import TaskDetailPage from '@/pages/tasks/tasks-detail/TaskDetailPage';
import { ResultsPage } from '@/pages/tasks/tasks-results/ResultsPage';
import { PipelineConfigPage } from '@/pages/pipelines/PipelineConfig';
import { ApiKeysPage } from '@/pages/api-keys/api-keys-list/ApiKeysPage';
import { TaskListPage } from '@/pages/tasks/task-list/TaskListPage';
import { ApiKeysIntegrationPage } from '@/pages/api-keys/api-keys-integrations/ApiKeyIntegrationPage';

const publicRoutes = [
  { path: '/login', element: <LoginPage /> },
  { path: '/password-reset', element: <PasswordResetPage /> },
  { path: '/reset-password', element: <PasswordUpdatePage /> },
];

const semiProtectedRoutes = [
  { path: '/setup-user', element: <SetupPage />, requireVerification: true },
  { path: '/complete-profile', element: <CompleteProfilePage />, requireVerification: false },
];

const protectedRoutes = [
  { path: '/tasks', element: <TaskListPage /> },
  { path: '/tasks/create', element: <SetupTaskPage /> },
  { path: '/tasks/:taskId/edit', element: <SetupTaskPage /> },
  { path: '/tasks/:taskId', element: <TaskDetailPage /> },
  { path: '/tasks/:taskId/result', element: <ResultsPage /> },

  { path: '/pipelines', element: <PipelineConfigPage /> },
  { path: '/api-keys', element: <ApiKeysPage />, allowedRoles: [Roles.Admin, Roles.Superadmin] },
  {
    path: '/api-keys/:keyId/integrations',
    element: <ApiKeysIntegrationPage />,
    allowedRoles: [Roles.Admin, Roles.Superadmin],
  },

  { path: '/users', element: <UsersListPage />, allowedRoles: [Roles.Admin, Roles.Superadmin] },
];

export const AppRoutes = () => {
  return (
    <Routes>
      {/* Public Routes */}
      {publicRoutes.map(({ path, element }) => (
        <Route key={path} path={path} element={element} />
      ))}

      {/* Semi-Protected Routes (setup pages - require auth but not full verification) */}
      {semiProtectedRoutes.map(({ path, element, requireVerification }) => (
        <Route
          key={path}
          path={path}
          element={
            <SemiProtectedRoute requireVerification={requireVerification}>
              {element}
            </SemiProtectedRoute>
          }
        />
      ))}

      {/* Protected Routes */}
      {protectedRoutes.map(({ path, element, allowedRoles }) => (
        <Route
          key={path}
          path={path}
          element={<ProtectedRoute allowedRoles={allowedRoles}>{element}</ProtectedRoute>}
        />
      ))}

      {/* Redirects */}
      <Route path="/" element={<Navigate to="/tasks" replace />} />
      <Route path="*" element={<Navigate to="/tasks" replace />} />
    </Routes>
  );
};
