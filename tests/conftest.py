"""
Pytest Configuration and Fixtures for AI Career Assistant

Provides comprehensive test fixtures including:
- Mock OpenAI/LangChain responses
- Sample user profiles and career data
- API test client
- Database fixtures
"""

import json
import os
import sys
from typing import Any, Dict, Generator, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ============================================================================
# Sample Data Fixtures
# ============================================================================

@pytest.fixture
def sample_user_profile() -> Dict[str, Any]:
    """Basic user profile for testing."""
    return {
        "name": "Test User",
        "experience": "3 years",
        "skills": ["Python", "JavaScript", "React", "SQL", "Docker"],
        "interests": ["Machine Learning", "Web Development", "Cloud Computing"],
        "education_level": "Bachelor's degree",
        "career_goals": ["Software Engineer", "Tech Lead"],
    }


@pytest.fixture
def sample_senior_profile() -> Dict[str, Any]:
    """Senior-level user profile for testing."""
    return {
        "name": "Senior Developer",
        "experience": "8 years",
        "skills": [
            "Python", "Java", "Go", "Kubernetes", "AWS", "System Design",
            "Team Leadership", "Agile", "CI/CD", "PostgreSQL"
        ],
        "interests": ["Architecture", "DevOps", "Mentoring"],
        "education_level": "Master's degree",
        "career_goals": ["Principal Engineer", "Engineering Manager"],
    }


@pytest.fixture
def sample_student_profile() -> Dict[str, Any]:
    """Student profile for pathway testing."""
    return {
        "student_level": "junior_college",
        "grade_year": "3",
        "interests": ["Data Science", "Artificial Intelligence"],
        "current_skills": ["Python", "Statistics", "Excel"],
        "career_goals": ["Data Scientist"],
        "gpa": 3.5,
        "standardized_scores": {"SAT": 1350, "GRE": 320},
    }


@pytest.fixture
def sample_career_data() -> Dict[str, Any]:
    """Sample career data matching O*NET format."""
    return {
        "soc_code": "15-1252.00",
        "title": "Software Developers",
        "description": "Research, design, and develop computer and network software.",
        "cluster": "Information Technology",
        "tasks": [
            "Develop software solutions by analyzing system requirements",
            "Design and implement software applications",
            "Debug and test software components",
        ],
        "skills": ["Programming", "Complex Problem Solving", "Systems Analysis"],
        "knowledge": ["Computers and Electronics", "Mathematics", "Engineering"],
        "abilities": ["Deductive Reasoning", "Information Ordering", "Oral Expression"],
        "median_salary": 120200,
        "education_level": "Bachelor's degree",
        "experience_level": "2-5 years",
        "employment_outlook": "Much faster than average",
        "growth_rate": "25%",
        "work_environment": ["Office", "Remote work options"],
        "interests": ["Investigative", "Conventional"],
        "work_styles": ["Analytical Thinking", "Attention to Detail"],
        "related_occupations": ["15-1251.00", "15-1253.00"],
    }


@pytest.fixture
def sample_job_data() -> Dict[str, Any]:
    """Sample job posting data."""
    return {
        "id": "job-123",
        "title": "Senior Software Engineer",
        "company": "Tech Corp",
        "location": "San Francisco, CA",
        "salary": {"min": 150000, "max": 200000},
        "type": "full-time",
        "description": "We are looking for a Senior Software Engineer...",
        "requirements": [
            "5+ years of software development experience",
            "Proficiency in Python and JavaScript",
            "Experience with cloud platforms (AWS/GCP)",
        ],
        "benefits": ["Health insurance", "401k", "Remote work"],
        "posted_date": "2026-03-01",
    }


@pytest.fixture
def sample_careers_list() -> List[Dict[str, Any]]:
    """List of sample careers for testing."""
    return [
        {
            "soc_code": "15-1252.00",
            "title": "Software Developers",
            "description": "Research, design, and develop computer software.",
            "cluster": "Information Technology",
            "median_salary": 120200,
            "skills": ["Programming", "Problem Solving"],
            "education_level": "Bachelor's degree",
            "employment_outlook": "Much faster than average",
        },
        {
            "soc_code": "15-2051.00",
            "title": "Data Scientists",
            "description": "Develop and implement statistical models.",
            "cluster": "Information Technology",
            "median_salary": 108660,
            "skills": ["Statistics", "Machine Learning", "Python"],
            "education_level": "Master's degree",
            "employment_outlook": "Faster than average",
        },
        {
            "soc_code": "11-3021.00",
            "title": "Computer and Information Systems Managers",
            "description": "Plan, direct, or coordinate activities in IT.",
            "cluster": "Management",
            "median_salary": 164070,
            "skills": ["Leadership", "Strategic Planning"],
            "education_level": "Bachelor's degree",
            "employment_outlook": "Average",
        },
    ]


