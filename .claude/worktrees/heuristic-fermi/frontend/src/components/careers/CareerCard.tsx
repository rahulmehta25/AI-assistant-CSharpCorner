/**
 * CareerCard.tsx
 * Displays a Career entry, used in Dashboard (compact) and CareerExplorer (full).
 *
 * Usage:
 *   <CareerCard career={career} compact showMatch />
 *   <CareerCard career={career} />
 */

import { Link } from 'react-router-dom';
import { TrendingUp, ArrowRight, Zap } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import type { Career } from '@/types';

interface CareerCardProps {
  career: Career;
  /** Render a slim single-row variant for the dashboard preview list */
  compact?: boolean;
  /** Show the numeric match badge */
  showMatch?: boolean;
  className?: string;
}

const demandColors: Record<Career['demandLevel'], string> = {
  high:   'border-emerald-500/30 text-emerald-500',
  medium: 'border-amber-500/30 text-amber-500',
  low:    'border-rose-500/30 text-rose-500',
};

const matchColor = (score: number) => {
  if (score >= 90) return 'border-emerald-500/30 text-emerald-500';
  if (score >= 75) return 'border-blue-500/30 text-blue-400';
  return 'border-border text-muted-foreground';
};

export function CareerCard({ career, compact = false, showMatch = false, className }: CareerCardProps) {
  const score = career.match ?? career.matchScore;
  const salary = career.salaryRange ?? (
    career.salary
      ? `$${Math.round(career.salary.min / 1000)}k – $${Math.round(career.salary.max / 1000)}k`
      : undefined
  );

  if (compact) {
    return (
      <Link
        to={`/careers/${career.id}`}
        id={`career-card-compact-${career.id}`}
        aria-label={`View ${career.title} career${score !== undefined ? `, ${score}% match` : ''}`}
        className={cn(
          'flex items-center gap-3 p-3 rounded-lg border border-border/50',
          'hover:bg-muted/30 hover:border-primary/20 transition-colors duration-150',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
          className
        )}
      >
        {/* Icon placeholder */}
        <div className="flex-shrink-0 h-9 w-9 rounded-lg bg-primary/10 flex items-center justify-center">
          <Zap className="h-4 w-4 text-primary" />
        </div>

        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium truncate">{career.title}</p>
          <p className="text-xs text-muted-foreground truncate">{career.category}</p>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          {showMatch && score !== undefined && (
            <Badge
              variant="outline"
              className={cn('text-xs', matchColor(score))}
            >
              {score}%
            </Badge>
          )}
          <ArrowRight className="h-3.5 w-3.5 text-muted-foreground" />
        </div>
      </Link>
    );
  }

  return (
    <Card
      id={`career-card-${career.id}`}
      className={cn('border-border/50 hover:border-primary/30 transition-colors duration-150', className)}
    >
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-center gap-3">
            <div className="flex-shrink-0 h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <Zap className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h3 className="font-semibold text-base leading-tight">{career.title}</h3>
              <p className="text-xs text-muted-foreground mt-0.5">{career.category}</p>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-shrink-0">
            <Badge
              variant="outline"
              className={cn('text-xs capitalize', demandColors[career.demandLevel])}
            >
              {career.demandLevel} demand
            </Badge>
            {showMatch && score !== undefined && (
              <Badge
                variant="outline"
                className={cn('text-xs', matchColor(score))}
              >
                {score}% match
              </Badge>
            )}
          </div>
        </div>

        <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
          {career.description}
        </p>

        <div className="flex items-center justify-between text-xs text-muted-foreground mb-4">
          {salary && (
            <span className="font-medium text-foreground">{salary}</span>
          )}
          <span className="flex items-center gap-1">
            <TrendingUp className="h-3 w-3 text-emerald-500" />
            {career.growthRate} growth
          </span>
          {career.timeToTransition && (
            <span>{career.timeToTransition} to transition</span>
          )}
        </div>

        {career.skills.length > 0 && (
          <div
            id={`career-skills-${career.id}`}
            className="flex flex-wrap gap-1 mb-4"
          >
            {career.skills.slice(0, 4).map((skill) => (
              <Badge
                key={skill}
                variant="secondary"
                className="text-xs px-2 py-0.5"
              >
                {skill}
              </Badge>
            ))}
            {career.skills.length > 4 && (
              <Badge variant="secondary" className="text-xs px-2 py-0.5 text-muted-foreground">
                +{career.skills.length - 4}
              </Badge>
            )}
          </div>
        )}

        <Button
          id={`career-cta-${career.id}`}
          variant="outline"
          size="sm"
          className="w-full border-border/60 hover:border-primary/40 hover:bg-primary/5"
          asChild
        >
          <Link to={`/careers/${career.id}`}>
            View Details
            <ArrowRight className="ml-2 h-3.5 w-3.5" />
          </Link>
        </Button>
      </CardContent>
    </Card>
  );
}
