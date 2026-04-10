import { cn } from '@/lib/utils';

interface SkeletonProps {
  className?: string;
}

export const Skeleton = ({ className }: SkeletonProps) => (
  <div
    className={cn(
      'rounded-md bg-muted animate-shimmer',
      className
    )}
    aria-hidden="true"
  />
);

export const SkeletonCard = ({
  lines = 3,
  className,
}: {
  lines?: number;
  className?: string;
}) => (
  <div
    id="skeleton-card"
    className={cn('p-4 rounded-xl border border-border/50 space-y-3', className)}
  >
    <Skeleton className="h-4 w-2/3" />
    <Skeleton className="h-3 w-full" />
    {Array.from({ length: Math.max(0, lines - 2) }).map((_, i) => (
      <Skeleton
        key={i}
        className={cn('h-3', i === lines - 3 ? 'w-1/2' : 'w-full')}
      />
    ))}
  </div>
);

export const SkeletonStats = ({ count = 4 }: { count?: number }) => (
  <div id="skeleton-stats" className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
    {Array.from({ length: count }).map((_, i) => (
      <div key={i} className="p-4 rounded-xl border border-border/50 space-y-3">
        <div className="flex items-center justify-between">
          <Skeleton className="h-3 w-24" />
          <Skeleton className="h-8 w-8 rounded-lg" />
        </div>
        <Skeleton className="h-8 w-16" />
        <Skeleton className="h-1.5 w-full rounded-full" />
        <Skeleton className="h-3 w-32" />
      </div>
    ))}
  </div>
);

export const SkeletonJobCard = () => (
  <div id="skeleton-job-card" className="p-4 rounded-xl border border-border/50 space-y-3">
    <div className="flex items-start justify-between">
      <div className="space-y-2 flex-1">
        <Skeleton className="h-4 w-48" />
        <Skeleton className="h-3 w-32" />
      </div>
      <Skeleton className="h-10 w-10 rounded-full flex-shrink-0 ml-4" />
    </div>
    <Skeleton className="h-3 w-full" />
    <Skeleton className="h-3 w-3/4" />
    <div className="flex gap-2">
      <Skeleton className="h-5 w-16 rounded-full" />
      <Skeleton className="h-5 w-20 rounded-full" />
      <Skeleton className="h-5 w-24 rounded-full" />
    </div>
  </div>
);

export const SkeletonList = ({ count = 3 }: { count?: number }) => (
  <div id="skeleton-list" className="space-y-3">
    {Array.from({ length: count }).map((_, i) => (
      <div key={i} className="flex items-center gap-3 p-3 rounded-lg border border-border/50">
        <Skeleton className="h-8 w-8 rounded-lg flex-shrink-0" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-3 w-40" />
          <Skeleton className="h-2.5 w-28" />
        </div>
        <Skeleton className="h-6 w-12 rounded-full" />
      </div>
    ))}
  </div>
);
