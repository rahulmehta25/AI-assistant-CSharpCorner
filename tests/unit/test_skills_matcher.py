"""
Unit Tests for Skills Matcher Module

Tests skill matching, job match scoring, skill normalization,
and skills database operations.
"""

import pytest
from unittest.mock import MagicMock, patch, mock_open
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestSkillsMatcherInitialization:
    """Test SkillsMatcher initialization."""

    def test_skills_matcher_creates_default_db(self, tmp_path):
        """Test that SkillsMatcher creates default DB when file doesn't exist."""
        with patch("modules.skills_matcher.Path") as mock_path:
            mock_path_instance = MagicMock()
            mock_path.return_value = mock_path_instance
            mock_path_instance.exists.return_value = False
            mock_path_instance.parent.mkdir = MagicMock()

            with patch("builtins.open", mock_open()):
                from modules.skills_matcher import SkillsMatcher
                matcher = SkillsMatcher(str(tmp_path / "skills.json"))

                db = matcher.create_default_skills_db()
                assert "programming_languages" in db
                assert "frameworks" in db
                assert "cloud_platforms" in db

    def test_default_skills_db_structure(self):
        """Test default skills database has correct structure."""
        from modules.skills_matcher import SkillsMatcher

        with patch.object(SkillsMatcher, 'load_skills_database', return_value={}):
            matcher = SkillsMatcher.__new__(SkillsMatcher)
            db = matcher.create_default_skills_db()

            # Check categories
            assert "programming_languages" in db
            assert "frameworks" in db
            assert "cloud_platforms" in db
            assert "databases" in db
            assert "data_science" in db
            assert "soft_skills" in db
            assert "tools" in db

    def test_default_skills_db_content(self):
        """Test default skills database has expected skills."""
        from modules.skills_matcher import SkillsMatcher

        with patch.object(SkillsMatcher, 'load_skills_database', return_value={}):
            matcher = SkillsMatcher.__new__(SkillsMatcher)
            db = matcher.create_default_skills_db()

            # Check programming languages
            assert "Python" in db["programming_languages"]
            assert "JavaScript" in db["programming_languages"]
            assert "SQL" in db["programming_languages"]

            # Check frameworks
            assert "React" in db["frameworks"]
            assert "Django" in db["frameworks"]

            # Check cloud platforms
            assert "AWS" in db["cloud_platforms"]
            assert "Docker" in db["cloud_platforms"]


class TestSkillOrganization:
    """Test skill organization by category."""

    @pytest.fixture
    def matcher_with_db(self):
        """Create SkillsMatcher with mock database."""
        from modules.skills_matcher import SkillsMatcher

        mock_db = {
            "programming_languages": {
                "Python": {"category": "programming", "difficulty": "medium", "demand": "very_high"},
                "JavaScript": {"category": "programming", "difficulty": "medium", "demand": "very_high"},
            },
            "frameworks": {
                "React": {"category": "frontend", "difficulty": "medium", "demand": "very_high"},
                "Django": {"category": "backend", "difficulty": "medium", "demand": "high"},
            }
        }

        with patch.object(SkillsMatcher, 'load_skills_database', return_value=mock_db):
            matcher = SkillsMatcher.__new__(SkillsMatcher)
            matcher.skills_db = mock_db
            matcher.skill_categories = matcher.organize_skills_by_category()
            return matcher

    def test_organize_skills_by_category(self, matcher_with_db):
        """Test skills are organized by category correctly."""
        categories = matcher_with_db.skill_categories

        assert "programming" in categories
        assert "frontend" in categories
        assert "backend" in categories

        assert "Python" in categories["programming"]
        assert "React" in categories["frontend"]


class TestJobMatchScoring:
    """Test job match score calculation."""

    @pytest.fixture
    def mock_matcher(self):
        """Create SkillsMatcher with mocked methods."""
        from modules.skills_matcher import SkillsMatcher

        mock_db = {
            "programming_languages": {
                "Python": {"category": "programming", "difficulty": "medium", "demand": "very_high"},
            }
        }

        with patch.object(SkillsMatcher, 'load_skills_database', return_value=mock_db):
            matcher = SkillsMatcher.__new__(SkillsMatcher)
            matcher.skills_db = mock_db
            matcher.skill_categories = {}
            matcher.normalize_skill = lambda x: x.lower().strip()
            matcher.calculate_similarity = lambda a, b: 1.0 if a == b else 0.5
            return matcher

    def test_calculate_job_match_exact_skills(self, mock_matcher):
        """Test job match calculation with exact skill matches."""
        user_skills = ["Python", "JavaScript", "SQL"]
        job_requirements = {
            "skills_required": ["Python", "JavaScript", "SQL"],
            "experience_level": "Mid-Level"
        }

        result = mock_matcher.calculate_job_match_score(user_skills, job_requirements)

        assert "exact_matches" in result or "match_score" in result

    def test_calculate_job_match_partial_skills(self, mock_matcher):
        """Test job match calculation with partial skill matches."""
        user_skills = ["Python", "JavaScript"]
        job_requirements = {
            "skills_required": ["Python", "JavaScript", "Go", "Kubernetes"],
            "experience_level": "Senior"
        }

        result = mock_matcher.calculate_job_match_score(user_skills, job_requirements)
        assert isinstance(result, dict)

    def test_calculate_job_match_no_skills(self, mock_matcher):
        """Test job match calculation with no user skills."""
        result = mock_matcher.calculate_job_match_score([], {"skills_required": ["Python"]})
        assert isinstance(result, dict)


