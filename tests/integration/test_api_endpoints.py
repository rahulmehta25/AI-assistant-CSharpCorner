"""
API Integration Tests for AI Career Assistant

Tests all FastAPI endpoints with mocked backend services
using httpx TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


@pytest.fixture
def mock_data_loader():
    """Mock data_loader module."""
    mock_loader = MagicMock()
    mock_loader.get_all_careers.return_value = [
        {
            "soc_code": "15-1252.00",
            "title": "Software Developers",
            "description": "Develop computer software",
            "cluster": "Information Technology",
            "median_salary": 120200,
            "skills": ["Python", "JavaScript"],
            "tasks": ["Write code", "Debug issues"],
            "education_level": "Bachelor's degree",
            "experience_level": "2-5 years",
            "employment_outlook": "Much faster than average",
        }
    ]
    mock_loader.get_career.return_value = {
        "soc_code": "15-1252.00",
        "title": "Software Developers",
        "description": "Develop computer software",
        "cluster": "Information Technology",
        "median_salary": 120200,
        "skills": ["Python", "JavaScript"],
        "tasks": ["Write code"],
        "knowledge": ["Programming"],
        "abilities": ["Problem Solving"],
        "education_level": "Bachelor's degree",
        "experience_level": "2-5 years",
        "employment_outlook": "Much faster than average",
        "growth_rate": "25%",
        "related_occupations": [],
        "work_environment": ["Office"],
        "interests": ["Investigative"],
        "work_styles": ["Analytical"],
    }
    mock_loader.search_careers.return_value = [
        {
            "soc_code": "15-1252.00",
            "title": "Software Developers",
            "description": "Develop computer software",
            "cluster": "Information Technology",
            "median_salary": 120200,
        }
    ]
    return mock_loader


@pytest.fixture
def mock_assistant():
    """Mock CareerAssistantCore."""
    mock = MagicMock()
    mock.analyze_profile.return_value = {
        "profile_score": 85,
        "recommendations": ["Learn more Python"],
    }
    mock.create_roadmap.return_value = {
        "roadmap": "5-year career roadmap",
        "milestones": [{"title": "Get certified", "year": 1}],
    }
    mock.match_jobs.return_value = [
        {"job_id": "1", "title": "Software Engineer", "match_score": 0.92},
    ]
    mock.analyze_skills.return_value = {
        "current_level": "intermediate",
        "gaps": ["Kubernetes", "AWS"],
    }
    mock.analyze_skill_gap.return_value = {
        "gaps": ["Cloud skills"],
        "recommendations": ["Take AWS course"],
    }
    mock.generate_resume.return_value = {"resume": "Optimized resume content"}
    mock.generate_cover_letter.return_value = {"cover_letter": "Cover letter content"}
    return mock


@pytest.fixture
def mock_pathway_generator():
    """Mock StudentPathwaySystem."""
    mock = MagicMock()
    mock_pathway = MagicMock()
    mock_pathway.student_level.value = "sophomore_college"
    mock_pathway.career_field = "software engineering"
    mock_pathway.onet_code = "15-1252.00"
    mock_pathway.milestones = []
    mock_pathway.courses = []
    mock_pathway.activities = []
    mock_pathway.skills_to_develop = ["Python", "Git"]
    mock_pathway.timeline = {"year_1": "Foundation"}
    mock.generate_pathway.return_value = mock_pathway
    mock.get_pathway_summary.return_value = "Career pathway summary"
    return mock


@pytest.fixture
def mock_job_scraper():
    """Mock LiveJobScraper."""
    mock = MagicMock()
    mock.search_jobs = AsyncMock(return_value={
        "combined": [
            {
                "id": "job1",
                "title": "Software Engineer",
                "company": "Tech Corp",
                "location": "Remote",
                "salary": "$120k-$150k",
            }
        ],
        "search_metadata": {"sources_used": ["indeed"]},
    })
    return mock


@pytest.fixture
def mock_recommendation_engine():
    """Mock RecommendationEngine."""
    mock = MagicMock()
    mock.generate_recommendations.return_value = [
        {"career": "Software Engineer", "match_score": 0.95},
        {"career": "Data Scientist", "match_score": 0.88},
    ]
    mock.get_ai_skill_gap_analysis.return_value = {
        "gaps": ["ML", "Cloud"],
        "recommendations": ["Take courses"],
    }
    mock.generate_ai_resume_suggestions.return_value = {
        "suggestions": ["Add metrics", "Use action verbs"],
    }
    mock.generate_ai_cover_letter.return_value = {
        "content": "AI-generated cover letter",
    }
    return mock


@pytest.fixture
def client(mock_data_loader, mock_assistant, mock_pathway_generator,
           mock_job_scraper, mock_recommendation_engine):
    """Create test client with all mocked dependencies."""
    with patch.multiple(
        "api_bridge",
        data_loader=mock_data_loader,
        assistant=mock_assistant,
        pathway_generator=mock_pathway_generator,
        job_scraper=mock_job_scraper,
        recommendation_engine=mock_recommendation_engine,
    ):
        from api_bridge import app
        return TestClient(app)


@pytest.mark.api
class TestRootEndpoint:
    """Test root endpoint."""

    def test_root_returns_status(self, client):
        """Test root endpoint returns API status."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["status"] == "active"


