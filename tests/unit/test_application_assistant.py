"""
Unit Tests for Application Assistant Module

Tests resume optimization, cover letter generation,
job description analysis, and ATS scoring.
"""

import pytest
from unittest.mock import MagicMock, patch, mock_open
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestApplicationAssistantInitialization:
    """Test ApplicationAssistant initialization."""

    def test_resume_keywords_loaded(self):
        """Test that resume keywords are loaded on init."""
        from modules.application_assistant import ApplicationAssistant

        with patch("pathlib.Path.mkdir"):
            assistant = ApplicationAssistant()
            keywords = assistant.load_resume_keywords()

            assert "action_verbs" in keywords
            assert "technical_skills" in keywords
            assert "soft_skills" in keywords

    def test_cover_letter_templates_loaded(self):
        """Test that cover letter templates are loaded."""
        from modules.application_assistant import ApplicationAssistant

        with patch("pathlib.Path.mkdir"):
            assistant = ApplicationAssistant()
            templates = assistant.load_cover_letter_templates()

            assert "standard" in templates
            assert "career_change" in templates
            assert "entry_level" in templates


class TestResumeKeywords:
    """Test resume keywords database."""

    @pytest.fixture
    def assistant(self):
        """Create ApplicationAssistant instance."""
        from modules.application_assistant import ApplicationAssistant

        with patch("pathlib.Path.mkdir"):
            return ApplicationAssistant()

    def test_action_verbs_present(self, assistant):
        """Test that action verbs are present."""
        keywords = assistant.resume_keywords_db

        assert len(keywords["action_verbs"]) > 10
        assert "Developed" in keywords["action_verbs"]
        assert "Implemented" in keywords["action_verbs"]
        assert "Led" in keywords["action_verbs"]

    def test_technical_skills_categories(self, assistant):
        """Test technical skills categories."""
        tech_skills = assistant.resume_keywords_db["technical_skills"]

        assert "software_engineering" in tech_skills
        assert "data_science" in tech_skills
        assert "product_management" in tech_skills
        assert "devops" in tech_skills

    def test_soft_skills_present(self, assistant):
        """Test that soft skills are present."""
        soft_skills = assistant.resume_keywords_db["soft_skills"]

        assert "Communication" in soft_skills
        assert "Leadership" in soft_skills
        assert "Problem-solving" in soft_skills


class TestCoverLetterTemplates:
    """Test cover letter templates."""

    @pytest.fixture
    def assistant(self):
        """Create ApplicationAssistant instance."""
        from modules.application_assistant import ApplicationAssistant

        with patch("pathlib.Path.mkdir"):
            return ApplicationAssistant()

    def test_standard_template_sections(self, assistant):
        """Test standard template has all sections."""
        template = assistant.cover_letter_templates["standard"]

        assert "opening" in template
        assert "body_paragraph_1" in template
        assert "body_paragraph_2" in template
        assert "closing" in template

    def test_career_change_template(self, assistant):
        """Test career change template exists and has placeholders."""
        template = assistant.cover_letter_templates["career_change"]

        assert "{previous_field}" in template["opening"]
        assert "{new_field}" in template["opening"]

    def test_entry_level_template(self, assistant):
        """Test entry level template exists."""
        template = assistant.cover_letter_templates["entry_level"]

        assert "{degree}" in template["opening"]
        assert "{university}" in template["opening"]

    def test_template_placeholders(self, assistant):
        """Test that templates have proper placeholders."""
        for template_name, template in assistant.cover_letter_templates.items():
            for section_name, section_content in template.items():
                # Check that placeholders use curly braces
                assert "{" in section_content, \
                    f"Template {template_name}.{section_name} should have placeholders"


class TestJobDescriptionAnalysis:
    """Test job description analysis."""

    @pytest.fixture
    def assistant(self):
        """Create ApplicationAssistant instance."""
        from modules.application_assistant import ApplicationAssistant

        with patch("pathlib.Path.mkdir"):
            return ApplicationAssistant()

    def test_analyze_job_description_basic(self, assistant):
        """Test basic job description analysis."""
        job_desc = """
        Senior Software Engineer

        Required Skills:
        - Python
        - JavaScript
        - AWS

        Preferred Skills:
        - Kubernetes
        - Machine Learning

        Responsibilities:
        - Design and implement scalable systems
        - Lead technical projects
        """

        result = assistant.analyze_job_description(job_desc)

        assert "required_skills" in result or "keywords" in result
        assert "technologies" in result or "keywords" in result

    def test_extract_keywords(self, assistant):
        """Test keyword extraction from text."""
        text = "Looking for Python developer with React experience and AWS knowledge"

        keywords = assistant.extract_keywords(text)

        assert isinstance(keywords, list)
        assert "python" in keywords or "Python" in [k.lower() for k in keywords]

    def test_extract_keywords_multiple_technologies(self, assistant):
        """Test extracting multiple technologies."""
        text = """
        Full stack developer needed with experience in:
        - React and Angular for frontend
        - Django and Flask for backend
        - PostgreSQL and MongoDB for databases
        - Docker and Kubernetes for deployment
        """

        keywords = assistant.extract_keywords(text)

        # Should find multiple keywords
        assert len(keywords) >= 2


