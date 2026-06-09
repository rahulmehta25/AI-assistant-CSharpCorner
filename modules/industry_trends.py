"""
Industry Trends Analyzer

Analyzes job market trends, emerging skills, and growing/declining roles
to provide career intelligence insights.

Author: Career Assistant AI System
Version: 1.0.0
"""

import json
import logging
import os
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrendDirection(Enum):
    """Trend direction classification"""
    RAPIDLY_GROWING = "rapidly_growing"
    GROWING = "growing"
    STABLE = "stable"
    DECLINING = "declining"
    RAPIDLY_DECLINING = "rapidly_declining"

    def growth_multiplier(self) -> float:
        """Get growth rate multiplier"""
        multipliers = {
            self.RAPIDLY_GROWING: 1.25,
            self.GROWING: 1.10,
            self.STABLE: 1.0,
            self.DECLINING: 0.90,
            self.RAPIDLY_DECLINING: 0.75
        }
        return multipliers[self]


class TimeHorizon(Enum):
    """Time horizon for trends"""
    SHORT_TERM = "short_term"   # 0-6 months
    MEDIUM_TERM = "medium_term"  # 6-18 months
    LONG_TERM = "long_term"     # 18+ months


@dataclass
class SkillTrend:
    """Trend data for a skill"""
    skill_name: str
    direction: TrendDirection
    growth_rate: float  # percentage
    demand_score: float  # 0-100
    job_postings_count: int
    salary_impact: float  # percentage premium
    emerging: bool
    industries: List[str]
    related_skills: List[str]
    time_horizon: TimeHorizon
    confidence: float

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['direction'] = self.direction.value
        data['time_horizon'] = self.time_horizon.value
        return data


@dataclass
class RoleTrend:
    """Trend data for a role/job title"""
    role_name: str
    direction: TrendDirection
    growth_rate: float
    demand_score: float
    avg_salary: int
    salary_growth: float
    job_postings_count: int
    remote_percentage: float
    top_skills: List[str]
    top_industries: List[str]
    geographic_hotspots: List[str]
    automation_risk: float  # 0-1
    ai_impact: str

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['direction'] = self.direction.value
        return data


@dataclass
class IndustryTrend:
    """Trend data for an industry"""
    industry_name: str
    direction: TrendDirection
    growth_rate: float
    hiring_velocity: str  # high, medium, low
    top_roles: List[str]
    top_skills: List[str]
    avg_salary_range: Tuple[int, int]
    remote_adoption: float
    key_trends: List[str]
    challenges: List[str]
    opportunities: List[str]

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['direction'] = self.direction.value
        return data


@dataclass
class TrendReport:
    """Comprehensive trend report"""
    generated_at: str
    time_period: str
    top_growing_skills: List[SkillTrend]
    top_declining_skills: List[SkillTrend]
    emerging_skills: List[SkillTrend]
    top_growing_roles: List[RoleTrend]
    top_declining_roles: List[RoleTrend]
    industry_insights: List[IndustryTrend]
    market_summary: str
    key_takeaways: List[str]
    predictions: List[str]


