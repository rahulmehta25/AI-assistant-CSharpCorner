import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { GraduationCap, CheckCircle, Clock, ChevronRight, Star, BookOpen, Briefcase, Code } from 'lucide-react';

interface PathwayStep {
  id: string;
  title: string;
  description: string;
  type: 'course' | 'project' | 'certification' | 'job';
  duration: string;
  status: 'completed' | 'active' | 'upcoming';
  resources?: string[];
}

interface Pathway {
  id: string;
  title: string;
  subtitle: string;
  level: string;
  duration: string;
  progress: number;
  steps: PathwayStep[];
  skills: string[];
  outcome: string;
}

const pathways: Pathway[] = [
  {
    id: 'frontend',
    title: 'Frontend Developer',
    subtitle: 'From beginner to job-ready in 12 months',
    level: 'Beginner → Mid',
    duration: '12 months',
    progress: 42,
    outcome: 'Land a $85K–$115K frontend role at a tech company',
    skills: ['HTML/CSS', 'JavaScript', 'React', 'TypeScript', 'Testing', 'Git'],
    steps: [
      {
        id: 'f1',
        title: 'HTML & CSS Fundamentals',
        description: 'Build the visual foundation. Learn semantic HTML, Flexbox, CSS Grid, and responsive design.',
        type: 'course',
        duration: '4 weeks',
        status: 'completed',
        resources: ['freeCodeCamp', 'The Odin Project'],
      },
      {
        id: 'f2',
        title: 'JavaScript Essentials',
        description: 'Core JS: DOM manipulation, events, async/await, fetch API, and ES6+ features.',
        type: 'course',
        duration: '6 weeks',
        status: 'completed',
        resources: ['javascript.info', 'Eloquent JavaScript'],
      },
      {
        id: 'f3',
        title: 'Build 3 Portfolio Projects',
        description: 'Apply your skills: to-do app, weather dashboard, and an API-driven web app.',
        type: 'project',
        duration: '4 weeks',
        status: 'active',
        resources: ['GitHub', 'Netlify', 'Vercel'],
      },
      {
        id: 'f4',
        title: 'React & TypeScript',
        description: 'Modern frontend development with React hooks, context, React Query, and strict TypeScript.',
        type: 'course',
        duration: '8 weeks',
        status: 'upcoming',
        resources: ['React docs', 'TypeScript docs', 'Frontend Masters'],
      },
      {
        id: 'f5',
        title: 'Testing & Quality',
        description: 'Write unit and integration tests with Vitest and React Testing Library.',
        type: 'course',
        duration: '2 weeks',
        status: 'upcoming',
      },
      {
        id: 'f6',
        title: 'Job Search Sprint',
        description: 'Apply to 30+ roles, prep for technical interviews, and land your first offer.',
        type: 'job',
        duration: '4–12 weeks',
        status: 'upcoming',
      },
    ],
  },
  {
    id: 'fullstack',
    title: 'Full Stack Engineer',
    subtitle: 'Master both frontend and backend systems',
    level: 'Mid → Senior',
    duration: '18 months',
    progress: 20,
    outcome: 'Become a full-stack engineer earning $110K–$150K',
    skills: ['React', 'Node.js', 'Databases', 'APIs', 'Docker', 'AWS'],
    steps: [
      {
        id: 'fs1',
        title: 'Node.js & Express APIs',
        description: 'Build RESTful APIs with Express, middleware, authentication, and error handling.',
        type: 'course',
        duration: '6 weeks',
        status: 'completed',
      },
      {
        id: 'fs2',
        title: 'Database Design (SQL + NoSQL)',
        description: 'PostgreSQL for relational data, MongoDB for documents. Schema design, indexes, ORMs.',
        type: 'course',
        duration: '4 weeks',
        status: 'active',
      },
      {
        id: 'fs3',
        title: 'Build a Full-Stack SaaS App',
        description: 'End-to-end project: React frontend, Node.js API, PostgreSQL, authentication, deployment.',
        type: 'project',
        duration: '8 weeks',
        status: 'upcoming',
      },
      {
        id: 'fs4',
        title: 'Docker & Deployment',
        description: 'Containerize your apps, set up CI/CD pipelines, deploy to AWS/Render.',
        type: 'course',
        duration: '3 weeks',
        status: 'upcoming',
      },
      {
        id: 'fs5',
        title: 'AWS Developer Associate (Optional)',
        description: 'Official AWS certification to validate your cloud skills.',
        type: 'certification',
        duration: '6 weeks',
        status: 'upcoming',
      },
    ],
  },
  {
    id: 'datascience',
    title: 'Data Scientist',
    subtitle: 'From Python basics to ML models in production',
    level: 'Beginner → Senior',
    duration: '24 months',
    progress: 8,
    outcome: 'Data Scientist role at $120K–$180K',
    skills: ['Python', 'Statistics', 'ML', 'SQL', 'Visualization', 'Deep Learning'],
    steps: [
      {
        id: 'ds1',
        title: 'Python for Data Science',
        description: 'NumPy, Pandas, Matplotlib, Seaborn — the core toolkit for every data scientist.',
        type: 'course',
        duration: '6 weeks',
        status: 'active',
      },
      {
        id: 'ds2',
        title: 'Statistics & Probability',
        description: 'Hypothesis testing, distributions, regression, Bayesian reasoning.',
        type: 'course',
        duration: '8 weeks',
        status: 'upcoming',
      },
      {
        id: 'ds3',
        title: 'Machine Learning with Scikit-learn',
        description: 'Classification, regression, clustering, model evaluation, feature engineering.',
        type: 'course',
        duration: '10 weeks',
        status: 'upcoming',
      },
      {
        id: 'ds4',
        title: 'Kaggle Competition (top 20%)',
        description: 'Apply your skills in a real ML competition to build portfolio credibility.',
        type: 'project',
        duration: '4 weeks',
        status: 'upcoming',
      },
    ],
  },
];

