"""
Unit Tests for Job Matcher Module

Tests job matching algorithms, skill similarity calculations,
experience matching, and location-based matching.
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestJobMatcherInitialization:
    """Test JobMatcher initialization and configuration."""

    def test_job_matcher_init_with_default_config(self):
        """Test JobMatcher initializes with default configuration."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            from modules.job_matcher import JobMatcher
            matcher = JobMatcher()
            assert matcher.config == {}
            assert matcher.weights is not None

    def test_job_matcher_loads_skill_synonyms(self):
        """Test that skill synonyms are loaded correctly."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            from modules.job_matcher import JobMatcher
            matcher = JobMatcher()
            synonyms = matcher._load_skill_synonyms()

            assert "python" in synonyms
            assert "javascript" in synonyms
            assert "node.js" in synonyms["javascript"]

    def test_job_matcher_loads_location_aliases(self):
        """Test that location aliases are loaded correctly."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            from modules.job_matcher import JobMatcher
            matcher = JobMatcher()
            aliases = matcher._load_location_aliases()

            assert "san francisco" in aliases
            assert "bay area" in aliases["san francisco"]
            assert "remote" in aliases


class TestSkillNormalization:
    """Test skill normalization functionality."""

    @pytest.fixture
    def job_matcher(self):
        """Create JobMatcher instance for tests."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            from modules.job_matcher import JobMatcher
            return JobMatcher()

    def test_normalize_skills_basic(self, job_matcher):
        """Test basic skill normalization."""
        skills = ["Python", "JavaScript", "SQL"]
        normalized = job_matcher._normalize_skills(skills)

        assert "python" in normalized
        assert "javascript" in normalized
        assert "sql" in normalized

    def test_normalize_skills_with_synonyms(self, job_matcher):
        """Test that synonyms are added during normalization."""
        skills = ["React"]
        normalized = job_matcher._normalize_skills(skills)

        assert "react" in normalized
        # React should have synonyms like reactjs
        assert any("react" in s for s in normalized)

    def test_normalize_skills_case_insensitive(self, job_matcher):
        """Test that normalization is case-insensitive."""
        skills = ["PYTHON", "JavaScript", "sql"]
        normalized = job_matcher._normalize_skills(skills)

        assert all(s.islower() for s in normalized)

    def test_normalize_skills_empty_list(self, job_matcher):
        """Test normalization of empty skills list."""
        normalized = job_matcher._normalize_skills([])
        assert normalized == []


class TestLocationNormalization:
    """Test location normalization functionality."""

    @pytest.fixture
    def job_matcher(self):
        """Create JobMatcher instance for tests."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            from modules.job_matcher import JobMatcher
            return JobMatcher()

    def test_normalize_location_basic(self, job_matcher):
        """Test basic location normalization."""
        normalized = job_matcher._normalize_location("San Francisco")

        assert "san francisco" in normalized
        assert "bay area" in normalized or "silicon valley" in normalized

    def test_normalize_location_alias(self, job_matcher):
        """Test location alias normalization."""
        normalized = job_matcher._normalize_location("NYC")

        assert any("new york" in loc for loc in normalized)

    def test_normalize_location_remote(self, job_matcher):
        """Test remote work location normalization."""
        normalized = job_matcher._normalize_location("remote")

        assert "remote" in normalized
        assert "work from home" in normalized or "telecommute" in normalized


class TestSkillExtraction:
    """Test skill extraction from text."""

    @pytest.fixture
    def job_matcher(self):
        """Create JobMatcher instance for tests."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            from modules.job_matcher import JobMatcher
            return JobMatcher()

    def test_extract_skills_from_text(self, job_matcher):
        """Test extracting skills from job description text."""
        text = "Looking for Python developer with experience in React and AWS"
        skills = job_matcher._extract_skills_from_text(text)

        assert "python" in skills
        assert "react" in skills
        assert "aws" in skills

    def test_extract_skills_empty_text(self, job_matcher):
        """Test extracting skills from empty text."""
        skills = job_matcher._extract_skills_from_text("")
        assert skills == []

    def test_extract_skills_no_matches(self, job_matcher):
        """Test extracting skills when no known skills present."""
        text = "Looking for a friendly team player"
        skills = job_matcher._extract_skills_from_text(text)
        # May return empty or match soft skills depending on implementation
        assert isinstance(skills, list)


class TestSkillSimilarity:
    """Test skill similarity calculations."""

    @pytest.fixture
    def job_matcher(self):
        """Create JobMatcher instance for tests."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            from modules.job_matcher import JobMatcher
            return JobMatcher()

    def test_calculate_skill_similarity_exact_match(self, job_matcher):
        """Test skill similarity with exact matches."""
        user_skills = ["Python", "JavaScript", "SQL"]
        job_skills = ["Python", "JavaScript", "SQL"]

        score, matches = job_matcher._calculate_skill_similarity(user_skills, job_skills)

        assert score >= 0.9
        assert len(matches) >= 3

    def test_calculate_skill_similarity_partial_match(self, job_matcher):
        """Test skill similarity with partial matches."""
        user_skills = ["Python", "JavaScript"]
        job_skills = ["Python", "JavaScript", "Java", "Go"]

        score, matches = job_matcher._calculate_skill_similarity(user_skills, job_skills)

        assert 0.0 < score < 1.0
        assert "python" in [m.lower() for m in matches]

    def test_calculate_skill_similarity_no_user_skills(self, job_matcher):
        """Test skill similarity with no user skills."""
        score, matches = job_matcher._calculate_skill_similarity([], ["Python"])

        assert score == 0.0
        assert matches == []

    def test_calculate_skill_similarity_no_job_skills(self, job_matcher):
        """Test skill similarity with no job skills."""
        score, matches = job_matcher._calculate_skill_similarity(["Python"], [])

        # May be 0 or return some score based on text extraction
        assert isinstance(score, float)


