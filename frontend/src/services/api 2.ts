import { Career, Job, StudentPathway, Skill, SkillGap } from '@/types';
import { staticApiService } from './staticApi';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const USE_STATIC_DATA = true; // Always use static data for now until backend is deployed

// API service with static data fallback
class ApiService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    // If using static data or in production, use static service
    if (USE_STATIC_DATA || import.meta.env.PROD) {
      return this.handleStaticRequest<T>(endpoint, options);
    }

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
      console.error('API Request failed, falling back to static data:', error);
      // Fallback to static data on error
      return this.handleStaticRequest<T>(endpoint, options);
    }
  }

  private async handleStaticRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
    // Parse endpoint and route to static service
    if (endpoint.includes('/careers') && !endpoint.includes('/search')) {
      if (endpoint.includes('/')) {
        const id = endpoint.split('/').pop();
        if (id && id !== 'careers') {
          const career = await staticApiService.getCareer(id);
          return career as T;
        }
      }
      const result = await staticApiService.getCareers();
      return result.careers as T;
    }

    if (endpoint.includes('/careers/search')) {
      const body = options?.body ? JSON.parse(options.body as string) : {};
      const result = await staticApiService.searchCareers(body.query || '');
      return result.results as T;
    }

    if (endpoint.includes('/jobs')) {
      const jobs = await staticApiService.getJobs();
      return jobs as T;
    }

    if (endpoint.includes('/student-pathways')) {
      const pathway = await staticApiService.getStudentPathway('college');
      return pathway as T;
    }

    if (endpoint.includes('/skills/analyze')) {
      const body = options?.body ? JSON.parse(options.body as string) : {};
      const gaps = await staticApiService.analyzeSkills(body.skills || []);
      return gaps as T;
    }

    if (endpoint.includes('/profile/analyze')) {
      const body = options?.body ? JSON.parse(options.body as string) : {};
      const analysis = await staticApiService.analyzeProfile(body);
      return analysis as T;
    }

    if (endpoint.includes('/stats')) {
      const stats = await staticApiService.getStats();
      return stats as T;
    }

    // Default empty response
    return {} as T;
  }

  // Career endpoints
  async getCareers(query?: string, filters?: any): Promise<Career[]> {
    if (USE_STATIC_DATA) {
      const result = await staticApiService.getCareers(query, filters);
      return result.careers;
    }

    const params = new URLSearchParams();
    if (query) params.append('q', query);
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, String(value));
      });
    }
    
    const response = await this.request<{ careers: Career[], total: number }>(`/api/careers?${params}`);
    return response.careers;
  }

  async getCareer(id: string): Promise<Career> {
    if (USE_STATIC_DATA) {
      const career = await staticApiService.getCareer(id);
      if (!career) throw new Error('Career not found');
      return career;
    }
    return this.request<Career>(`/api/careers/${id}`);
  }

  async getCareerRoadmap(id: string): Promise<any> {
    // For now, return basic roadmap from career data
    const career = await this.getCareer(id);
    return {
      career: career.title,
      phases: [
        { phase: 'Foundation', duration: '6 months', skills: career.skills.slice(0, 3) },
        { phase: 'Advanced', duration: '12 months', skills: career.skills.slice(3, 6) },
        { phase: 'Expert', duration: '6 months', skills: career.skills.slice(6) }
      ]
    };
  }

  async searchCareers(query: string): Promise<{ results: Career[], count: number }> {
    if (USE_STATIC_DATA) {
      return staticApiService.searchCareers(query);
    }
    
    return this.request<{ results: Career[], count: number }>('/api/careers/search', {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
  }

  // Job endpoints
  async getJobs(filters?: any): Promise<Job[]> {
    if (USE_STATIC_DATA) {
      return staticApiService.getJobs(filters?.careerId);
    }

    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, String(value));
      });
    }
    
    return this.request<Job[]>(`/api/jobs?${params}`);
  }

  async getJob(id: string): Promise<Job> {
    if (USE_STATIC_DATA) {
      const jobs = await staticApiService.getJobs();
      const job = jobs.find(j => j.id === id);
      if (!job) throw new Error('Job not found');
      return job;
    }
    return this.request<Job>(`/api/jobs/${id}`);
  }

  async searchJobs(query: string, location?: string): Promise<{ jobs: Job[], count: number }> {
    if (USE_STATIC_DATA) {
      return staticApiService.searchJobs(query, location);
    }

    return this.request<{ jobs: Job[], count: number }>('/api/jobs/search', {
      method: 'POST',
      body: JSON.stringify({ query, location }),
    });
  }

  // Student pathway endpoints
  async getStudentPathway(level: string, grade?: string): Promise<StudentPathway> {
    if (USE_STATIC_DATA) {
      return staticApiService.getStudentPathway(level, grade);
    }

    const params = new URLSearchParams({ level });
    if (grade) params.append('grade', grade);
    
    return this.request<StudentPathway>(`/api/student-pathways?${params}`);
  }

  // Skills endpoints
  async analyzeSkills(skills: string[]): Promise<SkillGap[]> {
    if (USE_STATIC_DATA) {
      return staticApiService.analyzeSkills(skills);
    }

    return this.request<SkillGap[]>('/api/skills/analyze', {
      method: 'POST',
      body: JSON.stringify({ skills }),
    });
  }

  async getSkillRecommendations(careerId: string): Promise<Skill[]> {
    const career = await this.getCareer(careerId);
    return career.skills.map(skill => ({
      id: skill.toLowerCase().replace(/\s+/g, '-'),
      name: skill,
      category: 'Technical',
      level: 'Intermediate'
    }));
  }

  // Application endpoints
  async generateResume(data: any): Promise<any> {
    // Mock resume generation
    return {
      resume: `
${data.name || 'Your Name'}
${data.email || 'email@example.com'}

SUMMARY
${data.experience || 'Experienced professional seeking new opportunities'}

SKILLS
${(data.skills || []).join(', ')}

EXPERIENCE
[Add your experience here]

EDUCATION
${data.education || 'Bachelor\'s Degree'}
      `.trim()
    };
  }

  async generateCoverLetter(jobId: string, userProfile: any): Promise<any> {
    return {
      coverLetter: `
Dear Hiring Manager,

I am writing to express my interest in this position.

[Your cover letter content here]

Sincerely,
${userProfile.name || 'Your Name'}
      `.trim()
    };
  }

  // Profile endpoints
  async updateProfile(profile: any): Promise<any> {
    // Store in localStorage for now
    localStorage.setItem('userProfile', JSON.stringify(profile));
    return profile;
  }

  async analyzeProfile(profile: any): Promise<any> {
    if (USE_STATIC_DATA) {
      return staticApiService.analyzeProfile(profile);
    }

    return this.request('/api/profile/analyze', {
      method: 'POST',
      body: JSON.stringify(profile),
    });
  }

  // Stats endpoint
  async getStats(): Promise<any> {
    if (USE_STATIC_DATA) {
      return staticApiService.getStats();
    }

    return this.request('/api/stats');
  }
}

export const apiService = new ApiService();