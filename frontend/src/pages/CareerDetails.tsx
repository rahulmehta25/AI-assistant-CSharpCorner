import { useParams, Link } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { apiService } from '@/services/api';
import { Career, RoadmapPhase, RoadmapStep } from '@/types';
import { useUserStore } from '@/store/useUserStore';
import { RoadmapSkeleton, CardSkeleton } from '@/components/ui/loading-skeletons';
import { EmptyState } from '@/components/ui/empty-state';
import { ErrorState } from '@/components/ui/error-boundary';
import {
  ArrowLeft,
  Bookmark,
  BookmarkCheck,
  DollarSign,
  TrendingUp,
  GraduationCap,
  Clock,
  CheckCircle2,
  Circle,
  Target,
  ChevronRight,
  BookOpen,
  Briefcase,
  Award
} from 'lucide-react';
import { cn } from '@/lib/utils';

function RoadmapTimeline({ phases, currentPhaseIndex }: { phases: RoadmapPhase[]; currentPhaseIndex: number }) {
  return (
    <div className="space-y-0">
      {phases.map((phase, index) => {
        const isCompleted = phase.status === 'completed';
        const isCurrent = phase.status === 'current';
        const isLast = index === phases.length - 1;

        return (
          <motion.div
            key={phase.id}
            className="relative"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: index * 0.15, ease: [0.25, 0.46, 0.45, 0.94] }}
          >
            {/* Connector line with grow animation */}
            {!isLast && (
              <motion.div
                className={cn(
                  'absolute left-[19px] top-10 w-0.5 h-full -mb-2',
                  isCompleted ? 'bg-primary' : 'bg-border'
                )}
                initial={{ scaleY: 0 }}
                animate={{ scaleY: 1 }}
                transition={{ duration: 0.6, delay: index * 0.15 + 0.2 }}
                style={{ transformOrigin: 'top' }}
              />
            )}

            <div className="flex gap-4 pb-8">
              {/* Status indicator */}
              <div className="relative z-10 flex-shrink-0">
                <motion.div
                  className={cn(
                    'h-10 w-10 rounded-full flex items-center justify-center border-2',
                    isCompleted && 'bg-primary border-primary',
                    isCurrent && 'bg-background border-primary',
                    !isCompleted && !isCurrent && 'bg-background border-border'
                  )}
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ duration: 0.3, delay: index * 0.15 + 0.1, type: 'spring', stiffness: 400, damping: 20 }}
                >
                  {isCompleted ? (
                    <CheckCircle2 className="h-5 w-5 text-primary-foreground" />
                  ) : isCurrent ? (
                    <div className="h-3 w-3 rounded-full bg-primary" />
                  ) : (
                    <Circle className="h-5 w-5 text-muted-foreground" />
                  )}
                </motion.div>
              </div>

              {/* Content */}
              <div className="flex-1 pt-1">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold">{phase.title}</h3>
                      {isCurrent && (
                        <Badge variant="default" className="text-xs">
                          Current
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">{phase.description}</p>
                  </div>
                  <span className="text-xs text-muted-foreground shrink-0 ml-4">
                    {phase.duration}
                  </span>
                </div>

                {/* Steps */}
                <div className="mt-4 space-y-2">
                  {phase.steps.map((step, stepIndex) => (
                    <motion.div
                      key={step.id}
                      className={cn(
                        'flex items-center gap-3 p-3 rounded-lg border',
                        step.completed ? 'bg-muted/50' : 'bg-background'
                      )}
                      initial={{ opacity: 0, x: -12 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.15 + stepIndex * 0.08 + 0.3 }}
                    >
                      {step.completed ? (
                        <CheckCircle2 className="h-4 w-4 text-success shrink-0" />
                      ) : (
                        <Circle className="h-4 w-4 text-muted-foreground shrink-0" />
                      )}
                      <div className="flex-1 min-w-0">
                        <p className={cn('text-sm', step.completed && 'text-muted-foreground')}>
                          {step.title}
                        </p>
                      </div>
                      <Badge variant="secondary" className="text-xs shrink-0">
                        {step.type}
                      </Badge>
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}

function MetricCard({
  icon: Icon,
  label,
  value,
  className
}: {
  icon: React.ElementType;
  label: string;
  value: string;
  className?: string;
}) {
  return (
    <div className={cn('text-center p-4', className)}>
      <Icon className="h-5 w-5 mx-auto mb-2 text-muted-foreground" />
      <p className="text-xs text-muted-foreground mb-1">{label}</p>
      <p className="text-sm font-medium">{value}</p>
    </div>
  );
}

export default function CareerDetails() {
  const { id } = useParams();
  const { bookmarkedCareers, bookmarkCareer, unbookmarkCareer, user } = useUserStore();
  const [career, setCareer] = useState<Career | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [relatedCareers, setRelatedCareers] = useState<Career[]>([]);

  useEffect(() => {
    const fetchCareer = async () => {
      if (!id) return;

      try {
        setLoading(true);
        const careerData = await apiService.getCareer(id);
        setCareer(careerData);

        const allCareers = await apiService.getCareers();
        setRelatedCareers(allCareers.slice(0, 3).filter((c) => c.id !== id));
      } catch (err) {
        setError('Failed to load career details');
        console.error('Error loading career:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchCareer();
  }, [id]);

  const isBookmarked = career ? bookmarkedCareers.some((c) => c.id === career.id) : false;

  const handleBookmark = () => {
    if (!career) return;
    if (isBookmarked) {
      unbookmarkCareer(career.id);
    } else {
      bookmarkCareer(career);
    }
  };

  // Generate roadmap phases based on career and user skills
  const generateRoadmap = (): { phases: RoadmapPhase[]; currentPhaseIndex: number; completionRate: number } => {
    const userSkills = user?.profile.skills?.map((s) => s.name.toLowerCase()) || [];
    const careerSkills = career?.skills?.map((s) => s.toLowerCase()) || [];
    const matchedSkills = careerSkills.filter((skill) =>
      userSkills.some((us) => us.includes(skill))
    );
    const completionRate = careerSkills.length > 0
      ? Math.round((matchedSkills.length / careerSkills.length) * 100)
      : 0;

    const phases: RoadmapPhase[] = [
      {
        id: '1',
        title: 'Foundation',
        description: 'Build core technical skills and fundamentals',
        duration: '3-4 months',
        status: completionRate >= 25 ? 'completed' : completionRate > 0 ? 'current' : 'upcoming',
        steps: [
          { id: '1-1', title: 'Complete fundamentals assessment', description: '', type: 'skill', completed: completionRate >= 10, resources: [] },
          { id: '1-2', title: career?.skills?.[0] || 'Core skill 1', description: '', type: 'skill', completed: matchedSkills.length >= 1, resources: [] },
          { id: '1-3', title: career?.skills?.[1] || 'Core skill 2', description: '', type: 'skill', completed: matchedSkills.length >= 2, resources: [] },
        ],
      },
      {
        id: '2',
        title: 'Development',
        description: 'Advance your skills through hands-on projects',
        duration: '4-6 months',
        status: completionRate >= 50 ? 'completed' : completionRate >= 25 ? 'current' : 'upcoming',
        steps: [
          { id: '2-1', title: 'Build portfolio project', description: '', type: 'experience', completed: completionRate >= 35, resources: [] },
          { id: '2-2', title: career?.skills?.[2] || 'Advanced skill 1', description: '', type: 'skill', completed: matchedSkills.length >= 3, resources: [] },
          { id: '2-3', title: career?.skills?.[3] || 'Advanced skill 2', description: '', type: 'skill', completed: matchedSkills.length >= 4, resources: [] },
        ],
      },
      {
        id: '3',
        title: 'Specialization',
        description: 'Gain industry-specific expertise and certifications',
        duration: '3-4 months',
        status: completionRate >= 75 ? 'completed' : completionRate >= 50 ? 'current' : 'upcoming',
        steps: [
          { id: '3-1', title: 'Industry certification', description: '', type: 'certification', completed: completionRate >= 60, resources: [] },
          { id: '3-2', title: 'Complete internship or freelance work', description: '', type: 'experience', completed: completionRate >= 70, resources: [] },
        ],
      },
      {
        id: '4',
        title: 'Job Ready',
        description: 'Prepare for job applications and interviews',
        duration: '2-3 months',
        status: completionRate >= 100 ? 'completed' : completionRate >= 75 ? 'current' : 'upcoming',
        steps: [
          { id: '4-1', title: 'Update resume and portfolio', description: '', type: 'skill', completed: completionRate >= 85, resources: [] },
          { id: '4-2', title: 'Practice technical interviews', description: '', type: 'skill', completed: completionRate >= 90, resources: [] },
          { id: '4-3', title: 'Apply to target companies', description: '', type: 'experience', completed: completionRate >= 100, resources: [] },
        ],
      },
    ];

    const currentPhaseIndex = phases.findIndex((p) => p.status === 'current');

    return { phases, currentPhaseIndex, completionRate };
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <div className="h-8 w-24 bg-muted rounded animate-pulse" />
          <div className="h-8 w-24 bg-muted rounded animate-pulse" />
        </div>
        <div className="h-10 w-64 bg-muted rounded animate-pulse" />
        <div className="h-6 w-96 bg-muted rounded animate-pulse" />
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      </div>
    );
  }

  if (error || !career) {
    return (
      <ErrorState
        title="Career Not Found"
        description={error || 'The career you are looking for could not be found.'}
        onRetry={() => window.location.reload()}
      />
    );
  }

  const { phases, currentPhaseIndex, completionRate } = generateRoadmap();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" asChild>
          <Link to="/careers">
            <ArrowLeft className="h-4 w-4 mr-1" />
            Careers
          </Link>
        </Button>
        <Button
          variant={isBookmarked ? 'default' : 'outline'}
          size="sm"
          onClick={handleBookmark}
        >
          {isBookmarked ? (
            <BookmarkCheck className="h-4 w-4 mr-1" />
          ) : (
            <Bookmark className="h-4 w-4 mr-1" />
          )}
          {isBookmarked ? 'Saved' : 'Save'}
        </Button>
      </div>

      {/* Title & Description */}
      <div>
        <div className="flex items-center gap-3 mb-2">
          <h1 className="text-2xl font-semibold bg-gradient-to-r from-slate-900 via-violet-800 to-slate-900 bg-clip-text text-transparent">{career.title}</h1>
          {career.match && (
            <Badge variant="secondary">{career.match}% match</Badge>
          )}
        </div>
        <p className="text-muted-foreground">{career.description}</p>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <MetricCard
            icon={DollarSign}
            label="Salary Range"
            value={`$${Math.round(career.salary.min / 1000)}k - $${Math.round(career.salary.max / 1000)}k`}
          />
        </Card>
        <Card>
          <MetricCard icon={TrendingUp} label="Growth" value={career.growth} />
        </Card>
        <Card>
          <MetricCard icon={GraduationCap} label="Education" value={career.education} />
        </Card>
        <Card>
          <MetricCard icon={Briefcase} label="Experience" value={career.experience} />
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="roadmap" className="space-y-6">
        <TabsList>
          <TabsTrigger value="roadmap">Your Roadmap</TabsTrigger>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="skills">Skills</TabsTrigger>
          <TabsTrigger value="related">Related</TabsTrigger>
        </TabsList>

        <TabsContent value="roadmap" className="space-y-6">
          {/* Roadmap Progress */}
          <Card>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-base">Career Progress</CardTitle>
                  <CardDescription>
                    Your personalized path to {career.title}
                  </CardDescription>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-semibold">{completionRate}%</div>
                  <p className="text-xs text-muted-foreground">Complete</p>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <Progress value={completionRate} className="h-2" />
              <div className="flex justify-between mt-2 text-xs text-muted-foreground">
                <span>Foundation</span>
                <span>Development</span>
                <span>Specialization</span>
                <span>Job Ready</span>
              </div>
            </CardContent>
          </Card>

          {/* Timeline */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Roadmap Timeline</CardTitle>
              <CardDescription>
                Estimated time: 12-18 months depending on your pace
              </CardDescription>
            </CardHeader>
            <CardContent>
              <RoadmapTimeline phases={phases} currentPhaseIndex={currentPhaseIndex} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Daily Tasks</CardTitle>
                <CardDescription>What you'll do in this role</CardDescription>
              </CardHeader>
              <CardContent>
                {career.tasks && career.tasks.length > 0 ? (
                  <ul className="space-y-3">
                    {career.tasks.map((task, index) => (
                      <li key={index} className="flex items-start gap-3">
                        <CheckCircle2 className="h-4 w-4 text-success mt-0.5 shrink-0" />
                        <span className="text-sm text-muted-foreground">{task}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-muted-foreground">Task details coming soon</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Work Environment</CardTitle>
                <CardDescription>What to expect</CardDescription>
              </CardHeader>
              <CardContent>
                {career.work_environment && career.work_environment.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {career.work_environment.map((env) => (
                      <Badge key={env} variant="secondary">
                        {env}
                      </Badge>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">Environment details coming soon</p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="skills" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Required Skills</CardTitle>
              <CardDescription>
                Skills needed for this career path
              </CardDescription>
            </CardHeader>
            <CardContent>
              {career.skills && career.skills.length > 0 ? (
                <div className="space-y-2">
                  {career.skills.map((skill) => {
                    const userHasSkill = user?.profile.skills?.some((s) =>
                      s.name.toLowerCase().includes(skill.toLowerCase())
                    );
                    return (
                      <div
                        key={skill}
                        className="flex items-center justify-between p-3 rounded-lg border"
                      >
                        <span className="text-sm">{skill}</span>
                        {userHasSkill ? (
                          <Badge variant="default" className="text-xs">
                            <CheckCircle2 className="h-3 w-3 mr-1" />
                            Acquired
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="text-xs">
                            To learn
                          </Badge>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">Skills data coming soon</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="related" className="space-y-6">
          {relatedCareers.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {relatedCareers.map((related) => (
                <Card key={related.id} className="hover:bg-muted/50 transition-colors">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base">{related.title}</CardTitle>
                    <CardDescription className="line-clamp-2">
                      {related.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between text-sm mb-3">
                      <span className="text-muted-foreground">
                        ${Math.round(related.salary.min / 1000)}k - ${Math.round(related.salary.max / 1000)}k
                      </span>
                      <Badge variant="secondary">{related.growth}</Badge>
                    </div>
                    <Button variant="outline" size="sm" className="w-full" asChild>
                      <Link to={`/careers/${related.id}`}>
                        View Details
                        <ChevronRight className="h-4 w-4 ml-1" />
                      </Link>
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <EmptyState
              icon={Briefcase}
              title="No related careers"
              description="Related career suggestions will appear here."
            />
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
