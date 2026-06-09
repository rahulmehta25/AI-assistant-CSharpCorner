"""
Salary Prediction Service

Predicts salary ranges based on role, location, experience, and skills.
Uses available data and AI to provide accurate compensation estimates.

Author: Career Assistant AI System
Version: 1.0.0
"""

import json
import logging
import os
import re
import statistics
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExperienceLevel(Enum):
    """Experience level classification"""
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"
    EXECUTIVE = "executive"

    def years_range(self) -> Tuple[int, int]:
        """Get years of experience range"""
        ranges = {
            self.ENTRY: (0, 1),
            self.JUNIOR: (1, 3),
            self.MID: (3, 5),
            self.SENIOR: (5, 8),
            self.LEAD: (8, 12),
            self.PRINCIPAL: (12, 18),
            self.EXECUTIVE: (15, 30)
        }
        return ranges[self]

    @classmethod
    def from_years(cls, years: int) -> 'ExperienceLevel':
        """Determine level from years of experience"""
        if years < 1:
            return cls.ENTRY
        elif years < 3:
            return cls.JUNIOR
        elif years < 5:
            return cls.MID
        elif years < 8:
            return cls.SENIOR
        elif years < 12:
            return cls.LEAD
        elif years < 18:
            return cls.PRINCIPAL
        else:
            return cls.EXECUTIVE


class CompanySize(Enum):
    """Company size classification"""
    STARTUP = "startup"  # 1-50 employees
    SMALL = "small"  # 51-200 employees
    MEDIUM = "medium"  # 201-1000 employees
    LARGE = "large"  # 1001-5000 employees
    ENTERPRISE = "enterprise"  # 5000+ employees

    def salary_multiplier(self) -> float:
        """Salary adjustment factor by company size"""
        multipliers = {
            self.STARTUP: 0.85,  # Often lower base, equity-heavy
            self.SMALL: 0.95,
            self.MEDIUM: 1.0,
            self.LARGE: 1.10,
            self.ENTERPRISE: 1.15
        }
        return multipliers[self]


@dataclass
class LocationData:
    """Location salary data"""
    city: str
    state: str
    country: str
    cost_of_living_index: float  # 100 = national average
    tech_hub_factor: float  # 1.0 = average, 1.3 = major tech hub
    remote_adjustment: float  # Factor for remote work adjustments


@dataclass
class SalaryPrediction:
    """Salary prediction result"""
    role: str
    location: str
    experience_level: ExperienceLevel
    base_salary_low: int
    base_salary_mid: int
    base_salary_high: int
    total_comp_low: int
    total_comp_mid: int
    total_comp_high: int
    currency: str = "USD"
    confidence_score: float = 0.0
    factors: Dict[str, float] = field(default_factory=dict)
    percentiles: Dict[str, int] = field(default_factory=dict)
    comparison_to_market: str = ""
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['experience_level'] = self.experience_level.value
        return data


@dataclass
class SalaryBenchmark:
    """Industry salary benchmark data"""
    role: str
    industry: str
    experience_level: ExperienceLevel
    percentile_25: int
    percentile_50: int
    percentile_75: int
    percentile_90: int
    sample_size: int
    last_updated: str


@dataclass
class CompensationPackage:
    """Full compensation package breakdown"""
    base_salary: int
    bonus_percent: float
    equity_value: int  # Estimated annual equity value
    benefits_value: int  # Annual value of benefits
    signing_bonus: int
    total_compensation: int
    notes: List[str] = field(default_factory=list)


