"""
Skills Taxonomy Service

Comprehensive skill database with categories, related skills, market demand data,
and learning resources. Provides skills intelligence for career development.

Author: Career Assistant AI System
Version: 1.0.0
"""

import json
import logging
import os
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SkillCategory(Enum):
    """Skill category classification"""
    TECHNICAL = "technical"
    SOFT = "soft"
    DOMAIN = "domain"
    TOOL = "tool"
    LANGUAGE = "language"
    FRAMEWORK = "framework"
    METHODOLOGY = "methodology"
    CERTIFICATION = "certification"

    @classmethod
    def from_string(cls, value: str) -> 'SkillCategory':
        """Convert string to enum"""
        mapping = {
            "technical": cls.TECHNICAL,
            "soft": cls.SOFT,
            "domain": cls.DOMAIN,
            "tool": cls.TOOL,
            "language": cls.LANGUAGE,
            "framework": cls.FRAMEWORK,
            "methodology": cls.METHODOLOGY,
            "certification": cls.CERTIFICATION,
        }
        return mapping.get(value.lower(), cls.TECHNICAL)


class DemandLevel(Enum):
    """Market demand level for skills"""
    VERY_HIGH = "very_high"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    DECLINING = "declining"

    def to_score(self) -> float:
        """Convert to numeric score"""
        scores = {
            self.VERY_HIGH: 1.0,
            self.HIGH: 0.8,
            self.MODERATE: 0.6,
            self.LOW: 0.4,
            self.DECLINING: 0.2,
        }
        return scores[self]


@dataclass
class LearningResource:
    """Learning resource for skill development"""
    name: str
    resource_type: str  # course, book, tutorial, certification, video
    provider: str
    url: Optional[str] = None
    cost: str = "Free"
    duration: str = "Self-paced"
    level: str = "Beginner"  # Beginner, Intermediate, Advanced
    rating: float = 4.0

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class Skill:
    """Comprehensive skill data structure"""
    id: str
    name: str
    category: SkillCategory
    subcategory: str
    description: str
    demand_level: DemandLevel
    growth_rate: float  # percentage annual growth
    avg_salary_premium: float  # percentage increase in salary
    related_skills: List[str] = field(default_factory=list)
    parent_skills: List[str] = field(default_factory=list)
    child_skills: List[str] = field(default_factory=list)
    complementary_skills: List[str] = field(default_factory=list)
    industries: List[str] = field(default_factory=list)
    roles: List[str] = field(default_factory=list)
    learning_resources: List[LearningResource] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    proficiency_levels: Dict[str, str] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        """Initialize computed fields"""
        if not self.proficiency_levels:
            self.proficiency_levels = {
                "beginner": "Basic understanding, can use with guidance",
                "intermediate": "Can work independently on common tasks",
                "advanced": "Expert level, can teach others and solve complex problems",
                "expert": "Industry leader, can innovate and set best practices"
            }

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['category'] = self.category.value
        data['demand_level'] = self.demand_level.value
        data['learning_resources'] = [r.to_dict() if isinstance(r, LearningResource) else r
                                       for r in self.learning_resources]
        return data


@dataclass
class SkillMatch:
    """Result of skill matching operation"""
    skill: Skill
    match_score: float
    match_type: str  # exact, partial, related
    context: str


@dataclass
class SkillGap:
    """Identified skill gap"""
    required_skill: str
    current_level: int  # 0-5
    required_level: int  # 1-5
    gap_severity: str  # critical, important, nice_to_have
    recommended_resources: List[LearningResource] = field(default_factory=list)
    estimated_time_to_acquire: str = ""


