"""
AI-Powered Career Recommendation Engine

This module provides personalized career recommendations using hybrid ML approaches:
- Collaborative filtering for similar student profiles
- Content-based filtering for skill and interest matching
- Explainable AI for transparent recommendations
- OpenAI GPT-4 for enhanced, personalized insights
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import logging
from datetime import datetime
import re
import os
from dotenv import load_dotenv

# OpenAI and LangChain imports
try:
    from openai import OpenAI
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    from langchain.output_parsers import PydanticOutputParser
    from pydantic import BaseModel, Field
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI libraries not available. Some features will be limited.")

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Pydantic models for OpenAI responses
if OPENAI_AVAILABLE:
    class AICareerInsight(BaseModel):
        """Structure for AI-generated career insights"""
        career_fit_analysis: str = Field(description="Detailed analysis of career fit")
        personalized_advice: str = Field(description="Personalized career advice")
        key_strengths: List[str] = Field(description="Key strengths for this career")
        development_areas: List[str] = Field(description="Areas needing development")
        success_probability: float = Field(description="Estimated success probability (0-1)")
        timeline_estimate: str = Field(description="Estimated timeline to enter career")
        
    class AISkillGapAnalysis(BaseModel):
        """Structure for AI-generated skill gap analysis"""
        critical_gaps: List[str] = Field(description="Critical skill gaps to address")
        learning_priorities: List[str] = Field(description="Prioritized learning recommendations")
        resources: List[str] = Field(description="Recommended learning resources")
        estimated_time: str = Field(description="Estimated time to bridge gaps")


@dataclass
class StudentProfile:
    """Represents a student's comprehensive profile"""
    student_id: str
    name: str
    age: int
    education_level: str  # high_school, undergraduate, graduate
    gpa: float
    major: Optional[str] = None
    interests: List[str] = None
    skills: Dict[str, int] = None  # skill: proficiency (1-5)
    activities: List[str] = None
    personality_traits: Dict[str, float] = None  # OCEAN model scores
    work_experience: List[Dict] = None
    preferred_work_environment: List[str] = None
    location_preference: str = "flexible"
    salary_expectations: Optional[str] = None
    
    def __post_init__(self):
        self.interests = self.interests or []
        self.skills = self.skills or {}
        self.activities = self.activities or []
        self.personality_traits = self.personality_traits or {}
        self.work_experience = self.work_experience or []
        self.preferred_work_environment = self.preferred_work_environment or []


@dataclass
class CareerRecommendation:
    """Represents a single career recommendation"""
    career_id: str
    title: str
    match_score: float
    confidence: float
    reasons: List[str]
    skill_gaps: List[Dict[str, Any]]
    learning_path: List[str]
    growth_potential: str
    salary_range: str
    job_outlook: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


