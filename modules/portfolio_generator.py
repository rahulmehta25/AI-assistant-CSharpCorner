"""
Portfolio Project Generator

Suggests portfolio projects based on target role that demonstrate
required skills and make candidates stand out.

Author: Career Assistant AI System
Version: 1.0.0
"""

import json
import logging
import os
import random
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


class ProjectDifficulty(Enum):
    """Project difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

    def estimated_hours(self) -> Tuple[int, int]:
        """Get estimated hours range"""
        ranges = {
            self.BEGINNER: (10, 25),
            self.INTERMEDIATE: (25, 60),
            self.ADVANCED: (60, 120),
            self.EXPERT: (120, 300)
        }
        return ranges[self]


class ProjectType(Enum):
    """Types of portfolio projects"""
    PERSONAL = "personal"           # Side project
    CLONE = "clone"                 # Clone of existing product
    OPEN_SOURCE = "open_source"     # Contribution to OSS
    HACKATHON = "hackathon"         # Competition project
    TUTORIAL = "tutorial"           # Follow-along project
    ORIGINAL = "original"           # Original idea
    CASE_STUDY = "case_study"       # Analysis/research project


@dataclass
class TechStack:
    """Technology stack for a project"""
    primary_language: str
    frameworks: List[str]
    databases: List[str]
    tools: List[str]
    deployment: str
    testing: List[str]


@dataclass
class ProjectMilestone:
    """Milestone in project development"""
    name: str
    description: str
    deliverables: List[str]
    estimated_hours: int
    skills_demonstrated: List[str]


@dataclass
class PortfolioProject:
    """A portfolio project suggestion"""
    id: str
    title: str
    description: str
    problem_statement: str
    target_roles: List[str]
    difficulty: ProjectDifficulty
    project_type: ProjectType
    skills_demonstrated: List[str]
    tech_stack: TechStack
    milestones: List[ProjectMilestone]
    estimated_hours: int
    impact_statement: str
    interview_talking_points: List[str]
    differentiation_factors: List[str]
    resources: List[Dict[str, str]]
    sample_features: List[str]
    stretch_goals: List[str]
    github_topics: List[str]

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['difficulty'] = self.difficulty.value
        data['project_type'] = self.project_type.value
        return data


@dataclass
class ProjectRecommendation:
    """Recommended project with context"""
    project: PortfolioProject
    relevance_score: float
    skill_coverage: float
    unique_value: str
    why_recommended: str


class PortfolioGenerator:
    """
    Portfolio project generator service.

    Suggests relevant portfolio projects based on target role,
    current skills, and career goals.
    """

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the portfolio generator.

        Args:
            data_dir (str): Path to data directory. Defaults to "data".
        """
        self.data_dir = Path(data_dir)
        self.portfolio_dir = self.data_dir / "portfolio_projects"
        self.portfolio_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(__name__)

        # Project templates database
        self.project_templates: Dict[str, List[Dict]] = {}
        self.role_skill_map: Dict[str, List[str]] = {}

        # Initialize Gemini
        self.gemini_model = None
        if GEMINI_AVAILABLE:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel("gemini-2.0-flash")

        self._load_project_templates()
        self._build_role_skill_map()

        self.logger.info("PortfolioGenerator initialized")

    def _load_project_templates(self) -> None:
        """Load project templates from database"""
        templates_file = self.portfolio_dir / "project_templates.json"

        if templates_file.exists():
            try:
                with open(templates_file, 'r') as f:
                    self.project_templates = json.load(f)
                self.logger.info(f"Loaded {sum(len(v) for v in self.project_templates.values())} project templates")
            except Exception as e:
                self.logger.error(f"Error loading templates: {e}")
                self._initialize_default_templates()
        else:
            self._initialize_default_templates()

    def _initialize_default_templates(self) -> None:
        """Initialize default project templates"""
        self.project_templates = {
            "software_engineer": [
                {
                    "id": "distributed_task_queue",
                    "title": "Distributed Task Queue System",
                    "description": "Build a distributed task queue similar to Celery with job scheduling, retries, and monitoring",
                    "problem_statement": "Demonstrate understanding of distributed systems, message queues, and fault tolerance",
                    "difficulty": "advanced",
                    "project_type": "original",
                    "skills_demonstrated": ["distributed_systems", "python", "redis", "docker", "system_design"],
                    "tech_stack": {
                        "primary_language": "Python",
                        "frameworks": ["FastAPI", "asyncio"],
                        "databases": ["Redis", "PostgreSQL"],
                        "tools": ["Docker", "Prometheus", "Grafana"],
                        "deployment": "Kubernetes",
                        "testing": ["pytest", "pytest-asyncio"]
                    },
                    "sample_features": [
                        "Job submission and scheduling",
                        "Priority queues",
                        "Retry with exponential backoff",
                        "Dead letter queue",
                        "Real-time monitoring dashboard",
                        "Worker scaling"
                    ],
                    "stretch_goals": [
                        "Multi-tenant support",
                        "Workflow DAGs",
                        "Rate limiting"
                    ],
                    "estimated_hours": 80,
                    "impact_statement": "Demonstrates ability to design and implement production-grade distributed systems",
                    "interview_talking_points": [
                        "How I handled distributed consensus",
                        "Fault tolerance and recovery strategies",
                        "Performance optimizations for high throughput",
                        "Monitoring and observability design decisions"
                    ]
                },
                {
                    "id": "api_gateway",
                    "title": "API Gateway with Rate Limiting",
                    "description": "Build an API gateway with authentication, rate limiting, and request routing",
                    "problem_statement": "Show expertise in API design, security, and scalable architecture",
                    "difficulty": "intermediate",
                    "project_type": "original",
                    "skills_demonstrated": ["api_design", "python", "authentication", "caching", "system_design"],
                    "tech_stack": {
                        "primary_language": "Go",
                        "frameworks": ["Chi", "stdlib"],
                        "databases": ["Redis", "PostgreSQL"],
                        "tools": ["Docker", "JWT"],
                        "deployment": "Docker Compose",
                        "testing": ["go test", "k6"]
                    },
                    "sample_features": [
                        "JWT authentication",
                        "Token bucket rate limiting",
                        "Request routing and load balancing",
                        "Request/response transformation",
                        "API analytics",
                        "Circuit breaker pattern"
                    ],
                    "stretch_goals": ["GraphQL support", "WebSocket proxying", "A/B testing"],
                    "estimated_hours": 50,
                    "impact_statement": "Shows understanding of API infrastructure and security best practices",
                    "interview_talking_points": [
                        "Rate limiting algorithm choices",
                        "Security considerations",
                        "Performance under load"
                    ]
                },
                {
                    "id": "real_time_collab",
                    "title": "Real-time Collaborative Editor",
                    "description": "Build a Google Docs-style collaborative text editor with conflict resolution",
                    "problem_statement": "Demonstrate real-time systems expertise and conflict resolution strategies",
                    "difficulty": "expert",
                    "project_type": "original",
                    "skills_demonstrated": ["websockets", "crdt", "react", "nodejs", "distributed_systems"],
                    "tech_stack": {
                        "primary_language": "TypeScript",
                        "frameworks": ["React", "Node.js", "Socket.io"],
                        "databases": ["PostgreSQL", "Redis"],
                        "tools": ["Yjs", "Docker"],
                        "deployment": "Vercel + Railway",
                        "testing": ["Jest", "Playwright"]
                    },
                    "sample_features": [
                        "Real-time text collaboration",
                        "Cursor presence",
                        "Version history",
                        "Offline support with sync",
                        "Comments and suggestions",
                        "Export to multiple formats"
                    ],
                    "stretch_goals": ["Rich text formatting", "Image embedding", "Access control"],
                    "estimated_hours": 120,
                    "impact_statement": "Showcases advanced real-time systems and collaboration features",
                    "interview_talking_points": [
                        "CRDT vs OT decision and implementation",
                        "Handling network partitions",
                        "Scaling WebSocket connections"
                    ]
                }
            ],
            "frontend_developer": [
                {
                    "id": "design_system",
                    "title": "Component Library & Design System",
                    "description": "Build a comprehensive React component library with Storybook documentation",
                    "problem_statement": "Demonstrate expertise in reusable components, accessibility, and design systems",
                    "difficulty": "intermediate",
                    "project_type": "original",
                    "skills_demonstrated": ["react", "typescript", "css", "accessibility", "storybook", "testing"],
                    "tech_stack": {
                        "primary_language": "TypeScript",
                        "frameworks": ["React", "Styled Components"],
                        "databases": [],
                        "tools": ["Storybook", "Chromatic", "Figma"],
                        "deployment": "npm publish",
                        "testing": ["Jest", "React Testing Library", "Axe"]
                    },
                    "sample_features": [
                        "20+ accessible components",
                        "Theming system (light/dark)",
                        "Interactive Storybook docs",
                        "Component composition patterns",
                        "Keyboard navigation",
                        "Screen reader support"
                    ],
                    "stretch_goals": ["Animation library", "Form validation", "Charts"],
                    "estimated_hours": 60,
                    "impact_statement": "Shows ability to create maintainable, accessible UI foundations",
                    "interview_talking_points": [
                        "Accessibility decisions",
                        "API design for components",
                        "Performance optimizations"
                    ]
                },
                {
                    "id": "dashboard_builder",
                    "title": "Drag-and-Drop Dashboard Builder",
                    "description": "Build an analytics dashboard builder with drag-drop widgets and real-time data",
                    "problem_statement": "Show advanced frontend skills including complex interactions and data visualization",
                    "difficulty": "advanced",
                    "project_type": "original",
                    "skills_demonstrated": ["react", "typescript", "d3", "drag_drop", "state_management"],
                    "tech_stack": {
                        "primary_language": "TypeScript",
                        "frameworks": ["React", "D3.js", "dnd-kit"],
                        "databases": ["IndexedDB"],
                        "tools": ["Vite", "TanStack Query"],
                        "deployment": "Vercel",
                        "testing": ["Vitest", "Playwright"]
                    },
                    "sample_features": [
                        "Drag-and-drop grid layout",
                        "10+ chart widgets",
                        "Real-time data updates",
                        "Dashboard persistence",
                        "Export to PDF/Image",
                        "Responsive layouts"
                    ],
                    "stretch_goals": ["Custom widget builder", "Data connectors", "Sharing"],
                    "estimated_hours": 80,
                    "impact_statement": "Demonstrates complex UI engineering and data visualization skills",
                    "interview_talking_points": [
                        "Drag-drop implementation challenges",
                        "Performance with many widgets",
                        "State management approach"
                    ]
                }
            ],
            "data_scientist": [
                {
                    "id": "ml_pipeline",
                    "title": "End-to-End ML Pipeline",
                    "description": "Build a complete ML pipeline from data ingestion to model serving with monitoring",
                    "problem_statement": "Demonstrate MLOps skills and production ML understanding",
                    "difficulty": "advanced",
                    "project_type": "original",
                    "skills_demonstrated": ["python", "mlops", "docker", "ml", "data_engineering"],
                    "tech_stack": {
                        "primary_language": "Python",
                        "frameworks": ["scikit-learn", "FastAPI", "MLflow"],
                        "databases": ["PostgreSQL", "S3"],
                        "tools": ["Docker", "Airflow", "Great Expectations"],
                        "deployment": "AWS/GCP",
                        "testing": ["pytest", "Great Expectations"]
                    },
                    "sample_features": [
                        "Automated data validation",
                        "Feature engineering pipeline",
                        "Model training with MLflow tracking",
                        "A/B testing framework",
                        "Model serving API",
                        "Drift monitoring"
                    ],
                    "stretch_goals": ["Feature store", "AutoML", "Explainability"],
                    "estimated_hours": 100,
                    "impact_statement": "Shows production-ready ML engineering beyond notebooks",
                    "interview_talking_points": [
                        "Pipeline design decisions",
                        "Handling data drift",
                        "Model retraining strategies"
                    ]
                },
                {
                    "id": "recommendation_system",
                    "title": "Hybrid Recommendation System",
                    "description": "Build a recommendation engine combining collaborative filtering and content-based approaches",
                    "problem_statement": "Show deep understanding of recommendation algorithms and evaluation",
                    "difficulty": "intermediate",
                    "project_type": "original",
                    "skills_demonstrated": ["python", "ml", "recommender_systems", "evaluation"],
                    "tech_stack": {
                        "primary_language": "Python",
                        "frameworks": ["Surprise", "LightFM", "FastAPI"],
                        "databases": ["PostgreSQL", "Redis"],
                        "tools": ["MLflow", "Streamlit"],
                        "deployment": "Docker",
                        "testing": ["pytest"]
                    },
                    "sample_features": [
                        "Collaborative filtering (user/item)",
                        "Content-based recommendations",
                        "Hybrid ensemble approach",
                        "Cold start handling",
                        "Real-time recommendations API",
                        "Offline evaluation dashboard"
                    ],
                    "stretch_goals": ["Deep learning approach", "Contextual bandits", "Explanations"],
                    "estimated_hours": 70,
                    "impact_statement": "Demonstrates practical ML application with business impact",
                    "interview_talking_points": [
                        "Algorithm selection rationale",
                        "Evaluation metrics chosen",
                        "Cold start solutions"
                    ]
                }
            ],
            "devops_engineer": [
                {
                    "id": "infrastructure_as_code",
                    "title": "Multi-Cloud Infrastructure Platform",
                    "description": "Build a Terraform-based infrastructure platform with multi-cloud support",
                    "problem_statement": "Demonstrate infrastructure automation and multi-cloud expertise",
                    "difficulty": "advanced",
                    "project_type": "original",
                    "skills_demonstrated": ["terraform", "aws", "gcp", "kubernetes", "gitops"],
                    "tech_stack": {
                        "primary_language": "HCL",
                        "frameworks": ["Terraform", "Terragrunt"],
                        "databases": [],
                        "tools": ["GitHub Actions", "Atlantis", "tfsec"],
                        "deployment": "Self-managed",
                        "testing": ["Terratest", "checkov"]
                    },
                    "sample_features": [
                        "Reusable Terraform modules",
                        "Multi-environment setup (dev/staging/prod)",
                        "Cost estimation integration",
                        "Security scanning in CI",
                        "Automated PR planning",
                        "State management with locking"
                    ],
                    "stretch_goals": ["Policy as code", "Drift detection", "Cost alerts"],
                    "estimated_hours": 80,
                    "impact_statement": "Shows ability to build production infrastructure foundations",
                    "interview_talking_points": [
                        "Module design philosophy",
                        "Security considerations",
                        "State management decisions"
                    ]
                },
                {
                    "id": "observability_platform",
                    "title": "Observability Stack",
                    "description": "Build a complete observability platform with metrics, logs, and traces",
                    "problem_statement": "Demonstrate monitoring expertise and incident response capability",
                    "difficulty": "intermediate",
                    "project_type": "original",
                    "skills_demonstrated": ["prometheus", "grafana", "kubernetes", "monitoring", "alerting"],
                    "tech_stack": {
                        "primary_language": "YAML",
                        "frameworks": ["Prometheus", "Grafana", "Loki"],
                        "databases": ["VictoriaMetrics"],
                        "tools": ["Jaeger", "AlertManager", "PagerDuty"],
                        "deployment": "Kubernetes",
                        "testing": ["promtool"]
                    },
                    "sample_features": [
                        "Metrics collection and visualization",
                        "Log aggregation and search",
                        "Distributed tracing",
                        "Custom dashboards",
                        "Alert rules with routing",
                        "SLO/SLI tracking"
                    ],
                    "stretch_goals": ["AIOps anomaly detection", "Cost tracking", "Chaos engineering"],
                    "estimated_hours": 60,
                    "impact_statement": "Demonstrates production operations expertise",
                    "interview_talking_points": [
                        "Metric cardinality management",
                        "Alert fatigue prevention",
                        "Trace sampling strategies"
                    ]
                }
            ],
            "product_manager": [
                {
                    "id": "product_analytics_dashboard",
                    "title": "Product Analytics Dashboard",
                    "description": "Build a product analytics tool tracking user behavior and conversion funnels",
                    "problem_statement": "Show analytical thinking and data-driven decision making",
                    "difficulty": "intermediate",
                    "project_type": "original",
                    "skills_demonstrated": ["sql", "analytics", "visualization", "product_thinking"],
                    "tech_stack": {
                        "primary_language": "Python",
                        "frameworks": ["Streamlit", "Plotly"],
                        "databases": ["PostgreSQL", "ClickHouse"],
                        "tools": ["dbt", "Metabase"],
                        "deployment": "Streamlit Cloud",
                        "testing": ["pytest"]
                    },
                    "sample_features": [
                        "Event tracking implementation",
                        "Funnel analysis",
                        "Cohort retention",
                        "A/B test analysis",
                        "Feature adoption tracking",
                        "Executive dashboard"
                    ],
                    "stretch_goals": ["Predictive churn", "LTV modeling", "Experimentation platform"],
                    "estimated_hours": 50,
                    "impact_statement": "Shows ability to measure and drive product decisions",
                    "interview_talking_points": [
                        "Metric selection rationale",
                        "How insights drove decisions",
                        "Experimentation approach"
                    ]
                }
            ],
            "security_engineer": [
                {
                    "id": "security_scanner",
                    "title": "Automated Security Scanner",
                    "description": "Build a security scanning tool for web applications and APIs",
                    "problem_statement": "Demonstrate security expertise and automation skills",
                    "difficulty": "advanced",
                    "project_type": "original",
                    "skills_demonstrated": ["python", "security", "api", "automation"],
                    "tech_stack": {
                        "primary_language": "Python",
                        "frameworks": ["FastAPI", "asyncio"],
                        "databases": ["PostgreSQL", "Redis"],
                        "tools": ["Docker", "OWASP ZAP"],
                        "deployment": "Docker",
                        "testing": ["pytest"]
                    },
                    "sample_features": [
                        "Vulnerability scanning",
                        "OWASP Top 10 checks",
                        "API security testing",
                        "Report generation",
                        "CI/CD integration",
                        "Remediation suggestions"
                    ],
                    "stretch_goals": ["DAST integration", "Compliance checks", "Slack alerts"],
                    "estimated_hours": 80,
                    "impact_statement": "Shows practical security engineering skills",
                    "interview_talking_points": [
                        "Vulnerability prioritization",
                        "False positive handling",
                        "Integration with SDLC"
                    ]
                }
            ]
        }

        self._save_templates()

    def _save_templates(self) -> None:
        """Save templates to file"""
        templates_file = self.portfolio_dir / "project_templates.json"
        with open(templates_file, 'w') as f:
            json.dump(self.project_templates, f, indent=2)

    def _build_role_skill_map(self) -> None:
        """Build mapping of roles to required skills"""
        self.role_skill_map = {
            "software_engineer": ["programming", "system_design", "debugging", "testing", "git"],
            "frontend_developer": ["javascript", "react", "css", "html", "typescript", "accessibility"],
            "backend_developer": ["python", "sql", "api_design", "databases", "docker"],
            "data_scientist": ["python", "ml", "statistics", "sql", "visualization"],
            "ml_engineer": ["python", "ml", "mlops", "docker", "system_design"],
            "data_engineer": ["python", "sql", "etl", "spark", "airflow"],
            "devops_engineer": ["docker", "kubernetes", "terraform", "ci_cd", "linux"],
            "sre": ["linux", "monitoring", "kubernetes", "incident_management"],
            "product_manager": ["analytics", "communication", "strategy", "sql"],
            "security_engineer": ["security", "python", "networking", "linux"],
            "cloud_architect": ["aws", "architecture", "terraform", "networking"],
        }

    def generate_projects(
        self,
        target_role: str,
        current_skills: List[str],
        experience_level: str = "intermediate",
        num_projects: int = 5,
        interests: Optional[List[str]] = None
    ) -> List[ProjectRecommendation]:
        """
        Generate project recommendations for a target role.

        Args:
            target_role (str): Target role/career
            current_skills (List[str]): User's current skills
            experience_level (str): beginner/intermediate/advanced
            num_projects (int): Number of projects to recommend
            interests (Optional[List[str]]): User's interests

        Returns:
            List[ProjectRecommendation]: Recommended projects
        """
        # Normalize role
        role_key = self._normalize_role(target_role)

        # Get relevant templates
        templates = self._get_relevant_templates(role_key, current_skills, interests)

        # Score and rank projects
        recommendations = []
        for template in templates:
            project = self._create_project_from_template(template)

            # Calculate relevance
            relevance = self._calculate_relevance(project, current_skills, role_key)

            # Calculate skill coverage
            role_skills = set(self.role_skill_map.get(role_key, []))
            project_skills = set(project.skills_demonstrated)
            coverage = len(role_skills & project_skills) / max(len(role_skills), 1)

            # Filter by difficulty
            if experience_level == "beginner" and project.difficulty in [ProjectDifficulty.ADVANCED, ProjectDifficulty.EXPERT]:
                continue
            if experience_level == "advanced" and project.difficulty == ProjectDifficulty.BEGINNER:
                continue

            recommendations.append(ProjectRecommendation(
                project=project,
                relevance_score=relevance,
                skill_coverage=coverage,
                unique_value=self._get_unique_value(project),
                why_recommended=self._explain_recommendation(project, current_skills, target_role)
            ))

        # Sort by relevance
        recommendations.sort(key=lambda x: x.relevance_score, reverse=True)

        return recommendations[:num_projects]

    def _normalize_role(self, role: str) -> str:
        """Normalize role name"""
        role_lower = role.lower().replace(" ", "_").replace("-", "_")

        mappings = {
            "swe": "software_engineer",
            "frontend": "frontend_developer",
            "backend": "backend_developer",
            "fullstack": "software_engineer",
            "data_science": "data_scientist",
            "ml": "ml_engineer",
            "machine_learning": "ml_engineer",
            "devops": "devops_engineer",
            "pm": "product_manager",
            "security": "security_engineer",
        }

        return mappings.get(role_lower, role_lower)

    def _get_relevant_templates(
        self,
        role_key: str,
        current_skills: List[str],
        interests: Optional[List[str]]
    ) -> List[Dict]:
        """Get templates relevant to role"""
        templates = []

        # Primary role templates
        templates.extend(self.project_templates.get(role_key, []))

        # Related role templates
        related_roles = {
            "software_engineer": ["frontend_developer", "devops_engineer"],
            "data_scientist": ["ml_engineer", "data_engineer"],
            "devops_engineer": ["sre", "cloud_architect"],
            "frontend_developer": ["software_engineer"],
        }

        for related in related_roles.get(role_key, []):
            templates.extend(self.project_templates.get(related, [])[:1])

        return templates

    def _create_project_from_template(self, template: Dict) -> PortfolioProject:
        """Create PortfolioProject from template"""
        tech_data = template.get('tech_stack', {})
        tech_stack = TechStack(
            primary_language=tech_data.get('primary_language', 'Python'),
            frameworks=tech_data.get('frameworks', []),
            databases=tech_data.get('databases', []),
            tools=tech_data.get('tools', []),
            deployment=tech_data.get('deployment', 'Docker'),
            testing=tech_data.get('testing', [])
        )

        # Generate milestones
        milestones = self._generate_milestones(template)

        return PortfolioProject(
            id=template.get('id', ''),
            title=template.get('title', ''),
            description=template.get('description', ''),
            problem_statement=template.get('problem_statement', ''),
            target_roles=[template.get('target_role', 'software_engineer')],
            difficulty=ProjectDifficulty[template.get('difficulty', 'intermediate').upper()],
            project_type=ProjectType[template.get('project_type', 'original').upper()],
            skills_demonstrated=template.get('skills_demonstrated', []),
            tech_stack=tech_stack,
            milestones=milestones,
            estimated_hours=template.get('estimated_hours', 40),
            impact_statement=template.get('impact_statement', ''),
            interview_talking_points=template.get('interview_talking_points', []),
            differentiation_factors=self._get_differentiation_factors(template),
            resources=self._get_resources(template),
            sample_features=template.get('sample_features', []),
            stretch_goals=template.get('stretch_goals', []),
            github_topics=self._generate_github_topics(template)
        )

    def _generate_milestones(self, template: Dict) -> List[ProjectMilestone]:
        """Generate milestones for a project"""
        total_hours = template.get('estimated_hours', 40)
        features = template.get('sample_features', [])

        milestones = []

        # Setup milestone
        milestones.append(ProjectMilestone(
            name="Project Setup",
            description="Initialize project structure and development environment",
            deliverables=[
                "Repository initialized with README",
                "Development environment configured",
                "Basic project structure created",
                "CI/CD pipeline setup"
            ],
            estimated_hours=int(total_hours * 0.1),
            skills_demonstrated=["git", "development_setup"]
        ))

        # Core feature milestones
        features_per_milestone = max(len(features) // 3, 1)
        for i in range(0, len(features), features_per_milestone):
            milestone_features = features[i:i + features_per_milestone]
            milestones.append(ProjectMilestone(
                name=f"Core Features Phase {i // features_per_milestone + 1}",
                description=f"Implement {', '.join(milestone_features[:2])}",
                deliverables=milestone_features,
                estimated_hours=int(total_hours * 0.25),
                skills_demonstrated=template.get('skills_demonstrated', [])[:3]
            ))

        # Testing and documentation
        milestones.append(ProjectMilestone(
            name="Testing & Documentation",
            description="Comprehensive testing and documentation",
            deliverables=[
                "Unit tests with 80%+ coverage",
                "Integration tests",
                "API documentation",
                "README with setup instructions"
            ],
            estimated_hours=int(total_hours * 0.15),
            skills_demonstrated=["testing", "documentation"]
        ))

        # Deployment
        milestones.append(ProjectMilestone(
            name="Deployment & Polish",
            description="Deploy and finalize the project",
            deliverables=[
                "Production deployment",
                "Performance optimization",
                "Demo video/screenshots",
                "Portfolio write-up"
            ],
            estimated_hours=int(total_hours * 0.1),
            skills_demonstrated=["deployment", "devops"]
        ))

        return milestones

    def _get_differentiation_factors(self, template: Dict) -> List[str]:
        """Get factors that differentiate this project"""
        factors = [
            f"Demonstrates real-world {template.get('skills_demonstrated', [''])[0]} experience",
            "Goes beyond tutorial-level implementation",
            "Includes production-ready features like monitoring and testing"
        ]

        if template.get('difficulty') in ['advanced', 'expert']:
            factors.append("Shows ability to tackle complex technical challenges")

        return factors

    def _get_resources(self, template: Dict) -> List[Dict[str, str]]:
        """Get learning resources for the project"""
        skills = template.get('skills_demonstrated', [])
        resources = []

        skill_resources = {
            "python": {"name": "Real Python", "url": "https://realpython.com", "type": "tutorial"},
            "react": {"name": "React Docs", "url": "https://react.dev", "type": "documentation"},
            "docker": {"name": "Docker Docs", "url": "https://docs.docker.com", "type": "documentation"},
            "kubernetes": {"name": "Kubernetes Docs", "url": "https://kubernetes.io/docs", "type": "documentation"},
            "ml": {"name": "ML Course by Andrew Ng", "url": "https://coursera.org/learn/machine-learning", "type": "course"},
            "terraform": {"name": "Terraform Tutorials", "url": "https://learn.hashicorp.com/terraform", "type": "tutorial"},
            "distributed_systems": {"name": "Designing Data-Intensive Applications", "url": "https://dataintensive.net", "type": "book"},
        }

        for skill in skills[:4]:
            if skill in skill_resources:
                resources.append(skill_resources[skill])

        return resources

    def _generate_github_topics(self, template: Dict) -> List[str]:
        """Generate GitHub topics for the project"""
        topics = []

        # From skills
        for skill in template.get('skills_demonstrated', [])[:5]:
            topics.append(skill.replace("_", "-"))

        # From tech stack
        tech = template.get('tech_stack', {})
        if tech.get('primary_language'):
            topics.append(tech['primary_language'].lower())
        for framework in tech.get('frameworks', [])[:2]:
            topics.append(framework.lower().replace(" ", "-"))

        return list(set(topics))[:10]

    def _calculate_relevance(
        self,
        project: PortfolioProject,
        current_skills: List[str],
        target_role: str
    ) -> float:
        """Calculate project relevance score"""
        score = 0.0

        # Skill overlap with current skills (can leverage existing knowledge)
        current_set = set(s.lower() for s in current_skills)
        project_set = set(s.lower() for s in project.skills_demonstrated)
        overlap = len(current_set & project_set) / max(len(project_set), 1)
        score += overlap * 0.3

        # Target role alignment
        target_skills = set(self.role_skill_map.get(target_role, []))
        alignment = len(target_skills & project_set) / max(len(target_skills), 1)
        score += alignment * 0.4

        # Difficulty appropriateness
        score += 0.2  # Base score for being in templates

        # Differentiation bonus
        if project.difficulty in [ProjectDifficulty.ADVANCED, ProjectDifficulty.EXPERT]:
            score += 0.1

        return min(score, 1.0)

    def _get_unique_value(self, project: PortfolioProject) -> str:
        """Get unique value proposition of project"""
        if project.difficulty == ProjectDifficulty.EXPERT:
            return "Demonstrates senior-level technical expertise"
        elif "distributed" in project.title.lower():
            return "Shows understanding of scale and distributed systems"
        elif "real-time" in project.title.lower():
            return "Showcases real-time systems knowledge"
        elif project.project_type == ProjectType.ORIGINAL:
            return "Original project demonstrating creativity and initiative"
        else:
            return "Practical project with clear business value"

    def _explain_recommendation(
        self,
        project: PortfolioProject,
        current_skills: List[str],
        target_role: str
    ) -> str:
        """Explain why project is recommended"""
        reasons = []

        # Skill leverage
        current_set = set(s.lower() for s in current_skills)
        project_set = set(s.lower() for s in project.skills_demonstrated)
        overlap = current_set & project_set
        if overlap:
            reasons.append(f"Leverages your {list(overlap)[0]} experience")

        # Target role alignment
        reasons.append(f"Directly relevant to {target_role.replace('_', ' ')} roles")

        # Impact
        reasons.append(project.impact_statement[:80] if project.impact_statement else "")

        return ". ".join(filter(None, reasons))

    def customize_project(
        self,
        project: PortfolioProject,
        user_interests: List[str],
        preferred_tech: List[str]
    ) -> PortfolioProject:
        """
        Customize a project based on user preferences.

        Args:
            project (PortfolioProject): Base project
            user_interests (List[str]): User's interests
            preferred_tech (List[str]): Preferred technologies

        Returns:
            PortfolioProject: Customized project
        """
        # Create a copy with modifications
        customized = PortfolioProject(
            id=f"{project.id}_custom",
            title=project.title,
            description=project.description,
            problem_statement=project.problem_statement,
            target_roles=project.target_roles,
            difficulty=project.difficulty,
            project_type=project.project_type,
            skills_demonstrated=project.skills_demonstrated,
            tech_stack=project.tech_stack,
            milestones=project.milestones,
            estimated_hours=project.estimated_hours,
            impact_statement=project.impact_statement,
            interview_talking_points=project.interview_talking_points,
            differentiation_factors=project.differentiation_factors,
            resources=project.resources,
            sample_features=project.sample_features,
            stretch_goals=project.stretch_goals,
            github_topics=project.github_topics
        )

        # Add interest-based features
        if "ai" in [i.lower() for i in user_interests]:
            customized.stretch_goals.append("AI-powered recommendations")
        if "mobile" in [i.lower() for i in user_interests]:
            customized.stretch_goals.append("Mobile-responsive design or React Native app")

        return customized

    def get_ai_project_idea(
        self,
        target_role: str,
        skills: List[str],
        interests: List[str],
        experience_level: str
    ) -> Optional[Dict]:
        """
        Generate AI-powered custom project idea.

        Args:
            target_role (str): Target role
            skills (List[str]): Current skills
            interests (List[str]): User interests
            experience_level (str): Experience level

        Returns:
            Optional[Dict]: Generated project idea
        """
        if not self.gemini_model:
            return None

        prompt = f"""Generate a unique portfolio project idea for someone targeting a {target_role} role.

Current Skills: {', '.join(skills)}
Interests: {', '.join(interests)}
Experience Level: {experience_level}

Create a project that:
1. Demonstrates skills required for {target_role}
2. Leverages existing skills: {', '.join(skills[:3])}
3. Incorporates interests: {', '.join(interests[:3])}
4. Is appropriate for {experience_level} level

Provide:
1. Project title and one-line description
2. Problem it solves
3. Key features (5-7)
4. Tech stack recommendation
5. Estimated timeline
6. 3 interview talking points
7. What makes it stand out

Be specific and creative - avoid generic todo apps or weather apps."""

        try:
            model = genai.GenerativeModel(
                "gemini-2.0-flash",
                system_instruction="You are a senior software engineer and career coach helping developers build impressive portfolios."
            )
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.8,
                    max_output_tokens=700,
                ),
            )

            return {
                "target_role": target_role,
                "project_idea": response.text,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"AI generation failed: {e}")
            return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get service statistics"""
        total_projects = sum(len(v) for v in self.project_templates.values())
        return {
            "total_templates": total_projects,
            "roles_covered": len(self.project_templates),
            "difficulty_distribution": {
                "beginner": 2,
                "intermediate": 5,
                "advanced": 8,
                "expert": 2
            }
        }


# Prompt templates
PROJECT_GENERATION_PROMPT = """Generate a portfolio project idea for this developer:

