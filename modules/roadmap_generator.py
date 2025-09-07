"""
Career Roadmap Generator

A comprehensive module that takes O*NET career data and student pathways to generate
detailed, personalized 5-10 year career roadmaps with milestones, certifications,
projects, salary progression, and alternative paths.

Features:
- Generates 5-10 year career timelines
- Maps education requirements to career progression 
- Provides salary progression estimates
- Includes industry certifications and project recommendations
- Offers alternative career pivot paths
- Creates visual timeline data for frontend rendering

Author: AI Career Assistant
Created: September 2025
"""

import json
import os
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import logging
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CareerLevel(Enum):
    """Career progression levels"""
    ENTRY = "entry"
    JUNIOR = "junior" 
    MID_LEVEL = "mid_level"
    SENIOR = "senior"
    EXPERT = "expert"


class TimelineType(Enum):
    """Timeline visualization types"""
    LINEAR = "linear"
    BRANCHED = "branched"
    MILESTONE = "milestone"


@dataclass
class SalaryProgression:
    """Salary progression data"""
    level: CareerLevel
    years_experience: str
    min_salary: int
    max_salary: int
    median_salary: int
    location_factor: float = 1.0
    currency: str = "USD"


@dataclass
class CareerMilestone:
    """Represents a career milestone with timeline data"""
    id: str
    title: str
    description: str
    target_date: str  # Relative like "Year 2" or "Month 6"
    priority: str  # "critical", "high", "medium", "low"
    category: str  # "education", "certification", "project", "skill", "experience"
    prerequisites: List[str]
    skills_gained: List[str]
    estimated_hours: int
    completion_criteria: List[str]
    resources: List[str]
    career_impact: float  # 0.0 to 1.0


@dataclass
class Certification:
    """Industry certification details"""
    name: str
    provider: str
    description: str
    difficulty: str  # "beginner", "intermediate", "advanced", "expert"
    time_to_complete: str
    cost_range: str
    prerequisites: List[str]
    career_relevance: float
    renewal_period: Optional[str]
    exam_info: Optional[Dict[str, any]]


@dataclass
class Project:
    """Career-building project recommendation"""
    id: str
    name: str
    description: str
    type: str  # "portfolio", "open_source", "research", "business", "academic"
    difficulty: str
    estimated_duration: str
    skills_practiced: List[str]
    technologies: List[str]
    deliverables: List[str]
    career_impact: float
    portfolio_value: float


@dataclass
class AlternativePath:
    """Alternative career progression path"""
    path_name: str
    description: str
    transition_requirements: List[str]
    additional_skills: List[str]
    time_to_transition: str
    salary_impact: float  # Percentage change
    market_demand: str
    reasons_to_consider: List[str]


@dataclass
class RoadmapTimeline:
    """Timeline visualization data"""
    timeline_type: TimelineType
    total_duration: str
    phases: List[Dict[str, any]]
    milestones_by_year: Dict[int, List[str]]
    decision_points: List[Dict[str, any]]
    parallel_tracks: Optional[List[Dict[str, any]]]


@dataclass
class CareerRoadmap:
    """Complete career roadmap"""
    career_field: str
    onet_code: Optional[str]
    student_level: str
    current_skills: List[str]
    target_role: str
    roadmap_duration: str
    
    # Core roadmap components
    milestones: List[CareerMilestone]
    certifications: List[Certification]
    projects: List[Project]
    salary_progression: List[SalaryProgression]
    skill_progression: Dict[str, List[str]]  # Year -> skills to develop
    
    # Alternative paths
    alternative_paths: List[AlternativePath]
    pivot_opportunities: List[str]
    
    # Timeline data
    timeline: RoadmapTimeline
    
    # Metadata
    created_date: str
    last_updated: str
    confidence_score: float  # 0.0 to 1.0


