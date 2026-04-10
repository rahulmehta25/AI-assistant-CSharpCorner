import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { StatsCard } from '@/components/dashboard/StatsCard';
import { CareerCard } from '@/components/careers/CareerCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Target,
  Briefcase,
  TrendingUp,
  Award,
  ArrowRight,
  Calendar,
  CheckCircle,
  Clock,
  BookOpen,
} from 'lucide-react';
import { useUserStore } from '@/store/useUserStore';
import { apiService } from '@/services/api';
import { Career, Job } from '@/types';
import { Link } from 'react-router-dom';
import { addDays, format } from 'date-fns';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.1 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

function getDynamicDate(daysFromNow: number): string {
  return format(addDays(new Date(), daysFromNow), 'yyyy-MM-dd');
}

function getRecentJobs(): Job[] {
  const today = new Date();
  return [
    {
      id: '1',
      title: 'Frontend Developer',
      company: 'TechCorp',
      location: 'San Francisco, CA',
      salary: '$95,000 – $125,000',
      type: 'full-time',
      description: 'Build amazing user interfaces with React and TypeScript.',
      requirements: ['3+ years React experience', 'TypeScript proficiency', 'CSS expertise'],
      benefits: ['Health insurance', '401k matching', 'Flexible PTO'],
      match: 94,
      postedDate: format(addDays(today, -2), 'yyyy-MM-dd'),
      applied: false,
      saved: false,
      source: 'LinkedIn',
    },
    {
      id: '2',
      title: 'Full Stack Engineer',
      company: 'StartupXYZ',
      location: 'Remote',
      salary: '$85,000 – $115,000',
      type: 'full-time',
      description: 'Work on both frontend and backend systems using modern technologies.',
      requirements: ['JavaScript/TypeScript', 'Node.js', 'Database design', 'API development'],
      benefits: ['Remote work', 'Stock options', 'Learning budget'],
      match: 89,
      postedDate: format(addDays(today, -5), 'yyyy-MM-dd'),
      applied: true,
      saved: true,
      source: 'Indeed',
    },
    {
      id: '3',
      title: 'Software Engineer – AI Products',
      company: 'AIFirst Inc',
      location: 'New York, NY',
      salary: '$110,000 – $145,000',
      type: 'full-time',
      description: 'Build AI-powered features and work with LLM integrations.',
      requirements: ['Python or TypeScript', 'API integration experience', 'Interest in AI/ML'],
      benefits: ['Equity', 'Mentorship', 'Conference budget'],
      match: 82,
      postedDate: format(addDays(today, -7), 'yyyy-MM-dd'),
      applied: false,
      saved: true,
      source: 'Company Website',
    },
  ];
}

function getMilestones() {
  return [
    {
      title: 'Complete Skills Assessment',
      type: 'assessment',
      dueDate: getDynamicDate(3),
      status: 'in-progress' as const,
      description: 'Identify your key strengths and areas for improvement',
    },
    {
      title: 'Apply to 5 Target Roles',
      type: 'application',
      dueDate: getDynamicDate(10),
      status: 'upcoming' as const,
      description: 'Focus on roles that match your top skills',
    },
    {
      title: 'Complete React Advanced Course',
      type: 'learning',
      dueDate: getDynamicDate(30),
      status: 'upcoming' as const,
      description: 'Advanced React patterns and best practices',
    },
    {
      title: 'Update Portfolio with 2 New Projects',
      type: 'portfolio',
      dueDate: getDynamicDate(45),
      status: 'upcoming' as const,
      description: 'Add recent projects and testimonials',
    },
  ];
}

