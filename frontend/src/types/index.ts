export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  profile: UserProfile;
  preferences: UserPreferences;
  progress: ProgressMetrics;
}

export interface UserProfile {
  title?: string;
  experience?: string;
  education?: string;
  location?: string;
  interests: string[];
  skills: Skill[];
  completedAssessments: string[];
}

export interface UserPreferences {
  jobType: 'full-time' | 'part-time' | 'contract' | 'internship';
  workEnvironment: 'remote' | 'onsite' | 'hybrid';
  salary: {
    min: number;
    max: number;
  };
  industries: string[];
}

export interface ProgressMetrics {
  careerMatch: number;
  skillsCompleted: number;
  applicationsSubmitted: number;
  assessmentsCompleted: number;
  profileCompletion: number;
}

export interface Career {
  id: string;
  title: string;
  description: string;
  match?: number;
  salary: {
    min: number;
    max: number;
  };
  growth: 'high' | 'medium' | 'low';
  education: string;
  experience: string;
  skills: string[];
  tasks: string[];
  relatedCareers: string[];
  pathway?: CareerPathway;
}

export interface CareerPathway {
  steps: PathwayStep[];
  estimatedTime: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
}

export interface PathwayStep {
  id: string;
  title: string;
  description: string;
  type: 'education' | 'skill' | 'experience' | 'certification';
  duration: string;
  resources: Resource[];
  completed: boolean;
}

export interface Resource {
  id: string;
  title: string;
  type: 'course' | 'book' | 'article' | 'video' | 'tool';
  url?: string;
  provider?: string;
  cost: 'free' | 'paid';
  rating?: number;
}

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  salary?: string;
  type: 'full-time' | 'part-time' | 'contract' | 'internship';
  description: string;
  requirements: string[];
  benefits?: string[];
  match?: number;
  postedDate: string;
  applicationDeadline?: string;
  applied: boolean;
  saved: boolean;
  source: string;
}

export interface Skill {
  id: string;
  name: string;
  level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  category: string;
  isCore: boolean;
  verified: boolean;
  endorsements?: number;
}

export interface SkillGap {
  skill: string;
  currentLevel: string;
  requiredLevel: string;
  priority: 'high' | 'medium' | 'low';
  learningPath: Resource[];
}

export interface StudentPathway {
  id: string;
  level: 'high-school' | 'college';
  grade?: string;
  major?: string;
  recommendations: {
    courses: string[];
    extracurriculars: string[];
    internships: Job[];
    certifications: string[];
    projects: string[];
  };
  timeline: TimelineEvent[];
}

export interface TimelineEvent {
  id: string;
  title: string;
  type: 'course' | 'internship' | 'project' | 'certification' | 'application';
  date: string;
  status: 'upcoming' | 'in-progress' | 'completed';
  description?: string;
}

export interface Application {
  id: string;
  jobId: string;
  resume: Resume;
  coverLetter: CoverLetter;
  status: 'draft' | 'submitted' | 'interview' | 'offer' | 'rejected';
  submittedDate?: string;
  followUpDate?: string;
}

export interface Resume {
  id: string;
  template: string;
  sections: ResumeSection[];
  lastUpdated: string;
}

export interface ResumeSection {
  type: 'header' | 'summary' | 'experience' | 'education' | 'skills' | 'projects';
  content: any;
  order: number;
}

export interface CoverLetter {
  id: string;
  jobId: string;
  content: string;
  lastUpdated: string;
}