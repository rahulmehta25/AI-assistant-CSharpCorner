"""
AI Service - LangChain integration with proper chain composition.
Provides streaming support, output parsers, and prompt templates.
"""

import asyncio
from typing import Any, AsyncIterator, Dict, List, Optional, Type

from pydantic import BaseModel

from core.config import settings
from core.exceptions import AIServiceError
from core.logging import get_logger

logger = get_logger(__name__)

# LangChain imports
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from langchain_core.runnables import RunnablePassthrough, RunnableLambda
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logger.warning("LangChain not available - AI features will be limited")


class AIService:
    """
    AI Service with LangChain integration.
    Provides chain composition, streaming, and structured output parsing.
    """

    def __init__(self):
        self._llm: Optional[ChatGoogleGenerativeAI] = None
        self._streaming_llm: Optional[ChatGoogleGenerativeAI] = None
        self._initialized = False

    def _ensure_initialized(self):
        """Lazy initialization of LLM."""
        if self._initialized:
            return

        if not LANGCHAIN_AVAILABLE:
            raise AIServiceError(
                "LangChain is not installed",
                service="langchain",
            )

        if not settings.gemini_api_key:
            raise AIServiceError(
                "Gemini API key not configured",
                service="gemini",
            )

        try:
            self._llm = ChatGoogleGenerativeAI(
                model=settings.gemini_model,
                temperature=settings.gemini_temperature,
                max_output_tokens=settings.gemini_max_tokens,
                google_api_key=settings.gemini_api_key,
            )

            self._streaming_llm = ChatGoogleGenerativeAI(
                model=settings.gemini_model,
                temperature=settings.gemini_temperature,
                max_output_tokens=settings.gemini_max_tokens,
                google_api_key=settings.gemini_api_key,
                streaming=True,
            )

            self._initialized = True
            logger.info(f"AI Service initialized with model: {settings.gemini_model}")

        except Exception as e:
            raise AIServiceError(
                f"Failed to initialize AI service: {str(e)}",
                service="gemini",
            )

    @property
    def llm(self) -> ChatGoogleGenerativeAI:
        """Get the LLM instance."""
        self._ensure_initialized()
        return self._llm

    @property
    def streaming_llm(self) -> ChatGoogleGenerativeAI:
        """Get the streaming LLM instance."""
        self._ensure_initialized()
        return self._streaming_llm

    # Prompt Templates

    def create_prompt(
        self,
        system_message: str,
        human_template: str,
        include_history: bool = False,
    ) -> ChatPromptTemplate:
        """Create a chat prompt template."""
        messages = [("system", system_message)]

        if include_history:
            messages.append(MessagesPlaceholder(variable_name="history"))

        messages.append(("human", human_template))

        return ChatPromptTemplate.from_messages(messages)

    # Chain Builders

    def build_chain(
        self,
        prompt: ChatPromptTemplate,
        output_parser: Optional[Any] = None,
        streaming: bool = False,
    ):
        """
        Build a chain with prompt, LLM, and output parser.

        Args:
            prompt: The prompt template
            output_parser: Optional output parser (JsonOutputParser, StrOutputParser, etc.)
            streaming: Whether to use streaming LLM

        Returns:
            Runnable chain
        """
        self._ensure_initialized()

        llm = self._streaming_llm if streaming else self._llm

        if output_parser:
            return prompt | llm | output_parser
        else:
            return prompt | llm | StrOutputParser()

    def build_structured_chain(
        self,
        prompt: ChatPromptTemplate,
        output_schema: Type[BaseModel],
    ):
        """
        Build a chain that outputs structured data.

        Args:
            prompt: The prompt template
            output_schema: Pydantic model for output structure

        Returns:
            Runnable chain that outputs parsed Pydantic model
        """
        self._ensure_initialized()

        parser = JsonOutputParser(pydantic_object=output_schema)

        # Add format instructions to prompt
        format_instructions = parser.get_format_instructions()

        return (
            RunnablePassthrough.assign(
                format_instructions=lambda _: format_instructions
            )
            | prompt
            | self._llm
            | parser
        )

    # Execution Methods

    async def invoke(
        self,
        prompt: ChatPromptTemplate,
        inputs: Dict[str, Any],
        output_parser: Optional[Any] = None,
    ) -> str:
        """
        Invoke a chain and return the result.

        Args:
            prompt: The prompt template
            inputs: Input variables for the prompt
            output_parser: Optional output parser

        Returns:
            String result
        """
        chain = self.build_chain(prompt, output_parser, streaming=False)

        try:
            result = await chain.ainvoke(inputs)
            return result
        except Exception as e:
            logger.error(f"AI invocation failed: {e}")
            raise AIServiceError(
                f"AI request failed: {str(e)}",
                service="gemini",
            )

    async def invoke_structured(
        self,
        prompt: ChatPromptTemplate,
        inputs: Dict[str, Any],
        output_schema: Type[BaseModel],
    ) -> BaseModel:
        """
        Invoke a chain and return structured output.

        Args:
            prompt: The prompt template
            inputs: Input variables for the prompt
            output_schema: Pydantic model for output

        Returns:
            Parsed Pydantic model instance
        """
        chain = self.build_structured_chain(prompt, output_schema)

        try:
            result = await chain.ainvoke(inputs)
            return result
        except Exception as e:
            logger.error(f"Structured AI invocation failed: {e}")
            raise AIServiceError(
                f"AI request failed: {str(e)}",
                service="gemini",
            )

    async def stream(
        self,
        prompt: ChatPromptTemplate,
        inputs: Dict[str, Any],
    ) -> AsyncIterator[str]:
        """
        Stream a response from the AI.

        Args:
            prompt: The prompt template
            inputs: Input variables for the prompt

        Yields:
            String chunks
        """
        chain = self.build_chain(prompt, streaming=True)

        try:
            async for chunk in chain.astream(inputs):
                yield chunk
        except Exception as e:
            logger.error(f"AI streaming failed: {e}")
            raise AIServiceError(
                f"AI streaming failed: {str(e)}",
                service="gemini",
            )

    # Pre-built Prompts

    def get_career_advisor_prompt(self) -> ChatPromptTemplate:
        """Get the career advisor system prompt."""
        return self.create_prompt(
            system_message="""You are an expert career advisor AI assistant. You help users with:
- Career planning and roadmaps
- Job search strategies
- Resume and cover letter optimization
- Interview preparation
- Skill development recommendations
- Industry insights and trends

Be supportive, practical, and provide actionable advice.
Always be encouraging while being realistic about career transitions.
When discussing salaries, use ranges and note they vary by location.
Format your responses with clear sections using markdown.""",
            human_template="{message}",
            include_history=True,
        )

    def get_resume_analysis_prompt(self) -> ChatPromptTemplate:
        """Get the resume analysis prompt."""
        return self.create_prompt(
            system_message="""You are an expert resume analyst and ATS optimization specialist.
Analyze resumes and provide actionable feedback to improve them.
Focus on:
- ATS compatibility and keyword optimization
- Impact and achievement quantification
- Structure and formatting
- Industry-specific best practices

Provide specific, actionable suggestions.""",
            human_template="""Analyze this resume for the target role: {target_role}

Resume:
{resume_text}

Job Description (if provided):
{job_description}

Provide a detailed analysis with specific improvement suggestions.""",
        )

    def get_cover_letter_prompt(self) -> ChatPromptTemplate:
        """Get the cover letter generation prompt."""
        return self.create_prompt(
            system_message="""You are an expert cover letter writer.
Create compelling, personalized cover letters that:
- Highlight relevant experience and skills
- Show genuine interest in the company
- Demonstrate value the candidate can bring
- Are professional but personable
- Are concise (under 400 words)

Match the tone to the company culture when possible.""",
            human_template="""Write a cover letter for:

Candidate: {candidate_name}
Current Position: {current_position}
Target Position: {target_position}
Company: {company_name}
Key Skills: {skills}
Key Achievement: {achievement}
Why interested in company: {company_reason}

Template Style: {template_type}""",
        )

    def get_skill_gap_prompt(self) -> ChatPromptTemplate:
        """Get the skill gap analysis prompt."""
        return self.create_prompt(
            system_message="""You are a career development expert specializing in skill gap analysis.
Analyze current skills versus target career requirements and provide:
- Prioritized list of skills to develop
- Estimated time to acquire each skill
- Recommended learning resources
- Project ideas to practice skills
- Career impact of each skill

Be realistic about timelines and prioritize high-impact skills.""",
            human_template="""Analyze the skill gap for this career transition:

Current Skills: {current_skills}
Target Career: {target_career}
Target Skills Required: {target_skills}

Provide a detailed analysis with a prioritized learning plan.""",
        )

    def get_interview_prep_prompt(self) -> ChatPromptTemplate:
        """Get the interview preparation prompt."""
        return self.create_prompt(
            system_message="""You are an expert interview coach with deep knowledge of hiring practices.
Generate tailored interview questions and preparation guidance.
Include:
- Behavioral questions (STAR method)
- Technical questions (role-specific)
- Situational questions
- Questions to ask the interviewer
- Tips for success

Tailor questions to the specific role and experience level.""",
            human_template="""Generate interview preparation for:

Job Title: {job_title}
Company: {company_name}
Experience Level: {experience_level}
Job Description: {job_description}
Candidate Skills: {user_skills}

Provide comprehensive interview preparation guidance.""",
        )


# Global AI service instance
ai_service = AIService()
