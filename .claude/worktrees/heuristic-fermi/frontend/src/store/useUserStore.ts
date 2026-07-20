import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, UserProfile, UserPreferences, Job } from '@/types';

interface UserStore {
  user: User;
  savedJobs: Job[];
  updateProfile: (profile: Partial<UserProfile>) => void;
  updatePreferences: (prefs: Partial<UserPreferences>) => void;
  saveJob: (job: Job) => void;
  unsaveJob: (jobId: string) => void;
}

const defaultUser: User = {
  id: 'user-1',
  name: 'Alex Johnson',
  email: 'alex.johnson@example.com',
  profile: {
    title: 'Software Engineer',
    experience: '3-5 years',
    education: "Bachelor's in Computer Science",
    location: 'San Francisco, CA',
    interests: ['AI/ML', 'Web Development', 'Cloud Computing', 'Product Management'],
    skills: [
      { id: 's1', name: 'React', level: 'advanced', category: 'Frontend' },
      { id: 's2', name: 'TypeScript', level: 'advanced', category: 'Languages' },
      { id: 's3', name: 'Node.js', level: 'intermediate', category: 'Backend' },
      { id: 's4', name: 'Python', level: 'intermediate', category: 'Languages' },
      { id: 's5', name: 'AWS', level: 'beginner', category: 'Cloud' },
      { id: 's6', name: 'SQL', level: 'advanced', category: 'Database' },
    ],
    bio: 'Passionate software engineer looking to transition into AI/ML roles.',
  },
  progress: {
    careerMatch: 85,
    skillsCompleted: 12,
    applicationsSubmitted: 3,
    profileCompletion: 78,
    streakDays: 7,
    xpPoints: 1250,
  },
  preferences: {
    notifications: true,
    emailUpdates: true,
    darkMode: true,
    language: 'en',
    jobAlerts: true,
  },
};

export const useUserStore = create<UserStore>()(
  persist(
    (set) => ({
      user: defaultUser,
      savedJobs: [],

      updateProfile: (profileUpdate) =>
        set((state) => ({
          user: {
            ...state.user,
            profile: { ...state.user.profile, ...profileUpdate },
          },
        })),

      updatePreferences: (prefsUpdate) =>
        set((state) => ({
          user: {
            ...state.user,
            preferences: { ...state.user.preferences, ...prefsUpdate } as UserPreferences,
          },
        })),

      saveJob: (job) =>
        set((state) => ({
          savedJobs: state.savedJobs.some((j) => j.id === job.id)
            ? state.savedJobs
            : [...state.savedJobs, job],
        })),

      unsaveJob: (jobId) =>
        set((state) => ({
          savedJobs: state.savedJobs.filter((j) => j.id !== jobId),
        })),
    }),
    { name: 'career-assistant-user' }
  )
);
