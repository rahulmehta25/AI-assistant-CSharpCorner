import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  GraduationCap, BookOpen, Code, Star, Briefcase,
  Target, TrendingUp, ArrowRight, ChevronRight,
} from 'lucide-react';
import { CareerTimeline, type TimelineStep } from '@/components/ui/career-timeline';
import { ResumeStrengthMeter } from '@/components/ui/resume-strength-meter';

/* ── Types ───────────────────────────────────────────────── */
type StepType = 'course' | 'project' | 'certification' | 'job';
type StepStatus = 'completed' | 'active' | 'upcoming';

interface PathwayStep {
  id: string;
  title: string;
  description: string;
  type: StepType;
  duration: string;
  status: StepStatus;
  resources?: string[];
}

interface Pathway {
  id: string;
  title: string;
  subtitle: string;
  level: string;
  duration: string;
  progress: number;
  outcome: string;
  salary: string;
  skills: string[];
  steps: PathwayStep[];
  color: string;
  icon: typeof GraduationCap;
}

/* ── Data ────────────────────────────────────────────────── */
const pathways: Pathway[] = [
  {
    id: 'frontend',
    title: 'Frontend Developer',
    subtitle: 'From beginner to job-ready',
    level: 'Beginner → Mid',
    duration: '12 months',
    progress: 42,
    outcome: 'Land a frontend role at a tech company',
    salary: '$85k – $115k',
    skills: ['HTML/CSS', 'JavaScript', 'React', 'TypeScript', 'Testing', 'Git'],
    color: 'from-blue-500 to-cyan-500',
    icon: Code,
    steps: [
      {
        id: 'f1', title: 'HTML & CSS Fundamentals', type: 'course', duration: '4 weeks', status: 'completed',
        description: 'Build the visual foundation. Learn semantic HTML, Flexbox, CSS Grid, and responsive design.',
        resources: ['freeCodeCamp', 'The Odin Project'],
      },
      {
        id: 'f2', title: 'JavaScript Essentials', type: 'course', duration: '6 weeks', status: 'completed',
        description: 'DOM manipulation, events, async/await, fetch API, and ES6+ features.',
        resources: ['javascript.info', 'Eloquent JS'],
      },
      {
        id: 'f3', title: 'Build 3 Portfolio Projects', type: 'project', duration: '4 weeks', status: 'active',
        description: 'Apply skills: to-do app, weather dashboard, and an API-driven web app.',
        resources: ['GitHub', 'Netlify', 'Vercel'],
      },
      {
        id: 'f4', title: 'React & TypeScript', type: 'course', duration: '8 weeks', status: 'upcoming',
        description: 'React hooks, context, React Query, and strict TypeScript.',
        resources: ['React docs', 'Frontend Masters'],
      },
      {
        id: 'f5', title: 'Testing & Quality', type: 'course', duration: '2 weeks', status: 'upcoming',
        description: 'Unit and integration tests with Vitest and React Testing Library.',
      },
      {
        id: 'f6', title: 'Job Search Sprint', type: 'job', duration: '4–12 weeks', status: 'upcoming',
        description: 'Apply to 30+ roles, prep for technical interviews, land your first offer.',
      },
    ],
  },
  {
    id: 'fullstack',
    title: 'Full Stack Engineer',
    subtitle: 'Master frontend and backend',
    level: 'Mid → Senior',
    duration: '18 months',
    progress: 20,
    outcome: 'Full-stack engineer at a growth-stage company',
    salary: '$110k – $150k',
    skills: ['React', 'Node.js', 'Databases', 'APIs', 'Docker', 'AWS'],
    color: 'from-violet-500 to-purple-500',
    icon: TrendingUp,
    steps: [
      {
        id: 'fs1', title: 'Node.js & Express APIs', type: 'course', duration: '6 weeks', status: 'completed',
        description: 'RESTful APIs with Express, middleware, authentication, error handling.',
      },
      {
        id: 'fs2', title: 'Database Design (SQL + NoSQL)', type: 'course', duration: '4 weeks', status: 'active',
        description: 'PostgreSQL for relational data, MongoDB for documents. Schema design and ORMs.',
      },
      {
        id: 'fs3', title: 'Build a Full-Stack SaaS App', type: 'project', duration: '8 weeks', status: 'upcoming',
        description: 'End-to-end project: React frontend, Node API, PostgreSQL, auth, deployment.',
      },
      {
        id: 'fs4', title: 'Docker & Deployment', type: 'course', duration: '3 weeks', status: 'upcoming',
        description: 'Containerize apps, CI/CD pipelines, deploy to AWS/Render.',
      },
      {
        id: 'fs5', title: 'AWS Developer Associate', type: 'certification', duration: '6 weeks', status: 'upcoming',
        description: 'Official AWS certification to validate cloud skills.',
      },
    ],
  },
  {
    id: 'datascience',
    title: 'Data Scientist',
    subtitle: 'From Python basics to ML in prod',
    level: 'Beginner → Senior',
    duration: '24 months',
    progress: 8,
    outcome: 'Data Scientist at a top analytics team',
    salary: '$120k – $180k',
    skills: ['Python', 'Statistics', 'ML', 'SQL', 'Visualization', 'Deep Learning'],
    color: 'from-emerald-500 to-teal-500',
    icon: Star,
    steps: [
      {
        id: 'ds1', title: 'Python for Data Science', type: 'course', duration: '6 weeks', status: 'active',
        description: 'NumPy, Pandas, Matplotlib — the core data science toolkit.',
      },
      {
        id: 'ds2', title: 'Statistics & Probability', type: 'course', duration: '8 weeks', status: 'upcoming',
        description: 'Hypothesis testing, distributions, regression, Bayesian reasoning.',
      },
      {
        id: 'ds3', title: 'Machine Learning (Scikit-learn)', type: 'course', duration: '10 weeks', status: 'upcoming',
        description: 'Classification, regression, clustering, model evaluation, feature engineering.',
      },
      {
        id: 'ds4', title: 'Kaggle Competition (top 20%)', type: 'project', duration: '4 weeks', status: 'upcoming',
        description: 'Apply skills in a real ML competition to build portfolio credibility.',
      },
    ],
  },
];

