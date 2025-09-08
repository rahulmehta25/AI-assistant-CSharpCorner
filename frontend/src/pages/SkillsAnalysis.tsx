import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useUserStore } from '@/store/useUserStore';
import { Brain, Target, TrendingUp, BookOpen, Award, Plus } from 'lucide-react';

const SkillsAnalysis = () => {
  const { user } = useUserStore();
  const [selectedSkill, setSelectedSkill] = useState<string | null>(null);

  const skillGaps = [
    {
      skill: 'Advanced React',
      currentLevel: 'Intermediate',
      requiredLevel: 'Advanced',
      gap: 25,
      priority: 'High',
      learningPath: ['Advanced React Patterns', 'Performance Optimization', 'Testing'],
    },
    {
      skill: 'System Design',
      currentLevel: 'Beginner',
      requiredLevel: 'Intermediate',
      gap: 50,
      priority: 'High',
      learningPath: ['Scalability Fundamentals', 'Database Design', 'API Architecture'],
    },
    {
      skill: 'DevOps',
      currentLevel: 'Beginner',
      requiredLevel: 'Intermediate',
      gap: 60,
      priority: 'Medium',
      learningPath: ['Docker Basics', 'CI/CD Pipelines', 'AWS Fundamentals'],
    },
  ];

  const skillCategories = [
    {
      name: 'Technical Skills',
      skills: user?.profile.skills || [],
      color: 'bg-gradient-to-r from-blue-500 to-cyan-500',
    },
    {
      name: 'Soft Skills', 
      skills: [
        { id: 'comm', name: 'Communication', level: 'advanced', category: 'Soft Skills', isCore: true, verified: true },
        { id: 'lead', name: 'Leadership', level: 'intermediate', category: 'Soft Skills', isCore: true, verified: false },
        { id: 'prob', name: 'Problem Solving', level: 'advanced', category: 'Soft Skills', isCore: true, verified: true },
      ],
      color: 'bg-gradient-to-r from-purple-500 to-pink-500',
    },
  ];

  const recommendations = [
    {
      title: 'Complete React Advanced Course',
      provider: 'Frontend Masters',
      duration: '6 weeks',
      cost: 'Paid',
      rating: 4.8,
      priority: 'High',
    },
    {
      title: 'System Design Interview Prep',
      provider: 'Educative',
      duration: '4 weeks', 
      cost: 'Paid',
      rating: 4.7,
      priority: 'High',
    },
    {
      title: 'AWS Cloud Practitioner',
      provider: 'AWS',
      duration: '3 weeks',
      cost: 'Free',
      rating: 4.6,
      priority: 'Medium',
    },
  ];

  const getSkillLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'expert': return 'bg-emerald-100 text-emerald-700 border-emerald-200';
      case 'advanced': return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'intermediate': return 'bg-amber-100 text-amber-700 border-amber-200';
      case 'beginner': return 'bg-gray-100 text-gray-700 border-gray-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'high': return 'bg-red-100 text-red-700 border-red-200';
      case 'medium': return 'bg-amber-100 text-amber-700 border-amber-200';
      case 'low': return 'bg-green-100 text-green-700 border-green-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-7xl">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-3 mb-4">
          <Brain className="h-8 w-8 text-primary" />
          <h1 className="text-4xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
            Skills Analysis
          </h1>
        </div>
        <p className="text-xl text-muted-foreground">
          Analyze your skills, identify gaps, and get personalized learning recommendations
        </p>
      </motion.div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="gaps">Skill Gaps</TabsTrigger>
          <TabsTrigger value="recommendations">Learn</TabsTrigger>
          <TabsTrigger value="progress">Progress</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="border-l-4 border-l-primary">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Total Skills</p>
                    <p className="text-3xl font-bold text-foreground">{user?.profile.skills?.length || 0}</p>
                  </div>
                  <Award className="h-8 w-8 text-primary" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-emerald-500">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Verified Skills</p>
                    <p className="text-3xl font-bold text-foreground">
                      {user?.profile.skills?.filter(s => s.verified).length || 0}
                    </p>
                  </div>
                  <Target className="h-8 w-8 text-emerald-500" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-amber-500">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Skill Gaps</p>
                    <p className="text-3xl font-bold text-foreground">{skillGaps.length}</p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-amber-500" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-l-4 border-l-purple-500">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">Learning Hours</p>
                    <p className="text-3xl font-bold text-foreground">24</p>
                  </div>
                  <BookOpen className="h-8 w-8 text-purple-500" />
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {skillCategories.map((category) => (
              <Card key={category.name}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${category.color}`} />
                    {category.name}
                  </CardTitle>
                  <CardDescription>Your current {category.name.toLowerCase()}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {category.skills.map((skill) => (
                      <div key={skill.id} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                        <div className="flex items-center gap-3">
                          <span className="font-medium text-foreground">{skill.name}</span>
                          {skill.verified && (
                            <Award className="h-4 w-4 text-emerald-500" />
                          )}
                        </div>
                        <Badge className={getSkillLevelColor(skill.level)}>
                          {skill.level}
                        </Badge>
                      </div>
                    ))}
                    <Button variant="outline" size="sm" className="w-full">
                      <Plus className="h-4 w-4 mr-2" />
                      Add Skill
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="gaps" className="space-y-6">
          <div className="space-y-4">
            {skillGaps.map((gap, index) => (
              <Card key={index} className="transition-shadow hover:shadow-md">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg text-foreground">{gap.skill}</CardTitle>
                    <Badge className={getPriorityColor(gap.priority)}>
                      {gap.priority} Priority
                    </Badge>
                  </div>
                  <CardDescription>
                    Current: {gap.currentLevel} → Target: {gap.requiredLevel}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="text-muted-foreground">Progress to target level</span>
                        <span className="text-foreground font-medium">{100 - gap.gap}%</span>
                      </div>
                      <Progress value={100 - gap.gap} className="h-2" />
                    </div>
                    
                    <div>
                      <p className="text-sm font-medium text-foreground mb-2">Recommended Learning Path:</p>
                      <div className="flex flex-wrap gap-2">
                        {gap.learningPath.map((step, stepIndex) => (
                          <Badge key={stepIndex} variant="secondary">
                            {step}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="recommendations" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {recommendations.map((rec, index) => (
              <Card key={index} className="transition-shadow hover:shadow-md">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-lg text-foreground">{rec.title}</CardTitle>
                    <Badge className={getPriorityColor(rec.priority)}>
                      {rec.priority}
                    </Badge>
                  </div>
                  <CardDescription>{rec.provider}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Duration:</span>
                      <span className="text-foreground font-medium">{rec.duration}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Cost:</span>
                      <span className="text-foreground font-medium">{rec.cost}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Rating:</span>
                      <span className="text-foreground font-medium">⭐ {rec.rating}</span>
                    </div>
                    <Button className="w-full mt-4">Start Learning</Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="progress" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Learning Progress Timeline</CardTitle>
              <CardDescription>Track your skill development over time</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {[
                  { date: '2024-01-15', skill: 'React', milestone: 'Completed Advanced React Course', type: 'completed' },
                  { date: '2024-01-10', skill: 'Python', milestone: 'Started Data Analysis Path', type: 'started' },
                  { date: '2024-01-05', skill: 'JavaScript', milestone: 'Verified ES6+ Knowledge', type: 'verified' },
                ].map((item, index) => (
                  <div key={index} className="flex items-start space-x-4">
                    <div className={`flex-shrink-0 w-3 h-3 rounded-full mt-2 ${
                      item.type === 'completed' ? 'bg-emerald-500' :
                      item.type === 'started' ? 'bg-blue-500' : 'bg-amber-500'
                    }`} />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-foreground">{item.milestone}</p>
                      <p className="text-xs text-muted-foreground">{item.skill} • {item.date}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default SkillsAnalysis;