"""
Resume analysis and cover letter generation endpoints.
"""

from fastapi import APIRouter, Depends

from api.dependencies.rate_limit import rate_limit_ai
from models.resume import (
    CoverLetterRequest,
    CoverLetterResult,
    ResumeAnalysisRequest,
    ResumeAnalysisResult,
)
from services.resume_service import resume_service

router = APIRouter(prefix="/resume", tags=["Resume & Cover Letter"])


@router.post("/analyze", response_model=ResumeAnalysisResult)
async def analyze_resume(
    request: ResumeAnalysisRequest,
    _: None = Depends(rate_limit_ai),
):
    """
    Analyze a resume for ATS compatibility and improvements.

    Provides:
    - ATS compatibility score
    - Keyword analysis
    - Missing technologies/skills
    - Specific improvement suggestions
    - AI-powered insights
    """
    return await resume_service.analyze_resume(request)


@router.post("/cover-letter", response_model=CoverLetterResult)
async def generate_cover_letter(
    request: CoverLetterRequest,
    _: None = Depends(rate_limit_ai),
):
    """
    Generate a personalized cover letter.

    Supports multiple template types:
    - standard: Traditional professional format
    - career_change: For career transitions
    - entry_level: For new graduates

    Can use AI for enhanced, personalized content.
    """
    return await resume_service.generate_cover_letter(request)
