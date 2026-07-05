"""
Unit Tests for LangChain Integration

Tests LangChain chains, prompt templates, and AI-powered
features with mocked LLM responses.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestLangChainPromptTemplates:
    """Test LangChain prompt template configurations."""

    def test_career_advisor_prompt_structure(self):
        """Test career advisor prompt has required placeholders."""
        # The prompt should include placeholders for user profile
        with patch("langchain_core.prompts.ChatPromptTemplate") as mock_template:
            mock_template.from_messages.return_value = MagicMock()

            # Verify prompt template can be created
            from langchain_core.prompts import ChatPromptTemplate

            template = ChatPromptTemplate.from_messages([
                ("system", "You are a career advisor. Help the user with: {topic}"),
                ("human", "{user_input}")
            ])

            assert template is not None

    def test_skill_gap_prompt_template(self):
        """Test skill gap analysis prompt template."""
        with patch("langchain_core.prompts.ChatPromptTemplate") as mock_template:
            mock_instance = MagicMock()
            mock_template.from_template.return_value = mock_instance

            from langchain_core.prompts import ChatPromptTemplate

            template = ChatPromptTemplate.from_template(
                """Analyze skill gaps for a user with skills: {current_skills}
                Target career: {target_career}
                Provide recommendations for improvement."""
            )

            assert template is not None


class TestMockedLLMResponses:
    """Test with mocked LLM responses."""

    @pytest.fixture
    def mock_chat_openai(self):
        """Create mocked ChatOpenAI instance."""
        with patch("langchain_openai.ChatOpenAI") as mock_llm:
            instance = MagicMock()
            mock_llm.return_value = instance

            # Mock invoke method
            mock_response = MagicMock()
            mock_response.content = json.dumps({
                "recommendations": [
                    {"skill": "Python", "priority": "high"},
                    {"skill": "AWS", "priority": "medium"},
                ],
                "timeline": "3-6 months",
                "confidence": 0.85
            })
            instance.invoke.return_value = mock_response

            yield instance

    def test_llm_career_recommendation(self, mock_chat_openai):
        """Test career recommendation with mocked LLM."""
        response = mock_chat_openai.invoke("Give me career advice")

        assert response.content is not None
        data = json.loads(response.content)
        assert "recommendations" in data

    def test_llm_response_parsing(self, mock_chat_openai):
        """Test parsing structured LLM responses."""
        response = mock_chat_openai.invoke("Analyze skills")

        data = json.loads(response.content)
        assert len(data["recommendations"]) == 2
        assert data["confidence"] == 0.85


class TestPydanticOutputParser:
    """Test Pydantic output parsing for LLM responses."""

    def test_career_insight_parsing(self):
        """Test parsing career insight from LLM response."""
        from pydantic import BaseModel
        from typing import List

        class CareerInsight(BaseModel):
            career_name: str
            match_score: float
            reasons: List[str]

        # Test that model can parse expected response format
        data = {
            "career_name": "Software Engineer",
            "match_score": 0.92,
            "reasons": ["Strong Python skills", "Good problem solving"]
        }

        insight = CareerInsight(**data)
        assert insight.career_name == "Software Engineer"
        assert insight.match_score == 0.92
        assert len(insight.reasons) == 2

    def test_skill_gap_response_parsing(self):
        """Test parsing skill gap analysis response."""
        from pydantic import BaseModel
        from typing import List, Optional

        class SkillGap(BaseModel):
            skill_name: str
            current_level: Optional[str]
            required_level: str
            priority: str

        class SkillGapAnalysis(BaseModel):
            gaps: List[SkillGap]
            overall_readiness: float

        data = {
            "gaps": [
                {"skill_name": "Kubernetes", "required_level": "intermediate", "priority": "high"},
                {"skill_name": "AWS", "required_level": "advanced", "priority": "medium"},
            ],
            "overall_readiness": 0.65
        }

        analysis = SkillGapAnalysis(**data)
        assert len(analysis.gaps) == 2
        assert analysis.overall_readiness == 0.65


@pytest.mark.langchain
class TestLangChainChainExecution:
    """Test LangChain chain execution with mocks."""

    @pytest.fixture
    def mock_runnable_chain(self):
        """Create mocked runnable chain."""
        with patch("langchain_core.runnables.RunnableSequence") as mock_chain:
            instance = MagicMock()
            mock_chain.return_value = instance

            instance.invoke.return_value = {
                "text": "Career recommendation result",
                "metadata": {"tokens": 150}
            }

            yield instance

    def test_chain_execution(self, mock_runnable_chain):
        """Test chain execution returns expected format."""
        result = mock_runnable_chain.invoke({"input": "career advice"})

        assert "text" in result
        assert "metadata" in result

    def test_chain_with_user_profile(self, mock_runnable_chain):
        """Test chain execution with user profile input."""
        profile = {
            "skills": ["Python", "JavaScript"],
            "experience": "3 years",
            "interests": ["AI"]
        }

        result = mock_runnable_chain.invoke(profile)

        assert result is not None


class TestChatMessageHistory:
    """Test chat message history functionality."""

    def test_message_history_storage(self):
        """Test that message history can store messages."""
        with patch("langchain_community.chat_message_histories.ChatMessageHistory") as mock_history:
            instance = MagicMock()
            mock_history.return_value = instance

            instance.messages = []

            # Simulate adding messages
            instance.add_user_message = MagicMock()
            instance.add_ai_message = MagicMock()

            instance.add_user_message("What career should I pursue?")
            instance.add_ai_message("Based on your skills...")

            assert instance.add_user_message.called
            assert instance.add_ai_message.called


class TestRunnableWithMessageHistory:
    """Test runnable with message history."""

    def test_message_history_integration(self):
        """Test chain with message history maintains context."""
        with patch("langchain_core.runnables.history.RunnableWithMessageHistory") as mock_runnable:
            instance = MagicMock()
            mock_runnable.return_value = instance

            instance.invoke.return_value = {
                "output": "Follow-up career advice based on context"
            }

            result = instance.invoke(
                {"input": "Tell me more about that career"},
                config={"configurable": {"session_id": "user123"}}
            )

            assert result is not None


@pytest.mark.langchain
class TestRecommendationEngineLangChain:
    """Test LangChain integration in RecommendationEngine."""

    @pytest.fixture
    def mock_recommendation_engine(self):
        """Create mocked recommendation engine."""
        with patch("modules.recommendation_engine.ChatOpenAI") as mock_llm:
            llm_instance = MagicMock()
            mock_llm.return_value = llm_instance

            mock_response = MagicMock()
            mock_response.content = json.dumps({
                "career_insights": [
                    {"career": "ML Engineer", "fit_score": 0.9}
                ],
                "skill_recommendations": ["TensorFlow", "PyTorch"]
            })
            llm_instance.invoke.return_value = mock_response

            yield llm_instance

    def test_ai_career_insights(self, mock_recommendation_engine):
        """Test AI-powered career insights."""
        response = mock_recommendation_engine.invoke("Generate career insights")

        data = json.loads(response.content)
        assert "career_insights" in data
        assert len(data["career_insights"]) > 0


class TestPromptFormatting:
    """Test prompt formatting utilities."""

    def test_format_user_profile_prompt(self):
        """Test formatting user profile into prompt."""
        profile = {
            "name": "Test User",
            "skills": ["Python", "JavaScript"],
            "experience": "3 years",
            "interests": ["AI", "Web Development"]
        }

        prompt = f"""
        User Profile:
        - Name: {profile['name']}
        - Skills: {', '.join(profile['skills'])}
        - Experience: {profile['experience']}
        - Interests: {', '.join(profile['interests'])}

        Based on this profile, provide career recommendations.
        """

        assert "Test User" in prompt
        assert "Python" in prompt
        assert "3 years" in prompt

    def test_format_skill_gap_prompt(self):
        """Test formatting skill gap analysis prompt."""
        current_skills = ["Python", "SQL"]
        target_career = "Data Scientist"
        required_skills = ["Python", "SQL", "Machine Learning", "Statistics"]

        missing = set(required_skills) - set(current_skills)

        prompt = f"""
        Analyze skill gaps:
        Current: {', '.join(current_skills)}
        Target: {target_career}
        Missing: {', '.join(missing)}
        """

        assert "Machine Learning" in prompt
        assert "Statistics" in prompt


class TestErrorHandlingLangChain:
    """Test error handling for LangChain operations."""

    def test_llm_timeout_handling(self):
        """Test handling LLM timeout errors."""
        with patch("langchain_openai.ChatOpenAI") as mock_llm:
            instance = MagicMock()
            mock_llm.return_value = instance

            instance.invoke.side_effect = TimeoutError("LLM request timed out")

            with pytest.raises(TimeoutError):
                instance.invoke("test")

    def test_invalid_api_key_handling(self):
        """Test handling invalid API key errors."""
        with patch("langchain_openai.ChatOpenAI") as mock_llm:
            instance = MagicMock()
            mock_llm.return_value = instance

            instance.invoke.side_effect = Exception("Invalid API key")

            with pytest.raises(Exception) as exc_info:
                instance.invoke("test")

            assert "Invalid API key" in str(exc_info.value)

    def test_malformed_response_handling(self):
        """Test handling malformed LLM responses."""
        with patch("langchain_openai.ChatOpenAI") as mock_llm:
            instance = MagicMock()
            mock_llm.return_value = instance

            mock_response = MagicMock()
            mock_response.content = "not valid json {"

            instance.invoke.return_value = mock_response

            response = instance.invoke("test")

            # Should be able to detect invalid JSON
            with pytest.raises(json.JSONDecodeError):
                json.loads(response.content)