const stepTypeConfig: Record<StepType, { icon: typeof BookOpen; color: string; bg: string }> = {
  course:        { icon: BookOpen,  color: 'text-blue-400',   bg: 'bg-blue-500/10'   },
  project:       { icon: Code,      color: 'text-violet-400', bg: 'bg-violet-500/10' },
  certification: { icon: Star,      color: 'text-amber-400',  bg: 'bg-amber-500/10'  },
  job:           { icon: Briefcase, color: 'text-emerald-400',bg: 'bg-emerald-500/10'},
};

/* ── Convert steps to CareerTimeline format ──────────────── */
function toTimelineSteps(steps: PathwayStep[]): TimelineStep[] {
  return steps.map((s) => ({
    id: s.id,
    title: s.title,
    description: s.description,
    status: s.status,
    duration: s.duration,
    tags: s.resources,
  }));
}

/* ── Pathway selector card ───────────────────────────────── */
const PathwayCard = ({
  pathway,
  selected,
  onSelect,
}: {
  pathway: Pathway;
  selected: boolean;
  onSelect: () => void;
}) => {
  const Icon = pathway.icon;
  return (
    <button
      id={`pathway-btn-${pathway.id}`}
      onClick={onSelect}
      className={`w-full text-left p-4 rounded-xl border transition-all duration-200 group ${
        selected
          ? 'border-primary/50 bg-primary/8'
          : 'border-border/40 hover:border-primary/30 hover:bg-muted/30'
      }`}
    >
      <div className="flex items-start gap-3">
        <div className={`h-9 w-9 rounded-xl bg-gradient-to-br ${pathway.color} flex items-center justify-center flex-shrink-0 shadow-sm`}>
          <Icon className="h-4 w-4 text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-0.5">
            <h3 className="font-semibold text-sm text-foreground truncate">{pathway.title}</h3>
            <span className="text-xs font-bold text-primary ml-2 flex-shrink-0">{pathway.progress}%</span>
          </div>
          <p className="text-[11px] text-muted-foreground">{pathway.level} · {pathway.duration}</p>
          <Progress value={pathway.progress} className="h-1 mt-2" />
        </div>
      </div>
    </button>
  );
};