class IndustryTrendsAnalyzer:
    """
    Industry trends analyzer service.

    Analyzes job market data to identify trends in skills, roles,
    and industries for career planning.
    """

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the industry trends analyzer.

        Args:
            data_dir (str): Path to data directory. Defaults to "data".
        """
        self.data_dir = Path(data_dir)
        self.trends_dir = self.data_dir / "industry_trends"
        self.trends_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(__name__)

        # Trend data stores
        self.skill_trends: Dict[str, SkillTrend] = {}
        self.role_trends: Dict[str, RoleTrend] = {}
        self.industry_trends: Dict[str, IndustryTrend] = {}

        # Historical data for trend calculation
        self.historical_data: Dict[str, List[Dict]] = {}

        # Initialize Gemini
        self.gemini_model = None
        if GEMINI_AVAILABLE:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel("gemini-2.0-flash")

        self._load_trend_data()
        self.logger.info("IndustryTrendsAnalyzer initialized")

    def _load_trend_data(self) -> None:
        """Load trend data from files"""
        trends_file = self.trends_dir / "current_trends.json"

        if trends_file.exists():
            try:
                with open(trends_file, 'r') as f:
                    data = json.load(f)
                    self._parse_trend_data(data)
                self.logger.info("Loaded trend data")
            except Exception as e:
                self.logger.error(f"Error loading trends: {e}")
                self._initialize_default_trends()
        else:
            self._initialize_default_trends()

    def _parse_trend_data(self, data: Dict) -> None:
        """Parse trend data from dictionary"""
        for skill_data in data.get('skill_trends', []):
            trend = SkillTrend(
                skill_name=skill_data['skill_name'],
                direction=TrendDirection[skill_data['direction'].upper()],
                growth_rate=skill_data['growth_rate'],
                demand_score=skill_data['demand_score'],
                job_postings_count=skill_data['job_postings_count'],
                salary_impact=skill_data['salary_impact'],
                emerging=skill_data['emerging'],
                industries=skill_data['industries'],
                related_skills=skill_data['related_skills'],
                time_horizon=TimeHorizon[skill_data.get('time_horizon', 'medium_term').upper()],
                confidence=skill_data.get('confidence', 0.8)
            )
            self.skill_trends[trend.skill_name.lower()] = trend

        for role_data in data.get('role_trends', []):
            trend = RoleTrend(
                role_name=role_data['role_name'],
                direction=TrendDirection[role_data['direction'].upper()],
                growth_rate=role_data['growth_rate'],
                demand_score=role_data['demand_score'],
                avg_salary=role_data['avg_salary'],
                salary_growth=role_data['salary_growth'],
                job_postings_count=role_data['job_postings_count'],
                remote_percentage=role_data['remote_percentage'],
                top_skills=role_data['top_skills'],
                top_industries=role_data['top_industries'],
                geographic_hotspots=role_data['geographic_hotspots'],
                automation_risk=role_data['automation_risk'],
                ai_impact=role_data['ai_impact']
            )
            self.role_trends[trend.role_name.lower()] = trend

        for ind_data in data.get('industry_trends', []):
            trend = IndustryTrend(
                industry_name=ind_data['industry_name'],
                direction=TrendDirection[ind_data['direction'].upper()],
                growth_rate=ind_data['growth_rate'],
                hiring_velocity=ind_data['hiring_velocity'],
                top_roles=ind_data['top_roles'],
                top_skills=ind_data['top_skills'],
                avg_salary_range=tuple(ind_data['avg_salary_range']),
                remote_adoption=ind_data['remote_adoption'],
                key_trends=ind_data['key_trends'],
                challenges=ind_data['challenges'],
                opportunities=ind_data['opportunities']
            )
            self.industry_trends[trend.industry_name.lower()] = trend

    def _initialize_default_trends(self) -> None:
        """Initialize with default trend data"""
        # Skill trends
        default_skills = [
            {
                "skill_name": "Generative AI",
                "direction": "RAPIDLY_GROWING",
                "growth_rate": 450.0,
                "demand_score": 95,
                "job_postings_count": 45000,
                "salary_impact": 35.0,
                "emerging": True,
                "industries": ["Technology", "Finance", "Healthcare", "Media"],
                "related_skills": ["LLMs", "Prompt Engineering", "Python", "ML"],
                "time_horizon": "SHORT_TERM",
                "confidence": 0.95
            },
            {
                "skill_name": "LLMs",
                "direction": "RAPIDLY_GROWING",
                "growth_rate": 380.0,
                "demand_score": 92,
                "job_postings_count": 35000,
                "salary_impact": 30.0,
                "emerging": True,
                "industries": ["Technology", "Finance", "Research"],
                "related_skills": ["Generative AI", "NLP", "Python", "Transformers"],
                "time_horizon": "SHORT_TERM",
                "confidence": 0.92
            },
            {
                "skill_name": "Kubernetes",
                "direction": "GROWING",
                "growth_rate": 35.0,
                "demand_score": 88,
                "job_postings_count": 120000,
                "salary_impact": 18.0,
                "emerging": False,
                "industries": ["Technology", "Finance", "Healthcare"],
                "related_skills": ["Docker", "Cloud", "DevOps", "Terraform"],
                "time_horizon": "MEDIUM_TERM",
                "confidence": 0.90
            },
            {
                "skill_name": "Rust",
                "direction": "RAPIDLY_GROWING",
                "growth_rate": 65.0,
                "demand_score": 75,
                "job_postings_count": 25000,
                "salary_impact": 22.0,
                "emerging": True,
                "industries": ["Technology", "Blockchain", "Systems"],
                "related_skills": ["Systems Programming", "C++", "WebAssembly"],
                "time_horizon": "MEDIUM_TERM",
                "confidence": 0.85
            },
            {
                "skill_name": "Python",
                "direction": "GROWING",
                "growth_rate": 18.0,
                "demand_score": 95,
                "job_postings_count": 450000,
                "salary_impact": 12.0,
                "emerging": False,
                "industries": ["All"],
                "related_skills": ["ML", "Data Science", "Django", "FastAPI"],
                "time_horizon": "LONG_TERM",
                "confidence": 0.95
            },
            {
                "skill_name": "TypeScript",
                "direction": "GROWING",
                "growth_rate": 28.0,
                "demand_score": 90,
                "job_postings_count": 200000,
                "salary_impact": 10.0,
                "emerging": False,
                "industries": ["Technology", "Finance", "E-commerce"],
                "related_skills": ["JavaScript", "React", "Node.js", "Angular"],
                "time_horizon": "MEDIUM_TERM",
                "confidence": 0.92
            },
            {
                "skill_name": "Go",
                "direction": "GROWING",
                "growth_rate": 25.0,
                "demand_score": 82,
                "job_postings_count": 80000,
                "salary_impact": 15.0,
                "emerging": False,
                "industries": ["Technology", "Cloud", "Finance"],
                "related_skills": ["Kubernetes", "Microservices", "Cloud"],
                "time_horizon": "MEDIUM_TERM",
                "confidence": 0.88
            },
            {
                "skill_name": "Terraform",
                "direction": "GROWING",
                "growth_rate": 32.0,
                "demand_score": 85,
                "job_postings_count": 95000,
                "salary_impact": 15.0,
                "emerging": False,
                "industries": ["Technology", "Finance", "Enterprise"],
                "related_skills": ["AWS", "GCP", "Azure", "IaC"],
                "time_horizon": "MEDIUM_TERM",
                "confidence": 0.90
            },
            {
                "skill_name": "Cybersecurity",
                "direction": "RAPIDLY_GROWING",
                "growth_rate": 38.0,
                "demand_score": 92,
                "job_postings_count": 180000,
                "salary_impact": 25.0,
                "emerging": False,
                "industries": ["All"],
                "related_skills": ["Cloud Security", "Penetration Testing", "Compliance"],
                "time_horizon": "LONG_TERM",
                "confidence": 0.95
            },
            {
                "skill_name": "MLOps",
                "direction": "RAPIDLY_GROWING",
                "growth_rate": 85.0,
                "demand_score": 80,
                "job_postings_count": 45000,
                "salary_impact": 20.0,
                "emerging": True,
                "industries": ["Technology", "Finance", "Healthcare"],
                "related_skills": ["ML", "DevOps", "Kubernetes", "Python"],
                "time_horizon": "MEDIUM_TERM",
                "confidence": 0.88
            },
            {
                "skill_name": "React",
                "direction": "STABLE",
                "growth_rate": 8.0,
                "demand_score": 92,
                "job_postings_count": 300000,
                "salary_impact": 8.0,
                "emerging": False,
                "industries": ["Technology", "E-commerce", "Media"],
                "related_skills": ["JavaScript", "TypeScript", "Next.js"],
                "time_horizon": "LONG_TERM",
                "confidence": 0.93
            },
            {
                "skill_name": "Angular",
                "direction": "DECLINING",
                "growth_rate": -8.0,
                "demand_score": 65,
                "job_postings_count": 80000,
                "salary_impact": 5.0,
                "emerging": False,
                "industries": ["Enterprise", "Finance"],
                "related_skills": ["TypeScript", "JavaScript", "RxJS"],
                "time_horizon": "MEDIUM_TERM",
                "confidence": 0.85
            },
            {
                "skill_name": "jQuery",
                "direction": "RAPIDLY_DECLINING",
                "growth_rate": -25.0,
                "demand_score": 35,
                "job_postings_count": 40000,
                "salary_impact": -5.0,
                "emerging": False,
                "industries": ["Legacy Enterprise"],
                "related_skills": ["JavaScript", "HTML", "CSS"],
                "time_horizon": "LONG_TERM",
                "confidence": 0.90
            },
            {
                "skill_name": "PHP",
                "direction": "DECLINING",
                "growth_rate": -12.0,
                "demand_score": 50,
                "job_postings_count": 90000,
                "salary_impact": -3.0,
                "emerging": False,
                "industries": ["Web Development", "Legacy"],
                "related_skills": ["Laravel", "WordPress", "MySQL"],
                "time_horizon": "LONG_TERM",
                "confidence": 0.85
            },
            {
                "skill_name": "Data Engineering",
                "direction": "RAPIDLY_GROWING",
                "growth_rate": 45.0,
                "demand_score": 88,
                "job_postings_count": 110000,
                "salary_impact": 18.0,
                "emerging": False,
                "industries": ["Technology", "Finance", "Healthcare", "Retail"],
                "related_skills": ["Python", "SQL", "Spark", "Airflow", "dbt"],
                "time_horizon": "MEDIUM_TERM",
                "confidence": 0.90
            }
        ]

        for skill_data in default_skills:
            trend = SkillTrend(
                skill_name=skill_data['skill_name'],
                direction=TrendDirection[skill_data['direction']],
                growth_rate=skill_data['growth_rate'],
                demand_score=skill_data['demand_score'],
                job_postings_count=skill_data['job_postings_count'],
                salary_impact=skill_data['salary_impact'],
                emerging=skill_data['emerging'],
                industries=skill_data['industries'],
                related_skills=skill_data['related_skills'],
                time_horizon=TimeHorizon[skill_data['time_horizon']],
                confidence=skill_data['confidence']
            )
            self.skill_trends[trend.skill_name.lower()] = trend

        # Role trends
        default_roles = [
            {
                "role_name": "AI/ML Engineer",
                "direction": "RAPIDLY_GROWING",
                "growth_rate": 55.0,
                "demand_score": 95,
                "avg_salary": 175000,
                "salary_growth": 12.0,
                "job_postings_count": 85000,
                "remote_percentage": 75.0,
                "top_skills": ["Python", "ML", "LLMs", "PyTorch", "TensorFlow"],
                "top_industries": ["Technology", "Finance", "Healthcare"],
                "geographic_hotspots": ["San Francisco", "Seattle", "New York", "Remote"],
                "automation_risk": 0.05,
                "ai_impact": "AI augments and expands this role significantly"
            },
            {
                "role_name": "Platform Engineer",
                "direction": "RAPIDLY_GROWING",
                "growth_rate": 48.0,
                "demand_score": 88,
                "avg_salary": 165000,
                "salary_growth": 10.0,
                "job_postings_count": 55000,
                "remote_percentage": 70.0,
                "top_skills": ["Kubernetes", "Terraform", "Go", "Python", "Cloud"],
                "top_industries": ["Technology", "Finance"],
                "geographic_hotspots": ["San Francisco", "Seattle", "Austin"],
                "automation_risk": 0.15,
                "ai_impact": "AI tools enhance productivity in infrastructure tasks"
            },
            {
                "role_name": "Data Engineer",
                "direction": "RAPIDLY_GROWING",
                "growth_rate": 42.0,
                "demand_score": 90,
                "avg_salary": 155000,
                "salary_growth": 9.0,
                "job_postings_count": 95000,
                "remote_percentage": 65.0,
                "top_skills": ["Python", "SQL", "Spark", "Airflow", "dbt"],
                "top_industries": ["Technology", "Finance", "Healthcare", "Retail"],
                "geographic_hotspots": ["San Francisco", "New York", "Seattle"],
                "automation_risk": 0.20,
                "ai_impact": "AI assists with code generation but increases data needs"
            },
            {
                "role_name": "Security Engineer",
                "direction": "RAPIDLY_GROWING",
                "growth_rate": 35.0,
                "demand_score": 92,
                "avg_salary": 160000,
                "salary_growth": 11.0,
                "job_postings_count": 75000,
                "remote_percentage": 60.0,
                "top_skills": ["Security", "Cloud", "Python", "Networking"],
                "top_industries": ["Technology", "Finance", "Government"],
                "geographic_hotspots": ["Washington DC", "San Francisco", "New York"],
                "automation_risk": 0.10,
                "ai_impact": "AI creates new attack vectors while enabling better defense"
            },
            {
                "role_name": "Full Stack Developer",
                "direction": "STABLE",
                "growth_rate": 8.0,
                "demand_score": 85,
                "avg_salary": 135000,
                "salary_growth": 5.0,
                "job_postings_count": 180000,
                "remote_percentage": 70.0,
                "top_skills": ["JavaScript", "React", "Node.js", "TypeScript", "SQL"],
                "top_industries": ["Technology", "E-commerce", "Startups"],
                "geographic_hotspots": ["All Major Cities", "Remote"],
                "automation_risk": 0.35,
                "ai_impact": "AI coding assistants increase productivity significantly"
            },
            {
                "role_name": "Product Manager",
                "direction": "GROWING",
                "growth_rate": 15.0,
                "demand_score": 82,
                "avg_salary": 155000,
                "salary_growth": 7.0,
                "job_postings_count": 65000,
                "remote_percentage": 55.0,
                "top_skills": ["Strategy", "Analytics", "Communication", "SQL"],
                "top_industries": ["Technology", "Finance", "Healthcare"],
                "geographic_hotspots": ["San Francisco", "New York", "Seattle"],
                "automation_risk": 0.15,
                "ai_impact": "AI handles more routine analysis, PMs focus on strategy"
            },
            {
                "role_name": "DevOps Engineer",
                "direction": "STABLE",
                "growth_rate": 10.0,
                "demand_score": 80,
                "avg_salary": 145000,
                "salary_growth": 5.0,
                "job_postings_count": 85000,
                "remote_percentage": 65.0,
                "top_skills": ["Docker", "Kubernetes", "CI/CD", "AWS", "Terraform"],
                "top_industries": ["Technology", "Finance"],
                "geographic_hotspots": ["San Francisco", "Seattle", "Austin"],
                "automation_risk": 0.30,
                "ai_impact": "Evolving into Platform Engineering with more abstraction"
            },
            {
                "role_name": "QA Engineer",
                "direction": "DECLINING",
                "growth_rate": -15.0,
                "demand_score": 55,
                "avg_salary": 95000,
                "salary_growth": 2.0,
                "job_postings_count": 45000,
                "remote_percentage": 55.0,
                "top_skills": ["Testing", "Automation", "Selenium", "Python"],
                "top_industries": ["Enterprise", "Finance"],
                "geographic_hotspots": ["All Major Cities"],
                "automation_risk": 0.65,
                "ai_impact": "AI testing tools reducing need for manual QA"
            },
            {
                "role_name": "Technical Writer",
                "direction": "DECLINING",
                "growth_rate": -18.0,
                "demand_score": 45,
                "avg_salary": 85000,
                "salary_growth": 1.0,
                "job_postings_count": 25000,
                "remote_percentage": 80.0,
                "top_skills": ["Writing", "Documentation", "Technical Knowledge"],
                "top_industries": ["Technology", "Software"],
                "geographic_hotspots": ["Remote"],
                "automation_risk": 0.70,
                "ai_impact": "AI can generate documentation, reducing headcount"
            }
        ]

        for role_data in default_roles:
            trend = RoleTrend(
                role_name=role_data['role_name'],
                direction=TrendDirection[role_data['direction']],
                growth_rate=role_data['growth_rate'],
                demand_score=role_data['demand_score'],
                avg_salary=role_data['avg_salary'],
                salary_growth=role_data['salary_growth'],
                job_postings_count=role_data['job_postings_count'],
                remote_percentage=role_data['remote_percentage'],
                top_skills=role_data['top_skills'],
                top_industries=role_data['top_industries'],
                geographic_hotspots=role_data['geographic_hotspots'],
                automation_risk=role_data['automation_risk'],
                ai_impact=role_data['ai_impact']
            )
            self.role_trends[trend.role_name.lower()] = trend

        # Industry trends
        default_industries = [
            {
                "industry_name": "Artificial Intelligence",
                "direction": "RAPIDLY_GROWING",
                "growth_rate": 65.0,
                "hiring_velocity": "high",
                "top_roles": ["ML Engineer", "AI Researcher", "Data Scientist"],
                "top_skills": ["Python", "ML", "LLMs", "Deep Learning"],
                "avg_salary_range": [140000, 250000],
                "remote_adoption": 75.0,
                "key_trends": [
                    "LLM integration across products",
                    "AI agents and automation",
                    "Multimodal AI models",
                    "AI safety and alignment"
                ],
                "challenges": ["Talent shortage", "Compute costs", "Regulation"],
                "opportunities": ["New product categories", "Productivity gains", "Research breakthroughs"]
            },
            {
                "industry_name": "Cloud Computing",
                "direction": "GROWING",
                "growth_rate": 22.0,
                "hiring_velocity": "high",
                "top_roles": ["Cloud Architect", "Platform Engineer", "SRE"],
                "top_skills": ["AWS", "Kubernetes", "Terraform", "Go"],
                "avg_salary_range": [130000, 220000],
                "remote_adoption": 70.0,
                "key_trends": [
                    "Multi-cloud strategies",
                    "Serverless adoption",
                    "FinOps focus",
                    "Edge computing"
                ],
                "challenges": ["Complexity", "Cost management", "Security"],
                "opportunities": ["Enterprise migration", "New cloud services", "Sustainability"]
            },
            {
                "industry_name": "Cybersecurity",
                "direction": "RAPIDLY_GROWING",
                "growth_rate": 35.0,
                "hiring_velocity": "high",
                "top_roles": ["Security Engineer", "Security Analyst", "CISO"],
                "top_skills": ["Security", "Cloud Security", "Python", "Compliance"],
                "avg_salary_range": [120000, 200000],
                "remote_adoption": 60.0,
                "key_trends": [
                    "Zero trust adoption",
                    "AI-powered threats",
                    "Supply chain security",
                    "Compliance automation"
                ],
                "challenges": ["Talent gap", "Evolving threats", "Alert fatigue"],
                "opportunities": ["AI defense tools", "New regulations", "Enterprise spend"]
            },
            {
                "industry_name": "FinTech",
                "direction": "GROWING",
                "growth_rate": 18.0,
                "hiring_velocity": "medium",
                "top_roles": ["Backend Engineer", "Data Engineer", "Product Manager"],
                "top_skills": ["Python", "Go", "SQL", "Cloud", "ML"],
                "avg_salary_range": [140000, 230000],
                "remote_adoption": 55.0,
                "key_trends": [
                    "Embedded finance",
                    "AI in trading",
                    "Crypto/blockchain maturation",
                    "Open banking"
                ],
                "challenges": ["Regulation", "Competition", "Economic conditions"],
                "opportunities": ["B2B payments", "AI applications", "Global expansion"]
            },
            {
                "industry_name": "Healthcare Tech",
                "direction": "RAPIDLY_GROWING",
                "growth_rate": 28.0,
                "hiring_velocity": "high",
                "top_roles": ["ML Engineer", "Data Scientist", "Backend Engineer"],
                "top_skills": ["Python", "ML", "Healthcare Domain", "Cloud"],
                "avg_salary_range": [130000, 200000],
                "remote_adoption": 50.0,
                "key_trends": [
                    "AI diagnostics",
                    "Telehealth expansion",
                    "Clinical AI copilots",
                    "Drug discovery AI"
                ],
                "challenges": ["Regulation (FDA/HIPAA)", "Data privacy", "Validation"],
                "opportunities": ["AI-assisted care", "Personalized medicine", "Cost reduction"]
            }
        ]

        for ind_data in default_industries:
            trend = IndustryTrend(
                industry_name=ind_data['industry_name'],
                direction=TrendDirection[ind_data['direction']],
                growth_rate=ind_data['growth_rate'],
                hiring_velocity=ind_data['hiring_velocity'],
                top_roles=ind_data['top_roles'],
                top_skills=ind_data['top_skills'],
                avg_salary_range=tuple(ind_data['avg_salary_range']),
                remote_adoption=ind_data['remote_adoption'],
                key_trends=ind_data['key_trends'],
                challenges=ind_data['challenges'],
                opportunities=ind_data['opportunities']
            )
            self.industry_trends[trend.industry_name.lower()] = trend

        self._save_trends()

    def _save_trends(self) -> None:
        """Save current trends to file"""
        trends_file = self.trends_dir / "current_trends.json"
        data = {
            "generated_at": datetime.now().isoformat(),
            "skill_trends": [t.to_dict() for t in self.skill_trends.values()],
            "role_trends": [t.to_dict() for t in self.role_trends.values()],
            "industry_trends": [t.to_dict() for t in self.industry_trends.values()]
        }

        with open(trends_file, 'w') as f:
            json.dump(data, f, indent=2)

    def get_skill_trend(self, skill_name: str) -> Optional[SkillTrend]:
        """
        Get trend data for a skill.

        Args:
            skill_name (str): Skill name

        Returns:
            Optional[SkillTrend]: Trend data or None
        """
        return self.skill_trends.get(skill_name.lower())

    def get_role_trend(self, role_name: str) -> Optional[RoleTrend]:
        """
        Get trend data for a role.

        Args:
            role_name (str): Role name

        Returns:
            Optional[RoleTrend]: Trend data or None
        """
        return self.role_trends.get(role_name.lower())

    def get_industry_trend(self, industry_name: str) -> Optional[IndustryTrend]:
        """
        Get trend data for an industry.

        Args:
            industry_name (str): Industry name

        Returns:
            Optional[IndustryTrend]: Trend data or None
        """
        return self.industry_trends.get(industry_name.lower())

    def get_top_growing_skills(self, limit: int = 10) -> List[SkillTrend]:
        """
        Get top growing skills.

        Args:
            limit (int): Maximum results

        Returns:
            List[SkillTrend]: Top growing skills
        """
        sorted_skills = sorted(
            self.skill_trends.values(),
            key=lambda s: s.growth_rate,
            reverse=True
        )
        return sorted_skills[:limit]

    def get_emerging_skills(self, limit: int = 10) -> List[SkillTrend]:
        """
        Get emerging skills.

        Args:
            limit (int): Maximum results

        Returns:
            List[SkillTrend]: Emerging skills
        """
        emerging = [s for s in self.skill_trends.values() if s.emerging]
        return sorted(emerging, key=lambda s: s.growth_rate, reverse=True)[:limit]

    def get_declining_skills(self, limit: int = 10) -> List[SkillTrend]:
        """
        Get declining skills.

        Args:
            limit (int): Maximum results

        Returns:
            List[SkillTrend]: Declining skills
        """
        declining = [s for s in self.skill_trends.values()
                    if s.direction in [TrendDirection.DECLINING, TrendDirection.RAPIDLY_DECLINING]]
        return sorted(declining, key=lambda s: s.growth_rate)[:limit]

    def get_top_growing_roles(self, limit: int = 10) -> List[RoleTrend]:
        """
        Get top growing roles.

        Args:
            limit (int): Maximum results

        Returns:
            List[RoleTrend]: Top growing roles
        """
        sorted_roles = sorted(
            self.role_trends.values(),
            key=lambda r: r.growth_rate,
            reverse=True
        )
        return sorted_roles[:limit]

    def get_high_automation_risk_roles(self, threshold: float = 0.5) -> List[RoleTrend]:
        """
        Get roles with high automation risk.

        Args:
            threshold (float): Risk threshold (0-1)

        Returns:
            List[RoleTrend]: High-risk roles
        """
        high_risk = [r for r in self.role_trends.values() if r.automation_risk >= threshold]
        return sorted(high_risk, key=lambda r: r.automation_risk, reverse=True)

    def get_skills_for_role(self, role_name: str) -> List[SkillTrend]:
        """
        Get trending skills for a role.

        Args:
            role_name (str): Role name

        Returns:
            List[SkillTrend]: Relevant skill trends
        """
        role_trend = self.get_role_trend(role_name)
        if not role_trend:
            return []

        skill_trends = []
        for skill_name in role_trend.top_skills:
            trend = self.get_skill_trend(skill_name)
            if trend:
                skill_trends.append(trend)

        return skill_trends

    def generate_trend_report(
        self,
        focus_area: Optional[str] = None
    ) -> TrendReport:
        """
        Generate comprehensive trend report.

        Args:
            focus_area (Optional[str]): Industry or role to focus on

        Returns:
            TrendReport: Comprehensive trend report
        """
        top_growing_skills = self.get_top_growing_skills(5)
        top_declining_skills = self.get_declining_skills(3)
        emerging_skills = self.get_emerging_skills(5)
        top_growing_roles = self.get_top_growing_roles(5)
        declining_roles = [r for r in self.role_trends.values()
                         if r.direction in [TrendDirection.DECLINING, TrendDirection.RAPIDLY_DECLINING]][:3]

        # Generate summary
        summary = f"The job market shows strong growth in AI/ML (+{top_growing_skills[0].growth_rate:.0f}%) " \
                  f"and cloud technologies. Traditional roles face automation pressure while new roles emerge. " \
                  f"Remote work remains significant at 65%+ for technical roles."

        # Key takeaways
        takeaways = [
            f"AI/ML skills showing {top_growing_skills[0].growth_rate:.0f}% growth - highest demand ever",
            "Platform Engineering replacing traditional DevOps roles",
            f"Security skills commanding {top_growing_skills[0].salary_impact:.0f}%+ salary premium",
            "Full-stack development stabilizing as AI assistants boost productivity",
            "Data Engineering critical for AI/ML pipeline success"
        ]

        # Predictions
        predictions = [
            "AI will automate 30-40% of routine coding tasks by 2026",
            "MLOps/LLMOps roles will grow 100%+ over next 2 years",
            "Remote-first companies will dominate for technical roles",
            "Security roles will see continued premium as threats increase",
            "Prompt Engineering will formalize into distinct career track"
        ]

        return TrendReport(
            generated_at=datetime.now().isoformat(),
            time_period="Q1 2026",
            top_growing_skills=top_growing_skills,
            top_declining_skills=top_declining_skills,
            emerging_skills=emerging_skills,
            top_growing_roles=top_growing_roles,
            top_declining_roles=declining_roles,
            industry_insights=list(self.industry_trends.values())[:5],
            market_summary=summary,
            key_takeaways=takeaways,
            predictions=predictions
        )

    def analyze_career_against_trends(
        self,
        current_role: str,
        current_skills: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze how a career aligns with market trends.

        Args:
            current_role (str): Current role
            current_skills (List[str]): Current skills

        Returns:
            Dict: Career trend analysis
        """
        analysis = {
            "current_role_outlook": None,
            "skill_health": {
                "growing": [],
                "stable": [],
                "declining": [],
                "missing_hot_skills": []
            },
            "recommendations": [],
            "risk_assessment": "",
            "opportunities": []
        }

        # Analyze current role
        role_trend = self.get_role_trend(current_role)
        if role_trend:
            analysis["current_role_outlook"] = {
                "direction": role_trend.direction.value,
                "growth_rate": role_trend.growth_rate,
                "automation_risk": role_trend.automation_risk,
                "ai_impact": role_trend.ai_impact
            }

        # Analyze skills
        current_skills_lower = [s.lower() for s in current_skills]
        for skill_name in current_skills_lower:
            trend = self.get_skill_trend(skill_name)
            if trend:
                if trend.direction in [TrendDirection.RAPIDLY_GROWING, TrendDirection.GROWING]:
                    analysis["skill_health"]["growing"].append(skill_name)
                elif trend.direction == TrendDirection.STABLE:
                    analysis["skill_health"]["stable"].append(skill_name)
                else:
                    analysis["skill_health"]["declining"].append(skill_name)

        # Find missing hot skills
        hot_skills = self.get_top_growing_skills(10)
        for skill_trend in hot_skills:
            if skill_trend.skill_name.lower() not in current_skills_lower:
                analysis["skill_health"]["missing_hot_skills"].append(skill_trend.skill_name)

        # Generate recommendations
        if analysis["skill_health"]["declining"]:
            analysis["recommendations"].append(
                f"Update declining skills: {', '.join(analysis['skill_health']['declining'][:3])}"
            )

        if analysis["skill_health"]["missing_hot_skills"]:
            analysis["recommendations"].append(
                f"Consider learning: {', '.join(analysis['skill_health']['missing_hot_skills'][:3])}"
            )

        # Risk assessment
        if role_trend and role_trend.automation_risk > 0.5:
            analysis["risk_assessment"] = "HIGH: Role has significant automation risk. Consider upskilling or transitioning."
        elif role_trend and role_trend.direction in [TrendDirection.DECLINING, TrendDirection.RAPIDLY_DECLINING]:
            analysis["risk_assessment"] = "MEDIUM: Role is declining. Plan for transition to growing field."
        else:
            analysis["risk_assessment"] = "LOW: Role is stable or growing with manageable automation risk."

        # Opportunities
        for industry_trend in self.industry_trends.values():
            if industry_trend.direction == TrendDirection.RAPIDLY_GROWING:
                analysis["opportunities"].append(
                    f"{industry_trend.industry_name}: {industry_trend.growth_rate}% growth, "
                    f"top skills: {', '.join(industry_trend.top_skills[:3])}"
                )

        return analysis

    def get_ai_trend_analysis(self, topic: str) -> Optional[Dict]:
        """
        Get AI-powered trend analysis.

        Args:
            topic (str): Topic to analyze (skill, role, or industry)

        Returns:
            Optional[Dict]: AI analysis
        """
        if not self.gemini_model:
            return None

        prompt = f"""Analyze current and future trends for: {topic}

Consider:
1. Current market demand and trajectory
2. Impact of AI/automation
3. Salary trends and job availability
4. Related skills and roles
5. Geographic considerations
6. 12-24 month outlook

Provide:
1. Current State (2-3 sentences)
2. Key Trends (3-4 bullet points)
3. Future Outlook (12-24 months)
4. Recommendations for professionals
5. Skills to pair with this

Be specific with data points and actionable advice."""

        try:
            model = genai.GenerativeModel(
                "gemini-2.0-flash",
                system_instruction="You are a senior tech industry analyst with deep knowledge of job market trends, technology adoption, and career development."
            )
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=700,
                ),
            )

            return {
                "topic": topic,
                "analysis": response.text,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"AI analysis failed: {e}")
            return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get service statistics"""
        growing_skills = len([s for s in self.skill_trends.values()
                             if s.direction in [TrendDirection.RAPIDLY_GROWING, TrendDirection.GROWING]])
        declining_skills = len([s for s in self.skill_trends.values()
                               if s.direction in [TrendDirection.DECLINING, TrendDirection.RAPIDLY_DECLINING]])

        return {
            "total_skills_tracked": len(self.skill_trends),
            "growing_skills": growing_skills,
            "declining_skills": declining_skills,
            "total_roles_tracked": len(self.role_trends),
            "industries_tracked": len(self.industry_trends),
            "emerging_skills": len([s for s in self.skill_trends.values() if s.emerging])
        }


# Prompt templates
TREND_ANALYSIS_PROMPT = """Analyze industry trends for: {topic}

