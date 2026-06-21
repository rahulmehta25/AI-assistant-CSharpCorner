"""
Career endpoints - Career data, roadmaps, and skill gap analysis.
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query

from api.dependencies.auth import get_current_user_optional
from api.dependencies.rate_limit import rate_limit_dependency, rate_limit_ai
from models.auth import CurrentUser
from models.career import (
    Career,
    CareerRoadmap,
    CareerRoadmapRequest,
    CareerSearchQuery,
    CareerSearchResult,
)
from models.skills import SkillGapAnalysis, SkillGapRequest
from services.career_service import career_service

router = APIRouter(prefix="/careers", tags=["Careers"])


@router.get("", response_model=CareerSearchResult)
async def list_careers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    _: None = Depends(rate_limit_dependency),
):
    """
    Get all available careers with pagination.
    """
    return await career_service.get_all_careers(page=page, page_size=page_size)


@router.get("/{career_id}", response_model=Career)
async def get_career(
    career_id: str,
    _: None = Depends(rate_limit_dependency),
):
    """
    Get detailed information about a specific career.
    """
    return await career_service.get_career(career_id)


@router.post("/search", response_model=CareerSearchResult)
async def search_careers(
    query: CareerSearchQuery,
    _: None = Depends(rate_limit_dependency),
):
    """
    Search for careers based on keywords, skills, or interests.
    """
    return await career_service.search_careers(
        query=query.query,
        page=query.page,
        page_size=query.page_size,
    )


@router.post("/roadmap", response_model=CareerRoadmap)
async def generate_roadmap(
    request: CareerRoadmapRequest,
    user: Optional[CurrentUser] = Depends(get_current_user_optional),
    _: None = Depends(rate_limit_ai),
):
    """
    Generate a personalized career roadmap.

    This is an AI-powered endpoint with stricter rate limits.
    Includes:
    - Milestones and timeline
    - Certifications to pursue
    - Projects to build
    - Salary progression estimates
    - Alternative career paths
    """
    user_id = user.user_id if user else None
    return await career_service.generate_roadmap(request, user_id)


@router.post("/skill-gap", response_model=SkillGapAnalysis)
async def analyze_skill_gap(
    request: SkillGapRequest,
    _: None = Depends(rate_limit_ai),
):
    """
    Analyze skill gaps between current skills and target career.

    Returns:
    - Skills coverage percentage
    - Prioritized list of skills to develop
    - Learning plan with time estimates
    - AI-powered recommendations
    """
    return await career_service.analyze_skill_gap(request)
