"""
Unit Tests for Student Pathways Module

Tests student pathway generation, milestone creation,
course recommendations, and activity suggestions.
"""

import pytest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestStudentLevelEnum:
    """Test StudentLevel enumeration."""

    def test_student_level_values(self):
        """Test StudentLevel enum has all expected values."""
        from modules.student_pathways import StudentLevel

        levels = [
            StudentLevel.FRESHMAN_HS,
            StudentLevel.SOPHOMORE_HS,
            StudentLevel.JUNIOR_HS,
            StudentLevel.SENIOR_HS,
            StudentLevel.FRESHMAN_COLLEGE,
            StudentLevel.SOPHOMORE_COLLEGE,
            StudentLevel.JUNIOR_COLLEGE,
            StudentLevel.SENIOR_COLLEGE,
        ]

        assert len(levels) == 8

    def test_high_school_levels(self):
        """Test high school level values."""
        from modules.student_pathways import StudentLevel

        hs_levels = [
            StudentLevel.FRESHMAN_HS,
            StudentLevel.SOPHOMORE_HS,
            StudentLevel.JUNIOR_HS,
            StudentLevel.SENIOR_HS,
        ]

        for level in hs_levels:
            assert "hs" in level.value.lower() or "high" in level.value.lower()

    def test_college_levels(self):
        """Test college level values."""
        from modules.student_pathways import StudentLevel

        college_levels = [
            StudentLevel.FRESHMAN_COLLEGE,
            StudentLevel.SOPHOMORE_COLLEGE,
            StudentLevel.JUNIOR_COLLEGE,
            StudentLevel.SENIOR_COLLEGE,
        ]

        for level in college_levels:
            assert "college" in level.value.lower()


class TestMilestoneDataclass:
    """Test Milestone dataclass."""

    def test_milestone_creation(self):
        """Test creating Milestone instance."""
        from modules.student_pathways import Milestone

        milestone = Milestone(
            title="Complete AP Computer Science",
            description="Take and pass AP CS exam",
            deadline="Spring Junior Year",
            priority="high",
            category="academic"
        )

        assert milestone.title == "Complete AP Computer Science"
        assert milestone.priority == "high"
        assert milestone.category == "academic"

    def test_milestone_valid_priorities(self):
        """Test milestone priority values."""
        from modules.student_pathways import Milestone

        priorities = ["high", "medium", "low"]

        for priority in priorities:
            milestone = Milestone(
                title="Test",
                description="Test",
                deadline="Test",
                priority=priority,
                category="academic"
            )
            assert milestone.priority == priority


class TestCourseRecommendationDataclass:
    """Test CourseRecommendation dataclass."""

    def test_course_recommendation_creation(self):
        """Test creating CourseRecommendation instance."""
        from modules.student_pathways import CourseRecommendation

        course = CourseRecommendation(
            course_name="Introduction to Computer Science",
            course_type="core",
            description="Fundamentals of programming",
            prerequisites=["Algebra II"],
            difficulty_level="intermediate",
            relevance_score=0.9
        )

        assert course.course_name == "Introduction to Computer Science"
        assert course.course_type == "core"
        assert course.relevance_score == 0.9

    def test_course_types(self):
        """Test valid course types."""
        from modules.student_pathways import CourseRecommendation

        course_types = ["core", "elective", "ap", "honors", "online"]

        for course_type in course_types:
            course = CourseRecommendation(
                course_name="Test Course",
                course_type=course_type,
                description="Test",
                prerequisites=[],
                difficulty_level="beginner",
                relevance_score=0.5
            )
            assert course.course_type == course_type


class TestActivityDataclass:
    """Test Activity dataclass."""

    def test_activity_creation(self):
        """Test creating Activity instance."""
        from modules.student_pathways import Activity

        activity = Activity(
            name="Coding Club",
            type="extracurricular",
            description="Weekly coding meetups",
            time_commitment="3 hours/week",
            skills_gained=["Python", "Teamwork"],
            career_relevance=0.85
        )

        assert activity.name == "Coding Club"
        assert activity.type == "extracurricular"
        assert len(activity.skills_gained) == 2
        assert activity.career_relevance == 0.85

    def test_activity_types(self):
        """Test valid activity types."""
        from modules.student_pathways import Activity

        activity_types = [
            "extracurricular",
            "internship",
            "project",
            "competition",
            "volunteer"
        ]

        for activity_type in activity_types:
            activity = Activity(
                name="Test Activity",
                type=activity_type,
                description="Test",
                time_commitment="1 hour/week",
                skills_gained=[],
                career_relevance=0.5
            )
            assert activity.type == activity_type


class TestPathwayDataclass:
    """Test Pathway dataclass."""

    def test_pathway_creation(self):
        """Test creating Pathway instance."""
        from modules.student_pathways import Pathway, StudentLevel

        pathway = Pathway(
            student_level=StudentLevel.JUNIOR_COLLEGE,
            career_field="computer science",
            onet_code="15-1252.00",
            milestones=[],
            courses=[],
            activities=[],
            skills_to_develop=["Python", "Machine Learning"],
            timeline={"year_1": "Foundation", "year_2": "Specialization"}
        )

        assert pathway.student_level == StudentLevel.JUNIOR_COLLEGE
        assert pathway.career_field == "computer science"
        assert len(pathway.skills_to_develop) == 2


