import { Skeleton } from '@/components/ui';

export function ResultPageSkeleton() {
  return (
    <div className="bg-[#f9fafb] min-h-screen">
      {/* Header skeleton */}
      <div className="bg-white border-b border-[rgba(0,0,0,0.1)] px-4 sm:px-8 pt-6 pb-1">
        <div className="flex items-center justify-between sm:h-14 gap-4">
          <div className="flex items-center gap-3">
            <Skeleton className="w-10 h-10 rounded-[10px]" />
            <div className="space-y-2">
              <Skeleton className="h-5 w-40" />
              <Skeleton className="h-3 w-56" />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Skeleton className="w-9 h-9" />
            <Skeleton className="h-9 w-32" />
            <Skeleton className="h-9 w-28" />
          </div>
        </div>
      </div>

      <div className="p-12 mx-7 space-y-8">
        {/* DocHeaderInfo skeleton */}
        <div className="bg-white rounded-xl border border-[rgba(0,0,0,0.08)] p-6 flex items-center gap-6">
          <Skeleton className="w-14 h-14 rounded-xl flex-shrink-0" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-5 w-48" />
            <Skeleton className="h-3 w-72" />
          </div>
          <div className="flex gap-3">
            <Skeleton variant="text" className="h-6 w-20 rounded-full" />
            <Skeleton variant="text" className="h-6 w-24 rounded-full" />
          </div>
        </div>

        {/* Two-column content skeleton */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Document preview card */}
          <div className="bg-white rounded-xl border border-[rgba(0,0,0,0.08)] overflow-hidden">
            <div className="px-6 py-4 border-b border-[rgba(0,0,0,0.06)]">
              <Skeleton className="h-5 w-36" />
            </div>
            <div className="p-6">
              <Skeleton className="w-full aspect-[3/4] rounded-lg" />
            </div>
          </div>

          {/* Extracted data card */}
          <div className="bg-white rounded-xl border border-[rgba(0,0,0,0.08)] overflow-hidden">
            <div className="px-6 py-4 border-b border-[rgba(0,0,0,0.06)]">
              <Skeleton className="h-5 w-40" />
            </div>
            <div className="p-6 space-y-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="space-y-1.5">
                  <Skeleton variant="text" className="h-3 w-24" />
                  <Skeleton className="h-9 w-full rounded-lg" />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
