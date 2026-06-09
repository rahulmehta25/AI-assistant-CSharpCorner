"""
Job search and matching endpoints.
"""

from fastapi import APIRouter, Depends

from api.dependencies.rate_limit import rate_limit_dependency
from models.job import (
    JobMatchRequest,
    JobMatchResponse,
    JobSearchQuery,
    JobSearchResult,
)
from services.job_service import job_service

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/search", response_model=JobSearchResult)
async def search_jobs(
    query: JobSearchQuery,
    _: None = Depends(rate_limit_dependency),
):
    """
    Search for job postings across multiple sources.

    Supports:
    - Keyword search
    - Location filtering
    - Experience level filtering
    - Remote-only filter
    - Multiple job sources
    """
    return await job_service.search_jobs(query)


@router.post("/match", response_model=JobMatchResponse)
async def match_jobs(
    request: JobMatchRequest,
    _: None = Depends(rate_limit_dependency),
):
    """
    Match jobs to a user profile.

    Analyzes jobs against user skills, experience, location preferences,
    and salary expectations to provide ranked matches with detailed scores.

    Returns:
    - Ranked job matches with scores
    - Match breakdown by category
    - Skill gaps identified
    - Recommendations
    """
    return await job_service.match_jobs(request)