**Current Data:**
- Growth Rate: {growth_rate}%
- Demand Score: {demand_score}/100
- Job Postings: {job_postings}
- Related Skills: {related_skills}

**Analysis Required:**
1. Current Market Position (2-3 sentences with specific data)
2. Key Drivers (what's causing the trend)
3. Risks and Challenges
4. 12-24 Month Outlook
5. Actionable Recommendations (3-4 specific steps)

**Example Analysis for "Kubernetes":**

1. Current Market Position: Kubernetes maintains very high demand (88/100) with 35% year-over-year growth. 120,000+ active job postings across major platforms, with 18% salary premium for certified practitioners.

2. Key Drivers:
- Cloud-native adoption by enterprises
- Microservices architecture standardization
- Multi-cloud strategy requirements
- DevOps to Platform Engineering evolution

3. Risks and Challenges:
- Complexity driving demand for managed services
- Competition from serverless alternatives
- Learning curve for operations teams

4. 12-24 Month Outlook: Continued strong demand as enterprises complete cloud migrations. Growth may moderate to 20-25% as market matures. Platform Engineering roles absorbing pure K8s positions.

5. Recommendations:
- Obtain CKA certification for credibility
- Develop expertise in GitOps (ArgoCD, Flux)
- Learn infrastructure as code (Terraform)
- Build experience with managed K8s (EKS, GKE, AKS)

Provide equally specific analysis for the given topic."""
