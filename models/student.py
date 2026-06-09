"""
Student pathway models.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class StudentLevel(str, Enum):
    """Student education levels."""

    FRESHMAN_HS = "freshman_hs"
    SOPHOMORE_HS = "sophomore_hs"
    JUNIOR_HS = "junior_hs"
    SENIOR_HS = "senior_hs"
    FRESHMAN_COLLEGE = "freshman_college"
    SOPHOMORE_COLLEGE = "sophomore_college"
    JUNIOR_COLLEGE = "junior_college"
    SENIOR_COLLEGE = "senior_college"
    GRADUATE = "graduate"
    PROFESSIONAL = "professional"


class PathwayMilestone(BaseModel):
    """Student pathway milestone."""

    title: str
    description: str
    deadline: str
    priority: str = Field(..., description="critical/high/medium/low")
    category: str = Field(
        ...,
        description="academic/extracurricular/test_prep/application/career_prep"
    )
    completed: bool = Field(default=False)


class CourseRecommendation(BaseModel):
    """Course recommendation for student."""

    course_name: str
    course_type: str = Field(..., description="ap/honors/regular/elective/dual_enrollment")
    description: str
    prerequisites: List[str] = Field(default_factory=list)
    difficulty_level: str = Field(default="intermediate")
    relevance_score: float = Field(default=0.5, ge=0, le=1)
    recommended_semester: Optional[str] = None


class ActivityRecommendation(BaseModel):
    """Extracurricular activity recommendation."""

    name: str
    type: str = Field(..., description="club/competition/volunteer/research/internship")
    description: str
    time_commitment: str
    skills_gained: List[str] = Field(default_factory=list)
    career_relevance: float = Field(default=0.5, ge=0, le=1)


class TestPrepRecommendation(BaseModel):
    """Standardized test prep recommendation."""

    test_name: str = Field(..., description="SAT/ACT/AP/GRE/etc")
    target_date: str
    recommended_score: Optional[str] = None
    prep_resources: List[str] = Field(default_factory=list)
    study_hours: Optional[int] = None


class StudentPathwayRequest(BaseModel):
    """Request to generate student pathway."""

    student_level: StudentLevel
    grade_year: Optional[str] = None
    interests: List[str] = Field(default_factory=list)
    current_skills: List[str] = Field(default_factory=list)
    career_goals: List[str] = Field(default_factory=list)
    gpa: Optional[float] = Field(None, ge=0, le=4.0)
    standardized_scores: Optional[Dict[str, int]] = None
    target_colleges: List[str] = Field(default_factory=list)
    budget_constraints: bool = Field(default=False)


class StudentPathway(BaseModel):
    """Complete student pathway."""

    student_level: StudentLevel
    career_field: str
    onet_code: Optional[str] = None

    # Recommendations
    milestones: List[PathwayMilestone]
    courses: List[CourseRecommendation]
    activities: List[ActivityRecommendation]
    test_prep: List[TestPrepRecommendation] = Field(default_factory=list)

    # Skills and timeline
    skills_to_develop: List[str]
    timeline: Dict[str, List[str]]

    # College guidance (if applicable)
    college_recommendations: List[str] = Field(default_factory=list)
    application_timeline: Optional[Dict[str, List[str]]] = None

    # Summary
    summary: str
    next_steps: List[str] = Field(default_factory=list)

    # AI insights
    ai_advice: Optional[str] = None
    personalized_tips: List[str] = Field(default_factory=list)

    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
