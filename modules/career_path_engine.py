"""
Career Path Recommendation Engine

Analyzes user profile and suggests optimal career transitions
with probability scores and detailed transition plans.

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


class TransitionDifficulty(Enum):
    """Career transition difficulty levels"""
    EASY = "easy"           # Similar role, minimal new skills
    MODERATE = "moderate"   # Some overlap, 3-6 months preparation
    CHALLENGING = "challenging"  # Significant change, 6-12 months
    DIFFICULT = "difficult"      # Major pivot, 12-24 months
    VERY_DIFFICULT = "very_difficult"  # Complete career change

    def to_months(self) -> Tuple[int, int]:
        """Get estimated months for transition"""
        ranges = {
            self.EASY: (1, 3),
            self.MODERATE: (3, 6),
            self.CHALLENGING: (6, 12),
            self.DIFFICULT: (12, 18),
            self.VERY_DIFFICULT: (18, 36)
        }
        return ranges[self]


class TransitionType(Enum):
    """Type of career transition"""
    LATERAL = "lateral"           # Same level, different specialty
    VERTICAL = "vertical"         # Promotion within same track
    DIAGONAL = "diagonal"         # Different track + level change
    PIVOT = "pivot"               # Complete change of direction
    SPECIALIZATION = "specialization"  # Narrowing focus


@dataclass
class CareerNode:
    """Represents a career/role in the graph"""
    id: str
    title: str
    category: str
    level: int  # 1-7 (entry to executive)
    required_skills: List[str]
    preferred_skills: List[str]
    typical_experience_years: int
    salary_range: Tuple[int, int]
    growth_rate: float  # percentage
    related_roles: List[str]
    transitions_from: List[str]  # Roles that commonly transition to this
    transitions_to: List[str]    # Roles this commonly transitions to


@dataclass
class UserCareerProfile:
    """User's career profile for path recommendations"""
    user_id: str
    current_role: str
    current_level: int
    years_experience: int
    skills: Dict[str, int]  # skill: proficiency (1-5)
    education: str
    certifications: List[str]
    interests: List[str]
    career_goals: List[str]
    constraints: Dict[str, Any]  # location, salary min, etc.
    strengths: List[str]
    weaknesses: List[str]


@dataclass
class TransitionStep:
    """A step in a career transition path"""
    action: str
    duration: str
    resources: List[str]
    milestones: List[str]
    skills_to_gain: List[str]
    estimated_cost: str


@dataclass
class CareerPathRecommendation:
    """A recommended career path"""
    target_role: str
    target_level: int
    match_score: float  # 0-1
    transition_probability: float  # 0-1
    transition_difficulty: TransitionDifficulty
    transition_type: TransitionType
    estimated_timeline: str
    salary_change: str  # e.g., "+25-35%"
    skill_gaps: List[str]
    skill_overlaps: List[str]
    transition_steps: List[TransitionStep]
    risks: List[str]
    opportunities: List[str]
    success_factors: List[str]
    similar_transitions: List[str]  # Example profiles who made this transition
    reasoning: str

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['transition_difficulty'] = self.transition_difficulty.value
        data['transition_type'] = self.transition_type.value
        return data


@dataclass
class CareerPathway:
    """A complete career pathway with multiple stages"""
    name: str
    description: str
    stages: List[CareerPathRecommendation]
    total_timeline: str
    total_salary_increase: str
    difficulty: str
    recommended_for: List[str]