# ============================================================================
# Mock OpenAI Fixtures
# ============================================================================

@pytest.fixture
def mock_openai_response():
    """Factory fixture for creating mock OpenAI responses."""
    def _create_response(content: str = "Test response"):
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.content = content
        return mock_response
    return _create_response


@pytest.fixture
def mock_openai_client(mock_openai_response):
    """Mock OpenAI client for testing."""
    with patch("openai.OpenAI") as mock_client:
        instance = MagicMock()
        mock_client.return_value = instance
        instance.chat.completions.create.return_value = mock_openai_response(
            json.dumps({
                "summary": "AI-generated career advice",
                "recommendations": ["Learn Python", "Build projects"],
                "confidence": 0.85,
            })
        )
        yield instance


@pytest.fixture
def mock_openai_async():
    """Mock async OpenAI client."""
    with patch("openai.AsyncOpenAI") as mock_client:
        instance = AsyncMock()
        mock_client.return_value = instance

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "analysis": "Career analysis result",
            "score": 0.9,
        })
        instance.chat.completions.create.return_value = mock_response
        yield instance


# ============================================================================
# Mock LangChain Fixtures
# ============================================================================

@pytest.fixture
def mock_langchain_llm():
    """Mock LangChain ChatOpenAI model."""
    with patch("langchain_openai.ChatOpenAI") as mock_llm:
        instance = MagicMock()
        mock_llm.return_value = instance

        # Mock invoke method
        mock_message = MagicMock()
        mock_message.content = json.dumps({
            "career_path": "Software Engineering",
            "timeline": "5 years",
            "milestones": ["Junior Dev", "Mid-level", "Senior"],
        })
        instance.invoke.return_value = mock_message

        yield instance


@pytest.fixture
def mock_langchain_chain():
    """Mock LangChain chain for testing."""
    with patch("langchain_core.runnables.RunnableSequence") as mock_chain:
        instance = MagicMock()
        mock_chain.return_value = instance

        instance.invoke.return_value = {
            "text": "Career recommendation based on your profile",
            "metadata": {"confidence": 0.9},
        }
        yield instance


@pytest.fixture
def mock_chat_prompt_template():
    """Mock ChatPromptTemplate."""
    with patch("langchain_core.prompts.ChatPromptTemplate") as mock_template:
        template_instance = MagicMock()
        mock_template.from_messages.return_value = template_instance
        mock_template.from_template.return_value = template_instance
        yield template_instance


# ============================================================================
# API Test Client Fixtures
# ============================================================================

@pytest.fixture
def mock_data_loader(sample_careers_list, sample_career_data):
    """Mock the data_loader module."""
    with patch("modules.data_loader.data_loader") as mock_loader:
        mock_loader.get_all_careers.return_value = sample_careers_list
        mock_loader.get_career.return_value = sample_career_data
        mock_loader.search_careers.return_value = sample_careers_list[:2]
        yield mock_loader


@pytest.fixture
def mock_career_assistant():
    """Mock CareerAssistantCore."""
    with patch("modules.career_assistant_core.CareerAssistantCore") as mock_assistant:
        instance = MagicMock()
        mock_assistant.return_value = instance

        instance.analyze_profile.return_value = {
            "profile_score": 85,
            "recommendations": ["Focus on cloud skills"],
        }
        instance.create_roadmap.return_value = {
            "roadmap": "5-year plan",
            "milestones": [],
        }
        instance.match_jobs.return_value = [
            {"job_id": "1", "score": 0.9, "title": "Software Engineer"},
        ]
        instance.analyze_skills.return_value = {
            "current_skills": ["Python"],
            "gaps": ["Kubernetes"],
        }
        instance.analyze_skill_gap.return_value = {
            "gaps": ["Cloud", "DevOps"],
            "recommendations": ["Take AWS certification"],
        }
        instance.generate_resume.return_value = {
            "resume": "Generated resume content",
        }
        instance.generate_cover_letter.return_value = {
            "cover_letter": "Generated cover letter",
        }
        yield instance


@pytest.fixture
def mock_pathway_generator():
    """Mock StudentPathwaySystem."""
    with patch("modules.student_pathways.StudentPathwaySystem") as mock_pathway:
        instance = MagicMock()
        mock_pathway.return_value = instance

        # Create a mock pathway
        mock_pathway_obj = MagicMock()
        mock_pathway_obj.student_level.value = "junior_college"
        mock_pathway_obj.career_field = "computer science"
        mock_pathway_obj.onet_code = "15-1252.00"
        mock_pathway_obj.milestones = []
        mock_pathway_obj.courses = []
        mock_pathway_obj.activities = []
        mock_pathway_obj.skills_to_develop = ["Python", "ML"]
        mock_pathway_obj.timeline = {}

        instance.generate_pathway.return_value = mock_pathway_obj
        instance.get_pathway_summary.return_value = "Pathway summary"
        yield instance


