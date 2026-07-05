import { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import {
  Target,
  Briefcase,
  TrendingUp,
  FileText,
  ArrowRight,
  CheckCircle2,
  Clock,
  Circle,
  MapPin,
  Building2,
  ChevronRight,
  Sparkles,
  BookOpen,
  MessageSquare
} from 'lucide-react';
import { useUserStore } from '@/store/useUserStore';
import { apiService } from '@/services/api';
import { Career, Job, Milestone } from '@/types';
import { DashboardSkeleton } from '@/components/ui/loading-skeletons';
import { EmptyState } from '@/components/ui/empty-state';

function useCountUp(end: number, duration = 1000) {
  const [count, setCount] = useState(0);
  const started = useRef(false);

  useEffect(() => {
    if (started.current || end === 0) return;
    started.current = true;

    let startTime: number | null = null;
    let frameId: number;

    const step = (ts: number) => {
      if (!startTime) startTime = ts;
      const progress = Math.min((ts - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setCount(Math.round(eased * end));
      if (progress < 1) {
        frameId = requestAnimationFrame(step);
      }
    };

    frameId = requestAnimationFrame(step);
    return () => cancelAnimationFrame(frameId);
  }, [end, duration]);

  return count;
}

function AnimatedStatCard({
  title,
  value,
  suffix,
  subtitle,
  progress,
  icon: Icon,
}: {
  title: string;
  value: number;
  suffix?: string;
  subtitle?: string;
  progress?: number;
  icon: React.ElementType;
}) {
  const animatedValue = useCountUp(value);

  return (
    <Card className="overflow-hidden">
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm text-muted-foreground">{title}</span>
          <Icon className="h-4 w-4 text-muted-foreground" />
        </div>
        <div className="text-2xl font-semibold mb-1">
          {animatedValue}
          {suffix}
        </div>
        {progress !== undefined && (
          <Progress value={animatedValue} className="h-1.5 mb-2" />
        )}
        {subtitle && (
          <p className="text-xs text-muted-foreground">{subtitle}</p>
        )}
      </CardContent>
    </Card>
  );
}

function MatchRingBadge({ percentage }: { percentage: number }) {
  const size = 32;
  const strokeWidth = 3;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

  return (
    <div className="relative inline-flex items-center justify-center shrink-0">
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="hsl(var(--muted))"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="hsl(var(--primary))"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="ring-progress"
        />
      </svg>
      <span className="absolute text-[9px] font-semibold">{percentage}%</span>
    </div>
  );
}

function MilestoneItem({ milestone }: { milestone: Milestone }) {
  const statusIcon = {
    completed: <CheckCircle2 className="h-4 w-4 text-success" />,
    'in-progress': <Clock className="h-4 w-4 text-primary" />,
    pending: <Circle className="h-4 w-4 text-muted-foreground" />,
    overdue: <Clock className="h-4 w-4 text-destructive" />,
  };

  return (
    <div className="flex items-start gap-3 py-3">
      <div className="mt-0.5">
        {statusIcon[milestone.status]}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2">
          <p className="text-sm font-medium truncate">{milestone.title}</p>
          <Badge
            variant={milestone.status === 'completed' ? 'default' : 'secondary'}
            className="text-xs shrink-0"
          >
            {milestone.status === 'in-progress' ? 'In Progress' : milestone.status}
          </Badge>
        </div>
        {milestone.description && (
          <p className="text-xs text-muted-foreground mt-0.5 truncate">
            {milestone.description}
          </p>
        )}
        {milestone.dueDate && (
          <p className="text-xs text-muted-foreground mt-1">
            Due {new Date(milestone.dueDate).toLocaleDateString()}
          </p>
        )}
      </div>
    </div>
  );
}

function CompactJobCard({ job, index }: { job: Job; index: number }) {
  return (
    <Link
      to="/jobs"
      className="flex items-start gap-3 p-3 rounded-lg border hover:bg-muted/50 transition-colors animate-slide-in-right hover-lift"
      style={{ animationDelay: `${index * 60}ms` }}
    >
      <div className="h-10 w-10 rounded-lg bg-muted flex items-center justify-center shrink-0">
        <Building2 className="h-5 w-5 text-muted-foreground" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2">
          <p className="text-sm font-medium truncate">{job.title}</p>
          {job.match && <MatchRingBadge percentage={job.match} />}
        </div>
        <p className="text-xs text-muted-foreground">{job.company}</p>
        <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
          <MapPin className="h-3 w-3" />
          <span>{job.location}</span>
          {job.salary && (
            <>
              <span className="text-muted-foreground/50">|</span>
              <span>{job.salary}</span>
            </>
          )}
        </div>
      </div>
      <ChevronRight className="h-4 w-4 text-muted-foreground shrink-0 mt-3" />
    </Link>
  );
}

function CompactCareerCard({ career }: { career: Career }) {
  return (
    <Link
      to={`/careers/${career.id}`}
      className="flex items-center justify-between p-3 rounded-lg border hover:bg-muted/50 transition-colors hover-lift"
    >
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <p className="text-sm font-medium truncate">{career.title}</p>
          {career.match && (
            <Badge variant="secondary" className="text-xs shrink-0">
              {career.match}% match
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
          <span>${Math.round(career.salary.min / 1000)}k - ${Math.round(career.salary.max / 1000)}k</span>
          <span className="text-muted-foreground/50">|</span>
          <span>{career.growth}</span>
        </div>
      </div>
      <ChevronRight className="h-4 w-4 text-muted-foreground shrink-0" />
    </Link>
  );
}

export default function Dashboard() {
  const { user, savedJobs } = useUserStore();
  const [careers, setCareers] = useState<Career[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await apiService.getCareers();
        setCareers(data.slice(0, 4));
      } catch (err) {
        setError('Failed to load career matches');
        console.error('Error loading careers:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (!user) {
    return (
      <EmptyState
        icon={Target}
        title="Welcome to AI Career Assistant"
        description="Sign in to access your personalized career dashboard and recommendations."
        action={{ label: 'Get Started', onClick: () => {} }}
      />
    );
  }

  if (loading) {
    return <DashboardSkeleton />;
  }

  const recentJobs: Job[] = [
    {
      id: '1',
      title: 'Frontend Developer',
      company: 'TechCorp',
      location: 'San Francisco, CA',
      salary: '$90k - $120k',
      type: 'full-time',
      description: '',
      requirements: [],
      match: 94,
      postedDate: '2024-01-15',
      applied: false,
      saved: false,
      source: 'LinkedIn',
    },
    {
      id: '2',
      title: 'Full Stack Engineer',
      company: 'StartupXYZ',
      location: 'Remote',
      salary: '$80k - $110k',
      type: 'full-time',
      description: '',
      requirements: [],
      match: 89,
      postedDate: '2024-01-12',
      applied: false,
      saved: true,
      source: 'Indeed',
    },
    {
      id: '3',
      title: 'Software Engineer',
      company: 'BigTech Inc',
      location: 'Seattle, WA',
      salary: '$100k - $140k',
      type: 'full-time',
      description: '',
      requirements: [],
      match: 87,
      postedDate: '2024-01-10',
      applied: false,
      saved: false,
      source: 'Glassdoor',
    },
  ];

  const milestones: Milestone[] = [
    {
      id: '1',
      title: 'Complete Skills Assessment',
      description: 'Identify your key strengths',
      type: 'skill',
      status: 'completed',
      completedDate: '2024-01-18',
    },
    {
      id: '2',
      title: 'Apply to TechCorp',
      description: 'Frontend Developer position',
      type: 'application',
      status: 'in-progress',
      dueDate: '2024-01-25',
    },
    {
      id: '3',
      title: 'Complete React Course',
      description: 'Advanced patterns',
      type: 'learning',
      status: 'pending',
      dueDate: '2024-02-01',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header with gradient text */}
      <div className="animate-fade-in-up">
        <h1 className="text-2xl font-semibold gradient-text">
          Welcome back, {user.name.split(' ')[0]}
        </h1>
        <p className="text-muted-foreground mt-1">
          Here's your career progress overview
        </p>
      </div>

      {/* Stats Grid - staggered entrance */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="animate-fade-in-up stagger-1 hover-lift">
          <AnimatedStatCard
            title="Career Match"
            value={user.progress.careerMatch}
            suffix="%"
            progress={user.progress.careerMatch}
            subtitle="Based on your profile"
            icon={Target}
          />
        </div>
        <div className="animate-fade-in-up stagger-2 hover-lift">
          <AnimatedStatCard
            title="Skills Completed"
            value={user.progress.skillsCompleted}
            subtitle="Keep learning to improve"
            icon={TrendingUp}
          />
        </div>
        <div className="animate-fade-in-up stagger-3 hover-lift">
          <AnimatedStatCard
            title="Applications"
            value={user.progress.applicationsSubmitted}
            subtitle="This month"
            icon={Briefcase}
          />
        </div>
        <div className="animate-fade-in-up stagger-4 hover-lift">
          <AnimatedStatCard
            title="Profile"
            value={user.progress.profileCompletion}
            suffix="%"
            progress={user.progress.profileCompletion}
            subtitle="Complete for better matches"
            icon={FileText}
          />
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left Column - Career Matches & Jobs */}
        <div className="lg:col-span-2 space-y-6">
          {/* Career Matches */}
          <div className="animate-fade-in-up stagger-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-3">
                <CardTitle className="text-base font-medium">Top Career Matches</CardTitle>
                <Button variant="ghost" size="sm" className="text-muted-foreground" asChild>
                  <Link to="/careers">
                    View all
                    <ArrowRight className="ml-1 h-4 w-4" />
                  </Link>
                </Button>
              </CardHeader>
              <CardContent className="space-y-2">
                {careers.length > 0 ? (
                  careers.map((career) => (
                    <CompactCareerCard key={career.id} career={career} />
                  ))
                ) : (
                  <EmptyState
                    icon={Target}
                    title="No career matches yet"
                    description="Complete your profile to get personalized career recommendations."
                    className="py-8"
                  />
                )}
              </CardContent>
            </Card>
          </div>

          {/* Recent Jobs */}
          <div className="animate-slide-in-right stagger-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-3">
                <CardTitle className="text-base font-medium">Recent Job Matches</CardTitle>
                <Button variant="ghost" size="sm" className="text-muted-foreground" asChild>
                  <Link to="/jobs">
                    View all
                    <ArrowRight className="ml-1 h-4 w-4" />
                  </Link>
                </Button>
              </CardHeader>
              <CardContent className="space-y-2">
                {recentJobs.map((job, index) => (
                  <CompactJobCard key={job.id} job={job} index={index} />
                ))}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Right Column - Milestones & Quick Actions */}
        <div className="space-y-6 animate-slide-in-right stagger-5">
          {/* Active Roadmap Summary */}
          <Card className="hover-lift">
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-medium">Your Roadmap</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Current goal</span>
                  <span className="font-medium">Software Engineer</span>
                </div>
                <Progress value={35} className="h-2" />
                <p className="text-xs text-muted-foreground">
                  35% complete - 3 of 8 milestones achieved
                </p>
              </div>
              <Button variant="outline" className="w-full mt-4" size="sm" asChild>
                <Link to="/careers">
                  View Roadmap
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </CardContent>
          </Card>

          {/* Milestones */}
          <Card className="hover-lift">
            <CardHeader className="pb-2">
              <CardTitle className="text-base font-medium">Milestones</CardTitle>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="divide-y">
                {milestones.map((milestone) => (
                  <MilestoneItem key={milestone.id} milestone={milestone} />
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card className="hover-lift">
            <CardHeader className="pb-3">
              <CardTitle className="text-base font-medium">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-2">
              <Button variant="outline" className="justify-start h-auto py-3" asChild>
                <Link to="/resume">
                  <FileText className="h-4 w-4 mr-3" />
                  <div className="text-left">
                    <div className="font-medium text-sm">Resume Builder</div>
                    <div className="text-xs text-muted-foreground">Upload and analyze</div>
                  </div>
                </Link>
              </Button>
              <Button variant="outline" className="justify-start h-auto py-3" asChild>
                <Link to="/interview">
                  <MessageSquare className="h-4 w-4 mr-3" />
                  <div className="text-left">
                    <div className="font-medium text-sm">Interview Prep</div>
                    <div className="text-xs text-muted-foreground">Practice questions</div>
                  </div>
                </Link>
              </Button>
              <Button variant="outline" className="justify-start h-auto py-3" asChild>
                <Link to="/assistant">
                  <Sparkles className="h-4 w-4 mr-3" />
                  <div className="text-left">
                    <div className="font-medium text-sm">AI Assistant</div>
                    <div className="text-xs text-muted-foreground">Get guidance</div>
                  </div>
                </Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
