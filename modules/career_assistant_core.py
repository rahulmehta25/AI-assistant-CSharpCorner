"""
Career Assistant Core Integration Module

This module provides a unified API that integrates all components of the Career Assistant system:
- O*NET career data and scraping
- Student pathways and education planning
- Roadmap generation and milestone tracking
- Job scraping and search functionality
- AI-powered recommendation engine
- User profile and progress management

Author: Career Assistant AI System
Version: 2.0.0
"""

import os
import json
import yaml
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# Import all system modules
from .onet_comprehensive_scraper import ONetComprehensiveScraper
from .onet_live_scraper import ONetLiveScraper
from .student_pathways import StudentPathwaySystem
from .roadmap_generator import RoadmapGenerator
from .milestone_tracker import MilestoneTracker
from .job_scraper import JobScraper
from .live_job_scraper import LiveJobScraper
from .recommendation_engine import RecommendationEngine
from .skills_assessment import SkillsAssessment
from .user_database import UserDatabase
from .config_manager import ConfigManager


@dataclass
class UserProfile:
    """User profile data structure"""
    user_id: str
    name: str
    email: Optional[str] = None
    education_level: str = "High School"
    current_skills: List[str] = None
    interests: List[str] = None
    career_goals: List[str] = None
    work_experience: List[Dict] = None
    preferred_locations: List[str] = None
    salary_expectations: Optional[Dict] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.current_skills is None:
            self.current_skills = []
        if self.interests is None:
            self.interests = []
        if self.career_goals is None:
            self.career_goals = []
        if self.work_experience is None:
            self.work_experience = []
        if self.preferred_locations is None:
            self.preferred_locations = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()


@dataclass
class CareerRecommendation:
    """Career recommendation data structure"""
    career_code: str
    title: str
    match_score: float
    reasoning: str
    salary_range: Dict
    growth_outlook: str
    education_requirements: List[str]
    key_skills: List[str]
    related_careers: List[str]
    job_market_data: Dict