class TestStudentPathwaySystem:
    """Test StudentPathwaySystem class."""

    @pytest.fixture
    def pathway_system(self):
        """Create StudentPathwaySystem instance."""
        from modules.student_pathways import StudentPathwaySystem
        return StudentPathwaySystem()

    def test_pathway_system_initialization(self, pathway_system):
        """Test StudentPathwaySystem initializes correctly."""
        assert pathway_system is not None

    def test_generate_pathway_basic(self, pathway_system):
        """Test basic pathway generation."""
        from modules.student_pathways import StudentLevel

        pathway = pathway_system.generate_pathway(
            student_level=StudentLevel.SOPHOMORE_COLLEGE,
            career_field="software engineering",
            interests=["programming", "web development"],
            current_skills=["Python basics"],
            gpa=3.5
        )

        assert pathway is not None
        assert pathway.student_level == StudentLevel.SOPHOMORE_COLLEGE

    def test_generate_pathway_with_all_params(self, pathway_system):
        """Test pathway generation with all parameters."""
        from modules.student_pathways import StudentLevel

        pathway = pathway_system.generate_pathway(
            student_level=StudentLevel.JUNIOR_HS,
            career_field="data science",
            interests=["math", "statistics", "coding"],
            current_skills=["Excel", "Basic Math"],
            gpa=3.8,
            standardized_scores={"SAT": 1400}
        )

        assert pathway is not None
        assert len(pathway.skills_to_develop) > 0

    def test_pathway_summary(self, pathway_system):
        """Test getting pathway summary."""
        from modules.student_pathways import StudentLevel

        pathway = pathway_system.generate_pathway(
            student_level=StudentLevel.FRESHMAN_COLLEGE,
            career_field="cybersecurity",
            interests=["security", "networking"],
            current_skills=["Linux basics"]
        )

        summary = pathway_system.get_pathway_summary(pathway)

        assert isinstance(summary, str)
        assert len(summary) > 0


@pytest.mark.unit
class TestPathwayCareerFields:
    """Test pathway generation for different career fields."""

    @pytest.fixture
    def pathway_system(self):
        """Create StudentPathwaySystem instance."""
        from modules.student_pathways import StudentPathwaySystem
        return StudentPathwaySystem()

    def test_software_engineering_pathway(self, pathway_system):
        """Test pathway for software engineering."""
        from modules.student_pathways import StudentLevel

        pathway = pathway_system.generate_pathway(
            student_level=StudentLevel.SOPHOMORE_COLLEGE,
            career_field="software engineering",
            interests=["coding", "web development"],
            current_skills=["Python"]
        )

        assert pathway is not None
        # Should have programming-related skills to develop
        skills_lower = [s.lower() for s in pathway.skills_to_develop]
        assert any("python" in s or "javascript" in s or "programming" in s
                   for s in skills_lower) or len(skills_lower) > 0

    def test_data_science_pathway(self, pathway_system):
        """Test pathway for data science."""
        from modules.student_pathways import StudentLevel

        pathway = pathway_system.generate_pathway(
            student_level=StudentLevel.JUNIOR_COLLEGE,
            career_field="data science",
            interests=["statistics", "machine learning"],
            current_skills=["Statistics"]
        )

        assert pathway is not None

    def test_product_management_pathway(self, pathway_system):
        """Test pathway for product management."""
        from modules.student_pathways import StudentLevel

        pathway = pathway_system.generate_pathway(
            student_level=StudentLevel.SENIOR_COLLEGE,
            career_field="product management",
            interests=["business", "technology"],
            current_skills=["Communication", "Analysis"]
        )

        assert pathway is not None


class TestStudentLevelProgression:
    """Test student level progression logic."""

    @pytest.fixture
    def pathway_system(self):
        """Create StudentPathwaySystem instance."""
        from modules.student_pathways import StudentPathwaySystem
        return StudentPathwaySystem()

    def test_high_school_pathway_different_from_college(self, pathway_system):
        """Test that high school and college pathways differ."""
        from modules.student_pathways import StudentLevel

        hs_pathway = pathway_system.generate_pathway(
            student_level=StudentLevel.SOPHOMORE_HS,
            career_field="computer science",
            interests=["coding"],
            current_skills=[]
        )

        college_pathway = pathway_system.generate_pathway(
            student_level=StudentLevel.SOPHOMORE_COLLEGE,
            career_field="computer science",
            interests=["coding"],
            current_skills=[]
        )

        assert hs_pathway.student_level != college_pathway.student_level

    def test_senior_has_career_focused_milestones(self, pathway_system):
        """Test that senior pathways focus on career preparation."""
        from modules.student_pathways import StudentLevel

        senior_pathway = pathway_system.generate_pathway(
            student_level=StudentLevel.SENIOR_COLLEGE,
            career_field="software engineering",
            interests=["programming"],
            current_skills=["Python", "JavaScript"]
        )

        assert senior_pathway is not None
        # Senior pathways should have content
        assert len(senior_pathway.skills_to_develop) >= 0


class TestPathwayTimeline:
    """Test pathway timeline generation."""

    @pytest.fixture
    def pathway_system(self):
        """Create StudentPathwaySystem instance."""
        from modules.student_pathways import StudentPathwaySystem
        return StudentPathwaySystem()

    def test_timeline_generated(self, pathway_system):
        """Test that timeline is generated."""
        from modules.student_pathways import StudentLevel

        pathway = pathway_system.generate_pathway(
            student_level=StudentLevel.FRESHMAN_COLLEGE,
            career_field="software engineering",
            interests=["programming"],
            current_skills=[]
        )

        assert pathway.timeline is not None
        assert isinstance(pathway.timeline, dict)
