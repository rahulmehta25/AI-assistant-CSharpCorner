// User & Profile Types
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
  jobType: JobType;
  workEnvironment: WorkEnvironment;
  salary: SalaryRange;
  industries: string[];
}

export interface ProgressMetrics {
  careerMatch: number;
  skillsCompleted: number;
  applicationsSubmitted: number;
  assessmentsCompleted: number;
  profileCompletion: number;
  interviewsScheduled?: number;
  milestonesAchieved?: number;
}

// Career Types
export interface Career {
  id: string;
  title: string;
  description: string;
  match?: number;
  salary: SalaryRange;
  growth: string;
  growth_rate?: string;
  education: string;
  experience: string;
  skills: string[];
  tasks: string[];
  knowledge?: string[];
  abilities?: string[];
  interests?: string[];
  work_styles?: string[];
  work_environment?: string[];
  cluster?: string;
  related_careers?: string[];
  relatedCareers?: string[];
  pathway?: CareerPathway;
}

export interface CareerPathway {
  steps: PathwayStep[];
  estimatedTime: string;
  difficulty: DifficultyLevel;
}

export interface PathwayStep {
  id: string;
  title: string;
  description: string;
  type: PathwayStepType;
  duration: string;
  resources: Resource[];
  completed: boolean;
}

export interface Resource {
  id: string;
  title: string;
  type: ResourceType;
  url?: string;
  provider?: string;
  cost: 'free' | 'paid';
  rating?: number;
}

// Job Types
export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  salary?: string;
  salaryRange?: SalaryRange;
  type: JobType;
  description: string;
  requirements: string[];
  benefits?: string[];
  match?: number;
  postedDate: string;
  applicationDeadline?: string;
  applied: boolean;
  saved: boolean;
  source: string;
  remote?: boolean;
  companyLogo?: string;
  companySize?: string;
  industry?: string;
}

export interface JobFilters {
  query?: string;
  location?: string;
  type?: JobType;
  salaryMin?: number;
  salaryMax?: number;
  remote?: boolean;
  sortBy?: JobSortOption;
}

// Skill Types
export interface Skill {
  id: string;
  name: string;
  level: SkillLevel;
  category: string;
  isCore: boolean;
  verified: boolean;
  endorsements?: number;
  progress?: number;
}

export interface SkillGap {
  skill: string;
  currentLevel: string;
  requiredLevel: string;
  priority: Priority;
  learningPath: Resource[];
}

// Student Pathway Types
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
  type: TimelineEventType;
  date: string;
  status: TimelineStatus;
  description?: string;
}

// Application Types
export interface Application {
  id: string;
  jobId: string;
  job?: Job;
  resume: Resume;
  coverLetter: CoverLetter;
  status: ApplicationStatus;
  submittedDate?: string;
  followUpDate?: string;
  notes?: string;
}

// Resume Types
export interface Resume {
  id: string;
  template: string;
  sections: ResumeSection[];
  lastUpdated: string;
  atsScore?: number;
  suggestions?: ResumeSuggestion[];
}

export interface ResumeSection {
  type: ResumeSectionType;
  content: unknown;
  order: number;
}

export interface ResumeSuggestion {
  id: string;
  section: ResumeSectionType;
  type: 'improvement' | 'warning' | 'success';
  message: string;
  highlight?: {
    start: number;
    end: number;
  };
}

export interface ParsedResume {
  name?: string;
  email?: string;
  phone?: string;
  location?: string;
  summary?: string;
  experience: WorkExperience[];
  education: Education[];
  skills: string[];
  certifications?: string[];
  projects?: Project[];
}

export interface WorkExperience {
  company: string;
  title: string;
  location?: string;
  startDate: string;
  endDate?: string;
  current?: boolean;
  description: string[];
}

export interface Education {
  institution: string;
  degree: string;
  field?: string;
  startDate?: string;
  endDate?: string;
  gpa?: string;
}

