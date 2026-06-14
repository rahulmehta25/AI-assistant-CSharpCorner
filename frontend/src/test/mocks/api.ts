import { vi } from "vitest";

export const mockCareers = [
  {
    id: "15-1252.00",
    title: "Software Developers",
    description: "Research, design, and develop computer software.",
    match: 92,
    salary: { min: 96160, max: 168280 },
    growth: "Much faster than average",
    education: "Bachelor's degree",
    experience: "2-5 years",
    skills: ["Python", "JavaScript", "SQL", "React", "AWS"],
    tasks: ["Write code", "Debug software", "Review code"],
    cluster: "Information Technology",
  },
  {
    id: "15-2051.00",
    title: "Data Scientists",
    description: "Develop and implement statistical models.",
    match: 88,
    salary: { min: 86928, max: 152124 },
    growth: "Faster than average",
    education: "Master's degree",
    experience: "2-5 years",
    skills: ["Python", "Statistics", "Machine Learning"],
    tasks: ["Analyze data", "Build models"],
    cluster: "Information Technology",
  },
];

export const mockJobs = [
  {
    id: "job1",
    title: "Senior Software Engineer",
    company: "Tech Corp",
    location: "San Francisco, CA",
    salary: { min: 150000, max: 200000 },
    type: "full-time",
    description: "Join our engineering team...",
    requirements: ["5+ years experience", "Python/JavaScript"],
    posted: "2026-03-10",
    match: 95,
  },
  {
    id: "job2",
    title: "Full Stack Developer",
    company: "Startup Inc",
    location: "Remote",
    salary: { min: 120000, max: 160000 },
    type: "full-time",
    description: "Build amazing products...",
    requirements: ["3+ years experience", "React/Node.js"],
    posted: "2026-03-08",
    match: 88,
  },
];

export const mockUser = {
  id: "user123",
  name: "Test User",
  email: "test@example.com",
  profile: {
    title: "Software Engineer",
    experience: 3,
    education: "Bachelor's in Computer Science",
    location: "San Francisco, CA",
    interests: ["Web Development", "Machine Learning"],
    skills: [
      { id: "1", name: "Python", level: "advanced" },
      { id: "2", name: "JavaScript", level: "intermediate" },
      { id: "3", name: "React", level: "intermediate" },
    ],
  },
  preferences: {
    jobType: "full-time",
    workEnvironment: "hybrid",
    salaryRange: { min: 120000, max: 180000 },
  },
  progress: {
    careerMatch: 85,
    skillsCompleted: 12,
    applications: 5,
    profileCompletion: 75,
  },
};

export const mockApiService = {
  getCareers: vi.fn().mockResolvedValue({ careers: mockCareers, total: 2 }),
  getCareer: vi.fn().mockResolvedValue(mockCareers[0]),
  searchCareers: vi.fn().mockResolvedValue({ results: mockCareers, count: 2 }),
  getJobs: vi.fn().mockResolvedValue({ jobs: mockJobs, count: 2 }),
  analyzeSkills: vi.fn().mockResolvedValue({
    currentLevel: "intermediate",
    gaps: ["AWS", "Kubernetes"],
    recommendations: ["Take AWS course"],
  }),
};
