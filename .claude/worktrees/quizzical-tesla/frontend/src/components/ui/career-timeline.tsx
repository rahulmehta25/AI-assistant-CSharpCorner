import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Circle, Clock, ChevronDown, ChevronRight, Zap } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

export interface TimelineStep {
  id: string;
  title: string;
  description?: string;
  status: 'completed' | 'active' | 'upcoming';
  date?: string;
  duration?: string;
  tags?: string[];
}

interface CareerTimelineProps {
  steps: TimelineStep[];
  className?: string;
}

const StatusIcon = ({ status }: { status: TimelineStep['status'] }) => {
  if (status === 'completed')
    return <CheckCircle2 className="h-5 w-5 text-emerald-500 flex-shrink-0" />;
  if (status === 'active')
    return (
      <div className="relative flex-shrink-0">
        <div className="h-5 w-5 rounded-full border-2 border-primary flex items-center justify-center">
          <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
        </div>
        <div className="absolute inset-0 rounded-full border-2 border-primary/30 scale-150 animate-ping opacity-30" />
      </div>
    );
  return <Circle className="h-5 w-5 text-muted-foreground/30 flex-shrink-0" />;
};

const TimelineItem = ({
  step,
  index,
  isLast,
}: {
  step: TimelineStep;
  index: number;
  isLast: boolean;
}) => {
  const [expanded, setExpanded] = useState(step.status === 'active');
  const hasDetail = Boolean(step.description || (step.tags && step.tags.length > 0));

  return (
    <motion.div
      id={`timeline-item-${step.id}`}
      initial={{ opacity: 0, x: -16 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.08, duration: 0.4, ease: 'easeOut' as const }}
      className="flex gap-3 relative"
    >
      {/* Left column: icon + connector line */}
      <div className="flex flex-col items-center" style={{ minWidth: 20 }}>
        <div className="z-10 bg-background pt-0.5">
          <StatusIcon status={step.status} />
        </div>
        {!isLast && (
          <div
            className={cn(
              'flex-1 w-px mt-1.5',
              step.status === 'completed'
                ? 'bg-emerald-500/25'
                : step.status === 'active'
                ? 'bg-primary/20'
                : 'bg-border/50'
            )}
            style={{ minHeight: 24 }}
          />
        )}
      </div>

      {/* Right column: content */}
      <div className={cn('flex-1 min-w-0', !isLast && 'pb-5')}>
        <button
          onClick={() => hasDetail && setExpanded(!expanded)}
          className={cn('w-full text-left', !hasDetail && 'cursor-default')}
        >
          <div className="flex items-start justify-between gap-2">
            <h4
              className={cn(
                'font-medium text-sm leading-snug',
                step.status === 'active'
                  ? 'text-primary'
                  : step.status === 'completed'
                  ? 'text-foreground'
                  : 'text-muted-foreground'
              )}
            >
              {step.title}
            </h4>
            <div className="flex items-center gap-2 flex-shrink-0 mt-0.5">
              {step.duration && (
                <span className="text-[11px] text-muted-foreground flex items-center gap-1">
                  <Clock className="h-3 w-3" />
                  {step.duration}
                </span>
              )}
              {hasDetail &&
                (expanded ? (
                  <ChevronDown className="h-3.5 w-3.5 text-muted-foreground/60" />
                ) : (
                  <ChevronRight className="h-3.5 w-3.5 text-muted-foreground/60" />
                ))}
            </div>
          </div>
          {step.date && !expanded && (
            <p className="text-[11px] text-muted-foreground/60 mt-0.5">{step.date}</p>
          )}
        </button>

        <AnimatePresence>
          {expanded && hasDetail && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.25, ease: 'easeInOut' }}
              className="overflow-hidden"
            >
              <div className="pt-1.5 space-y-2">
                {step.date && (
                  <p className="text-[11px] text-muted-foreground/60">{step.date}</p>
                )}
                {step.description && (
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    {step.description}
                  </p>
                )}
                {step.tags && step.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {step.tags.map((tag) => (
                      <Badge key={tag} variant="secondary" className="text-[10px] px-1.5 py-0 h-4">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                )}
                {step.status === 'active' && (
                  <button className="flex items-center gap-1.5 text-xs font-semibold text-primary hover:text-primary-light transition-colors mt-1">
                    <Zap className="h-3 w-3" />
                    Continue now
                  </button>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export const CareerTimeline = ({ steps, className }: CareerTimelineProps) => {
  return (
    <div id="career-timeline" className={cn('space-y-0', className)}>
      {steps.map((step, i) => (
        <TimelineItem
          key={step.id}
          step={step}
          index={i}
          isLast={i === steps.length - 1}
        />
      ))}
    </div>
  );
};
