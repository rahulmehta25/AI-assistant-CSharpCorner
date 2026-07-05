# AI Career Assistant Platform

A comprehensive AI-powered career development platform that provides personalized career roadmaps, job matching, skill assessments, and application assistance.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Load Balancer / CDN                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
            ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
            │   Frontend    │  │   Frontend    │  │   Frontend    │
            │ (React/Vite)  │  │ (React/Vite)  │  │   (Nginx)     │
            │   Port 3000   │  │   Port 3000   │  │   Port 80     │
            └───────────────┘  └───────────────┘  └───────────────┘
                    │                  │                  │
                    └──────────────────┼──────────────────┘
                                       ▼
            ┌─────────────────────────────────────────────────────┐
            │                  API Gateway                         │
            │              (FastAPI Backend)                       │
            │                  Port 8001                           │
            └─────────────────────────────────────────────────────┘
                    │                  │                  │
          ┌─────────┘                  │                  └─────────┐
          ▼                            ▼                            ▼
  ┌───────────────┐          ┌───────────────┐          ┌───────────────┐
  │  PostgreSQL   │          │     Redis     │          │  Background   │
  │   Database    │          │    Cache      │          │    Worker     │
  │   Port 5432   │          │  Port 6379    │          │  (Celery)     │
  └───────────────┘          └───────────────┘          └───────────────┘
                                                                │
                                                                ▼
                                                        ┌───────────────┐
                                                        │   OpenAI API  │
                                                        │   (GPT-4)     │
                                                        └───────────────┘
```

## Features

### Career Development
- **Personalized Roadmaps**: AI-generated career progression paths from current to target role
- **Skill Gap Analysis**: Identify missing skills with prioritized learning plans
- **Milestone Tracking**: Timeline-based progress tracking with achievements
- **Student Pathways**: Customized education paths for high school and college students

### Job Search & Matching
- **Smart Job Matching**: AI-powered compatibility scoring
- **Real-time Scraping**: Aggregate jobs from multiple sources
- **Advanced Filtering**: Location, salary, remote, experience level
- **Application Tracking**: Monitor your job applications

### AI Assistant
- **Career Advisor**: Interactive GPT-4 powered guidance
- **Resume Analysis**: ATS optimization and keyword suggestions
- **Cover Letter Generation**: Customized templates for each application
- **Interview Preparation**: Role-specific question preparation

### Gamification
- **Achievements**: Unlock badges for career milestones
- **Progress Tracking**: Visual career journey dashboard
- **Skill Assessments**: Test and validate your competencies

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, Vite, TypeScript, TailwindCSS, Shadcn/UI |
| Backend | Python 3.11+, FastAPI, Pydantic |
| Database | PostgreSQL 16, SQLAlchemy 2.0, Alembic |
| Cache | Redis 7 |
| AI/ML | OpenAI GPT-4, LangChain |
| Queue | Redis-based job queue |
| Monitoring | Prometheus, Grafana |
| Containers | Docker, Docker Compose |

## Quick Start

### Prerequisites
- Docker & Docker Compose (recommended)
- Or: Python 3.11+, Node.js 20+, PostgreSQL 16, Redis 7

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/rahulmehta25/AI-assistant-CSharpCorner.git
cd AI-assistant-CSharpCorner

# Copy environment file
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8001
# Grafana: http://localhost:3001
```

### Option 2: Development Setup

```bash
# Clone the repository
git clone https://github.com/rahulmehta25/AI-assistant-CSharpCorner.git
cd AI-assistant-CSharpCorner

# Start dependencies with Docker
docker-compose -f docker-compose.dev.yml up postgres redis -d

# Backend setup
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
pip install -r requirements-prod.txt

# Run migrations
cd backend && alembic upgrade head && cd ..

# Seed database
python scripts/seed_database.py

# Start backend
python api_bridge.py

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

### Option 3: Local Development (No Docker)

```bash
# Install PostgreSQL and Redis locally
# macOS: brew install postgresql redis
# Ubuntu: sudo apt install postgresql redis

# Set up database
createdb career_assistant
psql career_assistant < backend/db/schema.sql

