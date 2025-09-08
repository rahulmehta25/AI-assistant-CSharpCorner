"""
API Bridge for Frontend-Backend Integration
Provides REST endpoints for the React frontend to communicate with the Python backend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
import json
import sys
import os

# Add modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import backend modules
from modules.career_assistant_core import CareerAssistantCore
from modules.data_loader import data_loader
from modules.student_pathways import StudentPathwaySystem
from modules.live_job_scraper import LiveJobScraper
from modules.recommendation_engine import RecommendationEngine

# Initialize FastAPI
app = FastAPI(title="AI Career Assistant API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core components
assistant = CareerAssistantCore()
pathway_generator = StudentPathwaySystem()
job_scraper = LiveJobScraper()
recommendation_engine = RecommendationEngine()

# Request Models
class UserProfile(BaseModel):
    name: str
    experience: str
    skills: List[str]
    interests: List[str]
    education_level: Optional[str] = None
    career_goals: Optional[List[str]] = None

class CareerSearchQuery(BaseModel):
    query: str
    filters: Optional[Dict] = {}

class JobSearchQuery(BaseModel):
    query: str
    location: Optional[str] = ""
    experience_level: Optional[str] = ""
    max_results: Optional[int] = 50

class StudentProfileRequest(BaseModel):
    student_level: str  # "high_school" or "college"
    grade_year: Optional[str] = None
    interests: List[str]
    current_skills: Optional[List[str]] = []
    career_goals: Optional[List[str]] = []

# API Endpoints

@app.get("/")
async def root():
    return {"message": "AI Career Assistant API", "status": "active"}

@app.get("/api/careers")
async def get_all_careers():
    """Get all available careers from actual O*NET data"""
    try:
        # Get real careers from data loader
        careers_data = data_loader.get_all_careers()
        
        # Format careers for frontend
        careers = []
        for career in careers_data:
            median_salary = career.get('median_salary', 70000)
            if isinstance(median_salary, (int, float)) and median_salary > 0:
                salary_min = max(30000, int(median_salary * 0.8))
                salary_max = int(median_salary * 1.4)
            else:
                salary_min = 50000
                salary_max = 80000
            
            careers.append({
                'id': career.get('soc_code', ''),
                'title': career.get('title', ''),
                'description': career.get('description', '')[:200] + '...' if len(career.get('description', '')) > 200 else career.get('description', ''),
                'match': 85,  # Default match score
                'salary': {'min': salary_min, 'max': salary_max},
                'growth': career.get('employment_outlook', 'Average'),
                'education': career.get('education_level', "Bachelor's degree") if career.get('education_level') not in ['Education', None] else "Bachelor's degree",
                'experience': career.get('experience_level', '2-5 years') if career.get('experience_level') not in ['Experience Requirements', None] else "2-5 years",
                'skills': career.get('skills', [])[:5] if career.get('skills') else [],
                'tasks': career.get('tasks', [])[:3] if career.get('tasks') else [],
                'cluster': career.get('cluster', 'General')
            })
        
        return {"careers": careers, "total": len(careers)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/careers/{career_id}")
async def get_career_details(career_id: str):
    """Get detailed information about a specific career from real data"""
    try:
        # Get career from loaded data
        career_data = data_loader.get_career(career_id)
        
        if career_data:
            median_salary = career_data.get('median_salary', 70000)
            if isinstance(median_salary, (int, float)) and median_salary > 0:
                salary_min = max(30000, int(median_salary * 0.8))
                salary_max = int(median_salary * 1.4)
            else:
                salary_min = 50000
                salary_max = 80000
            
            return {
                'id': career_data.get('soc_code', career_id),
                'title': career_data.get('title', ''),
                'description': career_data.get('description', ''),
                'tasks': career_data.get('tasks', []),
                'skills': career_data.get('skills', []),
                'knowledge': career_data.get('knowledge', []),
                'abilities': career_data.get('abilities', []),
                'education': career_data.get('education_level', "Bachelor's degree") if career_data.get('education_level') not in ['Education', None] else "Bachelor's degree",
                'experience': career_data.get('experience_level', '2-5 years') if career_data.get('experience_level') not in ['Experience Requirements', None] else "2-5 years",
                'salary': {'min': salary_min, 'max': salary_max},
                'growth': career_data.get('employment_outlook', 'Average'),
                'growth_rate': career_data.get('growth_rate', '10%'),
                'related_careers': career_data.get('related_occupations', []),
                'work_environment': career_data.get('work_environment', []),
                'interests': career_data.get('interests', []),
                'work_styles': career_data.get('work_styles', []),
                'cluster': career_data.get('cluster', 'General')
            }
        else:
            raise HTTPException(status_code=404, detail=f"Career {career_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/careers/search")
async def search_careers(query: CareerSearchQuery):
    """Search for careers based on query using real data"""
    try:
        # Search in real career data
        results_data = data_loader.search_careers(query.query)
        
        # Format results for frontend
        results = []
        for career in results_data:
            median_salary = career.get('median_salary', 70000)
            if isinstance(median_salary, (int, float)) and median_salary > 0:
                salary_min = max(30000, int(median_salary * 0.8))
                salary_max = int(median_salary * 1.4)
            else:
                salary_min = 50000
                salary_max = 80000
            
            results.append({
                'id': career.get('soc_code', ''),
                'title': career.get('title', ''),
                'description': career.get('description', '')[:200] + '...' if len(career.get('description', '')) > 200 else career.get('description', ''),
                'match': 85,
                'salary': {'min': salary_min, 'max': salary_max},
                'growth': career.get('employment_outlook', 'Average'),
                'cluster': career.get('cluster', 'General')
            })
        
        return {"results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/profile/analyze")
async def analyze_profile(profile: UserProfile):
    """Analyze user profile and get recommendations"""
    try:
        profile_dict = profile.dict()
        recommendations = assistant.analyze_profile(profile_dict)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/careers/roadmap")
async def generate_roadmap(profile: UserProfile):
    """Generate career roadmap for user"""
    try:
        profile_dict = profile.dict()
        roadmap = assistant.create_roadmap(profile_dict)
        return roadmap
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/student-pathways")
async def generate_student_pathway(request: StudentProfileRequest):
    """Generate pathway for students"""
    try:
        pathway = pathway_generator.generate_pathway(
            student_level=request.student_level,
            career_field=request.career_goals[0] if request.career_goals else "Technology",
            current_skills=request.current_skills,
            grade_year=request.grade_year
        )
        return pathway
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/jobs/search")
async def search_jobs(query: JobSearchQuery):
    """Search for job postings"""
    try:
        jobs = job_scraper.scrape_jobs(
            query=query.query,
            location=query.location,
            max_results=query.max_results
        )
        return {"jobs": jobs, "count": len(jobs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/jobs/match")
async def match_jobs(profile: UserProfile):
    """Get job matches based on user profile"""
    try:
        profile_dict = profile.dict()
        matches = assistant.match_jobs(profile_dict)
        return {"matches": matches, "count": len(matches)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/skills/analyze")
async def analyze_skills(profile: UserProfile):
    """Analyze skills and get recommendations"""
    try:
        profile_dict = profile.dict()
        analysis = assistant.analyze_skills(profile_dict)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/skills/gap")
async def analyze_skill_gap(data: Dict):
    """Analyze skill gaps for target career"""
    try:
        current_skills = data.get("current_skills", [])
        target_career = data.get("target_career", "")
        gap_analysis = assistant.analyze_skill_gap(current_skills, target_career)
        return gap_analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/applications/resume")
async def generate_resume(profile: UserProfile):
    """Generate optimized resume"""
    try:
        profile_dict = profile.dict()
        resume = assistant.generate_resume(profile_dict)
        return {"resume": resume}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/applications/cover-letter")
async def generate_cover_letter(data: Dict):
    """Generate cover letter for specific job"""
    try:
        profile = data.get("profile", {})
        job_details = data.get("job_details", {})
        cover_letter = assistant.generate_cover_letter(profile, job_details)
        return {"cover_letter": cover_letter}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommendations")
async def get_recommendations(profile: UserProfile):
    """Get AI-powered career recommendations"""
    try:
        profile_dict = profile.dict()
        recommendations = recommendation_engine.generate_recommendations(profile_dict)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_platform_stats():
    """Get platform statistics"""
    try:
        stats = {
            "total_careers": len(data_loader.get_all_careers()),
            "active_jobs": 5000,  # Mock data
            "users_helped": 1250,  # Mock data
            "success_rate": 89.5  # Mock data
        }
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("Starting API Bridge on http://localhost:8001")
    print("Frontend should connect to this API for all backend operations")
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)