"""
Interview preparation endpoints.
"""

from fastapi import APIRouter, Depends

from api.dependencies.rate_limit import rate_limit_ai
from models.interview import InterviewPrepRequest, InterviewPrepResult
from services.interview_service import interview_service

router = APIRouter(prefix="/interview", tags=["Interview Prep"])


@router.post("/prepare", response_model=InterviewPrepResult)
async def generate_interview_prep(
    request: InterviewPrepRequest,
    _: None = Depends(rate_limit_ai),
):
    """
    Generate comprehensive interview preparation guide.

    Includes:
    - Behavioral questions (STAR method)
    - Technical questions (role-specific)
    - Situational questions
    - Questions to ask the interviewer
    - Preparation tips and strategies
    - AI-powered personalized advice
    """
    return await interview_service.generate_prep(request)