class TestSkillNormalization:
    """Test skill normalization."""

    @pytest.fixture
    def matcher(self):
        """Create SkillsMatcher instance."""
        from modules.skills_matcher import SkillsMatcher

        with patch.object(SkillsMatcher, 'load_skills_database', return_value={}):
            matcher = SkillsMatcher.__new__(SkillsMatcher)
            matcher.skills_db = {}
            matcher.skill_categories = {}
            return matcher

    def test_normalize_skill_lowercase(self, matcher):
        """Test skill normalization to lowercase."""
        if hasattr(matcher, 'normalize_skill'):
            result = matcher.normalize_skill("PYTHON")
            assert result == "python" or result.islower()

    def test_normalize_skill_whitespace(self, matcher):
        """Test skill normalization strips whitespace."""
        if hasattr(matcher, 'normalize_skill'):
            result = matcher.normalize_skill("  python  ")
            assert result.strip() == result


class TestSkillSimilarity:
    """Test skill similarity calculation."""

    @pytest.fixture
    def matcher(self):
        """Create SkillsMatcher instance."""
        from modules.skills_matcher import SkillsMatcher

        with patch.object(SkillsMatcher, 'load_skills_database', return_value={}):
            matcher = SkillsMatcher.__new__(SkillsMatcher)
            matcher.skills_db = {}
            matcher.skill_categories = {}
            return matcher

    def test_calculate_similarity_exact_match(self, matcher):
        """Test similarity calculation for exact matches."""
        if hasattr(matcher, 'calculate_similarity'):
            similarity = matcher.calculate_similarity("python", "python")
            assert similarity >= 0.95

    def test_calculate_similarity_different_skills(self, matcher):
        """Test similarity calculation for different skills."""
        if hasattr(matcher, 'calculate_similarity'):
            similarity = matcher.calculate_similarity("python", "javascript")
            assert similarity < 0.5

    def test_calculate_similarity_partial_match(self, matcher):
        """Test similarity calculation for partial matches."""
        if hasattr(matcher, 'calculate_similarity'):
            similarity = matcher.calculate_similarity("javascript", "typescript")
            # These are different but related
            assert 0.3 < similarity < 0.9


class TestSkillDemand:
    """Test skill demand classification."""

    def test_skill_demand_levels(self):
        """Test that skills have valid demand levels."""
        from modules.skills_matcher import SkillsMatcher

        with patch.object(SkillsMatcher, 'load_skills_database', return_value={}):
            matcher = SkillsMatcher.__new__(SkillsMatcher)
            db = matcher.create_default_skills_db()

            valid_demands = ["very_high", "high", "medium", "low"]

            for category, skills in db.items():
                for skill_name, skill_info in skills.items():
                    assert skill_info["demand"] in valid_demands, \
                        f"Invalid demand for {skill_name}: {skill_info['demand']}"


class TestSkillDifficulty:
    """Test skill difficulty classification."""

    def test_skill_difficulty_levels(self):
        """Test that skills have valid difficulty levels."""
        from modules.skills_matcher import SkillsMatcher

        with patch.object(SkillsMatcher, 'load_skills_database', return_value={}):
            matcher = SkillsMatcher.__new__(SkillsMatcher)
            db = matcher.create_default_skills_db()

            valid_difficulties = ["easy", "medium", "hard"]

            for category, skills in db.items():
                for skill_name, skill_info in skills.items():
                    assert skill_info["difficulty"] in valid_difficulties, \
                        f"Invalid difficulty for {skill_name}: {skill_info['difficulty']}"


@pytest.mark.unit
class TestSkillCategories:
    """Test skill category organization."""

    def test_all_skills_have_category(self):
        """Test that all skills have a category assigned."""
        from modules.skills_matcher import SkillsMatcher

        with patch.object(SkillsMatcher, 'load_skills_database', return_value={}):
            matcher = SkillsMatcher.__new__(SkillsMatcher)
            db = matcher.create_default_skills_db()

            for category, skills in db.items():
                for skill_name, skill_info in skills.items():
                    assert "category" in skill_info, \
                        f"Missing category for {skill_name}"
                    assert skill_info["category"], \
                        f"Empty category for {skill_name}"

    def test_expected_categories_exist(self):
        """Test that expected skill categories exist."""
        from modules.skills_matcher import SkillsMatcher

        with patch.object(SkillsMatcher, 'load_skills_database', return_value={}):
            matcher = SkillsMatcher.__new__(SkillsMatcher)
            db = matcher.create_default_skills_db()

            expected_categories = [
                "programming_languages",
                "frameworks",
                "cloud_platforms",
                "databases",
                "data_science",
                "soft_skills",
                "tools"
            ]

            for cat in expected_categories:
                assert cat in db, f"Missing category: {cat}"
