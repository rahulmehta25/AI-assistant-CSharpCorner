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
    
    const response = await this.request<{careers: Career[], total: number}>(`/api/careers?${params}`);
    return response.careers;
  }

  async searchCareers(query: string): Promise<Career[]> {
    const response = await this.request<{results: Career[], count: number}>('/api/careers/search', {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
    return response.results;
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