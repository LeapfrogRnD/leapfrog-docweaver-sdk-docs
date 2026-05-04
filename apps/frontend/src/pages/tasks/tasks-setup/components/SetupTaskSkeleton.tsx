import { Skeleton } from '@/components/ui/Skeleton';

export function SetupTaskSkeleton() {
  const stepLabels = ['Task Info', 'Upload', 'Pipeline'];
  return (
    <div className="flex-1 bg-[#f9fafb] min-h-screen">
      {/* Header skeleton */}
      <div className="bg-white border-b border-[#e4e4e7] px-8 py-4">
        <div className="flex items-center h-[52px] gap-3">
          {/* Back button */}
          <Skeleton className="w-9 h-9 rounded-lg" />
          {/* Icon */}
          <Skeleton className="w-10 h-10 rounded-[14px]" />
          <div className="flex flex-col gap-2">
            <Skeleton className="h-6 w-36" />
            <Skeleton className="h-4 w-28" />
          </div>
        </div>
      </div>

      {/* Stepper skeleton */}
      <div className="bg-white border-b border-[#e5e7eb] px-8 py-4">
        <div className="flex items-center justify-between max-w-2xl mx-auto">
          {stepLabels.map((label, index) => (
            <div key={label} className="flex items-center flex-1">
              <div className="flex items-center gap-2">
                <Skeleton className="w-6 h-[22px] rounded-lg" />
                <Skeleton className="h-4 w-16" />
              </div>
              {index < stepLabels.length - 1 && (
                <div className="flex-1 h-[2px] bg-[#e5e7eb] mx-4" />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Content card skeleton */}
      <div className="px-8 pt-8">
        <div className="bg-white border border-[rgba(0,0,0,0.1)] rounded-[14px] p-6 mx-auto max-w-3xl">
          {/* Card title */}
          <div className="mb-6 space-y-2">
            <Skeleton className="h-6 w-1/3" />
            <Skeleton className="h-4 w-1/2" />
          </div>

          {/* Form fields */}
          <div className="space-y-5">
            <div className="space-y-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-10 w-full rounded-lg" />
            </div>
            <div className="space-y-2">
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-24 w-full rounded-lg" />
            </div>
            <div className="space-y-2">
              <Skeleton className="h-4 w-28" />
              <Skeleton className="h-10 w-full rounded-lg" />
            </div>
          </div>

          {/* Action buttons */}
          <div className="border-t border-[#e5e7eb] pt-6 mt-8 flex items-center justify-between">
            <Skeleton className="h-9 w-20 rounded-lg" />
            <Skeleton className="h-9 w-28 rounded-lg" />
          </div>
        </div>
      </div>
    </div>
  );
}