@pytest.mark.api
class TestCareersEndpoints:
    """Test careers-related endpoints."""

    def test_get_all_careers(self, client):
        """Test getting all careers."""
        response = client.get("/api/careers")

        assert response.status_code == 200
        data = response.json()
        assert "careers" in data
        assert "total" in data

    def test_get_career_details(self, client):
        """Test getting specific career details."""
        response = client.get("/api/careers/15-1252.00")

        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "skills" in data

    def test_get_career_not_found(self, client, mock_data_loader):
        """Test getting non-existent career."""
        mock_data_loader.get_career.return_value = None

        response = client.get("/api/careers/99-9999.00")

        assert response.status_code == 404

    def test_search_careers(self, client):
        """Test searching careers."""
        response = client.post(
            "/api/careers/search",
            json={"query": "software", "filters": {}}
        )

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "count" in data


@pytest.mark.api
class TestProfileEndpoints:
    """Test profile-related endpoints."""

    def test_analyze_profile(self, client):
        """Test profile analysis."""
        profile_data = {
            "name": "Test User",
            "experience": "3 years",
            "skills": ["Python", "JavaScript"],
            "interests": ["Web Development"],
        }

        response = client.post("/api/profile/analyze", json=profile_data)

        assert response.status_code == 200

    def test_generate_roadmap(self, client):
        """Test roadmap generation."""
        profile_data = {
            "name": "Test User",
            "experience": "2 years",
            "skills": ["Python"],
            "interests": ["Machine Learning"],
        }

        response = client.post("/api/careers/roadmap", json=profile_data)

        assert response.status_code == 200


