import { Skeleton } from './skeleton';
import { Card, CardContent, CardHeader } from './card';

export function CardSkeleton() {
  return (
    <Card>
      <CardHeader className="pb-3">
        <Skeleton className="h-5 w-32" />
        <Skeleton className="h-4 w-48 mt-1" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-20 w-full" />
      </CardContent>
    </Card>
  );
}

export function StatsCardSkeleton() {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-2">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-4 w-4 rounded" />
        </div>
        <Skeleton className="h-8 w-16 mb-2" />
        <Skeleton className="h-2 w-full" />
      </CardContent>
    </Card>
  );
}

export function JobCardSkeleton() {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-start justify-between mb-3">
          <div className="space-y-2 flex-1">
            <Skeleton className="h-5 w-40" />
            <Skeleton className="h-4 w-24" />
          </div>
          <Skeleton className="h-6 w-16 rounded-full" />
        </div>
        <div className="flex items-center gap-4 mb-4">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-4 w-20" />
        </div>
        <Skeleton className="h-4 w-full mb-2" />
        <Skeleton className="h-4 w-3/4" />
        <div className="flex items-center gap-2 mt-4">
          <Skeleton className="h-8 w-20" />
          <Skeleton className="h-8 w-8" />
        </div>
      </CardContent>
    </Card>
  );
}

export function CareerCardSkeleton() {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-start justify-between mb-3">
          <Skeleton className="h-5 w-40" />
          <Skeleton className="h-6 w-16 rounded-full" />
        </div>
        <Skeleton className="h-4 w-full mb-2" />
        <Skeleton className="h-4 w-2/3 mb-4" />
        <div className="flex items-center gap-4">
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-4 w-24" />
        </div>
      </CardContent>
    </Card>
  );
}

export function ChatMessageSkeleton() {
  return (
    <div className="flex gap-3">
      <Skeleton className="h-8 w-8 rounded-full flex-shrink-0" />
      <div className="flex-1 space-y-2">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-4 w-1/2" />
      </div>
    </div>
  );
}

export function ResumePreviewSkeleton() {
  return (
    <div className="space-y-6 p-6">
      <div className="space-y-2">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-4 w-40" />
      </div>
      <div className="space-y-3">
        <Skeleton className="h-5 w-24" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
      </div>
      <div className="space-y-3">
        <Skeleton className="h-5 w-28" />
        <div className="space-y-4">
          <div className="space-y-2">
            <Skeleton className="h-4 w-40" />
            <Skeleton className="h-3 w-24" />
            <Skeleton className="h-3 w-full" />
            <Skeleton className="h-3 w-full" />
          </div>
          <div className="space-y-2">
            <Skeleton className="h-4 w-36" />
            <Skeleton className="h-3 w-20" />
            <Skeleton className="h-3 w-full" />
          </div>
        </div>
      </div>
    </div>
  );
}

export function RoadmapSkeleton() {
  return (
    <div className="space-y-6">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="flex gap-4">
          <div className="flex flex-col items-center">
            <Skeleton className="h-10 w-10 rounded-full" />
            {i < 4 && <Skeleton className="h-20 w-0.5 mt-2" />}
          </div>
          <div className="flex-1 pb-8">
            <Skeleton className="h-5 w-32 mb-2" />
            <Skeleton className="h-4 w-48 mb-3" />
            <div className="space-y-2">
              <Skeleton className="h-3 w-full" />
              <Skeleton className="h-3 w-3/4" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export function TableSkeleton({ rows = 5, cols = 4 }: { rows?: number; cols?: number }) {
  return (
    <div className="space-y-3">
      <div className="flex gap-4">
        {Array.from({ length: cols }).map((_, i) => (
          <Skeleton key={i} className="h-4 flex-1" />
        ))}
      </div>
      {Array.from({ length: rows }).map((_, rowIdx) => (
        <div key={rowIdx} className="flex gap-4">
          {Array.from({ length: cols }).map((_, colIdx) => (
            <Skeleton key={colIdx} className="h-8 flex-1" />
          ))}
        </div>
      ))}
    </div>
  );
}

export function PageHeaderSkeleton() {
  return (
    <div className="space-y-2">
      <Skeleton className="h-8 w-48" />
      <Skeleton className="h-4 w-64" />
    </div>
  );
}

export function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <PageHeaderSkeleton />
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <StatsCardSkeleton key={i} />
        ))}
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        <CardSkeleton />
        <CardSkeleton />
      </div>
    </div>
  );
}
