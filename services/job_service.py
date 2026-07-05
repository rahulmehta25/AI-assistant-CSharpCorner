"""
Job Service - Job search, matching, and recommendations.
"""

import sys
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cache import cache, CacheNamespace
from core.config import settings
from core.logging import get_logger
from models.job import (
    JobMatchRequest,
    JobMatchResponse,
    JobMatchResult,
    JobMatchScore,
    JobPosting,
    JobSearchQuery,
    JobSearchResult,
)

logger = get_logger(__name__)

# Import existing modules
try:
    from modules.live_job_scraper import LiveJobScraper
    from modules.job_matcher import JobMatcher, UserProfile as JobUserProfile
    JOB_MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Job modules not available: {e}")
    JOB_MODULES_AVAILABLE = False


class JobService:
    """
    Service for job search and matching.
    Integrates with existing scraper and matcher modules.
    """

    def __init__(self):
        self._scraper: Optional[LiveJobScraper] = None
        self._matcher: Optional[JobMatcher] = None
        self._initialized = False

    def _ensure_initialized(self):
        """Lazy initialization."""
        if self._initialized:
            return

        if not JOB_MODULES_AVAILABLE:
            logger.warning("Running without job modules")
            self._initialized = True
            return

        try:
            self._scraper = LiveJobScraper()
            self._matcher = JobMatcher()
            self._initialized = True
            logger.info("Job service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize job modules: {e}")
            self._initialized = True

    def _format_job_posting(self, job_data: Dict) -> JobPosting:
        """Format raw job data into JobPosting model."""
        salary_info = job_data.get('salary_info', {})

        return JobPosting(
            id=job_data.get('id', str(hash(f"{job_data.get('title')}:{job_data.get('company')}"))),
            title=job_data.get('title', ''),
            company=job_data.get('company', ''),
            location=job_data.get('location', ''),
            description=job_data.get('description', ''),
            salary_min=salary_info.get('min_salary'),
            salary_max=salary_info.get('max_salary'),
            salary_period=salary_info.get('period', 'year'),
            experience_level=job_data.get('experience_level', 'Mid-Level'),
            employment_type=job_data.get('employment_type', 'full-time'),
            remote='remote' in job_data.get('location', '').lower() or job_data.get('remote', False),
            skills_required=job_data.get('skills_required', []),
            posted_date=job_data.get('posted_date'),
            url=job_data.get('url'),
            source=job_data.get('source', 'unknown'),
        )

    async def search_jobs(
        self,
        query: JobSearchQuery,
    ) -> JobSearchResult:
        """
        Search for jobs across multiple sources.
        """
        self._ensure_initialized()

        # Build cache key
        cache_key = f"{query.query}:{query.location}:{query.experience_level}:{query.remote_only}"

        # Check cache (short TTL for job searches)
        cached_results = await cache.get(CacheNamespace.JOB_SEARCH, cache_key)
        if cached_results:
            logger.info(f"Returning cached job search results")
            return JobSearchResult(**cached_results)

        if not self._scraper:
            return JobSearchResult(
                jobs=[],
                total=0,
                query=query.query,
                location=query.location,
                sources_used=[],
            )

        try:
            # Search using existing scraper
            results = await self._scraper.search_jobs(
                query=query.query,
                location=query.location,
                sources=query.sources,
            )

            jobs_data = results.get('combined', [])

            # Apply filters
            if query.remote_only:
                jobs_data = [j for j in jobs_data if 'remote' in j.get('location', '').lower()]

            if query.experience_level:
                level = query.experience_level.lower()
                jobs_data = [
                    j for j in jobs_data
                    if level in j.get('experience_level', '').lower()
                ]

            if query.min_salary:
                jobs_data = [
                    j for j in jobs_data
                    if j.get('salary_info', {}).get('min_salary', 0) >= query.min_salary
                ]

            # Limit results
            jobs_data = jobs_data[:query.max_results]

            # Format results
            jobs = [self._format_job_posting(j) for j in jobs_data]

            result = JobSearchResult(
                jobs=jobs,
                total=len(jobs),
                query=query.query,
                location=query.location,
                sources_used=results.get('search_metadata', {}).get('sources_used', []),
                search_metadata=results.get('search_metadata', {}),
            )

            # Cache results (30 min TTL)
            await cache.set(
                CacheNamespace.JOB_SEARCH,
                cache_key,
                result.model_dump(mode="json"),
                ttl=1800,
            )

            return result

        except Exception as e:
            logger.error(f"Job search failed: {e}")
            return JobSearchResult(
                jobs=[],
                total=0,
                query=query.query,
                location=query.location,
                sources_used=[],
            )

    async def match_jobs(
        self,
        request: JobMatchRequest,
        jobs: Optional[List[JobPosting]] = None,
    ) -> JobMatchResponse:
        """
        Match jobs to user profile.
        """
        self._ensure_initialized()

        if not self._matcher:
            return JobMatchResponse(
                matches=[],
                total_analyzed=0,
                excellent_matches=0,
                good_matches=0,
            )

        try:
            # Create user profile for matcher
            user_profile = JobUserProfile(
                user_id="temp",
                skills=request.user_skills,
                experience_level=request.experience_level,
                experience_years=request.experience_years,
                preferred_locations=request.preferred_locations,
                salary_expectations=request.salary_expectations or {},
                job_titles=request.job_titles,
                industries=[],
                work_preferences=request.work_preferences,
                education_level="",
                certifications=[],
                languages=[],
                career_goals=[],
            )

            # If no jobs provided, search for them
            if not jobs:
                search_query = JobSearchQuery(
                    query=request.job_titles[0] if request.job_titles else "software engineer",
                    location=request.preferred_locations[0] if request.preferred_locations else "",
                    max_results=50,
                )
                search_result = await self.search_jobs(search_query)
                jobs = search_result.jobs

            # Convert to dict format for matcher
            jobs_dicts = [j.model_dump() for j in jobs]

            # Rank jobs
            ranked_jobs = self._matcher.rank_jobs_for_user(jobs_dicts, user_profile)

            # Generate report
            report = self._matcher.generate_match_report(ranked_jobs, user_profile)

            # Convert to response format
            matches = []
            for i, job_data in enumerate(ranked_jobs):
                match_score_data = job_data.get('match_score', {})
                matches.append(JobMatchResult(
                    job=self._format_job_posting(job_data),
                    match_score=JobMatchScore(
                        overall_score=match_score_data.get('overall_score', 0),
                        skill_score=match_score_data.get('skill_score', 0),
                        experience_score=match_score_data.get('experience_score', 0),
                        location_score=match_score_data.get('location_score', 0),
                        salary_score=match_score_data.get('salary_score', 0),
                        title_score=match_score_data.get('title_score', 0),
                        industry_score=match_score_data.get('industry_score', 0),
                        work_preference_score=match_score_data.get('work_preference_score', 0),
                        match_reasons=match_score_data.get('match_reasons', []),
                        concerns=match_score_data.get('concerns', []),
                        missing_skills=[],
                    ),
                    rank=i + 1,
                ))

            return JobMatchResponse(
                matches=matches,
                total_analyzed=report.get('total_jobs', 0),
                excellent_matches=report.get('match_distribution', {}).get('excellent', 0),
                good_matches=report.get('match_distribution', {}).get('good', 0),
                skill_gaps=report.get('skill_gaps', []),
                recommendations=report.get('recommendations', []),
            )

        except Exception as e:
            logger.error(f"Job matching failed: {e}")
            return JobMatchResponse(
                matches=[],
                total_analyzed=0,
                excellent_matches=0,
                good_matches=0,
            )


# Global instance
job_service = JobService()
