import { motion } from 'framer-motion';
import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';

export interface SkillData {
  subject: string;
  score: number;
  fullMark?: number;
}

interface SkillRadarChartProps {
  data: SkillData[];
  title?: string;
  height?: number;
}

const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: any[] }) => {
  if (active && payload && payload.length > 0) {
    const item = payload[0];
    return (
      <div
        id="radar-tooltip"
        className="bg-popover border border-border/60 rounded-lg px-3 py-2 shadow-lg text-sm"
      >
        <p className="font-semibold text-foreground">{item.payload.subject}</p>
        <p className="text-primary font-bold">{item.value}%</p>
      </div>
    );
  }
  return null;
};

const CustomDot = (props: any) => {
  const { cx, cy, value } = props;
  if (!cx || !cy) return null;
  return (
    <g>
      <circle cx={cx} cy={cy} r={5} fill="#3b82f6" stroke="#0c0f17" strokeWidth={2} />
      {value >= 80 && (
        <circle cx={cx} cy={cy} r={8} fill="none" stroke="#3b82f6" strokeWidth={1} opacity={0.4} />
      )}
    </g>
  );
};

export const SkillRadarChart = ({ data, title, height = 280 }: SkillRadarChartProps) => {
  return (
    <motion.div
      id="skill-radar-chart"
      initial={{ opacity: 0, scale: 0.92 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className="w-full"
    >
      {title && (
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">
          {title}
        </p>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <RadarChart data={data} margin={{ top: 10, right: 30, bottom: 10, left: 30 }}>
          <PolarGrid
            stroke="rgba(255,255,255,0.07)"
            strokeDasharray="3 3"
          />
          <PolarAngleAxis
            dataKey="subject"
            tick={{
              fill: '#6b7f94',
              fontSize: 11,
              fontWeight: 500,
              fontFamily: 'Inter, sans-serif',
            }}
          />
          <PolarRadiusAxis
            angle={30}
            domain={[0, 100]}
            tick={false}
            axisLine={false}
          />
          <Radar
            name="Skills"
            dataKey="score"
            stroke="#3b82f6"
            fill="#3b82f6"
            fillOpacity={0.15}
            strokeWidth={2}
            dot={<CustomDot />}
            animationBegin={200}
            animationDuration={1200}
            animationEasing="ease-out"
          />
          <Tooltip content={<CustomTooltip />} />
        </RadarChart>
      </ResponsiveContainer>
    </motion.div>
  );
};
