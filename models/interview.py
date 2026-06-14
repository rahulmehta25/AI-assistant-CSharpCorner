"""
Interview preparation models.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class InterviewQuestion(BaseModel):
    """Interview question with tips."""

    question: str
    category: str = Field(..., description="behavioral/technical/situational")
    difficulty: str = Field(default="medium", description="easy/medium/hard")
    tips: List[str] = Field(default_factory=list)
    sample_answer: Optional[str] = None
    follow_ups: List[str] = Field(default_factory=list)


class InterviewPrepRequest(BaseModel):
    """Request for interview preparation."""

    job_title: str = Field(..., min_length=1)
    job_description: Optional[str] = None
    company_name: Optional[str] = None
    experience_level: str = Field(default="mid", description="junior/mid/senior")
    user_skills: List[str] = Field(default_factory=list)
    include_technical: bool = Field(default=True)
    include_behavioral: bool = Field(default=True)
    include_situational: bool = Field(default=True)
    num_questions: int = Field(default=15, ge=5, le=50)


class CompanyResearch(BaseModel):
    """Company research information."""

    company_name: str
    industry: Optional[str] = None
    size: Optional[str] = None
    culture_notes: List[str] = Field(default_factory=list)
    recent_news: List[str] = Field(default_factory=list)
    interview_tips: List[str] = Field(default_factory=list)


class InterviewPrepResult(BaseModel):
    """Complete interview preparation guide."""

    job_title: str
    company_name: Optional[str] = None
    experience_level: str

    # Questions by category
    behavioral_questions: List[InterviewQuestion]
    technical_questions: List[InterviewQuestion]
    situational_questions: List[InterviewQuestion]
    questions_to_ask: List[str]

    # Preparation tips
    preparation_tips: List[str] = Field(default_factory=list)
    common_mistakes: List[str] = Field(default_factory=list)
    success_strategies: List[str] = Field(default_factory=list)

    # Company research
    company_research: Optional[CompanyResearch] = None

    # AI insights
    ai_insights: Optional[str] = None
    personalized_tips: List[str] = Field(default_factory=list)

    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class MockInterviewRequest(BaseModel):
    """Request for mock interview session."""

    job_title: str
    question_types: List[str] = Field(
        default=["behavioral", "technical"],
        description="Types of questions to include"
    )
    difficulty: str = Field(default="medium")
    num_questions: int = Field(default=5, ge=1, le=10)


class MockInterviewResponse(BaseModel):
    """Mock interview response."""

    session_id: str
    question: InterviewQuestion
    question_number: int
    total_questions: int


class AnswerFeedback(BaseModel):
    """Feedback on interview answer."""

    score: float = Field(..., ge=0, le=10)
    strengths: List[str]
    improvements: List[str]
    sample_better_answer: Optional[str] = None
    follow_up_question: Optional[str] = None
