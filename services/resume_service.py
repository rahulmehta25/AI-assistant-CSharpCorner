"""
Resume Service - Resume analysis and cover letter generation.
"""

import sys
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cache import cache, CacheNamespace
from core.config import settings
from core.logging import get_logger
from models.resume import (
    CoverLetterRequest,
    CoverLetterResult,
    ResumeAnalysisRequest,
    ResumeAnalysisResult,
    ResumeKeywordAnalysis,
    ResumeSuggestion,
)

from .ai_service import ai_service

logger = get_logger(__name__)

# Import existing modules
try:
    from modules.application_assistant import ApplicationAssistant
    RESUME_MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Resume modules not available: {e}")
    RESUME_MODULES_AVAILABLE = False


class ResumeService:
    """
    Service for resume analysis and cover letter generation.
    Combines existing module logic with AI enhancements.
    """

    def __init__(self):
        self._assistant: Optional[ApplicationAssistant] = None
        self._initialized = False

    def _ensure_initialized(self):
        """Lazy initialization."""
        if self._initialized:
            return

        if RESUME_MODULES_AVAILABLE:
            try:
                self._assistant = ApplicationAssistant()
                logger.info("Resume service initialized with ApplicationAssistant")
            except Exception as e:
                logger.warning(f"Failed to initialize ApplicationAssistant: {e}")

        self._initialized = True

    async def analyze_resume(
        self,
        request: ResumeAnalysisRequest,
    ) -> ResumeAnalysisResult:
        """
        Analyze a resume for ATS compatibility and improvements.
        """
        self._ensure_initialized()

        # Build cache key from resume hash
        import hashlib
        resume_hash = hashlib.md5(request.resume_text.encode()).hexdigest()[:12]
        cache_key = f"{resume_hash}:{request.target_role or 'general'}"

        # Check cache
        cached = await cache.get(CacheNamespace.RESUME_ANALYSIS, cache_key)
        if cached:
            cached['cached'] = True
            return ResumeAnalysisResult(**cached)

        suggestions = []
        missing_keywords = []
        missing_technologies = []
        keyword_analysis = ResumeKeywordAnalysis(
            found_keywords=[],
            missing_keywords=[],
            keyword_density=0.0,
            ats_compatibility=70.0,
        )

        # Use existing module if available
        if self._assistant and request.job_description:
            try:
                job_analysis = self._assistant.analyze_job_description(request.job_description)
                optimization = self._assistant.optimize_resume(request.resume_text, job_analysis)

                # Convert suggestions
                for s in optimization.get('suggestions', []):
                    suggestions.append(ResumeSuggestion(
                        type=s.get('type', 'general'),
                        priority=s.get('priority', 'medium'),
                        message=s.get('message', ''),
                    ))

                missing_keywords = optimization.get('missing_keywords', [])
                missing_technologies = optimization.get('missing_technologies', [])

                keyword_analysis = ResumeKeywordAnalysis(
                    found_keywords=job_analysis.get('keywords', []),
                    missing_keywords=missing_keywords,
                    keyword_density=0.0,
                    ats_compatibility=optimization.get('ats_score', 70),
                )

            except Exception as e:
                logger.warning(f"Module analysis failed: {e}")

        # Enhance with AI analysis
        ai_summary = None
        ai_improvements = []

        try:
            prompt = ai_service.get_resume_analysis_prompt()
            ai_response = await ai_service.invoke(prompt, {
                "resume_text": request.resume_text[:3000],  # Limit length
                "target_role": request.target_role or "general position",
                "job_description": request.job_description or "Not provided",
            })

            ai_summary = ai_response
            # Parse improvements from AI response
            if "improve" in ai_response.lower() or "suggest" in ai_response.lower():
                lines = ai_response.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith('-') or line.startswith('*') or line.startswith('1'):
                        ai_improvements.append(line.lstrip('-*0123456789. '))

        except Exception as e:
            logger.warning(f"AI analysis failed: {e}")

        # Calculate overall score
        ats_score = keyword_analysis.ats_compatibility
        if ai_improvements:
            # Adjust score based on number of improvements needed
            improvement_penalty = min(20, len(ai_improvements) * 2)
            overall_score = max(50, ats_score - improvement_penalty)
        else:
            overall_score = ats_score

        result = ResumeAnalysisResult(
            ats_score=ats_score,
            overall_score=overall_score,
            suggestions=suggestions,
            keyword_analysis=keyword_analysis,
            missing_technologies=missing_technologies,
            recommended_sections=self._assistant.recommend_resume_sections("Mid-Level") if self._assistant else [
                "Contact Information", "Summary", "Experience", "Education", "Skills"
            ],
            ai_summary=ai_summary,
            ai_improvements=ai_improvements[:10],
            cached=False,
        )

        # Cache result
        await cache.set(
            CacheNamespace.RESUME_ANALYSIS,
            cache_key,
            result.model_dump(mode="json"),
            ttl=settings.cache_resume_ttl,
        )

        return result

    async def generate_cover_letter(
        self,
        request: CoverLetterRequest,
    ) -> CoverLetterResult:
        """
        Generate a personalized cover letter.
        """
        self._ensure_initialized()

        cover_letter = ""
        ai_generated = False

        # Try AI generation first if requested
        if request.use_ai:
            try:
                prompt = ai_service.get_cover_letter_prompt()
                cover_letter = await ai_service.invoke(prompt, {
                    "candidate_name": request.name,
                    "current_position": request.current_position or "Professional",
                    "target_position": request.target_position,
                    "company_name": request.company_name,
                    "skills": ", ".join(request.skills) if request.skills else "various skills",
                    "achievement": request.key_achievement or "significant accomplishments",
                    "company_reason": request.company_reason or "your company's innovative approach",
                    "template_type": request.template_type,
                })
                ai_generated = True
                logger.info("Generated AI cover letter")

            except Exception as e:
                logger.warning(f"AI cover letter generation failed: {e}")

        # Fallback to template-based generation
        if not cover_letter and self._assistant:
            try:
                user_info = {
                    'name': request.name,
                    'current_position': request.current_position,
                    'skills': request.skills,
                    'achievement': request.key_achievement,
                    'experience_years': str(request.experience_years) if request.experience_years else '3',
                    'field': request.current_position.split()[-1] if request.current_position else 'technology',
                    'key_skill': request.skills[0] if request.skills else 'technical expertise',
                }

                job_info = {
                    'position': request.target_position,
                    'company': request.company_name,
                    'company_reason': request.company_reason or 'of your innovative approach',
                    'company_value': 'innovation and excellence',
                    'company_goal': 'driving industry advancement',
                }

                cover_letter = self._assistant.generate_cover_letter(
                    user_info, job_info, request.template_type
                )

            except Exception as e:
                logger.error(f"Template cover letter generation failed: {e}")
                cover_letter = self._generate_basic_cover_letter(request)

        if not cover_letter:
            cover_letter = self._generate_basic_cover_letter(request)

        # Count words
        word_count = len(cover_letter.split())

        return CoverLetterResult(
            cover_letter=cover_letter,
            template_used=request.template_type,
            ai_generated=ai_generated,
            customization_tips=[
                "Research the company's recent news and incorporate it",
                "Quantify your achievements with specific numbers",
                "Address the letter to a specific person if possible",
            ],
            word_count=word_count,
        )

    def _generate_basic_cover_letter(self, request: CoverLetterRequest) -> str:
        """Generate a basic cover letter as fallback."""
        return f"""Dear Hiring Manager,

I am writing to express my strong interest in the {request.target_position} position at {request.company_name}.

{f"In my current role as {request.current_position}, I have" if request.current_position else "Throughout my career, I have"} developed expertise in {', '.join(request.skills[:3]) if request.skills else "key areas relevant to this role"}. {f"One of my key achievements includes {request.key_achievement}." if request.key_achievement else ""}

I am excited about the opportunity to bring my skills and experience to {request.company_name}. {request.company_reason if request.company_reason else "Your company's reputation for excellence makes this an ideal opportunity."}

Thank you for considering my application. I look forward to discussing how I can contribute to your team.

Sincerely,
{request.name}"""


# Global instance
resume_service = ResumeService()
