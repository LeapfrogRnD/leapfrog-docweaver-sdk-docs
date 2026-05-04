import { Spinner } from './Spinner';

interface LoaderProps {
  message?: string;
  fullScreen?: boolean;
  overlay?: boolean;
}

export function Loader({
  message = 'Loading...',
  fullScreen = false,
  overlay = true,
}: LoaderProps) {
  const containerClasses = fullScreen
    ? 'fixed inset-0 z-50 flex items-center justify-center'
    : 'absolute inset-0 z-10 flex items-center justify-center';

  const overlayClasses = overlay ? 'bg-black/50 backdrop-blur-sm' : '';

  return (
    <div className={`${containerClasses} ${overlayClasses}`}>
      <div className="bg-white rounded-lg shadow-lg p-6 flex flex-col items-center gap-4 min-w-[200px]">
        <Spinner size="lg" />
        {message && <p className="text-sm font-medium text-[#111] text-center">{message}</p>}
      </div>
    </div>
  );
}