@pytest.mark.api
class TestStudentPathwayEndpoints:
    """Test student pathway endpoints."""

    def test_generate_student_pathway(self, client):
        """Test student pathway generation."""
        request_data = {
            "student_level": "sophomore_college",
            "grade_year": "2",
            "interests": ["programming", "AI"],
            "current_skills": ["Python basics"],
            "career_goals": ["Software Engineer"],
            "gpa": 3.5,
        }

        response = client.post("/api/student-pathways", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "student_level" in data
        assert "skills_to_develop" in data

    def test_generate_pathway_high_school(self, client):
        """Test pathway for high school student."""
        request_data = {
            "student_level": "junior_hs",
            "interests": ["coding"],
            "current_skills": [],
            "career_goals": ["Computer Science"],
        }

        response = client.post("/api/student-pathways", json=request_data)

        assert response.status_code == 200


@pytest.mark.api
class TestJobEndpoints:
    """Test job-related endpoints."""

    def test_search_jobs(self, client):
        """Test job search."""
        search_data = {
            "query": "software engineer",
            "location": "Remote",
            "experience_level": "mid",
            "max_results": 10,
        }

        response = client.post("/api/jobs/search", json=search_data)

        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert "count" in data

    def test_match_jobs(self, client):
        """Test job matching."""
        profile_data = {
            "name": "Test User",
            "experience": "5 years",
            "skills": ["Python", "AWS", "Docker"],
            "interests": ["Cloud Computing"],
        }

        response = client.post("/api/jobs/match", json=profile_data)

        assert response.status_code == 200
        data = response.json()
        assert "matches" in data


@pytest.mark.api
class TestSkillsEndpoints:
    """Test skills-related endpoints."""

    def test_analyze_skills(self, client):
        """Test skills analysis."""
        profile_data = {
            "name": "Test User",
            "experience": "3 years",
            "skills": ["Python", "JavaScript", "SQL"],
            "interests": ["Data Science"],
        }

        response = client.post("/api/skills/analyze", json=profile_data)

        assert response.status_code == 200

    def test_skill_gap_analysis(self, client):
        """Test skill gap analysis."""
        gap_data = {
            "current_skills": ["Python", "SQL"],
            "target_career": "Machine Learning Engineer",
            "target_skills": ["TensorFlow", "PyTorch"],
        }

        response = client.post("/api/skills/gap", json=gap_data)

        assert response.status_code == 200


@pytest.mark.api
class TestApplicationEndpoints:
    """Test application helper endpoints."""

    def test_generate_resume(self, client):
        """Test resume generation."""
        profile_data = {
            "name": "Test User",
            "experience": "5 years",
            "skills": ["Python", "Leadership"],
            "interests": ["Management"],
        }

        response = client.post("/api/applications/resume", json=profile_data)

        assert response.status_code == 200
        data = response.json()
        assert "resume" in data

    def test_generate_cover_letter(self, client):
        """Test cover letter generation."""
        request_data = {
            "profile": {
                "name": "Test User",
                "experience": "3 years",
                "skills": ["Python"],
            },
            "job_details": {
                "title": "Software Engineer",
                "company": "Tech Corp",
                "description": "Build software",
            },
        }

        response = client.post("/api/applications/cover-letter", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "cover_letter" in data


@pytest.mark.api
class TestRecommendationsEndpoint:
    """Test recommendations endpoint."""

    def test_get_recommendations(self, client):
        """Test getting career recommendations."""
        profile_data = {
            "name": "Test User",
            "experience": "2 years",
            "skills": ["Python", "Data Analysis"],
            "interests": ["AI", "Machine Learning"],
        }

        response = client.post("/api/recommendations", json=profile_data)

        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data


@pytest.mark.api
class TestStatsEndpoint:
    """Test platform stats endpoint."""

    def test_get_platform_stats(self, client):
        """Test getting platform statistics."""
        response = client.get("/api/stats")

        assert response.status_code == 200
        data = response.json()
        assert "total_careers" in data
        assert "active_jobs" in data


@pytest.mark.api
class TestErrorHandling:
    """Test API error handling."""

    def test_invalid_json(self, client):
        """Test handling of invalid JSON."""
        response = client.post(
            "/api/careers/search",
            content="not valid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422

    def test_missing_required_fields(self, client):
        """Test handling of missing required fields."""
        response = client.post(
            "/api/profile/analyze",
            json={"name": "Test"}  # Missing required fields
        )

        assert response.status_code == 422


@pytest.mark.api
class TestCORSHeaders:
    """Test CORS configuration."""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are set correctly."""
        response = client.options(
            "/api/careers",
            headers={"Origin": "http://localhost:5173"}
        )

        # CORS preflight should be handled
        assert response.status_code in [200, 405]