export interface Project {
  name: string;
  description: string;
  technologies?: string[];
  url?: string;
}

// Cover Letter Types
export interface CoverLetter {
  id: string;
  jobId: string;
  content: string;
  tone: CoverLetterTone;
  lastUpdated: string;
}

export interface CoverLetterGenerationRequest {
  jobDescription: string;
  resume?: ParsedResume;
  tone: CoverLetterTone;
  highlights?: string[];
}

// Interview Types
export interface InterviewQuestion {
  id: string;
  question: string;
  category: InterviewCategory;
  difficulty: DifficultyLevel;
  suggestedAnswer?: string;
  tips?: string[];
  followUps?: string[];
}

export interface MockInterview {
  id: string;
  role: string;
  questions: InterviewQuestion[];
  responses: InterviewResponse[];
  startedAt: string;
  completedAt?: string;
  overallScore?: number;
  feedback?: InterviewFeedback;
}

export interface InterviewResponse {
  questionId: string;
  response: string;
  score?: number;
  feedback?: string;
  timestamp: string;
}

export interface InterviewFeedback {
  strengths: string[];
  improvements: string[];
  overallComments: string;
}

// Chat Types
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  suggestions?: string[];
}

export interface ChatConversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: Date;
  updatedAt: Date;
}

// Progress Tracking Types
export interface Milestone {
  id: string;
  title: string;
  description: string;
  type: MilestoneType;
  status: MilestoneStatus;
  dueDate?: string;
  completedDate?: string;
  progress?: number;
}

export interface ActivityItem {
  id: string;
  type: ActivityType;
  title: string;
  description?: string;
  timestamp: Date;
  metadata?: Record<string, unknown>;
}

// Roadmap Types
export interface RoadmapPhase {
  id: string;
  title: string;
  description: string;
  duration: string;
  status: 'completed' | 'current' | 'upcoming';
  steps: RoadmapStep[];
}

export interface RoadmapStep {
  id: string;
  title: string;
  description: string;
  type: PathwayStepType;
  completed: boolean;
  resources?: Resource[];
}

// Command Palette Types
export interface CommandItem {
  id: string;
  title: string;
  description?: string;
  icon?: React.ComponentType<{ className?: string }>;
  shortcut?: string;
  action: () => void;
  category?: string;
}

// Enum Types
export type JobType = 'full-time' | 'part-time' | 'contract' | 'internship';
export type WorkEnvironment = 'remote' | 'onsite' | 'hybrid';
export type SkillLevel = 'beginner' | 'intermediate' | 'advanced' | 'expert';
export type DifficultyLevel = 'beginner' | 'intermediate' | 'advanced';
export type Priority = 'high' | 'medium' | 'low';
export type PathwayStepType = 'education' | 'skill' | 'experience' | 'certification';
export type ResourceType = 'course' | 'book' | 'article' | 'video' | 'tool';
export type TimelineEventType = 'course' | 'internship' | 'project' | 'certification' | 'application';
export type TimelineStatus = 'upcoming' | 'in-progress' | 'completed';
export type ApplicationStatus = 'draft' | 'submitted' | 'interview' | 'offer' | 'rejected';
export type ResumeSectionType = 'header' | 'summary' | 'experience' | 'education' | 'skills' | 'projects';
export type CoverLetterTone = 'professional' | 'enthusiastic' | 'casual' | 'formal';
export type InterviewCategory = 'behavioral' | 'technical' | 'situational' | 'case-study';
export type MilestoneType = 'skill' | 'application' | 'interview' | 'learning' | 'certification' | 'project';
export type MilestoneStatus = 'pending' | 'in-progress' | 'completed' | 'overdue';
export type ActivityType = 'skill_completed' | 'application_sent' | 'interview_scheduled' | 'job_saved' | 'career_bookmarked' | 'resume_updated' | 'milestone_achieved';
export type JobSortOption = 'match' | 'date' | 'salary' | 'company';

// Utility Types
export interface SalaryRange {
  min: number;
  max: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}
