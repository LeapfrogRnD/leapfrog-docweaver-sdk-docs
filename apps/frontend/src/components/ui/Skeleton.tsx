import clsx from 'clsx';

interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
  animation?: 'pulse' | 'wave' | 'none';
}

export function Skeleton({
  className,
  variant = 'rectangular',
  width,
  height,
  animation = 'pulse',
}: SkeletonProps) {
  const baseStyles = 'bg-gray-200';

  const variantStyles = {
    text: 'rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-md',
  };

  const animationStyles = {
    pulse: 'animate-pulse',
    wave: 'animate-shimmer bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 bg-[length:200%_100%]',
    none: '',
  };

  const style: React.CSSProperties = {};
  if (width) style.width = typeof width === 'number' ? `${width}px` : width;
  if (height) style.height = typeof height === 'number' ? `${height}px` : height;

  return (
    <div
      className={clsx(baseStyles, variantStyles[variant], animationStyles[animation], className)}
      style={style}
    />
  );
}

// Table Skeleton for consistent table loading states
interface TableSkeletonProps {
  rows?: number;
  columns?: number;
  showHeader?: boolean;
}

export function TableSkeleton({ rows = 5, columns = 6, showHeader = true }: TableSkeletonProps) {
  return (
    <div className="bg-white border border-[rgba(0,0,0,0.1)] rounded-[14px] overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          {showHeader && (
            <thead className="bg-[#f9fafb] border-b border-[rgba(0,0,0,0.1)]">
              <tr>
                {Array.from({ length: columns }).map((_, i) => (
                  <th key={i} className="px-6 py-3 text-left">
                    <Skeleton className="h-4 w-20" />
                  </th>
                ))}
              </tr>
            </thead>
          )}
          <tbody className="divide-y divide-[rgba(0,0,0,0.1)]">
            {Array.from({ length: rows }).map((_, rowIndex) => (
              <tr key={rowIndex} className="hover:bg-gray-50/50">
                {Array.from({ length: columns }).map((_, colIndex) => (
                  <td key={colIndex} className="px-6 py-4">
                    <Skeleton
                      className="h-4"
                      width={colIndex === 0 ? '80%' : colIndex === columns - 1 ? '60px' : '70%'}
                    />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// Card Skeleton for card view loading states
interface CardSkeletonProps {
  cards?: number;
}

export function CardSkeleton({ cards = 3 }: CardSkeletonProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
      {Array.from({ length: cards }).map((_, index) => (
        <div
          key={index}
          className="bg-white border border-[rgba(0,0,0,0.1)] rounded-[14px] p-6 space-y-4"
        >
          <div className="flex items-start justify-between">
            <div className="flex-1 space-y-3">
              <Skeleton className="h-5 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
            </div>
            <Skeleton variant="circular" width={40} height={40} />
          </div>
          <div className="space-y-2">
            <Skeleton className="h-3 w-full" />
            <Skeleton className="h-3 w-5/6" />
          </div>
          <div className="flex gap-2 pt-2">
            <Skeleton className="h-8 w-20" />
            <Skeleton className="h-8 w-20" />
          </div>
        </div>
      ))}
    </div>
  );
}

// Stats Card Skeleton for dashboard stats
interface StatsSkeletonProps {
  cards?: number;
}

export function StatsSkeleton({ cards = 4 }: StatsSkeletonProps) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {Array.from({ length: cards }).map((_, index) => (
        <div key={index} className="bg-white border border-[rgba(0,0,0,0.1)] rounded-[14px] p-6">
          <div className="flex items-center justify-between mb-4">
            <Skeleton className="h-1 w-24" />
            <Skeleton variant="circular" width={32} height={32} />
          </div>
          <Skeleton className="h-1 w-16 mb-2" />
          <Skeleton className="h-1 w-32" />
        </div>
      ))}
    </div>
  );
}
