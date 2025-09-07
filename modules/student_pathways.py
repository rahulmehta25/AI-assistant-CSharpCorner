"""
Student Pathway System

A comprehensive module that creates personalized career pathways for high school 
and college students, mapping O*NET careers to specific educational paths with 
year-by-year guidance.

Author: AI Career Assistant
Created: September 2025
"""

import json
import os
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StudentLevel(Enum):
    """Student education levels"""
    FRESHMAN_HS = "freshman_hs"  # Grade 9
    SOPHOMORE_HS = "sophomore_hs"  # Grade 10
    JUNIOR_HS = "junior_hs"  # Grade 11
    SENIOR_HS = "senior_hs"  # Grade 12
    FRESHMAN_COLLEGE = "freshman_college"
    SOPHOMORE_COLLEGE = "sophomore_college"
    JUNIOR_COLLEGE = "junior_college"
    SENIOR_COLLEGE = "senior_college"


@dataclass
class Milestone:
    """Represents a milestone in student pathway"""
    title: str
    description: str
    deadline: str
    priority: str  # "high", "medium", "low"
    category: str  # "academic", "career", "application", "skill"


@dataclass
class CourseRecommendation:
    """Represents a course recommendation"""
    course_name: str
    course_type: str  # "AP", "honors", "regular", "college", "major_required", "elective"
    description: str
    prerequisites: List[str]
    difficulty_level: str  # "beginner", "intermediate", "advanced"
    relevance_score: float  # 0.0 to 1.0


@dataclass
class Activity:
    """Represents an extracurricular activity or opportunity"""
    name: str
    type: str  # "club", "sport", "volunteer", "internship", "competition", "leadership"
    description: str
    time_commitment: str
    skills_gained: List[str]
    career_relevance: float  # 0.0 to 1.0


@dataclass
class Pathway:
    """Complete pathway for a student"""
    student_level: StudentLevel
    career_field: str
    onet_code: Optional[str]
    milestones: List[Milestone]
    courses: List[CourseRecommendation]
    activities: List[Activity]
    skills_to_develop: List[str]
    timeline: Dict[str, List[str]]  # month -> list of tasks


