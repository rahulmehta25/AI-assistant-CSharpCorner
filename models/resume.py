"""
Resume and cover letter models.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ResumeSuggestion(BaseModel):
    """Resume improvement suggestion."""

    type: str = Field(..., description="keywords/action_verbs/quantification/technologies/format")
    priority: str = Field(..., description="high/medium/low")
    message: str
    examples: List[str] = Field(default_factory=list)


class ResumeAnalysisRequest(BaseModel):
    """Request to analyze resume."""

    resume_text: str = Field(..., min_length=50, description="Resume content as text")
    job_description: Optional[str] = Field(None, description="Target job description")
    target_role: Optional[str] = Field(None, description="Target role")


class ResumeKeywordAnalysis(BaseModel):
    """Resume keyword analysis."""

    found_keywords: List[str]
    missing_keywords: List[str]
    keyword_density: float
    ats_compatibility: float = Field(..., ge=0, le=100)


class ResumeAnalysisResult(BaseModel):
    """Resume analysis response."""

    ats_score: float = Field(..., ge=0, le=100, description="ATS compatibility score")
    overall_score: float = Field(..., ge=0, le=100)

    # Analysis
    suggestions: List[ResumeSuggestion]
    keyword_analysis: ResumeKeywordAnalysis
    missing_technologies: List[str]

    # Structure
    recommended_sections: List[str]
    section_feedback: Dict[str, str] = Field(default_factory=dict)

    # AI insights
    ai_summary: Optional[str] = None
    ai_improvements: List[str] = Field(default_factory=list)

    # Metadata
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
    cached: bool = Field(default=False)


class CoverLetterRequest(BaseModel):
    """Request to generate cover letter."""

    # User info
    name: str = Field(..., min_length=1)
    current_position: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience_years: Optional[int] = None
    key_achievement: Optional[str] = None

    # Target info
    target_position: str = Field(..., min_length=1)
    company_name: str = Field(..., min_length=1)
    company_reason: Optional[str] = Field(None, description="Why interested in company")

    # Options
    template_type: str = Field(
        default="standard",
        description="standard/career_change/entry_level"
    )
    tone: str = Field(default="professional", description="professional/enthusiastic/formal")
    include_salary: bool = Field(default=False)

    # AI options
    use_ai: bool = Field(default=True, description="Use AI to enhance the letter")


class CoverLetterResult(BaseModel):
    """Generated cover letter response."""

    cover_letter: str = Field(..., description="Generated cover letter content")
    template_used: str
    ai_generated: bool = Field(default=False)

    # Suggestions
    customization_tips: List[str] = Field(default_factory=list)

    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    word_count: int = Field(default=0)


class ResumeGenerationRequest(BaseModel):
    """Request to generate resume suggestions."""

    profile: Dict[str, Any] = Field(..., description="User profile data")
    target_career: str = Field(..., description="Target career/role")
    format: str = Field(default="standard", description="standard/technical/executive")


class ResumeGenerationResult(BaseModel):
    """Resume generation response."""

    summary_suggestion: str
    skills_to_highlight: List[str]
    experience_bullets: List[str]
    keywords_to_include: List[str]
    format_recommendations: List[str]
    ai_generated: bool = Field(default=False)