class CareerAssistantCore:
    """
    Main integration class that coordinates all Career Assistant components
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Career Assistant Core system"""
        self.config_path = config_path or "config/system_config.yaml"
        self.config = self._load_config()
        self.logger = self._setup_logging()
        
        # Initialize data directories
        self._ensure_directories()
        
        # Initialize all modules with error handling
        try:
            self.onet_scraper = ONetComprehensiveScraper()
            self.onet_live = ONetLiveScraper()
            self.student_pathways = StudentPathwaySystem()
            self.roadmap_generator = RoadmapGenerator()
            self.milestone_tracker = MilestoneTracker()
            self.job_scraper = JobScraper()
            self.live_job_scraper = LiveJobScraper()
            self.recommendation_engine = RecommendationEngine()
            self.skills_assessment = SkillsAssessment()
            self.user_db = UserDatabase()
            
            self.logger.info("All modules initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing modules: {e}")
            # Initialize basic fallbacks
            self.onet_scraper = None
            self.onet_live = None
            self.student_pathways = None
            self.roadmap_generator = None
            self.milestone_tracker = None
            self.job_scraper = None
            self.live_job_scraper = None
            self.recommendation_engine = None
            self.skills_assessment = None
            self.user_db = None
        
        # Session management
        self.active_sessions = {}
        
        self.logger.info("Career Assistant Core initialized successfully")
    
    def _load_config(self) -> Dict:
        """Load system configuration from YAML file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return yaml.safe_load(f)
            else:
                # Return default configuration
                return self._get_default_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Return default configuration"""
        return {
            'app': {'debug': True},
            'database': {
                'user_profiles': 'data/user_profiles/',
                'career_data': 'data/comprehensive_careers/',
                'job_data': 'data/scraped_jobs/',
                'progress_data': 'data/user_progress/'
            },
            'modules': {
                'recommendation_engine': {
                    'max_recommendations': 10,
                    'min_match_score': 0.6
                }
            },
            'logging': {'level': 'INFO'}
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup system logging"""
        logger = logging.getLogger('CareerAssistantCore')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(getattr(logging, self.config.get('logging', {}).get('level', 'INFO')))
        return logger
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        directories = [
            self.config['database']['user_profiles'],
            self.config['database']['career_data'],
            self.config['database']['job_data'],
            self.config['database']['progress_data'],
            'logs/'
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    # User Management Methods
    
    def create_user_session(self, user_id: str) -> str:
        """Create a new user session"""
        session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.active_sessions[session_id] = {
            'user_id': user_id,
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'data': {}
        }
        self.logger.info(f"Created session {session_id} for user {user_id}")
        return session_id
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID"""
        try:
            profile_path = os.path.join(
                self.config['database']['user_profiles'], 
                f"{user_id}.json"
            )
            if os.path.exists(profile_path):
                with open(profile_path, 'r') as f:
                    data = json.load(f)
                    data['created_at'] = datetime.fromisoformat(data['created_at'])
                    data['updated_at'] = datetime.fromisoformat(data['updated_at'])
                    return UserProfile(**data)
            return None
        except Exception as e:
            self.logger.error(f"Error loading user profile {user_id}: {e}")
            return None
    
    def save_user_profile(self, profile: UserProfile) -> bool:
        """Save user profile to storage"""
        try:
            profile.updated_at = datetime.now()
            profile_path = os.path.join(
                self.config['database']['user_profiles'], 
                f"{profile.user_id}.json"
            )
            
            # Convert datetime objects to ISO format for JSON serialization
            profile_dict = asdict(profile)
            profile_dict['created_at'] = profile.created_at.isoformat()
            profile_dict['updated_at'] = profile.updated_at.isoformat()
            
            with open(profile_path, 'w') as f:
                json.dump(profile_dict, f, indent=2)
            
            self.logger.info(f"Saved profile for user {profile.user_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving user profile: {e}")
            return False
    
    def create_user_profile(self, user_id: str, name: str, **kwargs) -> UserProfile:
        """Create a new user profile"""
        profile = UserProfile(
            user_id=user_id,
            name=name,
            **kwargs
        )
        self.save_user_profile(profile)
        return profile
    
    # Career Exploration Methods
    
    def get_career_recommendations(self, user_id: str, limit: int = 10) -> List[CareerRecommendation]:
        """Get personalized career recommendations for a user"""
        try:
            profile = self.get_user_profile(user_id)
            if not profile:
                raise ValueError(f"User profile not found: {user_id}")
            
            if not self.recommendation_engine:
                return []
            
            # Use recommendation engine to get suggestions
            recommendations = self.recommendation_engine.get_personalized_recommendations(
                skills=profile.current_skills,
                interests=profile.interests,
                education_level=profile.education_level,
                experience_level="entry" if not profile.work_experience else "experienced"
            )
            
            # Convert to CareerRecommendation objects
            career_recs = []
            for rec in recommendations[:limit]:
                career_rec = CareerRecommendation(
                    career_code=rec.get('soc_code', 'Unknown'),
                    title=rec.get('title', 'Unknown'),
                    match_score=rec.get('match_score', 0.0),
                    reasoning=rec.get('reasoning', ''),
                    salary_range=rec.get('salary', {}),
                    growth_outlook=rec.get('growth_outlook', 'Average'),
                    education_requirements=rec.get('education_requirements', []),
                    key_skills=rec.get('skills', []),
                    related_careers=rec.get('related_careers', []),
                    job_market_data=rec.get('job_market_data', {})
                )
                career_recs.append(career_rec)
            
            self.logger.info(f"Generated {len(career_recs)} recommendations for user {user_id}")
            return career_recs
            
        except Exception as e:
            self.logger.error(f"Error generating career recommendations: {e}")
            return []
    
    def get_career_details(self, career_code: str) -> Optional[Dict]:
        """Get detailed information about a specific career"""
        try:
            career_file = os.path.join(
                self.config['database']['career_data'],
                f"{career_code}.json"
            )
            
            if os.path.exists(career_file):
                with open(career_file, 'r') as f:
                    return json.load(f)
            else:
                # Try to scrape the career data
                self.logger.info(f"Career data not found locally, attempting to scrape: {career_code}")
                return self.onet_live.scrape_career_details(career_code)
                
        except Exception as e:
            self.logger.error(f"Error getting career details for {career_code}: {e}")
            return None
    
    def search_careers(self, query: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Search careers by query and filters"""
        try:
            careers = []
            career_dir = self.config['database']['career_data']
            
            # Search through all career files
            for filename in os.listdir(career_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(career_dir, filename)
                    with open(filepath, 'r') as f:
                        career_data = json.load(f)
                        
                        # Simple text search in title and description
                        title = career_data.get('title', '').lower()
                        description = career_data.get('description', '').lower()
                        
                        if query.lower() in title or query.lower() in description:
                            careers.append(career_data)
            
            return careers[:20]  # Limit to 20 results
            
        except Exception as e:
            self.logger.error(f"Error searching careers: {e}")
            return []
    
    # Student Pathway Methods
    
    def generate_student_pathway(self, user_id: str, target_career: str) -> Optional[Dict]:
        """Generate education pathway for a student to reach target career"""
        try:
            profile = self.get_user_profile(user_id)
            if not profile:
                raise ValueError(f"User profile not found: {user_id}")
            
            pathway = self.student_pathways.generate_pathway(
                current_education=profile.education_level,
                target_career=target_career,
                current_skills=profile.current_skills,
                interests=profile.interests
            )
            
            self.logger.info(f"Generated pathway for user {user_id} targeting {target_career}")
            return pathway
            
        except Exception as e:
            self.logger.error(f"Error generating student pathway: {e}")
            return None
    
    def get_education_options(self, career_code: str) -> List[Dict]:
        """Get education options for a specific career"""
        try:
            return self.student_pathways.get_education_requirements(career_code)
        except Exception as e:
            self.logger.error(f"Error getting education options: {e}")
            return []
    
    # Career Roadmap Methods
    
    def generate_career_roadmap(self, user_id: str, target_career: str, timeline_months: int = 24) -> Optional[Dict]:
        """Generate detailed career roadmap for a user"""
        try:
            profile = self.get_user_profile(user_id)
            if not profile:
                raise ValueError(f"User profile not found: {user_id}")
            
            career_data = self.get_career_details(target_career)
            if not career_data:
                raise ValueError(f"Career data not found: {target_career}")
            
            roadmap = self.roadmap_generator.generate_roadmap(
                current_profile={
                    'education': profile.education_level,
                    'skills': profile.current_skills,
                    'experience': profile.work_experience
                },
                target_career=career_data,
                timeline_months=timeline_months
            )
            
            # Save roadmap to user progress
            self._save_user_roadmap(user_id, target_career, roadmap)
            
            self.logger.info(f"Generated roadmap for user {user_id} targeting {target_career}")
            return roadmap
            
        except Exception as e:
            self.logger.error(f"Error generating career roadmap: {e}")
            return None
    
    def update_milestone_progress(self, user_id: str, milestone_id: str, status: str, notes: str = "") -> bool:
        """Update progress on a specific milestone"""
        try:
            return self.milestone_tracker.update_milestone(
                user_id=user_id,
                milestone_id=milestone_id,
                status=status,
                notes=notes
            )
        except Exception as e:
            self.logger.error(f"Error updating milestone progress: {e}")
            return False
    
    def get_user_progress(self, user_id: str) -> Dict:
        """Get comprehensive progress report for a user"""
        try:
            return self.milestone_tracker.generate_progress_report(user_id)
        except Exception as e:
            self.logger.error(f"Error getting user progress: {e}")
            return {}
    
    # Job Search Methods
    
    def search_jobs(self, query: str, location: str = "", job_type: str = "", limit: int = 50) -> List[Dict]:
        """Search for jobs across multiple platforms"""
        try:
            jobs = []
            
            # Search using live job scraper
            live_results = self.live_job_scraper.search_jobs(
                query=query,
                location=location,
                job_type=job_type,
                max_results=limit
            )
            jobs.extend(live_results)
            
            # Search cached job data
            cached_results = self._search_cached_jobs(query, location, job_type)
            jobs.extend(cached_results)
            
            # Remove duplicates and limit results
            unique_jobs = self._deduplicate_jobs(jobs)
            
            self.logger.info(f"Found {len(unique_jobs)} jobs for query: {query}")
            return unique_jobs[:limit]
            
        except Exception as e:
            self.logger.error(f"Error searching jobs: {e}")
            return []
    
    def get_job_recommendations(self, user_id: str, limit: int = 20) -> List[Dict]:
        """Get job recommendations based on user profile"""
        try:
            profile = self.get_user_profile(user_id)
            if not profile:
                raise ValueError(f"User profile not found: {user_id}")
            
            # Get career recommendations first
            career_recs = self.get_career_recommendations(user_id, limit=5)
            
            # Search jobs for recommended careers
            recommended_jobs = []
            for career in career_recs[:3]:  # Top 3 career matches
                jobs = self.search_jobs(
                    query=career.title,
                    location=" ".join(profile.preferred_locations[:2]),
                    limit=10
                )
                recommended_jobs.extend(jobs)
            
            return recommended_jobs[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting job recommendations: {e}")
            return []
    
    # Skills Assessment Methods
    
    def assess_user_skills(self, user_id: str, skill_responses: Dict) -> Dict:
        """Assess user skills and update profile"""
        try:
            # Use evaluate_skills method from SkillsAssessment
            if hasattr(self.skills_assessment, 'evaluate_skills'):
                assessment_results = self.skills_assessment.evaluate_skills(skill_responses)
                
                # Update user profile with assessed skills
                profile = self.get_user_profile(user_id)
                if profile and hasattr(assessment_results, 'skill_levels'):
                    new_skills = [skill for skill, level in assessment_results.skill_levels.items() if level >= 3]
                    profile.current_skills = list(set(profile.current_skills + new_skills))
                    self.save_user_profile(profile)
                
                self.logger.info(f"Completed skills assessment for user {user_id}")
                return {
                    'skill_levels': getattr(assessment_results, 'skill_levels', {}),
                    'improvements': getattr(assessment_results, 'improvements', []),
                    'learning_plan': getattr(assessment_results, 'learning_plan', [])
                }
            else:
                return {'error': 'Skills assessment not available'}
            
        except Exception as e:
            self.logger.error(f"Error assessing user skills: {e}")
            return {'error': str(e)}
    
    def get_skill_gaps(self, user_id: str, target_career: str) -> Dict:
        """Identify skill gaps for a target career"""
        try:
            profile = self.get_user_profile(user_id)
            career_data = self.get_career_details(target_career)
            
            if not profile or not career_data:
                return {}
            
            current_skills = set(profile.current_skills)
            required_skills = set(career_data.get('skills', []))
            
            skill_gaps = required_skills - current_skills
            matching_skills = required_skills & current_skills
            
            return {
                'missing_skills': list(skill_gaps),
                'matching_skills': list(matching_skills),
                'match_percentage': len(matching_skills) / len(required_skills) * 100 if required_skills else 0,
                'recommendations': self._get_skill_development_recommendations(skill_gaps)
            }
            
        except Exception as e:
            self.logger.error(f"Error identifying skill gaps: {e}")
            return {}
    
    # Analytics and Reporting Methods
    
    def generate_user_analytics(self, user_id: str) -> Dict:
        """Generate comprehensive analytics for a user"""
        try:
            profile = self.get_user_profile(user_id)
            progress = self.get_user_progress(user_id)
            
            if not profile:
                return {}
            
            analytics = {
                'profile_completeness': self._calculate_profile_completeness(profile),
                'career_exploration_score': self._calculate_exploration_score(user_id),
                'progress_summary': progress,
                'recommendations_taken': self._count_recommendations_taken(user_id),
                'active_roadmaps': self._count_active_roadmaps(user_id),
                'skill_development_progress': self._track_skill_development(user_id)
            }
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error generating user analytics: {e}")
            return {}
    
    def export_user_data(self, user_id: str, format: str = "json") -> Optional[str]:
        """Export user data in specified format"""
        try:
            profile = self.get_user_profile(user_id)
            progress = self.get_user_progress(user_id)
            analytics = self.generate_user_analytics(user_id)
            
            export_data = {
                'profile': asdict(profile) if profile else {},
                'progress': progress,
                'analytics': analytics,
                'exported_at': datetime.now().isoformat()
            }
            
            if format.lower() == "json":
                filename = f"user_export_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                filepath = os.path.join(self.config['database']['user_profiles'], filename)
                
                with open(filepath, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
                
                return filepath
            
        except Exception as e:
            self.logger.error(f"Error exporting user data: {e}")
            return None
    
    # Helper Methods
    
    def _search_cached_jobs(self, query: str, location: str, job_type: str) -> List[Dict]:
        """Search through cached job data"""
        try:
            jobs = []
            job_dir = self.config['database']['job_data']
            
            if os.path.exists(job_dir):
                for filename in os.listdir(job_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(job_dir, filename)
                        with open(filepath, 'r') as f:
                            job_data = json.load(f)
                            
                            # Simple search logic
                            title = job_data.get('title', '').lower()
                            company = job_data.get('company', '').lower()
                            job_location = job_data.get('location', '').lower()
                            
                            if (query.lower() in title or query.lower() in company) and \
                               (not location or location.lower() in job_location):
                                jobs.append(job_data)
            
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error searching cached jobs: {e}")
            return []
    
    def _deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs from list"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            # Create a unique identifier for each job
            identifier = f"{job.get('title', '')}-{job.get('company', '')}-{job.get('location', '')}"
            if identifier not in seen:
                seen.add(identifier)
                unique_jobs.append(job)
        
        return unique_jobs
    
    def _save_user_roadmap(self, user_id: str, career: str, roadmap: Dict):
        """Save user's career roadmap"""
        try:
            roadmap_dir = os.path.join(self.config['database']['progress_data'], user_id)
            Path(roadmap_dir).mkdir(parents=True, exist_ok=True)
            
            filename = f"roadmap_{career.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json"
            filepath = os.path.join(roadmap_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(roadmap, f, indent=2, default=str)
                
        except Exception as e:
            self.logger.error(f"Error saving user roadmap: {e}")
    
    def _calculate_profile_completeness(self, profile: UserProfile) -> float:
        """Calculate how complete a user profile is"""
        total_fields = 8
        completed_fields = 0
        
        if profile.name: completed_fields += 1
        if profile.email: completed_fields += 1
        if profile.current_skills: completed_fields += 1
        if profile.interests: completed_fields += 1
        if profile.career_goals: completed_fields += 1
        if profile.work_experience: completed_fields += 1
        if profile.preferred_locations: completed_fields += 1
        if profile.salary_expectations: completed_fields += 1
        
        return (completed_fields / total_fields) * 100
    
    def _calculate_exploration_score(self, user_id: str) -> float:
        """Calculate career exploration activity score"""
        # This would track user activity like career views, assessments taken, etc.
        # For now, return a placeholder score
        return 75.0
    
    def _count_recommendations_taken(self, user_id: str) -> int:
        """Count how many recommendations the user has acted upon"""
        # Placeholder implementation
        return 3
    
    def _count_active_roadmaps(self, user_id: str) -> int:
        """Count active career roadmaps for user"""
        try:
            roadmap_dir = os.path.join(self.config['database']['progress_data'], user_id)
            if os.path.exists(roadmap_dir):
                return len([f for f in os.listdir(roadmap_dir) if f.startswith('roadmap_')])
            return 0
        except:
            return 0
    
    def _track_skill_development(self, user_id: str) -> Dict:
        """Track user's skill development over time"""
        # Placeholder implementation
        return {
            'skills_added': 5,
            'assessments_taken': 2,
            'improvement_areas': ['Programming', 'Communication']
        }
    
    def _get_skill_development_recommendations(self, missing_skills: set) -> List[Dict]:
        """Get recommendations for developing missing skills"""
        recommendations = []
        for skill in missing_skills:
            recommendations.append({
                'skill': skill,
                'resources': [
                    f"Online course: {skill} fundamentals",
                    f"Practice: {skill} projects",
                    f"Certification: {skill} professional"
                ],
                'estimated_time': "2-4 months",
                'priority': "high" if skill in ['Python', 'Communication', 'Problem Solving'] else "medium"
            })
        
        return recommendations
    
    # System Management Methods
    
    def health_check(self) -> Dict:
        """Perform system health check"""
        health = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'modules': {},
            'data_integrity': {},
            'performance': {}
        }
        
        try:
            # Check module availability
            health['modules'] = {
                'onet_scraper': self.onet_scraper is not None,
                'recommendation_engine': self.recommendation_engine is not None,
                'job_scraper': self.job_scraper is not None,
                'roadmap_generator': self.roadmap_generator is not None
            }
            
            # Check data directories
            health['data_integrity'] = {
                'career_data_available': len(os.listdir(self.config['database']['career_data'])) > 0,
                'user_profiles_accessible': os.path.exists(self.config['database']['user_profiles']),
                'job_data_available': os.path.exists(self.config['database']['job_data'])
            }
            
            # Performance metrics
            health['performance'] = {
                'active_sessions': len(self.active_sessions),
                'system_uptime': 'N/A'  # Would track actual uptime
            }
            
        except Exception as e:
            health['status'] = 'degraded'
            health['error'] = str(e)
            self.logger.error(f"Health check failed: {e}")
        
        return health
    
    def cleanup_expired_sessions(self):
        """Clean up expired user sessions"""
        try:
            current_time = datetime.now()
            expired_sessions = []
            
            for session_id, session_data in self.active_sessions.items():
                if current_time - session_data['last_activity'] > timedelta(hours=24):
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                del self.active_sessions[session_id]
                self.logger.info(f"Cleaned up expired session: {session_id}")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up sessions: {e}")
    
    # Additional API Methods for Frontend Integration
    
    def analyze_profile(self, profile_data: Dict) -> Dict:
        """Analyze user profile and return insights"""
        try:
            # Create temporary profile
            skills = profile_data.get('skills', [])
            interests = profile_data.get('interests', [])
            experience = profile_data.get('experience', '')
            
            analysis = {
                'profile_strength': self._calculate_profile_strength(profile_data),
                'career_matches': [],
                'skill_insights': {
                    'strong_skills': skills[:5] if skills else [],
                    'trending_skills': ['AI/ML', 'Cloud Computing', 'Data Analysis'],
                    'recommended_skills': self._get_recommended_skills(skills, interests)
                },
                'market_insights': {
                    'demand_level': 'High',
                    'growth_outlook': 'Positive',
                    'average_salary': '$85,000 - $120,000'
                }
            }
            
            # Get career matches
            if self.recommendation_engine:
                recommendations = self.recommendation_engine.get_personalized_recommendations(
                    skills=skills,
                    interests=interests,
                    education_level=profile_data.get('education_level', 'Bachelor'),
                    experience_level=experience
                )
                analysis['career_matches'] = recommendations[:5]
            
            return analysis
        except Exception as e:
            self.logger.error(f"Error analyzing profile: {e}")
            return {}
    
    def create_roadmap(self, profile_data: Dict) -> Dict:
        """Create career roadmap based on profile"""
        try:
            target_career = profile_data.get('career_goals', ['Software Engineer'])[0]
            
            if self.roadmap_generator:
                roadmap = self.roadmap_generator.generate_roadmap(
                    user_skills=profile_data.get('skills', []),
                    target_career=target_career,
                    timeline_months=24
                )
                return roadmap
            
            # Fallback roadmap
            return {
                'target_career': target_career,
                'timeline': '24 months',
                'phases': [
                    {
                        'phase': 1,
                        'title': 'Foundation',
                        'duration': '6 months',
                        'milestones': ['Learn basics', 'Build projects']
                    },
                    {
                        'phase': 2,
                        'title': 'Specialization',
                        'duration': '12 months',
                        'milestones': ['Deep dive into tech stack', 'Gain experience']
                    },
                    {
                        'phase': 3,
                        'title': 'Career Launch',
                        'duration': '6 months',
                        'milestones': ['Job search', 'Interview prep']
                    }
                ]
            }
        except Exception as e:
            self.logger.error(f"Error creating roadmap: {e}")
            return {}
    
    def match_jobs(self, profile_data: Dict) -> List[Dict]:
        """Match jobs based on user profile"""
        try:
            skills = profile_data.get('skills', [])
            experience = profile_data.get('experience', '')
            
            # Search for relevant jobs
            jobs = []
            if self.job_scraper:
                for skill in skills[:3]:  # Use top 3 skills
                    job_results = self.job_scraper.search_jobs(
                        query=skill,
                        location='Remote',
                        limit=10
                    )
                    jobs.extend(job_results)
            
            # Calculate match scores
            for job in jobs:
                job['match_score'] = self._calculate_job_match_score(job, profile_data)
            
            # Sort by match score
            jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
            
            return jobs[:20]  # Return top 20 matches
        except Exception as e:
            self.logger.error(f"Error matching jobs: {e}")
            return []
    
    def analyze_skills(self, profile_data: Dict) -> Dict:
        """Analyze user skills and provide insights"""
        try:
            current_skills = profile_data.get('skills', [])
            
            analysis = {
                'current_level': self._determine_skill_level(current_skills),
                'skill_categories': self._categorize_skills(current_skills),
                'market_demand': self._get_skill_market_demand(current_skills),
                'learning_recommendations': [],
                'certification_suggestions': []
            }
            
            # Get learning recommendations
            if self.recommendation_engine:
                analysis['learning_recommendations'] = self._get_learning_paths(current_skills)
                analysis['certification_suggestions'] = self._get_certification_suggestions(current_skills)
            
            return analysis
        except Exception as e:
            self.logger.error(f"Error analyzing skills: {e}")
            return {}
    
    def analyze_skill_gap(self, current_skills: List[str], target_career: str) -> Dict:
        """Analyze skill gaps for target career"""
        try:
            # Get required skills for target career
            required_skills = self._get_career_required_skills(target_career)
            
            # Calculate gaps
            current_set = set(current_skills)
            required_set = set(required_skills)
            
            gap_analysis = {
                'target_career': target_career,
                'current_skills': list(current_set),
                'required_skills': list(required_set),
                'missing_skills': list(required_set - current_set),
                'matching_skills': list(current_set & required_set),
                'match_percentage': len(current_set & required_set) / len(required_set) * 100 if required_set else 0,
                'recommendations': self._get_skill_development_recommendations(required_set - current_set)
            }
            
            return gap_analysis
        except Exception as e:
            self.logger.error(f"Error analyzing skill gap: {e}")
            return {}
    
    def generate_resume(self, profile_data: Dict) -> str:
        """Generate optimized resume"""
        try:
            name = profile_data.get('name', 'John Doe')
            skills = profile_data.get('skills', [])
            experience = profile_data.get('experience', '')
            
            resume = f"""
{name}
{'=' * len(name)}

PROFESSIONAL SUMMARY
{'-' * 20}
{experience}

SKILLS
{'-' * 6}
{', '.join(skills)}

EDUCATION
{'-' * 9}
{profile_data.get('education_level', 'Bachelor\'s Degree')}

EXPERIENCE
{'-' * 10}
[Add your work experience here]

PROJECTS
{'-' * 8}
[Add your projects here]
"""
            return resume
        except Exception as e:
            self.logger.error(f"Error generating resume: {e}")
            return ""
    
    def generate_cover_letter(self, profile_data: Dict, job_details: Dict) -> str:
        """Generate cover letter for specific job"""
        try:
            name = profile_data.get('name', 'John Doe')
            company = job_details.get('company', 'Company')
            position = job_details.get('title', 'Position')
            
            cover_letter = f"""
Dear Hiring Manager,

I am writing to express my strong interest in the {position} position at {company}.

[Your cover letter content here - customize based on the job requirements and your experience]

Thank you for considering my application.

Sincerely,
{name}
"""
            return cover_letter
        except Exception as e:
            self.logger.error(f"Error generating cover letter: {e}")
            return ""
    
    # Helper methods for API integration
    
    def _calculate_profile_strength(self, profile_data: Dict) -> float:
        """Calculate profile completion strength"""
        score = 0
        if profile_data.get('name'): score += 20
        if profile_data.get('skills'): score += 30
        if profile_data.get('experience'): score += 25
        if profile_data.get('interests'): score += 15
        if profile_data.get('education_level'): score += 10
        return min(score, 100)
    
    def _get_recommended_skills(self, current_skills: List[str], interests: List[str]) -> List[str]:
        """Get recommended skills based on current skills and interests"""
        # This would use ML/AI to recommend skills
        recommended = ['Python', 'JavaScript', 'Cloud Computing', 'Data Analysis', 'Machine Learning']
        return [s for s in recommended if s not in current_skills][:5]
    
    def _calculate_job_match_score(self, job: Dict, profile: Dict) -> float:
        """Calculate job match score"""
        score = 0
        job_skills = job.get('required_skills', [])
        user_skills = profile.get('skills', [])
        
        if job_skills and user_skills:
            matching = len(set(job_skills) & set(user_skills))
            score = (matching / len(job_skills)) * 100 if job_skills else 0
        
        return round(score, 1)
    
    def _determine_skill_level(self, skills: List[str]) -> str:
        """Determine overall skill level"""
        if len(skills) < 3:
            return 'Beginner'
        elif len(skills) < 7:
            return 'Intermediate'
        else:
            return 'Advanced'
    
    def _categorize_skills(self, skills: List[str]) -> Dict:
        """Categorize skills by type"""
        categories = {
            'Technical': [],
            'Soft Skills': [],
            'Tools': [],
            'Languages': []
        }
        
        # Simple categorization logic
        for skill in skills:
            skill_lower = skill.lower()
            if any(tech in skill_lower for tech in ['python', 'java', 'javascript', 'c++', 'sql']):
                categories['Languages'].append(skill)
            elif any(tool in skill_lower for tool in ['git', 'docker', 'aws', 'azure']):
                categories['Tools'].append(skill)
            elif any(soft in skill_lower for soft in ['communication', 'leadership', 'teamwork']):
                categories['Soft Skills'].append(skill)
            else:
                categories['Technical'].append(skill)
        
        return categories
    
    def _get_skill_market_demand(self, skills: List[str]) -> Dict:
        """Get market demand for skills"""
        # This would use real market data
        return {
            'high_demand': ['Python', 'Cloud Computing', 'AI/ML'],
            'moderate_demand': ['JavaScript', 'SQL', 'Docker'],
            'emerging': ['Rust', 'WebAssembly', 'Quantum Computing']
        }
    
    def _get_learning_paths(self, current_skills: List[str]) -> List[Dict]:
        """Get recommended learning paths"""
        return [
            {'path': 'Full Stack Development', 'duration': '6 months', 'difficulty': 'Intermediate'},
            {'path': 'Data Science', 'duration': '8 months', 'difficulty': 'Advanced'},
            {'path': 'Cloud Architecture', 'duration': '4 months', 'difficulty': 'Intermediate'}
        ]
    
    def _get_certification_suggestions(self, skills: List[str]) -> List[Dict]:
        """Get certification suggestions"""
        return [
            {'name': 'AWS Certified Solutions Architect', 'provider': 'Amazon', 'difficulty': 'Intermediate'},
            {'name': 'Google Cloud Professional', 'provider': 'Google', 'difficulty': 'Advanced'},
            {'name': 'Microsoft Azure Fundamentals', 'provider': 'Microsoft', 'difficulty': 'Beginner'}
        ]
    
    def _get_career_required_skills(self, career: str) -> List[str]:
        """Get required skills for a career"""
        # This would fetch from O*NET or database
        career_skills = {
            'Software Engineer': ['Python', 'JavaScript', 'Git', 'SQL', 'Algorithms'],
            'Data Scientist': ['Python', 'Statistics', 'Machine Learning', 'SQL', 'Data Visualization'],
            'DevOps Engineer': ['Docker', 'Kubernetes', 'CI/CD', 'AWS', 'Linux']
        }
        return career_skills.get(career, ['Problem Solving', 'Communication', 'Technical Skills'])