class CareerPathEngine:
    """
    Career path recommendation engine.

    Analyzes user profiles and recommends optimal career transitions
    with detailed plans and probability scores.
    """

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the career path engine.

        Args:
            data_dir (str): Path to data directory. Defaults to "data".
        """
        self.data_dir = Path(data_dir)
        self.paths_dir = self.data_dir / "career_paths"
        self.paths_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger(__name__)

        # Career graph
        self.career_nodes: Dict[str, CareerNode] = {}
        self.transition_matrix: Dict[str, Dict[str, float]] = {}  # role -> role -> probability

        # Skill requirements
        self.role_skills: Dict[str, List[str]] = {}

        # Initialize Gemini
        self.gemini_model = None
        if GEMINI_AVAILABLE:
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel("gemini-2.0-flash")

        self._load_career_graph()
        self._build_transition_matrix()

        self.logger.info(f"CareerPathEngine initialized with {len(self.career_nodes)} career nodes")

    def _load_career_graph(self) -> None:
        """Load career graph from data"""
        graph_file = self.paths_dir / "career_graph.json"

        if graph_file.exists():
            try:
                with open(graph_file, 'r') as f:
                    data = json.load(f)
                    for node_data in data.get('nodes', []):
                        node = self._parse_career_node(node_data)
                        self.career_nodes[node.id] = node
                self.logger.info(f"Loaded {len(self.career_nodes)} career nodes")
            except Exception as e:
                self.logger.error(f"Error loading career graph: {e}")
                self._initialize_default_graph()
        else:
            self._initialize_default_graph()

    def _parse_career_node(self, data: Dict) -> CareerNode:
        """Parse career node from dictionary"""
        return CareerNode(
            id=data.get('id', ''),
            title=data.get('title', ''),
            category=data.get('category', ''),
            level=data.get('level', 3),
            required_skills=data.get('required_skills', []),
            preferred_skills=data.get('preferred_skills', []),
            typical_experience_years=data.get('typical_experience_years', 3),
            salary_range=tuple(data.get('salary_range', [80000, 120000])),
            growth_rate=data.get('growth_rate', 10.0),
            related_roles=data.get('related_roles', []),
            transitions_from=data.get('transitions_from', []),
            transitions_to=data.get('transitions_to', [])
        )

    def _initialize_default_graph(self) -> None:
        """Initialize with default career graph"""
        default_nodes = [
            # Engineering Track
            {
                "id": "junior_swe",
                "title": "Junior Software Engineer",
                "category": "Engineering",
                "level": 2,
                "required_skills": ["programming", "git", "problem-solving"],
                "preferred_skills": ["python", "javascript", "sql", "testing"],
                "typical_experience_years": 1,
                "salary_range": [70000, 95000],
                "growth_rate": 15.0,
                "related_roles": ["frontend_dev", "backend_dev"],
                "transitions_from": ["intern", "bootcamp_grad"],
                "transitions_to": ["mid_swe", "frontend_dev", "backend_dev"]
            },
            {
                "id": "mid_swe",
                "title": "Software Engineer",
                "category": "Engineering",
                "level": 3,
                "required_skills": ["programming", "system_design", "git", "debugging"],
                "preferred_skills": ["cloud", "docker", "testing", "ci_cd"],
                "typical_experience_years": 3,
                "salary_range": [100000, 145000],
                "growth_rate": 12.0,
                "related_roles": ["frontend_dev", "backend_dev", "fullstack"],
                "transitions_from": ["junior_swe"],
                "transitions_to": ["senior_swe", "tech_lead", "data_engineer"]
            },
            {
                "id": "senior_swe",
                "title": "Senior Software Engineer",
                "category": "Engineering",
                "level": 4,
                "required_skills": ["system_design", "architecture", "mentoring", "code_review"],
                "preferred_skills": ["distributed_systems", "cloud", "kubernetes", "leadership"],
                "typical_experience_years": 5,
                "salary_range": [140000, 200000],
                "growth_rate": 10.0,
                "related_roles": ["staff_swe", "tech_lead"],
                "transitions_from": ["mid_swe"],
                "transitions_to": ["staff_swe", "tech_lead", "eng_manager", "architect"]
            },
            {
                "id": "staff_swe",
                "title": "Staff Software Engineer",
                "category": "Engineering",
                "level": 5,
                "required_skills": ["architecture", "technical_leadership", "cross_team_collaboration"],
                "preferred_skills": ["system_design", "mentoring", "strategy"],
                "typical_experience_years": 8,
                "salary_range": [180000, 280000],
                "growth_rate": 8.0,
                "related_roles": ["principal_swe", "architect"],
                "transitions_from": ["senior_swe"],
                "transitions_to": ["principal_swe", "eng_director", "cto"]
            },
            {
                "id": "principal_swe",
                "title": "Principal Software Engineer",
                "category": "Engineering",
                "level": 6,
                "required_skills": ["technical_vision", "architecture", "influence"],
                "preferred_skills": ["strategy", "innovation", "thought_leadership"],
                "typical_experience_years": 12,
                "salary_range": [220000, 350000],
                "growth_rate": 6.0,
                "related_roles": ["distinguished_engineer"],
                "transitions_from": ["staff_swe"],
                "transitions_to": ["distinguished_engineer", "cto", "vp_engineering"]
            },
            # Frontend Track
            {
                "id": "frontend_dev",
                "title": "Frontend Developer",
                "category": "Engineering",
                "level": 3,
                "required_skills": ["javascript", "html", "css", "react"],
                "preferred_skills": ["typescript", "testing", "accessibility", "performance"],
                "typical_experience_years": 2,
                "salary_range": [90000, 140000],
                "growth_rate": 12.0,
                "related_roles": ["fullstack", "ux_engineer"],
                "transitions_from": ["junior_swe"],
                "transitions_to": ["senior_frontend", "fullstack", "ux_designer"]
            },
            {
                "id": "senior_frontend",
                "title": "Senior Frontend Developer",
                "category": "Engineering",
                "level": 4,
                "required_skills": ["react", "typescript", "performance", "architecture"],
                "preferred_skills": ["design_systems", "testing", "accessibility"],
                "typical_experience_years": 5,
                "salary_range": [130000, 190000],
                "growth_rate": 10.0,
                "related_roles": ["frontend_lead", "ux_engineer"],
                "transitions_from": ["frontend_dev"],
                "transitions_to": ["frontend_lead", "staff_frontend", "fullstack_lead"]
            },
            # Backend Track
            {
                "id": "backend_dev",
                "title": "Backend Developer",
                "category": "Engineering",
                "level": 3,
                "required_skills": ["python", "sql", "api_design", "databases"],
                "preferred_skills": ["cloud", "docker", "microservices", "redis"],
                "typical_experience_years": 2,
                "salary_range": [95000, 145000],
                "growth_rate": 12.0,
                "related_roles": ["fullstack", "data_engineer"],
                "transitions_from": ["junior_swe"],
                "transitions_to": ["senior_backend", "data_engineer", "devops"]
            },
            # Data Track
            {
                "id": "data_analyst",
                "title": "Data Analyst",
                "category": "Data",
                "level": 2,
                "required_skills": ["sql", "excel", "visualization", "statistics"],
                "preferred_skills": ["python", "tableau", "power_bi"],
                "typical_experience_years": 1,
                "salary_range": [60000, 90000],
                "growth_rate": 18.0,
                "related_roles": ["business_analyst", "data_scientist"],
                "transitions_from": ["analyst"],
                "transitions_to": ["senior_data_analyst", "data_scientist", "analytics_engineer"]
            },
            {
                "id": "data_scientist",
                "title": "Data Scientist",
                "category": "Data",
                "level": 3,
                "required_skills": ["python", "ml", "statistics", "sql"],
                "preferred_skills": ["deep_learning", "nlp", "experimentation", "visualization"],
                "typical_experience_years": 3,
                "salary_range": [110000, 170000],
                "growth_rate": 22.0,
                "related_roles": ["ml_engineer", "research_scientist"],
                "transitions_from": ["data_analyst", "junior_swe"],
                "transitions_to": ["senior_data_scientist", "ml_engineer", "data_lead"]
            },
            {
                "id": "ml_engineer",
                "title": "Machine Learning Engineer",
                "category": "Data",
                "level": 4,
                "required_skills": ["python", "ml", "mlops", "system_design"],
                "preferred_skills": ["deep_learning", "kubernetes", "distributed_systems"],
                "typical_experience_years": 4,
                "salary_range": [140000, 220000],
                "growth_rate": 28.0,
                "related_roles": ["data_scientist", "ml_researcher"],
                "transitions_from": ["data_scientist", "senior_swe"],
                "transitions_to": ["senior_ml_engineer", "ml_lead", "ai_researcher"]
            },
            {
                "id": "data_engineer",
                "title": "Data Engineer",
                "category": "Data",
                "level": 3,
                "required_skills": ["python", "sql", "etl", "data_warehousing"],
                "preferred_skills": ["spark", "airflow", "cloud", "kafka"],
                "typical_experience_years": 3,
                "salary_range": [110000, 165000],
                "growth_rate": 25.0,
                "related_roles": ["backend_dev", "analytics_engineer"],
                "transitions_from": ["backend_dev", "data_analyst"],
                "transitions_to": ["senior_data_engineer", "data_architect", "ml_engineer"]
            },
            # DevOps/Platform Track
            {
                "id": "devops_engineer",
                "title": "DevOps Engineer",
                "category": "Infrastructure",
                "level": 3,
                "required_skills": ["linux", "ci_cd", "docker", "scripting"],
                "preferred_skills": ["kubernetes", "terraform", "aws", "monitoring"],
                "typical_experience_years": 3,
                "salary_range": [105000, 160000],
                "growth_rate": 20.0,
                "related_roles": ["sre", "platform_engineer"],
                "transitions_from": ["backend_dev", "sysadmin"],
                "transitions_to": ["senior_devops", "sre", "cloud_architect"]
            },
            {
                "id": "sre",
                "title": "Site Reliability Engineer",
                "category": "Infrastructure",
                "level": 4,
                "required_skills": ["linux", "monitoring", "incident_management", "automation"],
                "preferred_skills": ["kubernetes", "distributed_systems", "chaos_engineering"],
                "typical_experience_years": 4,
                "salary_range": [130000, 200000],
                "growth_rate": 18.0,
                "related_roles": ["devops_engineer", "platform_engineer"],
                "transitions_from": ["devops_engineer", "backend_dev"],
                "transitions_to": ["senior_sre", "platform_lead", "infrastructure_manager"]
            },
            {
                "id": "cloud_architect",
                "title": "Cloud Architect",
                "category": "Infrastructure",
                "level": 5,
                "required_skills": ["aws", "architecture", "security", "networking"],
                "preferred_skills": ["multi_cloud", "cost_optimization", "compliance"],
                "typical_experience_years": 7,
                "salary_range": [160000, 250000],
                "growth_rate": 22.0,
                "related_roles": ["solutions_architect", "infrastructure_manager"],
                "transitions_from": ["senior_devops", "senior_swe"],
                "transitions_to": ["vp_infrastructure", "cto"]
            },
            # Product Track
            {
                "id": "associate_pm",
                "title": "Associate Product Manager",
                "category": "Product",
                "level": 2,
                "required_skills": ["communication", "analysis", "user_research"],
                "preferred_skills": ["sql", "wireframing", "agile"],
                "typical_experience_years": 1,
                "salary_range": [80000, 110000],
                "growth_rate": 15.0,
                "related_roles": ["product_analyst"],
                "transitions_from": ["analyst", "swe"],
                "transitions_to": ["product_manager"]
            },
            {
                "id": "product_manager",
                "title": "Product Manager",
                "category": "Product",
                "level": 3,
                "required_skills": ["strategy", "roadmapping", "stakeholder_management", "metrics"],
                "preferred_skills": ["sql", "user_research", "ab_testing"],
                "typical_experience_years": 3,
                "salary_range": [120000, 175000],
                "growth_rate": 12.0,
                "related_roles": ["senior_pm", "product_lead"],
                "transitions_from": ["associate_pm", "senior_swe", "data_analyst"],
                "transitions_to": ["senior_pm", "product_lead", "gpm"]
            },
            {
                "id": "senior_pm",
                "title": "Senior Product Manager",
                "category": "Product",
                "level": 4,
                "required_skills": ["strategy", "vision", "leadership", "cross_functional"],
                "preferred_skills": ["market_analysis", "pricing", "go_to_market"],
                "typical_experience_years": 5,
                "salary_range": [150000, 220000],
                "growth_rate": 10.0,
                "related_roles": ["gpm", "product_lead"],
                "transitions_from": ["product_manager"],
                "transitions_to": ["gpm", "director_product", "cpo"]
            },
            # Management Track
            {
                "id": "tech_lead",
                "title": "Tech Lead",
                "category": "Engineering Management",
                "level": 4,
                "required_skills": ["technical_leadership", "mentoring", "architecture"],
                "preferred_skills": ["project_management", "communication"],
                "typical_experience_years": 5,
                "salary_range": [145000, 210000],
                "growth_rate": 10.0,
                "related_roles": ["senior_swe", "eng_manager"],
                "transitions_from": ["senior_swe"],
                "transitions_to": ["eng_manager", "staff_swe", "architect"]
            },
            {
                "id": "eng_manager",
                "title": "Engineering Manager",
                "category": "Engineering Management",
                "level": 5,
                "required_skills": ["people_management", "hiring", "performance_management"],
                "preferred_skills": ["budgeting", "strategy", "process_improvement"],
                "typical_experience_years": 7,
                "salary_range": [170000, 260000],
                "growth_rate": 8.0,
                "related_roles": ["tech_lead", "senior_eng_manager"],
                "transitions_from": ["tech_lead", "senior_swe"],
                "transitions_to": ["senior_eng_manager", "director_engineering"]
            },
            {
                "id": "director_engineering",
                "title": "Director of Engineering",
                "category": "Engineering Management",
                "level": 6,
                "required_skills": ["org_leadership", "strategy", "scaling_teams"],
                "preferred_skills": ["executive_communication", "budgeting"],
                "typical_experience_years": 10,
                "salary_range": [220000, 350000],
                "growth_rate": 6.0,
                "related_roles": ["vp_engineering"],
                "transitions_from": ["eng_manager"],
                "transitions_to": ["vp_engineering", "cto"]
            },
            # Design Track
            {
                "id": "ux_designer",
                "title": "UX Designer",
                "category": "Design",
                "level": 3,
                "required_skills": ["user_research", "wireframing", "prototyping", "figma"],
                "preferred_skills": ["usability_testing", "design_systems", "html_css"],
                "typical_experience_years": 2,
                "salary_range": [85000, 130000],
                "growth_rate": 15.0,
                "related_roles": ["ui_designer", "product_designer"],
                "transitions_from": ["graphic_designer"],
                "transitions_to": ["senior_ux", "product_designer", "ux_researcher"]
            },
            {
                "id": "product_designer",
                "title": "Product Designer",
                "category": "Design",
                "level": 4,
                "required_skills": ["end_to_end_design", "systems_thinking", "collaboration"],
                "preferred_skills": ["prototyping", "user_research", "design_systems"],
                "typical_experience_years": 4,
                "salary_range": [120000, 180000],
                "growth_rate": 12.0,
                "related_roles": ["senior_ux", "design_lead"],
                "transitions_from": ["ux_designer", "ui_designer"],
                "transitions_to": ["senior_product_designer", "design_lead", "design_manager"]
            },
            # Security Track
            {
                "id": "security_engineer",
                "title": "Security Engineer",
                "category": "Security",
                "level": 3,
                "required_skills": ["security_fundamentals", "networking", "scripting"],
                "preferred_skills": ["penetration_testing", "cloud_security", "compliance"],
                "typical_experience_years": 3,
                "salary_range": [110000, 170000],
                "growth_rate": 25.0,
                "related_roles": ["devops_engineer", "security_analyst"],
                "transitions_from": ["swe", "sysadmin"],
                "transitions_to": ["senior_security_engineer", "security_architect"]
            },
        ]

        for node_data in default_nodes:
            node = self._parse_career_node(node_data)
            self.career_nodes[node.id] = node

        self._save_career_graph()
        self.logger.info(f"Initialized {len(self.career_nodes)} career nodes")

    def _save_career_graph(self) -> None:
        """Save career graph to file"""
        graph_file = self.paths_dir / "career_graph.json"
        data = {
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "nodes": [
                {
                    "id": node.id,
                    "title": node.title,
                    "category": node.category,
                    "level": node.level,
                    "required_skills": node.required_skills,
                    "preferred_skills": node.preferred_skills,
                    "typical_experience_years": node.typical_experience_years,
                    "salary_range": list(node.salary_range),
                    "growth_rate": node.growth_rate,
                    "related_roles": node.related_roles,
                    "transitions_from": node.transitions_from,
                    "transitions_to": node.transitions_to
                }
                for node in self.career_nodes.values()
            ]
        }

        with open(graph_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _build_transition_matrix(self) -> None:
        """Build transition probability matrix"""
        for node_id, node in self.career_nodes.items():
            self.transition_matrix[node_id] = {}

            for target_id in node.transitions_to:
                if target_id in self.career_nodes:
                    target = self.career_nodes[target_id]

                    # Calculate base transition probability
                    prob = self._calculate_transition_probability(node, target)
                    self.transition_matrix[node_id][target_id] = prob

    def _calculate_transition_probability(
        self,
        source: CareerNode,
        target: CareerNode
    ) -> float:
        """Calculate probability of transitioning between roles"""
        base_prob = 0.5

        # Same category bonus
        if source.category == target.category:
            base_prob += 0.15

        # Level adjacency
        level_diff = abs(target.level - source.level)
        if level_diff == 0:
            base_prob += 0.1  # Lateral move
        elif level_diff == 1:
            base_prob += 0.05  # Natural progression
        else:
            base_prob -= 0.1 * level_diff  # Harder for big jumps

        # Skill overlap
        source_skills = set(source.required_skills + source.preferred_skills)
        target_skills = set(target.required_skills)
        overlap = len(source_skills & target_skills) / max(len(target_skills), 1)
        base_prob += overlap * 0.2

        # Common transitions
        if target.id in source.transitions_to:
            base_prob += 0.15

        return min(max(base_prob, 0.1), 0.95)

    def recommend_paths(
        self,
        profile: UserCareerProfile,
        num_paths: int = 5,
        max_steps: int = 3
    ) -> List[CareerPathRecommendation]:
        """
        Recommend career paths based on user profile.

        Args:
            profile (UserCareerProfile): User's career profile
            num_paths (int): Number of paths to recommend
            max_steps (int): Maximum transition steps to consider

        Returns:
            List[CareerPathRecommendation]: Recommended career paths
        """
        # Find current role node
        current_node = self._find_matching_node(profile.current_role)
        if not current_node:
            self.logger.warning(f"No matching node for role: {profile.current_role}")
            current_node = self._find_closest_node(profile)

        # Get all potential target roles
        candidates = self._get_candidate_roles(current_node, profile, max_steps)

        # Score and rank candidates
        scored_paths = []
        for target_id, path_data in candidates.items():
            target_node = self.career_nodes[target_id]

            # Calculate match score
            match_score = self._calculate_match_score(profile, target_node)

            # Calculate transition probability
            trans_prob = self._calculate_path_probability(
                current_node.id if current_node else "mid_swe",
                target_id,
                path_data.get('path', [])
            )

            # Calculate skill gaps and overlaps
            profile_skills = set(profile.skills.keys())
            required_skills = set(target_node.required_skills)
            skill_gaps = list(required_skills - profile_skills)
            skill_overlaps = list(required_skills & profile_skills)

            # Determine difficulty
            difficulty = self._assess_transition_difficulty(
                current_node, target_node, skill_gaps, profile
            )

            # Determine transition type
            trans_type = self._determine_transition_type(current_node, target_node)

            # Calculate salary change
            current_salary_mid = (current_node.salary_range[0] + current_node.salary_range[1]) / 2 if current_node else 100000
            target_salary_mid = (target_node.salary_range[0] + target_node.salary_range[1]) / 2
            salary_change_pct = ((target_salary_mid - current_salary_mid) / current_salary_mid) * 100

            # Generate transition steps
            steps = self._generate_transition_steps(
                current_node, target_node, skill_gaps, profile
            )

            # Generate risks and opportunities
            risks = self._identify_risks(current_node, target_node, profile)
            opportunities = self._identify_opportunities(target_node, profile)

            # Create recommendation
            recommendation = CareerPathRecommendation(
                target_role=target_node.title,
                target_level=target_node.level,
                match_score=match_score,
                transition_probability=trans_prob,
                transition_difficulty=difficulty,
                transition_type=trans_type,
                estimated_timeline=f"{difficulty.to_months()[0]}-{difficulty.to_months()[1]} months",
                salary_change=f"{'+' if salary_change_pct > 0 else ''}{salary_change_pct:.0f}%",
                skill_gaps=skill_gaps[:5],
                skill_overlaps=skill_overlaps[:5],
                transition_steps=steps,
                risks=risks,
                opportunities=opportunities,
                success_factors=self._identify_success_factors(target_node, profile),
                similar_transitions=[],  # Would be populated from historical data
                reasoning=self._generate_reasoning(current_node, target_node, profile)
            )

            # Combined score for ranking
            combined_score = (match_score * 0.4) + (trans_prob * 0.3) + (1 - len(skill_gaps) / 10) * 0.3
            scored_paths.append((combined_score, recommendation))

        # Sort by combined score
        scored_paths.sort(key=lambda x: x[0], reverse=True)

        return [rec for _, rec in scored_paths[:num_paths]]

    def _find_matching_node(self, role: str) -> Optional[CareerNode]:
        """Find career node matching role name"""
        role_lower = role.lower().replace(" ", "_").replace("-", "_")

        # Direct match
        if role_lower in self.career_nodes:
            return self.career_nodes[role_lower]

        # Fuzzy match
        for node_id, node in self.career_nodes.items():
            if role_lower in node_id or role_lower in node.title.lower().replace(" ", "_"):
                return node

        return None

    def _find_closest_node(self, profile: UserCareerProfile) -> CareerNode:
        """Find closest matching node based on profile"""
        best_match = None
        best_score = 0

        for node in self.career_nodes.values():
            score = 0

            # Level match
            if abs(node.level - profile.current_level) <= 1:
                score += 0.3

            # Skill overlap
            profile_skills = set(profile.skills.keys())
            node_skills = set(node.required_skills)
            if node_skills:
                overlap = len(profile_skills & node_skills) / len(node_skills)
                score += overlap * 0.4

            # Experience match
            exp_diff = abs(node.typical_experience_years - profile.years_experience)
            if exp_diff <= 2:
                score += 0.3 * (1 - exp_diff / 5)

            if score > best_score:
                best_score = score
                best_match = node

        return best_match or list(self.career_nodes.values())[0]

    def _get_candidate_roles(
        self,
        current_node: Optional[CareerNode],
        profile: UserCareerProfile,
        max_steps: int
    ) -> Dict[str, Dict]:
        """Get candidate target roles within max_steps transitions"""
        candidates = {}

        if not current_node:
            # If no current node, consider all roles
            for node_id in self.career_nodes:
                candidates[node_id] = {'path': [], 'distance': 1}
            return candidates

        # BFS to find reachable roles
        visited = {current_node.id}
        queue = [(current_node.id, [], 0)]

        while queue:
            node_id, path, distance = queue.pop(0)

            if distance >= max_steps:
                continue

            node = self.career_nodes.get(node_id)
            if not node:
                continue

            for target_id in node.transitions_to:
                if target_id not in visited and target_id in self.career_nodes:
                    visited.add(target_id)
                    new_path = path + [target_id]
                    candidates[target_id] = {'path': new_path, 'distance': distance + 1}
                    queue.append((target_id, new_path, distance + 1))

        # Also consider related roles not in direct transitions
        for node_id, node in self.career_nodes.items():
            if node_id not in candidates:
                # Check if profile interests align
                if any(interest.lower() in node.category.lower() for interest in profile.interests):
                    candidates[node_id] = {'path': [node_id], 'distance': 2}

        return candidates

    def _calculate_match_score(
        self,
        profile: UserCareerProfile,
        target: CareerNode
    ) -> float:
        """Calculate how well profile matches target role"""
        score = 0.0
        weights = {'skills': 0.4, 'interests': 0.25, 'goals': 0.2, 'experience': 0.15}

        # Skill match
        profile_skills = set(profile.skills.keys())
        required = set(target.required_skills)
        preferred = set(target.preferred_skills)

        if required:
            req_match = len(profile_skills & required) / len(required)
            score += req_match * weights['skills'] * 0.7

        if preferred:
            pref_match = len(profile_skills & preferred) / len(preferred)
            score += pref_match * weights['skills'] * 0.3

        # Interest match
        target_keywords = [target.category.lower(), target.title.lower()]
        interest_match = sum(
            1 for interest in profile.interests
            if any(kw in interest.lower() for kw in target_keywords)
        )
        score += min(interest_match / max(len(profile.interests), 1), 1) * weights['interests']

        # Goal alignment
        goal_keywords = ['leadership', 'technical', 'management', 'specialist', 'architect']
        for goal in profile.career_goals:
            goal_lower = goal.lower()
            if 'leadership' in goal_lower and target.level >= 5:
                score += weights['goals'] * 0.5
            if 'technical' in goal_lower and 'engineer' in target.title.lower():
                score += weights['goals'] * 0.3

        # Experience fit
        exp_diff = abs(target.typical_experience_years - profile.years_experience)
        if exp_diff <= 2:
            score += weights['experience'] * (1 - exp_diff / 5)

        return min(score, 1.0)

    def _calculate_path_probability(
        self,
        source_id: str,
        target_id: str,
        path: List[str]
    ) -> float:
        """Calculate probability of completing the transition path"""
        if not path:
            # Direct transition
            return self.transition_matrix.get(source_id, {}).get(target_id, 0.3)

        # Multiply probabilities along path
        prob = 1.0
        current = source_id
        for next_id in path:
            step_prob = self.transition_matrix.get(current, {}).get(next_id, 0.3)
            prob *= step_prob
            current = next_id

        return prob

    def _assess_transition_difficulty(
        self,
        source: Optional[CareerNode],
        target: CareerNode,
        skill_gaps: List[str],
        profile: UserCareerProfile
    ) -> TransitionDifficulty:
        """Assess difficulty of transition"""
        difficulty_score = 0

        # Skill gap impact
        difficulty_score += len(skill_gaps) * 0.15

        # Level difference
        source_level = source.level if source else 3
        level_diff = target.level - source_level
        if level_diff > 1:
            difficulty_score += level_diff * 0.2

        # Category change
        if source and source.category != target.category:
            difficulty_score += 0.3

        # Experience gap
        exp_gap = max(0, target.typical_experience_years - profile.years_experience)
        difficulty_score += exp_gap * 0.05

        # Map to difficulty level
        if difficulty_score < 0.3:
            return TransitionDifficulty.EASY
        elif difficulty_score < 0.5:
            return TransitionDifficulty.MODERATE
        elif difficulty_score < 0.7:
            return TransitionDifficulty.CHALLENGING
        elif difficulty_score < 0.9:
            return TransitionDifficulty.DIFFICULT
        else:
            return TransitionDifficulty.VERY_DIFFICULT

    def _determine_transition_type(
        self,
        source: Optional[CareerNode],
        target: CareerNode
    ) -> TransitionType:
        """Determine type of career transition"""
        if not source:
            return TransitionType.PIVOT

        level_diff = target.level - source.level
        same_category = source.category == target.category

        if same_category and level_diff == 0:
            return TransitionType.LATERAL
        elif same_category and level_diff > 0:
            return TransitionType.VERTICAL
        elif not same_category and level_diff != 0:
            return TransitionType.DIAGONAL
        elif not same_category:
            return TransitionType.PIVOT
        else:
            return TransitionType.SPECIALIZATION

    def _generate_transition_steps(
        self,
        source: Optional[CareerNode],
        target: CareerNode,
        skill_gaps: List[str],
        profile: UserCareerProfile
    ) -> List[TransitionStep]:
        """Generate actionable transition steps"""
        steps = []

        # Step 1: Skill assessment
        steps.append(TransitionStep(
            action="Assess current skills and identify gaps",
            duration="1-2 weeks",
            resources=["Skills assessment platforms", "Peer feedback", "Manager 1:1"],
            milestones=["Complete self-assessment", "Get external feedback", "Create learning plan"],
            skills_to_gain=[],
            estimated_cost="Free"
        ))

        # Step 2: Skill development (per gap)
        for i, skill in enumerate(skill_gaps[:3]):  # Top 3 gaps
            steps.append(TransitionStep(
                action=f"Develop {skill} expertise",
                duration="4-8 weeks",
                resources=[f"Online courses for {skill}", "Practice projects", "Mentorship"],
                milestones=[
                    f"Complete beginner {skill} course",
                    f"Build project using {skill}",
                    f"Get certified in {skill}" if "cloud" in skill.lower() else f"Contribute to {skill} project"
                ],
                skills_to_gain=[skill],
                estimated_cost="$0-500"
            ))

        # Step 3: Build portfolio/experience
        steps.append(TransitionStep(
            action="Build relevant experience",
            duration="2-3 months",
            resources=["Side projects", "Open source", "Internal transfers"],
            milestones=[
                "Complete 1-2 portfolio projects",
                "Contribute to relevant open source",
                "Shadow someone in target role"
            ],
            skills_to_gain=skill_gaps[:2],
            estimated_cost="Free"
        ))

        # Step 4: Network and apply
        steps.append(TransitionStep(
            action="Network and apply for positions",
            duration="1-3 months",
            resources=["LinkedIn", "Industry events", "Referrals"],
            milestones=[
                f"Connect with 10+ {target.title}s",
                "Get 2-3 referrals",
                "Apply to 15-20 positions"
            ],
            skills_to_gain=["networking", "interviewing"],
            estimated_cost="$0-200"
        ))

        return steps

    def _identify_risks(
        self,
        source: Optional[CareerNode],
        target: CareerNode,
        profile: UserCareerProfile
    ) -> List[str]:
        """Identify risks in the career transition"""
        risks = []

        # Skill gap risk
        profile_skills = set(profile.skills.keys())
        required_skills = set(target.required_skills)
        gap_ratio = len(required_skills - profile_skills) / max(len(required_skills), 1)

        if gap_ratio > 0.5:
            risks.append("Significant skill gaps may extend transition timeline")

        # Experience risk
        if target.typical_experience_years > profile.years_experience + 3:
            risks.append("Target role typically requires more experience")

        # Market risk
        if target.growth_rate < 5:
            risks.append("Slower growth market may limit opportunities")

        # Category change risk
        if source and source.category != target.category:
            risks.append("Cross-functional transition may require starting at lower level")

        # Competition risk
        if target.category in ["Data", "Product"]:
            risks.append("High competition for these roles - strong portfolio essential")

        return risks[:4]

    def _identify_opportunities(
        self,
        target: CareerNode,
        profile: UserCareerProfile
    ) -> List[str]:
        """Identify opportunities from the transition"""
        opportunities = []

        # Growth opportunity
        if target.growth_rate > 15:
            opportunities.append(f"Fast-growing field ({target.growth_rate}% growth rate)")

        # Salary opportunity
        if target.salary_range[1] > 150000:
            opportunities.append(f"High earning potential (up to ${target.salary_range[1]:,})")

        # Skill leverage
        profile_skills = set(profile.skills.keys())
        target_skills = set(target.required_skills)
        overlap = len(profile_skills & target_skills)
        if overlap >= 2:
            opportunities.append(f"Can leverage {overlap} existing skills")

        # Career path opportunities
        if target.transitions_to:
            next_roles = [self.career_nodes[r].title for r in target.transitions_to[:2]
                         if r in self.career_nodes]
            if next_roles:
                opportunities.append(f"Opens paths to: {', '.join(next_roles)}")

        return opportunities[:4]

    def _identify_success_factors(
        self,
        target: CareerNode,
        profile: UserCareerProfile
    ) -> List[str]:
        """Identify key success factors for the transition"""
        factors = []

        # Skill-based factors
        for skill in target.required_skills[:2]:
            factors.append(f"Strong proficiency in {skill}")

        # Experience factors
        factors.append("Relevant project experience demonstrating skills")

        # Network factors
        factors.append(f"Connections in the {target.category} field")

        # Attitude factors
        factors.append("Proactive learning and adaptability")

        return factors[:4]

    def _generate_reasoning(
        self,
        source: Optional[CareerNode],
        target: CareerNode,
        profile: UserCareerProfile
    ) -> str:
        """Generate reasoning for the recommendation"""
        reasons = []

        # Skill alignment
        profile_skills = set(profile.skills.keys())
        required = set(target.required_skills)
        overlap = profile_skills & required
        if overlap:
            reasons.append(f"Your {', '.join(list(overlap)[:2])} skills transfer directly")

        # Interest alignment
        for interest in profile.interests[:2]:
            if interest.lower() in target.category.lower() or interest.lower() in target.title.lower():
                reasons.append(f"Aligns with your interest in {interest}")
                break

        # Growth potential
        if target.growth_rate > 15:
            reasons.append(f"Strong market growth ({target.growth_rate}%)")

        # Logical progression
        if source and target.id in source.transitions_to:
            reasons.append("Natural career progression from current role")

        return ". ".join(reasons) if reasons else "Good match based on profile analysis"

    def get_ai_path_analysis(
        self,
        profile: UserCareerProfile,
        target_role: str
    ) -> Optional[Dict]:
        """Get AI-powered career path analysis"""
        if not self.gemini_model:
            return None

        target_node = self._find_matching_node(target_role)
        current_node = self._find_matching_node(profile.current_role)

        prompt = f"""Analyze this career transition:

Current Role: {profile.current_role} ({profile.years_experience} years experience)
Target Role: {target_role}
Current Skills: {', '.join(list(profile.skills.keys())[:10])}
Interests: {', '.join(profile.interests[:5])}
Career Goals: {', '.join(profile.career_goals[:3])}

{f"Required for target: {', '.join(target_node.required_skills)}" if target_node else ""}

Provide:
1. Feasibility assessment (realistic timeline and probability)
2. 3 biggest challenges they'll face
3. Step-by-step 6-month action plan
4. Specific resources (courses, certifications, communities)
5. Alternative paths if this doesn't work out

Be specific and actionable."""

        try:
            model = genai.GenerativeModel(
                "gemini-2.0-flash",
                system_instruction="You are an expert career coach specializing in tech career transitions."
            )
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=800,
                ),
            )

            return {
                "profile": profile.user_id,
                "target_role": target_role,
                "analysis": response.text,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"AI analysis failed: {e}")
            return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics"""
        categories = {}
        for node in self.career_nodes.values():
            categories[node.category] = categories.get(node.category, 0) + 1

        return {
            "total_career_nodes": len(self.career_nodes),
            "categories": categories,
            "total_transitions": sum(len(t) for t in self.transition_matrix.values()),
            "avg_transitions_per_role": sum(len(t) for t in self.transition_matrix.values()) / max(len(self.transition_matrix), 1)
        }