class SkillsTaxonomyService:
    """
    Comprehensive skills taxonomy and intelligence service.

    Provides skill database, categorization, market demand analysis,
    and learning resource recommendations.
    """

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the skills taxonomy service.

        Args:
            data_dir (str): Path to data directory. Defaults to "data".
        """
        self.data_dir = Path(data_dir)
        self.skills_dir = self.data_dir / "skills_taxonomy"
        self.skills_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(__name__)

        # Skills database
        self.skills: Dict[str, Skill] = {}
        self.skill_aliases: Dict[str, str] = {}  # Maps aliases to canonical skill IDs
        self.category_index: Dict[SkillCategory, List[str]] = {cat: [] for cat in SkillCategory}
        self.industry_index: Dict[str, List[str]] = {}

        # Initialize Gemini if available
        self.gemini_model = None
        if GEMINI_AVAILABLE:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel("gemini-2.0-flash")

        self._load_skills_database()
        self._build_indices()

        self.logger.info(f"SkillsTaxonomyService initialized with {len(self.skills)} skills")

    def _load_skills_database(self) -> None:
        """Load skills from JSON database"""
        skills_file = self.skills_dir / "skills_database.json"

        if skills_file.exists():
            try:
                with open(skills_file, 'r') as f:
                    data = json.load(f)
                    for skill_data in data.get('skills', []):
                        skill = self._parse_skill(skill_data)
                        self.skills[skill.id] = skill
                        # Index aliases
                        for alias in skill_data.get('aliases', []):
                            self.skill_aliases[alias.lower()] = skill.id
                self.logger.info(f"Loaded {len(self.skills)} skills from database")
            except Exception as e:
                self.logger.error(f"Error loading skills database: {e}")
                self._initialize_default_skills()
        else:
            self._initialize_default_skills()

    def _parse_skill(self, data: Dict) -> Skill:
        """Parse skill data from dictionary"""
        learning_resources = []
        for res in data.get('learning_resources', []):
            learning_resources.append(LearningResource(
                name=res.get('name', ''),
                resource_type=res.get('resource_type', 'course'),
                provider=res.get('provider', ''),
                url=res.get('url'),
                cost=res.get('cost', 'Free'),
                duration=res.get('duration', 'Self-paced'),
                level=res.get('level', 'Beginner'),
                rating=res.get('rating', 4.0)
            ))

        return Skill(
            id=data.get('id', ''),
            name=data.get('name', ''),
            category=SkillCategory.from_string(data.get('category', 'technical')),
            subcategory=data.get('subcategory', ''),
            description=data.get('description', ''),
            demand_level=DemandLevel[data.get('demand_level', 'MODERATE').upper()],
            growth_rate=data.get('growth_rate', 0.0),
            avg_salary_premium=data.get('avg_salary_premium', 0.0),
            related_skills=data.get('related_skills', []),
            parent_skills=data.get('parent_skills', []),
            child_skills=data.get('child_skills', []),
            complementary_skills=data.get('complementary_skills', []),
            industries=data.get('industries', []),
            roles=data.get('roles', []),
            learning_resources=learning_resources,
            certifications=data.get('certifications', []),
            proficiency_levels=data.get('proficiency_levels', {}),
            keywords=data.get('keywords', []),
            last_updated=data.get('last_updated', datetime.now().isoformat())
        )

    def _initialize_default_skills(self) -> None:
        """Initialize with comprehensive default skills database"""
        default_skills = self._get_comprehensive_skills_data()

        for skill_data in default_skills:
            skill = self._parse_skill(skill_data)
            self.skills[skill.id] = skill
            for alias in skill_data.get('aliases', []):
                self.skill_aliases[alias.lower()] = skill.id

        self._save_skills_database()
        self.logger.info(f"Initialized {len(self.skills)} default skills")

    def _get_comprehensive_skills_data(self) -> List[Dict]:
        """Get comprehensive default skills data"""
        return [
            # Programming Languages
            {
                "id": "python",
                "name": "Python",
                "category": "language",
                "subcategory": "Programming Languages",
                "description": "General-purpose programming language known for readability and versatility",
                "demand_level": "VERY_HIGH",
                "growth_rate": 25.0,
                "avg_salary_premium": 15.0,
                "related_skills": ["django", "flask", "numpy", "pandas", "tensorflow"],
                "parent_skills": ["programming"],
                "child_skills": ["django", "flask", "fastapi", "numpy", "pandas"],
                "complementary_skills": ["sql", "git", "docker", "linux"],
                "industries": ["Technology", "Finance", "Healthcare", "Data Science", "AI/ML"],
                "roles": ["Software Engineer", "Data Scientist", "ML Engineer", "Backend Developer"],
                "learning_resources": [
                    {"name": "Python for Everybody", "resource_type": "course", "provider": "Coursera",
                     "url": "https://www.coursera.org/specializations/python", "cost": "Free",
                     "duration": "8 months", "level": "Beginner", "rating": 4.8},
                    {"name": "Automate the Boring Stuff", "resource_type": "book", "provider": "No Starch Press",
                     "url": "https://automatetheboringstuff.com/", "cost": "Free",
                     "duration": "Self-paced", "level": "Beginner", "rating": 4.7}
                ],
                "certifications": ["PCEP", "PCAP", "PCPP"],
                "keywords": ["python", "py", "python3", "cpython", "pypython"],
                "aliases": ["py", "python3", "python 3"]
            },
            {
                "id": "javascript",
                "name": "JavaScript",
                "category": "language",
                "subcategory": "Programming Languages",
                "description": "Dynamic programming language essential for web development",
                "demand_level": "VERY_HIGH",
                "growth_rate": 20.0,
                "avg_salary_premium": 12.0,
                "related_skills": ["typescript", "react", "nodejs", "vue", "angular"],
                "parent_skills": ["programming", "web-development"],
                "child_skills": ["react", "nodejs", "vue", "angular", "typescript"],
                "complementary_skills": ["html", "css", "git", "webpack"],
                "industries": ["Technology", "E-commerce", "Media", "Finance"],
                "roles": ["Frontend Developer", "Full Stack Developer", "Web Developer"],
                "learning_resources": [
                    {"name": "JavaScript: The Complete Guide", "resource_type": "course", "provider": "Udemy",
                     "cost": "$20", "duration": "52 hours", "level": "Beginner", "rating": 4.7},
                    {"name": "Eloquent JavaScript", "resource_type": "book", "provider": "No Starch Press",
                     "url": "https://eloquentjavascript.net/", "cost": "Free",
                     "duration": "Self-paced", "level": "Intermediate", "rating": 4.6}
                ],
                "certifications": ["JavaScript Developer Certificate"],
                "keywords": ["javascript", "js", "ecmascript", "es6", "es2015"],
                "aliases": ["js", "ecmascript", "es6"]
            },
            {
                "id": "typescript",
                "name": "TypeScript",
                "category": "language",
                "subcategory": "Programming Languages",
                "description": "Typed superset of JavaScript for large-scale applications",
                "demand_level": "VERY_HIGH",
                "growth_rate": 35.0,
                "avg_salary_premium": 18.0,
                "related_skills": ["javascript", "react", "angular", "nodejs"],
                "parent_skills": ["javascript"],
                "child_skills": [],
                "complementary_skills": ["react", "angular", "webpack", "jest"],
                "industries": ["Technology", "Finance", "Enterprise Software"],
                "roles": ["Frontend Developer", "Full Stack Developer", "Software Engineer"],
                "learning_resources": [
                    {"name": "TypeScript Documentation", "resource_type": "tutorial", "provider": "Microsoft",
                     "url": "https://www.typescriptlang.org/docs/", "cost": "Free",
                     "duration": "Self-paced", "level": "Beginner", "rating": 4.5}
                ],
                "certifications": [],
                "keywords": ["typescript", "ts"],
                "aliases": ["ts"]
            },
            # Frameworks
            {
                "id": "react",
                "name": "React",
                "category": "framework",
                "subcategory": "Frontend Frameworks",
                "description": "JavaScript library for building user interfaces",
                "demand_level": "VERY_HIGH",
                "growth_rate": 22.0,
                "avg_salary_premium": 15.0,
                "related_skills": ["javascript", "typescript", "redux", "nextjs"],
                "parent_skills": ["javascript", "frontend-development"],
                "child_skills": ["nextjs", "redux", "react-native"],
                "complementary_skills": ["css", "html", "jest", "webpack"],
                "industries": ["Technology", "E-commerce", "Finance", "Media"],
                "roles": ["Frontend Developer", "React Developer", "Full Stack Developer"],
                "learning_resources": [
                    {"name": "React Official Tutorial", "resource_type": "tutorial", "provider": "React",
                     "url": "https://react.dev/learn", "cost": "Free",
                     "duration": "Self-paced", "level": "Beginner", "rating": 4.8}
                ],
                "certifications": ["Meta Front-End Developer Certificate"],
                "keywords": ["react", "reactjs", "react.js"],
                "aliases": ["reactjs", "react.js"]
            },
            {
                "id": "nodejs",
                "name": "Node.js",
                "category": "framework",
                "subcategory": "Backend Frameworks",
                "description": "JavaScript runtime for server-side development",
                "demand_level": "VERY_HIGH",
                "growth_rate": 18.0,
                "avg_salary_premium": 14.0,
                "related_skills": ["javascript", "express", "mongodb", "typescript"],
                "parent_skills": ["javascript", "backend-development"],
                "child_skills": ["express", "nestjs", "fastify"],
                "complementary_skills": ["mongodb", "postgresql", "docker", "aws"],
                "industries": ["Technology", "E-commerce", "Startups"],
                "roles": ["Backend Developer", "Full Stack Developer", "Node.js Developer"],
                "learning_resources": [
                    {"name": "The Complete Node.js Developer Course", "resource_type": "course", "provider": "Udemy",
                     "cost": "$20", "duration": "35 hours", "level": "Beginner", "rating": 4.7}
                ],
                "certifications": ["OpenJS Node.js Application Developer"],
                "keywords": ["nodejs", "node", "node.js"],
                "aliases": ["node", "node.js"]
            },
            # Cloud & DevOps
            {
                "id": "aws",
                "name": "Amazon Web Services (AWS)",
                "category": "tool",
                "subcategory": "Cloud Platforms",
                "description": "Leading cloud computing platform with comprehensive services",
                "demand_level": "VERY_HIGH",
                "growth_rate": 30.0,
                "avg_salary_premium": 20.0,
                "related_skills": ["azure", "gcp", "docker", "kubernetes", "terraform"],
                "parent_skills": ["cloud-computing"],
                "child_skills": ["ec2", "s3", "lambda", "rds"],
                "complementary_skills": ["linux", "docker", "kubernetes", "terraform"],
                "industries": ["Technology", "Finance", "Healthcare", "Enterprise"],
                "roles": ["Cloud Engineer", "DevOps Engineer", "Solutions Architect"],
                "learning_resources": [
                    {"name": "AWS Certified Solutions Architect", "resource_type": "certification", "provider": "AWS",
                     "url": "https://aws.amazon.com/certification/", "cost": "$300",
                     "duration": "3 months", "level": "Intermediate", "rating": 4.8}
                ],
                "certifications": ["AWS Solutions Architect", "AWS Developer", "AWS SysOps"],
                "keywords": ["aws", "amazon web services", "ec2", "s3", "lambda"],
                "aliases": ["amazon web services"]
            },
            {
                "id": "docker",
                "name": "Docker",
                "category": "tool",
                "subcategory": "DevOps Tools",
                "description": "Platform for developing, shipping, and running containerized applications",
                "demand_level": "VERY_HIGH",
                "growth_rate": 25.0,
                "avg_salary_premium": 15.0,
                "related_skills": ["kubernetes", "linux", "ci-cd", "aws"],
                "parent_skills": ["devops", "containerization"],
                "child_skills": ["docker-compose", "docker-swarm"],
                "complementary_skills": ["kubernetes", "linux", "jenkins", "github-actions"],
                "industries": ["Technology", "Finance", "Healthcare"],
                "roles": ["DevOps Engineer", "SRE", "Platform Engineer", "Backend Developer"],
                "learning_resources": [
                    {"name": "Docker Deep Dive", "resource_type": "book", "provider": "Nigel Poulton",
                     "cost": "$30", "duration": "Self-paced", "level": "Intermediate", "rating": 4.7}
                ],
                "certifications": ["Docker Certified Associate"],
                "keywords": ["docker", "containers", "containerization"],
                "aliases": ["containers"]
            },
            {
                "id": "kubernetes",
                "name": "Kubernetes",
                "category": "tool",
                "subcategory": "DevOps Tools",
                "description": "Container orchestration platform for automating deployment and scaling",
                "demand_level": "VERY_HIGH",
                "growth_rate": 35.0,
                "avg_salary_premium": 22.0,
                "related_skills": ["docker", "helm", "aws", "gcp", "terraform"],
                "parent_skills": ["devops", "container-orchestration"],
                "child_skills": ["helm", "istio", "argo-cd"],
                "complementary_skills": ["docker", "linux", "prometheus", "grafana"],
                "industries": ["Technology", "Finance", "Enterprise"],
                "roles": ["DevOps Engineer", "SRE", "Platform Engineer", "Cloud Architect"],
                "learning_resources": [
                    {"name": "CKA Certification Course", "resource_type": "course", "provider": "Linux Foundation",
                     "cost": "$395", "duration": "3 months", "level": "Advanced", "rating": 4.8}
                ],
                "certifications": ["CKA", "CKAD", "CKS"],
                "keywords": ["kubernetes", "k8s", "container orchestration"],
                "aliases": ["k8s"]
            },
            # Data & AI
            {
                "id": "machine-learning",
                "name": "Machine Learning",
                "category": "domain",
                "subcategory": "AI/ML",
                "description": "Building systems that learn from data to make predictions",
                "demand_level": "VERY_HIGH",
                "growth_rate": 40.0,
                "avg_salary_premium": 30.0,
                "related_skills": ["deep-learning", "python", "tensorflow", "pytorch", "scikit-learn"],
                "parent_skills": ["artificial-intelligence", "data-science"],
                "child_skills": ["deep-learning", "nlp", "computer-vision", "reinforcement-learning"],
                "complementary_skills": ["python", "statistics", "linear-algebra", "sql"],
                "industries": ["Technology", "Finance", "Healthcare", "Automotive", "Retail"],
                "roles": ["ML Engineer", "Data Scientist", "AI Researcher", "Applied Scientist"],
                "learning_resources": [
                    {"name": "Machine Learning by Andrew Ng", "resource_type": "course", "provider": "Coursera",
                     "url": "https://www.coursera.org/learn/machine-learning", "cost": "Free",
                     "duration": "3 months", "level": "Intermediate", "rating": 4.9}
                ],
                "certifications": ["AWS ML Specialty", "Google ML Engineer", "TensorFlow Developer"],
                "keywords": ["machine learning", "ml", "ai", "artificial intelligence"],
                "aliases": ["ml", "ai/ml"]
            },
            {
                "id": "sql",
                "name": "SQL",
                "category": "language",
                "subcategory": "Query Languages",
                "description": "Standard language for managing and querying relational databases",
                "demand_level": "VERY_HIGH",
                "growth_rate": 10.0,
                "avg_salary_premium": 10.0,
                "related_skills": ["postgresql", "mysql", "database-design", "data-analysis"],
                "parent_skills": ["data-management"],
                "child_skills": ["postgresql", "mysql", "sql-server", "oracle"],
                "complementary_skills": ["python", "excel", "tableau", "power-bi"],
                "industries": ["All Industries"],
                "roles": ["Data Analyst", "Database Administrator", "Backend Developer", "Data Engineer"],
                "learning_resources": [
                    {"name": "SQL for Data Science", "resource_type": "course", "provider": "Coursera",
                     "cost": "Free", "duration": "4 weeks", "level": "Beginner", "rating": 4.6}
                ],
                "certifications": ["Microsoft SQL Server Certification", "Oracle SQL Certification"],
                "keywords": ["sql", "database", "query"],
                "aliases": ["structured query language"]
            },
            # Soft Skills
            {
                "id": "communication",
                "name": "Communication",
                "category": "soft",
                "subcategory": "Interpersonal Skills",
                "description": "Ability to convey information clearly and effectively",
                "demand_level": "VERY_HIGH",
                "growth_rate": 5.0,
                "avg_salary_premium": 12.0,
                "related_skills": ["presentation", "writing", "active-listening", "negotiation"],
                "parent_skills": ["interpersonal-skills"],
                "child_skills": ["technical-writing", "public-speaking", "stakeholder-management"],
                "complementary_skills": ["leadership", "teamwork", "emotional-intelligence"],
                "industries": ["All Industries"],
                "roles": ["All Roles"],
                "learning_resources": [
                    {"name": "Effective Communication Skills", "resource_type": "course", "provider": "LinkedIn Learning",
                     "cost": "$30/month", "duration": "2 hours", "level": "Beginner", "rating": 4.5}
                ],
                "certifications": [],
                "keywords": ["communication", "verbal", "written", "interpersonal"],
                "aliases": ["communications", "verbal communication"]
            },
            {
                "id": "leadership",
                "name": "Leadership",
                "category": "soft",
                "subcategory": "Management Skills",
                "description": "Ability to guide, motivate, and influence teams to achieve goals",
                "demand_level": "HIGH",
                "growth_rate": 8.0,
                "avg_salary_premium": 25.0,
                "related_skills": ["team-management", "decision-making", "strategic-thinking"],
                "parent_skills": ["management"],
                "child_skills": ["team-management", "mentoring", "conflict-resolution"],
                "complementary_skills": ["communication", "emotional-intelligence", "project-management"],
                "industries": ["All Industries"],
                "roles": ["Manager", "Director", "VP", "C-Level"],
                "learning_resources": [
                    {"name": "Leadership Foundations", "resource_type": "course", "provider": "LinkedIn Learning",
                     "cost": "$30/month", "duration": "1.5 hours", "level": "Beginner", "rating": 4.6}
                ],
                "certifications": ["PMP", "Six Sigma Black Belt"],
                "keywords": ["leadership", "management", "lead", "manage"],
                "aliases": ["leading", "team lead"]
            },
            {
                "id": "problem-solving",
                "name": "Problem Solving",
                "category": "soft",
                "subcategory": "Cognitive Skills",
                "description": "Ability to analyze issues and develop effective solutions",
                "demand_level": "VERY_HIGH",
                "growth_rate": 5.0,
                "avg_salary_premium": 15.0,
                "related_skills": ["critical-thinking", "analytical-skills", "creativity"],
                "parent_skills": ["cognitive-skills"],
                "child_skills": ["root-cause-analysis", "debugging", "troubleshooting"],
                "complementary_skills": ["communication", "research", "decision-making"],
                "industries": ["All Industries"],
                "roles": ["All Roles"],
                "learning_resources": [
                    {"name": "Problem Solving Techniques", "resource_type": "course", "provider": "Coursera",
                     "cost": "Free", "duration": "4 weeks", "level": "Beginner", "rating": 4.4}
                ],
                "certifications": [],
                "keywords": ["problem solving", "troubleshooting", "debugging"],
                "aliases": ["troubleshooting", "analytical thinking"]
            },
            # Data Skills
            {
                "id": "data-analysis",
                "name": "Data Analysis",
                "category": "domain",
                "subcategory": "Data Skills",
                "description": "Process of inspecting, cleansing, and modeling data to discover insights",
                "demand_level": "VERY_HIGH",
                "growth_rate": 28.0,
                "avg_salary_premium": 18.0,
                "related_skills": ["sql", "excel", "python", "tableau", "statistics"],
                "parent_skills": ["data-science"],
                "child_skills": ["statistical-analysis", "data-visualization", "business-intelligence"],
                "complementary_skills": ["sql", "excel", "python", "communication"],
                "industries": ["All Industries"],
                "roles": ["Data Analyst", "Business Analyst", "BI Analyst", "Data Scientist"],
                "learning_resources": [
                    {"name": "Google Data Analytics", "resource_type": "certification", "provider": "Google",
                     "url": "https://www.coursera.org/professional-certificates/google-data-analytics",
                     "cost": "$39/month", "duration": "6 months", "level": "Beginner", "rating": 4.8}
                ],
                "certifications": ["Google Data Analytics", "Microsoft Data Analyst"],
                "keywords": ["data analysis", "analytics", "data analyst"],
                "aliases": ["analytics", "data analytics"]
            },
            # Project Management
            {
                "id": "project-management",
                "name": "Project Management",
                "category": "methodology",
                "subcategory": "Management Methodologies",
                "description": "Planning, organizing, and overseeing projects to achieve goals",
                "demand_level": "HIGH",
                "growth_rate": 12.0,
                "avg_salary_premium": 20.0,
                "related_skills": ["agile", "scrum", "stakeholder-management", "risk-management"],
                "parent_skills": ["management"],
                "child_skills": ["agile", "scrum", "waterfall", "kanban"],
                "complementary_skills": ["leadership", "communication", "budgeting", "scheduling"],
                "industries": ["All Industries"],
                "roles": ["Project Manager", "Program Manager", "Scrum Master", "Product Owner"],
                "learning_resources": [
                    {"name": "Google Project Management", "resource_type": "certification", "provider": "Google",
                     "url": "https://www.coursera.org/professional-certificates/google-project-management",
                     "cost": "$39/month", "duration": "6 months", "level": "Beginner", "rating": 4.8}
                ],
                "certifications": ["PMP", "CAPM", "Prince2", "CSM"],
                "keywords": ["project management", "pm", "pmp"],
                "aliases": ["pm", "programme management"]
            },
            {
                "id": "agile",
                "name": "Agile Methodology",
                "category": "methodology",
                "subcategory": "Management Methodologies",
                "description": "Iterative approach to project management and software development",
                "demand_level": "VERY_HIGH",
                "growth_rate": 15.0,
                "avg_salary_premium": 12.0,
                "related_skills": ["scrum", "kanban", "jira", "project-management"],
                "parent_skills": ["project-management"],
                "child_skills": ["scrum", "kanban", "xp", "lean"],
                "complementary_skills": ["communication", "collaboration", "sprint-planning"],
                "industries": ["Technology", "Finance", "Healthcare"],
                "roles": ["Scrum Master", "Agile Coach", "Product Owner", "Software Developer"],
                "learning_resources": [
                    {"name": "Agile with Atlassian Jira", "resource_type": "course", "provider": "Coursera",
                     "cost": "Free", "duration": "4 weeks", "level": "Beginner", "rating": 4.6}
                ],
                "certifications": ["CSM", "SAFe Agilist", "PMI-ACP"],
                "keywords": ["agile", "scrum", "kanban", "sprint"],
                "aliases": ["agile methodology", "agile development"]
            },
            # Security
            {
                "id": "cybersecurity",
                "name": "Cybersecurity",
                "category": "domain",
                "subcategory": "Security",
                "description": "Practice of protecting systems, networks, and data from attacks",
                "demand_level": "VERY_HIGH",
                "growth_rate": 33.0,
                "avg_salary_premium": 25.0,
                "related_skills": ["network-security", "penetration-testing", "encryption", "compliance"],
                "parent_skills": ["information-technology"],
                "child_skills": ["network-security", "application-security", "cloud-security", "incident-response"],
                "complementary_skills": ["linux", "networking", "python", "scripting"],
                "industries": ["Technology", "Finance", "Healthcare", "Government", "Defense"],
                "roles": ["Security Engineer", "Security Analyst", "Penetration Tester", "CISO"],
                "learning_resources": [
                    {"name": "CompTIA Security+", "resource_type": "certification", "provider": "CompTIA",
                     "cost": "$381", "duration": "3 months", "level": "Intermediate", "rating": 4.7}
                ],
                "certifications": ["Security+", "CISSP", "CEH", "OSCP"],
                "keywords": ["cybersecurity", "security", "infosec", "information security"],
                "aliases": ["security", "infosec", "information security"]
            },
            # Design
            {
                "id": "ui-ux-design",
                "name": "UI/UX Design",
                "category": "domain",
                "subcategory": "Design",
                "description": "Designing user interfaces and experiences for digital products",
                "demand_level": "HIGH",
                "growth_rate": 22.0,
                "avg_salary_premium": 15.0,
                "related_skills": ["figma", "adobe-xd", "user-research", "prototyping"],
                "parent_skills": ["design"],
                "child_skills": ["ui-design", "ux-research", "interaction-design", "visual-design"],
                "complementary_skills": ["html", "css", "javascript", "user-research"],
                "industries": ["Technology", "E-commerce", "Media", "Finance"],
                "roles": ["UX Designer", "UI Designer", "Product Designer", "Design Lead"],
                "learning_resources": [
                    {"name": "Google UX Design", "resource_type": "certification", "provider": "Google",
                     "url": "https://www.coursera.org/professional-certificates/google-ux-design",
                     "cost": "$39/month", "duration": "6 months", "level": "Beginner", "rating": 4.8}
                ],
                "certifications": ["Google UX Design", "Nielsen Norman UX Certification"],
                "keywords": ["ui", "ux", "user interface", "user experience", "design"],
                "aliases": ["ux", "ui", "user experience design", "user interface design"]
            },
            {
                "id": "git",
                "name": "Git",
                "category": "tool",
                "subcategory": "Version Control",
                "description": "Distributed version control system for tracking code changes",
                "demand_level": "VERY_HIGH",
                "growth_rate": 8.0,
                "avg_salary_premium": 5.0,
                "related_skills": ["github", "gitlab", "version-control", "ci-cd"],
                "parent_skills": ["version-control"],
                "child_skills": ["github", "gitlab", "bitbucket"],
                "complementary_skills": ["linux", "command-line", "ci-cd"],
                "industries": ["Technology", "All Software Companies"],
                "roles": ["Software Developer", "DevOps Engineer", "All Technical Roles"],
                "learning_resources": [
                    {"name": "Git & GitHub Bootcamp", "resource_type": "course", "provider": "Udemy",
                     "cost": "$20", "duration": "17 hours", "level": "Beginner", "rating": 4.7}
                ],
                "certifications": [],
                "keywords": ["git", "version control", "github"],
                "aliases": ["version control", "source control"]
            },
        ]

    def _build_indices(self) -> None:
        """Build search indices for efficient lookups"""
        for skill_id, skill in self.skills.items():
            # Category index
            self.category_index[skill.category].append(skill_id)

            # Industry index
            for industry in skill.industries:
                if industry not in self.industry_index:
                    self.industry_index[industry] = []
                self.industry_index[industry].append(skill_id)

    def _save_skills_database(self) -> None:
        """Save skills database to JSON file"""
        skills_file = self.skills_dir / "skills_database.json"
        data = {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "skills": [skill.to_dict() for skill in self.skills.values()]
        }

        with open(skills_file, 'w') as f:
            json.dump(data, f, indent=2)

        self.logger.info(f"Saved {len(self.skills)} skills to database")

    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """
        Get a skill by ID or alias.

        Args:
            skill_id (str): Skill ID or alias

        Returns:
            Optional[Skill]: The skill if found, None otherwise
        """
        # Check direct ID match
        if skill_id in self.skills:
            return self.skills[skill_id]

        # Check aliases
        canonical_id = self.skill_aliases.get(skill_id.lower())
        if canonical_id:
            return self.skills.get(canonical_id)

        return None

    def search_skills(
        self,
        query: str,
        category: Optional[SkillCategory] = None,
        industry: Optional[str] = None,
        demand_level: Optional[DemandLevel] = None,
        limit: int = 10
    ) -> List[SkillMatch]:
        """
        Search for skills matching the query and filters.

        Args:
            query (str): Search query
            category (Optional[SkillCategory]): Filter by category
            industry (Optional[str]): Filter by industry
            demand_level (Optional[DemandLevel]): Filter by demand level
            limit (int): Maximum results to return

        Returns:
            List[SkillMatch]: Matching skills with scores
        """
        matches = []
        query_lower = query.lower()
        query_terms = set(query_lower.split())

        for skill_id, skill in self.skills.items():
            # Apply filters
            if category and skill.category != category:
                continue
            if industry and industry not in skill.industries:
                continue
            if demand_level and skill.demand_level != demand_level:
                continue

            # Calculate match score
            score = 0.0
            match_type = "partial"

            # Exact name match
            if query_lower == skill.name.lower():
                score = 1.0
                match_type = "exact"
            # ID match
            elif query_lower == skill.id:
                score = 0.95
                match_type = "exact"
            # Alias match
            elif query_lower in self.skill_aliases and self.skill_aliases[query_lower] == skill.id:
                score = 0.9
                match_type = "exact"
            else:
                # Partial matching
                name_lower = skill.name.lower()

                # Name contains query
                if query_lower in name_lower:
                    score = 0.7 + (len(query_lower) / len(name_lower)) * 0.2
                # Query terms in keywords
                elif query_terms & set(kw.lower() for kw in skill.keywords):
                    overlap = len(query_terms & set(kw.lower() for kw in skill.keywords))
                    score = 0.5 + (overlap / len(query_terms)) * 0.3
                # Query in description
                elif query_lower in skill.description.lower():
                    score = 0.3
                # Related skill match
                elif any(query_lower in rs.lower() for rs in skill.related_skills):
                    score = 0.2
                    match_type = "related"

            if score > 0:
                matches.append(SkillMatch(
                    skill=skill,
                    match_score=score,
                    match_type=match_type,
                    context=f"Found in: {skill.category.value}"
                ))

        # Sort by score and return top results
        matches.sort(key=lambda x: x.match_score, reverse=True)
        return matches[:limit]

    def get_related_skills(self, skill_id: str, limit: int = 10) -> List[Skill]:
        """
        Get skills related to the given skill.

        Args:
            skill_id (str): Skill ID
            limit (int): Maximum results

        Returns:
            List[Skill]: Related skills
        """
        skill = self.get_skill(skill_id)
        if not skill:
            return []

        related = []
        seen = {skill_id}

        # Get directly related skills
        for related_id in skill.related_skills[:limit]:
            if related_id in self.skills and related_id not in seen:
                related.append(self.skills[related_id])
                seen.add(related_id)

        # Get complementary skills
        for comp_id in skill.complementary_skills[:limit - len(related)]:
            if comp_id in self.skills and comp_id not in seen:
                related.append(self.skills[comp_id])
                seen.add(comp_id)

        # Get parent skills
        for parent_id in skill.parent_skills:
            if parent_id in self.skills and parent_id not in seen and len(related) < limit:
                related.append(self.skills[parent_id])
                seen.add(parent_id)

        # Get child skills
        for child_id in skill.child_skills:
            if child_id in self.skills and child_id not in seen and len(related) < limit:
                related.append(self.skills[child_id])
                seen.add(child_id)

        return related[:limit]

    def get_skills_by_category(self, category: SkillCategory) -> List[Skill]:
        """
        Get all skills in a category.

        Args:
            category (SkillCategory): The category

        Returns:
            List[Skill]: Skills in the category
        """
        return [self.skills[skill_id] for skill_id in self.category_index.get(category, [])]

    def get_skills_by_industry(self, industry: str) -> List[Skill]:
        """
        Get skills relevant to an industry.

        Args:
            industry (str): Industry name

        Returns:
            List[Skill]: Skills for the industry
        """
        skill_ids = self.industry_index.get(industry, [])
        return [self.skills[skill_id] for skill_id in skill_ids]

    def get_high_demand_skills(self, limit: int = 20) -> List[Skill]:
        """
        Get skills with highest market demand.

        Args:
            limit (int): Maximum results

        Returns:
            List[Skill]: High demand skills
        """
        sorted_skills = sorted(
            self.skills.values(),
            key=lambda s: (s.demand_level.to_score(), s.growth_rate),
            reverse=True
        )
        return sorted_skills[:limit]

    def get_fastest_growing_skills(self, limit: int = 20) -> List[Skill]:
        """
        Get skills with fastest growth rate.

        Args:
            limit (int): Maximum results

        Returns:
            List[Skill]: Fastest growing skills
        """
        sorted_skills = sorted(
            self.skills.values(),
            key=lambda s: s.growth_rate,
            reverse=True
        )
        return sorted_skills[:limit]

    def analyze_skill_gaps(
        self,
        current_skills: Dict[str, int],
        target_role: str,
        required_skills: List[str]
    ) -> List[SkillGap]:
        """
        Analyze gaps between current skills and role requirements.

        Args:
            current_skills (Dict[str, int]): Current skills with proficiency levels (1-5)
            target_role (str): Target role
            required_skills (List[str]): Required skills for the role

        Returns:
            List[SkillGap]: Identified skill gaps
        """
        gaps = []

        for req_skill in required_skills:
            skill = self.get_skill(req_skill)
            if not skill:
                continue

            current_level = current_skills.get(req_skill, 0)
            required_level = 3  # Default intermediate level

            if current_level < required_level:
                gap_size = required_level - current_level

                # Determine severity
                if gap_size >= 3:
                    severity = "critical"
                elif gap_size >= 2:
                    severity = "important"
                else:
                    severity = "nice_to_have"

                # Estimate time to acquire
                if current_level == 0:
                    time_estimate = "3-6 months"
                elif current_level == 1:
                    time_estimate = "2-4 months"
                else:
                    time_estimate = "1-2 months"

                gaps.append(SkillGap(
                    required_skill=req_skill,
                    current_level=current_level,
                    required_level=required_level,
                    gap_severity=severity,
                    recommended_resources=skill.learning_resources[:3],
                    estimated_time_to_acquire=time_estimate
                ))

        # Sort by severity
        severity_order = {"critical": 0, "important": 1, "nice_to_have": 2}
        gaps.sort(key=lambda g: severity_order[g.gap_severity])

        return gaps

    def get_learning_path(self, skill_id: str) -> Dict[str, Any]:
        """
        Get recommended learning path for a skill.

        Args:
            skill_id (str): Skill ID

        Returns:
            Dict: Learning path with stages and resources
        """
        skill = self.get_skill(skill_id)
        if not skill:
            return {"error": "Skill not found"}

        # Build learning path
        path = {
            "skill": skill.name,
            "description": skill.description,
            "stages": []
        }

        # Prerequisites (parent skills)
        if skill.parent_skills:
            prereqs = [self.get_skill(ps) for ps in skill.parent_skills if self.get_skill(ps)]
            path["stages"].append({
                "stage": "Prerequisites",
                "description": "Master these foundational skills first",
                "skills": [ps.name for ps in prereqs if ps],
                "resources": [r for ps in prereqs if ps for r in ps.learning_resources[:1]]
            })

        # Beginner stage
        beginner_resources = [r for r in skill.learning_resources if r.level == "Beginner"]
        path["stages"].append({
            "stage": "Beginner",
            "description": f"Learn the fundamentals of {skill.name}",
            "duration": "4-8 weeks",
            "resources": [r.to_dict() for r in beginner_resources[:3]]
        })

        # Intermediate stage
        intermediate_resources = [r for r in skill.learning_resources if r.level == "Intermediate"]
        path["stages"].append({
            "stage": "Intermediate",
            "description": f"Build proficiency in {skill.name}",
            "duration": "8-12 weeks",
            "resources": [r.to_dict() for r in intermediate_resources[:3]]
        })

        # Advanced stage
        advanced_resources = [r for r in skill.learning_resources if r.level == "Advanced"]
        path["stages"].append({
            "stage": "Advanced",
            "description": f"Achieve expertise in {skill.name}",
            "duration": "3-6 months",
            "resources": [r.to_dict() for r in advanced_resources[:3]],
            "certifications": skill.certifications
        })

        # Complementary skills
        if skill.complementary_skills:
            comp_skills = [self.get_skill(cs) for cs in skill.complementary_skills[:5] if self.get_skill(cs)]
            path["complementary_skills"] = [
                {"name": cs.name, "id": cs.id, "description": cs.description}
                for cs in comp_skills if cs
            ]

        return path

    def get_skill_market_data(self, skill_id: str) -> Dict[str, Any]:
        """
        Get market data for a skill.

        Args:
            skill_id (str): Skill ID

        Returns:
            Dict: Market data including demand, growth, salary impact
        """
        skill = self.get_skill(skill_id)
        if not skill:
            return {"error": "Skill not found"}

        return {
            "skill": skill.name,
            "demand_level": skill.demand_level.value,
            "demand_score": skill.demand_level.to_score(),
            "growth_rate": f"{skill.growth_rate}%",
            "salary_premium": f"+{skill.avg_salary_premium}%",
            "top_industries": skill.industries[:5],
            "top_roles": skill.roles[:5],
            "related_high_demand": [
                rs for rs in skill.related_skills[:5]
                if rs in self.skills and self.skills[rs].demand_level in [DemandLevel.VERY_HIGH, DemandLevel.HIGH]
            ],
            "certifications": skill.certifications,
            "recommendation": self._get_skill_recommendation(skill)
        }

    def _get_skill_recommendation(self, skill: Skill) -> str:
        """Generate recommendation based on skill metrics"""
        if skill.demand_level == DemandLevel.VERY_HIGH and skill.growth_rate > 20:
            return "Highly recommended - strong demand and excellent growth trajectory"
        elif skill.demand_level == DemandLevel.VERY_HIGH:
            return "Strongly recommended - consistently high demand across industries"
        elif skill.growth_rate > 25:
            return "Emerging skill - rapid growth indicates future demand"
        elif skill.demand_level == DemandLevel.HIGH:
            return "Recommended - solid demand with good career prospects"
        elif skill.demand_level == DemandLevel.DECLINING:
            return "Consider alternatives - demand is declining, focus on related modern skills"
        else:
            return "Moderate priority - useful but consider pairing with high-demand skills"

    def get_ai_skill_analysis(self, skill_id: str) -> Optional[Dict]:
        """
        Get AI-powered analysis of a skill using GPT-4.

        Args:
            skill_id (str): Skill ID

        Returns:
            Optional[Dict]: AI analysis or None if unavailable
        """
        if not self.gemini_model:
            return None

        skill = self.get_skill(skill_id)
        if not skill:
            return None

        prompt = f"""Analyze the following skill for career development:

Skill: {skill.name}
Category: {skill.category.value}
Description: {skill.description}
Current Demand: {skill.demand_level.value}
Growth Rate: {skill.growth_rate}%
Industries: {', '.join(skill.industries[:5])}
Related Skills: {', '.join(skill.related_skills[:5])}

Provide:
1. A brief market outlook (2-3 sentences)
2. Top 3 career paths leveraging this skill
3. 3 complementary skills to learn alongside
4. Potential salary range for different experience levels
5. Key trends affecting this skill's future demand

Be specific and actionable."""

        try:
            model = genai.GenerativeModel(
                "gemini-2.0-flash",
                system_instruction="You are an expert career advisor with deep knowledge of tech skills and job market trends."
            )
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=600,
                ),
            )

            return {
                "skill": skill.name,
                "analysis": response.text,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"AI analysis failed: {e}")
            return None

    def add_skill(self, skill: Skill) -> bool:
        """
        Add a new skill to the taxonomy.

        Args:
            skill (Skill): Skill to add

        Returns:
            bool: Success status
        """
        if skill.id in self.skills:
            self.logger.warning(f"Skill {skill.id} already exists")
            return False

        self.skills[skill.id] = skill
        self.category_index[skill.category].append(skill.id)
        for industry in skill.industries:
            if industry not in self.industry_index:
                self.industry_index[industry] = []
            self.industry_index[industry].append(skill.id)

        self._save_skills_database()
        return True

    def update_skill(self, skill_id: str, updates: Dict) -> bool:
        """
        Update an existing skill.

        Args:
            skill_id (str): Skill ID
            updates (Dict): Fields to update

        Returns:
            bool: Success status
        """
        if skill_id not in self.skills:
            return False

        skill = self.skills[skill_id]
        for key, value in updates.items():
            if hasattr(skill, key):
                setattr(skill, key, value)

        skill.last_updated = datetime.now().isoformat()
        self._save_skills_database()
        return True

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the skills database.

        Returns:
            Dict: Database statistics
        """
        category_counts = {cat.value: len(ids) for cat, ids in self.category_index.items()}
        demand_counts = {}
        for skill in self.skills.values():
            demand = skill.demand_level.value
            demand_counts[demand] = demand_counts.get(demand, 0) + 1

        return {
            "total_skills": len(self.skills),
            "categories": category_counts,
            "demand_distribution": demand_counts,
            "industries_covered": len(self.industry_index),
            "total_aliases": len(self.skill_aliases),
            "avg_growth_rate": sum(s.growth_rate for s in self.skills.values()) / len(self.skills) if self.skills else 0
        }


