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
from modules.onet_comprehensive_scraper import ONETComprehensiveScraper
from modules.student_pathways import StudentPathwayGenerator
from modules.live_job_scraper import LiveJobScraper
from modules.recommendation_engine import RecommendationEngine

# Initialize FastAPI
app = FastAPI(title="AI Career Assistant API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core components
assistant = CareerAssistantCore()
onet_scraper = ONETComprehensiveScraper()
pathway_generator = StudentPathwayGenerator()
job_scraper = LiveJobScraper()
recommendation_engine = RecommendationEngine()

# Cache for career data
career_cache = {}

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
    """Get all available careers"""
    try:
        # Try to get careers from cache first
        if not career_cache:
            # Get careers from O*NET scraper
            occupations = onet_scraper.get_bright_outlook_occupations()
            if not occupations:
                # Fallback to getting from clusters
                occupations = onet_scraper.get_occupations_from_clusters()
            
            # Format careers for frontend
            careers = []
            for occ in occupations[:100]:  # Limit to 100 for now
                careers.append({
                    'id': occ.get('soc_code', ''),
                    'title': occ.get('title', ''),
                    'description': occ.get('description', ''),
                    'growth': occ.get('growth_outlook', 'Average'),
                    'salary': occ.get('salary_range', '$50,000 - $80,000')
                })
            career_cache['careers'] = careers
        
        return {"careers": career_cache.get('careers', []), "total": len(career_cache.get('careers', []))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/careers/{career_id}")
async def get_career_details(career_id: str):
    """Get detailed information about a specific career"""
    try:
        # Try to scrape detailed career data
        occupation = {'soc_code': career_id, 'title': 'Career', 'url': f'/summary/{career_id}'}
        career_data = onet_scraper.scrape_occupation_details(occupation)
        
        if career_data:
            return {
                'id': career_data.soc_code,
                'title': career_data.title,
                'description': career_data.description,
                'tasks': career_data.tasks,
                'skills': career_data.skills,
                'knowledge': career_data.knowledge,
                'abilities': career_data.abilities,
                'education': career_data.education_level,
                'experience': career_data.experience_level,
                'salary': {'min': career_data.median_salary - 10000 if career_data.median_salary else 50000,
                          'max': career_data.median_salary + 20000 if career_data.median_salary else 80000},
                'growth': career_data.employment_outlook,
                'related_careers': career_data.related_occupations
            }
        else:
            raise HTTPException(status_code=404, detail="Career not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/careers/search")
async def search_careers(query: CareerSearchQuery):
    """Search for careers based on query"""
    try:
        # Get all careers and filter based on query
        if not career_cache:
            await get_all_careers()
        
        careers = career_cache.get('careers', [])
        query_lower = query.query.lower()
        
        # Filter careers based on search query
        results = [
            career for career in careers
            if query_lower in career['title'].lower() or 
               query_lower in career.get('description', '').lower()
        ]
        
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
            "total_careers": len(onet_scraper.get_career_list()),
            "active_jobs": 5000,  # Mock data
            "users_helped": 1250,  # Mock data
            "success_rate": 89.5  # Mock data
        }
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("Starting API Bridge on http://localhost:8000")
    print("Frontend should connect to this API for all backend operations")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)