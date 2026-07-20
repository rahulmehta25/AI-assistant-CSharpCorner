import type { Career, Job, LearningResource, Application } from '@/types';

// Simulated network delay
const delay = (ms = 400) => new Promise((res) => setTimeout(res, ms));

const mockCareers: Career[] = [
  {
    id: 'c1',
    title: 'AI/ML Engineer',
    description: 'Design and implement machine learning models and AI systems at scale.',
    matchScore: 92,
    salaryRange: '$140,000 - $200,000',
    growthRate: '+23%',
    skills: ['Python', 'TensorFlow', 'PyTorch', 'MLOps', 'SQL'],
    category: 'Engineering',
    demandLevel: 'high',
    timeToTransition: '6-12 months',
    companies: ['Google', 'OpenAI', 'Anthropic', 'Meta'],
  },
  {
    id: 'c2',
    title: 'Senior Full-Stack Engineer',
    description: 'Build end-to-end web applications using modern frameworks and cloud services.',
    matchScore: 88,
    salaryRange: '$130,000 - $180,000',
    growthRate: '+15%',
    skills: ['React', 'Node.js', 'TypeScript', 'PostgreSQL', 'AWS'],
    category: 'Engineering',
    demandLevel: 'high',
    timeToTransition: '3-6 months',
    companies: ['Stripe', 'Airbnb', 'Notion', 'Linear'],
  },
  {
    id: 'c3',
    title: 'Product Manager',
    description: 'Lead cross-functional teams to deliver impactful products users love.',
    matchScore: 74,
    salaryRange: '$120,000 - $170,000',
    growthRate: '+12%',
    skills: ['Strategy', 'Data Analysis', 'Agile', 'User Research', 'SQL'],
    category: 'Product',
    demandLevel: 'high',
    timeToTransition: '6-18 months',
    companies: ['Figma', 'Slack', 'Dropbox', 'HubSpot'],
  },
  {
    id: 'c4',
    title: 'DevOps / Platform Engineer',
    description: 'Build and maintain CI/CD pipelines and cloud infrastructure.',
    matchScore: 68,
    salaryRange: '$125,000 - $175,000',
    growthRate: '+18%',
    skills: ['Kubernetes', 'Terraform', 'Docker', 'AWS', 'Python'],
    category: 'Infrastructure',
    demandLevel: 'high',
    timeToTransition: '4-8 months',
    companies: ['HashiCorp', 'Datadog', 'PagerDuty', 'Cloudflare'],
  },
  {
    id: 'c5',
    title: 'Data Scientist',
    description: 'Extract insights from complex datasets to drive business decisions.',
    matchScore: 81,
    salaryRange: '$115,000 - $160,000',
    growthRate: '+20%',
    skills: ['Python', 'R', 'Statistics', 'SQL', 'Tableau'],
    category: 'Data',
    demandLevel: 'high',
    timeToTransition: '4-10 months',
    companies: ['Netflix', 'Spotify', 'LinkedIn', 'Uber'],
  },
];

const mockJobs: Job[] = [
  {
    id: 'j1',
    title: 'Senior React Developer',
    company: 'Stripe',
    location: 'Remote',
    salary: '$155,000 - $185,000',
    matchScore: 94,
    type: 'remote',
    postedDate: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    skills: ['React', 'TypeScript', 'GraphQL', 'Node.js'],
    remote: true,
  },
  {
    id: 'j2',
    title: 'Full Stack Engineer',
    company: 'Notion',
    location: 'San Francisco, CA',
    salary: '$140,000 - $170,000',
    matchScore: 89,
    type: 'full-time',
    postedDate: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
    skills: ['React', 'Python', 'PostgreSQL', 'TypeScript'],
    remote: false,
  },
  {
    id: 'j3',
    title: 'ML Engineer',
    company: 'Anthropic',
    location: 'San Francisco, CA',
    salary: '$170,000 - $220,000',
    matchScore: 76,
    type: 'full-time',
    postedDate: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    skills: ['Python', 'PyTorch', 'ML Systems', 'Distributed Computing'],
    remote: false,
  },
  {
    id: 'j4',
    title: 'Frontend Engineer',
    company: 'Linear',
    location: 'Remote',
    salary: '$130,000 - $160,000',
    matchScore: 91,
    type: 'remote',
    postedDate: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    skills: ['React', 'TypeScript', 'CSS', 'Performance'],
    remote: true,
  },
];

const mockLearning: LearningResource[] = [
  {
    id: 'l1',
    title: 'Machine Learning Specialization',
    provider: 'Coursera (Andrew Ng)',
    url: 'https://coursera.org',
    duration: '3 months',
    level: 'beginner',
    rating: 4.9,
    free: false,
    category: 'AI/ML',
    skills: ['Python', 'Machine Learning', 'Neural Networks'],
  },
  {
    id: 'l2',
    title: 'TypeScript Deep Dive',
    provider: 'Udemy',
    url: 'https://udemy.com',
    duration: '20 hours',
    level: 'intermediate',
    rating: 4.7,
    free: false,
    category: 'Programming',
    skills: ['TypeScript', 'JavaScript'],
  },
  {
    id: 'l3',
    title: 'AWS Certified Developer',
    provider: 'AWS Training',
    url: 'https://aws.amazon.com/training',
    duration: '2 months',
    level: 'intermediate',
    rating: 4.6,
    free: false,
    category: 'Cloud',
    skills: ['AWS', 'Cloud Computing', 'DevOps'],
  },
];

const mockApplications: Application[] = [
  {
    id: 'a1',
    jobTitle: 'Senior React Developer',
    company: 'Stripe',
    status: 'interview',
    appliedDate: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
    lastUpdated: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
    salary: '$155,000 - $185,000',
    location: 'Remote',
  },
  {
    id: 'a2',
    jobTitle: 'Full Stack Engineer',
    company: 'Notion',
    status: 'screening',
    appliedDate: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    lastUpdated: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
    salary: '$140,000 - $170,000',
    location: 'San Francisco, CA',
  },
  {
    id: 'a3',
    jobTitle: 'Frontend Engineer',
    company: 'Linear',
    status: 'applied',
    appliedDate: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    lastUpdated: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    salary: '$130,000 - $160,000',
    location: 'Remote',
  },
];

export const apiService = {
  getCareers: async (): Promise<Career[]> => {
    await delay();
    return mockCareers;
  },

  getCareerById: async (id: string): Promise<Career | undefined> => {
    await delay();
    return mockCareers.find((c) => c.id === id);
  },

  getJobs: async (): Promise<Job[]> => {
    await delay();
    return mockJobs;
  },

  getLearningResources: async (): Promise<LearningResource[]> => {
    await delay();
    return mockLearning;
  },

  getApplications: async (): Promise<Application[]> => {
    await delay();
    return mockApplications;
  },
};

export default apiService;