# Prompt templates for AI-powered features
SKILL_ANALYSIS_PROMPT = """You are an expert career advisor analyzing skills for career development.

**Skill Information:**
- Name: {skill_name}
- Category: {category}
- Description: {description}
- Current Demand: {demand_level}
- Growth Rate: {growth_rate}%
- Top Industries: {industries}

**Analysis Required:**
1. Market Outlook: Provide a 2-3 sentence analysis of current and future demand
2. Career Paths: List 3 specific career paths that leverage this skill
3. Complementary Skills: Recommend 3 skills that pair well with this
4. Salary Impact: Estimate salary ranges for Junior/Mid/Senior levels
5. Future Trends: Identify 2-3 trends affecting this skill's demand

**Example Analysis:**
For "Machine Learning":
1. Market Outlook: Machine learning demand continues to surge as organizations prioritize AI adoption. The skill shows 40% annual growth with very high demand across tech, finance, and healthcare sectors.
2. Career Paths: ML Engineer ($120-180K), Data Scientist ($100-160K), AI Research Scientist ($130-200K)
3. Complementary Skills: Python, Statistics, Cloud Computing (AWS/GCP)
4. Salary Impact: Junior ($85-110K), Mid ($120-150K), Senior ($160-220K)
5. Future Trends: AutoML democratizing access, Edge ML growing, Regulatory oversight increasing

Now analyze the provided skill with the same level of detail and specificity."""

SKILL_GAP_ANALYSIS_PROMPT = """You are a career development expert analyzing skill gaps.

**Current Skills:**
{current_skills}

**Target Role:** {target_role}

**Required Skills for Role:**
{required_skills}

**Analysis Required:**
1. Identify critical skill gaps (must-have skills the candidate lacks)
2. Identify important skill gaps (strongly recommended skills)
3. Identify nice-to-have skill gaps (would be beneficial)
4. For each gap, recommend specific learning resources and timeline
5. Suggest a prioritized learning roadmap

**Example Gap Analysis:**
For transitioning from "Data Analyst" to "ML Engineer":
Critical Gaps:
- Python for ML (3-month intensive): Coursera ML Specialization, hands-on Kaggle projects
- Deep Learning fundamentals (2-month): fast.ai course, build 3 neural network projects

Important Gaps:
- MLOps/Model deployment (1-month): AWS ML certification prep, deploy 2 models to production
- SQL optimization (2-week): LeetCode SQL problems, optimize 5 existing queries

Nice-to-Have:
- Cloud certifications: AWS ML Specialty after 6 months of hands-on work

Provide specific, actionable recommendations."""