const stepTypeConfig = {
  course: { icon: BookOpen, color: 'text-blue-400', bg: 'bg-blue-500/10' },
  project: { icon: Code, color: 'text-purple-400', bg: 'bg-purple-500/10' },
  certification: { icon: Star, color: 'text-amber-400', bg: 'bg-amber-500/10' },
  job: { icon: Briefcase, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
};

function PathwayCard({ pathway, selected, onSelect }: { pathway: Pathway; selected: boolean; onSelect: () => void }) {
  return (
    <button
      id={`pathway-btn-${pathway.id}`}
      onClick={onSelect}
      className={`w-full text-left p-4 rounded-xl border transition-all ${
        selected ? 'border-primary bg-primary/5' : 'border-border/50 hover:border-primary/30'
      }`}
    >
      <div className="flex items-start justify-between mb-2">
        <div>
          <h3 className="font-semibold text-sm">{pathway.title}</h3>
          <p className="text-xs text-muted-foreground">{pathway.level} · {pathway.duration}</p>
        </div>
        <Badge variant="outline" className="text-xs">{pathway.progress}%</Badge>
      </div>
      <Progress value={pathway.progress} className="h-1" />
    </button>
  );
}

function StepCard({ step }: { step: PathwayStep }) {
  const cfg = stepTypeConfig[step.type];
  const Icon = cfg.icon;

  return (
    <div
      id={`step-${step.id}`}
      className={`flex gap-4 p-4 rounded-xl border transition-colors ${
        step.status === 'active'
          ? 'border-primary/30 bg-primary/5'
          : step.status === 'completed'
          ? 'border-emerald-500/20 bg-emerald-500/5'
          : 'border-border/50'
      }`}
    >
      {/* Timeline dot */}
      <div className="flex flex-col items-center gap-1 flex-shrink-0">
        <div
          className={`h-8 w-8 rounded-full flex items-center justify-center ${
            step.status === 'completed'
              ? 'bg-emerald-500/20'
              : step.status === 'active'
              ? 'bg-primary/20'
              : 'bg-muted'
          }`}
        >
          {step.status === 'completed' ? (
            <CheckCircle className="h-4 w-4 text-emerald-500" />
          ) : step.status === 'active' ? (
            <Clock className="h-4 w-4 text-primary" />
          ) : (
            <div className="h-3 w-3 rounded-full border-2 border-muted-foreground/30" />
          )}
        </div>
      </div>

      <div className="flex-1">
        <div className="flex items-start justify-between gap-2 mb-1">
          <div className="flex items-center gap-2">
            <div className={`p-1.5 rounded-lg ${cfg.bg}`}>
              <Icon className={`h-3 w-3 ${cfg.color}`} />
            </div>
            <h4 className="font-semibold text-sm">{step.title}</h4>
          </div>
          <span className="text-xs text-muted-foreground flex-shrink-0 flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {step.duration}
          </span>
        </div>
        <p className="text-xs text-muted-foreground mb-2 leading-relaxed">{step.description}</p>
        {step.resources && (
          <div className="flex flex-wrap gap-1">
            {step.resources.map((r) => (
              <Badge key={r} variant="secondary" className="text-xs px-2 py-0.5">{r}</Badge>
            ))}
          </div>
        )}
        {step.status === 'active' && (
          <Button id={`start-${step.id}`} size="sm" className="mt-3 gap-1.5">
            Continue <ChevronRight className="h-3 w-3" />
          </Button>
        )}
      </div>
    </div>
  );
}

export default function Pathways() {
  const [selectedId, setSelectedId] = useState('frontend');
  const selected = pathways.find((p) => p.id === selectedId)!;

  return (
    <div id="pathways-container" className="container mx-auto py-8 px-4 max-w-6xl">
      <motion.div id="pathways-header" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
            <GraduationCap className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">Career Pathways</h1>
            <p className="text-muted-foreground">Structured roadmaps from where you are to where you want to be</p>
          </div>
        </div>
      </motion.div>

      <div id="pathways-layout" className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pathway selector */}
        <div id="pathway-selector" className="space-y-3">
          <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Choose a Pathway</h2>
          {pathways.map((p) => (
            <PathwayCard
              key={p.id}
              pathway={p}
              selected={selectedId === p.id}
              onSelect={() => setSelectedId(p.id)}
            />
          ))}
        </div>

        {/* Pathway detail */}
        <div id="pathway-detail" className="lg:col-span-2">
          <motion.div key={selectedId} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
            {/* Header */}
            <Card id="pathway-detail-card" className="border-border/50 mb-5">
              <CardContent className="pt-5 pb-5">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h2 className="text-2xl font-bold mb-1">{selected.title}</h2>
                    <p className="text-muted-foreground">{selected.subtitle}</p>
                  </div>
                  <Badge className="bg-primary/10 text-primary border-primary/20">{selected.level}</Badge>
                </div>
                <div className="space-y-2 mb-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Overall Progress</span>
                    <span className="font-semibold">{selected.progress}%</span>
                  </div>
                  <Progress value={selected.progress} className="h-2" />
                </div>
                <div id="pathway-outcome" className="p-3 bg-emerald-500/5 rounded-lg border border-emerald-500/15">
                  <p className="text-xs font-medium text-emerald-500">Target Outcome</p>
                  <p className="text-sm mt-0.5">{selected.outcome}</p>
                </div>
                <div id="pathway-skills" className="flex flex-wrap gap-1.5 mt-4">
                  {selected.skills.map((skill) => (
                    <Badge key={skill} variant="secondary" className="text-xs">{skill}</Badge>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Steps */}
            <div id="pathway-steps" className="space-y-3">
              {selected.steps.map((step) => (
                <StepCard key={step.id} step={step} />
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
