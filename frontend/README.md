# AI Career Assistant - Frontend

## Overview

AI-powered career guidance platform that helps students and professionals discover their ideal career path, develop skills, and find the perfect job opportunities.

## Features

- **Career Explorer**: Browse 100+ O*NET careers with detailed roadmaps
- **Student Pathways**: Grade-specific guidance for high school and college students  
- **Job Search**: Live job listings with AI-powered matching
- **Skills Analysis**: Gap analysis and personalized learning paths
- **Application Assistant**: Resume and cover letter generation
- **Progress Tracking**: Milestones and achievement monitoring

## Tech Stack

- **Framework**: React 18 + Vite
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: Zustand
- **API Calls**: React Query
- **Routing**: React Router v6
- **Charts**: Recharts

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python backend running on http://localhost:7860

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at http://localhost:5173

### Environment Variables

Create a `.env` file in the root directory:

```env
VITE_API_URL=http://localhost:7860
VITE_APP_NAME="AI Career Assistant"
```

## Project Structure

```
src/
├── components/     # Reusable UI components
├── pages/         # Page components
├── services/      # API services
├── hooks/         # Custom React hooks
├── store/         # State management
├── utils/         # Utility functions
└── types/         # TypeScript types
```

## Backend Integration

The frontend connects to a Python/Gradio backend with these endpoints:

- `/api/profile` - User profile management
- `/api/careers` - Career data and roadmaps
- `/api/student-pathways` - Student guidance
- `/api/jobs` - Job search and matching
- `/api/skills` - Skills analysis
- `/api/applications` - Resume/cover letter generation

## Development

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linting
npm run lint

# Type checking
npm run type-check
```

## License

MIT