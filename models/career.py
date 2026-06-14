"""
Career and roadmap models.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CareerLevel(str, Enum):
    """Career progression levels."""

    ENTRY = "entry"
    JUNIOR = "junior"
    MID_LEVEL = "mid_level"
    SENIOR = "senior"
    EXPERT = "expert"


class SalaryRange(BaseModel):
    """Salary range information."""

    min_salary: int = Field(..., ge=0, description="Minimum salary")
    max_salary: int = Field(..., ge=0, description="Maximum salary")
    currency: str = Field(default="USD")
    period: str = Field(default="year")


class CareerSummary(BaseModel):
    """Summary career information for listing."""

    id: str = Field(..., description="Career ID (SOC code)")
    title: str = Field(..., description="Career title")
    description: str = Field(..., description="Brief description")
    match_score: Optional[int] = Field(None, ge=0, le=100, description="Match percentage")
    salary: SalaryRange
    growth: str = Field(..., description="Employment outlook")
    education: str = Field(..., description="Required education level")
    cluster: str = Field(default="General", description="Career cluster")
    skills: List[str] = Field(default_factory=list, description="Top skills required")


class Career(BaseModel):
    """Full career details."""

    id: str = Field(..., description="Career ID (SOC code)")
    title: str = Field(..., description="Career title")
    description: str = Field(..., description="Full description")

    # Requirements
    education: str = Field(..., description="Required education")
    experience: str = Field(..., description="Required experience")
    salary: SalaryRange

    # Details
    skills: List[str] = Field(default_factory=list)
    knowledge: List[str] = Field(default_factory=list)
    abilities: List[str] = Field(default_factory=list)
    tasks: List[str] = Field(default_factory=list)

    # Outlook
    growth: str = Field(..., description="Employment outlook")
    growth_rate: str = Field(default="0%")

    # Related
    related_careers: List[str] = Field(default_factory=list)
    work_environment: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    work_styles: List[str] = Field(default_factory=list)
    cluster: str = Field(default="General")


class CareerSearchQuery(BaseModel):
    """Career search request."""

    query: str = Field(..., min_length=1, description="Search query")
    filters: Dict[str, Any] = Field(default_factory=dict)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class CareerSearchResult(BaseModel):
    """Career search response."""

    results: List[CareerSummary]
    total: int
    page: int
    page_size: int
    query: str


# Roadmap Models

class Milestone(BaseModel):
    """Career milestone."""

    id: str
    title: str
    description: str
    target_date: str = Field(..., description="Relative date like 'Year 2'")
    priority: str = Field(..., description="critical/high/medium/low")
    category: str = Field(..., description="education/certification/project/skill/experience")
    prerequisites: List[str] = Field(default_factory=list)
    skills_gained: List[str] = Field(default_factory=list)
    estimated_hours: int = Field(default=0, ge=0)
    completion_criteria: List[str] = Field(default_factory=list)
    resources: List[str] = Field(default_factory=list)
    career_impact: float = Field(default=0.5, ge=0, le=1)
    completed: bool = Field(default=False)


class Certification(BaseModel):
    """Industry certification."""

    name: str
    provider: str
    description: str
    difficulty: str = Field(..., description="beginner/intermediate/advanced/expert")
    time_to_complete: str
    cost_range: str
    prerequisites: List[str] = Field(default_factory=list)
    career_relevance: float = Field(default=0.5, ge=0, le=1)
    renewal_period: Optional[str] = None


class Project(BaseModel):
    """Career-building project."""

    id: str
    name: str
    description: str
    type: str = Field(..., description="portfolio/open_source/research/business/academic")
    difficulty: str
    estimated_duration: str
    skills_practiced: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    deliverables: List[str] = Field(default_factory=list)
    career_impact: float = Field(default=0.5, ge=0, le=1)
    portfolio_value: float = Field(default=0.5, ge=0, le=1)


class SalaryProgression(BaseModel):
    """Salary progression by level."""

    level: CareerLevel
    years_experience: str
    min_salary: int
    max_salary: int
    median_salary: int
    location_factor: float = Field(default=1.0)
    currency: str = Field(default="USD")


class AlternativePath(BaseModel):
    """Alternative career path."""

    path_name: str
    description: str
    transition_requirements: List[str]
    additional_skills: List[str]
    time_to_transition: str
    salary_impact: float = Field(description="Percentage change")
    market_demand: str
    reasons_to_consider: List[str]


class TimelinePhase(BaseModel):
    """Roadmap timeline phase."""

    phase_name: str
    years: str
    focus: str
    milestones: List[str]


class RoadmapTimeline(BaseModel):
    """Timeline visualization data."""

    timeline_type: str = Field(default="milestone")
    total_duration: str
    phases: List[TimelinePhase]
    milestones_by_year: Dict[int, List[str]]
    decision_points: List[Dict[str, Any]]


class CareerRoadmapRequest(BaseModel):
    """Request to generate career roadmap."""

    career_field: str = Field(..., description="Target career field")
    student_level: Optional[str] = Field(None, description="Current student level")
    current_skills: List[str] = Field(default_factory=list)
    target_role: Optional[str] = Field(None)
    roadmap_years: int = Field(default=5, ge=1, le=10)
    location: str = Field(default="US_National")
    specializations: List[str] = Field(default_factory=list)
    budget_constraints: bool = Field(default=False)
    fast_track: bool = Field(default=False)


class CareerRoadmap(BaseModel):
    """Complete career roadmap."""

    career_field: str
    onet_code: Optional[str] = None
    student_level: Optional[str] = None
    current_skills: List[str]
    target_role: str
    roadmap_duration: str

    # Core components
    milestones: List[Milestone]
    certifications: List[Certification]
    projects: List[Project]
    salary_progression: List[SalaryProgression]
    skill_progression: Dict[str, List[str]]

    # Alternative paths
    alternative_paths: List[AlternativePath]
    pivot_opportunities: List[str]

    # Timeline
    timeline: RoadmapTimeline

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    confidence_score: float = Field(ge=0, le=1)

    # Summary
    summary: Optional[Dict[str, Any]] = None
    ai_insights: Optional[str] = None
