import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid } from 'recharts';
import { TrendingUp, Target, Briefcase, Award, Brain, Calendar } from 'lucide-react';
import { useUserStore } from '@/store/useUserStore';
import { subDays, format } from 'date-fns';

function generateActivityData() {
  return Array.from({ length: 12 }, (_, i) => ({
    month: format(subDays(new Date(), (11 - i) * 30), 'MMM'),
    applications: Math.floor(Math.random() * 8) + 1,
    skills: Math.floor(Math.random() * 3) + 0,
    views: Math.floor(Math.random() * 15) + 3,
  }));
}

function generateSkillProgress() {
  return [
    { skill: 'JavaScript', level: 75 },
    { skill: 'React', level: 60 },
    { skill: 'TypeScript', level: 55 },
    { skill: 'Python', level: 45 },
    { skill: 'Node.js', level: 35 },
    { skill: 'System Design', level: 25 },
  ];
}

const activityData = generateActivityData();
const skillProgress = generateSkillProgress();

const jobSearchData = [
  { week: 'W1', applied: 3, responses: 0, interviews: 0 },
  { week: 'W2', applied: 5, responses: 1, interviews: 0 },
  { week: 'W3', applied: 4, responses: 2, interviews: 1 },
  { week: 'W4', applied: 6, responses: 3, interviews: 1 },
  { week: 'W5', applied: 8, responses: 4, interviews: 2 },
];

const insights = [
  { label: 'Response Rate', value: '24%', trend: '+8%', positive: true, desc: 'Above average for your field' },
  { label: 'Avg. Days to Response', value: '6.2', trend: '-1.4', positive: true, desc: 'Faster than last month' },
  { label: 'Interview Conversion', value: '33%', trend: '+5%', positive: true, desc: 'When you get a response' },
  { label: 'Profile Views', value: '47', trend: '+12', positive: true, desc: 'In the last 30 days' },
];

function ChartSkeleton({ height = 200 }: { height?: number }) {
  return (
    <div
      className="w-full rounded-lg bg-muted/40 animate-pulse"
      style={{ height }}
      aria-hidden="true"
    />
  );
}

export default function Analytics() {
  const { user } = useUserStore();
  const [chartsLoaded] = useState(true); // Charts render immediately; set to false to preview skeletons

  return (
    <div id="analytics-container" className="container mx-auto py-8 px-4 max-w-6xl">
      <motion.div id="analytics-header" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
            <TrendingUp className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">Analytics</h1>
            <p className="text-muted-foreground">Track your career development metrics over time</p>
          </div>
        </div>
      </motion.div>

      {/* Key Insights */}
      <motion.div id="key-insights" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {insights.map((insight, i) => (
          <Card key={i} id={`insight-${i}`} className="border-border/50 hover:border-primary/20 transition-colors duration-200">
            <CardContent className="pt-4 pb-4">
              <p className="text-xs text-muted-foreground mb-1">{insight.label}</p>
              <div className="flex items-end justify-between">
                <p className="text-2xl font-bold">{insight.value}</p>
                <Badge
                  className={`text-xs ${
                    insight.positive
                      ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20'
                      : 'bg-destructive/10 text-destructive border-destructive/20'
                  }`}
                >
                  {insight.trend}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground mt-1">{insight.desc}</p>
            </CardContent>
          </Card>
        ))}
      </motion.div>

      <div id="analytics-charts" className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Activity over time */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
          <Card id="activity-chart-card" className="border-border/50">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Calendar className="h-4 w-4 text-primary" />
                Activity Overview
              </CardTitle>
              <CardDescription>Applications and skills added per month</CardDescription>
            </CardHeader>
            <CardContent>
              <div
                aria-label="Bar chart showing number of job applications and skills added per month over the last 12 months"
                role="img"
              >
                {chartsLoaded ? (
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart data={activityData} barGap={4}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis dataKey="month" tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }} axisLine={false} tickLine={false} />
                      <Tooltip
                        contentStyle={{
                          background: 'hsl(var(--card))',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px',
                          fontSize: '12px',
                        }}
                      />
                      <Bar dataKey="applications" name="Applications" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="skills" name="Skills" fill="hsl(var(--secondary))" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <ChartSkeleton height={200} />
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Job search funnel */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card id="funnel-chart-card" className="border-border/50">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Briefcase className="h-4 w-4 text-primary" />
                Job Search Funnel
              </CardTitle>
              <CardDescription>Applications → Responses → Interviews over 5 weeks</CardDescription>
            </CardHeader>
            <CardContent>
              <div
                aria-label="Line chart showing job search funnel: applications sent, responses received, and interviews scheduled over 5 weeks"
                role="img"
              >
                {chartsLoaded ? (
                  <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={jobSearchData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                      <XAxis dataKey="week" tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }} axisLine={false} tickLine={false} />
                      <Tooltip
                        contentStyle={{
                          background: 'hsl(var(--card))',
                          border: '1px solid hsl(var(--border))',
                          borderRadius: '8px',
                          fontSize: '12px',
                        }}
                      />
                      <Line type="monotone" dataKey="applied" name="Applied" stroke="hsl(var(--primary))" strokeWidth={2} dot={false} />
                      <Line type="monotone" dataKey="responses" name="Responses" stroke="hsl(var(--secondary))" strokeWidth={2} dot={false} />
                      <Line type="monotone" dataKey="interviews" name="Interviews" stroke="hsl(158 64% 52%)" strokeWidth={2} dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <ChartSkeleton height={200} />
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Skill Progress */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
        <Card id="skill-progress-card" className="border-border/50">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Brain className="h-4 w-4 text-primary" />
              Skill Proficiency Estimates
            </CardTitle>
            <CardDescription>Based on your self-assessment and completed activities</CardDescription>
          </CardHeader>
          <CardContent>
            <div id="skill-bars" className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {skillProgress.map((s) => (
                <div key={s.skill} id={`skill-bar-${s.skill}`} className="space-y-1.5">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium">{s.skill}</span>
                    <span className="text-muted-foreground">{s.level}%</span>
                  </div>
                  <Progress
                    value={s.level}
                    className="h-2"
                    aria-label={`${s.skill} proficiency`}
                    aria-valuenow={s.level}
                    aria-valuemax={100}
                  />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Career Match Trend */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="mt-6">
        <Card id="career-health-card" className="border-border/50">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Target className="h-4 w-4 text-primary" />
              Career Health Score
            </CardTitle>
            <CardDescription>Composite of profile strength, skills, activity, and job search momentum</CardDescription>
          </CardHeader>
          <CardContent>
            <div id="health-metrics" className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'Profile', score: user?.progress?.profileCompletion ?? 78, color: 'text-blue-400' },
                { label: 'Skills', score: 62, color: 'text-purple-400' },
                { label: 'Activity', score: 74, color: 'text-amber-400' },
                { label: 'Job Search', score: 55, color: 'text-emerald-500' },
              ].map((m, i) => (
                <div key={i} id={`health-metric-${i}`} className="text-center p-4 rounded-xl border border-border/50">
                  <p className={`text-3xl font-bold ${m.color}`}>{m.score}</p>
                  <p className="text-xs text-muted-foreground mt-1">{m.label}</p>
                  <Progress
                    value={m.score}
                    className="h-1 mt-2"
                    aria-label={`${m.label} health score`}
                    aria-valuenow={m.score}
                    aria-valuemax={100}
                  />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
