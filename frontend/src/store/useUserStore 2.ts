import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User, Career, Job, Application } from '@/types';

interface UserState {
  user: User | null;
  bookmarkedCareers: Career[];
  savedJobs: Job[];
  applications: Application[];
  currentPathway: any | null;
  
  // Actions
  setUser: (user: User) => void;
  updateProfile: (profile: Partial<User['profile']>) => void;
  updatePreferences: (preferences: Partial<User['preferences']>) => void;
  updateProgress: (progress: Partial<User['progress']>) => void;
  
  // Careers
  bookmarkCareer: (career: Career) => void;
  unbookmarkCareer: (careerId: string) => void;
  
  // Jobs
  saveJob: (job: Job) => void;
  unsaveJob: (jobId: string) => void;
  
  // Applications
  addApplication: (application: Application) => void;
  updateApplication: (id: string, updates: Partial<Application>) => void;
  
  // Pathway
  setCurrentPathway: (pathway: any) => void;
}

// Mock user data for development
const mockUser: User = {
  id: '1',
  name: 'Alex Johnson',
  email: 'alex@example.com',
  avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=face',
  profile: {
    title: 'Computer Science Student',
    experience: 'Entry Level',
    education: "Bachelor's in Computer Science",
    location: 'San Francisco, CA',
    interests: ['Software Development', 'Data Science', 'AI/ML', 'Web Development'],
    skills: [
      { id: '1', name: 'JavaScript', level: 'intermediate', category: 'Programming', isCore: true, verified: false },
      { id: '2', name: 'Python', level: 'intermediate', category: 'Programming', isCore: true, verified: true },
      { id: '3', name: 'React', level: 'beginner', category: 'Frontend', isCore: false, verified: false },
      { id: '4', name: 'Data Analysis', level: 'beginner', category: 'Analytics', isCore: false, verified: false },
    ],
    completedAssessments: ['technical', 'personality', 'interests'],
  },
  preferences: {
    jobType: 'full-time',
    workEnvironment: 'hybrid',
    salary: {
      min: 70000,
      max: 120000,
    },
    industries: ['Technology', 'Fintech', 'Healthcare Tech'],
  },
  progress: {
    careerMatch: 85,
    skillsCompleted: 12,
    applicationsSubmitted: 3,
    assessmentsCompleted: 3,
    profileCompletion: 78,
  },
};

export const useUserStore = create<UserState>()(
  persist(
    (set, get) => ({
      user: mockUser,
      bookmarkedCareers: [],
      savedJobs: [],
      applications: [],
      currentPathway: null,

      setUser: (user) => set({ user }),
      
      updateProfile: (profile) =>
        set((state) => ({
          user: state.user
            ? { ...state.user, profile: { ...state.user.profile, ...profile } }
            : null,
        })),
      
      updatePreferences: (preferences) =>
        set((state) => ({
          user: state.user
            ? { ...state.user, preferences: { ...state.user.preferences, ...preferences } }
            : null,
        })),
      
      updateProgress: (progress) =>
        set((state) => ({
          user: state.user
            ? { ...state.user, progress: { ...state.user.progress, ...progress } }
            : null,
        })),

      bookmarkCareer: (career) =>
        set((state) => ({
          bookmarkedCareers: [...state.bookmarkedCareers, career],
        })),

      unbookmarkCareer: (careerId) =>
        set((state) => ({
          bookmarkedCareers: state.bookmarkedCareers.filter((c) => c.id !== careerId),
        })),

      saveJob: (job) =>
        set((state) => ({
          savedJobs: [...state.savedJobs, { ...job, saved: true }],
        })),

      unsaveJob: (jobId) =>
        set((state) => ({
          savedJobs: state.savedJobs.filter((j) => j.id !== jobId),
        })),

      addApplication: (application) =>
        set((state) => ({
          applications: [...state.applications, application],
        })),

      updateApplication: (id, updates) =>
        set((state) => ({
          applications: state.applications.map((app) =>
            app.id === id ? { ...app, ...updates } : app
          ),
        })),

      setCurrentPathway: (pathway) => set({ currentPathway: pathway }),
    }),
    {
      name: 'career-assistant-user',
    }
  )
);