"""
Job search and matching models.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class JobPosting(BaseModel):
    """Job posting information."""

    id: str = Field(..., description="Job posting ID")
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location")
    description: str = Field(..., description="Job description")

    # Compensation
    salary_min: Optional[int] = Field(None, description="Minimum salary")
    salary_max: Optional[int] = Field(None, description="Maximum salary")
    salary_period: str = Field(default="year")

    # Details
    experience_level: str = Field(default="Mid-Level")
    employment_type: str = Field(default="full-time", description="full-time/part-time/contract")
    remote: bool = Field(default=False)
    skills_required: List[str] = Field(default_factory=list)

    # Metadata
    posted_date: Optional[datetime] = None
    url: Optional[str] = None
    source: str = Field(default="unknown")

    # Match info (populated after matching)
    match_score: Optional[float] = Field(None, ge=0, le=1)


class JobSearchQuery(BaseModel):
    """Job search request."""

    query: str = Field(..., min_length=1, description="Search query (job title, keywords)")
    location: str = Field(default="", description="Location filter")
    experience_level: Optional[str] = Field(None, description="junior/mid/senior")
    remote_only: bool = Field(default=False)
    min_salary: Optional[int] = Field(None, ge=0)
    max_results: int = Field(default=50, ge=1, le=200)
    sources: List[str] = Field(
        default=["indeed", "linkedin"],
        description="Job sources to search"
    )
    page: int = Field(default=1, ge=1)


class JobSearchResult(BaseModel):
    """Job search response."""

    jobs: List[JobPosting]
    total: int
    query: str
    location: str
    sources_used: List[str]
    search_metadata: Dict[str, Any] = Field(default_factory=dict)


class JobMatchScore(BaseModel):
    """Detailed job match score breakdown."""

    overall_score: float = Field(..., ge=0, le=1)
    skill_score: float = Field(..., ge=0, le=1)
    experience_score: float = Field(..., ge=0, le=1)
    location_score: float = Field(..., ge=0, le=1)
    salary_score: float = Field(..., ge=0, le=1)
    title_score: float = Field(..., ge=0, le=1)
    industry_score: float = Field(..., ge=0, le=1)
    work_preference_score: float = Field(..., ge=0, le=1)

    match_reasons: List[str] = Field(default_factory=list)
    concerns: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)


class JobMatchRequest(BaseModel):
    """Request to match jobs to user profile."""

    user_skills: List[str] = Field(..., min_length=1)
    experience_years: int = Field(..., ge=0)
    experience_level: str = Field(default="mid")
    preferred_locations: List[str] = Field(default_factory=list)
    salary_expectations: Optional[Dict[str, Any]] = None
    job_titles: List[str] = Field(default_factory=list)
    work_preferences: Dict[str, bool] = Field(
        default={"remote": True, "hybrid": True, "onsite": True}
    )


class JobMatchResult(BaseModel):
    """Job with match score."""

    job: JobPosting
    match_score: JobMatchScore
    rank: int


class JobMatchResponse(BaseModel):
    """Response with matched jobs."""

    matches: List[JobMatchResult]
    total_analyzed: int
    excellent_matches: int = Field(description="Score >= 0.8")
    good_matches: int = Field(description="Score >= 0.6")
    skill_gaps: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
