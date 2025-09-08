import { Career, Job, StudentPathway, Skill, SkillGap } from '@/types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// API service functions
class ApiService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('API Request failed:', error);
      throw error;
    }
  }

  // Career endpoints
  async getCareers(query?: string, filters?: any): Promise<Career[]> {
    const params = new URLSearchParams();
    if (query) params.append('q', query);
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, String(value));
      });
    }
    
    return this.request<Career[]>(`/api/careers?${params}`);
  }

  async getCareer(id: string): Promise<Career> {
    return this.request<Career>(`/api/careers/${id}`);
  }

  async getCareerRoadmap(id: string): Promise<any> {
    return this.request(`/api/careers/${id}/roadmap`);
  }

  // Job endpoints
  async getJobs(filters?: any): Promise<Job[]> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, String(value));
      });
    }
    
    return this.request<Job[]>(`/api/jobs?${params}`);
  }

  async getJob(id: string): Promise<Job> {
    return this.request<Job>(`/api/jobs/${id}`);
  }

  // Student pathway endpoints
  async getStudentPathway(level: string, grade?: string): Promise<StudentPathway> {
    const params = new URLSearchParams({ level });
    if (grade) params.append('grade', grade);
    
    return this.request<StudentPathway>(`/api/student-pathways?${params}`);
  }

  // Skills endpoints
  async analyzeSkills(skills: string[]): Promise<SkillGap[]> {
    return this.request<SkillGap[]>('/api/skills/analyze', {
      method: 'POST',
      body: JSON.stringify({ skills }),
    });
  }

  async getSkillRecommendations(careerId: string): Promise<Skill[]> {
    return this.request<Skill[]>(`/api/skills/recommendations/${careerId}`);
  }

  // Application endpoints
  async generateResume(data: any): Promise<any> {
    return this.request('/api/applications/resume', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async generateCoverLetter(jobId: string, userProfile: any): Promise<any> {
    return this.request('/api/applications/cover-letter', {
      method: 'POST',
      body: JSON.stringify({ jobId, userProfile }),
    });
  }

  // Profile endpoints
  async updateProfile(profile: any): Promise<any> {
    return this.request('/api/profile', {
      method: 'PUT',
      body: JSON.stringify(profile),
    });
  }
}

export const apiService = new ApiService();

// Mock data for development
export const mockCareers: Career[] = [
  {
    id: '1',
    title: 'Software Engineer',
    description: 'Design, develop, and maintain software applications and systems.',
    match: 92,
    salary: { min: 80000, max: 150000 },
    growth: 'high',
    education: "Bachelor's degree in Computer Science or related field",
    experience: '2-5 years',
    skills: ['JavaScript', 'Python', 'React', 'Node.js', 'SQL'],
    tasks: ['Write clean, maintainable code', 'Debug and troubleshoot issues', 'Collaborate with team members'],
    relatedCareers: ['2', '3', '4'],
  },
  {
    id: '2',
    title: 'Data Scientist',
    description: 'Analyze complex data to help companies make strategic decisions.',
    match: 87,
    salary: { min: 90000, max: 160000 },
    growth: 'high',
    education: "Bachelor's degree in Statistics, Mathematics, or Computer Science",
    experience: '3-6 years',
    skills: ['Python', 'R', 'SQL', 'Machine Learning', 'Statistics'],
    tasks: ['Clean and analyze data', 'Build predictive models', 'Present insights to stakeholders'],
    relatedCareers: ['1', '3', '5'],
  },
  {
    id: '3',
    title: 'UX Designer',
    description: 'Create intuitive and engaging user experiences for digital products.',
    match: 78,
    salary: { min: 70000, max: 130000 },
    growth: 'high',
    education: "Bachelor's degree in Design, Psychology, or related field",
    experience: '2-4 years',
    skills: ['Figma', 'User Research', 'Prototyping', 'Adobe Creative Suite'],
    tasks: ['Conduct user research', 'Create wireframes and prototypes', 'Test user interfaces'],
    relatedCareers: ['1', '2', '4'],
  },
  {
    id: '4',
    title: 'Product Manager',
    description: 'Guide product development from conception to launch and beyond.',
    match: 83,
    salary: { min: 100000, max: 180000 },
    growth: 'high',
    education: "Bachelor's degree in Business, Engineering, or related field",
    experience: '4-7 years',
    skills: ['Strategic Planning', 'Analytics', 'Communication', 'Project Management'],
    tasks: ['Define product roadmap', 'Coordinate cross-functional teams', 'Analyze market trends'],
    relatedCareers: ['1', '2', '3'],
  },
  {
    id: '5',
    title: 'Cybersecurity Analyst',
    description: 'Protect organizations from digital threats and security breaches.',
    match: 89,
    salary: { min: 75000, max: 140000 },
    growth: 'high',
    education: "Bachelor's degree in Cybersecurity, Computer Science, or IT",
    experience: '2-5 years',
    skills: ['Network Security', 'Risk Assessment', 'Incident Response', 'Compliance'],
    tasks: ['Monitor security systems', 'Investigate incidents', 'Implement security measures'],
    relatedCareers: ['1', '2', '6'],
  },
  {
    id: '6',
    title: 'DevOps Engineer',
    description: 'Bridge development and operations to improve deployment and infrastructure.',
    match: 91,
    salary: { min: 85000, max: 155000 },
    growth: 'high',
    education: "Bachelor's degree in Computer Science or Engineering",
    experience: '3-6 years',
    skills: ['AWS', 'Docker', 'Kubernetes', 'CI/CD', 'Infrastructure as Code'],
    tasks: ['Automate deployments', 'Manage cloud infrastructure', 'Monitor system performance'],
    relatedCareers: ['1', '5', '7'],
  },
];

export const mockJobs: Job[] = [
  {
    id: '1',
    title: 'Frontend Developer',
    company: 'TechCorp',
    location: 'San Francisco, CA',
    salary: '$90,000 - $120,000',
    type: 'full-time',
    description: 'Build amazing user interfaces with React and TypeScript.',
    requirements: ['3+ years React experience', 'TypeScript proficiency', 'CSS expertise'],
    benefits: ['Health insurance', '401k matching', 'Flexible PTO'],
    match: 94,
    postedDate: '2024-01-15',
    applied: false,
    saved: false,
    source: 'LinkedIn',
  },
  {
    id: '2',
    title: 'Full Stack Engineer',
    company: 'StartupXYZ',
    location: 'Remote',
    salary: '$80,000 - $110,000',
    type: 'full-time',
    description: 'Work on both frontend and backend systems using modern technologies.',
    requirements: ['JavaScript/TypeScript', 'Node.js', 'Database design', 'API development'],
    benefits: ['Remote work', 'Stock options', 'Learning budget'],
    match: 89,
    postedDate: '2024-01-12',
    applied: true,
    saved: true,
    source: 'Indeed',
  },
  {
    id: '3',
    title: 'Software Engineering Intern',
    company: 'BigTech Inc',
    location: 'Seattle, WA',
    salary: '$35/hour',
    type: 'internship',
    description: 'Summer internship program for computer science students.',
    requirements: ['CS major', 'Programming skills', 'Problem-solving abilities'],
    benefits: ['Mentorship', 'Housing stipend', 'Return offer potential'],
    match: 87,
    postedDate: '2024-01-10',
    applied: false,
    saved: true,
    source: 'Company Website',
  },
];