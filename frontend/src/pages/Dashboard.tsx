import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { StatsCard } from '@/components/dashboard/StatsCard';
import { CareerCard } from '@/components/careers/CareerCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
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
  BookOpen
} from 'lucide-react';
import { useUserStore } from '@/store/useUserStore';
import { apiService } from '@/services/api';
import { Career, Job } from '@/types';
import { Link } from 'react-router-dom';

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
};

export default function Dashboard() {
  const { user } = useUserStore();
  const [careers, setCareers] = useState<Career[]>([]);
  const [loadingCareers, setLoadingCareers] = useState(true);

  useEffect(() => {
    const fetchCareers = async () => {
      try {
        const data = await apiService.getCareers();
        setCareers(data.slice(0, 3)); // Get top 3 careers
      } catch (error) {
        console.error('Error loading careers:', error);
      } finally {
        setLoadingCareers(false);
      }
    };

    fetchCareers();
  }, []);

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <h2 className="text-2xl font-semibold mb-2">Welcome to AI Career Assistant</h2>
          <p className="text-muted-foreground">Please sign in to access your dashboard.</p>
        </div>
      </div>
    );
  }

  // Mock jobs data for now (since jobs endpoint doesn't exist yet)
  const recentJobs: Job[] = [
    {
      id: '1',
      title: 'Frontend Developer',
      company: 'TechCorp',
      location: 'San Francisco, CA',
      salary: '$90,000 - $120,000',
      type: 'full-time',
      description: 'Build amazing user interfaces with React and TypeScript.',
      requirements: ['3+ years React experience', 'TypeScript proficiency', 'CSS expertise'],
      benefits: ['Health insurance', '401k matching', 'Flexible PTO'],
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
      salary: '$80,000 - $110,000',
      type: 'full-time',
      description: 'Work on both frontend and backend systems using modern technologies.',
      requirements: ['JavaScript/TypeScript', 'Node.js', 'Database design', 'API development'],
      benefits: ['Remote work', 'Stock options', 'Learning budget'],
      match: 89,
      postedDate: '2024-01-12',
      applied: true,
      saved: true,
      source: 'Indeed',
    },
    {
      id: '3',
      title: 'Software Engineering Intern',
      company: 'BigTech Inc',
      location: 'Seattle, WA',
      salary: '$35/hour',
      type: 'internship',
      description: 'Summer internship program for computer science students.',
      requirements: ['CS major', 'Programming skills', 'Problem-solving abilities'],
      benefits: ['Mentorship', 'Housing stipend', 'Return offer potential'],
      match: 87,
      postedDate: '2024-01-10',
      applied: false,
      saved: true,
      source: 'Company Website',
    }
  ];

  const milestones = [
    {
      title: 'Complete Skills Assessment',
      type: 'assessment',
      dueDate: '2024-01-20',
      status: 'completed' as const,
      description: 'Identify your key strengths and areas for improvement'
    },
    {
      title: 'Apply to Software Engineer Role',
      type: 'application',
      dueDate: '2024-01-25',
      status: 'in-progress' as const,
      description: 'TechCorp - Frontend Developer position'
    },
    {
      title: 'Complete React Course',
      type: 'learning',
      dueDate: '2024-02-01',
      status: 'upcoming' as const,
      description: 'Advanced React patterns and best practices'
    },
    {
      title: 'Update Portfolio',
      type: 'portfolio',
      dueDate: '2024-02-05',
      status: 'upcoming' as const,
      description: 'Add recent projects and testimonials'
    }
  ];

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Welcome Section */}
      <motion.div variants={itemVariants} className="space-y-2">
        <h1 className="text-3xl font-bold">
          Welcome back, {user.name.split(' ')[0]}! 👋
        </h1>
        <p className="text-muted-foreground text-lg">
          Let's continue building your career path. Here's your progress overview.
        </p>
      </motion.div>

      {/* Stats Grid */}
      <motion.div variants={itemVariants} className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Career Match"
          value={`${user.progress.careerMatch}%`}
          progress={user.progress.careerMatch}
          change={{ value: 5, trend: 'up' }}
          icon={<Target className="h-4 w-4" />}
          variant="success"
          description="Based on your skills and interests"
        />
        <StatsCard
          title="Skills Completed"
          value={user.progress.skillsCompleted}
          change={{ value: 2, trend: 'up' }}
          icon={<Award className="h-4 w-4" />}
          description="New skills learned this month"
        />
        <StatsCard
          title="Applications"
          value={user.progress.applicationsSubmitted}
          icon={<Briefcase className="h-4 w-4" />}
          description="Submitted this month"
        />
        <StatsCard
          title="Profile Completion"
          value={`${user.progress.profileCompletion}%`}
          progress={user.progress.profileCompletion}
          icon={<TrendingUp className="h-4 w-4" />}
          variant="warning"
          description="Complete your profile for better matches"
        />
      </motion.div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Top Career Matches */}
        <motion.div variants={itemVariants}>
          <Card>
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
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary mx-auto mb-2"></div>
                  <p className="text-sm text-muted-foreground">Loading careers...</p>
                </div>
              ) : (
                careers.map((career) => (
                  <CareerCard key={career.id} career={career} compact showMatch />
                ))
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Recent Job Recommendations */}
        <motion.div variants={itemVariants}>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-xl">Recent Job Matches</CardTitle>
              <Button variant="ghost" size="sm" asChild>
                <Link to="/jobs">
                  View All
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
            </CardHeader>
            <CardContent className="space-y-4">
              {recentJobs.map((job) => (
                <div
                  key={job.id}
                  className="flex items-start space-x-4 p-4 rounded-lg border hover:bg-muted/50 transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-medium truncate">{job.title}</h4>
                      {job.match && (
                        <Badge variant="outline" className="text-xs">
                          {job.match}% match
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">{job.company}</p>
                    <p className="text-sm text-muted-foreground">{job.location}</p>
                    {job.salary && (
                      <p className="text-sm font-medium text-primary">{job.salary}</p>
                    )}
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Upcoming Milestones */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-xl flex items-center">
              <Calendar className="mr-2 h-5 w-5" />
              Upcoming Milestones
            </CardTitle>
            <Button variant="ghost" size="sm">
              Manage Timeline
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {milestones.map((milestone, index) => (
                <div
                  key={index}
                  className="flex items-start space-x-4 p-4 rounded-lg border"
                >
                  <div className="flex-shrink-0 mt-1">
                    {milestone.status === 'completed' ? (
                      <CheckCircle className="h-5 w-5 text-success" />
                    ) : milestone.status === 'in-progress' ? (
                      <Clock className="h-5 w-5 text-warning" />
                    ) : (
                      <div className="h-5 w-5 rounded-full border-2 border-muted" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-medium">{milestone.title}</h4>
                      <Badge
                        variant={
                          milestone.status === 'completed'
                            ? 'default'
                            : milestone.status === 'in-progress'
                            ? 'secondary'
                            : 'outline'
                        }
                        className="text-xs"
                      >
                        {milestone.status.replace('-', ' ')}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-1">
                      {milestone.description}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Due: {new Date(milestone.dueDate).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Quick Actions */}
      <motion.div variants={itemVariants}>
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <Button variant="outline" className="h-20 flex-col space-y-2" asChild>
                <Link to="/skills">
                  <Target className="h-6 w-6" />
                  <span>Assess Skills</span>
                </Link>
              </Button>
              <Button variant="outline" className="h-20 flex-col space-y-2" asChild>
                <Link to="/careers">
                  <TrendingUp className="h-6 w-6" />
                  <span>Explore Careers</span>
                </Link>
              </Button>
              <Button variant="outline" className="h-20 flex-col space-y-2" asChild>
                <Link to="/jobs">
                  <Briefcase className="h-6 w-6" />
                  <span>Find Jobs</span>
                </Link>
              </Button>
              <Button variant="outline" className="h-20 flex-col space-y-2" asChild>
                <Link to="/applications">
                  <BookOpen className="h-6 w-6" />
                  <span>Build Resume</span>
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
}