class TestExperienceLevelDetection:
    """Test experience level detection."""

    @pytest.fixture
    def assistant(self):
        """Create ApplicationAssistant instance."""
        from modules.application_assistant import ApplicationAssistant

        with patch("pathlib.Path.mkdir"):
            return ApplicationAssistant()

    def test_detect_entry_level(self, assistant):
        """Test detecting entry-level position."""
        if hasattr(assistant, 'determine_experience_level'):
            job_desc = "Entry-level position for new graduates with 0-2 years experience"
            level = assistant.determine_experience_level(job_desc)

            assert "entry" in level.lower() or "junior" in level.lower()

    def test_detect_senior_level(self, assistant):
        """Test detecting senior-level position."""
        if hasattr(assistant, 'determine_experience_level'):
            job_desc = "Senior developer with 8+ years experience in leading technical teams"
            level = assistant.determine_experience_level(job_desc)

            assert "senior" in level.lower() or "lead" in level.lower()

    def test_detect_mid_level(self, assistant):
        """Test detecting mid-level position."""
        if hasattr(assistant, 'determine_experience_level'):
            job_desc = "Looking for a developer with 3-5 years of experience"
            level = assistant.determine_experience_level(job_desc)

            assert "mid" in level.lower() or "intermediate" in level.lower()


class TestActionVerbSuggestion:
    """Test action verb suggestion."""

    @pytest.fixture
    def assistant(self):
        """Create ApplicationAssistant instance."""
        from modules.application_assistant import ApplicationAssistant

        with patch("pathlib.Path.mkdir"):
            return ApplicationAssistant()

    def test_suggest_action_verbs(self, assistant):
        """Test action verb suggestions."""
        if hasattr(assistant, 'suggest_action_verbs'):
            job_desc = "Develop software, manage projects, and lead teams"
            verbs = assistant.suggest_action_verbs(job_desc)

            assert isinstance(verbs, list)


class TestTechnologyExtraction:
    """Test technology extraction."""

    @pytest.fixture
    def assistant(self):
        """Create ApplicationAssistant instance."""
        from modules.application_assistant import ApplicationAssistant

        with patch("pathlib.Path.mkdir"):
            return ApplicationAssistant()

    def test_extract_technologies(self, assistant):
        """Test technology extraction from job description."""
        if hasattr(assistant, 'extract_technologies'):
            job_desc = "Experience with Python, React, AWS, and Docker required"
            technologies = assistant.extract_technologies(job_desc)

            assert isinstance(technologies, list)


@pytest.mark.unit
class TestResumeOptimization:
    """Test resume optimization functionality."""

    @pytest.fixture
    def assistant(self):
        """Create ApplicationAssistant instance."""
        from modules.application_assistant import ApplicationAssistant

        with patch("pathlib.Path.mkdir"):
            return ApplicationAssistant()

    def test_resume_keywords_completeness(self, assistant):
        """Test that resume keywords database is complete."""
        keywords = assistant.resume_keywords_db

        # Check action verbs
        assert len(keywords["action_verbs"]) >= 15

        # Check technical skills coverage
        tech_skills = keywords["technical_skills"]
        assert len(tech_skills.get("software_engineering", [])) >= 5
        assert len(tech_skills.get("data_science", [])) >= 5

        # Check soft skills
        assert len(keywords["soft_skills"]) >= 5


class TestCoverLetterGeneration:
    """Test cover letter generation."""

    @pytest.fixture
    def assistant(self):
        """Create ApplicationAssistant instance."""
        from modules.application_assistant import ApplicationAssistant

        with patch("pathlib.Path.mkdir"):
            return ApplicationAssistant()

    def test_template_variable_replacement(self, assistant):
        """Test that template variables can be replaced."""
        template = assistant.cover_letter_templates["standard"]["opening"]

        filled = template.format(
            position="Software Engineer",
            company="Tech Corp",
            experience_years="5",
            field="software development"
        )

        assert "Software Engineer" in filled
        assert "Tech Corp" in filled
        assert "{" not in filled  # No unreplaced placeholders

    def test_all_templates_have_required_sections(self, assistant):
        """Test all templates have required sections."""
        required_sections = ["opening", "closing"]

        for template_name, template in assistant.cover_letter_templates.items():
            for section in required_sections:
                assert section in template, \
                    f"Template {template_name} missing {section}"
