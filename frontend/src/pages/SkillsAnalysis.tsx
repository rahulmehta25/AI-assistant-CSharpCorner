import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { SkillRadarChart, type SkillData } from '@/components/ui/skill-radar-chart';
import { ResumeStrengthMeter } from '@/components/ui/resume-strength-meter';
import { SkeletonCard } from '@/components/ui/skeleton-card';
import { useUserStore } from '@/store/useUserStore';
import { Brain, Target, TrendingUp, BookOpen, Award, Plus, CheckCircle, Star } from 'lucide-react';

const container = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.08 } },
};
const item = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' as const } },
};

const skillGaps = [
  {
    skill: 'Advanced React',
    currentLevel: 'Intermediate', requiredLevel: 'Advanced',
    progress: 60, gap: 40, priority: 'High',
    learningPath: ['Advanced Patterns', 'Performance', 'Testing'],
  },
  {
    skill: 'System Design',
    currentLevel: 'Beginner', requiredLevel: 'Intermediate',
    progress: 35, gap: 65, priority: 'High',
    learningPath: ['Scalability', 'Database Design', 'API Architecture'],
  },
  {
    skill: 'DevOps / CI-CD',
    currentLevel: 'Beginner', requiredLevel: 'Intermediate',
    progress: 25, gap: 75, priority: 'Medium',
    learningPath: ['Docker Basics', 'GitHub Actions', 'AWS Fundamentals'],
  },
];

const recommendations = [
  { title: 'Advanced React Patterns', provider: 'Frontend Masters', duration: '6 weeks', cost: 'Paid', rating: 4.8, priority: 'High', tag: 'React' },
  { title: 'System Design Interview', provider: 'Educative', duration: '4 weeks', cost: 'Paid', rating: 4.7, priority: 'High', tag: 'Architecture' },
  { title: 'AWS Cloud Practitioner', provider: 'AWS Training', duration: '3 weeks', cost: 'Free', rating: 4.6, priority: 'Medium', tag: 'Cloud' },
];

const historyItems = [
  { date: 'Jan 15, 2025', skill: 'React', milestone: 'Completed Advanced React Course', type: 'completed' },
  { date: 'Jan 10, 2025', skill: 'Python', milestone: 'Started Data Analysis Path', type: 'started' },
  { date: 'Jan 5, 2025',  skill: 'JavaScript', milestone: 'Verified ES6+ Knowledge', type: 'verified' },
];

const levelValue = (level: string) =>
  ({ expert: 92, advanced: 78, intermediate: 55, beginner: 32 }[level.toLowerCase()] ?? 40);

function getLevelColor(level: string) {
  const map: Record<string, string> = {
    expert:       'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    advanced:     'bg-blue-500/10 text-blue-400 border-blue-500/20',
    intermediate: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    beginner:     'bg-muted/60 text-muted-foreground border-border/60',
  };
  return map[level.toLowerCase()] ?? map['beginner'];
}

function getLevelBg(level: string) {
  const map: Record<string, string> = {
    expert:       'bg-emerald-500/10',
    advanced:     'bg-blue-500/10',
    intermediate: 'bg-amber-500/10',
    beginner:     'bg-muted/60',
  };
  return map[level.toLowerCase()] ?? 'bg-muted/60';
}

function getLevelText(level: string) {
  const map: Record<string, string> = {
    expert:       'text-emerald-400',
    advanced:     'text-blue-400',
    intermediate: 'text-amber-400',
    beginner:     'text-muted-foreground',
  };
  return map[level.toLowerCase()] ?? 'text-muted-foreground';
}

