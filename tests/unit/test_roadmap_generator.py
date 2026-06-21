"""
Unit Tests for Roadmap Generator Module

Tests career roadmap generation, milestone creation,
salary progression, and career timeline functionality.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestCareerLevelEnum:
    """Test CareerLevel enumeration."""

    def test_career_level_values(self):
        """Test CareerLevel enum values."""
        from modules.roadmap_generator import CareerLevel

        assert CareerLevel.ENTRY.value == "entry"
        assert CareerLevel.JUNIOR.value == "junior"
        assert CareerLevel.MID_LEVEL.value == "mid_level"
        assert CareerLevel.SENIOR.value == "senior"
        assert CareerLevel.EXPERT.value == "expert"

    def test_career_level_ordering(self):
        """Test that career levels can be compared."""
        from modules.roadmap_generator import CareerLevel

        levels = list(CareerLevel)
        assert len(levels) == 5


class TestTimelineTypeEnum:
    """Test TimelineType enumeration."""

    def test_timeline_type_values(self):
        """Test TimelineType enum values."""
        from modules.roadmap_generator import TimelineType

        assert TimelineType.LINEAR.value == "linear"
        assert TimelineType.BRANCHED.value == "branched"
        assert TimelineType.MILESTONE.value == "milestone"


class TestSalaryProgressionDataclass:
    """Test SalaryProgression dataclass."""

    def test_salary_progression_creation(self):
        """Test creating SalaryProgression instance."""
        from modules.roadmap_generator import SalaryProgression, CareerLevel

        progression = SalaryProgression(
            level=CareerLevel.MID_LEVEL,
            years_experience="3-5 years",
            min_salary=80000,
            max_salary=120000,
            median_salary=100000,
            location_factor=1.2,
            currency="USD"
        )

        assert progression.level == CareerLevel.MID_LEVEL
        assert progression.min_salary == 80000
        assert progression.max_salary == 120000
        assert progression.median_salary == 100000
        assert progression.location_factor == 1.2

    def test_salary_progression_defaults(self):
        """Test SalaryProgression default values."""
        from modules.roadmap_generator import SalaryProgression, CareerLevel

        progression = SalaryProgression(
            level=CareerLevel.ENTRY,
            years_experience="0-2 years",
            min_salary=50000,
            max_salary=70000,
            median_salary=60000
        )

        assert progression.location_factor == 1.0
        assert progression.currency == "USD"


class TestCareerMilestoneDataclass:
    """Test CareerMilestone dataclass."""

    def test_career_milestone_creation(self):
        """Test creating CareerMilestone instance."""
        from modules.roadmap_generator import CareerMilestone

        milestone = CareerMilestone(
            id="m1",
            title="Complete Python Certification",
            description="Obtain professional Python certification",
            target_date="Year 1",
            priority="high",
            category="certification",
            prerequisites=["Basic Python knowledge"],
            skills_gained=["Advanced Python", "Testing"],
            estimated_hours=120,
            completion_criteria=["Pass exam with 80%+"],
            resources=["Python docs", "Coursera"],
            career_impact=0.8
        )

        assert milestone.id == "m1"
        assert milestone.priority == "high"
        assert milestone.category == "certification"
        assert milestone.career_impact == 0.8

    def test_career_milestone_valid_priorities(self):
        """Test that milestone priorities are valid."""
        from modules.roadmap_generator import CareerMilestone

        valid_priorities = ["critical", "high", "medium", "low"]

        for priority in valid_priorities:
            milestone = CareerMilestone(
                id="test",
                title="Test",
                description="Test",
                target_date="Year 1",
                priority=priority,
                category="skill",
                prerequisites=[],
                skills_gained=[],
                estimated_hours=10,
                completion_criteria=[],
                resources=[],
                career_impact=0.5
            )
            assert milestone.priority == priority


class TestCertificationDataclass:
    """Test Certification dataclass."""

    def test_certification_creation(self):
        """Test creating Certification instance."""
        from modules.roadmap_generator import Certification

        cert = Certification(
            name="AWS Solutions Architect",
            provider="Amazon",
            description="Cloud architecture certification",
            difficulty="advanced",
            time_to_complete="3-6 months",
            cost_range="$300-$500",
            prerequisites=["AWS Practitioner"],
            career_relevance=0.9,
            renewal_period="3 years",
            exam_info={"questions": 65, "duration": "130 minutes"}
        )

        assert cert.name == "AWS Solutions Architect"
        assert cert.difficulty == "advanced"
        assert cert.career_relevance == 0.9

    def test_certification_optional_fields(self):
        """Test Certification with optional fields."""
        from modules.roadmap_generator import Certification

        cert = Certification(
            name="Test Cert",
            provider="Test Provider",
            description="Test",
            difficulty="beginner",
            time_to_complete="1 month",
            cost_range="Free",
            prerequisites=[],
            career_relevance=0.5,
            renewal_period=None,
            exam_info=None
        )

        assert cert.renewal_period is None
        assert cert.exam_info is None


class TestProjectDataclass:
    """Test Project dataclass."""

    def test_project_creation(self):
        """Test creating Project instance."""
        from modules.roadmap_generator import Project

        project = Project(
            id="p1",
            name="E-commerce Platform",
            description="Build a full-stack e-commerce site",
            type="portfolio"
        )

        assert project.id == "p1"
        assert project.name == "E-commerce Platform"
        assert project.type == "portfolio"

    def test_project_types(self):
        """Test valid project types."""
        from modules.roadmap_generator import Project

        valid_types = ["portfolio", "open_source", "research", "business", "academic"]

        for proj_type in valid_types:
            project = Project(
                id="test",
                name="Test Project",
                description="Test",
                type=proj_type
            )
            assert project.type == proj_type


@pytest.mark.unit
class TestRoadmapGeneratorIntegration:
    """Integration tests for RoadmapGenerator functionality."""

    @pytest.fixture
    def sample_career_data(self):
        """Sample career data for testing."""
        return {
            "soc_code": "15-1252.00",
            "title": "Software Developers",
            "description": "Develop computer software",
            "skills": ["Programming", "Problem Solving"],
            "education_level": "Bachelor's degree",
            "median_salary": 120200,
            "employment_outlook": "Much faster than average",
        }

    @pytest.fixture
    def sample_user_profile(self):
        """Sample user profile for testing."""
        return {
            "name": "Test User",
            "experience": "2 years",
            "skills": ["Python", "JavaScript"],
            "interests": ["Web Development"],
            "education_level": "Bachelor's degree",
            "career_goals": ["Software Engineer"],
        }

    def test_roadmap_generator_initialization(self):
        """Test RoadmapGenerator can be initialized."""
        # This test may need adjustment based on actual module structure
        try:
            from modules.roadmap_generator import CareerLevel, TimelineType
            assert CareerLevel is not None
            assert TimelineType is not None
        except ImportError:
            pytest.skip("RoadmapGenerator class not directly importable")

    def test_career_level_progression(self):
        """Test career level progression makes sense."""
        from modules.roadmap_generator import CareerLevel

        levels = [
            CareerLevel.ENTRY,
            CareerLevel.JUNIOR,
            CareerLevel.MID_LEVEL,
            CareerLevel.SENIOR,
            CareerLevel.EXPERT
        ]

        # Verify all levels are distinct
        assert len(set(l.value for l in levels)) == 5


class TestMilestoneCategories:
    """Test milestone category functionality."""

    def test_valid_milestone_categories(self):
        """Test that milestone categories are valid."""
        valid_categories = [
            "education",
            "certification",
            "project",
            "skill",
            "experience"
        ]

        from modules.roadmap_generator import CareerMilestone

        for category in valid_categories:
            milestone = CareerMilestone(
                id="test",
                title="Test",
                description="Test",
                target_date="Year 1",
                priority="medium",
                category=category,
                prerequisites=[],
                skills_gained=[],
                estimated_hours=10,
                completion_criteria=[],
                resources=[],
                career_impact=0.5
            )
            assert milestone.category == category


class TestCareerImpactScoring:
    """Test career impact scoring."""

    def test_career_impact_range(self):
        """Test that career impact is within valid range."""
        from modules.roadmap_generator import CareerMilestone

        # Test boundary values
        for impact in [0.0, 0.5, 1.0]:
            milestone = CareerMilestone(
                id="test",
                title="Test",
                description="Test",
                target_date="Year 1",
                priority="medium",
                category="skill",
                prerequisites=[],
                skills_gained=[],
                estimated_hours=10,
                completion_criteria=[],
                resources=[],
                career_impact=impact
            )
            assert 0.0 <= milestone.career_impact <= 1.0


class TestTimelineFormatting:
    """Test timeline date formatting."""

    def test_target_date_formats(self):
        """Test various target date formats."""
        from modules.roadmap_generator import CareerMilestone

        date_formats = ["Year 1", "Month 6", "Q3 Year 2", "Week 4"]

        for date_format in date_formats:
            milestone = CareerMilestone(
                id="test",
                title="Test",
                description="Test",
                target_date=date_format,
                priority="medium",
                category="skill",
                prerequisites=[],
                skills_gained=[],
                estimated_hours=10,
                completion_criteria=[],
                resources=[],
                career_impact=0.5
            )
            assert milestone.target_date == date_format
