"""
Skills assessment and gap analysis models.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SkillLevel(str, Enum):
    """Skill proficiency levels."""

    BEGINNER = "beginner"
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class Skill(BaseModel):
    """Individual skill with proficiency."""

    name: str = Field(..., description="Skill name")
    level: SkillLevel = Field(default=SkillLevel.BEGINNER)
    years_experience: Optional[float] = None
    last_used: Optional[str] = None
    certified: bool = Field(default=False)


class SkillGapRequest(BaseModel):
    """Request for skill gap analysis."""

    current_skills: List[str] = Field(..., min_length=1)
    skill_levels: Optional[Dict[str, int]] = Field(
        None,
        description="Skill name to proficiency level (1-5)"
    )
    target_career: str = Field(..., description="Target career or role")
    target_skills: Optional[List[str]] = Field(None, description="Specific target skills")


class SkillGap(BaseModel):
    """Individual skill gap."""

    skill: str
    current_level: Optional[int] = Field(None, ge=0, le=5)
    required_level: int = Field(..., ge=1, le=5)
    gap: int = Field(..., description="Level difference")
    priority: str = Field(..., description="critical/high/medium/low")
    demand_score: float = Field(..., ge=0, le=1, description="Market demand")


class LearningResource(BaseModel):
    """Learning resource recommendation."""

    name: str
    type: str = Field(..., description="course/book/tutorial/certification/project")
    provider: Optional[str] = None
    url: Optional[str] = None
    duration: Optional[str] = None
    cost: Optional[str] = None
    skill_covered: str


class LearningPlan(BaseModel):
    """Learning plan item."""

    order: int
    skill: str
    time_estimate: str
    practice_project: str
    resources: List[LearningResource] = Field(default_factory=list)


class SkillGapAnalysis(BaseModel):
    """Complete skill gap analysis result."""

    # Coverage
    skill_coverage: float = Field(..., ge=0, le=100, description="Percentage of required skills covered")
    total_required_skills: int
    skills_met: int
    skills_partial: int
    skills_missing: int

    # Gaps
    skill_gaps: List[SkillGap]
    prioritized_skills: List[Dict[str, Any]]

    # Learning plan
    learning_plan: List[LearningPlan]
    estimated_total_time: str

    # AI insights
    ai_analysis: Optional[str] = None
    recommendations: List[str] = Field(default_factory=list)

    # Metadata
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    target_career: str


class SkillAssessment(BaseModel):
    """User skill self-assessment."""

    skills: List[Skill]
    assessment_date: datetime = Field(default_factory=datetime.utcnow)

    # Computed
    total_skills: int = Field(default=0)
    average_level: float = Field(default=0)
    strongest_skills: List[str] = Field(default_factory=list)
    growth_areas: List[str] = Field(default_factory=list)


class SkillRecommendation(BaseModel):
    """Skill learning recommendation."""

    skill: str
    reason: str
    priority: str
    estimated_time: str
    career_impact: str
    resources: List[LearningResource] = Field(default_factory=list)
    related_jobs: List[str] = Field(default_factory=list)