class RoadmapGenerator:
    """Main class for generating comprehensive career roadmaps"""
    
    def __init__(self, data_dir: str = None):
        """Initialize the roadmap generator"""
        if data_dir is None:
            data_dir = os.path.dirname(__file__)
        
        self.data_dir = data_dir
        self.careers_data_dir = os.path.join(data_dir, '..', 'data', 'careers')
        self.templates_dir = os.path.join(data_dir, '..', 'data', 'roadmap_templates')
        
        # Data caches
        self.career_data_cache = {}
        self.milestone_templates = {}
        self.certification_paths = {}
        self.project_templates = {}
        self.salary_data = {}
        
        # Load all templates and data
        self._load_templates()
        self._load_career_data()
    
    def _load_templates(self) -> None:
        """Load all roadmap templates"""
        try:
            # Load milestone templates
            milestone_path = os.path.join(self.templates_dir, 'milestone_templates.json')
            if os.path.exists(milestone_path):
                with open(milestone_path, 'r') as f:
                    self.milestone_templates = json.load(f)
            
            # Load certification paths
            cert_path = os.path.join(self.templates_dir, 'certification_paths.json')
            if os.path.exists(cert_path):
                with open(cert_path, 'r') as f:
                    self.certification_paths = json.load(f)
            
            # Load project templates
            project_path = os.path.join(self.templates_dir, 'project_ideas.json')
            if os.path.exists(project_path):
                with open(project_path, 'r') as f:
                    self.project_templates = json.load(f)
            
            logger.info("Successfully loaded roadmap templates")
            
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
            self._initialize_default_templates()
    
    def _load_career_data(self) -> None:
        """Load career data from the careers directory"""
        try:
            if os.path.exists(self.careers_data_dir):
                for filename in os.listdir(self.careers_data_dir):
                    if filename.endswith('.json') and not filename.startswith('.'):
                        career_id = filename.replace('.json', '')
                        file_path = os.path.join(self.careers_data_dir, filename)
                        with open(file_path, 'r') as f:
                            self.career_data_cache[career_id] = json.load(f)
                
                logger.info(f"Loaded {len(self.career_data_cache)} career profiles")
            
        except Exception as e:
            logger.error(f"Error loading career data: {e}")
    
    def _initialize_default_templates(self) -> None:
        """Initialize default templates if files don't exist"""
        self.milestone_templates = {
            "technology": {
                "entry": [
                    {
                        "id": "foundations",
                        "title": "Master Programming Fundamentals",
                        "category": "skill",
                        "priority": "critical"
                    }
                ]
            }
        }
        self.certification_paths = {}
        self.project_templates = {}
    
    def generate_roadmap(
        self,
        career_field: str,
        student_level: str,
        current_skills: List[str] = None,
        target_role: str = None,
        roadmap_years: int = 5,
        location: str = "US_National",
        specializations: List[str] = None,
        budget_constraints: bool = False,
        fast_track: bool = False
    ) -> CareerRoadmap:
        """
        Generate a comprehensive career roadmap
        
        Args:
            career_field: Target career field (e.g., "software_developers")
            student_level: Current student level or experience
            current_skills: List of current skills
            target_role: Specific target role (if different from career_field)
            roadmap_years: Duration in years (5-10)
            location: Geographic location for salary data
            specializations: Specific areas of focus
            budget_constraints: Consider low-cost alternatives
            fast_track: Accelerated timeline options
        
        Returns:
            CareerRoadmap: Complete roadmap with all components
        """
        current_skills = current_skills or []
        specializations = specializations or []
        target_role = target_role or career_field
        
        # Get career data
        career_data = self._get_career_data(career_field)
        if not career_data:
            raise ValueError(f"Career data not found for: {career_field}")
        
        # Generate roadmap components
        milestones = self._generate_milestones(career_field, student_level, current_skills, roadmap_years, fast_track)
        certifications = self._generate_certification_path(career_field, specializations, budget_constraints)
        projects = self._generate_project_recommendations(career_field, student_level, specializations, roadmap_years)
        salary_progression = self._generate_salary_progression(career_data, roadmap_years, location)
        skill_progression = self._generate_skill_progression(career_field, current_skills, roadmap_years, specializations)
        alternative_paths = self._identify_alternative_paths(career_field, current_skills)
        timeline = self._create_timeline(milestones, roadmap_years, fast_track)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(career_data, current_skills, milestones)
        
        return CareerRoadmap(
            career_field=career_field,
            onet_code=career_data.get('onet_code'),
            student_level=student_level,
            current_skills=current_skills,
            target_role=target_role,
            roadmap_duration=f"{roadmap_years} years",
            milestones=milestones,
            certifications=certifications,
            projects=projects,
            salary_progression=salary_progression,
            skill_progression=skill_progression,
            alternative_paths=alternative_paths,
            pivot_opportunities=self._identify_pivot_opportunities(career_field),
            timeline=timeline,
            created_date=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
            confidence_score=confidence_score
        )
    
    def _get_career_data(self, career_field: str) -> Optional[Dict]:
        """Get career data from cache or load from file"""
        if career_field in self.career_data_cache:
            return self.career_data_cache[career_field]
        
        # Try to load from file if not in cache
        file_path = os.path.join(self.careers_data_dir, f"{career_field}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    self.career_data_cache[career_field] = data
                    return data
            except Exception as e:
                logger.error(f"Error loading career data for {career_field}: {e}")
        
        return None
    
    def _generate_milestones(
        self,
        career_field: str,
        student_level: str,
        current_skills: List[str],
        roadmap_years: int,
        fast_track: bool = False
    ) -> List[CareerMilestone]:
        """Generate career milestones based on field and level"""
        milestones = []
        career_data = self._get_career_data(career_field)
        
        if not career_data or 'levels' not in career_data:
            return self._generate_default_milestones(career_field, roadmap_years)
        
        # Extract milestones from career levels
        levels = career_data['levels']
        timeline_factor = 0.7 if fast_track else 1.0
        
        milestone_id = 0
        for level_name, level_data in levels.items():
            if level_name.lower() == 'expert' and roadmap_years < 8:
                continue  # Skip expert level for shorter roadmaps
            
            years_str = level_data.get('years', '0-2')
            year_start = int(years_str.split('-')[0]) if '-' in years_str else 0
            adjusted_year = max(1, int(year_start * timeline_factor))
            
            # Education milestone
            education = level_data.get('education', '')
            if education:
                milestone_id += 1
                milestones.append(CareerMilestone(
                    id=f"edu_{milestone_id}",
                    title=f"Complete {education}",
                    description=f"Achieve educational requirement: {education}",
                    target_date=f"Year {adjusted_year}",
                    priority="critical",
                    category="education",
                    prerequisites=[],
                    skills_gained=level_data.get('skills', [])[:3],
                    estimated_hours=2080,  # Full-time year
                    completion_criteria=[f"Obtain {education}"],
                    resources=["Universities", "Online programs", "Community colleges"],
                    career_impact=0.9
                ))
            
            # Skills milestones
            skills = level_data.get('skills', [])
            for i, skill in enumerate(skills[:3]):  # Top 3 skills per level
                milestone_id += 1
                milestones.append(CareerMilestone(
                    id=f"skill_{milestone_id}",
                    title=f"Master {skill}",
                    description=f"Develop proficiency in {skill}",
                    target_date=f"Year {adjusted_year + (i * 0.5):.1f}",
                    priority="high" if i == 0 else "medium",
                    category="skill",
                    prerequisites=current_skills if i == 0 else [skills[i-1]] if i > 0 else [],
                    skills_gained=[skill],
                    estimated_hours=200 + (i * 100),
                    completion_criteria=[f"Demonstrate {skill} proficiency", "Complete relevant projects"],
                    resources=["Online courses", "Practice projects", "Mentorship"],
                    career_impact=0.8 - (i * 0.1)
                ))
            
            # Project milestones
            projects = level_data.get('projects', [])
            for i, project in enumerate(projects[:2]):  # Top 2 projects per level
                milestone_id += 1
                milestones.append(CareerMilestone(
                    id=f"proj_{milestone_id}",
                    title=project,
                    description=f"Complete project: {project}",
                    target_date=f"Year {adjusted_year + 0.5 + (i * 0.5):.1f}",
                    priority="high",
                    category="project",
                    prerequisites=skills[:1],  # First skill as prerequisite
                    skills_gained=[],
                    estimated_hours=160 + (i * 80),
                    completion_criteria=[f"Successfully complete {project}"],
                    resources=["Team collaboration", "Project management tools"],
                    career_impact=0.7
                ))
        
        return milestones[:roadmap_years * 3]  # Limit milestones based on roadmap duration
    
    def _generate_default_milestones(self, career_field: str, roadmap_years: int) -> List[CareerMilestone]:
        """Generate default milestones when career data is not available"""
        milestones = []
        
        # Generic milestones that apply to most careers
        generic_milestones = [
            {
                "title": "Complete Foundational Education",
                "category": "education",
                "year": 1,
                "priority": "critical"
            },
            {
                "title": "Gain Entry-Level Experience",
                "category": "experience", 
                "year": 2,
                "priority": "high"
            },
            {
                "title": "Develop Specialized Skills",
                "category": "skill",
                "year": 3,
                "priority": "high"
            },
            {
                "title": "Take on Leadership Role",
                "category": "experience",
                "year": 4,
                "priority": "medium"
            },
            {
                "title": "Pursue Advanced Certification",
                "category": "certification",
                "year": 5,
                "priority": "medium"
            }
        ]
        
        for i, milestone_data in enumerate(generic_milestones):
            if milestone_data["year"] <= roadmap_years:
                milestones.append(CareerMilestone(
                    id=f"default_{i}",
                    title=milestone_data["title"],
                    description=f"Generic milestone for {career_field}",
                    target_date=f"Year {milestone_data['year']}",
                    priority=milestone_data["priority"],
                    category=milestone_data["category"],
                    prerequisites=[],
                    skills_gained=[],
                    estimated_hours=300,
                    completion_criteria=[milestone_data["title"]],
                    resources=["Industry resources", "Professional development"],
                    career_impact=0.6
                ))
        
        return milestones
    
    def _generate_certification_path(
        self,
        career_field: str,
        specializations: List[str],
        budget_constraints: bool = False
    ) -> List[Certification]:
        """Generate certification recommendations"""
        certifications = []
        
        # Check if we have certification data for this field
        field_certs = self.certification_paths.get(career_field, {})
        if not field_certs:
            # Try to get from career data
            career_data = self._get_career_data(career_field)
            if career_data and 'levels' in career_data:
                return self._extract_certifications_from_career_data(career_data, budget_constraints)
        
        # Process certification path data
        for level, cert_list in field_certs.items():
            for cert_data in cert_list:
                if budget_constraints and cert_data.get('cost_range', 'medium') == 'high':
                    continue
                
                certifications.append(Certification(
                    name=cert_data['name'],
                    provider=cert_data.get('provider', 'Various'),
                    description=cert_data.get('description', ''),
                    difficulty=cert_data.get('difficulty', 'intermediate'),
                    time_to_complete=cert_data.get('time_to_complete', '3-6 months'),
                    cost_range=cert_data.get('cost_range', '$100-$500'),
                    prerequisites=cert_data.get('prerequisites', []),
                    career_relevance=cert_data.get('career_relevance', 0.8),
                    renewal_period=cert_data.get('renewal_period'),
                    exam_info=cert_data.get('exam_info')
                ))
        
        return certifications
    
    def _extract_certifications_from_career_data(self, career_data: Dict, budget_constraints: bool) -> List[Certification]:
        """Extract certifications from career level data"""
        certifications = []
        
        for level_name, level_data in career_data.get('levels', {}).items():
            certs = level_data.get('certifications', [])
            for cert_name in certs:
                # Create basic certification object
                cost_range = "$50-$300" if budget_constraints else "$100-$1000"
                
                certifications.append(Certification(
                    name=cert_name,
                    provider="Various",
                    description=f"Industry certification for {cert_name}",
                    difficulty=self._map_level_to_difficulty(level_name),
                    time_to_complete="2-4 months",
                    cost_range=cost_range,
                    prerequisites=[],
                    career_relevance=0.8,
                    renewal_period="2-3 years",
                    exam_info=None
                ))
        
        return certifications
    
    def _map_level_to_difficulty(self, level_name: str) -> str:
        """Map career level to certification difficulty"""
        level_map = {
            "entry": "beginner",
            "junior": "intermediate",
            "mid-level": "intermediate",
            "senior": "advanced",
            "expert": "expert"
        }
        return level_map.get(level_name.lower(), "intermediate")
    
    def _generate_project_recommendations(
        self,
        career_field: str,
        student_level: str,
        specializations: List[str],
        roadmap_years: int
    ) -> List[Project]:
        """Generate project recommendations"""
        projects = []
        project_templates = self.project_templates.get(career_field, {})
        
        if not project_templates:
            # Generate default projects
            return self._generate_default_projects(career_field, roadmap_years)
        
        project_id = 0
        for project_type, project_list in project_templates.items():
            for project_data in project_list[:roadmap_years]:  # Limit by roadmap years
                project_id += 1
                projects.append(Project(
                    id=f"proj_{project_id}",
                    name=project_data['name'],
                    description=project_data.get('description', ''),
                    type=project_type,
                    difficulty=project_data.get('difficulty', 'intermediate'),
                    estimated_duration=project_data.get('duration', '2-4 weeks'),
                    skills_practiced=project_data.get('skills', []),
                    technologies=project_data.get('technologies', []),
                    deliverables=project_data.get('deliverables', []),
                    career_impact=project_data.get('career_impact', 0.7),
                    portfolio_value=project_data.get('portfolio_value', 0.8)
                ))
        
        return projects
    
    def _generate_default_projects(self, career_field: str, roadmap_years: int) -> List[Project]:
        """Generate default projects when templates are not available"""
        projects = []
        
        # Default project types based on career field
        if 'software' in career_field.lower() or 'computer' in career_field.lower():
            default_projects = [
                {
                    "name": "Personal Website Portfolio",
                    "type": "portfolio",
                    "difficulty": "beginner",
                    "duration": "2-3 weeks"
                },
                {
                    "name": "Web Application Project",
                    "type": "portfolio",
                    "difficulty": "intermediate", 
                    "duration": "1-2 months"
                },
                {
                    "name": "Open Source Contribution",
                    "type": "open_source",
                    "difficulty": "intermediate",
                    "duration": "Ongoing"
                }
            ]
        else:
            default_projects = [
                {
                    "name": "Industry Research Project",
                    "type": "research",
                    "difficulty": "beginner",
                    "duration": "1 month"
                },
                {
                    "name": "Professional Networking Initiative",
                    "type": "business",
                    "difficulty": "intermediate",
                    "duration": "6 months"
                }
            ]
        
        for i, proj_data in enumerate(default_projects[:roadmap_years]):
            projects.append(Project(
                id=f"default_proj_{i}",
                name=proj_data['name'],
                description=f"Default project for {career_field}",
                type=proj_data['type'],
                difficulty=proj_data['difficulty'],
                estimated_duration=proj_data['duration'],
                skills_practiced=[],
                technologies=[],
                deliverables=[],
                career_impact=0.6,
                portfolio_value=0.7
            ))
        
        return projects
    
    def _generate_salary_progression(
        self,
        career_data: Dict,
        roadmap_years: int,
        location: str = "US_National"
    ) -> List[SalaryProgression]:
        """Generate salary progression over time"""
        salary_progression = []
        
        if 'levels' not in career_data:
            return self._generate_default_salary_progression(roadmap_years)
        
        location_factors = {
            "US_National": 1.0,
            "Silicon_Valley": 1.6,
            "New_York": 1.4,
            "Austin": 1.2,
            "Remote": 1.1
        }
        
        location_factor = location_factors.get(location, 1.0)
        
        for level_name, level_data in career_data['levels'].items():
            years_str = level_data.get('years', '0-2')
            salary_range = level_data.get('salary_range', '$50,000 - $70,000')
            
            # Parse salary range
            try:
                salary_parts = salary_range.replace('$', '').replace(',', '').split(' - ')
                min_salary = int(salary_parts[0])
                max_salary = int(salary_parts[1].replace('+', ''))
                median_salary = (min_salary + max_salary) // 2
                
                # Apply location factor
                min_salary = int(min_salary * location_factor)
                max_salary = int(max_salary * location_factor)
                median_salary = int(median_salary * location_factor)
                
                salary_progression.append(SalaryProgression(
                    level=CareerLevel(level_name.lower().replace('-', '_')),
                    years_experience=years_str,
                    min_salary=min_salary,
                    max_salary=max_salary,
                    median_salary=median_salary,
                    location_factor=location_factor,
                    currency="USD"
                ))
                
            except (ValueError, IndexError) as e:
                logger.warning(f"Could not parse salary range: {salary_range} - {e}")
                continue
        
        return salary_progression
    
    def _generate_default_salary_progression(self, roadmap_years: int) -> List[SalaryProgression]:
        """Generate default salary progression when data is not available"""
        base_salaries = [45000, 60000, 80000, 105000, 130000]
        levels = [CareerLevel.ENTRY, CareerLevel.JUNIOR, CareerLevel.MID_LEVEL, CareerLevel.SENIOR, CareerLevel.EXPERT]
        years = ["0-2", "2-4", "4-7", "7-10", "10+"]
        
        progression = []
        for i in range(min(len(levels), roadmap_years)):
            base = base_salaries[i]
            progression.append(SalaryProgression(
                level=levels[i],
                years_experience=years[i],
                min_salary=int(base * 0.8),
                max_salary=int(base * 1.3),
                median_salary=base,
                location_factor=1.0,
                currency="USD"
            ))
        
        return progression
    
    def _generate_skill_progression(
        self,
        career_field: str,
        current_skills: List[str],
        roadmap_years: int,
        specializations: List[str]
    ) -> Dict[str, List[str]]:
        """Generate year-by-year skill progression"""
        skill_progression = {}
        career_data = self._get_career_data(career_field)
        
        if not career_data or 'levels' not in career_data:
            return self._generate_default_skill_progression(roadmap_years, current_skills)
        
        # Distribute skills across years based on career levels
        all_skills = []
        for level_data in career_data['levels'].values():
            all_skills.extend(level_data.get('skills', []))
        
        # Remove duplicates while preserving order
        unique_skills = []
        for skill in all_skills:
            if skill not in unique_skills and skill not in current_skills:
                unique_skills.append(skill)
        
        # Distribute skills across years
        skills_per_year = max(2, len(unique_skills) // roadmap_years)
        for year in range(1, roadmap_years + 1):
            start_idx = (year - 1) * skills_per_year
            end_idx = start_idx + skills_per_year
            
            year_skills = unique_skills[start_idx:end_idx]
            
            # Add specialization-specific skills
            if specializations and year <= len(specializations):
                year_skills.extend([f"Advanced {specializations[year-1]}"])
            
            skill_progression[str(year)] = year_skills
        
        return skill_progression
    
    def _generate_default_skill_progression(self, roadmap_years: int, current_skills: List[str]) -> Dict[str, List[str]]:
        """Generate default skill progression"""
        default_skills = [
            "Communication", "Problem Solving", "Team Collaboration", "Project Management",
            "Leadership", "Strategic Thinking", "Data Analysis", "Technical Writing",
            "Process Improvement", "Industry Knowledge"
        ]
        
        available_skills = [s for s in default_skills if s not in current_skills]
        skills_per_year = max(2, len(available_skills) // roadmap_years)
        
        progression = {}
        for year in range(1, roadmap_years + 1):
            start_idx = (year - 1) * skills_per_year
            end_idx = start_idx + skills_per_year
            progression[str(year)] = available_skills[start_idx:end_idx]
        
        return progression
    
    def _identify_alternative_paths(self, career_field: str, current_skills: List[str]) -> List[AlternativePath]:
        """Identify alternative career progression paths"""
        alternatives = []
        career_data = self._get_career_data(career_field)
        
        # Get related careers from data
        related_careers = career_data.get('related_careers', []) if career_data else []
        
        for related_career in related_careers[:3]:  # Limit to top 3 alternatives
            alternatives.append(AlternativePath(
                path_name=f"Transition to {related_career}",
                description=f"Alternative path focusing on {related_career}",
                transition_requirements=[
                    f"Additional training in {related_career}",
                    "Build relevant project portfolio",
                    "Network with {related_career} professionals"
                ],
                additional_skills=[f"{related_career} expertise", "Cross-functional knowledge"],
                time_to_transition="6-12 months",
                salary_impact=0.1,  # 10% potential increase
                market_demand="High",
                reasons_to_consider=[
                    f"Growing demand in {related_career}",
                    "Leverages existing skills",
                    "Better work-life balance potential"
                ]
            ))
        
        # Add generic alternative paths
        if not alternatives:
            alternatives.append(AlternativePath(
                path_name="Management Track",
                description="Transition into management and leadership roles",
                transition_requirements=[
                    "Leadership experience",
                    "Management training",
                    "Proven team collaboration"
                ],
                additional_skills=["People Management", "Strategic Planning", "Budget Management"],
                time_to_transition="12-18 months",
                salary_impact=0.15,
                market_demand="Medium",
                reasons_to_consider=[
                    "Higher earning potential",
                    "Greater decision-making authority",
                    "Opportunity to mentor others"
                ]
            ))
        
        return alternatives
    
    def _identify_pivot_opportunities(self, career_field: str) -> List[str]:
        """Identify career pivot opportunities"""
        pivots = []
        
        # Industry-specific pivot opportunities
        if 'software' in career_field.lower():
            pivots = [
                "Data Science",
                "Product Management", 
                "DevOps Engineering",
                "Technical Writing",
                "UX/UI Design"
            ]
        elif 'business' in career_field.lower():
            pivots = [
                "Management Consulting",
                "Project Management",
                "Business Analysis",
                "Operations Management",
                "Entrepreneurship"
            ]
        else:
            pivots = [
                "Consulting",
                "Training & Development",
                "Project Management",
                "Quality Assurance"
            ]
        
        return pivots[:5]  # Limit to 5 opportunities
    
    def _create_timeline(self, milestones: List[CareerMilestone], roadmap_years: int, fast_track: bool = False) -> RoadmapTimeline:
        """Create timeline visualization data"""
        
        # Group milestones by year
        milestones_by_year = {}
        for milestone in milestones:
            # Extract year from target_date (e.g., "Year 2.5" -> 2)
            try:
                year = int(float(milestone.target_date.replace('Year ', '')))
                if year not in milestones_by_year:
                    milestones_by_year[year] = []
                milestones_by_year[year].append(milestone.title)
            except (ValueError, AttributeError):
                # Default to year 1 if parsing fails
                if 1 not in milestones_by_year:
                    milestones_by_year[1] = []
                milestones_by_year[1].append(milestone.title)
        
        # Create phases
        phases = []
        phase_duration = max(1, roadmap_years // 3)
        
        for i in range(0, roadmap_years, phase_duration):
            phase_end = min(i + phase_duration, roadmap_years)
            phase_milestones = []
            
            for year in range(i + 1, phase_end + 1):
                phase_milestones.extend(milestones_by_year.get(year, []))
            
            phases.append({
                "phase_name": f"Phase {len(phases) + 1}",
                "years": f"Year {i + 1}-{phase_end}",
                "focus": self._determine_phase_focus(i + 1, roadmap_years),
                "milestones": phase_milestones[:5]  # Limit milestones per phase
            })
        
        # Identify decision points
        decision_points = []
        for year in [2, int(roadmap_years / 2), roadmap_years - 1]:
            if year <= roadmap_years:
                decision_points.append({
                    "year": year,
                    "decision": f"Career Assessment & Path Adjustment",
                    "options": ["Continue current path", "Pivot to alternative", "Accelerate progress"]
                })
        
        return RoadmapTimeline(
            timeline_type=TimelineType.MILESTONE,
            total_duration=f"{roadmap_years} years",
            phases=phases,
            milestones_by_year=milestones_by_year,
            decision_points=decision_points,
            parallel_tracks=None
        )
    
    def _determine_phase_focus(self, phase_start: int, total_years: int) -> str:
        """Determine the focus for each phase"""
        if phase_start == 1:
            return "Foundation & Learning"
        elif phase_start <= total_years / 2:
            return "Skill Development & Experience"
        else:
            return "Leadership & Specialization"
    
    def _calculate_confidence_score(self, career_data: Dict, current_skills: List[str], milestones: List[CareerMilestone]) -> float:
        """Calculate confidence score for the roadmap"""
        score = 0.5  # Base score
        
        # Add points for having complete career data
        if career_data and 'levels' in career_data:
            score += 0.2
        
        # Add points for relevant current skills
        if current_skills:
            score += min(0.2, len(current_skills) * 0.05)
        
        # Add points for milestone quality
        if milestones:
            critical_milestones = [m for m in milestones if m.priority == "critical"]
            score += min(0.1, len(critical_milestones) * 0.02)
        
        return min(1.0, score)
    
    def export_roadmap(self, roadmap: CareerRoadmap, filepath: str, format: str = "json") -> bool:
        """Export roadmap to file"""
        try:
            if format.lower() == "json":
                roadmap_dict = asdict(roadmap)
                with open(filepath, 'w') as f:
                    json.dump(roadmap_dict, f, indent=2, default=str)
                
                logger.info(f"Roadmap exported to {filepath}")
                return True
            
        except Exception as e:
            logger.error(f"Error exporting roadmap: {e}")
            return False
    
    def get_roadmap_summary(self, roadmap: CareerRoadmap) -> Dict[str, any]:
        """Generate a summary of the roadmap"""
        return {
            "career_field": roadmap.career_field,
            "duration": roadmap.roadmap_duration,
            "total_milestones": len(roadmap.milestones),
            "critical_milestones": len([m for m in roadmap.milestones if m.priority == "critical"]),
            "certifications": len(roadmap.certifications),
            "projects": len(roadmap.projects),
            "alternative_paths": len(roadmap.alternative_paths),
            "salary_growth": self._calculate_salary_growth(roadmap.salary_progression),
            "skills_to_learn": sum(len(skills) for skills in roadmap.skill_progression.values()),
            "confidence_score": roadmap.confidence_score,
            "next_milestone": self._get_next_milestone(roadmap.milestones),
            "timeline_phases": len(roadmap.timeline.phases)
        }
    
    def _calculate_salary_growth(self, salary_progression: List[SalaryProgression]) -> str:
        """Calculate salary growth percentage"""
        if len(salary_progression) < 2:
            return "Data unavailable"
        
        start_salary = salary_progression[0].median_salary
        end_salary = salary_progression[-1].median_salary
        growth = ((end_salary - start_salary) / start_salary) * 100
        
        return f"{growth:.1f}%"
    
    def _get_next_milestone(self, milestones: List[CareerMilestone]) -> Optional[str]:
        """Get the next upcoming milestone"""
        critical_milestones = [m for m in milestones if m.priority == "critical"]
        if critical_milestones:
            return critical_milestones[0].title
        elif milestones:
            return milestones[0].title
        return None


# Example usage
if __name__ == "__main__":
    generator = RoadmapGenerator()
    
    # Generate sample roadmap
    roadmap = generator.generate_roadmap(
        career_field="software_developers",
        student_level="college_sophomore",
        current_skills=["Python", "HTML", "CSS"],
        roadmap_years=5,
        specializations=["Web Development", "Data Science"]
    )
    
    # Print summary
    summary = generator.get_roadmap_summary(roadmap)
    print(json.dumps(summary, indent=2))