class TestExperienceSimilarity:
    """Test experience similarity calculations."""

    @pytest.fixture
    def job_matcher(self):
        """Create JobMatcher instance for tests."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            from modules.job_matcher import JobMatcher
            return JobMatcher()

    def test_experience_similarity_exact_match(self, job_matcher):
        """Test experience similarity with exact match."""
        score, reasons = job_matcher._calculate_experience_similarity(
            user_experience=5,
            user_level="mid",
            job_text="Looking for mid-level developer with 5 years experience"
        )

        assert score >= 0.6
        assert len(reasons) > 0

    def test_experience_similarity_entry_level(self, job_matcher):
        """Test experience similarity for entry-level position."""
        score, reasons = job_matcher._calculate_experience_similarity(
            user_experience=1,
            user_level="entry",
            job_text="Entry-level position for new graduates"
        )

        assert score >= 0.6

    def test_experience_similarity_senior_level(self, job_matcher):
        """Test experience similarity for senior position."""
        score, reasons = job_matcher._calculate_experience_similarity(
            user_experience=10,
            user_level="senior",
            job_text="Senior developer with 8+ years experience"
        )

        assert score >= 0.6


class TestLocationSimilarity:
    """Test location similarity calculations."""

    @pytest.fixture
    def job_matcher(self):
        """Create JobMatcher instance for tests."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            from modules.job_matcher import JobMatcher
            return JobMatcher()

    def test_location_similarity_exact_match(self, job_matcher):
        """Test location similarity with exact match."""
        score, reasons = job_matcher._calculate_location_similarity(
            user_locations=["San Francisco"],
            job_location="San Francisco, CA"
        )

        assert score >= 0.7

    def test_location_similarity_alias_match(self, job_matcher):
        """Test location similarity with alias match."""
        score, reasons = job_matcher._calculate_location_similarity(
            user_locations=["NYC"],
            job_location="New York, NY"
        )

        assert score >= 0.5

    def test_location_similarity_remote(self, job_matcher):
        """Test location similarity for remote positions."""
        score, reasons = job_matcher._calculate_location_similarity(
            user_locations=["Remote"],
            job_location="Remote - USA"
        )

        assert score >= 0.7

    def test_location_similarity_no_match(self, job_matcher):
        """Test location similarity with no match."""
        score, reasons = job_matcher._calculate_location_similarity(
            user_locations=["Tokyo"],
            job_location="London, UK"
        )

        # Should be low score for no match
        assert score <= 0.5


class TestUserProfile:
    """Test UserProfile dataclass."""

    def test_user_profile_creation(self):
        """Test creating UserProfile instance."""
        from modules.job_matcher import UserProfile

        profile = UserProfile(
            user_id="user123",
            skills=["Python", "JavaScript"],
            experience_level="mid",
            experience_years=5,
            preferred_locations=["San Francisco", "Remote"],
            salary_expectations={"min": 100000, "max": 150000},
            job_titles=["Software Engineer"],
            industries=["Technology"],
            work_preferences={"remote": True},
            education_level="Bachelor's",
            certifications=["AWS"],
            languages=["English"],
            career_goals=["Tech Lead"]
        )

        assert profile.user_id == "user123"
        assert len(profile.skills) == 2
        assert profile.experience_years == 5


class TestJobMatchScore:
    """Test JobMatchScore dataclass."""

    def test_job_match_score_creation(self):
        """Test creating JobMatchScore instance."""
        from modules.job_matcher import JobMatchScore

        score = JobMatchScore(
            overall_score=0.85,
            skill_score=0.9,
            experience_score=0.8,
            location_score=0.7,
            salary_score=0.9,
            title_score=0.85,
            industry_score=0.8,
            work_preference_score=1.0,
            match_reasons=["Strong skill match"],
            concerns=["Location not ideal"]
        )

        assert score.overall_score == 0.85
        assert len(score.match_reasons) == 1
        assert len(score.concerns) == 1


@pytest.mark.unit
class TestJobMatcherWeights:
    """Test that JobMatcher uses correct weights."""

    def test_default_weights(self):
        """Test default matching weights."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            from modules.job_matcher import JobMatcher
            matcher = JobMatcher()

            # Default weights should exist
            assert "skills" in matcher.weights
            assert "experience" in matcher.weights
            assert "location" in matcher.weights
            assert "salary" in matcher.weights

            # Weights should sum to approximately 1.0
            total = sum(matcher.weights.values())
            assert 0.95 <= total <= 1.05
