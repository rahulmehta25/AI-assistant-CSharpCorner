# Architecture Review: AI Career Assistant Platform

**Review Date:** 2026-03-13
**Reviewer:** Architecture Review Agent
**Version:** 2.0.0

---

## Executive Summary

The AI Career Assistant Platform is a full-stack application combining a FastAPI Python backend with a React/TypeScript frontend. The architecture demonstrates good separation of concerns but has several areas requiring attention, particularly around dual API implementations, inconsistent patterns, and production readiness.

---

## 1. FastAPI Backend Structure

### 1.1 Application Entry Points

| Finding | Severity | Location |
|---------|----------|----------|
| **Dual API implementations exist** - `api_bridge.py` (standalone) and `api/` (modular) | **High** | `api_bridge.py:1-463`, `api/app.py` |
| `run_api.py` references `api.app:app` but `api_bridge.py` runs independently | Medium | `run_api.py:19` |
| No clear documentation on which entry point is canonical | Medium | Project root |

**Details:**
- `api_bridge.py` contains a monolithic FastAPI application with all endpoints inline
- `api/` directory contains a properly structured modular API with routers
- This creates confusion about which API is the production implementation

### 1.2 Router Organization

The modular API (`api/`) follows proper FastAPI patterns:

```
api/
├── __init__.py
├── app.py                 # Main app factory
├── dependencies/
│   ├── auth.py           # Auth dependencies
│   ├── rate_limit.py     # Rate limiting
│   └── common.py         # Shared deps
└── routes/
    ├── auth.py           # Authentication
    ├── careers.py        # Career endpoints
    ├── conversation.py   # Chat/AI
    ├── health.py         # Health checks
    ├── interview.py      # Interview prep
    ├── jobs.py           # Job search
    ├── resume.py         # Resume analysis
    └── student.py        # Student pathways
```

| Finding | Severity | Location |
|---------|----------|----------|
| Good router separation by domain | - | `api/routes/` |
| Dependencies properly isolated | - | `api/dependencies/` |
| Missing versioning strategy (no `/v1/` prefix) | Low | `api/routes/*.py` |

### 1.3 Middleware Configuration

| Finding | Severity | Location |
|---------|----------|----------|
| CORS configured but duplicated across files | Medium | `api_bridge.py:48-54`, `api/app.py:90-91` |
| Prometheus instrumentation conditionally enabled | Low | `api_bridge.py:40-42` |
| Missing request ID middleware for tracing | Medium | `api/app.py` |
| No compression middleware | Low | `api/app.py` |

---

## 2. LangChain Integration Patterns

### 2.1 AI Service Architecture

| Finding | Severity | Location |
|---------|----------|----------|
| Clean abstraction via `AIService` class | - | `services/ai_service.py:30-376` |
| Lazy initialization pattern (good) | - | `services/ai_service.py:41-44` |
| Streaming support implemented | - | `services/ai_service.py:232-257` |
| Pre-built prompt templates (career advisor, resume, etc.) | - | `services/ai_service.py:261-371` |

**Architecture:**
```
AIService (services/ai_service.py)
├── LLM Management (ChatOpenAI instances)
├── Prompt Templates (ChatPromptTemplate)
├── Chain Builders (build_chain, build_structured_chain)
├── Execution Methods (invoke, stream)
└── Domain Prompts (career advisor, resume analysis, etc.)
```

### 2.2 LangChain Usage Issues

| Finding | Severity | Location |
|---------|----------|----------|
| **Multiple OpenAI client instantiation patterns** - inconsistent across modules | **High** | `modules/recommendation_engine.py:134-149`, `modules/industry_trends.py:176-178` |
| Direct OpenAI client used alongside LangChain in same modules | Medium | `modules/recommendation_engine.py:137-141` |
| LangChain imports scattered with fallback patterns | Medium | `services/ai_service.py:18-27` |
| No centralized prompt management | Medium | Multiple files |

**Example of inconsistency:**
- `services/ai_service.py` uses LangChain's `ChatOpenAI`
- `modules/recommendation_engine.py` uses both direct `OpenAI()` and `ChatOpenAI`
- Each module handles API key retrieval independently

### 2.3 Conversation Memory

| Finding | Severity | Location |
|---------|----------|----------|
| Good context windowing implementation | - | `services/conversation_service.py:136-139` |
| Automatic summarization for long conversations | - | `services/conversation_service.py:142-180` |
| Conversations stored in Redis cache (7 days TTL) | - | `services/conversation_service.py:62-67` |
| No database persistence for long-term history | Medium | `services/conversation_service.py:325-336` |

---

## 3. Frontend Architecture

### 3.1 React/TypeScript Structure

```
frontend/src/
├── components/
│   ├── layout/          # Layout components (Header, Sidebar, Layout)
│   ├── ui/              # shadcn/ui components
│   ├── careers/         # Career-related components
│   ├── dashboard/       # Dashboard components
│   └── jobs/            # Job-related components
├── pages/               # Route pages
├── hooks/               # Custom hooks
├── lib/                 # Utilities
├── test/                # Test utilities
└── types/               # TypeScript types
```

