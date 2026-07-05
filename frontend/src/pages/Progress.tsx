import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { useUserStore } from '@/store/useUserStore';
import { Milestone, ActivityItem, Skill } from '@/types';
import { EmptyState } from '@/components/ui/empty-state';
import {
  Target,
  TrendingUp,
  Briefcase,
  Calendar,
  CheckCircle2,
  Circle,
  Clock,
  Award,
  BookOpen,
  FileText,
  MessageSquare,
  Star,
  Trophy,
  ArrowRight,
  ChevronRight
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { cn } from '@/lib/utils';

const mockMilestones: Milestone[] = [
  {
    id: '1',
    title: 'Complete Profile',
    description: 'Fill out all profile sections',
    type: 'skill',
    status: 'completed',
    completedDate: '2024-01-10',
    progress: 100,
  },
  {
    id: '2',
    title: 'Skills Assessment',
    description: 'Take the skills assessment quiz',
    type: 'skill',
    status: 'completed',
    completedDate: '2024-01-12',
    progress: 100,
  },
  {
    id: '3',
    title: 'First Job Application',
    description: 'Apply to your first matched job',
    type: 'application',
    status: 'completed',
    completedDate: '2024-01-15',
    progress: 100,
  },
  {
    id: '4',
    title: 'Complete React Course',
    description: 'Finish advanced React patterns course',
    type: 'learning',
    status: 'in-progress',
    dueDate: '2024-02-01',
    progress: 65,
  },
  {
    id: '5',
    title: 'Land First Interview',
    description: 'Get invited to your first interview',
    type: 'interview',
    status: 'pending',
    progress: 0,
  },
];

const mockActivities: ActivityItem[] = [
  {
    id: '1',
    type: 'skill_completed',
    title: 'Completed TypeScript Basics',
    timestamp: new Date('2024-01-18T14:30:00'),
  },
  {
    id: '2',
    type: 'application_sent',
    title: 'Applied to Frontend Developer at TechCorp',
    timestamp: new Date('2024-01-17T10:15:00'),
  },
  {
    id: '3',
    type: 'job_saved',
    title: 'Saved Full Stack Engineer at StartupXYZ',
    timestamp: new Date('2024-01-16T16:45:00'),
  },
  {
    id: '4',
    type: 'career_bookmarked',
    title: 'Bookmarked Software Engineer career path',
    timestamp: new Date('2024-01-15T09:00:00'),
  },
  {
    id: '5',
    type: 'milestone_achieved',
    title: 'Achieved: First Job Application milestone',
    timestamp: new Date('2024-01-15T11:30:00'),
  },
];

const mockSkills: Skill[] = [
  { id: '1', name: 'JavaScript', level: 'advanced', category: 'Programming', isCore: true, verified: true, progress: 85 },
  { id: '2', name: 'React', level: 'intermediate', category: 'Frameworks', isCore: true, verified: true, progress: 65 },
  { id: '3', name: 'TypeScript', level: 'intermediate', category: 'Programming', isCore: true, verified: false, progress: 55 },
  { id: '4', name: 'Node.js', level: 'beginner', category: 'Backend', isCore: false, verified: false, progress: 30 },
  { id: '5', name: 'Python', level: 'intermediate', category: 'Programming', isCore: false, verified: true, progress: 60 },
];

function StatCard({
  icon: Icon,
  label,
  value,
  change,
  className,
}: {
  icon: React.ElementType;
  label: string;
  value: string | number;
  change?: { value: number; positive: boolean };
  className?: string;
}) {
  return (
    <Card className={className}>
      <CardContent className="p-5">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-muted-foreground">{label}</span>
          <Icon className="h-4 w-4 text-muted-foreground" />
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-semibold">{value}</span>
          {change && (
            <span
              className={cn(
                'text-xs',
                change.positive ? 'text-success' : 'text-destructive'
              )}
            >
              {change.positive ? '+' : ''}{change.value}
            </span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

function MilestoneCard({ milestone }: { milestone: Milestone }) {
  const statusConfig = {
    completed: { icon: CheckCircle2, color: 'text-success', bg: 'bg-success/10' },
    'in-progress': { icon: Clock, color: 'text-primary', bg: 'bg-primary/10' },
    pending: { icon: Circle, color: 'text-muted-foreground', bg: 'bg-muted' },
    overdue: { icon: Clock, color: 'text-destructive', bg: 'bg-destructive/10' },
  };

  const config = statusConfig[milestone.status];
  const Icon = config.icon;

  return (
    <div className="flex items-start gap-3 p-3 rounded-lg border">
      <div className={cn('p-2 rounded-lg', config.bg)}>
        <Icon className={cn('h-4 w-4', config.color)} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between gap-2 mb-1">
          <p className="font-medium text-sm truncate">{milestone.title}</p>
          <Badge
            variant={milestone.status === 'completed' ? 'default' : 'secondary'}
            className="text-xs shrink-0"
          >
            {milestone.status === 'in-progress' ? 'In Progress' : milestone.status}
          </Badge>
        </div>
        <p className="text-xs text-muted-foreground mb-2">{milestone.description}</p>
        {milestone.progress !== undefined && milestone.progress < 100 && (
          <div className="flex items-center gap-2">
            <Progress value={milestone.progress} className="h-1.5 flex-1" />
            <span className="text-xs text-muted-foreground">{milestone.progress}%</span>
          </div>
        )}
        {milestone.dueDate && milestone.status !== 'completed' && (
          <p className="text-xs text-muted-foreground mt-1">
            Due {new Date(milestone.dueDate).toLocaleDateString()}
          </p>
        )}
      </div>
    </div>
  );
}

function ActivityItem({ activity }: { activity: ActivityItem }) {
  const iconMap: Record<string, React.ElementType> = {
    skill_completed: Award,
    application_sent: FileText,
    interview_scheduled: Calendar,
    job_saved: Briefcase,
    career_bookmarked: Star,
    resume_updated: FileText,
    milestone_achieved: Trophy,
  };

  const Icon = iconMap[activity.type] || Circle;

  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    return 'Just now';
  };

  return (
    <div className="flex items-center gap-3 py-2">
      <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center shrink-0">
        <Icon className="h-4 w-4 text-muted-foreground" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm truncate">{activity.title}</p>
        <p className="text-xs text-muted-foreground">{formatTime(activity.timestamp)}</p>
      </div>
    </div>
  );
}

function SkillProgress({ skill }: { skill: Skill }) {
  const levelColors = {
    beginner: 'bg-yellow-500',
    intermediate: 'bg-blue-500',
    advanced: 'bg-green-500',
    expert: 'bg-purple-500',
  };

  return (
    <div className="flex items-center gap-3 py-2">
      <div className="flex-1 min-w-0">
        <div className="flex items-center justify-between mb-1">
          <div className="flex items-center gap-2">
            <p className="text-sm font-medium">{skill.name}</p>
            {skill.verified && (
              <CheckCircle2 className="h-3 w-3 text-success" />
            )}
          </div>
          <Badge variant="secondary" className="text-xs capitalize">
            {skill.level}
          </Badge>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
            <div
              className={cn('h-full rounded-full', levelColors[skill.level])}
              style={{ width: `${skill.progress || 0}%` }}
            />
          </div>
          <span className="text-xs text-muted-foreground w-8">{skill.progress}%</span>
        </div>
      </div>
    </div>
  );
}

export default function Progress() {
  const { user, savedJobs, bookmarkedCareers } = useUserStore();

  const completedMilestones = mockMilestones.filter((m) => m.status === 'completed').length;
  const totalMilestones = mockMilestones.length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold bg-gradient-to-r from-slate-900 via-violet-800 to-slate-900 bg-clip-text text-transparent">Your Progress</h1>
        <p className="text-muted-foreground mt-1">
          Track your career development journey
        </p>
      </div>

      {/* Overview Stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          icon={Trophy}
          label="Milestones"
          value={`${completedMilestones}/${totalMilestones}`}
          change={{ value: 1, positive: true }}
        />
        <StatCard
          icon={Award}
          label="Skills Mastered"
          value={mockSkills.filter((s) => s.progress && s.progress >= 80).length}
          change={{ value: 2, positive: true }}
        />
        <StatCard
          icon={Briefcase}
          label="Applications"
          value={user?.progress.applicationsSubmitted || 0}
        />
        <StatCard
          icon={Calendar}
          label="Interviews"
          value={user?.progress.interviewsScheduled || 0}
        />
      </div>

      {/* Main Content */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left Column - Milestones */}
        <div className="lg:col-span-2 space-y-6">
          {/* Overall Progress */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Career Progress</CardTitle>
              <CardDescription>Your journey to becoming a Software Engineer</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-muted-foreground">Overall completion</span>
                <span className="text-sm font-medium">
                  {Math.round((completedMilestones / totalMilestones) * 100)}%
                </span>
              </div>
              <Progress value={(completedMilestones / totalMilestones) * 100} className="h-2 mb-4" />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>Started</span>
                <span>Skills</span>
                <span>Projects</span>
                <span>Interview</span>
                <span>Job Ready</span>
              </div>
            </CardContent>
          </Card>

          {/* Milestones */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div>
                <CardTitle className="text-base">Milestones</CardTitle>
                <CardDescription>Key achievements on your path</CardDescription>
              </div>
              <Button variant="ghost" size="sm">
                View all
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </CardHeader>
            <CardContent className="space-y-3">
              {mockMilestones.map((milestone) => (
                <MilestoneCard key={milestone.id} milestone={milestone} />
              ))}
            </CardContent>
          </Card>

          {/* Skills Progress */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div>
                <CardTitle className="text-base">Skills Progress</CardTitle>
                <CardDescription>Track your skill development</CardDescription>
              </div>
              <Button variant="ghost" size="sm" asChild>
                <Link to="/skills">
                  Assess skills
                  <ArrowRight className="h-4 w-4 ml-1" />
                </Link>
              </Button>
            </CardHeader>
            <CardContent className="divide-y">
              {mockSkills.map((skill) => (
                <SkillProgress key={skill.id} skill={skill} />
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Right Column - Activity & Summary */}
        <div className="space-y-6">
          {/* Quick Stats */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">This Week</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Skills practiced</span>
                <span className="font-medium">3</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Jobs viewed</span>
                <span className="font-medium">12</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Applications</span>
                <span className="font-medium">2</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Learning time</span>
                <span className="font-medium">4h 30m</span>
              </div>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Recent Activity</CardTitle>
            </CardHeader>
            <CardContent className="divide-y">
              {mockActivities.length > 0 ? (
                mockActivities.map((activity) => (
                  <ActivityItem key={activity.id} activity={activity} />
                ))
              ) : (
                <EmptyState
                  icon={Clock}
                  title="No recent activity"
                  description="Your activity will appear here"
                  className="py-6"
                />
              )}
            </CardContent>
          </Card>

          {/* Saved Items */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base">Saved Items</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between p-3 rounded-lg border">
                <div className="flex items-center gap-2">
                  <Briefcase className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">Saved Jobs</span>
                </div>
                <Badge variant="secondary">{savedJobs.length}</Badge>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg border">
                <div className="flex items-center gap-2">
                  <Target className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">Bookmarked Careers</span>
                </div>
                <Badge variant="secondary">{bookmarkedCareers.length}</Badge>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
