"""
Skills Assessment Module

Comprehensive skills and personality assessment system for students
Includes Holland codes (RIASEC), skill evaluation, and personality mapping
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from enum import Enum

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SkillLevel(Enum):
    """Skill proficiency levels"""
    BEGINNER = 1
    BASIC = 2
    INTERMEDIATE = 3
    ADVANCED = 4
    EXPERT = 5
    
    @classmethod
    def from_string(cls, level_str: str) -> 'SkillLevel':
        """Convert string to SkillLevel"""
        level_map = {
            "beginner": cls.BEGINNER,
            "basic": cls.BASIC,
            "intermediate": cls.INTERMEDIATE,
            "advanced": cls.ADVANCED,
            "expert": cls.EXPERT
        }
        return level_map.get(level_str.lower(), cls.BEGINNER)
    
    def to_description(self) -> str:
        """Get human-readable description"""
        descriptions = {
            self.BEGINNER: "Just starting to learn",
            self.BASIC: "Fundamental understanding",
            self.INTERMEDIATE: "Comfortable with common tasks",
            self.ADVANCED: "Can handle complex scenarios",
            self.EXPERT: "Master level proficiency"
        }
        return descriptions[self]


class HollandCode(Enum):
    """Holland's RIASEC personality types"""
    REALISTIC = "R"      # Doers - practical, physical, hands-on
    INVESTIGATIVE = "I"  # Thinkers - analytical, intellectual, scientific
    ARTISTIC = "A"       # Creators - creative, original, independent
    SOCIAL = "S"         # Helpers - cooperative, supporting, helping
    ENTERPRISING = "E"   # Persuaders - competitive, leadership, persuading
    CONVENTIONAL = "C"   # Organizers - detail-oriented, organizing, clerical


@dataclass
class SkillAssessmentResult:
    """Complete skill assessment results"""
    skill_levels: Dict[str, int]  # skill_name: level (1-5)
    skill_categories: Dict[str, List[str]]  # category: [skills]
    strengths: List[str]
    areas_for_improvement: List[str]
    recommended_skills: List[Dict[str, Any]]
    skill_gap_analysis: Dict[str, Any]
    learning_recommendations: List[str]
    

@dataclass
class InterestProfile:
    """Student interest profile based on Holland codes"""
    primary_code: str
    secondary_code: str
    tertiary_code: str
    scores: Dict[str, float]  # Holland code: score
    interest_areas: List[str]
    career_families: List[str]
    description: str


@dataclass
class PersonalityProfile:
    """Personality assessment using OCEAN/Big Five model"""
    openness: float  # 0-1 scale
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float
    dominant_traits: List[str]
    work_style: str
    team_role: str
    leadership_potential: float


@dataclass
class AcademicStrengthAnalysis:
    """Analysis of academic strengths and performance"""
    strong_subjects: List[str]
    weak_subjects: List[str]
    learning_style: str
    gpa_analysis: Dict[str, Any]
    academic_achievements: List[str]
    recommended_majors: List[str]
    study_recommendations: List[str]