class StudentPathwaySystem:
    """Main class for generating student pathways"""
    
    def __init__(self, data_dir: str = None):
        """Initialize the pathway system"""
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'education_pathways')
        
        self.data_dir = data_dir
        self.templates = {}
        self.skills_by_grade = {}
        self.activities_by_career = {}
        
        # Load data templates
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load all pathway templates from JSON files"""
        try:
            # Load high school pathway template
            hs_path = os.path.join(self.data_dir, 'high_school_pathway_template.json')
            if os.path.exists(hs_path):
                with open(hs_path, 'r') as f:
                    self.templates['high_school'] = json.load(f)
            
            # Load college pathway template
            college_path = os.path.join(self.data_dir, 'college_pathway_template.json')
            if os.path.exists(college_path):
                with open(college_path, 'r') as f:
                    self.templates['college'] = json.load(f)
            
            # Load skills by grade
            skills_path = os.path.join(self.data_dir, 'skills_by_grade.json')
            if os.path.exists(skills_path):
                with open(skills_path, 'r') as f:
                    self.skills_by_grade = json.load(f)
            
            # Load activities by career
            activities_path = os.path.join(self.data_dir, 'activities_by_career.json')
            if os.path.exists(activities_path):
                with open(activities_path, 'r') as f:
                    self.activities_by_career = json.load(f)
                    
            logger.info("Successfully loaded pathway templates")
            
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
            # Initialize with empty templates if files don't exist
            self._initialize_empty_templates()
    
    def _initialize_empty_templates(self) -> None:
        """Initialize empty templates if files don't exist"""
        self.templates = {'high_school': {}, 'college': {}}
        self.skills_by_grade = {}
        self.activities_by_career = {}
    
    def generate_pathway(
        self, 
        student_level: StudentLevel, 
        career_field: str, 
        onet_code: str = None,
        interests: List[str] = None,
        current_skills: List[str] = None,
        gpa: float = None,
        standardized_scores: Dict[str, int] = None
    ) -> Pathway:
        """
        Generate a personalized pathway for a student
        
        Args:
            student_level: Current student level (grade/year)
            career_field: Target career field
            onet_code: O*NET SOC code for specific career
            interests: List of student interests
            current_skills: List of current skills
            gpa: Current GPA (if available)
            standardized_scores: Dict with test scores (SAT, ACT, etc.)
        
        Returns:
            Pathway: Complete pathway with recommendations
        """
        interests = interests or []
        current_skills = current_skills or []
        standardized_scores = standardized_scores or {}
        
        # Determine if high school or college
        is_high_school = student_level.value.endswith('_hs')
        template_key = 'high_school' if is_high_school else 'college'
        
        # Generate pathway components
        milestones = self._generate_milestones(student_level, career_field, gpa, standardized_scores)
        courses = self._generate_course_recommendations(student_level, career_field, onet_code, current_skills)
        activities = self._generate_activity_recommendations(career_field, interests, student_level)
        skills_to_develop = self._identify_skills_gap(student_level, career_field, current_skills)
        timeline = self._create_timeline(student_level, milestones, courses, activities)
        
        return Pathway(
            student_level=student_level,
            career_field=career_field,
            onet_code=onet_code,
            milestones=milestones,
            courses=courses,
            activities=activities,
            skills_to_develop=skills_to_develop,
            timeline=timeline
        )
    
    def _generate_milestones(
        self, 
        level: StudentLevel, 
        career_field: str, 
        gpa: float = None,
        test_scores: Dict[str, int] = None
    ) -> List[Milestone]:
        """Generate grade/year-specific milestones"""
        milestones = []
        
        if level == StudentLevel.FRESHMAN_HS:
            milestones.extend([
                Milestone("Explore Interests", "Take career assessment and explore different fields", "End of Fall", "high", "career"),
                Milestone("Build Strong Foundation", "Focus on core academic subjects", "Ongoing", "high", "academic"),
                Milestone("Join Clubs", "Join 1-2 clubs related to interests", "October", "medium", "career"),
                Milestone("Develop Study Habits", "Establish effective study routines", "September", "high", "skill")
            ])
        
        elif level == StudentLevel.SOPHOMORE_HS:
            milestones.extend([
                Milestone("Choose Career Path", "Research and narrow down career interests", "End of Spring", "high", "career"),
                Milestone("Plan Junior Year Courses", "Select challenging courses for junior year", "March", "high", "academic"),
                Milestone("Begin Standardized Test Prep", "Start SAT/ACT preparation", "January", "high", "application"),
                Milestone("Leadership Opportunities", "Take on leadership roles in activities", "Ongoing", "medium", "career")
            ])
        
        elif level == StudentLevel.JUNIOR_HS:
            milestones.extend([
                Milestone("Take Standardized Tests", "Complete SAT/ACT and subject tests", "Spring", "high", "application"),
                Milestone("Research Colleges", "Create list of target colleges", "Fall", "high", "application"),
                Milestone("Summer Programs/Internships", "Apply for relevant summer experiences", "February", "high", "career"),
                Milestone("Build College List", "Finalize college application list", "Spring", "high", "application")
            ])
        
        elif level == StudentLevel.SENIOR_HS:
            milestones.extend([
                Milestone("Submit Applications", "Complete all college applications", "January", "high", "application"),
                Milestone("Apply for Financial Aid", "Complete FAFSA and scholarship applications", "January", "high", "application"),
                Milestone("Senior Project", "Complete capstone project related to career field", "Spring", "medium", "career"),
                Milestone("Make College Decision", "Choose college and submit enrollment deposit", "May", "high", "application")
            ])
        
        elif level == StudentLevel.FRESHMAN_COLLEGE:
            milestones.extend([
                Milestone("Declare/Explore Major", "Confirm major or explore options", "End of Freshman Year", "high", "academic"),
                Milestone("Build Academic Foundation", "Excel in core requirements", "Ongoing", "high", "academic"),
                Milestone("Join Professional Organizations", "Join clubs related to career field", "Fall", "medium", "career"),
                Milestone("Meet with Career Services", "Establish relationship with career center", "Spring", "medium", "career")
            ])
        
        elif level == StudentLevel.SOPHOMORE_COLLEGE:
            milestones.extend([
                Milestone("Summer Internship", "Secure relevant summer internship", "Spring application", "high", "career"),
                Milestone("Develop Technical Skills", "Build portfolio and technical competencies", "Ongoing", "high", "skill"),
                Milestone("Research Study Abroad", "Explore international opportunities", "Fall", "low", "academic"),
                Milestone("Network Building", "Attend career fairs and networking events", "Ongoing", "medium", "career")
            ])
        
        elif level == StudentLevel.JUNIOR_COLLEGE:
            milestones.extend([
                Milestone("Major Internship/Co-op", "Complete significant work experience", "Summer", "high", "career"),
                Milestone("Research Projects", "Engage in research or capstone projects", "Fall", "high", "academic"),
                Milestone("GRE/Professional Exams", "Prepare for graduate school or professional exams", "Spring", "medium", "application"),
                Milestone("Leadership Roles", "Take on significant leadership positions", "Ongoing", "medium", "career")
            ])
        
        elif level == StudentLevel.SENIOR_COLLEGE:
            milestones.extend([
                Milestone("Job/Grad School Applications", "Apply for jobs or graduate programs", "Fall", "high", "application"),
                Milestone("Complete Capstone", "Finish senior thesis or capstone project", "Spring", "high", "academic"),
                Milestone("Professional Certification", "Obtain relevant industry certifications", "Spring", "medium", "career"),
                Milestone("Transition Planning", "Plan for post-graduation transition", "Spring", "high", "career")
            ])
        
        # Add career-specific milestones
        career_milestones = self._get_career_specific_milestones(career_field, level)
        milestones.extend(career_milestones)
        
        return milestones
    
    def _get_career_specific_milestones(self, career_field: str, level: StudentLevel) -> List[Milestone]:
        """Get milestones specific to career field"""
        milestones = []
        
        # STEM careers
        if career_field.lower() in ['engineering', 'computer science', 'medicine', 'research']:
            if level in [StudentLevel.SOPHOMORE_HS, StudentLevel.JUNIOR_HS]:
                milestones.append(Milestone("STEM Competitions", "Participate in science fairs or coding competitions", "Spring", "medium", "career"))
            if level in [StudentLevel.JUNIOR_COLLEGE, StudentLevel.SENIOR_COLLEGE]:
                milestones.append(Milestone("Research Publication", "Work towards publishing research", "Spring", "medium", "career"))
        
        # Business careers
        elif career_field.lower() in ['business', 'finance', 'marketing']:
            if level in [StudentLevel.JUNIOR_HS, StudentLevel.SENIOR_HS]:
                milestones.append(Milestone("Business Plan Competition", "Enter entrepreneurship competitions", "Spring", "low", "career"))
            if level in [StudentLevel.SOPHOMORE_COLLEGE, StudentLevel.JUNIOR_COLLEGE]:
                milestones.append(Milestone("Professional Certification", "Pursue relevant business certifications", "Summer", "medium", "career"))
        
        # Arts careers
        elif career_field.lower() in ['art', 'design', 'media', 'creative']:
            if level in [StudentLevel.JUNIOR_HS, StudentLevel.SENIOR_HS]:
                milestones.append(Milestone("Portfolio Development", "Build comprehensive portfolio", "Ongoing", "high", "career"))
            if level in [StudentLevel.SOPHOMORE_COLLEGE, StudentLevel.JUNIOR_COLLEGE]:
                milestones.append(Milestone("Gallery/Exhibition", "Showcase work in exhibitions", "Spring", "medium", "career"))
        
        return milestones
    
    def _generate_course_recommendations(
        self, 
        level: StudentLevel, 
        career_field: str, 
        onet_code: str = None,
        current_skills: List[str] = None
    ) -> List[CourseRecommendation]:
        """Generate course recommendations based on level and career field"""
        courses = []
        current_skills = current_skills or []
        
        if level == StudentLevel.FRESHMAN_HS:
            # Core foundation courses
            courses.extend([
                CourseRecommendation("Algebra II", "regular", "Strong math foundation", ["Algebra I"], "intermediate", 0.9),
                CourseRecommendation("Biology", "regular", "Introduction to life sciences", [], "beginner", 0.8),
                CourseRecommendation("English I", "regular", "Communication skills", [], "beginner", 1.0),
                CourseRecommendation("World History", "regular", "Global perspectives", [], "beginner", 0.6)
            ])
        
        elif level == StudentLevel.SOPHOMORE_HS:
            courses.extend([
                CourseRecommendation("Geometry", "regular", "Spatial reasoning", ["Algebra II"], "intermediate", 0.8),
                CourseRecommendation("Chemistry", "regular", "Physical sciences foundation", ["Biology"], "intermediate", 0.9),
                CourseRecommendation("English II", "regular", "Advanced communication", ["English I"], "intermediate", 1.0)
            ])
            
            # Career-specific recommendations
            if career_field.lower() in ['engineering', 'computer science']:
                courses.append(CourseRecommendation("Introduction to Computer Science", "regular", "Programming basics", [], "beginner", 1.0))
        
        elif level == StudentLevel.JUNIOR_HS:
            courses.extend([
                CourseRecommendation("Pre-Calculus", "regular", "Advanced math preparation", ["Geometry"], "intermediate", 0.9),
                CourseRecommendation("Physics", "regular", "Physical world understanding", ["Chemistry"], "intermediate", 0.8),
                CourseRecommendation("English III", "regular", "Literature and composition", ["English II"], "intermediate", 1.0)
            ])
            
            # AP course recommendations
            if career_field.lower() in ['engineering', 'computer science', 'medicine']:
                courses.extend([
                    CourseRecommendation("AP Calculus AB", "AP", "Advanced mathematics", ["Pre-Calculus"], "advanced", 1.0),
                    CourseRecommendation("AP Physics 1", "AP", "Advanced physics", ["Physics"], "advanced", 0.9),
                    CourseRecommendation("AP Computer Science A", "AP", "Advanced programming", ["Intro CS"], "advanced", 1.0)
                ])
        
        elif level == StudentLevel.SENIOR_HS:
            # Advanced courses for college prep
            if career_field.lower() in ['engineering', 'computer science']:
                courses.extend([
                    CourseRecommendation("AP Calculus BC", "AP", "Advanced calculus", ["AP Calc AB"], "advanced", 1.0),
                    CourseRecommendation("AP Chemistry", "AP", "Advanced chemistry", ["Chemistry"], "advanced", 0.9),
                    CourseRecommendation("AP Physics C", "AP", "Calculus-based physics", ["AP Physics 1"], "advanced", 0.9)
                ])
        
        # College-level courses
        elif level == StudentLevel.FRESHMAN_COLLEGE:
            if career_field.lower() == 'computer science':
                courses.extend([
                    CourseRecommendation("Introduction to Programming", "major_required", "Programming fundamentals", [], "beginner", 1.0),
                    CourseRecommendation("Calculus I", "major_required", "Mathematical foundations", [], "intermediate", 1.0),
                    CourseRecommendation("Introduction to Computer Science", "major_required", "CS concepts", [], "beginner", 1.0)
                ])
            elif career_field.lower() == 'engineering':
                courses.extend([
                    CourseRecommendation("Engineering Fundamentals", "major_required", "Engineering principles", [], "beginner", 1.0),
                    CourseRecommendation("Calculus I", "major_required", "Mathematical foundations", [], "intermediate", 1.0),
                    CourseRecommendation("Physics I", "major_required", "Mechanics", [], "intermediate", 1.0)
                ])
        
        elif level == StudentLevel.SOPHOMORE_COLLEGE:
            if career_field.lower() == 'computer science':
                courses.extend([
                    CourseRecommendation("Data Structures", "major_required", "Advanced programming", ["Intro Programming"], "intermediate", 1.0),
                    CourseRecommendation("Computer Systems", "major_required", "Hardware understanding", [], "intermediate", 0.9),
                    CourseRecommendation("Discrete Mathematics", "major_required", "Mathematical reasoning", ["Calculus I"], "intermediate", 0.8)
                ])
        
        elif level == StudentLevel.JUNIOR_COLLEGE:
            if career_field.lower() == 'computer science':
                courses.extend([
                    CourseRecommendation("Algorithms", "major_required", "Algorithm design", ["Data Structures"], "advanced", 1.0),
                    CourseRecommendation("Database Systems", "major_required", "Data management", [], "intermediate", 0.9),
                    CourseRecommendation("Software Engineering", "major_required", "Development practices", [], "intermediate", 1.0)
                ])
        
        elif level == StudentLevel.SENIOR_COLLEGE:
            if career_field.lower() == 'computer science':
                courses.extend([
                    CourseRecommendation("Machine Learning", "elective", "AI fundamentals", ["Algorithms"], "advanced", 0.9),
                    CourseRecommendation("Capstone Project", "major_required", "Applied project work", [], "advanced", 1.0),
                    CourseRecommendation("Professional Development", "elective", "Career preparation", [], "beginner", 0.8)
                ])
        
        return courses
    
    def _generate_activity_recommendations(
        self, 
        career_field: str, 
        interests: List[str], 
        level: StudentLevel
    ) -> List[Activity]:
        """Generate activity recommendations"""
        activities = []
        
        # High school activities
        if level.value.endswith('_hs'):
            # STEM career activities
            if career_field.lower() in ['engineering', 'computer science', 'medicine']:
                activities.extend([
                    Activity("Robotics Club", "club", "Build and program robots", "10-15 hours/week", 
                           ["programming", "teamwork", "problem-solving"], 1.0),
                    Activity("Science Olympiad", "competition", "Academic STEM competition", "5-8 hours/week",
                           ["research", "presentation", "analytical thinking"], 0.9),
                    Activity("Math Team", "club", "Mathematical problem solving", "3-5 hours/week",
                           ["mathematics", "logic", "competition"], 0.8)
                ])
            
            # Business career activities
            elif career_field.lower() in ['business', 'finance', 'marketing']:
                activities.extend([
                    Activity("DECA", "club", "Business and marketing competition", "8-12 hours/week",
                           ["business knowledge", "presentation", "networking"], 1.0),
                    Activity("Student Government", "leadership", "School leadership role", "5-10 hours/week",
                           ["leadership", "public speaking", "organization"], 0.9),
                    Activity("Debate Team", "club", "Argumentation and public speaking", "6-10 hours/week",
                           ["communication", "research", "critical thinking"], 0.8)
                ])
            
            # Arts career activities
            elif career_field.lower() in ['art', 'design', 'media']:
                activities.extend([
                    Activity("Art Club", "club", "Creative expression and portfolio building", "4-8 hours/week",
                           ["creativity", "artistic skills", "portfolio development"], 1.0),
                    Activity("Yearbook/Newspaper", "club", "Design and media production", "8-12 hours/week",
                           ["design", "writing", "deadline management"], 0.9),
                    Activity("Theater/Drama", "club", "Performance and creative expression", "10-15 hours/week",
                           ["creativity", "teamwork", "confidence"], 0.8)
                ])
        
        # College activities
        else:
            # Professional organizations
            if career_field.lower() == 'computer science':
                activities.extend([
                    Activity("ACM Student Chapter", "club", "Professional computer science organization", "3-5 hours/week",
                           ["networking", "professional development", "technical skills"], 1.0),
                    Activity("Hackathons", "competition", "Programming competitions", "Weekend events",
                           ["programming", "teamwork", "innovation"], 1.0),
                    Activity("Research Assistant", "internship", "Faculty research support", "10-20 hours/week",
                           ["research", "technical skills", "academic writing"], 0.9)
                ])
            
            elif career_field.lower() == 'business':
                activities.extend([
                    Activity("Business Club", "club", "Professional business development", "4-6 hours/week",
                           ["networking", "business knowledge", "leadership"], 1.0),
                    Activity("Case Competition Team", "competition", "Business case analysis", "8-12 hours/week",
                           ["analytical thinking", "presentation", "teamwork"], 0.9),
                    Activity("Internship Program", "internship", "Professional work experience", "20-40 hours/week",
                           ["professional experience", "networking", "industry knowledge"], 1.0)
                ])
        
        # General activities for all students
        activities.extend([
            Activity("Volunteer Work", "volunteer", "Community service", "2-4 hours/week",
                   ["empathy", "leadership", "community engagement"], 0.7),
            Activity("Study Groups", "academic", "Collaborative learning", "3-5 hours/week",
                   ["teamwork", "communication", "academic success"], 0.6)
        ])
        
        return activities
    
    def _identify_skills_gap(
        self, 
        level: StudentLevel, 
        career_field: str, 
        current_skills: List[str]
    ) -> List[str]:
        """Identify skills that need to be developed"""
        # Define required skills by career field
        career_skills = {
            'computer science': [
                'programming', 'data structures', 'algorithms', 'software design',
                'database management', 'web development', 'problem-solving',
                'mathematical reasoning', 'system analysis'
            ],
            'engineering': [
                'mathematical modeling', 'physics principles', 'problem-solving',
                'technical drawing', 'project management', 'analytical thinking',
                'CAD software', 'materials science', 'system design'
            ],
            'business': [
                'financial analysis', 'market research', 'project management',
                'presentation skills', 'negotiation', 'leadership',
                'data analysis', 'strategic thinking', 'communication'
            ],
            'medicine': [
                'anatomy', 'physiology', 'chemistry', 'biology',
                'patient care', 'medical terminology', 'research methods',
                'critical thinking', 'attention to detail'
            ],
            'art': [
                'creative design', 'color theory', 'composition',
                'digital tools', 'portfolio development', 'art history',
                'visual communication', 'creativity', 'aesthetic sense'
            ]
        }
        
        # Get required skills for the career field
        required_skills = career_skills.get(career_field.lower(), [])
        
        # Find skills gap
        skills_to_develop = [skill for skill in required_skills if skill not in current_skills]
        
        # Add level-appropriate foundational skills
        if level.value.endswith('_hs'):
            foundational_skills = [
                'time management', 'study skills', 'note-taking',
                'test-taking strategies', 'research skills'
            ]
        else:
            foundational_skills = [
                'professional communication', 'networking', 'interview skills',
                'resume writing', 'project management', 'critical thinking'
            ]
        
        skills_to_develop.extend([skill for skill in foundational_skills if skill not in current_skills])
        
        return list(set(skills_to_develop))  # Remove duplicates
    
    def _create_timeline(
        self, 
        level: StudentLevel, 
        milestones: List[Milestone], 
        courses: List[CourseRecommendation], 
        activities: List[Activity]
    ) -> Dict[str, List[str]]:
        """Create a month-by-month timeline"""
        timeline = {
            "September": [],
            "October": [],
            "November": [],
            "December": [],
            "January": [],
            "February": [],
            "March": [],
            "April": [],
            "May": [],
            "June": [],
            "July": [],
            "August": []
        }
        
        # Map milestones to timeline
        for milestone in milestones:
            if "Fall" in milestone.deadline or "September" in milestone.deadline:
                timeline["September"].append(f"Milestone: {milestone.title}")
            elif "October" in milestone.deadline:
                timeline["October"].append(f"Milestone: {milestone.title}")
            elif "Spring" in milestone.deadline or "March" in milestone.deadline:
                timeline["March"].append(f"Milestone: {milestone.title}")
            elif "May" in milestone.deadline:
                timeline["May"].append(f"Milestone: {milestone.title}")
            elif "January" in milestone.deadline:
                timeline["January"].append(f"Milestone: {milestone.title}")
            elif "February" in milestone.deadline:
                timeline["February"].append(f"Milestone: {milestone.title}")
        
        # Add course registration periods
        if level.value.endswith('_hs'):
            timeline["March"].append("Course Registration: Plan next year's courses")
        else:
            timeline["April"].append("Course Registration: Register for fall semester")
            timeline["November"].append("Course Registration: Register for spring semester")
        
        # Add activity-related timeline items
        timeline["August"].append("Activities: Research and prepare for new activities")
        timeline["September"].append("Activities: Join clubs and organizations")
        
        return timeline
    
    def get_pathway_summary(self, pathway: Pathway) -> Dict[str, any]:
        """Generate a summary of the pathway"""
        return {
            "student_level": pathway.student_level.value,
            "career_field": pathway.career_field,
            "total_milestones": len(pathway.milestones),
            "high_priority_milestones": len([m for m in pathway.milestones if m.priority == "high"]),
            "recommended_courses": len(pathway.courses),
            "ap_courses": len([c for c in pathway.courses if c.course_type == "AP"]),
            "activities": len(pathway.activities),
            "skills_to_develop": len(pathway.skills_to_develop),
            "next_milestone": self._get_next_milestone(pathway.milestones),
            "focus_areas": self._identify_focus_areas(pathway)
        }
    
    def _get_next_milestone(self, milestones: List[Milestone]) -> Optional[str]:
        """Get the next upcoming milestone"""
        high_priority = [m for m in milestones if m.priority == "high"]
        if high_priority:
            return high_priority[0].title
        elif milestones:
            return milestones[0].title
        return None
    
    def _identify_focus_areas(self, pathway: Pathway) -> List[str]:
        """Identify key focus areas for the student"""
        focus_areas = []
        
        # Academic focus
        if any(c.course_type == "AP" for c in pathway.courses):
            focus_areas.append("Advanced Academics")
        
        # Career preparation
        if any(a.type in ["internship", "competition"] for a in pathway.activities):
            focus_areas.append("Career Preparation")
        
        # Skill development
        if len(pathway.skills_to_develop) > 5:
            focus_areas.append("Skill Development")
        
        # College/application preparation
        if any(m.category == "application" for m in pathway.milestones):
            focus_areas.append("Application Preparation")
        
        return focus_areas
    
    def export_pathway_to_json(self, pathway: Pathway, filepath: str) -> bool:
        """Export pathway to JSON file"""
        try:
            pathway_dict = {
                "student_level": pathway.student_level.value,
                "career_field": pathway.career_field,
                "onet_code": pathway.onet_code,
                "milestones": [
                    {
                        "title": m.title,
                        "description": m.description,
                        "deadline": m.deadline,
                        "priority": m.priority,
                        "category": m.category
                    } for m in pathway.milestones
                ],
                "courses": [
                    {
                        "course_name": c.course_name,
                        "course_type": c.course_type,
                        "description": c.description,
                        "prerequisites": c.prerequisites,
                        "difficulty_level": c.difficulty_level,
                        "relevance_score": c.relevance_score
                    } for c in pathway.courses
                ],
                "activities": [
                    {
                        "name": a.name,
                        "type": a.type,
                        "description": a.description,
                        "time_commitment": a.time_commitment,
                        "skills_gained": a.skills_gained,
                        "career_relevance": a.career_relevance
                    } for a in pathway.activities
                ],
                "skills_to_develop": pathway.skills_to_develop,
                "timeline": pathway.timeline
            }
            
            with open(filepath, 'w') as f:
                json.dump(pathway_dict, f, indent=2)
            
            logger.info(f"Pathway exported to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting pathway: {e}")
            return False