@pytest.fixture
def mock_job_scraper():
    """Mock LiveJobScraper."""
    with patch("modules.live_job_scraper.LiveJobScraper") as mock_scraper:
        instance = MagicMock()
        mock_scraper.return_value = instance

        async_mock = AsyncMock()
        async_mock.return_value = {
            "combined": [
                {"id": "1", "title": "Software Engineer", "company": "Tech Co"},
            ],
            "search_metadata": {"sources_used": ["indeed"]},
        }
        instance.search_jobs = async_mock
        yield instance


@pytest.fixture
def mock_recommendation_engine():
    """Mock RecommendationEngine."""
    with patch("modules.recommendation_engine.RecommendationEngine") as mock_engine:
        instance = MagicMock()
        mock_engine.return_value = instance

        instance.generate_recommendations.return_value = [
            {"career": "Software Engineer", "score": 0.95},
        ]
        instance.get_ai_skill_gap_analysis.return_value = {
            "gaps": ["Cloud", "ML"],
            "recommendations": ["Take courses"],
        }
        instance.generate_ai_resume_suggestions.return_value = {
            "suggestions": ["Add more metrics"],
        }
        instance.generate_ai_cover_letter.return_value = {
            "content": "Generated cover letter",
        }
        yield instance


@pytest.fixture
def api_client(
    mock_data_loader,
    mock_career_assistant,
    mock_pathway_generator,
    mock_job_scraper,
    mock_recommendation_engine,
):
    """Create a test client with all dependencies mocked."""
    # Patch all imports before importing the app
    with patch.dict("sys.modules", {
        "modules.career_assistant_core": MagicMock(CareerAssistantCore=mock_career_assistant),
        "modules.data_loader": MagicMock(data_loader=mock_data_loader),
        "modules.student_pathways": MagicMock(
            StudentPathwaySystem=mock_pathway_generator.__class__,
            StudentLevel=MagicMock()
        ),
        "modules.live_job_scraper": MagicMock(LiveJobScraper=mock_job_scraper.__class__),
        "modules.recommendation_engine": MagicMock(RecommendationEngine=mock_recommendation_engine.__class__),
    }):
        # Import fresh to get mocked dependencies
        import importlib
        import api_bridge
        importlib.reload(api_bridge)

        client = TestClient(api_bridge.app)
        yield client


@pytest.fixture
def simple_api_client():
    """Simple API test client without mocks - for testing actual integration."""
    from api_bridge import app
    return TestClient(app)


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database path."""
    return str(tmp_path / "test_career_assistant.db")


@pytest.fixture
def mock_database(temp_db_path):
    """Mock database for testing."""
    with patch("modules.user_database.DATABASE_PATH", temp_db_path):
        yield temp_db_path


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def mock_env_vars():
    """Set up mock environment variables."""
    env_vars = {
        "OPENAI_API_KEY": "test-api-key-12345",
        "DATABASE_PATH": ":memory:",
        "LOG_LEVEL": "DEBUG",
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def sample_roadmap_data() -> Dict[str, Any]:
    """Sample roadmap data for testing."""
    return {
        "career_path": "Software Engineering",
        "current_level": "junior",
        "target_level": "senior",
        "timeline_years": 5,
        "milestones": [
            {
                "id": "m1",
                "title": "Complete Python certification",
                "target_date": "Year 1",
                "priority": "high",
                "category": "certification",
            },
            {
                "id": "m2",
                "title": "Lead first project",
                "target_date": "Year 2",
                "priority": "critical",
                "category": "experience",
            },
            {
                "id": "m3",
                "title": "Obtain AWS certification",
                "target_date": "Year 3",
                "priority": "medium",
                "category": "certification",
            },
        ],
        "salary_progression": [
            {"year": 1, "salary": 80000},
            {"year": 3, "salary": 110000},
            {"year": 5, "salary": 150000},
        ],
    }


@pytest.fixture
def sample_skill_gap_data() -> Dict[str, Any]:
    """Sample skill gap analysis data."""
    return {
        "current_skills": ["Python", "JavaScript", "SQL"],
        "target_career": "Machine Learning Engineer",
        "required_skills": ["Python", "TensorFlow", "PyTorch", "MLOps", "Statistics"],
        "skill_gaps": ["TensorFlow", "PyTorch", "MLOps"],
        "recommendations": [
            {"skill": "TensorFlow", "priority": "high", "resources": ["Coursera", "Udacity"]},
            {"skill": "PyTorch", "priority": "high", "resources": ["fast.ai", "PyTorch tutorials"]},
            {"skill": "MLOps", "priority": "medium", "resources": ["MLflow docs", "Kubeflow"]},
        ],
    }


# ============================================================================
# Async Fixtures
# ============================================================================

@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Markers Configuration
# ============================================================================

def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "api: API endpoint tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "langchain: LangChain related tests")
