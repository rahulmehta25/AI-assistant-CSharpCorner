export interface Skill {
  id: string;
  name: string;
  level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  category: string;
  verified?: boolean;
  endorsements?: number;
}

export interface UserProfile {
  title: string;
  experience: string;
  education: string;
  location: string;
  interests: string[];
  skills: Skill[];
  avatar?: string;
  bio?: string;
}

export interface UserProgress {
  careerMatch: number;
  skillsCompleted: number;
  applicationsSubmitted: number;
  profileCompletion: number;
  streakDays?: number;
  xpPoints?: number;
}

export interface User {
  id: string;
  name: string;
  email: string;
  profile: UserProfile;
  progress: UserProgress;
  preferences?: UserPreferences;
  avatar?: string;
}

export interface UserPreferences {
  notifications: boolean;
  emailUpdates: boolean;
  darkMode: boolean;
  language: string;
  jobAlerts: boolean;
}

export interface Career {
  id: string;
  title: string;
  description: string;
  /** Numeric match score 0-100 */
  match?: number;
  /** Alias for match — some components use matchScore */
  matchScore?: number;
  /** Salary as a display string e.g. "$120k – $160k" */
  salaryRange?: string;
  /** Salary as structured object { min, max } */
  salary?: { min: number; max: number };
  growthRate: string;
  skills: string[];
  category: string;
  demandLevel: 'high' | 'medium' | 'low';
  timeToTransition?: string;
  companies?: string[];
}

export interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  salary: string;
  /** Numeric match score 0-100 */
  match?: number;
  /** Alias for match — some components use matchScore */
  matchScore?: number;
  type: 'full-time' | 'part-time' | 'contract' | 'remote' | 'internship';
  postedDate: string;
  description?: string;
  requirements?: string[];
  benefits?: string[];
  skills?: string[];
  logo?: string;
  remote?: boolean;
  applied?: boolean;
  saved?: boolean;
  source?: string;
}

export interface LearningResource {
  id: string;
  title: string;
  provider: string;
  url: string;
  duration: string;
  level: 'beginner' | 'intermediate' | 'advanced';
  rating: number;
  free: boolean;
  category: string;
  skills: string[];
}

export interface Application {
  id: string;
  jobTitle: string;
  company: string;
  status: 'applied' | 'screening' | 'interview' | 'offer' | 'rejected' | 'withdrawn';
  appliedDate: string;
  lastUpdated: string;
  notes?: string;
  salary?: string;
  location?: string;
}
