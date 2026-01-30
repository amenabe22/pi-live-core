import { cn } from '@/lib/utils';

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'card' | 'table' | 'text' | 'circle';
}

export function Skeleton({ className, variant = 'default', ...props }: SkeletonProps) {
  const baseClasses = 'animate-pulse bg-muted';
  
  const variantClasses = {
    default: 'rounded-md',
    card: 'rounded-lg h-32',
    table: 'rounded h-12',
    text: 'rounded h-4',
    circle: 'rounded-full',
  };

  return (
    <div
      className={cn(baseClasses, variantClasses[variant], className)}
      {...props}
    />
  );
}

export function SkeletonCard() {
  return (
    <div className="rounded-lg border bg-card p-6 space-y-4">
      <Skeleton variant="text" className="h-6 w-1/3" />
      <Skeleton variant="text" className="h-4 w-full" />
      <Skeleton variant="text" className="h-4 w-2/3" />
    </div>
  );
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4">
          <Skeleton variant="table" className="flex-1" />
          <Skeleton variant="table" className="w-24" />
          <Skeleton variant="table" className="w-32" />
        </div>
      ))}
    </div>
  );
}
