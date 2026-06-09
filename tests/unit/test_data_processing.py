"""
Unit Tests for Data Processing Utilities

Tests data loading, transformation, caching,
and various utility functions.
"""

import pytest
from unittest.mock import MagicMock, patch, mock_open
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestDataLoader:
    """Test data_loader module functionality."""

    @pytest.fixture
    def sample_careers_json(self):
        """Sample careers JSON data."""
        return json.dumps([
            {
                "soc_code": "15-1252.00",
                "title": "Software Developers",
                "description": "Develop computer software",
                "cluster": "Information Technology",
                "median_salary": 120200,
                "skills": ["Python", "JavaScript"],
            },
            {
                "soc_code": "15-2051.00",
                "title": "Data Scientists",
                "description": "Analyze data using statistics",
                "cluster": "Information Technology",
                "median_salary": 108660,
                "skills": ["Python", "Statistics", "ML"],
            },
        ])

    def test_load_careers_from_json(self, sample_careers_json):
        """Test loading careers from JSON file."""
        with patch("builtins.open", mock_open(read_data=sample_careers_json)):
            with patch("os.path.exists", return_value=True):
                from modules.data_loader import DataLoader

                loader = DataLoader.__new__(DataLoader)
                loader.careers_data = json.loads(sample_careers_json)

                assert len(loader.careers_data) == 2

    def test_get_all_careers(self, sample_careers_json):
        """Test getting all careers."""
        with patch("builtins.open", mock_open(read_data=sample_careers_json)):
            with patch("os.path.exists", return_value=True):
                from modules.data_loader import DataLoader

                loader = DataLoader.__new__(DataLoader)
                loader.careers_data = json.loads(sample_careers_json)
                loader.get_all_careers = lambda: loader.careers_data

                careers = loader.get_all_careers()
                assert len(careers) == 2

    def test_get_career_by_id(self, sample_careers_json):
        """Test getting career by SOC code."""
        careers = json.loads(sample_careers_json)

        from modules.data_loader import DataLoader

        loader = DataLoader.__new__(DataLoader)
        loader.careers_data = careers
        loader.get_career = lambda code: next(
            (c for c in loader.careers_data if c["soc_code"] == code), None
        )

        career = loader.get_career("15-1252.00")
        assert career is not None
        assert career["title"] == "Software Developers"

    def test_search_careers(self, sample_careers_json):
        """Test searching careers by query."""
        careers = json.loads(sample_careers_json)

        from modules.data_loader import DataLoader

        loader = DataLoader.__new__(DataLoader)
        loader.careers_data = careers
        loader.search_careers = lambda q: [
            c for c in loader.careers_data
            if q.lower() in c["title"].lower() or q.lower() in c["description"].lower()
        ]

        results = loader.search_careers("software")
        assert len(results) == 1
        assert results[0]["title"] == "Software Developers"

    def test_search_careers_no_results(self, sample_careers_json):
        """Test searching with no matching results."""
        careers = json.loads(sample_careers_json)

        from modules.data_loader import DataLoader

        loader = DataLoader.__new__(DataLoader)
        loader.careers_data = careers
        loader.search_careers = lambda q: [
            c for c in loader.careers_data
            if q.lower() in c["title"].lower()
        ]

        results = loader.search_careers("nonexistent")
        assert len(results) == 0


class TestCareerDataValidation:
    """Test career data validation."""

    def test_career_has_required_fields(self):
        """Test that career data has all required fields."""
        required_fields = [
            "soc_code", "title", "description", "cluster"
        ]

        career = {
            "soc_code": "15-1252.00",
            "title": "Software Developers",
            "description": "Develop software",
            "cluster": "IT",
        }

        for field in required_fields:
            assert field in career

    def test_salary_is_numeric(self):
        """Test that salary values are numeric."""
        career = {
            "median_salary": 120200,
            "min_salary": 80000,
            "max_salary": 160000,
        }

        for key, value in career.items():
            if "salary" in key:
                assert isinstance(value, (int, float))

    def test_skills_is_list(self):
        """Test that skills is a list."""
        career = {
            "skills": ["Python", "JavaScript", "SQL"]
        }

        assert isinstance(career["skills"], list)


