import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { BookOpen, Search, ExternalLink, Star, Clock, DollarSign, Flame, PlayCircle } from 'lucide-react';

interface Course {
  id: string;
  title: string;
  provider: string;
  category: string;
  duration: string;
  cost: 'Free' | 'Paid';
  rating: number;
  enrolled: number;
  tags: string[];
  url?: string;
  progress?: number;
  priority: 'high' | 'medium' | 'low';
  description: string;
}

const courses: Course[] = [
  {
    id: '1',
    title: 'Advanced React Patterns',
    provider: 'Frontend Masters',
    category: 'Frontend',
    duration: '6 weeks',
    cost: 'Paid',
    rating: 4.9,
    enrolled: 12400,
    tags: ['React', 'TypeScript', 'Patterns'],
    progress: 35,
    priority: 'high',
    description: 'Master compound components, render props, custom hooks, and performance optimization patterns used in production apps.',
  },
  {
    id: '2',
    title: 'System Design for Interviews',
    provider: 'Educative',
    category: 'Architecture',
    duration: '4 weeks',
    cost: 'Paid',
    rating: 4.8,
    enrolled: 28900,
    tags: ['System Design', 'Scalability', 'Architecture'],
    priority: 'high',
    description: 'Learn how to design large-scale distributed systems. Covers load balancing, caching, databases, and real interview questions.',
  },
  {
    id: '3',
    title: 'AWS Cloud Practitioner',
    provider: 'AWS Training',
    category: 'Cloud',
    duration: '3 weeks',
    cost: 'Free',
    rating: 4.7,
    enrolled: 89000,
    tags: ['AWS', 'Cloud', 'DevOps'],
    priority: 'medium',
    description: 'Official AWS certification prep covering core cloud concepts, services, pricing, and security fundamentals.',
  },
  {
    id: '4',
    title: "TypeScript: The Complete Developer's Guide",
    provider: 'Udemy',
    category: 'Languages',
    duration: '5 weeks',
    cost: 'Paid',
    rating: 4.8,
    enrolled: 62000,
    tags: ['TypeScript', 'JavaScript', 'React'],
    progress: 72,
    priority: 'high',
    description: 'Deep dive into TypeScript generics, utility types, decorators, and advanced patterns used in real-world projects.',
  },
  {
    id: '5',
    title: 'Node.js Microservices',
    provider: 'Pluralsight',
    category: 'Backend',
    duration: '8 weeks',
    cost: 'Paid',
    rating: 4.6,
    enrolled: 14200,
    tags: ['Node.js', 'Microservices', 'Docker', 'API'],
    priority: 'medium',
    description: 'Build production-ready microservices with Node.js, Docker, message queues, and API gateways.',
  },
  {
    id: '6',
    title: 'Machine Learning Crash Course',
    provider: 'Google',
    category: 'AI/ML',
    duration: '3 weeks',
    cost: 'Free',
    rating: 4.7,
    enrolled: 250000,
    tags: ['ML', 'Python', 'TensorFlow', 'AI'],
    priority: 'low',
    description: "Google's fast-paced introduction to machine learning with TensorFlow. No prior ML experience required.",
  },
  {
    id: '7',
    title: 'Docker & Kubernetes for Developers',
    provider: 'Udemy',
    category: 'DevOps',
    duration: '4 weeks',
    cost: 'Paid',
    rating: 4.7,
    enrolled: 45000,
    tags: ['Docker', 'Kubernetes', 'DevOps', 'CI/CD'],
    priority: 'medium',
    description: 'Learn to containerize apps with Docker and orchestrate them with Kubernetes. Covers Helm, Ingress, and production deployment.',
  },
  {
    id: '8',
    title: 'CS50: Introduction to Computer Science',
    provider: 'Harvard / edX',
    category: 'Fundamentals',
    duration: '12 weeks',
    cost: 'Free',
    rating: 4.9,
    enrolled: 3200000,
    tags: ['CS Fundamentals', 'Algorithms', 'C', 'Python'],
    priority: 'low',
    description: "Harvard's legendary intro to CS. Covers algorithms, data structures, memory management, and problem solving from first principles.",
  },
];

const categories = ['All', 'Frontend', 'Backend', 'Architecture', 'Cloud', 'DevOps', 'AI/ML', 'Languages', 'Fundamentals'];

