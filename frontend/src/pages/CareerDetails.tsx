import { useParams, Link } from 'react-router-dom';
import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { mockCareers } from '@/services/api';
import { useUserStore } from '@/store/useUserStore';
import { 
  ArrowLeft, Bookmark, BookmarkCheck, DollarSign, TrendingUp, 
  GraduationCap, Clock, CheckCircle, Circle, Star, Users,
  BookOpen, Award, Target, Calendar
} from 'lucide-react';

const CareerDetails = () => {
  const { id } = useParams();
  const { bookmarkedCareers, bookmarkCareer, unbookmarkCareer, user } = useUserStore();
  const [activeStep, setActiveStep] = useState(0);

  const career = mockCareers.find(c => c.id === id);
  const isBookmarked = bookmarkedCareers.some(c => c.id === id);

  if (!career) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-foreground mb-4">Career Not Found</h1>
          <Link to="/careers">
            <Button>Back to Careers</Button>
          </Link>
        </div>
      </div>
    );
  }

  const handleBookmark = () => {
    if (isBookmarked) {
      unbookmarkCareer(career.id);
    } else {
      bookmarkCareer(career);
    }
  };

  // Generate personalized roadmap based on user's current skills
  const generatePersonalizedRoadmap = () => {
    const userSkills = user?.profile.skills?.map(s => s.name.toLowerCase()) || [];
    const careerSkills = career.skills.map(s => s.toLowerCase());
    const missingSkills = careerSkills.filter(skill => 
      !userSkills.some(userSkill => userSkill.includes(skill.toLowerCase()))
    );

    return {
      currentLevel: "Entry Level",
      targetLevel: "Mid Level",
      estimatedTime: "12-18 months",
      completionRate: Math.round((userSkills.length / careerSkills.length) * 100),
      steps: [
        {
          id: 1,
          phase: "Foundation",
          title: "Build Core Skills",
          duration: "3-4 months",
          status: userSkills.length > 2 ? "completed" : "current",
          skills: career.skills.slice(0, 2),
          description: "Master the fundamental skills required for this career path",
          resources: [
            { title: "Introduction to Programming", type: "course", provider: "Coursera" },
            { title: "Computer Science Fundamentals", type: "book", provider: "MIT Press" }
          ]
        },
        {
          id: 2,
          phase: "Development",
          title: "Advanced Skills & Projects",
          duration: "4-6 months", 
          status: userSkills.length > 4 ? "completed" : missingSkills.length < 3 ? "current" : "upcoming",
          skills: career.skills.slice(2, 4),
          description: "Develop advanced technical skills through hands-on projects",
          resources: [
            { title: "Advanced Web Development", type: "course", provider: "Udemy" },
            { title: "Build a Portfolio Project", type: "project", provider: "Self-guided" }
          ]
        },
        {
          id: 3,
          phase: "Specialization",
          title: "Industry Expertise",
          duration: "3-4 months",
          status: userSkills.length >= careerSkills.length ? "current" : "upcoming",
          skills: career.skills.slice(4),
          description: "Specialize in industry-specific tools and frameworks",
          resources: [
            { title: "Industry Certification Prep", type: "certification", provider: "Professional Body" },
            { title: "Real-world Internship", type: "experience", provider: "Company" }
          ]
        },
        {
          id: 4,
          phase: "Job Ready",
          title: "Career Preparation",
          duration: "2-3 months",
          status: "upcoming",
          skills: ["Interview Prep", "Portfolio Review", "Network Building"],
          description: "Prepare for job applications and interviews",
          resources: [
            { title: "Technical Interview Prep", type: "course", provider: "LeetCode" },
            { title: "Portfolio Review Session", type: "mentoring", provider: "Industry Mentor" }
          ]
        }
      ]
    };
  };

  const roadmap = generatePersonalizedRoadmap();

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-5 w-5 text-emerald-500" />;
      case 'current': return <Circle className="h-5 w-5 text-primary fill-current" />;
      default: return <Circle className="h-5 w-5 text-muted-foreground" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-emerald-100 text-emerald-700 border-emerald-200';
      case 'current': return 'bg-blue-100 text-blue-700 border-blue-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-6xl">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center gap-4 mb-6">
          <Link to="/careers">
            <Button variant="outline" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Careers
            </Button>
          </Link>
          <Button
            variant={isBookmarked ? "default" : "outline"}
            size="sm"
            onClick={handleBookmark}
          >
            {isBookmarked ? (
              <BookmarkCheck className="h-4 w-4 mr-2" />
            ) : (
              <Bookmark className="h-4 w-4 mr-2" />
            )}
            {isBookmarked ? 'Bookmarked' : 'Bookmark'}
          </Button>
        </div>

        <div className="flex flex-col lg:flex-row gap-8">
          <div className="flex-1">
            <h1 className="text-4xl font-bold text-foreground mb-4">{career.title}</h1>
            <p className="text-xl text-muted-foreground mb-6">{career.description}</p>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center">
                <DollarSign className="h-6 w-6 mx-auto mb-2 text-emerald-500" />
                <p className="text-sm text-muted-foreground">Salary Range</p>
                <p className="font-semibold text-foreground">
                  ${career.salary.min.toLocaleString()} - ${career.salary.max.toLocaleString()}
                </p>
              </div>
              <div className="text-center">
                <TrendingUp className="h-6 w-6 mx-auto mb-2 text-blue-500" />
                <p className="text-sm text-muted-foreground">Growth</p>
                <Badge className={
                  career.growth === 'high' ? 'bg-emerald-100 text-emerald-700' : 
                  career.growth === 'medium' ? 'bg-amber-100 text-amber-700' : 
                  'bg-red-100 text-red-700'
                }>
                  {career.growth}
                </Badge>
              </div>
              <div className="text-center">
                <GraduationCap className="h-6 w-6 mx-auto mb-2 text-purple-500" />
                <p className="text-sm text-muted-foreground">Education</p>
                <p className="font-semibold text-foreground text-xs">{career.education}</p>
              </div>
              <div className="text-center">
                <Users className="h-6 w-6 mx-auto mb-2 text-orange-500" />
                <p className="text-sm text-muted-foreground">Experience</p>
                <p className="font-semibold text-foreground">{career.experience}</p>
              </div>
            </div>
          </div>

          {career.match && (
            <Card className="lg:w-80">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="h-5 w-5 text-primary" />
                  Your Match
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center">
                  <div className="text-4xl font-bold text-primary mb-2">{career.match}%</div>
                  <Progress value={career.match} className="mb-4" />
                  <p className="text-sm text-muted-foreground">
                    Based on your skills and interests
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </motion.div>

      {/* Tabs */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="roadmap">Personal Roadmap</TabsTrigger>
          <TabsTrigger value="skills">Skills & Tasks</TabsTrigger>
          <TabsTrigger value="related">Related Careers</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Required Skills</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {career.skills.map((skill) => (
                    <Badge key={skill} variant="secondary">{skill}</Badge>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Daily Tasks</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  {career.tasks.map((task, index) => (
                    <li key={index} className="flex items-start gap-2 text-sm">
                      <CheckCircle className="h-4 w-4 text-emerald-500 mt-0.5 flex-shrink-0" />
                      <span className="text-muted-foreground">{task}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="roadmap" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Star className="h-5 w-5 text-primary" />
                Personalized Career Roadmap
              </CardTitle>
              <CardDescription>
                Based on your current skills and target career goals
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                <div className="text-center">
                  <Calendar className="h-6 w-6 mx-auto mb-2 text-primary" />
                  <p className="text-sm text-muted-foreground">Estimated Time</p>
                  <p className="font-semibold text-foreground">{roadmap.estimatedTime}</p>
                </div>
                <div className="text-center">
                  <Target className="h-6 w-6 mx-auto mb-2 text-emerald-500" />
                  <p className="text-sm text-muted-foreground">Completion Rate</p>
                  <p className="font-semibold text-foreground">{roadmap.completionRate}%</p>
                </div>
                <div className="text-center">
                  <TrendingUp className="h-6 w-6 mx-auto mb-2 text-blue-500" />
                  <p className="text-sm text-muted-foreground">Current Level</p>
                  <p className="font-semibold text-foreground">{roadmap.currentLevel}</p>
                </div>
              </div>

              <div className="space-y-6">
                {roadmap.steps.map((step, index) => (
                  <div key={step.id} className="relative">
                    {/* Connection Line */}
                    {index < roadmap.steps.length - 1 && (
                      <div className="absolute left-6 top-12 w-0.5 h-24 bg-border" />
                    )}
                    
                    <div className="flex gap-4">
                      <div className="flex-shrink-0 mt-2">
                        {getStatusIcon(step.status)}
                      </div>
                      
                      <Card className="flex-1 transition-shadow hover:shadow-md">
                        <CardHeader>
                          <div className="flex items-center justify-between">
                            <div>
                              <Badge variant="outline" className="mb-2">
                                {step.phase}
                              </Badge>
                              <CardTitle className="text-lg">{step.title}</CardTitle>
                              <CardDescription>{step.description}</CardDescription>
                            </div>
                            <Badge className={getStatusColor(step.status)}>
                              {step.status}
                            </Badge>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-4">
                            <div className="flex items-center gap-2">
                              <Clock className="h-4 w-4 text-muted-foreground" />
                              <span className="text-sm text-muted-foreground">{step.duration}</span>
                            </div>
                            
                            <div>
                              <p className="text-sm font-medium mb-2 text-foreground">Skills to develop:</p>
                              <div className="flex flex-wrap gap-1">
                                {step.skills.map((skill) => (
                                  <Badge key={skill} variant="secondary" className="text-xs">
                                    {skill}
                                  </Badge>
                                ))}
                              </div>
                            </div>

                            <div>
                              <p className="text-sm font-medium mb-2 text-foreground">Learning resources:</p>
                              <div className="space-y-1">
                                {step.resources.map((resource, idx) => (
                                  <div key={idx} className="flex items-center gap-2 text-sm">
                                    <BookOpen className="h-3 w-3 text-muted-foreground" />
                                    <span className="text-muted-foreground">
                                      {resource.title} ({resource.provider})
                                    </span>
                                  </div>
                                ))}
                              </div>
                            </div>

                            {step.status === 'current' && (
                              <Button className="w-full">Start This Phase</Button>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="skills" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Required Skills</CardTitle>
                <CardDescription>Skills needed for this career</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {career.skills.map((skill) => {
                    const userHasSkill = user?.profile.skills?.some(s => 
                      s.name.toLowerCase().includes(skill.toLowerCase())
                    );
                    return (
                      <div key={skill} className="flex items-center justify-between p-2 rounded-lg bg-muted/50">
                        <span className="text-foreground">{skill}</span>
                        {userHasSkill ? (
                          <CheckCircle className="h-4 w-4 text-emerald-500" />
                        ) : (
                          <Circle className="h-4 w-4 text-muted-foreground" />
                        )}
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Daily Responsibilities</CardTitle>
                <CardDescription>What you'll do in this role</CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {career.tasks.map((task, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <CheckCircle className="h-4 w-4 text-primary mt-1 flex-shrink-0" />
                      <span className="text-muted-foreground text-sm">{task}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="related" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {career.relatedCareers.map((relatedId) => {
              const relatedCareer = mockCareers.find(c => c.id === relatedId);
              if (!relatedCareer) return null;
              
              return (
                <Card key={relatedId} className="transition-shadow hover:shadow-md">
                  <CardHeader>
                    <CardTitle className="text-lg">{relatedCareer.title}</CardTitle>
                    <CardDescription className="text-sm">
                      {relatedCareer.description.substring(0, 100)}...
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Salary:</span>
                        <span className="font-medium text-foreground">
                          ${relatedCareer.salary.min.toLocaleString()}k+
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Growth:</span>
                        <Badge className={
                          relatedCareer.growth === 'high' ? 'bg-emerald-100 text-emerald-700' : 
                          relatedCareer.growth === 'medium' ? 'bg-amber-100 text-amber-700' : 
                          'bg-red-100 text-red-700'
                        }>
                          {relatedCareer.growth}
                        </Badge>
                      </div>
                      <Link to={`/careers/${relatedCareer.id}`}>
                        <Button variant="outline" size="sm" className="w-full">
                          Learn More
                        </Button>
                      </Link>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CareerDetails;