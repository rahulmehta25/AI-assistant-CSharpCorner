/**
 * StatsCard.tsx
 * Reusable metric card for dashboard stats grid.
 *
 * Usage:
 *   <StatsCard
 *     title="Career Match"
 *     value="85%"
 *     progress={85}
 *     change={{ value: 5, trend: 'up' }}
 *     icon={<Target className="h-4 w-4" />}
 *     variant="success"
 *     description="Based on your skills and interests"
 *   />
 */

import { ReactNode } from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

interface StatsCardChange {
  value: number;
  trend: 'up' | 'down' | 'neutral';
}

interface StatsCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: ReactNode;
  progress?: number;
  change?: StatsCardChange;
  variant?: 'default' | 'success' | 'warning' | 'destructive';
  className?: string;
}

const variantStyles: Record<NonNullable<StatsCardProps['variant']>, string> = {
  default:     'text-primary',
  success:     'text-emerald-500',
  warning:     'text-amber-500',
  destructive: 'text-destructive',
};

const progressVariantStyles: Record<NonNullable<StatsCardProps['variant']>, string> = {
  default:     '[&>div]:bg-primary',
  success:     '[&>div]:bg-emerald-500',
  warning:     '[&>div]:bg-amber-500',
  destructive: '[&>div]:bg-destructive',
};

export function StatsCard({
  title,
  value,
  description,
  icon,
  progress,
  change,
  variant = 'default',
  className,
}: StatsCardProps) {
  const colorClass = variantStyles[variant];
  const progressColor = progressVariantStyles[variant];

  return (
    <Card
      id={`stats-card-${title.toLowerCase().replace(/\s+/g, '-')}`}
      className={cn('border-border/50', className)}
    >
      <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        {icon && (
          <div className={cn('opacity-70', colorClass)}>
            {icon}
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="flex items-end justify-between gap-2 mb-1">
          <div
            id={`stats-card-value-${title.toLowerCase().replace(/\s+/g, '-')}`}
            className={cn('text-2xl font-bold tabular-nums', colorClass)}
          >
            {value}
          </div>
          {change && (
            <ChangeIndicator change={change} />
          )}
        </div>

        {progress !== undefined && (
          <Progress
            id={`stats-card-progress-${title.toLowerCase().replace(/\s+/g, '-')}`}
            value={progress}
            className={cn('h-1.5 mt-2 bg-muted', progressColor)}
            aria-label={`${title} progress`}
            aria-valuenow={progress}
            aria-valuemin={0}
            aria-valuemax={100}
          />
        )}

        {description && (
          <p
            id={`stats-card-desc-${title.toLowerCase().replace(/\s+/g, '-')}`}
            className="text-xs text-muted-foreground mt-2"
          >
            {description}
          </p>
        )}
      </CardContent>
    </Card>
  );
}

function ChangeIndicator({ change }: { change: StatsCardChange }) {
  const { value, trend } = change;
  const isUp = trend === 'up';
  const isDown = trend === 'down';

  return (
    <span
      className={cn(
        'flex items-center gap-0.5 text-xs font-medium',
        isUp && 'text-emerald-500',
        isDown && 'text-destructive',
        !isUp && !isDown && 'text-muted-foreground'
      )}
    >
      {isUp && <TrendingUp className="h-3 w-3" />}
      {isDown && <TrendingDown className="h-3 w-3" />}
      {!isUp && !isDown && <Minus className="h-3 w-3" />}
      {value > 0 ? '+' : ''}{value}
    </span>
  );
}