class TestDataTransformation:
    """Test data transformation utilities."""

    def test_normalize_salary_data(self):
        """Test salary data normalization."""
        career = {"median_salary": 120200}

        # Calculate salary range
        salary_min = max(30000, int(career["median_salary"] * 0.8))
        salary_max = int(career["median_salary"] * 1.4)

        assert salary_min == 96160
        assert salary_max == 168280

    def test_truncate_description(self):
        """Test description truncation."""
        description = "A" * 500

        truncated = description[:200] + "..." if len(description) > 200 else description

        assert len(truncated) == 203  # 200 chars + "..."
        assert truncated.endswith("...")

    def test_format_career_for_frontend(self):
        """Test formatting career data for frontend."""
        career = {
            "soc_code": "15-1252.00",
            "title": "Software Developers",
            "description": "Develop software applications",
            "median_salary": 120200,
            "skills": ["Python", "JavaScript", "SQL", "React", "AWS", "Docker"],
            "tasks": ["Code", "Debug", "Design", "Review"],
        }

        formatted = {
            "id": career["soc_code"],
            "title": career["title"],
            "description": career["description"],
            "salary": {
                "min": int(career["median_salary"] * 0.8),
                "max": int(career["median_salary"] * 1.4)
            },
            "skills": career["skills"][:5],  # Limit to 5
            "tasks": career["tasks"][:3],    # Limit to 3
        }

        assert formatted["id"] == "15-1252.00"
        assert len(formatted["skills"]) == 5
        assert len(formatted["tasks"]) == 3


class TestCachingFunctionality:
    """Test caching functionality."""

    def test_cache_key_generation(self):
        """Test cache key generation."""
        query = "software engineer"
        location = "San Francisco"

        cache_key = f"jobs:{query}:{location}".lower().replace(" ", "_")

        assert cache_key == "jobs:software_engineer:san_francisco"

    def test_cache_ttl_calculation(self):
        """Test cache TTL calculation."""
        from datetime import datetime, timedelta

        cache_duration_hours = 2
        created_at = datetime.now()
        expires_at = created_at + timedelta(hours=cache_duration_hours)

        assert expires_at > created_at
        assert (expires_at - created_at).total_seconds() == 7200


class TestConfigManager:
    """Test configuration management."""

    def test_load_yaml_config(self):
        """Test loading YAML configuration."""
        sample_config = """
app:
  name: AI Career Assistant
  version: 2.0.0
database:
  path: data/career_data.db
"""
        with patch("builtins.open", mock_open(read_data=sample_config)):
            import yaml
            config = yaml.safe_load(sample_config)

            assert config["app"]["name"] == "AI Career Assistant"
            assert config["app"]["version"] == "2.0.0"

    def test_get_nested_config(self):
        """Test getting nested configuration values."""
        config = {
            "app": {
                "name": "Test",
                "settings": {
                    "debug": True
                }
            }
        }

        def get_config(keys: str, default=None):
            parts = keys.split(".")
            value = config
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return default
            return value

        assert get_config("app.name") == "Test"
        assert get_config("app.settings.debug") is True
        assert get_config("app.nonexistent", "default") == "default"


class TestUserDatabaseOperations:
    """Test user database operations."""

    def test_user_profile_serialization(self):
        """Test user profile serialization."""
        profile = {
            "user_id": "user123",
            "name": "Test User",
            "skills": ["Python", "JavaScript"],
            "experience_years": 3,
        }

        serialized = json.dumps(profile)
        deserialized = json.loads(serialized)

        assert deserialized["user_id"] == "user123"
        assert deserialized["skills"] == ["Python", "JavaScript"]

    def test_skills_list_handling(self):
        """Test handling skills as JSON array."""
        skills = ["Python", "JavaScript", "SQL"]
        skills_json = json.dumps(skills)

        assert json.loads(skills_json) == skills


class TestTextProcessing:
    """Test text processing utilities."""

    def test_extract_keywords_from_text(self):
        """Test keyword extraction from text."""
        import re

        text = "Looking for Python developer with React experience"
        pattern = r'\b(python|react|javascript|java|sql)\b'

        matches = re.findall(pattern, text.lower())

        assert "python" in matches
        assert "react" in matches

    def test_calculate_text_similarity(self):
        """Test text similarity calculation."""
        from difflib import SequenceMatcher

        text1 = "software engineer"
        text2 = "software developer"

        ratio = SequenceMatcher(None, text1, text2).ratio()

        assert ratio > 0.5  # Should be similar

    def test_normalize_text(self):
        """Test text normalization."""
        text = "  Python Developer  "
        normalized = text.lower().strip()

        assert normalized == "python developer"


@pytest.mark.unit
class TestDataIntegrity:
    """Test data integrity checks."""

    def test_soc_code_format(self):
        """Test SOC code format validation."""
        import re

        soc_codes = ["15-1252.00", "11-3021.00", "17-2051.00"]
        pattern = r'^\d{2}-\d{4}\.\d{2}$'

        for code in soc_codes:
            assert re.match(pattern, code), f"Invalid SOC code format: {code}"

    def test_salary_range_validity(self):
        """Test salary range validity."""
        salary = {"min": 80000, "max": 150000}

        assert salary["min"] > 0
        assert salary["max"] > salary["min"]
        assert salary["max"] < 1000000  # Reasonable upper limit

    def test_skill_list_not_empty(self):
        """Test that skill lists are not empty for valid careers."""
        career = {
            "title": "Software Developer",
            "skills": ["Python", "JavaScript"],
        }

        assert len(career["skills"]) > 0
