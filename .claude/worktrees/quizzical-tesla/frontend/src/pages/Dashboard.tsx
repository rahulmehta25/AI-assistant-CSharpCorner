import { useState, useEffect } from 'react';
import { motion, type Variants } from 'framer-motion';
import { Link } from 'react-router-dom';
import { format, addDays } from 'date-fns';
import {
  Target, Briefcase, TrendingUp, Award, ArrowRight,
  Bot, Sparkles, CheckCircle, Clock, BookOpen,
  ChevronRight, Zap,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { SkillRadarChart, type SkillData } from '@/components/ui/skill-radar-chart';
import { JobMatchRing } from '@/components/ui/job-match-ring';
import { ResumeStrengthMeter } from '@/components/ui/resume-strength-meter';
import { CareerTimeline, type TimelineStep } from '@/components/ui/career-timeline';
import { SkeletonStats, SkeletonList } from '@/components/ui/skeleton-card';
import { useUserStore } from '@/store/useUserStore';
import { apiService } from '@/services/api';
import type { Career, Job } from '@/types';

/* ── Animation variants ─────────────────────────────── */
const container: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.07 } },
};
const item: Variants = {
  hidden: { opacity: 0, y: 18 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' as const } },
};

/* ── Static helpers ──────────────────────────────────── */
const defaultSkillData: SkillData[] = [
  { subject: 'React',      score: 85 },
  { subject: 'TypeScript', score: 72 },
  { subject: 'Node.js',    score: 60 },
  { subject: 'Python',     score: 45 },
  { subject: 'SQL',        score: 68 },
  { subject: 'CSS/Design', score: 78 },
];

function getRecentJobs(): Job[] {
  const today = new Date();
  return [
    {
      id: '1', title: 'Frontend Developer', company: 'TechCorp',
      location: 'San Francisco, CA', salary: '$95k – $125k', type: 'full-time',
      description: 'Build amazing UIs with React & TypeScript.',
      requirements: ['React', 'TypeScript', 'CSS'],
      benefits: ['Health', '401k', 'PTO'],
      match: 94, postedDate: format(addDays(today, -2), 'yyyy-MM-dd'),
      applied: false, saved: false, source: 'LinkedIn',
    },
    {
      id: '2', title: 'Full Stack Engineer', company: 'StartupXYZ',
      location: 'Remote', salary: '$85k – $115k', type: 'full-time',
      description: 'Frontend + backend with modern tech.',
      requirements: ['TypeScript', 'Node.js', 'PostgreSQL'],
      benefits: ['Remote', 'Equity', 'Learning'],
      match: 89, postedDate: format(addDays(today, -5), 'yyyy-MM-dd'),
      applied: true, saved: true, source: 'Indeed',
    },
    {
      id: '3', title: 'Software Engineer – AI', company: 'AIFirst Inc',
      location: 'New York, NY', salary: '$110k – $145k', type: 'full-time',
      description: 'Build AI-powered features with LLM integrations.',
      requirements: ['Python', 'TypeScript', 'API Design'],
      benefits: ['Equity', 'Mentorship', 'Conf budget'],
      match: 82, postedDate: format(addDays(today, -7), 'yyyy-MM-dd'),
      applied: false, saved: true, source: 'Company',
    },
  ];
}

function getMilestones(): TimelineStep[] {
  return [
    {
      id: 'm1', title: 'Complete Skills Assessment',
      status: 'active',
      duration: '3 days left',
      description: 'Identify your key strengths and areas for improvement.',
      tags: ['Self-assessment', 'Career planning'],
    },
    {
      id: 'm2', title: 'Apply to 5 Target Roles',
      status: 'upcoming',
      duration: '10 days',
      description: 'Focus on roles that match your top skills and interests.',
      tags: ['Applications', 'Job search'],
    },
    {
      id: 'm3', title: 'Complete Advanced React Course',
      status: 'upcoming',
      duration: '30 days',
      description: 'Advanced patterns, performance optimization, and testing.',
      tags: ['Learning', 'React'],
    },
    {
      id: 'm4', title: 'Add 2 New Portfolio Projects',
      status: 'upcoming',
      duration: '45 days',
      description: 'Showcase recent projects with live demos and case studies.',
      tags: ['Portfolio', 'GitHub'],
    },
  ];
}

/* ── Stat card component ─────────────────────────────── */
interface StatCardProps {
  id: string;
  title: string;
  value: string | number;
  icon: React.ReactNode;
  iconBg: string;
  progress?: number;
  badge?: string;
  badgeColor?: string;
  description: string;
}

const StatCard = ({
  id, title, value, icon, iconBg, progress, badge, badgeColor, description,
}: StatCardProps) => (
  <motion.div id={id} variants={item}>
    <Card className="border-border/50 bg-card/80 hover:border-primary/30 hover:shadow-lg transition-all duration-300 group">
      <CardContent className="pt-5 pb-5">
        <div className="flex items-start justify-between mb-3">
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
            {title}
          </p>
          <div className={`h-9 w-9 rounded-xl flex items-center justify-center ${iconBg} group-hover:scale-110 transition-transform duration-200`}>
            {icon}
          </div>
        </div>
        <p className="text-3xl font-extrabold tracking-tight text-foreground mb-2">
          {value}
        </p>
        {progress !== undefined && (
          <Progress
            value={progress}
            className="h-1.5 mb-2"
          />
        )}
        <div className="flex items-center justify-between">
          <p className="text-xs text-muted-foreground">{description}</p>
          {badge && (
            <Badge
              variant="outline"
              className={`text-[10px] h-4 px-1.5 ${badgeColor}`}
            >
              {badge}
            </Badge>
          )}
        </div>
      </CardContent>
    </Card>
  </motion.div>
);

/* ── Main Dashboard ──────────────────────────────────── */
export default function Dashboard() {
  const { user } = useUserStore();
  const [careers, setCareers] = useState<Career[]>([]);
  const [loadingCareers, setLoadingCareers] = useState(true);

  const firstName = user?.name?.split(' ')[0] ?? 'there';
  const careerMatch     = user?.progress?.careerMatch       ?? 85;
  const skillsCompleted = user?.progress?.skillsCompleted   ?? 12;
  const applications    = user?.progress?.applicationsSubmitted ?? 3;
  const profileCompletion = user?.progress?.profileCompletion ?? 78;

  const skillData: SkillData[] =
    user?.profile?.skills?.slice(0, 6).map((s) => ({
      subject: s.name,
      score:
        s.level === 'expert'       ? 92 :
        s.level === 'advanced'     ? 78 :
        s.level === 'intermediate' ? 60 : 38,
    })) ?? defaultSkillData;

  useEffect(() => {
    apiService.getCareers()
      .then((data) => setCareers(data.slice(0, 3)))
      .catch(console.error)
      .finally(() => setLoadingCareers(false));
  }, []);

  const recentJobs = getRecentJobs();
  const milestones = getMilestones();

  return (
    <motion.div
      id="dashboard-container"
      variants={container}
      initial="hidden"
      animate="visible"
      className="space-y-6 max-w-7xl"
    >
      {/* ── Hero greeting ──────────────────────────────── */}
      <motion.div id="dashboard-hero" variants={item} className="relative">
        <div className="absolute inset-0 rounded-2xl hero-glow pointer-events-none" />
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight">
              Welcome back,{' '}
              <span className="text-gradient-primary">{firstName}!</span>
            </h1>
            <p className="text-muted-foreground mt-1">
              Here's your career intelligence summary.
            </p>
          </div>
          <Button
            asChild
            className="bg-gradient-primary hover:opacity-90 text-white border-0 shadow-glow gap-2"
          >
            <Link to="/assistant">
              <Bot className="h-4 w-4" />
              Ask AI Assistant
            </Link>
          </Button>
        </div>
      </motion.div>

      {/* ── Stats row ──────────────────────────────────── */}
      <div id="dashboard-stats" className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          id="stat-career-match"
          title="Career Match"
          value={`${careerMatch}%`}
          icon={<Target className="h-4 w-4 text-primary" />}
          iconBg="bg-primary/10"
          progress={careerMatch}
          badge="+5% this week"
          badgeColor="border-emerald-500/30 text-emerald-400"
          description="Based on skills & interests"
        />
        <StatCard
          id="stat-skills"
          title="Skills Earned"
          value={skillsCompleted}
          icon={<Award className="h-4 w-4 text-amber-400" />}
          iconBg="bg-amber-500/10"
          badge="+2 this month"
          badgeColor="border-amber-500/30 text-amber-400"
          description="New skills learned"
        />
        <StatCard
          id="stat-applications"
          title="Applications"
          value={applications}
          icon={<Briefcase className="h-4 w-4 text-cyan-400" />}
          iconBg="bg-cyan-500/10"
          description="Submitted this month"
        />
        <StatCard
          id="stat-profile"
          title="Profile Strength"
          value={`${profileCompletion}%`}
          icon={<TrendingUp className="h-4 w-4 text-violet-400" />}
          iconBg="bg-violet-500/10"
          progress={profileCompletion}
          description="Complete for better matches"
        />
      </div>

      {/* ── Main content grid ──────────────────────────── */}
      <div id="dashboard-main" className="grid gap-6 lg:grid-cols-3">

        {/* Left column: Skill radar + resume strength */}
        <motion.div id="dashboard-left-col" variants={item} className="space-y-4">
          {/* Skill Radar */}
          <Card className="border-border/50 bg-card/80">
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-primary" />
                Skill Radar
              </CardTitle>
            </CardHeader>
            <CardContent className="pb-4">
              <SkillRadarChart data={skillData} />
            </CardContent>
          </Card>

          {/* Resume Strength */}
          <Card id="resume-strength-card" className="border-border/50 bg-card/80">
            <CardContent className="pt-5 pb-5 space-y-4">
              <ResumeStrengthMeter score={profileCompletion} />
              <div className="border-t border-border/40 pt-3">
                <p className="text-xs font-semibold text-muted-foreground mb-2">
                  Quick improvements
                </p>
                <ul id="profile-improvements" className="space-y-1.5">
                  {[
                    'Add a professional summary',
                    'Upload 2 more projects',
                    'Verify top 3 skills',
                  ].map((tip) => (
                    <li key={tip} className="flex items-center gap-2 text-xs text-muted-foreground">
                      <div className="h-1.5 w-1.5 rounded-full bg-primary/60 flex-shrink-0" />
                      {tip}
                    </li>
                  ))}
                </ul>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Right 2 columns: Career + Job matches */}
        <motion.div id="dashboard-right-cols" variants={item} className="lg:col-span-2 space-y-4">

          {/* Career Matches */}
          <Card id="career-matches-card" className="border-border/50 bg-card/80">
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <CardTitle className="text-base">Top Career Matches</CardTitle>
              <Button variant="ghost" size="sm" asChild className="text-xs text-primary hover:text-primary-light h-7 px-2">
                <Link to="/careers">
                  View All <ArrowRight className="ml-1 h-3 w-3" />
                </Link>
              </Button>
            </CardHeader>
            <CardContent className="space-y-2.5">
              {loadingCareers ? (
                <SkeletonList count={3} />
              ) : careers.length > 0 ? (
                careers.map((career) => (
                  <Link
                    key={career.id}
                    to={`/careers/${career.id}`}
                    id={`career-match-${career.id}`}
                    className="flex items-center gap-3 p-3 rounded-xl border border-border/40 hover:border-primary/30 hover:bg-muted/30 transition-all duration-200 group"
                  >
                    <div className="h-9 w-9 rounded-lg bg-gradient-primary/10 flex items-center justify-center flex-shrink-0">
                      <Target className="h-4 w-4 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-sm text-foreground group-hover:text-primary transition-colors truncate">
                        {career.title}
                      </p>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {career.salary ? `$${(career.salary.min / 1000).toFixed(0)}k – $${(career.salary.max / 1000).toFixed(0)}k` : career.salaryRange ?? ''}
                      </p>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      {career.match && (
                        <Badge
                          variant="outline"
                          className={`text-xs ${
                            career.match >= 85 ? 'border-emerald-500/30 text-emerald-400' :
                            career.match >= 70 ? 'border-blue-500/30 text-blue-400' :
                            'border-border'
                          }`}
                        >
                          {career.match}%
                        </Badge>
                      )}
                      <ChevronRight className="h-3.5 w-3.5 text-muted-foreground/40 group-hover:text-primary transition-colors" />
                    </div>
                  </Link>
                ))
              ) : (
                <div id="careers-empty" className="text-center py-8 text-muted-foreground">
                  <Target className="h-8 w-8 mx-auto mb-2 opacity-20" />
                  <p className="text-sm">No matches yet</p>
                  <Button variant="link" size="sm" asChild className="text-primary">
                    <Link to="/careers">Browse careers</Link>
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Job Recommendations */}
          <Card id="job-matches-card" className="border-border/50 bg-card/80">
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <CardTitle className="text-base">Job Recommendations</CardTitle>
              <Button variant="ghost" size="sm" asChild className="text-xs text-primary hover:text-primary-light h-7 px-2">
                <Link to="/jobs">
                  View All <ArrowRight className="ml-1 h-3 w-3" />
                </Link>
              </Button>
            </CardHeader>
            <CardContent className="space-y-2.5">
              {recentJobs.map((job) => (
                <div
                  key={job.id}
                  id={`job-rec-${job.id}`}
                  className="flex items-center gap-3 p-3 rounded-xl border border-border/40 hover:border-primary/30 hover:bg-muted/30 transition-all duration-200 group"
                >
                  {/* Match ring */}
                  <JobMatchRing
                    percentage={job.match ?? 0}
                    size={56}
                    strokeWidth={4}
                    className="flex-shrink-0"
                  />

                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-sm text-foreground group-hover:text-primary transition-colors truncate">
                      {job.title}
                    </p>
                    <p className="text-xs text-muted-foreground">{job.company}</p>
                    <div className="flex items-center gap-2 mt-1 flex-wrap">
                      <span className="text-xs text-muted-foreground">{job.location}</span>
                      {job.salary && (
                        <span className="text-xs font-semibold text-primary">{job.salary}</span>
                      )}
                    </div>
                  </div>

                  <div className="flex flex-col items-end gap-1 flex-shrink-0">
                    {job.applied && (
                      <Badge variant="default" className="text-[10px] h-4 px-1.5">
                        Applied
                      </Badge>
                    )}
                    <span className="text-[10px] text-muted-foreground/60">
                      {new Date(job.postedDate).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* ── Bottom row: Milestones + Quick Actions ──────── */}
      <div id="dashboard-bottom" className="grid gap-6 lg:grid-cols-5">
        {/* Career Milestones */}
        <motion.div id="milestones-section" variants={item} className="lg:col-span-3">
          <Card className="border-border/50 bg-card/80 h-full">
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-emerald-400" />
                Upcoming Milestones
              </CardTitle>
              <Button variant="ghost" size="sm" asChild className="text-xs text-primary hover:text-primary-light h-7 px-2">
                <Link to="/pathways">
                  Pathways <ArrowRight className="ml-1 h-3 w-3" />
                </Link>
              </Button>
            </CardHeader>
            <CardContent>
              <CareerTimeline steps={milestones} />
            </CardContent>
          </Card>
        </motion.div>

        {/* Quick Actions */}
        <motion.div id="quick-actions-section" variants={item} className="lg:col-span-2">
          <Card className="border-border/50 bg-card/80 h-full">
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Zap className="h-4 w-4 text-primary" />
                Quick Actions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div id="quick-actions-grid" className="grid grid-cols-2 gap-3">
                {[
                  { label: 'Assess Skills',    to: '/skills',    icon: Target,     bg: 'bg-blue-500/10',   color: 'text-blue-400'   },
                  { label: 'Explore Careers',  to: '/careers',   icon: TrendingUp, bg: 'bg-violet-500/10', color: 'text-violet-400' },
                  { label: 'Find Jobs',        to: '/jobs',      icon: Briefcase,  bg: 'bg-cyan-500/10',   color: 'text-cyan-400'   },
                  { label: 'AI Assistant',     to: '/assistant', icon: Bot,        bg: 'bg-emerald-500/10',color: 'text-emerald-400'},
                  { label: 'Learning Hub',     to: '/learning',  icon: BookOpen,   bg: 'bg-amber-500/10',  color: 'text-amber-400'  },
                  { label: 'Pathways',         to: '/pathways',  icon: Clock,      bg: 'bg-primary/10',    color: 'text-primary'    },
                ].map(({ label, to, icon: Icon, bg, color }) => (
                  <Link
                    key={to}
                    to={to}
                    id={`qa-${to.replace('/', '')}`}
                    className={`flex flex-col items-center justify-center gap-2 p-3 rounded-xl border border-border/40 hover:border-primary/30 transition-all duration-200 group ${bg}/40 hover:${bg}`}
                  >
                    <div className={`h-8 w-8 rounded-lg ${bg} flex items-center justify-center group-hover:scale-110 transition-transform`}>
                      <Icon className={`h-4 w-4 ${color}`} />
                    </div>
                    <span className="text-xs font-medium text-muted-foreground group-hover:text-foreground transition-colors text-center leading-tight">
                      {label}
                    </span>
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  );
}
