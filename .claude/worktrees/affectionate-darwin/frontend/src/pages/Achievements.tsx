import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Award, Lock, Star, Zap, Target, BookOpen, Briefcase, Brain, Flame, CheckCircle } from 'lucide-react';
import { useUserStore } from '@/store/useUserStore';

interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType<any>;
  category: 'skills' | 'career' | 'learning' | 'jobs';
  unlocked: boolean;
  progress?: number;
  xp: number;
  unlockedDate?: string;
}

const achievements: Achievement[] = [
  {
    id: 'first-skill',
    title: 'First Skill Added',
    description: 'Added your first skill to your profile',
    icon: Star,
    category: 'skills',
    unlocked: true,
    xp: 50,
    unlockedDate: 'Jan 15, 2026',
  },
  {
    id: 'skill-collector',
    title: 'Skill Collector',
    description: 'Added 5 or more skills to your profile',
    icon: Brain,
    category: 'skills',
    unlocked: true,
    xp: 100,
    unlockedDate: 'Feb 3, 2026',
  },
  {
    id: 'career-explorer',
    title: 'Career Explorer',
    description: 'Browsed 10 different career paths',
    icon: Target,
    category: 'career',
    unlocked: true,
    xp: 75,
    unlockedDate: 'Feb 10, 2026',
  },
  {
    id: 'ai-user',
    title: 'AI Advisor',
    description: 'Started your first conversation with the AI Career Assistant',
    icon: Zap,
    category: 'career',
    unlocked: true,
    xp: 50,
    unlockedDate: 'Feb 18, 2026',
  },
  {
    id: 'first-application',
    title: 'First Application',
    description: 'Submitted your first job application',
    icon: Briefcase,
    category: 'jobs',
    unlocked: true,
    xp: 150,
    unlockedDate: 'Mar 1, 2026',
  },
  {
    id: 'learner',
    title: 'Eager Learner',
    description: 'Enrolled in your first course',
    icon: BookOpen,
    category: 'learning',
    unlocked: true,
    xp: 75,
    unlockedDate: 'Mar 5, 2026',
  },
  {
    id: 'streak-7',
    title: '7-Day Streak',
    description: 'Logged in 7 days in a row',
    icon: Flame,
    category: 'career',
    unlocked: false,
    progress: 71,
    xp: 200,
  },
  {
    id: 'job-hunter',
    title: 'Job Hunter',
    description: 'Applied to 10 or more jobs',
    icon: Briefcase,
    category: 'jobs',
    unlocked: false,
    progress: 30,
    xp: 250,
  },
  {
    id: 'skill-master',
    title: 'Skill Master',
    description: 'Verified 5 skills through assessment',
    icon: CheckCircle,
    category: 'skills',
    unlocked: false,
    progress: 40,
    xp: 300,
  },
  {
    id: 'course-completer',
    title: 'Course Completer',
    description: 'Finished your first course 100%',
    icon: Award,
    category: 'learning',
    unlocked: false,
    progress: 72,
    xp: 200,
  },
  {
    id: 'interview-ace',
    title: 'Interview Ace',
    description: 'Reached the interview stage at 3 companies',
    icon: Target,
    category: 'jobs',
    unlocked: false,
    progress: 33,
    xp: 400,
  },
  {
    id: 'pathfinder',
    title: 'Pathfinder',
    description: 'Completed all steps in a career pathway',
    icon: Star,
    category: 'career',
    unlocked: false,
    progress: 42,
    xp: 500,
  },
];

const categoryColors: Record<string, string> = {
  skills: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  career: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  learning: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  jobs: 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20',
};

export default function Achievements() {
  const { user } = useUserStore();

  const unlocked = achievements.filter((a) => a.unlocked);
  const locked = achievements.filter((a) => !a.unlocked);
  const totalXp = unlocked.reduce((acc, a) => acc + a.xp, 0);
  const maxXp = achievements.reduce((acc, a) => acc + a.xp, 0);

  return (
    <div id="achievements-container" className="container mx-auto py-8 px-4 max-w-5xl">
      <motion.div id="achievements-header" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center">
            <Award className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">Achievements</h1>
            <p className="text-muted-foreground">Track your milestones and career progress</p>
          </div>
        </div>
      </motion.div>

      {/* XP Card */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
        <Card id="xp-card" className="border-border/50 mb-8 bg-gradient-to-br from-amber-500/5 to-orange-500/5">
          <CardContent className="pt-6 pb-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm text-muted-foreground">Total XP Earned</p>
                <p className="text-4xl font-bold text-amber-500">{totalXp.toLocaleString()}</p>
                <p className="text-xs text-muted-foreground mt-1">of {maxXp.toLocaleString()} possible</p>
              </div>
              <div id="xp-stats" className="grid grid-cols-2 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold">{unlocked.length}</p>
                  <p className="text-xs text-muted-foreground">Unlocked</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-muted-foreground">{locked.length}</p>
                  <p className="text-xs text-muted-foreground">Remaining</p>
                </div>
              </div>
            </div>
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>Overall Progress</span>
                <span>{Math.round((unlocked.length / achievements.length) * 100)}%</span>
              </div>
              <Progress value={(unlocked.length / achievements.length) * 100} className="h-2" />
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Unlocked Achievements */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="mb-8">
        <h2 id="unlocked-heading" className="text-lg font-semibold mb-4 flex items-center gap-2">
          <CheckCircle className="h-5 w-5 text-emerald-500" />
          Unlocked ({unlocked.length})
        </h2>
        <div id="unlocked-grid" className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {unlocked.map((a) => {
            const Icon = a.icon;
            return (
              <Card key={a.id} id={`achievement-${a.id}`} className="border-emerald-500/20 bg-emerald-500/3">
                <CardContent className="pt-4 pb-4">
                  <div className="flex items-start gap-3">
                    <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 flex items-center justify-center flex-shrink-0">
                      <Icon className="h-5 w-5 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-0.5">
                        <h3 className="font-semibold text-sm">{a.title}</h3>
                        <Badge variant="outline" className="text-xs px-1.5 py-0 text-amber-500 border-amber-500/30">
                          +{a.xp} XP
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">{a.description}</p>
                      {a.unlockedDate && (
                        <p className="text-xs text-emerald-500 mt-1">Earned {a.unlockedDate}</p>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </motion.div>

      {/* Locked Achievements */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
        <h2 id="locked-heading" className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Lock className="h-5 w-5 text-muted-foreground" />
          In Progress ({locked.length})
        </h2>
        <div id="locked-grid" className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {locked.map((a) => {
            const Icon = a.icon;
            return (
              <Card key={a.id} id={`achievement-locked-${a.id}`} className="border-border/50 opacity-80">
                <CardContent className="pt-4 pb-4">
                  <div className="flex items-start gap-3">
                    <div className="h-10 w-10 rounded-xl bg-muted flex items-center justify-center flex-shrink-0">
                      <Icon className="h-5 w-5 text-muted-foreground" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-0.5">
                        <h3 className="font-semibold text-sm text-muted-foreground">{a.title}</h3>
                        <Badge variant="outline" className="text-xs px-1.5 py-0">
                          +{a.xp} XP
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground">{a.description}</p>
                      {a.progress != null && (
                        <div className="mt-2 space-y-1">
                          <div className="flex justify-between text-xs text-muted-foreground">
                            <span>Progress</span>
                            <span>{a.progress}%</span>
                          </div>
                          <Progress value={a.progress} className="h-1.5" />
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </motion.div>
    </div>
  );
}