| Finding | Severity | Location |
|---------|----------|----------|
| Good component organization | - | `frontend/src/components/` |
| TypeScript types well-defined | - | `frontend/src/types/index.ts` |
| Using shadcn/ui component library | - | `frontend/src/components/ui/` |
| Test files co-located with components | - | `*.test.tsx` files |

### 3.2 State Management

| Finding | Severity | Location |
|---------|----------|----------|
| TanStack Query for server state | - | `frontend/src/App.tsx:4` |
| No global state management (Redux, Zustand) | Low | N/A |
| **AI chat uses local mock data instead of API** | **High** | `frontend/src/pages/AIAssistant.tsx:217-307` |
| Form state handled locally per component | - | Various pages |

**Critical Issue:**
The `AIAssistant.tsx` page simulates AI responses with hardcoded logic (`generateResponse` function) instead of calling the backend API. This bypasses all backend AI services.

### 3.3 Routing & Navigation

| Finding | Severity | Location |
|---------|----------|----------|
| React Router v6 with nested routes | - | `frontend/src/App.tsx:31-49` |
| Command palette for navigation | - | `frontend/src/components/CommandPalette.tsx` |
| Error boundary implemented | - | `frontend/src/components/ui/error-boundary.tsx` |
| Several placeholder routes ("Coming Soon") | Low | `frontend/src/App.tsx:44-48` |

---

## 4. API Contract Analysis

### 4.1 Endpoint Documentation

| Finding | Severity | Location |
|---------|----------|----------|
| OpenAPI/Swagger auto-generated by FastAPI | - | Built-in |
| Pydantic models for request/response validation | - | `models/*.py` |
| Missing explicit API versioning | Medium | All routes |

### 4.2 Request/Response Models

| Finding | Severity | Location |
|---------|----------|----------|
| Comprehensive Pydantic models | - | `models/` directory |
| Field validation with constraints | - | `models/resume.py:23` (min_length) |
| Good use of Optional fields with defaults | - | `models/*.py` |
| Some models lack description metadata | Low | Various |

### 4.3 API Inconsistencies

