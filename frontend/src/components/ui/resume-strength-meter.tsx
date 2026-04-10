import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface ResumeStrengthMeterProps {
  score: number; // 0–100
  className?: string;
  compact?: boolean;
}

type Config = {
  label: string;
  gradientClass: string;
  textColor: string;
  description: string;
  segments: number;
};

function getConfig(score: number): Config {
  if (score >= 85)
    return {
      label: 'Excellent',
      gradientClass: 'from-emerald-500 to-teal-400',
      textColor: 'text-emerald-400',
      description: 'Your profile is highly competitive',
      segments: 5,
    };
  if (score >= 70)
    return {
      label: 'Strong',
      gradientClass: 'from-blue-500 to-cyan-400',
      textColor: 'text-blue-400',
      description: 'Great foundation — minor improvements possible',
      segments: 4,
    };
  if (score >= 50)
    return {
      label: 'Fair',
      gradientClass: 'from-amber-500 to-yellow-400',
      textColor: 'text-amber-400',
      description: 'Some key improvements recommended',
      segments: 3,
    };
  return {
    label: 'Needs Work',
    gradientClass: 'from-red-500 to-orange-400',
    textColor: 'text-red-400',
    description: 'Significant updates will boost your match rate',
    segments: 2,
  };
}

export const ResumeStrengthMeter = ({
  score,
  className,
  compact = false,
}: ResumeStrengthMeterProps) => {
  const cfg = getConfig(score);

  return (
    <div id="resume-strength-meter" className={cn('space-y-2', className)}>
      {!compact && (
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-muted-foreground">Resume Strength</span>
          <div className="flex items-center gap-2">
            <span className={cn('text-sm font-bold', cfg.textColor)}>{cfg.label}</span>
            <span className="text-xs text-muted-foreground font-mono">{score}/100</span>
          </div>
        </div>
      )}

      {/* Segmented bar — 5 blocks */}
      <div id="strength-bar-container" className="flex gap-1">
        {Array.from({ length: 5 }).map((_, i) => {
          const filled = (i + 1) * 20 <= score;
          const partial = !filled && i * 20 < score;
          const partialWidth = partial ? ((score - i * 20) / 20) * 100 : 0;

          return (
            <div
              key={i}
              id={`strength-segment-${i}`}
              className="relative flex-1 h-2 rounded-full bg-muted overflow-hidden"
            >
              {(filled || partial) && (
                <motion.div
                  className={cn('absolute inset-y-0 left-0 rounded-full bg-gradient-to-r', cfg.gradientClass)}
                  initial={{ width: 0 }}
                  animate={{ width: filled ? '100%' : `${partialWidth}%` }}
                  transition={{
                    duration: 0.8,
                    delay: i * 0.08,
                    ease: 'easeOut' as const,
                  }}
                />
              )}
            </div>
          );
        })}
      </div>

      {!compact && (
        <p className="text-xs text-muted-foreground">{cfg.description}</p>
      )}

      {compact && (
        <div className="flex items-center justify-between">
          <span className={cn('text-xs font-semibold', cfg.textColor)}>{cfg.label}</span>
          <span className="text-xs text-muted-foreground">{score}/100</span>
        </div>
      )}
    </div>
  );
};
