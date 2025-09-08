import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StatsCardProps {
  title: string;
  value: string | number;
  change?: {
    value: number;
    trend: 'up' | 'down';
  };
  progress?: number;
  icon?: React.ReactNode;
  description?: string;
  variant?: 'default' | 'success' | 'warning' | 'destructive';
}

export const StatsCard = ({
  title,
  value,
  change,
  progress,
  icon,
  description,
  variant = 'default',
}: StatsCardProps) => {
  const variantStyles = {
    default: 'border-border',
    success: 'border-success/20 bg-success/5',
    warning: 'border-warning/20 bg-warning/5',
    destructive: 'border-destructive/20 bg-destructive/5',
  };

  return (
    <Card className={cn('transition-all duration-200 hover:shadow-md', variantStyles[variant])}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        {icon && (
          <div className={cn(
            'h-8 w-8 rounded-lg flex items-center justify-center',
            variant === 'success' && 'bg-success/10 text-success',
            variant === 'warning' && 'bg-warning/10 text-warning',
            variant === 'destructive' && 'bg-destructive/10 text-destructive',
            variant === 'default' && 'bg-primary/10 text-primary'
          )}>
            {icon}
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        
        {change && (
          <div className="flex items-center space-x-1 mt-1">
            {change.trend === 'up' ? (
              <TrendingUp className="h-4 w-4 text-success" />
            ) : (
              <TrendingDown className="h-4 w-4 text-destructive" />
            )}
            <Badge
              variant="outline"
              className={cn(
                'text-xs',
                change.trend === 'up' ? 'text-success border-success/20' : 'text-destructive border-destructive/20'
              )}
            >
              {change.value > 0 ? '+' : ''}{change.value}%
            </Badge>
          </div>
        )}
        
        {progress !== undefined && (
          <div className="mt-3">
            <Progress value={progress} className="w-full" />
            <p className="text-xs text-muted-foreground mt-1">
              {progress}% complete
            </p>
          </div>
        )}
        
        {description && (
          <p className="text-xs text-muted-foreground mt-2">
            {description}
          </p>
        )}
      </CardContent>
    </Card>
  );
};