**Profile:**
- Target Role: {target_role}
- Current Skills: {skills}
- Interests: {interests}
- Experience: {experience_level}

**Requirements:**
- Must demonstrate skills needed for {target_role}
- Should leverage existing skills where possible
- Should align with stated interests
- Difficulty appropriate for {experience_level}

**Provide:**
1. **Project Title**: Catchy, descriptive name
2. **One-liner**: What it does in one sentence
3. **Problem Statement**: What problem does it solve?
4. **Key Features**: 5-7 specific features
5. **Tech Stack**: Languages, frameworks, databases, tools
6. **Timeline**: Estimated hours/weeks
7. **Milestones**: 4-5 development phases
8. **Interview Talking Points**: 3 impressive things to discuss
9. **Differentiation**: What makes this stand out

**Example Output:**
For a Data Scientist targeting ML Engineer roles:

1. **Title**: Real-time Fraud Detection Pipeline
2. **One-liner**: ML pipeline that detects fraudulent transactions in real-time with <100ms latency
3. **Problem**: Demonstrate production ML beyond notebooks
4. **Features**:
   - Stream processing with Kafka
   - Feature engineering pipeline
   - Model serving with FastAPI
   - A/B testing framework
   - Monitoring dashboard
   - Drift detection alerts
5. **Tech Stack**: Python, Kafka, FastAPI, scikit-learn, MLflow, Docker, Grafana
6. **Timeline**: 80-100 hours over 6-8 weeks
7. **Milestones**: Setup -> Feature Pipeline -> Model Training -> Serving -> Monitoring
8. **Talking Points**: Latency optimization, handling concept drift, production tradeoffs
9. **Differentiation**: Shows complete MLOps lifecycle, not just model training

Create a similarly detailed and impressive project idea."""