export default function Dashboard() {
  const { user } = useUserStore();
  const [careers, setCareers] = useState<Career[]>([]);
  const [loadingCareers, setLoadingCareers] = useState(true);

  useEffect(() => {
    const fetchCareers = async () => {
      try {
        const data = await apiService.getCareers();
        setCareers(data.slice(0, 3));
      } catch (error) {
        console.error('Error loading careers:', error);
      } finally {
        setLoadingCareers(false);
      }
    };
    fetchCareers();
  }, []);

  const recentJobs: Job[] = getRecentJobs();
  const milestones = getMilestones();

  return (
    <motion.div
      id="dashboard-container"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Welcome Section */}
      <motion.div id="dashboard-welcome" variants={itemVariants} className="space-y-1">
        <h1 className="text-3xl font-bold">
          Welcome back, {user?.name?.split(' ')[0] ?? 'there'}!
        </h1>
        <p className="text-muted-foreground text-lg">
          Here's your career progress overview.
        </p>
      </motion.div>

      {/* Stats Grid */}
      <motion.div id="dashboard-stats" variants={itemVariants} className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Career Match"
          value={`${user?.progress?.careerMatch ?? 85}%`}
          progress={user?.progress?.careerMatch ?? 85}
          change={{ value: 5, trend: 'up' }}
          icon={<Target className="h-4 w-4" />}
          variant="success"
          description="Based on your skills and interests"
        />
        <StatsCard
          title="Skills Completed"
          value={user?.progress?.skillsCompleted ?? 12}
          change={{ value: 2, trend: 'up' }}
          icon={<Award className="h-4 w-4" />}
          description="New skills learned this month"
        />
        <StatsCard
          title="Applications"
          value={user?.progress?.applicationsSubmitted ?? 3}
          icon={<Briefcase className="h-4 w-4" />}
          description="Submitted this month"
        />
        <StatsCard
          title="Profile Completion"
          value={`${user?.progress?.profileCompletion ?? 78}%`}
          progress={user?.progress?.profileCompletion ?? 78}
          icon={<TrendingUp className="h-4 w-4" />}
          variant="warning"
          description="Complete your profile for better matches"
        />
      </motion.div>

      <div id="dashboard-main-grid" className="grid gap-6 lg:grid-cols-2">
        {/* Top Career Matches */}
        <motion.div id="career-matches-section" variants={itemVariants}>
          <Card className="border-border/50">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-xl">Top Career Matches</CardTitle>
              <Button variant="ghost" size="sm" asChild>
                <Link to="/careers">
                  View All
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </CardHeader>
            <CardContent className="space-y-4">
              {loadingCareers ? (
                <div id="careers-skeleton" className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-16 rounded-lg bg-muted animate-pulse" />
                  ))}
                </div>
              ) : careers.length > 0 ? (
                careers.map((career) => (
                  <CareerCard key={career.id} career={career} compact showMatch />
                ))
              ) : (
                <div id="careers-empty" className="text-center py-8 text-muted-foreground">
                  <Briefcase className="h-8 w-8 mx-auto mb-2 opacity-30" />
                  <p className="text-sm">No careers loaded yet.</p>
                  <Button variant="link" size="sm" asChild>
                    <Link to="/careers">Browse all careers</Link>
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Recent Job Recommendations */}
        <motion.div id="job-matches-section" variants={itemVariants}>
          <Card className="border-border/50">
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-xl">Recent Job Matches</CardTitle>
              <Button variant="ghost" size="sm" asChild>
                <Link to="/jobs">
                  View All
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </CardHeader>
            <CardContent className="space-y-3">
              {recentJobs.map((job) => (
                <div
                  key={job.id}
                  id={`job-card-${job.id}`}
                  className="flex items-start space-x-4 p-4 rounded-lg border border-border/50 hover:bg-muted/30 transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-medium truncate">{job.title}</h4>
                      {job.match != null && (
                        <Badge
                          variant="outline"
                          className={`text-xs ml-2 flex-shrink-0 ${
                            job.match >= 90
                              ? 'border-emerald-500/30 text-emerald-500'
                              : job.match >= 80
                              ? 'border-blue-500/30 text-blue-400'
                              : 'border-border'
                          }`}
                        >
                          {job.match}% match
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">{job.company}</p>
                    <div className="flex items-center gap-3 mt-1">
                      <p className="text-xs text-muted-foreground">{job.location}</p>
                      {job.salary && (
                        <p className="text-xs font-medium text-primary">{job.salary}</p>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      Posted {new Date(job.postedDate).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Upcoming Milestones */}
      <motion.div id="milestones-section" variants={itemVariants}>
        <Card className="border-border/50">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-xl flex items-center">
              <Calendar className="mr-2 h-5 w-5" />
              Upcoming Milestones
            </CardTitle>
            <Button variant="ghost" size="sm" asChild>
              <Link to="/pathways">
                View Pathways
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent>
            <div id="milestones-list" className="grid gap-3 sm:grid-cols-2">
              {milestones.map((milestone, index) => (
                <div
                  key={index}
                  id={`milestone-${index}`}
                  className="flex items-start space-x-3 p-4 rounded-lg border border-border/50"
                >
                  <div className="flex-shrink-0 mt-0.5">
                    {milestone.status === 'completed' ? (
                      <CheckCircle className="h-5 w-5 text-emerald-500" />
                    ) : milestone.status === 'in-progress' ? (
                      <Clock className="h-5 w-5 text-amber-500" />
                    ) : (
                      <div className="h-5 w-5 rounded-full border-2 border-muted-foreground/30" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-0.5">
                      <h4 className="font-medium text-sm">{milestone.title}</h4>
                    </div>
                    <p className="text-xs text-muted-foreground mb-1">{milestone.description}</p>
                    <p className="text-xs text-muted-foreground">
                      Due:{' '}
                      <span className={milestone.status === 'in-progress' ? 'text-amber-500 font-medium' : ''}>
                        {new Date(milestone.dueDate).toLocaleDateString()}
                      </span>
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Quick Actions */}
      <motion.div id="quick-actions-section" variants={itemVariants}>
        <Card className="border-border/50">
          <CardHeader>
            <CardTitle className="text-xl">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div id="quick-actions-grid" className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
              <Button id="qa-skills" variant="outline" className="h-20 flex-col space-y-2 border-border/50 hover:border-primary/30" asChild>
                <Link to="/skills">
                  <Target className="h-6 w-6" />
                  <span>Assess Skills</span>
                </Link>
              </Button>
              <Button id="qa-careers" variant="outline" className="h-20 flex-col space-y-2 border-border/50 hover:border-primary/30" asChild>
                <Link to="/careers">
                  <TrendingUp className="h-6 w-6" />
                  <span>Explore Careers</span>
                </Link>
              </Button>
              <Button id="qa-jobs" variant="outline" className="h-20 flex-col space-y-2 border-border/50 hover:border-primary/30" asChild>
                <Link to="/jobs">
                  <Briefcase className="h-6 w-6" />
                  <span>Find Jobs</span>
                </Link>
              </Button>
              <Button id="qa-assistant" variant="outline" className="h-20 flex-col space-y-2 border-border/50 hover:border-primary/30" asChild>
                <Link to="/assistant">
                  <BookOpen className="h-6 w-6" />
                  <span>AI Assistant</span>
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}