export default function Learning() {
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('All');

  const inProgress = courses.filter((c) => (c.progress ?? 0) > 0);

  const filtered = courses.filter((c) => {
    const matchesSearch =
      c.title.toLowerCase().includes(search.toLowerCase()) ||
      c.provider.toLowerCase().includes(search.toLowerCase()) ||
      c.tags.some((t) => t.toLowerCase().includes(search.toLowerCase()));
    const matchesCategory = category === 'All' || c.category === category;
    return matchesSearch && matchesCategory;
  });

  return (
    <div id="learning-container" className="container mx-auto py-8 px-4 max-w-6xl">
      <motion.div id="learning-header" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
            <BookOpen className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold">Learning Hub</h1>
            <p className="text-muted-foreground">Curated courses to accelerate your career</p>
          </div>
        </div>
      </motion.div>

      {/* In Progress */}
      {inProgress.length > 0 && (
        <motion.div id="in-progress-section" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="mb-8">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Flame className="h-5 w-5 text-amber-500" />
            In Progress
          </h2>
          <div id="in-progress-list" className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {inProgress.map((course) => (
              <Card key={course.id} id={`progress-card-${course.id}`} className="border-border/50 hover:border-primary/20 transition-colors">
                <CardContent className="pt-4 pb-4">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-semibold text-sm">{course.title}</h3>
                      <p className="text-xs text-muted-foreground">{course.provider}</p>
                    </div>
                    <Badge variant="outline" className="text-xs">{course.category}</Badge>
                  </div>
                  <div className="space-y-1.5">
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>Progress</span>
                      <span className="font-medium text-foreground">{course.progress}%</span>
                    </div>
                    <Progress value={course.progress} className="h-1.5" />
                  </div>
                  <Button id={`continue-${course.id}`} size="sm" className="w-full mt-3 gap-2">
                    <PlayCircle className="h-3.5 w-3.5" />
                    Continue Learning
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </motion.div>
      )}

      {/* Search + Filter */}
      <motion.div id="learning-controls" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="mb-6 space-y-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            id="learning-search"
            placeholder="Search courses, skills, providers..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>
        <div id="category-filters" className="flex flex-wrap gap-2">
          {categories.map((cat) => (
            <button
              key={cat}
              id={`cat-${cat}`}
              onClick={() => setCategory(cat)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-all ${
                category === cat
                  ? 'bg-primary text-primary-foreground border-primary'
                  : 'border-border/50 text-muted-foreground hover:border-primary/30 hover:text-foreground'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Course Grid */}
      <motion.div id="courses-grid" initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filtered.map((course) => (
          <Card key={course.id} id={`course-card-${course.id}`} className="border-border/50 hover:border-primary/20 transition-colors flex flex-col">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1">
                  <div className="flex items-center gap-1.5 mb-1.5">
                    <Badge
                      className={`text-xs ${
                        course.priority === 'high'
                          ? 'bg-red-500/10 text-red-400 border-red-500/20'
                          : course.priority === 'medium'
                          ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                          : 'bg-muted text-muted-foreground border-border'
                      }`}
                    >
                      {course.priority === 'high' ? 'High Priority' : course.priority === 'medium' ? 'Recommended' : 'Explore'}
                    </Badge>
                  </div>
                  <CardTitle className="text-base leading-snug">{course.title}</CardTitle>
                  <CardDescription className="text-xs mt-0.5">{course.provider}</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col">
              <p className="text-xs text-muted-foreground mb-4 leading-relaxed flex-1">{course.description}</p>

              <div className="space-y-3">
                <div id={`course-meta-${course.id}`} className="flex items-center gap-3 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {course.duration}
                  </span>
                  <span className="flex items-center gap-1">
                    <Star className="h-3 w-3 text-amber-400 fill-amber-400" />
                    {course.rating}
                  </span>
                  <span className={`flex items-center gap-1 font-medium ${course.cost === 'Free' ? 'text-emerald-500' : 'text-muted-foreground'}`}>
                    <DollarSign className="h-3 w-3" />
                    {course.cost}
                  </span>
                </div>

                <div id={`course-tags-${course.id}`} className="flex flex-wrap gap-1">
                  {course.tags.slice(0, 3).map((tag) => (
                    <Badge key={tag} variant="secondary" className="text-xs px-2 py-0.5">
                      {tag}
                    </Badge>
                  ))}
                </div>

                <Button id={`enroll-${course.id}`} variant="outline" className="w-full gap-2 hover:border-primary/30">
                  <ExternalLink className="h-3.5 w-3.5" />
                  {(course.progress ?? 0) > 0 ? 'Continue' : 'Enroll Now'}
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </motion.div>

      {filtered.length === 0 && (
        <div id="no-courses" className="text-center py-16 text-muted-foreground">
          <BookOpen className="h-10 w-10 mx-auto mb-3 opacity-20" />
          <p>No courses found for "{search}"</p>
        </div>
      )}
    </div>
  );
}
