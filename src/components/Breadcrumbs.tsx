import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

export function Breadcrumbs() {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter((x) => x);

  const getBreadcrumbName = (path: string) => {
    const nameMap: Record<string, string> = {
      upload: 'Upload Files',
      pipelines: 'Pipeline Configuration',
      results: 'Results',
      login: 'Login',
    };
    return nameMap[path] || path.charAt(0).toUpperCase() + path.slice(1);
  };

  if (pathnames.length === 0 || location.pathname === '/login') {
    return null;
  }

  return (
    <nav className="flex items-center gap-2 text-sm mb-6">
      <Link
        to="/"
        className="flex items-center gap-1 text-[#666] hover:text-primary-brand transition-colors"
      >
        <Home className="w-4 h-4" />
        <span>Home</span>
      </Link>

      {pathnames.map((path, index) => {
        const routeTo = `/${pathnames.slice(0, index + 1).join('/')}`;
        const isLast = index === pathnames.length - 1;

        return (
          <div key={path} className="flex items-center gap-2">
            <ChevronRight className="w-4 h-4 text-[#999]" />
            {isLast ? (
              <span className="text-primary-black font-medium">{getBreadcrumbName(path)}</span>
            ) : (
              <Link to={routeTo} className="text-[#666] hover:text-primary-brand transition-colors">
                {getBreadcrumbName(path)}
              </Link>
            )}
          </div>
        );
      })}
    </nav>
  );
}
