"""
Interview Service - Interview preparation and mock interviews.
"""

import sys
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.logging import get_logger
from models.interview import (
    InterviewPrepRequest,
    InterviewPrepResult,
    InterviewQuestion,
    CompanyResearch,
)

from .ai_service import ai_service

logger = get_logger(__name__)

# Import existing modules
try:
    from modules.application_assistant import ApplicationAssistant
    INTERVIEW_MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Interview modules not available: {e}")
    INTERVIEW_MODULES_AVAILABLE = False


class InterviewService:
    """
    Service for interview preparation and practice.
    """

    def __init__(self):
        self._assistant: Optional[ApplicationAssistant] = None
        self._initialized = False

    def _ensure_initialized(self):
        """Lazy initialization."""
        if self._initialized:
            return

        if INTERVIEW_MODULES_AVAILABLE:
            try:
                self._assistant = ApplicationAssistant()
                logger.info("Interview service initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize ApplicationAssistant: {e}")

        self._initialized = True

    def _format_question(
        self,
        question_text: str,
        category: str,
        difficulty: str = "medium",
    ) -> InterviewQuestion:
        """Format a question into InterviewQuestion model."""
        return InterviewQuestion(
            question=question_text,
            category=category,
            difficulty=difficulty,
            tips=[],
        )

    async def generate_prep(
        self,
        request: InterviewPrepRequest,
    ) -> InterviewPrepResult:
        """
        Generate comprehensive interview preparation.
        """
        self._ensure_initialized()

        behavioral_questions = []
        technical_questions = []
        situational_questions = []
        questions_to_ask = []

        # Use existing module for base questions
        if self._assistant:
            try:
                questions = self._assistant.generate_interview_questions(
                    request.job_title,
                    request.job_description or "",
                    request.experience_level,
                )

                if request.include_behavioral:
                    behavioral_questions = [
                        self._format_question(q, "behavioral")
                        for q in questions.get('behavioral', [])
                    ]

                if request.include_technical:
                    technical_questions = [
                        self._format_question(q, "technical", "medium")
                        for q in questions.get('technical', [])
                    ]

                if request.include_situational:
                    situational_questions = [
                        self._format_question(q, "situational")
                        for q in questions.get('situational', [])
                    ]

                questions_to_ask = questions.get('questions_to_ask', [])

            except Exception as e:
                logger.warning(f"Module question generation failed: {e}")

        # Enhance with AI if we don't have enough questions
        total_questions = len(behavioral_questions) + len(technical_questions) + len(situational_questions)
        if total_questions < request.num_questions:
            try:
                prompt = ai_service.get_interview_prep_prompt()
                ai_response = await ai_service.invoke(prompt, {
                    "job_title": request.job_title,
                    "company_name": request.company_name or "the company",
                    "experience_level": request.experience_level,
                    "job_description": request.job_description or "Not provided",
                    "user_skills": ", ".join(request.user_skills) if request.user_skills else "various skills",
                })

                # Parse AI response to extract additional questions
                lines = ai_response.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.endswith('?'):
                        # Simple heuristic to categorize
                        if any(word in line.lower() for word in ['tell me', 'describe', 'time when']):
                            if len(behavioral_questions) < 7:
                                behavioral_questions.append(self._format_question(line, "behavioral"))
                        elif any(word in line.lower() for word in ['would you', 'how would', 'what if']):
                            if len(situational_questions) < 5:
                                situational_questions.append(self._format_question(line, "situational"))
                        elif any(word in line.lower() for word in ['explain', 'how does', 'implement', 'design']):
                            if len(technical_questions) < 6:
                                technical_questions.append(self._format_question(line, "technical"))

            except Exception as e:
                logger.warning(f"AI question generation failed: {e}")

        # Generate AI insights
        ai_insights = None
        personalized_tips = []

        try:
            insight_prompt = ai_service.create_prompt(
                system_message="You are an interview coach. Provide brief, actionable advice.",
                human_template="Job: {job_title} at {company}\nCandidate skills: {skills}\n\nProvide 3-4 specific tips for this interview.",
            )
            ai_insights = await ai_service.invoke(insight_prompt, {
                "job_title": request.job_title,
                "company": request.company_name or "the company",
                "skills": ", ".join(request.user_skills) if request.user_skills else "technical skills",
            })

            # Parse tips
            for line in ai_insights.split('\n'):
                line = line.strip()
                if line.startswith(('-', '*', '1', '2', '3', '4')):
                    personalized_tips.append(line.lstrip('-*0123456789. '))

        except Exception as e:
            logger.warning(f"AI insights failed: {e}")

        # Default questions to ask if none generated
        if not questions_to_ask:
            questions_to_ask = [
                "What does a typical day look like in this role?",
                "What are the biggest challenges facing the team right now?",
                "How do you measure success in this position?",
                "What opportunities are there for professional development?",
                "What do you enjoy most about working here?",
            ]

        return InterviewPrepResult(
            job_title=request.job_title,
            company_name=request.company_name,
            experience_level=request.experience_level,
            behavioral_questions=behavioral_questions[:7],
            technical_questions=technical_questions[:6],
            situational_questions=situational_questions[:5],
            questions_to_ask=questions_to_ask[:7],
            preparation_tips=[
                "Research the company thoroughly before the interview",
                "Prepare specific examples using the STAR method",
                "Practice your answers out loud",
                "Prepare thoughtful questions to ask",
                "Dress appropriately and arrive early",
            ],
            common_mistakes=[
                "Not researching the company",
                "Giving vague answers without specific examples",
                "Speaking negatively about previous employers",
                "Not asking any questions",
                "Focusing only on salary and benefits",
            ],
            success_strategies=[
                "Show enthusiasm for the role and company",
                "Connect your experience to job requirements",
                "Be concise but thorough in your answers",
                "Ask insightful questions that show preparation",
                "Follow up with a thank you note",
            ],
            ai_insights=ai_insights,
            personalized_tips=personalized_tips[:5],
        )


# Global instance
interview_service = InterviewService()