class SkillsAssessment:
    """Main skills assessment system"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.load_assessment_data()
        
    def load_assessment_data(self):
        """Load or create assessment reference data"""
        # Skill categories and mappings
        self.skill_categories = {
            "technical": {
                "programming": ["Python", "Java", "JavaScript", "C++", "SQL", "HTML/CSS"],
                "data": ["Data Analysis", "Statistics", "Excel", "Tableau", "Power BI"],
                "engineering": ["CAD", "MATLAB", "Circuit Design", "3D Modeling"],
                "it": ["Network Admin", "Cybersecurity", "Cloud Computing", "DevOps"]
            },
            "creative": {
                "design": ["Graphic Design", "UI/UX", "Video Editing", "Photography"],
                "writing": ["Creative Writing", "Technical Writing", "Copywriting", "Journalism"],
                "arts": ["Drawing", "Music", "Acting", "Animation"]
            },
            "business": {
                "management": ["Project Management", "Team Leadership", "Strategic Planning"],
                "finance": ["Financial Analysis", "Accounting", "Budgeting", "Investment"],
                "marketing": ["Digital Marketing", "SEO", "Content Marketing", "Social Media"],
                "sales": ["B2B Sales", "Customer Relations", "Negotiation", "Presentation"]
            },
            "interpersonal": {
                "communication": ["Public Speaking", "Active Listening", "Written Communication"],
                "collaboration": ["Teamwork", "Conflict Resolution", "Mentoring", "Facilitation"],
                "leadership": ["Decision Making", "Delegation", "Motivation", "Vision Setting"]
            },
            "analytical": {
                "research": ["Research Methods", "Data Collection", "Literature Review"],
                "problem_solving": ["Critical Thinking", "Logic", "Systems Thinking"],
                "quantitative": ["Mathematics", "Statistical Analysis", "Modeling"]
            }
        }
        
        # Holland code career mappings
        self.holland_careers = {
            "R": {  # Realistic
                "careers": ["Engineer", "Mechanic", "Architect", "Pilot", "Farmer"],
                "interests": ["Building", "Fixing", "Working outdoors", "Using tools"],
                "skills": ["Mechanical", "Athletic", "Practical", "Physical coordination"]
            },
            "I": {  # Investigative
                "careers": ["Scientist", "Doctor", "Researcher", "Data Analyst", "Professor"],
                "interests": ["Research", "Analysis", "Learning", "Problem-solving"],
                "skills": ["Analytical", "Mathematical", "Scientific", "Critical thinking"]
            },
            "A": {  # Artistic
                "careers": ["Designer", "Writer", "Musician", "Actor", "Photographer"],
                "interests": ["Creating", "Expressing", "Designing", "Performing"],
                "skills": ["Creative", "Imaginative", "Expressive", "Original"]
            },
            "S": {  # Social
                "careers": ["Teacher", "Counselor", "Nurse", "Social Worker", "HR Manager"],
                "interests": ["Helping", "Teaching", "Caring", "Counseling"],
                "skills": ["Interpersonal", "Communication", "Empathy", "Patience"]
            },
            "E": {  # Enterprising
                "careers": ["Manager", "Salesperson", "Entrepreneur", "Lawyer", "CEO"],
                "interests": ["Leading", "Persuading", "Selling", "Managing"],
                "skills": ["Leadership", "Persuasion", "Negotiation", "Decision-making"]
            },
            "C": {  # Conventional
                "careers": ["Accountant", "Administrator", "Banker", "Clerk", "Auditor"],
                "interests": ["Organizing", "Data management", "Following procedures"],
                "skills": ["Detail-oriented", "Organizational", "Numerical", "Systematic"]
            }
        }
        
        # Learning style indicators
        self.learning_styles = {
            "visual": {
                "indicators": ["Prefer diagrams", "Good at reading maps", "Remember faces"],
                "study_methods": ["Mind maps", "Color coding", "Videos", "Infographics"]
            },
            "auditory": {
                "indicators": ["Remember conversations", "Enjoy discussions", "Think aloud"],
                "study_methods": ["Lectures", "Podcasts", "Group discussions", "Recording notes"]
            },
            "kinesthetic": {
                "indicators": ["Learn by doing", "Fidget while studying", "Good at sports"],
                "study_methods": ["Hands-on practice", "Lab work", "Field trips", "Role-play"]
            },
            "reading_writing": {
                "indicators": ["Love reading", "Take detailed notes", "Prefer written instructions"],
                "study_methods": ["Reading textbooks", "Writing summaries", "Lists", "Essays"]
            }
        }
    
    def assess_skill_level(self, skill_name: str, 
                          assessment_data: Dict[str, Any]) -> Tuple[SkillLevel, float]:
        """
        Assess skill level based on various inputs
        
        Args:
            skill_name: Name of the skill
            assessment_data: Dict containing:
                - self_rating: 1-5 scale
                - years_experience: float
                - projects_completed: int
                - certifications: List[str]
                - test_score: Optional[float] (0-100)
        
        Returns:
            Tuple of (SkillLevel, confidence_score)
        """
        score = 0.0
        confidence = 0.5
        
        # Self-assessment (weighted lower due to bias)
        if "self_rating" in assessment_data:
            score += assessment_data["self_rating"] * 0.2
            confidence += 0.1
        
        # Experience-based assessment
        if "years_experience" in assessment_data:
            years = assessment_data["years_experience"]
            if years >= 5:
                score += 5 * 0.3
            elif years >= 3:
                score += 4 * 0.3
            elif years >= 1:
                score += 3 * 0.3
            elif years >= 0.5:
                score += 2 * 0.3
            else:
                score += 1 * 0.3
            confidence += 0.15
        
        # Project-based assessment
        if "projects_completed" in assessment_data:
            projects = assessment_data["projects_completed"]
            if projects >= 10:
                score += 5 * 0.25
            elif projects >= 5:
                score += 4 * 0.25
            elif projects >= 3:
                score += 3 * 0.25
            elif projects >= 1:
                score += 2 * 0.25
            else:
                score += 1 * 0.25
            confidence += 0.15
        
        # Certification-based assessment
        if "certifications" in assessment_data and assessment_data["certifications"]:
            cert_count = len(assessment_data["certifications"])
            cert_score = min(cert_count * 1.5, 5)
            score += cert_score * 0.15
            confidence += 0.1
        
        # Test score if available
        if "test_score" in assessment_data:
            test_score = assessment_data["test_score"]
            score += (test_score / 20) * 0.1  # Convert 0-100 to 1-5
            confidence += 0.2  # High confidence from objective test
        
        # Normalize score to 1-5 range
        final_score = min(max(score, 1), 5)
        skill_level = SkillLevel(round(final_score))
        
        # Normalize confidence to 0-1 range
        confidence = min(confidence, 1.0)
        
        return skill_level, confidence
    
    def evaluate_skills(self, skills_data: Dict[str, Dict[str, Any]]) -> SkillAssessmentResult:
        """
        Comprehensive skill evaluation
        
        Args:
            skills_data: Dict of skill_name: assessment_data
        
        Returns:
            SkillAssessmentResult with complete analysis
        """
        skill_levels = {}
        skill_by_category = {cat: [] for cat in self.skill_categories}
        strengths = []
        improvements = []
        
        # Assess each skill
        for skill_name, assessment_data in skills_data.items():
            level, confidence = self.assess_skill_level(skill_name, assessment_data)
            skill_levels[skill_name] = level.value
            
            # Categorize skill
            skill_categorized = False
            for category, subcategories in self.skill_categories.items():
                for subcat, skills in subcategories.items():
                    if any(skill_name.lower() in s.lower() or s.lower() in skill_name.lower() 
                          for s in skills):
                        skill_by_category[category].append(skill_name)
                        skill_categorized = True
                        break
                if skill_categorized:
                    break
            
            # Identify strengths and improvements
            if level.value >= 4:
                strengths.append(f"{skill_name} ({level.to_description()})")
            elif level.value <= 2:
                improvements.append(skill_name)
        
        # Generate skill recommendations
        recommended_skills = self.recommend_skills_to_learn(
            skill_levels, 
            skill_by_category
        )
        
        # Perform gap analysis
        skill_gap_analysis = self.analyze_skill_gaps(skill_levels)
        
        # Generate learning recommendations
        learning_recommendations = self.generate_learning_plan(
            skill_levels,
            improvements,
            recommended_skills
        )
        
        return SkillAssessmentResult(
            skill_levels=skill_levels,
            skill_categories=skill_by_category,
            strengths=strengths,
            areas_for_improvement=improvements,
            recommended_skills=recommended_skills,
            skill_gap_analysis=skill_gap_analysis,
            learning_recommendations=learning_recommendations
        )
    
    def recommend_skills_to_learn(self, current_skills: Dict[str, int],
                                 categorized_skills: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Recommend complementary skills to learn"""
        recommendations = []
        
        # Analyze current skill distribution
        strong_categories = []
        for category, skills in categorized_skills.items():
            if skills:
                avg_level = np.mean([current_skills.get(s, 1) for s in skills])
                if avg_level >= 3:
                    strong_categories.append(category)
        
        # Recommend complementary skills
        complementary_map = {
            "technical": ["business", "interpersonal"],
            "creative": ["business", "technical"],
            "business": ["technical", "analytical"],
            "interpersonal": ["technical", "analytical"],
            "analytical": ["interpersonal", "creative"]
        }
        
        for strong_cat in strong_categories:
            if strong_cat in complementary_map:
                for comp_cat in complementary_map[strong_cat]:
                    # Find skills in complementary category not yet learned
                    for subcat, skills in self.skill_categories.get(comp_cat, {}).items():
                        for skill in skills[:2]:  # Recommend top 2 from each subcategory
                            if skill not in current_skills or current_skills[skill] < 3:
                                recommendations.append({
                                    "skill": skill,
                                    "category": comp_cat,
                                    "reason": f"Complements your {strong_cat} skills",
                                    "priority": "high" if skill not in current_skills else "medium",
                                    "estimated_time": "3-6 months"
                                })
        
        # Remove duplicates and limit recommendations
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec["skill"] not in seen:
                seen.add(rec["skill"])
                unique_recommendations.append(rec)
        
        return unique_recommendations[:10]
    
    def analyze_skill_gaps(self, skill_levels: Dict[str, int]) -> Dict[str, Any]:
        """Analyze gaps in skill portfolio"""
        analysis = {
            "missing_categories": [],
            "weak_areas": [],
            "balance_score": 0.0,
            "recommendations": []
        }
        
        # Check category coverage
        category_coverage = {}
        for category in self.skill_categories:
            category_skills = []
            for subcat, skills in self.skill_categories[category].items():
                for skill in skills:
                    if skill in skill_levels:
                        category_skills.append(skill_levels[skill])
            
            if category_skills:
                category_coverage[category] = np.mean(category_skills)
            else:
                analysis["missing_categories"].append(category)
        
        # Identify weak areas
        for category, avg_level in category_coverage.items():
            if avg_level < 2.5:
                analysis["weak_areas"].append({
                    "category": category,
                    "average_level": avg_level,
                    "improvement_needed": True
                })
        
        # Calculate balance score (0-1, higher is better)
        if category_coverage:
            analysis["balance_score"] = 1 - np.std(list(category_coverage.values())) / 2
        
        # Generate recommendations
        if analysis["missing_categories"]:
            analysis["recommendations"].append(
                f"Consider developing skills in: {', '.join(analysis['missing_categories'])}"
            )
        
        if analysis["weak_areas"]:
            weak_cats = [w["category"] for w in analysis["weak_areas"]]
            analysis["recommendations"].append(
                f"Strengthen your skills in: {', '.join(weak_cats)}"
            )
        
        if analysis["balance_score"] < 0.5:
            analysis["recommendations"].append(
                "Work on creating a more balanced skill portfolio across different areas"
            )
        
        return analysis
    
    def generate_learning_plan(self, skill_levels: Dict[str, int],
                              improvements: List[str],
                              recommended_skills: List[Dict]) -> List[str]:
        """Generate personalized learning recommendations"""
        plan = []
        
        # Phase 1: Strengthen weak skills
        if improvements:
            plan.append("Phase 1: Strengthen Foundation (1-3 months)")
            for skill in improvements[:3]:
                current_level = skill_levels.get(skill, 1)
                target_level = min(current_level + 2, 5)
                plan.append(f"  • Improve {skill} from level {current_level} to {target_level}")
        
        # Phase 2: Learn recommended skills
        if recommended_skills:
            plan.append("Phase 2: Expand Skill Set (3-6 months)")
            for rec in recommended_skills[:3]:
                plan.append(f"  • Learn {rec['skill']} ({rec['reason']})")
        
        # Phase 3: Advanced development
        advanced_skills = [s for s, l in skill_levels.items() if l >= 3]
        if advanced_skills:
            plan.append("Phase 3: Advanced Mastery (6-12 months)")
            for skill in advanced_skills[:2]:
                plan.append(f"  • Advance {skill} to expert level through projects and certifications")
        
        # Add general recommendations
        plan.append("\nGeneral Recommendations:")
        plan.append("  • Join online communities and forums in your areas of interest")
        plan.append("  • Work on real-world projects to apply your skills")
        plan.append("  • Seek mentorship from professionals in your field")
        plan.append("  • Maintain a portfolio showcasing your skill progression")
        
        return plan
    
    def assess_interests(self, interests: List[str], 
                        activities: List[str]) -> InterestProfile:
        """
        Assess interests and generate Holland code profile
        
        Args:
            interests: List of stated interests
            activities: List of activities/hobbies
        
        Returns:
            InterestProfile with Holland codes and career suggestions
        """
        holland_scores = {code.value: 0.0 for code in HollandCode}
        
        # Keywords for each Holland type
        holland_keywords = {
            "R": ["build", "fix", "outdoor", "hands-on", "mechanical", "physical", "tool",
                  "repair", "construct", "athletic", "nature", "practical"],
            "I": ["research", "analyze", "investigate", "science", "math", "study", "think",
                  "experiment", "solve", "discover", "theory", "data"],
            "A": ["create", "design", "art", "music", "write", "perform", "imagine",
                  "express", "innovate", "original", "aesthetic", "creative"],
            "S": ["help", "teach", "care", "serve", "counsel", "support", "nurture",
                  "collaborate", "volunteer", "community", "social", "team"],
            "E": ["lead", "manage", "sell", "persuade", "business", "entrepreneur",
                  "negotiate", "influence", "compete", "achieve", "organize"],
            "C": ["organize", "detail", "data", "file", "systematic", "procedure",
                  "accurate", "efficient", "administrative", "structure", "routine"]
        }
        
        # Score based on interests and activities
        all_items = interests + activities
        for item in all_items:
            item_lower = item.lower()
            for code, keywords in holland_keywords.items():
                for keyword in keywords:
                    if keyword in item_lower:
                        holland_scores[code] += 1.0
        
        # Normalize scores
        max_score = max(holland_scores.values()) if max(holland_scores.values()) > 0 else 1
        for code in holland_scores:
            holland_scores[code] = holland_scores[code] / max_score
        
        # Get top 3 codes
        sorted_codes = sorted(holland_scores.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_codes[0][0]
        secondary = sorted_codes[1][0] if len(sorted_codes) > 1 else primary
        tertiary = sorted_codes[2][0] if len(sorted_codes) > 2 else secondary
        
        # Generate interest areas and career families
        interest_areas = []
        career_families = []
        
        for code, score in sorted_codes[:3]:
            if score > 0:
                code_data = self.holland_careers[code]
                interest_areas.extend(code_data["interests"][:2])
                career_families.extend(code_data["careers"][:3])
        
        # Generate description
        description = self.generate_holland_description(primary, secondary, tertiary)
        
        return InterestProfile(
            primary_code=primary,
            secondary_code=secondary,
            tertiary_code=tertiary,
            scores=holland_scores,
            interest_areas=list(set(interest_areas))[:10],
            career_families=list(set(career_families))[:15],
            description=description
        )
    
    def generate_holland_description(self, primary: str, secondary: str, tertiary: str) -> str:
        """Generate description based on Holland code combination"""
        code_names = {
            "R": "Realistic", "I": "Investigative", "A": "Artistic",
            "S": "Social", "E": "Enterprising", "C": "Conventional"
        }
        
        descriptions = {
            "RI": "practical problem-solver who enjoys working with tools and technology",
            "RA": "hands-on creator who combines practical skills with artistic vision",
            "RS": "practical helper who enjoys hands-on work in service of others",
            "RE": "action-oriented leader who gets things done",
            "RC": "detail-oriented doer who values precision and quality",
            "IR": "analytical thinker who enjoys solving complex technical problems",
            "IA": "creative researcher who combines analysis with innovation",
            "IS": "thoughtful helper who uses knowledge to serve others",
            "IE": "strategic thinker who leads through expertise",
            "IC": "systematic analyst who values accuracy and order",
            "AI": "creative innovator who explores new ideas and concepts",
            "AR": "artistic creator who brings ideas to life",
            "AS": "creative communicator who inspires and helps others",
            "AE": "creative entrepreneur who leads with vision",
            "AC": "organized creative who balances artistry with structure",
            "SI": "caring educator who helps others learn and grow",
            "SA": "expressive helper who uses creativity to serve others",
            "SR": "practical caregiver who provides hands-on support",
            "SE": "inspiring leader who motivates and develops others",
            "SC": "organized helper who supports others through systems",
            "EI": "analytical leader who makes data-driven decisions",
            "EA": "visionary entrepreneur who innovates and inspires",
            "ER": "results-driven leader who takes action",
            "ES": "charismatic leader who builds strong teams",
            "EC": "organized manager who leads through systems",
            "CI": "methodical analyst who ensures accuracy",
            "CA": "detail-oriented creative who perfects their craft",
            "CR": "systematic implementer who follows through",
            "CS": "supportive organizer who helps others succeed",
            "CE": "efficient manager who optimizes operations"
        }
        
        combo = primary + secondary
        base_description = descriptions.get(combo, descriptions.get(secondary + primary, 
                                           "well-rounded individual with diverse interests"))
        
        return f"You are a {base_description}. Your {code_names[primary]} nature is " \
               f"complemented by {code_names[secondary]} tendencies, with some " \
               f"{code_names[tertiary]} characteristics adding depth to your profile."
    
    def assess_personality(self, assessment_responses: Dict[str, Any]) -> PersonalityProfile:
        """
        Assess personality using OCEAN/Big Five model
        
        Args:
            assessment_responses: Dictionary with personality assessment data
        
        Returns:
            PersonalityProfile with trait scores and insights
        """
        # Initialize scores (default to moderate)
        ocean_scores = {
            "openness": 0.5,
            "conscientiousness": 0.5,
            "extraversion": 0.5,
            "agreeableness": 0.5,
            "neuroticism": 0.5
        }
        
        # Process assessment responses
        # This would typically come from a standardized questionnaire
        if "questionnaire_scores" in assessment_responses:
            ocean_scores.update(assessment_responses["questionnaire_scores"])
        
        # Behavioral indicators can also inform scores
        if "behaviors" in assessment_responses:
            behaviors = assessment_responses["behaviors"]
            
            # Openness indicators
            if any(b in behaviors for b in ["tries_new_things", "creative", "curious"]):
                ocean_scores["openness"] = min(ocean_scores["openness"] + 0.2, 1.0)
            
            # Conscientiousness indicators
            if any(b in behaviors for b in ["organized", "punctual", "detail_oriented"]):
                ocean_scores["conscientiousness"] = min(ocean_scores["conscientiousness"] + 0.2, 1.0)
            
            # Extraversion indicators
            if any(b in behaviors for b in ["social", "talkative", "energetic"]):
                ocean_scores["extraversion"] = min(ocean_scores["extraversion"] + 0.2, 1.0)
            
            # Agreeableness indicators
            if any(b in behaviors for b in ["helpful", "cooperative", "trusting"]):
                ocean_scores["agreeableness"] = min(ocean_scores["agreeableness"] + 0.2, 1.0)
        
        # Identify dominant traits
        dominant_traits = []
        for trait, score in ocean_scores.items():
            if score >= 0.7:
                dominant_traits.append(trait.capitalize())
        
        # Determine work style
        work_style = self.determine_work_style(ocean_scores)
        
        # Determine team role
        team_role = self.determine_team_role(ocean_scores)
        
        # Calculate leadership potential
        leadership_potential = self.calculate_leadership_potential(ocean_scores)
        
        return PersonalityProfile(
            openness=ocean_scores["openness"],
            conscientiousness=ocean_scores["conscientiousness"],
            extraversion=ocean_scores["extraversion"],
            agreeableness=ocean_scores["agreeableness"],
            neuroticism=ocean_scores["neuroticism"],
            dominant_traits=dominant_traits,
            work_style=work_style,
            team_role=team_role,
            leadership_potential=leadership_potential
        )
    
    def determine_work_style(self, ocean_scores: Dict[str, float]) -> str:
        """Determine work style based on personality"""
        if ocean_scores["conscientiousness"] > 0.7 and ocean_scores["extraversion"] < 0.4:
            return "Independent and detail-oriented"
        elif ocean_scores["extraversion"] > 0.7 and ocean_scores["agreeableness"] > 0.6:
            return "Collaborative and people-focused"
        elif ocean_scores["openness"] > 0.7 and ocean_scores["conscientiousness"] < 0.5:
            return "Creative and flexible"
        elif ocean_scores["conscientiousness"] > 0.7 and ocean_scores["extraversion"] > 0.6:
            return "Organized leader"
        else:
            return "Balanced and adaptable"
    
    def determine_team_role(self, ocean_scores: Dict[str, float]) -> str:
        """Determine natural team role based on personality"""
        if ocean_scores["extraversion"] > 0.7 and ocean_scores["conscientiousness"] > 0.6:
            return "Team Leader"
        elif ocean_scores["openness"] > 0.7:
            return "Creative Innovator"
        elif ocean_scores["conscientiousness"] > 0.7:
            return "Quality Controller"
        elif ocean_scores["agreeableness"] > 0.7:
            return "Team Harmonizer"
        elif ocean_scores["extraversion"] > 0.7:
            return "Motivator"
        else:
            return "Flexible Contributor"
    
    def calculate_leadership_potential(self, ocean_scores: Dict[str, float]) -> float:
        """Calculate leadership potential score"""
        # Leadership correlates positively with extraversion, conscientiousness, 
        # and openness, negatively with neuroticism
        potential = (
            ocean_scores["extraversion"] * 0.3 +
            ocean_scores["conscientiousness"] * 0.3 +
            ocean_scores["openness"] * 0.2 +
            ocean_scores["agreeableness"] * 0.1 +
            (1 - ocean_scores["neuroticism"]) * 0.1
        )
        return round(potential, 2)
    
    def analyze_academic_strengths(self, academic_data: Dict[str, Any]) -> AcademicStrengthAnalysis:
        """
        Analyze academic performance and strengths
        
        Args:
            academic_data: Dictionary containing:
                - grades: Dict[subject: grade]
                - gpa: float
                - achievements: List[str]
                - preferred_subjects: List[str]
                - struggled_subjects: List[str]
                - learning_preferences: List[str]
        
        Returns:
            AcademicStrengthAnalysis with insights and recommendations
        """
        # Analyze grades to find strong/weak subjects
        grades = academic_data.get("grades", {})
        strong_subjects = []
        weak_subjects = []
        
        for subject, grade in grades.items():
            # Assuming grades are on 0-100 scale or letter grades
            if isinstance(grade, str):
                grade_value = self.convert_letter_grade(grade)
            else:
                grade_value = grade
            
            if grade_value >= 85:
                strong_subjects.append(subject)
            elif grade_value < 70:
                weak_subjects.append(subject)
        
        # Add user-specified preferences
        if "preferred_subjects" in academic_data:
            strong_subjects.extend(academic_data["preferred_subjects"])
        if "struggled_subjects" in academic_data:
            weak_subjects.extend(academic_data["struggled_subjects"])
        
        # Remove duplicates
        strong_subjects = list(set(strong_subjects))
        weak_subjects = list(set(weak_subjects))
        
        # Determine learning style
        learning_style = self.determine_learning_style(
            academic_data.get("learning_preferences", [])
        )
        
        # GPA analysis
        gpa = academic_data.get("gpa", 3.0)
        gpa_analysis = {
            "value": gpa,
            "percentile": self.calculate_gpa_percentile(gpa),
            "category": self.categorize_gpa(gpa),
            "trend": academic_data.get("gpa_trend", "stable")
        }
        
        # Academic achievements
        achievements = academic_data.get("achievements", [])
        
        # Recommend majors based on strengths
        recommended_majors = self.recommend_majors(strong_subjects, weak_subjects)
        
        # Generate study recommendations
        study_recommendations = self.generate_study_recommendations(
            learning_style,
            weak_subjects,
            gpa_analysis
        )
        
        return AcademicStrengthAnalysis(
            strong_subjects=strong_subjects,
            weak_subjects=weak_subjects,
            learning_style=learning_style,
            gpa_analysis=gpa_analysis,
            academic_achievements=achievements,
            recommended_majors=recommended_majors,
            study_recommendations=study_recommendations
        )
    
    def convert_letter_grade(self, letter_grade: str) -> float:
        """Convert letter grade to numerical value"""
        grade_map = {
            "A+": 97, "A": 93, "A-": 90,
            "B+": 87, "B": 83, "B-": 80,
            "C+": 77, "C": 73, "C-": 70,
            "D+": 67, "D": 63, "D-": 60,
            "F": 50
        }
        return grade_map.get(letter_grade.upper(), 75)
    
    def calculate_gpa_percentile(self, gpa: float) -> int:
        """Calculate GPA percentile (approximate)"""
        # Simplified percentile calculation
        if gpa >= 3.9:
            return 95
        elif gpa >= 3.7:
            return 85
        elif gpa >= 3.5:
            return 75
        elif gpa >= 3.3:
            return 65
        elif gpa >= 3.0:
            return 50
        elif gpa >= 2.7:
            return 35
        elif gpa >= 2.5:
            return 25
        else:
            return 15
    
    def categorize_gpa(self, gpa: float) -> str:
        """Categorize GPA performance"""
        if gpa >= 3.8:
            return "Excellent"
        elif gpa >= 3.5:
            return "Very Good"
        elif gpa >= 3.0:
            return "Good"
        elif gpa >= 2.5:
            return "Average"
        else:
            return "Below Average"
    
    def determine_learning_style(self, preferences: List[str]) -> str:
        """Determine primary learning style"""
        if not preferences:
            return "Mixed"
        
        style_scores = {
            "visual": 0,
            "auditory": 0,
            "kinesthetic": 0,
            "reading_writing": 0
        }
        
        # Score based on preferences
        for pref in preferences:
            pref_lower = pref.lower()
            if any(v in pref_lower for v in ["visual", "diagram", "chart", "video"]):
                style_scores["visual"] += 1
            if any(a in pref_lower for a in ["audio", "lecture", "discuss", "listen"]):
                style_scores["auditory"] += 1
            if any(k in pref_lower for k in ["hands-on", "practice", "do", "experiment"]):
                style_scores["kinesthetic"] += 1
            if any(r in pref_lower for r in ["read", "write", "note", "text"]):
                style_scores["reading_writing"] += 1
        
        # Return dominant style
        if max(style_scores.values()) == 0:
            return "Mixed"
        
        return max(style_scores, key=style_scores.get).replace("_", "/").title()
    
    def recommend_majors(self, strong_subjects: List[str], 
                        weak_subjects: List[str]) -> List[str]:
        """Recommend college majors based on academic strengths"""
        majors = []
        
        # Subject to major mapping
        subject_major_map = {
            "mathematics": ["Mathematics", "Statistics", "Data Science", "Engineering"],
            "physics": ["Physics", "Engineering", "Astronomy"],
            "chemistry": ["Chemistry", "Chemical Engineering", "Pharmacy"],
            "biology": ["Biology", "Pre-Med", "Biotechnology", "Environmental Science"],
            "computer science": ["Computer Science", "Software Engineering", "Information Systems"],
            "english": ["English", "Journalism", "Communications", "Creative Writing"],
            "history": ["History", "Political Science", "International Relations"],
            "economics": ["Economics", "Finance", "Business Administration"],
            "psychology": ["Psychology", "Neuroscience", "Counseling"],
            "art": ["Fine Arts", "Graphic Design", "Animation"],
            "music": ["Music", "Music Production", "Music Education"],
            "business": ["Business Administration", "Marketing", "Management"]
        }
        
        # Find majors based on strong subjects
        for subject in strong_subjects:
            subject_lower = subject.lower()
            for key, major_list in subject_major_map.items():
                if key in subject_lower:
                    majors.extend(major_list)
        
        # Remove duplicates and filter out majors related to weak subjects
        majors = list(set(majors))
        
        # Filter out majors that heavily rely on weak subjects
        filtered_majors = []
        for major in majors:
            major_lower = major.lower()
            if not any(weak.lower() in major_lower for weak in weak_subjects):
                filtered_majors.append(major)
        
        return filtered_majors[:10]  # Return top 10 recommendations
    
    def generate_study_recommendations(self, learning_style: str,
                                      weak_subjects: List[str],
                                      gpa_analysis: Dict) -> List[str]:
        """Generate personalized study recommendations"""
        recommendations = []
        
        # Learning style specific recommendations
        if learning_style == "Visual":
            recommendations.append("Use mind maps and diagrams to organize information")
            recommendations.append("Watch educational videos and animations")
        elif learning_style == "Auditory":
            recommendations.append("Record lectures and listen to them while reviewing")
            recommendations.append("Join study groups for discussion-based learning")
        elif learning_style == "Kinesthetic":
            recommendations.append("Use hands-on experiments and simulations")
            recommendations.append("Take frequent breaks and move while studying")
        elif learning_style == "Reading/Writing":
            recommendations.append("Take detailed notes and rewrite them for review")
            recommendations.append("Create summaries and outlines of material")
        
        # Weak subject recommendations
        if weak_subjects:
            recommendations.append(f"Seek tutoring for: {', '.join(weak_subjects[:3])}")
            recommendations.append("Form study groups for challenging subjects")
        
        # GPA-based recommendations
        if gpa_analysis["category"] in ["Below Average", "Average"]:
            recommendations.append("Meet with academic advisor to create improvement plan")
            recommendations.append("Utilize office hours to get help from professors")
        elif gpa_analysis["category"] in ["Excellent", "Very Good"]:
            recommendations.append("Consider advanced courses or honors programs")
            recommendations.append("Apply for academic scholarships and research opportunities")
        
        # General recommendations
        recommendations.append("Use spaced repetition for long-term retention")
        recommendations.append("Practice active recall instead of passive reading")
        recommendations.append("Set specific, measurable academic goals each semester")
        
        return recommendations
    
    def generate_comprehensive_report(self, 
                                     skills: SkillAssessmentResult,
                                     interests: InterestProfile,
                                     personality: PersonalityProfile,
                                     academic: AcademicStrengthAnalysis) -> Dict[str, Any]:
        """Generate comprehensive assessment report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "top_skills": skills.strengths[:5],
                "holland_code": f"{interests.primary_code}{interests.secondary_code}{interests.tertiary_code}",
                "personality_type": personality.work_style,
                "academic_strength": academic.gpa_analysis["category"],
                "leadership_potential": personality.leadership_potential
            },
            "detailed_results": {
                "skills": asdict(skills),
                "interests": asdict(interests),
                "personality": asdict(personality),
                "academic": asdict(academic)
            },
            "career_indicators": {
                "best_fit_careers": interests.career_families[:10],
                "recommended_majors": academic.recommended_majors[:5],
                "work_environment": personality.work_style,
                "team_role": personality.team_role
            },
            "development_plan": {
                "immediate_actions": skills.learning_recommendations[:3],
                "skill_priorities": skills.recommended_skills[:5],
                "study_strategies": academic.study_recommendations[:5]
            }
        }
        
        return report


def main():
    """Example usage of the skills assessment module"""
    
    # Initialize assessment system
    assessor = SkillsAssessment()
    
    # Example skill assessment data
    skills_data = {
        "Python": {
            "self_rating": 4,
            "years_experience": 2,
            "projects_completed": 5,
            "certifications": ["Python Institute PCEP"]
        },
        "Data Analysis": {
            "self_rating": 3,
            "years_experience": 1,
            "projects_completed": 3
        },
        "Public Speaking": {
            "self_rating": 2,
            "years_experience": 0.5,
            "projects_completed": 2
        },
        "Machine Learning": {
            "self_rating": 2,
            "years_experience": 0.5,
            "projects_completed": 1
        }
    }
    
    # Assess skills
    skill_results = assessor.evaluate_skills(skills_data)
    
    # Assess interests
    interests = ["technology", "problem-solving", "data analysis", "creating solutions"]
    activities = ["coding", "hackathons", "reading tech blogs", "building apps"]
    interest_profile = assessor.assess_interests(interests, activities)
    
    # Assess personality
    personality_data = {
        "questionnaire_scores": {
            "openness": 0.75,
            "conscientiousness": 0.65,
            "extraversion": 0.55,
            "agreeableness": 0.70,
            "neuroticism": 0.35
        },
        "behaviors": ["creative", "organized", "helpful"]
    }
    personality_profile = assessor.assess_personality(personality_data)
    
    # Assess academic strengths
    academic_data = {
        "grades": {
            "Mathematics": 90,
            "Computer Science": 92,
            "English": 78,
            "Physics": 85
        },
        "gpa": 3.6,
        "achievements": ["Dean's List", "Hackathon Winner", "Research Assistant"],
        "preferred_subjects": ["Computer Science", "Mathematics"],
        "struggled_subjects": ["English"],
        "learning_preferences": ["visual", "hands-on practice"]
    }
    academic_analysis = assessor.analyze_academic_strengths(academic_data)
    
    # Generate comprehensive report
    report = assessor.generate_comprehensive_report(
        skill_results,
        interest_profile,
        personality_profile,
        academic_analysis
    )
    
    # Display results
    print("\n" + "="*80)
    print("COMPREHENSIVE SKILLS ASSESSMENT REPORT")
    print("="*80)
    
    print("\n### SUMMARY ###")
    for key, value in report["summary"].items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    print("\n### TOP CAREER MATCHES ###")
    for i, career in enumerate(report["career_indicators"]["best_fit_careers"][:5], 1):
        print(f"{i}. {career}")
    
    print("\n### DEVELOPMENT PRIORITIES ###")
    print("\nImmediate Actions:")
    for action in report["development_plan"]["immediate_actions"]:
        print(f"  • {action}")
    
    print("\nSkills to Develop:")
    for skill in report["development_plan"]["skill_priorities"][:3]:
        print(f"  • {skill['skill']} - {skill['reason']}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()