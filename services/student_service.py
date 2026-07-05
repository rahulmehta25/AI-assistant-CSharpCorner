"""
Student Service - Student pathways and education planning.
"""

import sys
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.logging import get_logger
from models.student import (
    StudentLevel,
    StudentPathway,
    StudentPathwayRequest,
    PathwayMilestone,
    CourseRecommendation,
    ActivityRecommendation,
)

from .ai_service import ai_service

logger = get_logger(__name__)

# Import existing modules
try:
    from modules.student_pathways import StudentPathwaySystem, StudentLevel as ModuleStudentLevel
    STUDENT_MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Student modules not available: {e}")
    STUDENT_MODULES_AVAILABLE = False


class StudentService:
    """
    Service for student career pathway planning.
    """

    def __init__(self):
        self._pathway_system: Optional[StudentPathwaySystem] = None
        self._initialized = False

    def _ensure_initialized(self):
        """Lazy initialization."""
        if self._initialized:
            return

        if STUDENT_MODULES_AVAILABLE:
            try:
                self._pathway_system = StudentPathwaySystem()
                logger.info("Student service initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize StudentPathwaySystem: {e}")

        self._initialized = True

    def _convert_student_level(self, level: StudentLevel) -> Optional[Any]:
        """Convert API StudentLevel to module StudentLevel."""
        if not STUDENT_MODULES_AVAILABLE:
            return None

        level_map = {
            StudentLevel.FRESHMAN_HS: ModuleStudentLevel.FRESHMAN_HS,
            StudentLevel.SOPHOMORE_HS: ModuleStudentLevel.SOPHOMORE_HS,
            StudentLevel.JUNIOR_HS: ModuleStudentLevel.JUNIOR_HS,
            StudentLevel.SENIOR_HS: ModuleStudentLevel.SENIOR_HS,
            StudentLevel.FRESHMAN_COLLEGE: ModuleStudentLevel.FRESHMAN_COLLEGE,
            StudentLevel.SOPHOMORE_COLLEGE: ModuleStudentLevel.SOPHOMORE_COLLEGE,
            StudentLevel.JUNIOR_COLLEGE: ModuleStudentLevel.JUNIOR_COLLEGE,
            StudentLevel.SENIOR_COLLEGE: ModuleStudentLevel.SENIOR_COLLEGE,
        }

        return level_map.get(level)

    async def generate_pathway(
        self,
        request: StudentPathwayRequest,
    ) -> StudentPathway:
        """
        Generate a comprehensive student pathway.
        """
        self._ensure_initialized()

        milestones = []
        courses = []
        activities = []
        skills_to_develop = []
        timeline = {}
        summary = ""

        career_field = request.career_goals[0] if request.career_goals else "computer science"
        onet_code = None

        # Use existing module if available
        if self._pathway_system:
            try:
                module_level = self._convert_student_level(request.student_level)
                if module_level:
                    pathway_data = self._pathway_system.generate_pathway(
                        student_level=module_level,
                        career_field=career_field,
                        interests=request.interests,
                        current_skills=request.current_skills,
                        gpa=request.gpa,
                        standardized_scores=request.standardized_scores,
                    )

                    # Convert milestones
                    for m in pathway_data.milestones:
                        milestones.append(PathwayMilestone(
                            title=m.title,
                            description=m.description,
                            deadline=m.deadline,
                            priority=m.priority,
                            category=m.category,
                        ))

                    # Convert courses
                    for c in pathway_data.courses:
                        courses.append(CourseRecommendation(
                            course_name=c.course_name,
                            course_type=c.course_type,
                            description=c.description,
                            prerequisites=c.prerequisites,
                            difficulty_level=c.difficulty_level,
                            relevance_score=c.relevance_score,
                        ))

                    # Convert activities
                    for a in pathway_data.activities:
                        activities.append(ActivityRecommendation(
                            name=a.name,
                            type=a.type,
                            description=a.description,
                            time_commitment=a.time_commitment,
                            skills_gained=a.skills_gained,
                            career_relevance=a.career_relevance,
                        ))

                    skills_to_develop = pathway_data.skills_to_develop
                    timeline = pathway_data.timeline
                    onet_code = pathway_data.onet_code
                    summary = self._pathway_system.get_pathway_summary(pathway_data)

            except Exception as e:
                logger.warning(f"Module pathway generation failed: {e}")

        # Enhance with AI if needed
        ai_advice = None
        personalized_tips = []

        try:
            prompt = ai_service.create_prompt(
                system_message="You are an academic and career advisor for students. Provide encouraging, specific guidance.",
                human_template="""Student Level: {student_level}
Career Goal: {career_field}
Interests: {interests}
Current Skills: {skills}
GPA: {gpa}

Provide 3-4 specific, actionable pieces of advice for this student.""",
            )

            ai_advice = await ai_service.invoke(prompt, {
                "student_level": request.student_level.value,
                "career_field": career_field,
                "interests": ", ".join(request.interests) if request.interests else "various",
                "skills": ", ".join(request.current_skills) if request.current_skills else "developing",
                "gpa": str(request.gpa) if request.gpa else "not specified",
            })

            # Parse tips
            for line in ai_advice.split('\n'):
                line = line.strip()
                if line.startswith(('-', '*', '1', '2', '3', '4')):
                    personalized_tips.append(line.lstrip('-*0123456789. '))

        except Exception as e:
            logger.warning(f"AI advice failed: {e}")

        # Generate summary if not provided
        if not summary:
            summary = f"Personalized pathway for a {request.student_level.value.replace('_', ' ')} "
            summary += f"interested in {career_field}. "
            if milestones:
                summary += f"Includes {len(milestones)} key milestones, "
            if courses:
                summary += f"{len(courses)} recommended courses, "
            if activities:
                summary += f"and {len(activities)} activities."

        # Generate next steps
        next_steps = []
        if milestones:
            critical_milestones = [m for m in milestones if m.priority == "critical"]
            if critical_milestones:
                next_steps.append(f"Focus on: {critical_milestones[0].title}")
        if courses:
            next_steps.append(f"Consider enrolling in: {courses[0].course_name}")
        if activities:
            next_steps.append(f"Explore: {activities[0].name}")
        if not next_steps:
            next_steps = [
                "Research your target career field",
                "Connect with mentors or professionals",
                "Start building relevant skills",
            ]

        return StudentPathway(
            student_level=request.student_level,
            career_field=career_field,
            onet_code=onet_code,
            milestones=milestones,
            courses=courses,
            activities=activities,
            test_prep=[],
            skills_to_develop=skills_to_develop or ["Communication", "Problem Solving", "Technical Skills"],
            timeline=timeline or {"Year 1": ["Explore interests", "Build foundation"]},
            college_recommendations=request.target_colleges,
            summary=summary,
            next_steps=next_steps[:5],
            ai_advice=ai_advice,
            personalized_tips=personalized_tips[:5],
        )


# Global instance
student_service = StudentService()