| Finding | Severity | Location |
|---------|----------|----------|
| **Different endpoint naming between api_bridge.py and api/** | **High** | `api_bridge.py` vs `api/routes/` |
| Inconsistent response envelope patterns | Medium | Various endpoints |
| Some endpoints return raw dicts, others use models | Medium | `api_bridge.py:450-458` |

---

## 5. Data Persistence

### 5.1 Database Schema

| Finding | Severity | Location |
|---------|----------|----------|
| Comprehensive PostgreSQL schema | - | `backend/db/schema.sql` |
| Proper use of UUIDs, indexes, and constraints | - | `backend/db/schema.sql:12-26` |
| JSONB columns for flexible data (skills, preferences) | - | `backend/db/schema.sql:51-54` |
| Audit logging table | - | `backend/db/schema.sql:395-406` |
| Triggers for updated_at timestamps | - | `backend/db/schema.sql:416-454` |

**Schema Structure:**
```
Core: users, career_profiles
Progress: roadmaps, roadmap_milestones
Jobs: saved_jobs, applications
AI: conversations, conversation_messages, ai_response_cache
Assessment: skill_assessments, skill_assessment_questions
Reference: careers, skills_taxonomy
Infrastructure: job_queue, audit_log
```

### 5.2 Database Issues

| Finding | Severity | Location |
|---------|----------|----------|
| **SQLAlchemy models not fully implemented** | **High** | `backend/models/` |
| Schema exists but ORM layer incomplete | High | `backend/models/base.py` |
| SQLite fallback still referenced | Medium | `core/config.py:59-60` |
| No Alembic migrations beyond initial | Medium | `backend/migrations/` |

### 5.3 Caching Strategy

| Finding | Severity | Location |
|---------|----------|----------|
| Redis used for caching and rate limiting | - | `core/cache.py` |
| Cache namespaces properly defined | - | `core/cache.py` (CacheNamespace enum) |
| Conversation cache TTL: 7 days | - | `services/conversation_service.py:67` |
| Resume analysis cache uses MD5 hash | - | `services/resume_service.py:72-73` |
| AI response cache table in PostgreSQL | - | `backend/db/schema.sql:372-389` |

---

## 6. AI Service Abstraction

### 6.1 Service Layer Pattern

| Finding | Severity | Location |
|---------|----------|----------|
| Clean service layer (`services/`) | - | `services/*.py` |
| Global singleton instances | - | `services/ai_service.py:375` |
| Lazy initialization pattern | - | `services/ai_service.py:41-44` |

### 6.2 Module Coupling Issues

| Finding | Severity | Location |
|---------|----------|----------|
| **Modules directly access OpenAI instead of using AIService** | **High** | `modules/recommendation_engine.py`, `modules/industry_trends.py` |
| Tight coupling between modules and environment variables | Medium | All modules |
| No dependency injection pattern | Medium | All modules |

**Recommended Pattern:**
```python
# Current (problematic)
class RecommendationEngine:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = OpenAI(api_key=api_key)

# Recommended
class RecommendationEngine:
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
```

---

## 7. Configuration Management

### 7.1 Environment Configuration

| Finding | Severity | Location |
|---------|----------|----------|
| Pydantic Settings for config | - | `core/config.py` |
| Comprehensive .env.example | - | `.env.example` |
| Cached settings singleton | - | `core/config.py:117-120` |
| CORS origins from env (comma-separated) | - | `core/config.py:93-98` |

### 7.2 Configuration Issues

| Finding | Severity | Location |
|---------|----------|----------|
| Default secret key in code | **Critical** | `core/config.py:40-42` |
| Hardcoded CORS origins in api_bridge.py | Medium | `api_bridge.py:50` |
| Legacy config_manager.py duplicates Settings | Low | `modules/config_manager.py` |
| Feature flags defined but not consistently used | Low | `.env.example:175-181` |

---

## 8. Docker & Infrastructure

### 8.1 Container Architecture

```
docker-compose.yml
├── postgres       # Database
├── redis          # Cache & Queue
├── backend        # FastAPI
├── frontend       # React (nginx)
├── worker         # Background jobs
├── prometheus     # Metrics
└── grafana        # Dashboards
```

| Finding | Severity | Location |
|---------|----------|----------|
| Well-structured multi-container setup | - | `docker-compose.yml` |
| Health checks for all services | - | `docker-compose.yml:19-23, 39-44` |
| Named volumes for persistence | - | `docker-compose.yml:164-172` |
| Development compose file exists | - | `docker-compose.dev.yml` |

### 8.2 Infrastructure Issues

| Finding | Severity | Location |
|---------|----------|----------|
| Default Grafana credentials in compose | Medium | `docker-compose.yml:149-150` |
| Worker references module that may not exist | Low | `docker-compose.yml:107` |
| No production-specific compose override | Medium | Project root |

---

## 9. Testing Infrastructure

| Finding | Severity | Location |
|---------|----------|----------|
| Pytest configuration with markers | - | `pyproject.toml:9-26` |
| Coverage configured (70% threshold) | - | `pyproject.toml:32-51` |
| Unit test structure exists | - | `tests/unit/` |
| Integration test structure exists | - | `tests/integration/` |
| Frontend tests with Vitest | - | `frontend/*.test.tsx` |
| Test fixtures in conftest.py | - | `tests/conftest.py` |

---

## Prioritized Action Plan

### Critical (Immediate)

1. **Remove hardcoded default secret key** (`core/config.py:40-42`)
   - Fail fast if SECRET_KEY not set in production

2. **Consolidate API implementations** (`api_bridge.py` vs `api/`)
   - Choose one canonical implementation
   - Remove or deprecate the other

3. **Complete database ORM layer** (`backend/models/`)
   - Implement SQLAlchemy models matching schema
   - Remove SQLite fallback for production

4. **Connect frontend to real backend API** (`frontend/src/pages/AIAssistant.tsx:217-307`)
   - Replace mock `generateResponse` with API calls

### High Priority (This Sprint)

5. **Centralize OpenAI client management**
   - Route all AI calls through `AIService`
   - Remove direct OpenAI instantiation from modules

6. **Implement proper dependency injection**
   - Use FastAPI's dependency system consistently
   - Inject services rather than importing singletons

7. **Add API versioning** (`/api/v1/` prefix)
   - Prepare for future breaking changes

### Medium Priority (Next Sprint)

8. **Add request ID middleware** for distributed tracing
9. **Implement proper database migrations** with Alembic
10. **Standardize response envelope** across all endpoints
11. **Add compression middleware** for large responses
12. **Configure production Docker overrides**

### Low Priority (Backlog)

13. Clean up legacy `modules/config_manager.py`
14. Add API documentation metadata to all Pydantic models
15. Implement feature flag system consistently
16. Add Sentry integration for error tracking

---

## Architecture Diagram

```
                                 +------------------+
                                 |   React/Vite     |
                                 |   Frontend       |
                                 +--------+---------+
                                          |
                                          | HTTP/REST
                                          v
+------------------+            +------------------+            +------------------+
|   Prometheus     |<-----------|   FastAPI        |----------->|   PostgreSQL     |
|   /Grafana       |  metrics   |   Backend        |   SQL      |   Database       |
+------------------+            +--------+---------+            +------------------+
                                         |
                          +--------------+--------------+
                          |              |              |
                          v              v              v
                   +------------+ +------------+ +------------+
                   |   Redis    | |   OpenAI   | |  Worker    |
                   |   Cache    | |   API      | |  Queue     |
                   +------------+ +------------+ +------------+
```

---

*Review completed: 2026-03-13*