# Example usage and testing functions
def create_sample_pathways():
    """Create sample pathways for testing"""
    system = StudentPathwaySystem()
    
    # High school computer science pathway
    hs_cs_pathway = system.generate_pathway(
        student_level=StudentLevel.JUNIOR_HS,
        career_field="computer science",
        interests=["programming", "mathematics", "problem-solving"],
        current_skills=["basic programming", "algebra"],
        gpa=3.7
    )
    
    # College engineering pathway
    college_eng_pathway = system.generate_pathway(
        student_level=StudentLevel.SOPHOMORE_COLLEGE,
        career_field="engineering",
        onet_code="17-2112.00",
        interests=["design", "mathematics", "technology"],
        current_skills=["calculus", "physics", "CAD basics"]
    )
    
    return hs_cs_pathway, college_eng_pathway


if __name__ == "__main__":
    # Test the system
    system = StudentPathwaySystem()
    
    # Create sample pathway
    pathway = system.generate_pathway(
        student_level=StudentLevel.JUNIOR_HS,
        career_field="computer science",
        interests=["programming", "games"],
        current_skills=["basic math", "some programming"]
    )
    
    # Print summary
    summary = system.get_pathway_summary(pathway)
    print("Pathway Summary:")
    print(json.dumps(summary, indent=2))
    
    print(f"\nNext milestone: {summary['next_milestone']}")
    print(f"Focus areas: {', '.join(summary['focus_areas'])}")