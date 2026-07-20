# AI Career Assistant

An AI-powered career guidance platform that helps students and professionals explore career paths, assess skills, find jobs, and receive personalized AI-driven recommendations.

**Live demo:** Deployed on Vercel — dark-themed, fully navigable, no account required.

---

## What It Does

| Feature | Status | Notes |
|---------|--------|-------|
| Career Explorer (300+ O*NET careers) | Working | Static O*NET data, searchable |
| AI Career Assistant | Working | Powered by Claude via Vercel serverless API |
| Skills Analysis & Gap Identification | Working | Based on user profile |
| Job Search & Listings | Working | Curated job data |
| Career Pathways (structured roadmaps) | Working | Frontend → Full Stack → Data Science |
| Application Tracker | Working | Track applications through the hiring pipeline |
| Learning Hub | Working | Curated courses from top providers |
| Achievements System | Working | Gamified milestone tracking |
| Career Analytics | Working | Charts, metrics, skill progress |
| Profile Management | Working | Edit skills, title, location, education |
| Settings | Working | Theme, notifications, privacy, job preferences |
| Help Center | Working | FAQ + quick navigation |
| User Authentication | Not Implemented | Profile stored in localStorage |
| Real-time Job Scraping | Not Implemented | Backend not deployed to production |
| Persistent Cloud Storage | Not Implemented | localStorage only |

---

## Tech Stack

### Frontend (deployed on Vercel)
- **React 18.3** + **TypeScript 5.8** + **Vite 5.4**
- **Tailwind CSS 3.4** + **shadcn/ui** — component system
- **Zustand 5** — state management
- **React Query 5** — data fetching
- **Framer Motion** — animations
- **Recharts** — analytics charts
- **React Router v6** — client-side routing

### AI Integration
- **Claude (claude-opus-4-6)** via Vercel Edge Function at `/api/chat`
- Full user profile sent as system context on every request
- API key stored as Vercel environment variable (never exposed to browser)

### Python Backend (local only)
- **FastAPI** — REST API (`api_bridge.py`)
- **Gradio** — parallel web UI (`main_integrated.py`)
- **OpenAI GPT-4 + LangChain** — AI modules
- **SQLite** — local data persistence
- **Scikit-learn** — TF-IDF and collaborative filtering
- **BeautifulSoup4 + Selenium** — O*NET scraping

> The Python backend runs locally but is not deployed to production. The frontend uses static O*NET data and the Claude serverless function.

---

## Quickstart

### Frontend (the main product)

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:8080
```

For the AI Assistant to work, create a `.env.local` file:

```env
ANTHROPIC_API_KEY=your_key_here
```

Get your API key at [console.anthropic.com](https://console.anthropic.com).

### Python Backend (optional, local only)

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # Add your OPENAI_API_KEY
python api_bridge.py      # Starts FastAPI on port 8000
```

---

## Deploying to Vercel

1. Push this repo to GitHub
2. Connect the `frontend/` directory to Vercel (or configure `rootDirectory: frontend` in Vercel project settings)
3. Add `ANTHROPIC_API_KEY` as an Environment Variable in the Vercel dashboard
4. Deploy — the `/api/chat` serverless function is picked up automatically

The `vercel.json` in `frontend/` handles SPA routing and API route exclusion.

---

## Project Structure

```
AI-assistant-CSharpCorner/
├── frontend/                    # React/TypeScript frontend (main product)
│   ├── api/
│   │   └── chat.ts              # Vercel Edge Function — Claude AI proxy
│   ├── src/
│   │   ├── pages/               # All page components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── AIAssistant.tsx  # Real Claude integration
│   │   │   ├── CareerExplorer.tsx
│   │   │   ├── JobSearch.tsx
│   │   │   ├── SkillsAnalysis.tsx
│   │   │   ├── Pathways.tsx
│   │   │   ├── Applications.tsx
│   │   │   ├── Learning.tsx
│   │   │   ├── Achievements.tsx
│   │   │   ├── Analytics.tsx
│   │   │   ├── Settings.tsx
│   │   │   ├── Profile.tsx
│   │   │   └── Help.tsx
│   │   ├── components/
│   │   │   ├── ErrorBoundary.tsx
│   │   │   ├── layout/          # Header, Sidebar, Layout
│   │   │   ├── careers/
│   │   │   ├── dashboard/
│   │   │   └── ui/              # shadcn/ui components
│   │   ├── services/
│   │   │   ├── api.ts           # API service (static data mode)
│   │   │   └── staticApi.ts     # O*NET static data service
│   │   ├── store/
│   │   │   └── useUserStore.ts  # Zustand user state
│   │   ├── data/
│   │   │   └── onetCareers.ts   # 300+ O*NET careers (static)
│   │   └── types/               # TypeScript type definitions
│   ├── vercel.json
│   └── package.json
│
├── modules/                     # Python backend modules
│   ├── career_roadmap_engine.py
│   ├── job_scraper.py
│   ├── skills_matcher.py
│   ├── recommendation_engine.py
│   ├── student_pathways.py
│   └── application_assistant.py
├── api_bridge.py                # FastAPI backend
├── main_integrated.py           # Gradio web UI
├── requirements.txt
└── config/system_config.yaml
```

---

## AI Assistant Architecture

The AI Assistant uses a Vercel Edge Function (`/api/chat`) that:

1. Receives the conversation history and the user's full profile from the browser
2. Builds a personalized system prompt with the user's skills, title, experience, and interests
3. Calls the Anthropic Claude API (`claude-opus-4-6`)
4. Returns the response to the browser

The API key never touches the browser — it lives only in Vercel's environment variables.

```
Browser → POST /api/chat → Vercel Edge Function → Claude API → Response
```

---

## Known Limitations

- **No real authentication** — user profile lives in `localStorage`. Data doesn't sync across devices.
- **Job listings are curated mock data** — not scraped live in production (backend not deployed).
- **O*NET career data has quality gaps** — skills/tasks fields are empty for most careers (scraper limitation).
- **No code splitting** for the 6,000-line career data file — impacts initial load time.
- **SQLite backend not production-ready** — would need PostgreSQL for concurrent users.

---

## Roadmap

- [ ] Deploy FastAPI backend to Railway/Render
- [ ] Real-time job scraping via the Python backend
- [ ] User accounts and cross-device sync (Supabase or Firebase)
- [ ] Fix O*NET skills data quality (re-run scraper with corrected field extraction)
- [ ] Resume and cover letter generation (connect to Python `ApplicationAssistant`)
- [ ] Split `onetCareers.ts` into lazy-loaded chunks
- [ ] Migrate SQLite to PostgreSQL for backend persistence

---

## Author

**Rahul Mehta** — [GitHub](https://github.com/rahulmehta25)

Originally developed for C# Corner. Powered by Claude (Anthropic) and O*NET data from the US Department of Labor.