function getPriorityColor(priority: string) {
  const map: Record<string, string> = {
    high:   'bg-red-500/10 text-red-400 border-red-500/20',
    medium: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    low:    'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  };
  return map[priority.toLowerCase()] ?? '';
}

export default function SkillsAnalysis() {
  const { user } = useUserStore();
  const isLoading = user === null;

  const technicalSkills = user?.profile.skills ?? [];
  const softSkills = [
    { id: 'comm', name: 'Communication',   level: 'advanced',     category: 'Soft', isCore: true, verified: true  },
    { id: 'lead', name: 'Leadership',      level: 'intermediate', category: 'Soft', isCore: true, verified: false },
    { id: 'prob', name: 'Problem Solving', level: 'advanced',     category: 'Soft', isCore: true, verified: true  },
    { id: 'col',  name: 'Collaboration',   level: 'advanced',     category: 'Soft', isCore: true, verified: true  },
  ];

  const radarData: SkillData[] = technicalSkills.length > 0
    ? technicalSkills.slice(0, 6).map((s) => ({ subject: s.name, score: levelValue(s.level) }))
    : [
        { subject: 'React',      score: 78 },
        { subject: 'TypeScript', score: 65 },
        { subject: 'Node.js',    score: 55 },
        { subject: 'Python',     score: 40 },
        { subject: 'SQL',        score: 62 },
        { subject: 'DevOps',     score: 30 },
      ];

  const profileScore = Math.min(100, Math.round(
    (technicalSkills.length / 10) * 50 +
    (technicalSkills.filter((s) => s.verified).length / Math.max(1, technicalSkills.length)) * 30 +
    20
  ));

  return (
    <motion.div
      id="skills-container"
      variants={container}
      initial="hidden"
      animate="visible"
      className="space-y-6 max-w-7xl"
    >
      {/* ── Header ──────────────────────────────────────── */}
      <motion.div id="skills-header" variants={item}>
        <div className="flex items-center gap-3 mb-1">
          <div className="h-10 w-10 rounded-xl bg-blue-500/15 flex items-center justify-center">
            <Brain className="h-5 w-5 text-blue-400" />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold tracking-tight text-gradient-primary">
              Skills Analysis
            </h1>
            <p className="text-sm text-muted-foreground">
              Visualize your skills, identify gaps, and get learning recommendations
            </p>
          </div>
        </div>
      </motion.div>

      {isLoading && (
        <motion.div id="skills-loading-skeleton" variants={item} className="space-y-4" aria-label="Loading skills data" aria-busy="true">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-24 rounded-xl bg-muted animate-pulse" aria-hidden="true" />
            ))}
          </div>
          <div className="h-64 rounded-xl bg-muted animate-pulse" aria-hidden="true" />
        </motion.div>
      )}

      <Tabs defaultValue="overview" aria-label="Skills analysis sections" className="space-y-5">
        <motion.div variants={item}>
          <TabsList className="grid w-full grid-cols-4 bg-muted/40 border border-border/50">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="gaps">Skill Gaps</TabsTrigger>
            <TabsTrigger value="recommendations">Learn</TabsTrigger>
            <TabsTrigger value="progress">History</TabsTrigger>
          </TabsList>
        </motion.div>

        {/* ── Overview tab ──────────────────────────────── */}
        <TabsContent value="overview" className="space-y-5">
          {/* Stat strip */}
          <motion.div variants={item} className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Total Skills', value: technicalSkills.length || 8, icon: Award,     color: 'text-primary', bg: 'bg-primary/10'   },
              { label: 'Verified',     value: technicalSkills.filter(s => s.verified).length || 4, icon: CheckCircle, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
              { label: 'Skill Gaps',   value: skillGaps.length, icon: TrendingUp, color: 'text-amber-400', bg: 'bg-amber-500/10' },
              { label: 'Study Hours',  value: 24, icon: BookOpen, color: 'text-violet-400', bg: 'bg-violet-500/10' },
            ].map(({ label, value, icon: Icon, color, bg }) => (
              <Card key={label} className="border-border/50 bg-card/80">
                <CardContent className="pt-4 pb-4">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-xs font-semibold text-muted-foreground">{label}</p>
                    <div className={`h-8 w-8 rounded-lg ${bg} flex items-center justify-center`}>
                      <Icon className={`h-4 w-4 ${color}`} />
                    </div>
                  </div>
                  <p className="text-3xl font-extrabold">{value}</p>
                </CardContent>
              </Card>
            ))}
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-5 gap-5">
            {/* Radar chart */}
            <motion.div variants={item} className="lg:col-span-3">
              <Card className="border-border/50 bg-card/80 h-full">
                <CardHeader className="pb-2">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Target className="h-4 w-4 text-primary" />
                    Skill Radar
                  </CardTitle>
                  <CardDescription className="text-xs">
                    Visual breakdown of your skill levels across domains
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <SkillRadarChart data={radarData} height={300} />
                </CardContent>
              </Card>
            </motion.div>

            {/* Skill lists */}
            <motion.div variants={item} className="lg:col-span-2 space-y-4">
              {/* Resume strength */}
              <Card className="border-border/50 bg-card/80">
                <CardContent className="pt-4 pb-4">
                  <ResumeStrengthMeter score={profileScore} />
                </CardContent>
              </Card>

              {/* Technical skills */}
              <Card id="technical-skills-card" className="border-border/50 bg-card/80">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm">Technical Skills</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {technicalSkills.length > 0 ? (
                    technicalSkills.slice(0, 5).map((skill) => (
                      <div
                        key={skill.id}
                        className="flex items-center justify-between p-2.5 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors"
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-foreground">{skill.name}</span>
                          {skill.verified && (
                            <CheckCircle className="h-3.5 w-3.5 text-emerald-500" />
                          )}
                        </div>
                        <Badge className={`text-xs border ${getLevelColor(skill.level)}`}>
                          {skill.level}
                        </Badge>
                      </div>
                    ))
                  ) : (
                    <div className="space-y-2">
                      {[['React', 'advanced'], ['TypeScript', 'intermediate'], ['CSS', 'advanced']].map(([name, level]) => (
                        <div key={name} className="flex items-center justify-between p-2.5 rounded-lg bg-muted/30">
                          <span className="text-sm font-medium">{name}</span>
                          <Badge className={`text-xs border ${getLevelColor(level)}`}>{level}</Badge>
                        </div>
                      ))}
                    </div>
                  )}
                  <Button variant="outline" size="sm" className="w-full border-dashed border-border/60 text-muted-foreground hover:text-foreground text-xs">
                    <Plus className="h-3.5 w-3.5 mr-1" /> Add Skill
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {/* Soft skills */}
          <motion.div variants={item}>
            <Card id="soft-skills-card" className="border-border/50 bg-card/80">
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Soft Skills</CardTitle>
                <CardDescription className="text-xs">Interpersonal and leadership competencies</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {softSkills.map((skill) => (
                    <div
                      key={skill.id}
                      className="flex flex-col items-center p-4 rounded-xl border border-border/40 bg-muted/20 text-center"
                    >
                      <div className={`h-8 w-8 rounded-full ${getLevelBg(skill.level)} flex items-center justify-center mb-2`}>
                        <Star className={`h-4 w-4 ${getLevelText(skill.level)}`} />
                      </div>
                      <p className="text-sm font-medium text-foreground">{skill.name}</p>
                      <Badge className={`mt-1.5 text-[10px] border ${getLevelColor(skill.level)}`}>
                        {skill.level}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>

        {/* ── Skill Gaps tab ──────────────────────────────── */}
        <TabsContent value="gaps" className="space-y-4">
          <motion.div variants={container} initial="hidden" animate="visible" className="space-y-4">
            {skillGaps.map((gap, i) => (
              <motion.div key={i} variants={item}>
                <Card id={`gap-card-${i}`} className="border-border/50 bg-card/80 hover:border-primary/20 transition-colors">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base">{gap.skill}</CardTitle>
                      <Badge className={`text-xs border ${getPriorityColor(gap.priority)}`}>
                        {gap.priority} Priority
                      </Badge>
                    </div>
                    <CardDescription className="text-xs">
                      Current: <span className="text-foreground font-medium">{gap.currentLevel}</span>
                      {' → '}Target: <span className="text-primary font-medium">{gap.requiredLevel}</span>
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <div className="flex justify-between text-xs mb-2">
                        <span className="text-muted-foreground">Progress to target</span>
                        <span className="font-bold text-foreground">{gap.progress}%</span>
                      </div>
                      <Progress value={gap.progress} className="h-2" />
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-muted-foreground mb-2">Recommended learning path</p>
                      <div className="flex flex-wrap gap-1.5">
                        {gap.learningPath.map((step, j) => (
                          <Badge key={j} variant="secondary" className="text-xs">
                            {j + 1}. {step}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <Button size="sm" className="bg-gradient-primary hover:opacity-90 border-0 text-white gap-2">
                      <BookOpen className="h-3.5 w-3.5" />
                      Start Learning
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </TabsContent>

        {/* ── Recommendations tab ─────────────────────────── */}
        <TabsContent value="recommendations">
          <motion.div variants={container} initial="hidden" animate="visible" className="grid gap-4 md:grid-cols-3">
            {recommendations.map((rec, i) => (
              <motion.div key={i} variants={item}>
                <Card id={`rec-card-${i}`} className="border-border/50 bg-card/80 hover:border-primary/20 transition-all hover:shadow-lg h-full flex flex-col">
                  <CardHeader>
                    <div className="flex items-start justify-between gap-2">
                      <CardTitle className="text-base leading-snug">{rec.title}</CardTitle>
                      <Badge className={`text-xs border flex-shrink-0 ${getPriorityColor(rec.priority)}`}>
                        {rec.priority}
                      </Badge>
                    </div>
                    <CardDescription className="text-xs flex items-center gap-2">
                      {rec.provider}
                      <Badge variant="outline" className="text-[10px] h-4 px-1.5">{rec.tag}</Badge>
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="flex-1 flex flex-col justify-between space-y-4">
                    <dl className="space-y-2 text-sm">
                      {[['Duration', rec.duration], ['Cost', rec.cost], ['Rating', `⭐ ${rec.rating}/5`]].map(([k, v]) => (
                        <div key={k} className="flex justify-between">
                          <dt className="text-muted-foreground">{k}</dt>
                          <dd className="font-semibold text-foreground">{v}</dd>
                        </div>
                      ))}
                    </dl>
                    <Button className="w-full bg-gradient-primary hover:opacity-90 border-0 text-white">
                      Start Learning
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </TabsContent>

        {/* ── Progress History tab ────────────────────────── */}
        <TabsContent value="progress">
          <motion.div variants={item}>
            <Card className="border-border/50 bg-card/80">
              <CardHeader>
                <CardTitle className="text-base">Learning History</CardTitle>
                <CardDescription className="text-xs">Track your skill development over time</CardDescription>
              </CardHeader>
              <CardContent>
                <div id="history-timeline" className="space-y-0">
                  {historyItems.map((h, i) => (
                    <div key={i} id={`history-${i}`} className="flex gap-4 relative">
                      <div className="flex flex-col items-center">
                        <div className={`h-3 w-3 rounded-full mt-1 flex-shrink-0 z-10 ${
                          h.type === 'completed' ? 'bg-emerald-500' :
                          h.type === 'started'   ? 'bg-blue-500' : 'bg-amber-500'
                        }`} />
                        {i < historyItems.length - 1 && (
                          <div className="flex-1 w-px bg-border/50 mt-1" style={{ minHeight: 32 }} />
                        )}
                      </div>
                      <div className="flex-1 pb-6">
                        <p className="text-sm font-semibold text-foreground">{h.milestone}</p>
                        <p className="text-xs text-muted-foreground mt-0.5">
                          <span className="font-medium text-primary">{h.skill}</span> · {h.date}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </TabsContent>
      </Tabs>
    </motion.div>
  );
}