/* ── Main page ───────────────────────────────────────────── */
export default function Pathways() {
  const [selectedId, setSelectedId] = useState('frontend');
  const selected = pathways.find((p) => p.id === selectedId)!;

  const timelineSteps = toTimelineSteps(selected.steps);
  const completedCount = selected.steps.filter((s) => s.status === 'completed').length;

  return (
    <div id="pathways-container" className="max-w-6xl space-y-6">
      {/* ── Header ──────────────────────────────────────── */}
      <motion.div
        id="pathways-header"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center gap-3"
      >
        <div className="h-11 w-11 rounded-2xl bg-gradient-primary flex items-center justify-center shadow-glow">
          <GraduationCap className="h-5 w-5 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight text-gradient-primary">
            Career Pathways
          </h1>
          <p className="text-sm text-muted-foreground">
            Structured roadmaps from where you are to where you want to be
          </p>
        </div>
      </motion.div>

      {/* ── Body ──────────────────────────────────────────── */}
      <div id="pathways-body" className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Left: Pathway selector */}
        <div id="pathway-selector" className="space-y-3">
          <p className="text-xs font-bold text-muted-foreground/60 uppercase tracking-widest px-1">
            Choose a Pathway
          </p>
          {pathways.map((p) => (
            <PathwayCard
              key={p.id}
              pathway={p}
              selected={selectedId === p.id}
              onSelect={() => setSelectedId(p.id)}
            />
          ))}

          {/* Resume strength teaser */}
          <div className="mt-4 p-4 rounded-xl border border-border/40 bg-card/60">
            <ResumeStrengthMeter score={selected.progress} compact />
          </div>
        </div>

        {/* Right: Pathway detail */}
        <div id="pathway-detail" className="lg:col-span-2">
          <AnimatePresence mode="wait">
            <motion.div
              key={selectedId}
              initial={{ opacity: 0, x: 16 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -8 }}
              transition={{ duration: 0.25, ease: 'easeOut' }}
              className="space-y-4"
            >
              {/* Overview card */}
              <Card id="pathway-overview-card" className="border-border/50 bg-card/80">
                <CardContent className="pt-5 pb-5">
                  <div className="flex items-start justify-between gap-3 mb-4">
                    <div>
                      <h2 className="text-xl font-extrabold tracking-tight">{selected.title}</h2>
                      <p className="text-sm text-muted-foreground mt-0.5">{selected.subtitle}</p>
                    </div>
                    <Badge
                      variant="outline"
                      className="border-primary/30 text-primary bg-primary/5 flex-shrink-0"
                    >
                      {selected.level}
                    </Badge>
                  </div>

                  {/* Progress */}
                  <div className="space-y-1.5 mb-4">
                    <div className="flex justify-between text-xs">
                      <span className="text-muted-foreground">
                        {completedCount} of {selected.steps.length} steps complete
                      </span>
                      <span className="font-bold text-foreground">{selected.progress}%</span>
                    </div>
                    <Progress value={selected.progress} className="h-2" />
                  </div>

                  {/* Target outcome */}
                  <div
                    id="pathway-outcome"
                    className="p-3 rounded-xl border border-emerald-500/15 bg-emerald-500/5 mb-3"
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <Target className="h-3.5 w-3.5 text-emerald-400" />
                      <span className="text-xs font-bold text-emerald-400">Target Outcome</span>
                    </div>
                    <p className="text-sm font-medium">{selected.outcome}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      Expected salary: <span className="text-emerald-400 font-semibold">{selected.salary}</span>
                    </p>
                  </div>

                  {/* Skill tags */}
                  <div id="pathway-skills" className="flex flex-wrap gap-1.5">
                    {selected.skills.map((skill) => (
                      <Badge key={skill} variant="secondary" className="text-xs">{skill}</Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Steps as timeline */}
              <Card id="pathway-steps-card" className="border-border/50 bg-card/80">
                <CardContent className="pt-4 pb-4">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-sm flex items-center gap-2">
                      <ArrowRight className="h-4 w-4 text-primary" />
                      Learning Steps
                    </h3>
                    {/* Step type legend */}
                    <div className="flex items-center gap-3 flex-wrap">
                      {(Object.entries(stepTypeConfig) as [StepType, typeof stepTypeConfig[StepType]][]).map(([type, cfg]) => {
                        const Ic = cfg.icon;
                        return (
                          <div key={type} className="flex items-center gap-1">
                            <div className={`h-5 w-5 rounded ${cfg.bg} flex items-center justify-center`}>
                              <Ic className={`h-3 w-3 ${cfg.color}`} />
                            </div>
                            <span className="text-[10px] text-muted-foreground capitalize">{type}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  <CareerTimeline steps={timelineSteps} />
                </CardContent>
              </Card>

              {/* CTA */}
              <div
                id="pathway-cta"
                className="flex gap-3 flex-wrap"
              >
                <Button
                  className="flex-1 bg-gradient-primary hover:opacity-90 border-0 text-white shadow-glow gap-2"
                >
                  Continue This Pathway
                  <ChevronRight className="h-4 w-4" />
                </Button>
                <Button variant="outline" className="border-border/60">
                  Share Progress
                </Button>
              </div>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