class SalaryPredictionService:
    """
    Salary prediction and compensation intelligence service.

    Provides salary estimates based on role, location, experience,
    skills, and market data.
    """

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the salary prediction service.

        Args:
            data_dir (str): Path to data directory. Defaults to "data".
        """
        self.data_dir = Path(data_dir)
        self.salary_dir = self.data_dir / "salary_data"
        self.salary_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(__name__)

        # Load salary data
        self.base_salaries: Dict[str, Dict] = {}
        self.location_data: Dict[str, LocationData] = {}
        self.industry_multipliers: Dict[str, float] = {}
        self.skill_premiums: Dict[str, float] = {}

        # Initialize Gemini
        self.gemini_model = None
        if GEMINI_AVAILABLE:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel("gemini-2.0-flash")

        self._load_salary_data()
        self._load_location_data()
        self._load_skill_premiums()

        self.logger.info("SalaryPredictionService initialized")

    def _load_salary_data(self) -> None:
        """Load base salary data for roles"""
        salary_file = self.salary_dir / "base_salaries.json"

        if salary_file.exists():
            try:
                with open(salary_file, 'r') as f:
                    self.base_salaries = json.load(f)
                self.logger.info(f"Loaded salary data for {len(self.base_salaries)} roles")
            except Exception as e:
                self.logger.error(f"Error loading salary data: {e}")
                self._initialize_default_salaries()
        else:
            self._initialize_default_salaries()

    def _initialize_default_salaries(self) -> None:
        """Initialize with default salary data"""
        self.base_salaries = {
            # Software Engineering
            "software_engineer": {
                "entry": {"low": 70000, "mid": 85000, "high": 100000},
                "junior": {"low": 80000, "mid": 95000, "high": 115000},
                "mid": {"low": 100000, "mid": 125000, "high": 150000},
                "senior": {"low": 130000, "mid": 160000, "high": 200000},
                "lead": {"low": 160000, "mid": 190000, "high": 230000},
                "principal": {"low": 190000, "mid": 230000, "high": 280000},
                "executive": {"low": 250000, "mid": 350000, "high": 500000},
                "bonus_percent": 15,
                "equity_range": {"low": 10000, "high": 150000}
            },
            "frontend_developer": {
                "entry": {"low": 60000, "mid": 75000, "high": 90000},
                "junior": {"low": 75000, "mid": 90000, "high": 105000},
                "mid": {"low": 95000, "mid": 115000, "high": 140000},
                "senior": {"low": 120000, "mid": 150000, "high": 180000},
                "lead": {"low": 150000, "mid": 180000, "high": 220000},
                "principal": {"low": 180000, "mid": 220000, "high": 270000},
                "executive": {"low": 220000, "mid": 300000, "high": 400000},
                "bonus_percent": 12,
                "equity_range": {"low": 8000, "high": 120000}
            },
            "backend_developer": {
                "entry": {"low": 65000, "mid": 80000, "high": 95000},
                "junior": {"low": 78000, "mid": 93000, "high": 110000},
                "mid": {"low": 98000, "mid": 120000, "high": 145000},
                "senior": {"low": 125000, "mid": 155000, "high": 190000},
                "lead": {"low": 155000, "mid": 185000, "high": 225000},
                "principal": {"low": 185000, "mid": 225000, "high": 275000},
                "executive": {"low": 240000, "mid": 330000, "high": 450000},
                "bonus_percent": 14,
                "equity_range": {"low": 9000, "high": 130000}
            },
            "fullstack_developer": {
                "entry": {"low": 65000, "mid": 78000, "high": 92000},
                "junior": {"low": 77000, "mid": 92000, "high": 108000},
                "mid": {"low": 97000, "mid": 118000, "high": 142000},
                "senior": {"low": 125000, "mid": 155000, "high": 188000},
                "lead": {"low": 155000, "mid": 185000, "high": 225000},
                "principal": {"low": 185000, "mid": 225000, "high": 275000},
                "executive": {"low": 235000, "mid": 320000, "high": 430000},
                "bonus_percent": 13,
                "equity_range": {"low": 9000, "high": 125000}
            },
            # Data & ML
            "data_scientist": {
                "entry": {"low": 75000, "mid": 90000, "high": 105000},
                "junior": {"low": 90000, "mid": 108000, "high": 125000},
                "mid": {"low": 115000, "mid": 140000, "high": 165000},
                "senior": {"low": 145000, "mid": 175000, "high": 210000},
                "lead": {"low": 175000, "mid": 210000, "high": 250000},
                "principal": {"low": 210000, "mid": 260000, "high": 320000},
                "executive": {"low": 280000, "mid": 380000, "high": 550000},
                "bonus_percent": 18,
                "equity_range": {"low": 15000, "high": 180000}
            },
            "machine_learning_engineer": {
                "entry": {"low": 85000, "mid": 100000, "high": 120000},
                "junior": {"low": 100000, "mid": 120000, "high": 140000},
                "mid": {"low": 130000, "mid": 155000, "high": 185000},
                "senior": {"low": 165000, "mid": 200000, "high": 240000},
                "lead": {"low": 200000, "mid": 240000, "high": 290000},
                "principal": {"low": 240000, "mid": 300000, "high": 370000},
                "executive": {"low": 320000, "mid": 420000, "high": 600000},
                "bonus_percent": 20,
                "equity_range": {"low": 20000, "high": 250000}
            },
            "data_analyst": {
                "entry": {"low": 50000, "mid": 62000, "high": 75000},
                "junior": {"low": 60000, "mid": 72000, "high": 85000},
                "mid": {"low": 75000, "mid": 90000, "high": 108000},
                "senior": {"low": 95000, "mid": 115000, "high": 140000},
                "lead": {"low": 120000, "mid": 145000, "high": 175000},
                "principal": {"low": 150000, "mid": 180000, "high": 220000},
                "executive": {"low": 180000, "mid": 240000, "high": 320000},
                "bonus_percent": 10,
                "equity_range": {"low": 5000, "high": 80000}
            },
            "data_engineer": {
                "entry": {"low": 70000, "mid": 85000, "high": 100000},
                "junior": {"low": 85000, "mid": 100000, "high": 118000},
                "mid": {"low": 110000, "mid": 135000, "high": 160000},
                "senior": {"low": 140000, "mid": 170000, "high": 205000},
                "lead": {"low": 170000, "mid": 205000, "high": 245000},
                "principal": {"low": 205000, "mid": 250000, "high": 310000},
                "executive": {"low": 270000, "mid": 360000, "high": 480000},
                "bonus_percent": 15,
                "equity_range": {"low": 12000, "high": 160000}
            },
            # DevOps & Cloud
            "devops_engineer": {
                "entry": {"low": 70000, "mid": 85000, "high": 100000},
                "junior": {"low": 85000, "mid": 102000, "high": 120000},
                "mid": {"low": 110000, "mid": 135000, "high": 160000},
                "senior": {"low": 140000, "mid": 172000, "high": 210000},
                "lead": {"low": 175000, "mid": 210000, "high": 250000},
                "principal": {"low": 210000, "mid": 255000, "high": 310000},
                "executive": {"low": 270000, "mid": 360000, "high": 480000},
                "bonus_percent": 15,
                "equity_range": {"low": 12000, "high": 150000}
            },
            "cloud_architect": {
                "entry": {"low": 90000, "mid": 105000, "high": 125000},
                "junior": {"low": 105000, "mid": 125000, "high": 145000},
                "mid": {"low": 130000, "mid": 155000, "high": 185000},
                "senior": {"low": 165000, "mid": 195000, "high": 235000},
                "lead": {"low": 200000, "mid": 240000, "high": 290000},
                "principal": {"low": 245000, "mid": 300000, "high": 370000},
                "executive": {"low": 320000, "mid": 420000, "high": 550000},
                "bonus_percent": 18,
                "equity_range": {"low": 18000, "high": 200000}
            },
            "sre": {
                "entry": {"low": 75000, "mid": 90000, "high": 108000},
                "junior": {"low": 90000, "mid": 108000, "high": 128000},
                "mid": {"low": 115000, "mid": 140000, "high": 168000},
                "senior": {"low": 148000, "mid": 180000, "high": 218000},
                "lead": {"low": 182000, "mid": 220000, "high": 265000},
                "principal": {"low": 220000, "mid": 270000, "high": 330000},
                "executive": {"low": 290000, "mid": 380000, "high": 500000},
                "bonus_percent": 16,
                "equity_range": {"low": 15000, "high": 175000}
            },
            # Product & Design
            "product_manager": {
                "entry": {"low": 80000, "mid": 95000, "high": 115000},
                "junior": {"low": 95000, "mid": 115000, "high": 135000},
                "mid": {"low": 120000, "mid": 145000, "high": 175000},
                "senior": {"low": 150000, "mid": 180000, "high": 220000},
                "lead": {"low": 185000, "mid": 220000, "high": 270000},
                "principal": {"low": 220000, "mid": 270000, "high": 340000},
                "executive": {"low": 300000, "mid": 400000, "high": 600000},
                "bonus_percent": 20,
                "equity_range": {"low": 15000, "high": 200000}
            },
            "ux_designer": {
                "entry": {"low": 55000, "mid": 68000, "high": 82000},
                "junior": {"low": 68000, "mid": 82000, "high": 98000},
                "mid": {"low": 88000, "mid": 108000, "high": 130000},
                "senior": {"low": 115000, "mid": 140000, "high": 172000},
                "lead": {"low": 145000, "mid": 175000, "high": 215000},
                "principal": {"low": 175000, "mid": 215000, "high": 265000},
                "executive": {"low": 220000, "mid": 300000, "high": 420000},
                "bonus_percent": 12,
                "equity_range": {"low": 8000, "high": 100000}
            },
            # Security
            "security_engineer": {
                "entry": {"low": 75000, "mid": 90000, "high": 108000},
                "junior": {"low": 90000, "mid": 108000, "high": 128000},
                "mid": {"low": 118000, "mid": 145000, "high": 175000},
                "senior": {"low": 152000, "mid": 185000, "high": 225000},
                "lead": {"low": 190000, "mid": 230000, "high": 280000},
                "principal": {"low": 235000, "mid": 285000, "high": 350000},
                "executive": {"low": 300000, "mid": 400000, "high": 550000},
                "bonus_percent": 16,
                "equity_range": {"low": 15000, "high": 180000}
            },
            # Management
            "engineering_manager": {
                "entry": {"low": 130000, "mid": 155000, "high": 185000},
                "junior": {"low": 145000, "mid": 172000, "high": 205000},
                "mid": {"low": 165000, "mid": 195000, "high": 235000},
                "senior": {"low": 190000, "mid": 230000, "high": 280000},
                "lead": {"low": 230000, "mid": 280000, "high": 340000},
                "principal": {"low": 280000, "mid": 350000, "high": 430000},
                "executive": {"low": 350000, "mid": 480000, "high": 700000},
                "bonus_percent": 25,
                "equity_range": {"low": 30000, "high": 350000}
            },
        }

        # Industry multipliers
        self.industry_multipliers = {
            "big_tech": 1.30,  # FAANG, etc.
            "finance": 1.25,
            "fintech": 1.20,
            "healthcare_tech": 1.10,
            "enterprise": 1.05,
            "consulting": 1.10,
            "startup_funded": 0.95,  # Often equity-heavy
            "startup_early": 0.85,
            "agency": 0.90,
            "government": 0.85,
            "nonprofit": 0.75,
            "education": 0.80,
            "retail": 0.95,
        }

        self._save_salary_data()

    def _load_location_data(self) -> None:
        """Load location-based salary adjustments"""
        self.location_data = {
            # US Major Tech Hubs
            "san_francisco": LocationData("San Francisco", "CA", "USA", 180, 1.35, 0.95),
            "san_jose": LocationData("San Jose", "CA", "USA", 170, 1.32, 0.95),
            "new_york": LocationData("New York", "NY", "USA", 165, 1.28, 0.95),
            "seattle": LocationData("Seattle", "WA", "USA", 150, 1.25, 0.95),
            "los_angeles": LocationData("Los Angeles", "CA", "USA", 145, 1.15, 0.92),
            "boston": LocationData("Boston", "MA", "USA", 140, 1.18, 0.93),
            "austin": LocationData("Austin", "TX", "USA", 115, 1.12, 0.90),
            "denver": LocationData("Denver", "CO", "USA", 115, 1.08, 0.88),
            "chicago": LocationData("Chicago", "IL", "USA", 110, 1.05, 0.88),
            "atlanta": LocationData("Atlanta", "GA", "USA", 102, 1.02, 0.85),
            "miami": LocationData("Miami", "FL", "USA", 120, 1.00, 0.85),
            "dallas": LocationData("Dallas", "TX", "USA", 100, 0.98, 0.85),
            "phoenix": LocationData("Phoenix", "AZ", "USA", 95, 0.95, 0.82),
            "raleigh": LocationData("Raleigh", "NC", "USA", 98, 1.00, 0.85),
            "portland": LocationData("Portland", "OR", "USA", 125, 1.05, 0.88),

            # International
            "london": LocationData("London", "", "UK", 145, 1.20, 0.92),
            "berlin": LocationData("Berlin", "", "Germany", 110, 1.05, 0.88),
            "amsterdam": LocationData("Amsterdam", "", "Netherlands", 115, 1.08, 0.88),
            "dublin": LocationData("Dublin", "", "Ireland", 120, 1.15, 0.90),
            "toronto": LocationData("Toronto", "ON", "Canada", 110, 1.05, 0.88),
            "vancouver": LocationData("Vancouver", "BC", "Canada", 115, 1.08, 0.88),
            "sydney": LocationData("Sydney", "", "Australia", 115, 1.10, 0.88),
            "singapore": LocationData("Singapore", "", "Singapore", 120, 1.15, 0.92),
            "bangalore": LocationData("Bangalore", "", "India", 45, 0.45, 0.80),
            "tel_aviv": LocationData("Tel Aviv", "", "Israel", 105, 1.15, 0.90),

            # Remote/Default
            "remote_us": LocationData("Remote", "", "USA", 100, 1.00, 1.00),
            "remote_global": LocationData("Remote", "", "Global", 85, 0.90, 1.00),
        }

    def _load_skill_premiums(self) -> None:
        """Load skill-based salary premiums"""
        self.skill_premiums = {
            # High-demand technical skills
            "machine_learning": 0.15,
            "artificial_intelligence": 0.18,
            "deep_learning": 0.15,
            "kubernetes": 0.12,
            "aws": 0.10,
            "gcp": 0.10,
            "azure": 0.10,
            "golang": 0.12,
            "rust": 0.15,
            "scala": 0.10,
            "typescript": 0.08,
            "react": 0.06,
            "python": 0.05,
            "blockchain": 0.12,
            "web3": 0.10,
            "security": 0.12,
            "penetration_testing": 0.14,
            "system_design": 0.10,
            "distributed_systems": 0.12,
            "data_engineering": 0.10,
            "mlops": 0.12,
            "terraform": 0.08,
            "graphql": 0.06,
        }

    def _save_salary_data(self) -> None:
        """Save salary data to file"""
        salary_file = self.salary_dir / "base_salaries.json"
        with open(salary_file, 'w') as f:
            json.dump(self.base_salaries, f, indent=2)

    def predict_salary(
        self,
        role: str,
        location: str,
        years_experience: int,
        skills: Optional[List[str]] = None,
        industry: Optional[str] = None,
        company_size: Optional[CompanySize] = None,
        education: Optional[str] = None
    ) -> SalaryPrediction:
        """
        Predict salary based on role, location, and other factors.

        Args:
            role (str): Job role/title
            location (str): Location (city or 'remote')
            years_experience (int): Years of experience
            skills (Optional[List[str]]): List of skills
            industry (Optional[str]): Industry sector
            company_size (Optional[CompanySize]): Company size
            education (Optional[str]): Highest education level

        Returns:
            SalaryPrediction: Salary prediction with ranges
        """
        # Normalize role
        role_key = self._normalize_role(role)
        experience_level = ExperienceLevel.from_years(years_experience)

        # Get base salary
        base_data = self._get_base_salary(role_key, experience_level)

        # Apply adjustments
        factors = {}

        # Location adjustment
        location_key = self._normalize_location(location)
        loc_data = self.location_data.get(location_key, self.location_data["remote_us"])
        location_factor = loc_data.tech_hub_factor
        factors["location"] = location_factor

        # Industry adjustment
        industry_factor = 1.0
        if industry:
            industry_factor = self.industry_multipliers.get(industry.lower().replace(" ", "_"), 1.0)
        factors["industry"] = industry_factor

        # Company size adjustment
        size_factor = 1.0
        if company_size:
            size_factor = company_size.salary_multiplier()
        factors["company_size"] = size_factor

        # Skills premium
        skills_factor = 1.0
        if skills:
            skill_premiums = [self.skill_premiums.get(s.lower().replace(" ", "_"), 0) for s in skills]
            # Diminishing returns for multiple premium skills
            if skill_premiums:
                sorted_premiums = sorted(skill_premiums, reverse=True)
                total_premium = 0
                for i, premium in enumerate(sorted_premiums[:5]):  # Cap at 5 skills
                    total_premium += premium * (0.8 ** i)  # Each additional skill has 80% impact
                skills_factor = 1.0 + total_premium
        factors["skills"] = skills_factor

        # Education adjustment
        education_factor = 1.0
        if education:
            education_factors = {
                "phd": 1.10,
                "masters": 1.05,
                "bachelors": 1.0,
                "associate": 0.95,
                "bootcamp": 0.98,
                "self_taught": 0.95
            }
            education_factor = education_factors.get(education.lower().replace(" ", "_"), 1.0)
        factors["education"] = education_factor

        # Calculate adjusted salary
        total_factor = location_factor * industry_factor * size_factor * skills_factor * education_factor

        adjusted_low = int(base_data["low"] * total_factor)
        adjusted_mid = int(base_data["mid"] * total_factor)
        adjusted_high = int(base_data["high"] * total_factor)

        # Calculate total compensation
        bonus_percent = base_data.get("bonus_percent", 10) / 100
        equity_low = base_data.get("equity_range", {}).get("low", 5000)
        equity_high = base_data.get("equity_range", {}).get("high", 50000)

        total_comp_low = int(adjusted_low * (1 + bonus_percent * 0.5) + equity_low * 0.5)
        total_comp_mid = int(adjusted_mid * (1 + bonus_percent) + (equity_low + equity_high) / 2)
        total_comp_high = int(adjusted_high * (1 + bonus_percent * 1.2) + equity_high)

        # Calculate confidence
        confidence = self._calculate_confidence(role_key, location_key, skills)

        # Build percentiles
        percentiles = {
            "p25": int(adjusted_low * 0.95),
            "p50": adjusted_mid,
            "p75": int(adjusted_high * 0.95),
            "p90": int(adjusted_high * 1.10)
        }

        # Generate recommendations
        recommendations = self._generate_recommendations(
            role, skills or [], adjusted_mid, factors
        )

        # Market comparison
        comparison = self._compare_to_market(role_key, adjusted_mid, location_key)

        return SalaryPrediction(
            role=role,
            location=location,
            experience_level=experience_level,
            base_salary_low=adjusted_low,
            base_salary_mid=adjusted_mid,
            base_salary_high=adjusted_high,
            total_comp_low=total_comp_low,
            total_comp_mid=total_comp_mid,
            total_comp_high=total_comp_high,
            confidence_score=confidence,
            factors=factors,
            percentiles=percentiles,
            comparison_to_market=comparison,
            recommendations=recommendations
        )

    def _normalize_role(self, role: str) -> str:
        """Normalize role name to match database"""
        role_lower = role.lower().replace(" ", "_").replace("-", "_")

        # Direct match
        if role_lower in self.base_salaries:
            return role_lower

        # Common mappings
        mappings = {
            "swe": "software_engineer",
            "software_developer": "software_engineer",
            "developer": "software_engineer",
            "frontend": "frontend_developer",
            "frontend_engineer": "frontend_developer",
            "backend": "backend_developer",
            "backend_engineer": "backend_developer",
            "full_stack": "fullstack_developer",
            "fullstack": "fullstack_developer",
            "full_stack_developer": "fullstack_developer",
            "ml_engineer": "machine_learning_engineer",
            "mle": "machine_learning_engineer",
            "ai_engineer": "machine_learning_engineer",
            "ds": "data_scientist",
            "da": "data_analyst",
            "de": "data_engineer",
            "sre_engineer": "sre",
            "site_reliability": "sre",
            "devops": "devops_engineer",
            "cloud_engineer": "cloud_architect",
            "security": "security_engineer",
            "infosec": "security_engineer",
            "pm": "product_manager",
            "ux": "ux_designer",
            "ui_ux": "ux_designer",
            "em": "engineering_manager",
        }

        return mappings.get(role_lower, "software_engineer")

    def _normalize_location(self, location: str) -> str:
        """Normalize location name"""
        location_lower = location.lower().replace(" ", "_").replace(",", "")

        # Direct match
        if location_lower in self.location_data:
            return location_lower

        # Common mappings
        mappings = {
            "sf": "san_francisco",
            "bay_area": "san_francisco",
            "silicon_valley": "san_jose",
            "nyc": "new_york",
            "la": "los_angeles",
            "dc": "remote_us",
            "remote": "remote_us",
        }

        # Check for city name in location
        for key in self.location_data:
            if key.replace("_", " ") in location_lower:
                return key

        return mappings.get(location_lower, "remote_us")

    def _get_base_salary(self, role_key: str, level: ExperienceLevel) -> Dict:
        """Get base salary data for role and level"""
        role_data = self.base_salaries.get(role_key, self.base_salaries["software_engineer"])
        level_data = role_data.get(level.value, role_data.get("mid", {}))

        return {
            "low": level_data.get("low", 80000),
            "mid": level_data.get("mid", 100000),
            "high": level_data.get("high", 120000),
            "bonus_percent": role_data.get("bonus_percent", 10),
            "equity_range": role_data.get("equity_range", {"low": 5000, "high": 50000})
        }

    def _calculate_confidence(
        self,
        role_key: str,
        location_key: str,
        skills: Optional[List[str]]
    ) -> float:
        """Calculate prediction confidence score"""
        confidence = 0.5  # Base confidence

        # Role in database
        if role_key in self.base_salaries:
            confidence += 0.2

        # Location in database
        if location_key in self.location_data:
            confidence += 0.15

        # Skills provided
        if skills and len(skills) >= 3:
            confidence += 0.15

        return min(confidence, 0.95)

    def _generate_recommendations(
        self,
        role: str,
        skills: List[str],
        predicted_salary: int,
        factors: Dict[str, float]
    ) -> List[str]:
        """Generate salary optimization recommendations"""
        recommendations = []

        # Location optimization
        if factors.get("location", 1.0) < 1.1:
            recommendations.append(
                "Consider relocating to a major tech hub (SF, NYC, Seattle) for 15-30% higher compensation"
            )

        # Industry optimization
        if factors.get("industry", 1.0) < 1.1:
            recommendations.append(
                "Big tech and finance companies typically pay 20-30% above market rates"
            )

        # Skills optimization
        high_premium_skills = [
            ("machine learning", 0.15),
            ("kubernetes", 0.12),
            ("rust", 0.15),
            ("golang", 0.12),
            ("security", 0.12)
        ]

        skills_lower = [s.lower() for s in skills]
        for skill, premium in high_premium_skills:
            if skill not in skills_lower:
                recommendations.append(
                    f"Adding {skill} to your skillset could increase salary by ~{int(premium*100)}%"
                )
                break  # Only show one skill recommendation

        # Negotiation tip
        recommendations.append(
            f"When negotiating, aim for the 75th percentile: ${int(predicted_salary * 1.15):,}"
        )

        return recommendations[:4]  # Limit to 4 recommendations

    def _compare_to_market(self, role_key: str, salary: int, location_key: str) -> str:
        """Compare salary to market average"""
        base_data = self.base_salaries.get(role_key, {}).get("mid", {})
        base_mid = base_data.get("mid", 100000)

        ratio = salary / base_mid

        if ratio > 1.2:
            return "Well above market average (top 20%)"
        elif ratio > 1.1:
            return "Above market average (top 30%)"
        elif ratio > 0.95:
            return "At market average"
        elif ratio > 0.85:
            return "Below market average"
        else:
            return "Significantly below market average"

    def get_compensation_breakdown(
        self,
        role: str,
        base_salary: int,
        industry: str,
        company_size: CompanySize = CompanySize.MEDIUM
    ) -> CompensationPackage:
        """
        Get detailed compensation package breakdown.

        Args:
            role (str): Job role
            base_salary (int): Base salary
            industry (str): Industry
            company_size (CompanySize): Company size

        Returns:
            CompensationPackage: Full compensation breakdown
        """
        role_key = self._normalize_role(role)
        role_data = self.base_salaries.get(role_key, self.base_salaries["software_engineer"])

        # Determine bonus
        base_bonus = role_data.get("bonus_percent", 10)
        if industry in ["big_tech", "finance", "fintech"]:
            base_bonus *= 1.3
        bonus_percent = base_bonus / 100

        # Determine equity
        equity_range = role_data.get("equity_range", {"low": 5000, "high": 50000})
        if company_size == CompanySize.STARTUP:
            # Startups often give more equity
            equity_value = int((equity_range["low"] + equity_range["high"]) * 0.8)
        elif company_size == CompanySize.ENTERPRISE:
            equity_value = int(equity_range["high"] * 0.6)
        else:
            equity_value = int((equity_range["low"] + equity_range["high"]) / 2)

        # Benefits value (insurance, 401k match, etc.)
        benefits_value = int(base_salary * 0.15)  # ~15% of base

        # Signing bonus
        signing_bonus = 0
        if industry in ["big_tech", "finance"]:
            signing_bonus = int(base_salary * 0.15)
        elif company_size == CompanySize.ENTERPRISE:
            signing_bonus = int(base_salary * 0.10)

        # Calculate total
        annual_bonus = int(base_salary * bonus_percent)
        total = base_salary + annual_bonus + equity_value + benefits_value

        notes = []
        if company_size == CompanySize.STARTUP:
            notes.append("Equity value may be higher if company exits successfully")
        if industry == "big_tech":
            notes.append("RSU vesting typically over 4 years")
        if signing_bonus > 0:
            notes.append(f"Signing bonus typically paid in first paycheck")

        return CompensationPackage(
            base_salary=base_salary,
            bonus_percent=bonus_percent * 100,
            equity_value=equity_value,
            benefits_value=benefits_value,
            signing_bonus=signing_bonus,
            total_compensation=total,
            notes=notes
        )

    def get_salary_benchmarks(
        self,
        role: str,
        industry: Optional[str] = None
    ) -> List[SalaryBenchmark]:
        """
        Get salary benchmarks across experience levels.

        Args:
            role (str): Job role
            industry (Optional[str]): Industry filter

        Returns:
            List[SalaryBenchmark]: Benchmarks for each level
        """
        role_key = self._normalize_role(role)
        role_data = self.base_salaries.get(role_key, self.base_salaries["software_engineer"])

        industry_mult = 1.0
        if industry:
            industry_mult = self.industry_multipliers.get(
                industry.lower().replace(" ", "_"), 1.0
            )

        benchmarks = []
        for level in ExperienceLevel:
            level_data = role_data.get(level.value)
            if not level_data:
                continue

            benchmarks.append(SalaryBenchmark(
                role=role,
                industry=industry or "General",
                experience_level=level,
                percentile_25=int(level_data["low"] * 0.95 * industry_mult),
                percentile_50=int(level_data["mid"] * industry_mult),
                percentile_75=int(level_data["high"] * 0.98 * industry_mult),
                percentile_90=int(level_data["high"] * 1.15 * industry_mult),
                sample_size=1000,  # Placeholder
                last_updated=datetime.now().strftime("%Y-%m-%d")
            ))

        return benchmarks

    def calculate_salary_growth(
        self,
        current_salary: int,
        current_level: ExperienceLevel,
        years_forward: int = 5
    ) -> List[Dict]:
        """
        Project salary growth over time.

        Args:
            current_salary (int): Current salary
            current_level (ExperienceLevel): Current level
            years_forward (int): Years to project

        Returns:
            List[Dict]: Projected salary by year
        """
        projections = []
        salary = current_salary
        level = current_level

        # Average annual raises
        raise_rates = {
            ExperienceLevel.ENTRY: 0.10,
            ExperienceLevel.JUNIOR: 0.08,
            ExperienceLevel.MID: 0.07,
            ExperienceLevel.SENIOR: 0.05,
            ExperienceLevel.LEAD: 0.04,
            ExperienceLevel.PRINCIPAL: 0.03,
            ExperienceLevel.EXECUTIVE: 0.03,
        }

        # Promotion bumps
        promo_bumps = {
            ExperienceLevel.ENTRY: 0.15,
            ExperienceLevel.JUNIOR: 0.15,
            ExperienceLevel.MID: 0.18,
            ExperienceLevel.SENIOR: 0.20,
            ExperienceLevel.LEAD: 0.15,
            ExperienceLevel.PRINCIPAL: 0.12,
        }

        levels = list(ExperienceLevel)
        current_level_idx = levels.index(level)

        for year in range(1, years_forward + 1):
            # Apply annual raise
            raise_rate = raise_rates.get(level, 0.03)
            salary = int(salary * (1 + raise_rate))

            # Check for promotion (every 2-3 years on average)
            if year % 3 == 0 and current_level_idx < len(levels) - 1:
                current_level_idx += 1
                level = levels[current_level_idx]
                promo_bump = promo_bumps.get(levels[current_level_idx - 1], 0.10)
                salary = int(salary * (1 + promo_bump))

            projections.append({
                "year": year,
                "salary": salary,
                "level": level.value,
                "notes": f"Projected based on {raise_rate*100:.0f}% annual growth"
            })

        return projections

    def get_ai_salary_analysis(
        self,
        role: str,
        location: str,
        skills: List[str],
        years_experience: int,
        current_salary: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Get AI-powered salary analysis using GPT-4.

        Args:
            role (str): Job role
            location (str): Location
            skills (List[str]): Skills list
            years_experience (int): Years of experience
            current_salary (Optional[int]): Current salary for comparison

        Returns:
            Optional[Dict]: AI analysis or None
        """
        if not self.gemini_model:
            return None

        # Get prediction first
        prediction = self.predict_salary(role, location, years_experience, skills)

        prompt = f"""Analyze this salary situation:

Role: {role}
Location: {location}
Experience: {years_experience} years
Skills: {', '.join(skills)}
{f'Current Salary: ${current_salary:,}' if current_salary else ''}

My analysis shows:
- Predicted range: ${prediction.base_salary_low:,} - ${prediction.base_salary_high:,}
- Market position: {prediction.comparison_to_market}

Provide:
1. Assessment of their market position (2 sentences)
2. Top 3 specific actions to maximize compensation
3. Negotiation strategy for their next role
4. Realistic 3-year salary projection with milestones

Be specific with numbers and actionable advice."""

        try:
            model = genai.GenerativeModel(
                "gemini-2.0-flash",
                system_instruction="You are an expert compensation analyst and career advisor with deep knowledge of tech industry salaries."
            )
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=700,
                ),
            )

            return {
                "prediction": prediction.to_dict(),
                "ai_analysis": response.text,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"AI analysis failed: {e}")
            return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            "roles_tracked": len(self.base_salaries),
            "locations_tracked": len(self.location_data),
            "industries_tracked": len(self.industry_multipliers),
            "skill_premiums_tracked": len(self.skill_premiums)
        }


