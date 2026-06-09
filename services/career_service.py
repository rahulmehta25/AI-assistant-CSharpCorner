"""
Career Service - Career data, roadmaps, and skill gap analysis.
"""

import sys
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

# Add modules to path for existing module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cache import cache, cached, CacheNamespace
from core.config import settings
from core.exceptions import NotFoundError
from core.logging import get_logger
from models.career import (
    Career,
    CareerRoadmap,
    CareerRoadmapRequest,
    CareerSearchResult,
    CareerSummary,
    SalaryRange,
)
from models.skills import SkillGapAnalysis, SkillGapRequest

from .ai_service import ai_service

logger = get_logger(__name__)

# Import existing modules
try:
    from modules.data_loader import data_loader
    from modules.roadmap_generator import RoadmapGenerator
    from modules.recommendation_engine import RecommendationEngine
    DATA_MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Career modules not available: {e}")
    DATA_MODULES_AVAILABLE = False


class CareerService:
    """
    Service for career data, roadmaps, and recommendations.
    Integrates with existing modules while adding caching and AI enhancements.
    """

    def __init__(self):
        self._roadmap_generator: Optional[RoadmapGenerator] = None
        self._recommendation_engine: Optional[RecommendationEngine] = None
        self._initialized = False

    def _ensure_initialized(self):
        """Lazy initialization of modules."""
        if self._initialized:
            return

        if not DATA_MODULES_AVAILABLE:
            logger.warning("Running without career data modules")
            self._initialized = True
            return

        try:
            self._roadmap_generator = RoadmapGenerator()
            self._recommendation_engine = RecommendationEngine()
            self._initialized = True
            logger.info("Career service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize career modules: {e}")
            self._initialized = True

    def _format_career_summary(self, career_data: Dict) -> CareerSummary:
        """Format raw career data into CareerSummary model."""
        median_salary = career_data.get('median_salary', 70000)
        if isinstance(median_salary, (int, float)) and median_salary > 0:
            salary_min = max(30000, int(median_salary * 0.8))
            salary_max = int(median_salary * 1.4)
        else:
            salary_min = 50000
            salary_max = 80000

        return CareerSummary(
            id=career_data.get('soc_code', ''),
            title=career_data.get('title', ''),
            description=career_data.get('description', '')[:200] + '...' if len(career_data.get('description', '')) > 200 else career_data.get('description', ''),
            salary=SalaryRange(min_salary=salary_min, max_salary=salary_max),
            growth=career_data.get('employment_outlook', 'Average'),
            education=career_data.get('education_level', "Bachelor's degree") or "Bachelor's degree",
            cluster=career_data.get('cluster', 'General'),
            skills=career_data.get('skills', [])[:5],
        )

    def _format_career_detail(self, career_data: Dict) -> Career:
        """Format raw career data into full Career model."""
        median_salary = career_data.get('median_salary', 70000)
        if isinstance(median_salary, (int, float)) and median_salary > 0:
            salary_min = max(30000, int(median_salary * 0.8))
            salary_max = int(median_salary * 1.4)
        else:
            salary_min = 50000
            salary_max = 80000

        return Career(
            id=career_data.get('soc_code', ''),
            title=career_data.get('title', ''),
            description=career_data.get('description', ''),
            education=career_data.get('education_level', "Bachelor's degree") or "Bachelor's degree",
            experience=career_data.get('experience_level', '2-5 years') or "2-5 years",
            salary=SalaryRange(min_salary=salary_min, max_salary=salary_max),
            skills=career_data.get('skills', []),
            knowledge=career_data.get('knowledge', []),
            abilities=career_data.get('abilities', []),
            tasks=career_data.get('tasks', []),
            growth=career_data.get('employment_outlook', 'Average'),
            growth_rate=career_data.get('growth_rate', '10%'),
            related_careers=career_data.get('related_occupations', []),
            work_environment=career_data.get('work_environment', []),
            interests=career_data.get('interests', []),
            work_styles=career_data.get('work_styles', []),
            cluster=career_data.get('cluster', 'General'),
        )

    async def get_all_careers(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> CareerSearchResult:
        """Get all available careers with pagination."""
        self._ensure_initialized()

        if not DATA_MODULES_AVAILABLE:
            return CareerSearchResult(results=[], total=0, page=page, page_size=page_size, query="")

        try:
            all_careers = data_loader.get_all_careers()

            # Paginate
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            page_careers = all_careers[start_idx:end_idx]

            results = [self._format_career_summary(c) for c in page_careers]

            return CareerSearchResult(
                results=results,
                total=len(all_careers),
                page=page,
                page_size=page_size,
                query="",
            )
        except Exception as e:
            logger.error(f"Failed to get careers: {e}")
            return CareerSearchResult(results=[], total=0, page=page, page_size=page_size, query="")

    async def get_career(self, career_id: str) -> Career:
        """Get detailed career information."""
        self._ensure_initialized()

        # Check cache first
        cached_data = await cache.get(CacheNamespace.CAREER_DATA, career_id)
        if cached_data:
            return Career(**cached_data)

        if not DATA_MODULES_AVAILABLE:
            raise NotFoundError("Career", career_id)

        career_data = data_loader.get_career(career_id)
        if not career_data:
            raise NotFoundError("Career", career_id)

        career = self._format_career_detail(career_data)

        # Cache the result
        await cache.set(
            CacheNamespace.CAREER_DATA,
            career_id,
            career.model_dump(mode="json"),
            ttl=86400,  # 24 hours
        )

        return career

    async def search_careers(
        self,
        query: str,
        page: int = 1,
        page_size: int = 20,
    ) -> CareerSearchResult:
        """Search for careers."""
        self._ensure_initialized()

        if not DATA_MODULES_AVAILABLE:
            return CareerSearchResult(results=[], total=0, page=page, page_size=page_size, query=query)

        try:
            results_data = data_loader.search_careers(query)

            # Paginate
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            page_results = results_data[start_idx:end_idx]

            results = [self._format_career_summary(c) for c in page_results]

            return CareerSearchResult(
                results=results,
                total=len(results_data),
                page=page,
                page_size=page_size,
                query=query,
            )
        except Exception as e:
            logger.error(f"Career search failed: {e}")
            return CareerSearchResult(results=[], total=0, page=page, page_size=page_size, query=query)

    async def generate_roadmap(
        self,
        request: CareerRoadmapRequest,
        user_id: Optional[str] = None,
    ) -> CareerRoadmap:
        """
        Generate a personalized career roadmap.
        Uses caching for expensive operations.
        """
        self._ensure_initialized()

        # Build cache key
        cache_key = f"{request.career_field}:{request.student_level}:{':'.join(sorted(request.current_skills))}:{request.roadmap_years}"

        # Check cache
        cached_roadmap = await cache.get(CacheNamespace.ROADMAP, cache_key)
        if cached_roadmap:
            logger.info(f"Returning cached roadmap for {request.career_field}")
            return CareerRoadmap(**cached_roadmap)

        if not self._roadmap_generator:
            raise NotFoundError("Roadmap generator not available")

        try:
            # Generate roadmap using existing module
            roadmap_data = self._roadmap_generator.generate_roadmap(
                career_field=request.career_field,
                student_level=request.student_level or "entry",
                current_skills=request.current_skills,
                target_role=request.target_role,
                roadmap_years=request.roadmap_years,
                location=request.location,
                specializations=request.specializations,
                budget_constraints=request.budget_constraints,
                fast_track=request.fast_track,
            )

            # Get summary
            summary = self._roadmap_generator.get_roadmap_summary(roadmap_data)

            # Convert dataclass to dict for model
            from dataclasses import asdict
            roadmap_dict = asdict(roadmap_data)

            # Add AI insights if available
            ai_insights = None
            try:
                prompt = ai_service.create_prompt(
                    system_message="You are a career advisor. Provide brief, personalized insights.",
                    human_template="Career field: {career_field}\nCurrent skills: {skills}\nGoal: {target_role}\n\nProvide 2-3 sentences of personalized career advice.",
                )
                ai_insights = await ai_service.invoke(prompt, {
                    "career_field": request.career_field,
                    "skills": ", ".join(request.current_skills),
                    "target_role": request.target_role or request.career_field,
                })
            except Exception as e:
                logger.warning(f"AI insights unavailable: {e}")

            # Build response model
            roadmap = CareerRoadmap(
                career_field=roadmap_dict['career_field'],
                onet_code=roadmap_dict.get('onet_code'),
                student_level=roadmap_dict.get('student_level'),
                current_skills=roadmap_dict['current_skills'],
                target_role=roadmap_dict['target_role'],
                roadmap_duration=roadmap_dict['roadmap_duration'],
                milestones=[m for m in roadmap_dict['milestones']],
                certifications=[c for c in roadmap_dict['certifications']],
                projects=[p for p in roadmap_dict['projects']],
                salary_progression=[s for s in roadmap_dict['salary_progression']],
                skill_progression=roadmap_dict['skill_progression'],
                alternative_paths=[a for a in roadmap_dict['alternative_paths']],
                pivot_opportunities=roadmap_dict['pivot_opportunities'],
                timeline=roadmap_dict['timeline'],
                confidence_score=roadmap_dict['confidence_score'],
                summary=summary,
                ai_insights=ai_insights,
            )

            # Cache the roadmap
            await cache.set(
                CacheNamespace.ROADMAP,
                cache_key,
                roadmap.model_dump(mode="json"),
                ttl=settings.cache_roadmap_ttl,
            )

            logger.info(f"Generated roadmap for {request.career_field}")
            return roadmap

        except Exception as e:
            logger.error(f"Roadmap generation failed: {e}")
            raise

    async def analyze_skill_gap(
        self,
        request: SkillGapRequest,
    ) -> SkillGapAnalysis:
        """Analyze skill gaps for a target career."""
        self._ensure_initialized()

        # Build cache key
        cache_key = f"{':'.join(sorted(request.current_skills))}:{request.target_career}"

        # Check cache
        cached_analysis = await cache.get(CacheNamespace.SKILL_GAP, cache_key)
        if cached_analysis:
            return SkillGapAnalysis(**cached_analysis)

        # Use AI for analysis
        try:
            prompt = ai_service.get_skill_gap_prompt()

            target_skills = request.target_skills or []
            if not target_skills and self._recommendation_engine:
                # Get target skills from career data
                career_data = data_loader.get_career(request.target_career) if DATA_MODULES_AVAILABLE else None
                if career_data:
                    target_skills = career_data.get('skills', [])[:10]

            response = await ai_service.invoke(prompt, {
                "current_skills": ", ".join(request.current_skills),
                "target_career": request.target_career,
                "target_skills": ", ".join(target_skills),
            })

            # Parse AI response into structured format
            # This is a simplified version - in production you'd use structured output
            analysis = SkillGapAnalysis(
                skill_coverage=70.0,  # Would be calculated
                total_required_skills=len(target_skills),
                skills_met=len(set(request.current_skills) & set(target_skills)),
                skills_partial=0,
                skills_missing=len(set(target_skills) - set(request.current_skills)),
                skill_gaps=[],
                prioritized_skills=[],
                learning_plan=[],
                estimated_total_time="6-12 months",
                ai_analysis=response,
                recommendations=[],
                target_career=request.target_career,
            )

            # Cache result
            await cache.set(
                CacheNamespace.SKILL_GAP,
                cache_key,
                analysis.model_dump(mode="json"),
                ttl=3600,
            )

            return analysis

        except Exception as e:
            logger.error(f"Skill gap analysis failed: {e}")
            raise


# Global instance
career_service = CareerService()