# Prompt templates
CAREER_PATH_ANALYSIS_PROMPT = """You are an expert career coach analyzing a career transition.

**Current State:**
- Role: {current_role}
- Experience: {years_experience} years
- Skills: {current_skills}
- Interests: {interests}
- Goals: {career_goals}

**Target State:**
- Role: {target_role}
- Required Skills: {required_skills}
- Typical Experience: {typical_experience} years
- Salary Range: {salary_range}

**Analysis Required:**
1. Transition Feasibility (probability and timeline)
2. Top 3 Challenges with mitigation strategies
3. 6-Month Action Plan (monthly milestones)
4. Specific Resources (courses, certifications, communities)
5. Alternative Paths if primary fails

**Example Analysis:**
For Data Analyst -> ML Engineer:

1. Feasibility: 70% probability over 12-18 months. Strong foundation in data skills provides good starting point.

2. Challenges:
   - Deep ML theory gap: Mitigate with Andrew Ng's courses + hands-on Kaggle
   - Production ML experience: Seek internal ML projects or contribute to open source
   - Interview preparation: LeetCode ML problems + system design for ML

3. 6-Month Plan:
   - Month 1-2: Complete ML fundamentals (Coursera ML Specialization)
   - Month 3-4: Build 2 end-to-end ML projects for portfolio
   - Month 5-6: Apply MLOps skills, deploy model to production

4. Resources:
   - Courses: fast.ai, Coursera ML, CS229
   - Certifications: AWS ML Specialty, TensorFlow Developer
   - Communities: MLOps Community, Kaggle, r/MachineLearning

5. Alternatives:
   - Analytics Engineer (lower bar, still ML-adjacent)
   - Data Engineer with ML focus
   - ML Product Manager (leverages domain knowledge)

Provide equally specific analysis for the given transition."""