# Prompt templates
SALARY_ANALYSIS_PROMPT = """You are an expert compensation analyst. Analyze this salary situation:

**Candidate Profile:**
- Role: {role}
- Location: {location}
- Experience: {years_experience} years
- Skills: {skills}
- Current Salary: {current_salary}

**Market Data:**
- Predicted Range: {salary_low} - {salary_high}
- Market Position: {market_position}
- Key Factors: {factors}

**Required Analysis:**
1. Market Position Assessment (2-3 sentences)
2. Top 3 Actions to Maximize Compensation
3. Negotiation Strategy for Next Role
4. 3-Year Salary Projection with Milestones

**Example Analysis:**
For a Senior Software Engineer in Seattle with 6 years experience earning $155K:

1. Market Position: You're currently at the 45th percentile for your role and location. Given your experience with Kubernetes and AWS, you should be targeting the 65-75th percentile range of $175K-$195K.

2. Actions to Maximize Compensation:
   - Target FAANG or well-funded unicorns (20-30% premium over market)
   - Add machine learning to your skillset (+15% premium)
   - Consider Staff Engineer track for faster salary growth

3. Negotiation Strategy: Lead with your cloud infrastructure impact metrics. Request $190K base with 15% bonus target. Use competing offers as leverage.

4. 3-Year Projection:
   - Year 1: Senior SWE at larger company, $180K
   - Year 2: Promotion to Staff, $210K
   - Year 3: Staff Engineer established, $235K

Provide specific, actionable advice with real numbers."""

SALARY_NEGOTIATION_PROMPT = """You are an expert salary negotiator. Help with this negotiation:

**Situation:**
- Offer: {offer_amount} for {role} at {company}
- Market Rate: {market_rate_low} - {market_rate_high}
- Candidate Experience: {experience}
- Competing Offers: {competing_offers}

**Provide:**
1. Assessment of the offer quality
2. Specific counter-offer recommendation with justification
3. 3 talking points for the negotiation call
4. What to ask for if base salary is firm
5. Walk-away point recommendation

Be specific with numbers and phrases to use."""