# Follow steps from Option 2 for Python and Node setup
```

## Project Structure

```
AI-assistant-CSharpCorner/
├── frontend/                   # React/Vite frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Route pages
│   │   ├── services/          # API services
│   │   └── store/             # State management
│   ├── Dockerfile             # Frontend container
│   └── nginx.conf             # Production nginx config
│
├── backend/                    # Backend infrastructure
│   ├── db/
│   │   └── schema.sql         # PostgreSQL schema
│   ├── models/                # SQLAlchemy models
│   ├── migrations/            # Alembic migrations
│   ├── services/
│   │   ├── cache.py           # Redis caching
│   │   └── queue.py           # Job queue
│   └── workers/
│       └── queue_worker.py    # Background worker
│
├── modules/                    # Core business logic
│   ├── career_assistant_core.py
│   ├── career_roadmap_engine.py
│   ├── job_scraper.py
│   ├── recommendation_engine.py
│   ├── skills_assessment.py
│   └── student_pathways.py
│
├── data/                       # Data files
│   ├── careers/               # Career definitions (O*NET)
│   ├── education_pathways/    # Student pathway templates
│   └── roadmap_templates/     # Roadmap templates
│
├── monitoring/                 # Observability
│   ├── prometheus/
│   │   └── prometheus.yml
│   └── grafana/
│       └── dashboards/
│
├── scripts/
│   └── seed_database.py       # Database seeder
│
├── docker-compose.yml          # Production compose
├── docker-compose.dev.yml      # Development compose
├── Dockerfile.backend          # Backend image
├── Dockerfile.frontend         # Frontend image
├── api_bridge.py               # FastAPI application
└── requirements*.txt           # Python dependencies
```

## API Reference

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/careers` | List all careers |
| GET | `/api/careers/{id}` | Get career details |
| POST | `/api/careers/search` | Search careers |
| POST | `/api/careers/roadmap` | Generate career roadmap |
| POST | `/api/profile/analyze` | Analyze user profile |
| POST | `/api/jobs/search` | Search for jobs |
| POST | `/api/jobs/match` | Get job matches for user |
| POST | `/api/skills/analyze` | Analyze skills |
| POST | `/api/skills/gap` | Skill gap analysis |
| POST | `/api/applications/resume` | Generate resume |
| POST | `/api/applications/cover-letter` | Generate cover letter |
| POST | `/api/student-pathways` | Generate student pathway |
| GET | `/api/stats` | Platform statistics |
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

### Example Request

```bash
# Get career recommendations
curl -X POST http://localhost:8001/api/profile/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "experience": "3 years",
    "skills": ["Python", "React", "SQL"],
    "interests": ["AI/ML", "Cloud"],
    "career_goals": ["Senior Engineer", "Tech Lead"]
  }'
```

## Database Migrations

```bash
# Create a new migration
cd backend
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Monitoring

### Prometheus Metrics
- Request rate, latency, and error rate
- AI token usage and cache hit rate
- Job queue depth and processing time
- Database connection pool stats

### Grafana Dashboard
Access at `http://localhost:3001` (default: admin/admin)
- API performance overview
- AI operations metrics
- System health indicators

## Environment Variables

See `.env.example` for all available options. Key variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for AI features | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `SECRET_KEY` | JWT signing key | Yes |
| `CORS_ORIGINS` | Allowed CORS origins | No |

## Deployment

### Production Checklist
- [ ] Set strong `SECRET_KEY`
- [ ] Configure `CORS_ORIGINS` for your domain
- [ ] Set up SSL/TLS certificates
- [ ] Configure proper database credentials
- [ ] Set up log aggregation
- [ ] Configure alerting in Grafana
- [ ] Enable rate limiting
- [ ] Set up backup strategy

### Docker Production

```bash
# Build and deploy
docker-compose -f docker-compose.yml up -d --build

# Scale workers
docker-compose -f docker-compose.yml up -d --scale worker=3

# Update with zero downtime
docker-compose -f docker-compose.yml up -d --no-deps --build backend
```

## Development

### Makefile Commands

The project includes a comprehensive Makefile for common tasks:

```bash
# Show all available commands
make help

# Development servers
make dev              # Start both backend and frontend
make dev-backend      # Start backend only (port 8001)
make dev-frontend     # Start frontend only (port 8080)

# Testing
make test             # Run all tests
make test-backend     # Backend tests only
make test-frontend    # Frontend tests only

# Coverage
make coverage         # Generate coverage reports
make coverage-backend # Backend coverage (htmlcov/)
make coverage-frontend# Frontend coverage (frontend/coverage/)

# Code Quality
make lint             # Run all linters
make format           # Format all code
make typecheck        # Run type checking

# Build
make build            # Build frontend for production
make install          # Install all dependencies
make install-dev      # Install with pre-commit hooks
make clean            # Clean build artifacts
```

### Running Tests

```bash
# Using Make (recommended)
make test
make coverage

# Python tests directly
pytest tests/ -v
pytest tests/ --cov=modules --cov-report=html

# Frontend tests directly
cd frontend && npm run test:run
cd frontend && npm run test:coverage
```

### Code Quality

```bash
# Using Make (recommended)
make lint
make format

# Python linting with Ruff
ruff check .
ruff format .

# Frontend linting
cd frontend && npm run lint
cd frontend && npm run typecheck
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
make install-dev
# or
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## CI/CD Pipeline

The project uses GitHub Actions for continuous integration:

1. **Backend Lint** - Ruff linter and formatter checks
2. **Backend Test** - pytest with coverage reporting
3. **Frontend Lint** - ESLint and TypeScript checks
4. **Frontend Test** - Vitest with coverage reporting
5. **Frontend Build** - Production build verification
6. **Integration Check** - Verify all components work together

All checks must pass before merging to main/develop branches.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

**Rahul Mehta** - [GitHub](https://github.com/rahulmehta25)

## Acknowledgments

- Originally developed for C# Corner platform
- Powered by OpenAI GPT-4 and LangChain
- Career data sourced from O*NET Online
- Built with React, FastAPI, and modern cloud-native technologies
