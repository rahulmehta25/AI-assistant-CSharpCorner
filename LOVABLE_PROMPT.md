# Lovable Frontend Prompt for AI Career Assistant

## Project Overview
Create a modern, responsive Vite + React frontend for an AI-powered Career Assistant platform that integrates with an existing Python/Gradio backend API.

## Backend API Endpoints
The backend runs on `http://localhost:7860` with these main endpoints:
- `/api/profile` - User profile management
- `/api/careers` - Career exploration and roadmaps
- `/api/student-pathways` - Student-specific guidance
- `/api/jobs` - Live job search and matching
- `/api/skills` - Skills analysis and recommendations
- `/api/applications` - Resume and cover letter generation

## Core Features to Implement

### 1. Dashboard (Home)
- User profile card with progress metrics
- Career match percentage visualization
- Recent job recommendations
- Skill gap analysis chart
- Upcoming milestones timeline

### 2. Career Explorer
- Search/filter 100+ O*NET careers
- Career cards with:
  - Title, description, salary range
  - Required skills and education
  - Growth outlook indicators
- Detailed career view with:
  - Complete roadmap visualization
  - Step-by-step progression path
  - Learning resources
  - Related careers

### 3. Student Pathways
- Toggle: High School / College Student
- Grade/year specific guidance
- Course recommendations
- Extracurricular suggestions
- Internship opportunities
- Timeline visualization

### 4. Job Search
- Live job listings from multiple sources
- Advanced filters (location, salary, experience)
- Job match percentage
- One-click apply tracking
- Saved jobs functionality

### 5. Skills Analysis
- Current skills assessment
- Skills gap visualization
- Learning path recommendations
- Progress tracking
- Certification suggestions

### 6. Application Assistant
- Resume builder with templates
- Cover letter generator
- ATS optimization tips
- Download in multiple formats

## Design Requirements

### Color Scheme
```css
--primary: #6366f1 (Indigo)
--secondary: #8b5cf6 (Purple)
--accent: #10b981 (Emerald)
--background: #f9fafb
--text: #111827
--card-bg: #ffffff
```

### Components Needed
- Navigation bar with user avatar
- Sidebar navigation (collapsible)
- Card components for careers/jobs
- Progress bars and charts (use Recharts)
- Modal for detailed views
- Toast notifications
- Loading skeletons
- Search with autocomplete
- Multi-step forms
- Timeline component
- Skills tag pills

### Responsive Design
- Mobile-first approach
- Breakpoints: 640px, 768px, 1024px, 1280px
- Touch-friendly interactions
- Swipeable cards on mobile

## Technical Stack
- Vite + React 18
- TypeScript
- Tailwind CSS
- Shadcn/ui components
- React Query for API state
- React Router v6
- Recharts for visualizations
- React Hook Form
- Zustand for state management
- Framer Motion for animations

## API Integration Pattern
```typescript
// Example API service
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:7860';

export const careerService = {
  async getCareer(id: string) {
    const response = await fetch(`${API_BASE}/api/careers/${id}`);
    return response.json();
  },
  
  async searchCareers(query: string) {
    const response = await fetch(`${API_BASE}/api/careers/search?q=${query}`);
    return response.json();
  }
};
```

## State Management Structure
```typescript
interface AppState {
  user: {
    profile: UserProfile;
    preferences: UserPreferences;
    progress: ProgressMetrics;
  };
  careers: {
    selected: Career | null;
    bookmarked: Career[];
    roadmap: Roadmap | null;
  };
  jobs: {
    listings: Job[];
    applied: Job[];
    saved: Job[];
  };
}
```

## Key Pages/Routes
- `/` - Dashboard
- `/careers` - Career explorer
- `/careers/:id` - Career details
- `/pathways` - Student pathways
- `/jobs` - Job search
- `/jobs/:id` - Job details
- `/skills` - Skills analysis
- `/applications` - Application assistant
- `/profile` - User profile settings

## Performance Requirements
- Lighthouse score > 90
- Lazy load images
- Code splitting by route
- Virtual scrolling for long lists
- Optimistic UI updates
- PWA ready

## Accessibility
- WCAG 2.1 AA compliance
- Keyboard navigation
- Screen reader support
- Focus management
- ARIA labels

## Additional Features
- Dark mode toggle
- Export data (PDF/CSV)
- Share career paths
- Print-friendly views
- Offline support (PWA)
- Real-time notifications

## Sample Component Structure
```
src/
  components/
    layout/
      Header.tsx
      Sidebar.tsx
      Footer.tsx
    careers/
      CareerCard.tsx
      CareerDetails.tsx
      RoadmapVisualization.tsx
    jobs/
      JobCard.tsx
      JobFilters.tsx
      MatchScore.tsx
    common/
      ProgressBar.tsx
      SkillTag.tsx
      LoadingSkeleton.tsx
  pages/
    Dashboard.tsx
    CareerExplorer.tsx
    StudentPathways.tsx
    JobSearch.tsx
    SkillsAnalysis.tsx
  services/
    api.ts
    auth.ts
    careers.ts
    jobs.ts
  hooks/
    useCareer.ts
    useJobs.ts
    useProfile.ts
  store/
    userStore.ts
    careerStore.ts
  utils/
    formatters.ts
    validators.ts
```

## Environment Variables
```
VITE_API_URL=http://localhost:7860
VITE_APP_NAME="AI Career Assistant"
VITE_ENABLE_ANALYTICS=false
```

## Testing Requirements
- Unit tests for utilities
- Component testing with React Testing Library
- E2E tests for critical flows
- Accessibility testing

## Deployment
- Build for production with Vite
- Deploy to Vercel/Netlify
- Environment-specific configs
- CI/CD pipeline ready

## Notes for Integration
- The backend uses Gradio but exposes REST endpoints
- Authentication will be JWT-based
- Real-time updates via WebSocket (future)
- File uploads for resume parsing
- Rate limiting on API calls

Please create a beautiful, modern, and fully functional frontend that connects seamlessly with this backend API. Focus on user experience, performance, and visual appeal. Use modern React patterns, TypeScript for type safety, and ensure the interface is intuitive for students and job seekers.