import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

interface JobMatchRingProps {
  percentage: number;
  size?: number;
  strokeWidth?: number;
  className?: string;
  animate?: boolean;
  showLabel?: boolean;
}

function getColor(pct: number): string {
  if (pct >= 85) return '#22c8a0'; // teal/success
  if (pct >= 70) return '#3b82f6'; // blue/primary
  return '#f59e0b';                 // amber/warning
}

function getTextClass(pct: number): string {
  if (pct >= 85) return 'fill-emerald-400';
  if (pct >= 70) return 'fill-blue-400';
  return 'fill-amber-400';
}

export const JobMatchRing = ({
  percentage,
  size = 80,
  strokeWidth = 6,
  className,
  animate = true,
  showLabel = true,
}: JobMatchRingProps) => {
  const [displayed, setDisplayed] = useState(animate ? 0 : percentage);

  useEffect(() => {
    if (!animate) { setDisplayed(percentage); return; }
    const id = setTimeout(() => setDisplayed(percentage), 150);
    return () => clearTimeout(id);
  }, [percentage, animate]);

  const cx = size / 2;
  const cy = size / 2;
  const radius = (size - strokeWidth * 2) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference * (1 - displayed / 100);
  const color = getColor(percentage);
  const textClass = getTextClass(percentage);

  return (
    <div
      id={`job-match-ring-${percentage}`}
      className={cn('relative inline-flex items-center justify-center flex-shrink-0', className)}
    >
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        style={{ transform: 'rotate(-90deg)' }}
        aria-label={`${percentage}% match`}
      >
        {/* Track */}
        <circle
          cx={cx}
          cy={cy}
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.08)"
          strokeWidth={strokeWidth}
        />
        {/* Progress arc */}
        <circle
          cx={cx}
          cy={cy}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          style={{
            transition: animate ? 'stroke-dashoffset 1.1s cubic-bezier(0.4,0,0.2,1)' : 'none',
            filter: `drop-shadow(0 0 4px ${color}60)`,
          }}
        />

        {/* Center text — drawn at correct rotation to counteract outer rotate */}
        <text
          x={cx}
          y={cy - (showLabel ? 5 : 0)}
          textAnchor="middle"
          dominantBaseline="middle"
          className={cn('font-bold', textClass)}
          style={{
            transform: `rotate(90deg)`,
            transformOrigin: `${cx}px ${cy}px`,
            fontSize: size <= 60 ? '10px' : size <= 80 ? '13px' : '15px',
            fontFamily: 'Inter, sans-serif',
          }}
        >
          {percentage}%
        </text>
        {showLabel && size > 70 && (
          <text
            x={cx}
            y={cy + 8}
            textAnchor="middle"
            dominantBaseline="middle"
            style={{
              transform: `rotate(90deg)`,
              transformOrigin: `${cx}px ${cy}px`,
              fontSize: '8px',
              fill: '#6b7f94',
              fontFamily: 'Inter, sans-serif',
              fontWeight: 500,
            }}
          >
            match
          </text>
        )}
      </svg>
    </div>
  );
};