class RecommendationEngine:
    """Main recommendation engine for career suggestions"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.careers_dir = self.data_dir / "careers"
        self.models_dir = self.data_dir / "recommendation_models"
        
        # Ensure directories exist
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize models and data
        self.career_embeddings = self.load_or_create_embeddings()
        self.skill_mappings = self.load_or_create_skill_mappings()
        self.interest_profiles = self.load_or_create_interest_profiles()
        self.career_data = self.load_career_data()
        
        # Initialize ML components
        self.tfidf_vectorizer = TfidfVectorizer(max_features=500)
        self.scaler = MinMaxScaler()
        
        # Initialize OpenAI client if available
        self.openai_client = None
        self.langchain_llm = None
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key and api_key != "your_openai_api_key_here":
                try:
                    self.openai_client = OpenAI(api_key=api_key)
                    self.langchain_llm = ChatOpenAI(
                        model="gpt-4-turbo-preview",
                        temperature=0.7,
                        api_key=api_key
                    )
                    logger.info("OpenAI GPT-4 initialized successfully")
                except Exception as e:
                    logger.warning(f"Failed to initialize OpenAI: {e}")
                    self.openai_client = None
                    self.langchain_llm = None
            else:
                logger.warning("OpenAI API key not configured. Add OPENAI_API_KEY to .env file for enhanced recommendations.")
        
        # Holland code mapping (RIASEC)
        self.holland_codes = {
            "realistic": ["engineering", "construction", "manufacturing", "agriculture"],
            "investigative": ["science", "research", "healthcare", "technology"],
            "artistic": ["design", "media", "writing", "performing_arts"],
            "social": ["education", "counseling", "social_work", "healthcare"],
            "enterprising": ["business", "sales", "management", "entrepreneurship"],
            "conventional": ["accounting", "administration", "finance", "data_entry"]
        }
        
        # Personality to career mapping (OCEAN model)
        self.personality_career_map = {
            "openness": ["creative", "innovative", "research", "artistic"],
            "conscientiousness": ["organized", "detail-oriented", "analytical", "structured"],
            "extraversion": ["leadership", "sales", "public_speaking", "networking"],
            "agreeableness": ["teamwork", "helping", "teaching", "counseling"],
            "neuroticism": ["stable_environment", "structured_roles", "clear_expectations"]
        }
    
    def load_or_create_embeddings(self) -> Dict:
        """Load or create career embeddings for similarity matching"""
        embeddings_path = self.models_dir / "career_embeddings.json"
        
        if embeddings_path.exists():
            with open(embeddings_path, 'r') as f:
                return json.load(f)
        
        # Create default embeddings based on career characteristics
        embeddings = {}
        career_files = list(self.careers_dir.glob("*.json")) if self.careers_dir.exists() else []
        
        for career_file in career_files[:50]:  # Limit for initial creation
            try:
                with open(career_file, 'r') as f:
                    career_data = json.load(f)
                    career_id = career_file.stem
                    
                    # Create feature vector based on career attributes
                    features = self.extract_career_features(career_data)
                    embeddings[career_id] = features
            except Exception as e:
                logger.warning(f"Error processing {career_file}: {e}")
        
        # Save embeddings
        with open(embeddings_path, 'w') as f:
            json.dump(embeddings, f, indent=2)
        
        return embeddings
    
    def extract_career_features(self, career_data: Dict) -> List[float]:
        """Extract numerical features from career data"""
        features = []
        
        # Extract growth rate as numerical value
        growth = career_data.get("growth_rate", "5%")
        growth_num = float(re.findall(r'\d+', growth)[0]) if re.findall(r'\d+', growth) else 5
        features.append(growth_num / 100)
        
        # Extract average salary (from entry level)
        if "levels" in career_data and "Entry" in career_data["levels"]:
            salary = career_data["levels"]["Entry"].get("salary_range", "$50,000")
            salary_nums = re.findall(r'\d+', salary.replace(',', ''))
            avg_salary = sum(map(float, salary_nums)) / len(salary_nums) if salary_nums else 50000
            features.append(avg_salary / 200000)  # Normalize
        else:
            features.append(0.25)  # Default normalized salary
        
        # Count skills required
        total_skills = 0
        if "levels" in career_data:
            for level in career_data["levels"].values():
                total_skills += len(level.get("skills", []))
        features.append(min(total_skills / 50, 1))  # Normalize
        
        # Add category encoding (simplified)
        category = career_data.get("category", "general")
        category_map = {
            "technology": 1.0, "healthcare": 0.8, "business": 0.6,
            "education": 0.4, "creative": 0.2, "general": 0.5
        }
        features.append(category_map.get(category, 0.5))
        
        # Pad or trim to fixed size
        target_size = 10
        if len(features) < target_size:
            features.extend([0.0] * (target_size - len(features)))
        else:
            features = features[:target_size]
        
        return features
    
    def load_or_create_skill_mappings(self) -> Dict:
        """Load or create skill to career mappings"""
        mappings_path = self.models_dir / "skill_mappings.json"
        
        if mappings_path.exists():
            with open(mappings_path, 'r') as f:
                return json.load(f)
        
        # Create default skill mappings
        skill_mappings = {
            "programming": {
                "careers": ["software_developer", "data_scientist", "web_developer", 
                           "mobile_developer", "devops_engineer", "system_administrator"],
                "weight": 1.0
            },
            "data_analysis": {
                "careers": ["data_analyst", "data_scientist", "business_analyst", 
                           "market_researcher", "financial_analyst"],
                "weight": 0.9
            },
            "communication": {
                "careers": ["teacher", "marketing_manager", "public_relations", 
                           "sales_representative", "hr_specialist"],
                "weight": 0.8
            },
            "leadership": {
                "careers": ["project_manager", "executive", "team_lead", 
                           "entrepreneur", "operations_manager"],
                "weight": 0.85
            },
            "creativity": {
                "careers": ["graphic_designer", "ux_designer", "content_creator", 
                           "marketing_specialist", "product_designer"],
                "weight": 0.8
            },
            "problem_solving": {
                "careers": ["consultant", "engineer", "researcher", "analyst", "developer"],
                "weight": 0.9
            },
            "mathematics": {
                "careers": ["actuary", "statistician", "data_scientist", 
                           "financial_analyst", "engineer"],
                "weight": 0.95
            },
            "writing": {
                "careers": ["content_writer", "journalist", "technical_writer", 
                           "copywriter", "editor"],
                "weight": 0.9
            },
            "teaching": {
                "careers": ["teacher", "professor", "trainer", "instructional_designer", 
                           "education_consultant"],
                "weight": 1.0
            },
            "research": {
                "careers": ["research_scientist", "market_researcher", "ux_researcher", 
                           "policy_analyst", "academic_researcher"],
                "weight": 0.95
            }
        }
        
        # Save mappings
        with open(mappings_path, 'w') as f:
            json.dump(skill_mappings, f, indent=2)
        
        return skill_mappings
    
    def load_or_create_interest_profiles(self) -> Dict:
        """Load or create interest to career profiles"""
        profiles_path = self.models_dir / "interest_profiles.json"
        
        if profiles_path.exists():
            with open(profiles_path, 'r') as f:
                return json.load(f)
        
        # Create default interest profiles
        interest_profiles = {
            "technology": {
                "careers": ["software_developer", "data_scientist", "cybersecurity_analyst",
                           "ai_engineer", "cloud_architect", "devops_engineer"],
                "related_interests": ["coding", "ai", "robotics", "gaming", "innovation"]
            },
            "healthcare": {
                "careers": ["doctor", "nurse", "medical_researcher", "therapist",
                           "healthcare_administrator", "public_health_specialist"],
                "related_interests": ["helping_others", "biology", "medicine", "wellness"]
            },
            "business": {
                "careers": ["business_analyst", "marketing_manager", "entrepreneur",
                           "financial_analyst", "consultant", "product_manager"],
                "related_interests": ["strategy", "finance", "leadership", "innovation"]
            },
            "creative_arts": {
                "careers": ["graphic_designer", "animator", "photographer", "artist",
                           "creative_director", "ux_designer"],
                "related_interests": ["art", "design", "creativity", "visual_arts"]
            },
            "education": {
                "careers": ["teacher", "professor", "educational_technologist",
                           "curriculum_developer", "education_administrator"],
                "related_interests": ["teaching", "mentoring", "child_development", "learning"]
            },
            "environment": {
                "careers": ["environmental_scientist", "conservation_biologist",
                           "sustainability_consultant", "renewable_energy_engineer"],
                "related_interests": ["nature", "sustainability", "climate", "conservation"]
            },
            "social_impact": {
                "careers": ["social_worker", "nonprofit_manager", "community_organizer",
                           "policy_analyst", "human_rights_advocate"],
                "related_interests": ["social_justice", "community", "advocacy", "helping"]
            }
        }
        
        # Save profiles
        with open(profiles_path, 'w') as f:
            json.dump(interest_profiles, f, indent=2)
        
        return interest_profiles
    
    def load_career_data(self) -> Dict:
        """Load all available career data"""
        career_data = {}
        
        if not self.careers_dir.exists():
            logger.warning(f"Careers directory not found: {self.careers_dir}")
            return career_data
        
        for career_file in self.careers_dir.glob("*.json"):
            try:
                with open(career_file, 'r') as f:
                    career_data[career_file.stem] = json.load(f)
            except Exception as e:
                logger.warning(f"Error loading {career_file}: {e}")
        
        logger.info(f"Loaded {len(career_data)} careers")
        return career_data
    
    def calculate_skill_match(self, student_skills: Dict[str, int], 
                            career_skills: List[str]) -> Tuple[float, List[Dict]]:
        """Calculate skill match score and identify gaps"""
        if not career_skills:
            return 0.5, []
        
        matched_skills = 0
        skill_gaps = []
        
        # Normalize student skills to lowercase
        student_skills_lower = {k.lower(): v for k, v in student_skills.items()}
        
        for required_skill in career_skills:
            skill_lower = required_skill.lower()
            
            # Check for exact match
            if skill_lower in student_skills_lower:
                matched_skills += student_skills_lower[skill_lower] / 5.0
            else:
                # Check for partial matches
                partial_match = False
                for student_skill, level in student_skills_lower.items():
                    if (skill_lower in student_skill or student_skill in skill_lower or
                        self.calculate_string_similarity(skill_lower, student_skill) > 0.7):
                        matched_skills += (level / 5.0) * 0.7  # Partial credit
                        partial_match = True
                        break
                
                if not partial_match:
                    skill_gaps.append({
                        "skill": required_skill,
                        "importance": "high",
                        "learning_resources": self.get_learning_resources(required_skill)
                    })
        
        match_score = matched_skills / len(career_skills) if career_skills else 0
        return min(match_score, 1.0), skill_gaps
    
    def calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def get_learning_resources(self, skill: str) -> List[str]:
        """Get learning resources for a skill"""
        # This would connect to a learning resources database
        # For now, return generic resources
        return [
            f"Online course: Introduction to {skill}",
            f"Book: Mastering {skill}",
            f"Tutorial: {skill} for beginners",
            f"Practice projects in {skill}"
        ]
    
    def calculate_interest_match(self, student_interests: List[str], 
                                career_category: str) -> float:
        """Calculate interest alignment score"""
        if not student_interests:
            return 0.5
        
        score = 0.0
        for interest in student_interests:
            interest_lower = interest.lower()
            
            # Check interest profiles
            for profile_name, profile_data in self.interest_profiles.items():
                if interest_lower in profile_name or profile_name in interest_lower:
                    # Check if career matches this interest profile
                    if any(career_category in career for career in profile_data["careers"]):
                        score += 1.0
                    elif any(interest_lower in related for related in profile_data["related_interests"]):
                        score += 0.7
                    break
            
            # Direct category match
            if interest_lower in career_category.lower():
                score += 1.5
        
        return min(score / len(student_interests), 1.0)
    
    def calculate_personality_fit(self, personality_traits: Dict[str, float], 
                                 career_data: Dict) -> float:
        """Calculate personality-career fit using OCEAN model"""
        if not personality_traits:
            return 0.5
        
        score = 0.0
        weights_sum = 0.0
        
        # Map personality traits to career requirements
        career_personality_reqs = self.infer_career_personality_requirements(career_data)
        
        for trait, value in personality_traits.items():
            trait_lower = trait.lower()
            if trait_lower in career_personality_reqs:
                required_level = career_personality_reqs[trait_lower]
                # Calculate fit (1.0 - normalized difference)
                fit = 1.0 - abs(value - required_level) / 1.0
                score += fit
                weights_sum += 1.0
        
        return score / weights_sum if weights_sum > 0 else 0.5
    
    def infer_career_personality_requirements(self, career_data: Dict) -> Dict[str, float]:
        """Infer personality requirements from career data"""
        requirements = {
            "openness": 0.5,
            "conscientiousness": 0.5,
            "extraversion": 0.5,
            "agreeableness": 0.5,
            "neuroticism": 0.3  # Lower is generally better
        }
        
        # Adjust based on career category and description
        category = career_data.get("category", "").lower()
        description = career_data.get("description", "").lower()
        
        # Technology careers - high openness, moderate conscientiousness
        if "technology" in category or "software" in description:
            requirements["openness"] = 0.8
            requirements["conscientiousness"] = 0.7
        
        # Healthcare - high conscientiousness and agreeableness
        elif "healthcare" in category or "medical" in description:
            requirements["conscientiousness"] = 0.9
            requirements["agreeableness"] = 0.8
        
        # Sales/Business - high extraversion
        elif "sales" in category or "business" in category:
            requirements["extraversion"] = 0.8
            requirements["conscientiousness"] = 0.7
        
        # Creative fields - very high openness
        elif "creative" in category or "design" in description:
            requirements["openness"] = 0.9
            requirements["extraversion"] = 0.6
        
        # Education - high agreeableness and moderate extraversion
        elif "education" in category or "teaching" in description:
            requirements["agreeableness"] = 0.85
            requirements["extraversion"] = 0.65
        
        return requirements
    
    def calculate_academic_fit(self, gpa: float, education_level: str, 
                              career_data: Dict) -> float:
        """Calculate academic qualification fit"""
        # Normalize GPA to 0-1 scale (assuming 4.0 scale)
        normalized_gpa = min(gpa / 4.0, 1.0)
        
        # Get required education level
        entry_level = career_data.get("levels", {}).get("Entry", {})
        required_education = entry_level.get("education", "").lower()
        
        education_match = 0.5  # Default
        
        # Education level matching
        education_hierarchy = {
            "high_school": 1,
            "associate": 2,
            "bachelor": 3,
            "undergraduate": 3,
            "master": 4,
            "graduate": 4,
            "phd": 5,
            "doctorate": 5
        }
        
        student_level = education_hierarchy.get(education_level.lower(), 2)
        
        # Parse required education
        if "phd" in required_education or "doctorate" in required_education:
            required_level = 5
        elif "master" in required_education:
            required_level = 4
        elif "bachelor" in required_education:
            required_level = 3
        elif "associate" in required_education:
            required_level = 2
        else:
            required_level = 1
        
        # Calculate education match
        if student_level >= required_level:
            education_match = 1.0
        elif student_level == required_level - 1:
            education_match = 0.7  # Can potentially qualify with experience
        else:
            education_match = 0.3
        
        # Combine GPA and education level
        # Some careers care more about GPA than others
        if "research" in career_data.get("title", "").lower():
            return normalized_gpa * 0.6 + education_match * 0.4
        elif "academic" in career_data.get("title", "").lower():
            return normalized_gpa * 0.7 + education_match * 0.3
        else:
            return normalized_gpa * 0.3 + education_match * 0.7
    
    def generate_learning_path(self, student_profile: StudentProfile, 
                              career_data: Dict, skill_gaps: List[Dict]) -> List[str]:
        """Generate personalized learning path"""
        learning_path = []
        
        # Start with foundational skills
        if skill_gaps:
            learning_path.append(f"Phase 1: Foundation Building (3-6 months)")
            for i, gap in enumerate(skill_gaps[:3], 1):
                learning_path.append(f"  {i}. Master {gap['skill']} through online courses and practice")
        
        # Add intermediate steps based on career levels
        if "levels" in career_data:
            entry_level = career_data["levels"].get("Entry", {})
            
            # Certifications
            certs = entry_level.get("certifications", [])
            if certs:
                learning_path.append(f"Phase 2: Professional Certifications (6-12 months)")
                for cert in certs[:2]:
                    learning_path.append(f"  - Obtain {cert} certification")
            
            # Projects
            projects = entry_level.get("projects", [])
            if projects:
                learning_path.append(f"Phase 3: Portfolio Development (Ongoing)")
                for project in projects[:3]:
                    learning_path.append(f"  - {project}")
        
        # Add experience building
        learning_path.append(f"Phase 4: Experience Building")
        learning_path.append(f"  - Seek internships in {career_data.get('title', 'this field')}")
        learning_path.append(f"  - Contribute to relevant open-source projects or volunteer work")
        learning_path.append(f"  - Network with professionals in the field")
        
        # Final preparation
        learning_path.append(f"Phase 5: Career Launch Preparation")
        learning_path.append(f"  - Build professional portfolio showcasing your skills")
        learning_path.append(f"  - Practice interview skills specific to {career_data.get('title', 'this role')}")
        learning_path.append(f"  - Customize resume for {career_data.get('category', 'this')} industry")
        
        return learning_path
    
    def calculate_collaborative_score(self, student_profile: StudentProfile, 
                                     career_id: str) -> float:
        """Calculate score based on similar student success patterns"""
        # In a production system, this would use historical student data
        # For now, we'll use a simplified approach
        
        # Simulate collaborative filtering based on profile similarity
        base_score = 0.5
        
        # Boost score for popular career paths for similar profiles
        if student_profile.education_level == "undergraduate":
            popular_undergrad_careers = ["software_developer", "data_analyst", 
                                        "marketing_specialist", "financial_analyst"]
            if any(career in career_id for career in popular_undergrad_careers):
                base_score += 0.2
        
        # Consider major alignment
        if student_profile.major:
            major_lower = student_profile.major.lower()
            if "computer" in major_lower and "software" in career_id:
                base_score += 0.3
            elif "business" in major_lower and ("analyst" in career_id or "manager" in career_id):
                base_score += 0.25
            elif "engineering" in major_lower and "engineer" in career_id:
                base_score += 0.3
        
        return min(base_score, 1.0)
    
    def generate_recommendation_reasons(self, student_profile: StudentProfile,
                                       career_data: Dict,
                                       skill_score: float,
                                       interest_score: float,
                                       personality_score: float,
                                       academic_score: float) -> List[str]:
        """Generate explainable reasons for the recommendation"""
        reasons = []
        
        # Skill-based reasons
        if skill_score > 0.7:
            matching_skills = []
            career_skills = []
            if "levels" in career_data and "Entry" in career_data["levels"]:
                career_skills = career_data["levels"]["Entry"].get("skills", [])
            
            for skill in student_profile.skills:
                if any(skill.lower() in cs.lower() or cs.lower() in skill.lower() 
                      for cs in career_skills):
                    matching_skills.append(skill)
            
            if matching_skills:
                reasons.append(f"Strong skill match: Your expertise in {', '.join(matching_skills[:3])} "
                             f"aligns well with this career")
        
        # Interest-based reasons
        if interest_score > 0.6:
            matching_interests = []
            career_category = career_data.get("category", "")
            for interest in student_profile.interests:
                if interest.lower() in career_category.lower() or \
                   career_category.lower() in interest.lower():
                    matching_interests.append(interest)
            
            if matching_interests:
                reasons.append(f"Interest alignment: Your passion for {', '.join(matching_interests)} "
                             f"matches this field perfectly")
        
        # Personality-based reasons
        if personality_score > 0.7:
            high_traits = [trait for trait, score in student_profile.personality_traits.items() 
                          if score > 0.7]
            if high_traits:
                reasons.append(f"Personality fit: Your {', '.join(high_traits)} traits are "
                             f"ideal for success in this role")
        
        # Academic qualification reasons
        if academic_score > 0.8:
            reasons.append(f"Academic excellence: Your {student_profile.gpa} GPA and "
                         f"{student_profile.education_level} education exceed requirements")
        
        # Growth and opportunity reasons
        growth_rate = career_data.get("growth_rate", "moderate")
        if "high" in growth_rate.lower() or any(x in growth_rate for x in ["15", "20", "25", "30"]):
            reasons.append(f"High growth field: This career has {growth_rate} growth rate, "
                         f"offering excellent future opportunities")
        
        # Work environment match
        if student_profile.preferred_work_environment:
            work_env_match = self.check_work_environment_match(
                student_profile.preferred_work_environment,
                career_data
            )
            if work_env_match:
                reasons.append(f"Work environment match: This role offers the {work_env_match} "
                             f"environment you prefer")
        
        # If no specific reasons, add generic positive reason
        if not reasons:
            reasons.append("This career offers a good balance of challenge and reward "
                         "aligned with your overall profile")
        
        return reasons
    
    def check_work_environment_match(self, preferences: List[str], 
                                    career_data: Dict) -> Optional[str]:
        """Check if career matches work environment preferences"""
        career_desc = career_data.get("description", "").lower()
        career_title = career_data.get("title", "").lower()
        
        for pref in preferences:
            pref_lower = pref.lower()
            if pref_lower == "remote" and ("remote" in career_desc or "software" in career_title):
                return "remote-friendly"
            elif pref_lower == "collaborative" and ("team" in career_desc or "collaborative" in career_desc):
                return "collaborative"
            elif pref_lower == "independent" and ("independent" in career_desc or "autonomous" in career_desc):
                return "independent"
            elif pref_lower == "fast-paced" and ("dynamic" in career_desc or "fast" in career_desc):
                return "fast-paced"
        
        return None
    
    def recommend_careers(self, student_profile: StudentProfile, 
                         top_n: int = 10) -> List[CareerRecommendation]:
        """
        Generate top N career recommendations for a student
        
        Args:
            student_profile: Complete student profile
            top_n: Number of recommendations to return
            
        Returns:
            List of CareerRecommendation objects with explanations
        """
        recommendations = []
        
        # Calculate scores for each career
        for career_id, career_data in self.career_data.items():
            try:
                # Get entry-level requirements
                entry_level = career_data.get("levels", {}).get("Entry", {})
                career_skills = entry_level.get("skills", [])
                
                # Calculate different matching scores
                skill_score, skill_gaps = self.calculate_skill_match(
                    student_profile.skills, 
                    career_skills
                )
                
                interest_score = self.calculate_interest_match(
                    student_profile.interests,
                    career_data.get("category", "general")
                )
                
                personality_score = self.calculate_personality_fit(
                    student_profile.personality_traits,
                    career_data
                )
                
                academic_score = self.calculate_academic_fit(
                    student_profile.gpa,
                    student_profile.education_level,
                    career_data
                )
                
                collaborative_score = self.calculate_collaborative_score(
                    student_profile,
                    career_id
                )
                
                # Weighted average of all scores
                weights = {
                    "skills": 0.35,
                    "interests": 0.25,
                    "personality": 0.15,
                    "academic": 0.15,
                    "collaborative": 0.10
                }
                
                match_score = (
                    skill_score * weights["skills"] +
                    interest_score * weights["interests"] +
                    personality_score * weights["personality"] +
                    academic_score * weights["academic"] +
                    collaborative_score * weights["collaborative"]
                )
                
                # Calculate confidence based on data completeness
                confidence = self.calculate_confidence(student_profile, career_data)
                
                # Generate learning path
                learning_path = self.generate_learning_path(
                    student_profile, 
                    career_data, 
                    skill_gaps
                )
                
                # Generate explanation reasons
                reasons = self.generate_recommendation_reasons(
                    student_profile,
                    career_data,
                    skill_score,
                    interest_score,
                    personality_score,
                    academic_score
                )
                
                # Create recommendation object
                recommendation = CareerRecommendation(
                    career_id=career_id,
                    title=career_data.get("title", career_id.replace("_", " ").title()),
                    match_score=round(match_score, 3),
                    confidence=round(confidence, 2),
                    reasons=reasons,
                    skill_gaps=skill_gaps[:5],  # Top 5 gaps
                    learning_path=learning_path,
                    growth_potential=career_data.get("growth_rate", "Moderate"),
                    salary_range=entry_level.get("salary_range", "Competitive"),
                    job_outlook=self.get_job_outlook(career_data)
                )
                
                recommendations.append(recommendation)
                
            except Exception as e:
                logger.warning(f"Error processing career {career_id}: {e}")
                continue
        
        # Sort by match score and return top N
        recommendations.sort(key=lambda x: x.match_score, reverse=True)
        
        # Ensure diversity in recommendations
        diverse_recommendations = self.ensure_diversity(recommendations, top_n)
        
        return diverse_recommendations[:top_n]
    
    def calculate_confidence(self, student_profile: StudentProfile, 
                           career_data: Dict) -> float:
        """Calculate confidence score based on data completeness"""
        confidence = 0.5  # Base confidence
        
        # Check student profile completeness
        if student_profile.skills:
            confidence += 0.1
        if student_profile.interests:
            confidence += 0.1
        if student_profile.personality_traits:
            confidence += 0.1
        if student_profile.work_experience:
            confidence += 0.1
        
        # Check career data completeness
        if "levels" in career_data:
            confidence += 0.05
        if "growth_rate" in career_data:
            confidence += 0.025
        if career_data.get("description"):
            confidence += 0.025
        
        return min(confidence, 1.0)
    
    def get_job_outlook(self, career_data: Dict) -> str:
        """Generate job outlook description"""
        growth_rate = career_data.get("growth_rate", "5%")
        
        # Parse growth rate
        growth_num = 5  # default
        if growth_rate:
            numbers = re.findall(r'\d+', growth_rate)
            if numbers:
                growth_num = int(numbers[0])
        
        if growth_num >= 20:
            return "Excellent - Much faster than average growth"
        elif growth_num >= 15:
            return "Very Good - Faster than average growth"
        elif growth_num >= 10:
            return "Good - Above average growth"
        elif growth_num >= 5:
            return "Stable - Average growth expected"
        else:
            return "Moderate - Some growth expected"
    
    def ensure_diversity(self, recommendations: List[CareerRecommendation], 
                        top_n: int) -> List[CareerRecommendation]:
        """Ensure diversity in career recommendations"""
        diverse_list = []
        categories_included = set()
        
        # First pass: include top recommendations from different categories
        for rec in recommendations:
            # Extract category from career_id or title
            category = self.extract_category(rec.career_id)
            
            if category not in categories_included or len(diverse_list) < top_n // 2:
                diverse_list.append(rec)
                categories_included.add(category)
            
            if len(diverse_list) >= top_n:
                break
        
        # Second pass: fill remaining slots with highest scores
        for rec in recommendations:
            if rec not in diverse_list:
                diverse_list.append(rec)
            if len(diverse_list) >= top_n:
                break
        
        return diverse_list
    
    def extract_category(self, career_id: str) -> str:
        """Extract category from career ID"""
        # Common category keywords
        if any(tech in career_id for tech in ["software", "data", "developer", "engineer"]):
            return "technology"
        elif any(health in career_id for health in ["medical", "nurse", "doctor", "therapist"]):
            return "healthcare"
        elif any(bus in career_id for bus in ["manager", "analyst", "consultant", "marketing"]):
            return "business"
        elif any(edu in career_id for edu in ["teacher", "professor", "educator"]):
            return "education"
        elif any(creative in career_id for creative in ["designer", "artist", "writer"]):
            return "creative"
        else:
            return "general"
    
    def save_recommendations(self, student_id: str, 
                            recommendations: List[CareerRecommendation]):
        """Save recommendations for future reference"""
        output_dir = self.data_dir / "recommendations"
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        output_data = {
            "student_id": student_id,
            "timestamp": timestamp,
            "recommendations": [rec.to_dict() for rec in recommendations]
        }
        
        output_file = output_dir / f"{student_id}_{timestamp[:10]}.json"
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        logger.info(f"Saved recommendations to {output_file}")
        return output_file
    
    def get_ai_career_insights(self, student_profile: StudentProfile, 
                               career_data: Dict) -> Optional[Dict]:
        """Get AI-powered career insights using OpenAI GPT-4"""
        if not self.openai_client:
            return None
        
        try:
            # Prepare profile summary
            profile_summary = f"""
            Student Profile:
            - Name: {student_profile.name}
            - Age: {student_profile.age}
            - Education: {student_profile.education_level} (GPA: {student_profile.gpa})
            - Major: {student_profile.major or 'Not specified'}
            - Skills: {', '.join([f'{k} (Level {v}/5)' for k, v in list(student_profile.skills.items())[:5]])}
            - Interests: {', '.join(student_profile.interests[:5])}
            - Work Experience: {len(student_profile.work_experience)} positions
            - Personality: {', '.join([f'{k}: {v:.1f}' for k, v in list(student_profile.personality_traits.items())[:5]])}
            """
            
            career_summary = f"""
            Career: {career_data.get('title', 'Unknown')}
            Category: {career_data.get('category', 'General')}
            Description: {career_data.get('description', 'No description')[:200]}
            Growth Rate: {career_data.get('growth_rate', 'Unknown')}
            """
            
            prompt = f"""As an expert career counselor, analyze this student's fit for the given career.
            
            {profile_summary}
            
            {career_summary}
            
            Provide a comprehensive analysis including:
            1. Detailed career fit analysis (2-3 sentences)
            2. Personalized advice for pursuing this career (2-3 sentences)
            3. List 3-4 key strengths the student has for this career
            4. List 3-4 areas for development
            5. Estimate success probability (0.0 to 1.0)
            6. Realistic timeline to enter this career field
            
            Be specific, actionable, and encouraging while being realistic."""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert career counselor with deep knowledge of career pathways and student development."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            # Parse the response
            content = response.choices[0].message.content
            
            # Extract structured information from the response
            insights = {
                "career_fit_analysis": self._extract_section(content, "career fit analysis", 2),
                "personalized_advice": self._extract_section(content, "advice", 2),
                "key_strengths": self._extract_list(content, "strengths", 4),
                "development_areas": self._extract_list(content, "development", 4),
                "success_probability": self._extract_probability(content),
                "timeline_estimate": self._extract_timeline(content),
                "raw_analysis": content
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting AI career insights: {e}")
            return None
    
    def _extract_section(self, text: str, keyword: str, sentences: int = 2) -> str:
        """Extract a section from AI response"""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if keyword.lower() in line.lower():
                # Get next few lines
                section = []
                for j in range(i, min(i + sentences + 1, len(lines))):
                    if lines[j].strip():
                        section.append(lines[j].strip())
                return ' '.join(section) if section else "Analysis not available"
        return "Analysis not available"
    
    def _extract_list(self, text: str, keyword: str, max_items: int = 4) -> List[str]:
        """Extract list items from AI response"""
        items = []
        lines = text.split('\n')
        found_section = False
        
        for line in lines:
            if keyword.lower() in line.lower():
                found_section = True
                continue
            if found_section and (line.strip().startswith('-') or line.strip().startswith('•') or line.strip().startswith('*')):
                item = line.strip().lstrip('-•* ').strip()
                if item:
                    items.append(item)
                if len(items) >= max_items:
                    break
        
        return items if items else ["No specific items identified"]
    
    def _extract_probability(self, text: str) -> float:
        """Extract probability from AI response"""
        import re
        # Look for patterns like "0.7", "70%", "probability: 0.8"
        patterns = [
            r'probability[:\s]+([0-9.]+)',
            r'([0-9.]+)\s*probability',
            r'success[:\s]+([0-9.]+)',
            r'([0-9]+)%\s*(?:chance|probability|success)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                value = float(match.group(1))
                if value > 1:  # It's a percentage
                    return value / 100
                return min(value, 1.0)
        
        return 0.7  # Default probability
    
    def _extract_timeline(self, text: str) -> str:
        """Extract timeline from AI response"""
        import re
        # Look for time-related patterns
        patterns = [
            r'timeline[:\s]+([^.]+)',
            r'(\d+[-\s]+\d+\s*(?:months?|years?))',
            r'(?:approximately|about|around)\s+(\d+\s*(?:months?|years?))',
            r'(?:within|in)\s+(\d+[-\s]+\d+\s*(?:months?|years?))'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1).strip().capitalize()
        
        return "1-2 years with focused preparation"
    
    def get_ai_skill_gap_analysis(self, student_skills: Dict[str, int], 
                                  career_skills: List[str]) -> Optional[Dict]:
        """Get AI-powered skill gap analysis using OpenAI GPT-4"""
        if not self.openai_client:
            return None
        
        try:
            current_skills = ', '.join([f'{k} (Level {v}/5)' for k, v in student_skills.items()])
            required_skills = ', '.join(career_skills)
            
            prompt = f"""As a career development expert, analyze the skill gaps between current and required skills.
            
            Current Skills: {current_skills}
            Required Career Skills: {required_skills}
            
            Provide:
            1. List the 3-5 most critical skill gaps to address
            2. Prioritized learning recommendations (3-5 items)
            3. Specific resources for skill development (3-5 resources)
            4. Realistic timeline to bridge these gaps
            
            Be specific and actionable in your recommendations."""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert in skill development and career transitions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )
            
            content = response.choices[0].message.content
            
            return {
                "critical_gaps": self._extract_list(content, "critical", 5),
                "learning_priorities": self._extract_list(content, "learning", 5),
                "resources": self._extract_list(content, "resources", 5),
                "estimated_time": self._extract_timeline(content),
                "raw_analysis": content
            }
            
        except Exception as e:
            logger.error(f"Error in AI skill gap analysis: {e}")
            return None
    
    def generate_ai_resume_suggestions(self, profile: Dict, target_career: str) -> Optional[str]:
        """Generate AI-powered resume optimization suggestions"""
        if not self.openai_client:
            return None
        
        try:
            prompt = f"""As a professional resume writer, provide specific suggestions to optimize this resume for a {target_career} position.
            
            Current Profile:
            - Skills: {', '.join(profile.get('skills', [])[:8])}
            - Experience: {profile.get('experience', 'Entry level')}
            - Education: {profile.get('education_level', 'Not specified')}
            
            Provide:
            1. Key skills to highlight (3-4 items)
            2. Action verbs to use (5-6 verbs)
            3. Quantifiable achievements to include (2-3 examples)
            4. Keywords for ATS optimization (5-7 keywords)
            5. Resume format recommendations
            
            Be specific and tailored to {target_career}."""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert resume writer and career coach."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating resume suggestions: {e}")
            return None
    
    def generate_ai_cover_letter(self, profile: Dict, job_details: Dict) -> Optional[str]:
        """Generate AI-powered cover letter"""
        if not self.openai_client:
            return None
        
        try:
            prompt = f"""Write a professional cover letter for this position.
            
            Candidate Profile:
            - Name: {profile.get('name', 'Candidate')}
            - Skills: {', '.join(profile.get('skills', [])[:5])}
            - Experience: {profile.get('experience', 'Entry level')}
            - Interests: {', '.join(profile.get('interests', [])[:3])}
            
            Job Details:
            - Title: {job_details.get('title', 'Position')}
            - Company: {job_details.get('company', 'the company')}
            - Key Requirements: {', '.join(job_details.get('requirements', [])[:4])}
            
            Write a compelling, professional cover letter (250-300 words) that:
            1. Shows enthusiasm for the role
            2. Highlights relevant skills and experience
            3. Demonstrates knowledge of the company/role
            4. Includes a strong opening and closing
            
            Use a professional tone and format."""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a professional career coach and expert cover letter writer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=600
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating cover letter: {e}")
            return None
    
    def generate_recommendations(self, profile_dict: Dict) -> List[Dict]:
        """Generate AI-enhanced career recommendations from profile dictionary"""
        # Convert dictionary to StudentProfile
        student_profile = StudentProfile(
            student_id=profile_dict.get('id', 'USER001'),
            name=profile_dict.get('name', 'User'),
            age=profile_dict.get('age', 25),
            education_level=profile_dict.get('education_level', 'undergraduate'),
            gpa=profile_dict.get('gpa', 3.5),
            major=profile_dict.get('major'),
            interests=profile_dict.get('interests', []),
            skills={skill: 3 for skill in profile_dict.get('skills', [])},  # Default level 3
            activities=profile_dict.get('activities', []),
            personality_traits=profile_dict.get('personality_traits', {}),
            work_experience=profile_dict.get('work_experience', []),
            preferred_work_environment=profile_dict.get('preferred_work_environment', []),
            location_preference=profile_dict.get('location_preference', 'flexible'),
            salary_expectations=profile_dict.get('salary_expectations')
        )
        
        # Get base recommendations
        recommendations = self.recommend_careers(student_profile, top_n=10)
        
        # Enhance with AI insights if available
        enhanced_recommendations = []
        for rec in recommendations:
            rec_dict = rec.to_dict()
            
            # Add AI insights if OpenAI is available
            if self.openai_client and rec.match_score > 0.6:  # Only for good matches
                career_data = self.career_data.get(rec.career_id, {})
                ai_insights = self.get_ai_career_insights(student_profile, career_data)
                
                if ai_insights:
                    rec_dict['ai_insights'] = ai_insights
                    # Update confidence based on AI analysis
                    if 'success_probability' in ai_insights:
                        rec_dict['confidence'] = (rec_dict['confidence'] + ai_insights['success_probability']) / 2
            
            enhanced_recommendations.append(rec_dict)
        
        return enhanced_recommendations


def main():
    """Example usage of the recommendation engine"""
    
    # Create sample student profile
    sample_student = StudentProfile(
        student_id="STU001",
        name="Jane Doe",
        age=20,
        education_level="undergraduate",
        gpa=3.5,
        major="Computer Science",
        interests=["technology", "problem-solving", "innovation", "teamwork"],
        skills={
            "Python": 4,
            "Data Analysis": 3,
            "Communication": 4,
            "Problem Solving": 5,
            "Machine Learning": 2
        },
        activities=["Coding Club", "Hackathons", "Volunteer Tutoring"],
        personality_traits={
            "openness": 0.8,
            "conscientiousness": 0.7,
            "extraversion": 0.6,
            "agreeableness": 0.75,
            "neuroticism": 0.3
        },
        work_experience=[
            {"role": "Software Intern", "duration": "3 months", "company": "Tech Startup"}
        ],
        preferred_work_environment=["collaborative", "innovative", "remote-friendly"],
        location_preference="flexible",
        salary_expectations="$60,000+"
    )
    
    # Initialize engine and get recommendations
    engine = RecommendationEngine()
    recommendations = engine.recommend_careers(sample_student, top_n=10)
    
    # Display recommendations
    print(f"\n{'='*80}")
    print(f"Career Recommendations for {sample_student.name}")
    print(f"{'='*80}\n")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec.title}")
        print(f"   Match Score: {rec.match_score:.1%} | Confidence: {rec.confidence:.0%}")
        print(f"   Growth: {rec.growth_potential} | Salary: {rec.salary_range}")
        print(f"   Outlook: {rec.job_outlook}")
        print(f"\n   Why this career?")
        for reason in rec.reasons[:2]:
            print(f"   • {reason}")
        
        if rec.skill_gaps:
            print(f"\n   Skills to develop:")
            for gap in rec.skill_gaps[:3]:
                print(f"   • {gap['skill']}")
        
        print(f"\n   Learning Path Preview:")
        for step in rec.learning_path[:3]:
            print(f"   {step}")
        print()
    
    # Save recommendations
    engine.save_recommendations(sample_student.student_id, recommendations)
    print(f"Recommendations saved for student {sample_student.student_id}")


if __name__ == "__main__":
    main()