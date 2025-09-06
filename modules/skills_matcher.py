import re
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher
import json
from pathlib import Path

class SkillsMatcher:
    def __init__(self, skills_db_path: str = "data/skills_db.json"):
        self.skills_db_path = Path(skills_db_path)
        self.skills_db = self.load_skills_database()
        self.skill_categories = self.organize_skills_by_category()
    
    def load_skills_database(self) -> Dict:
        if self.skills_db_path.exists():
            with open(self.skills_db_path, 'r') as f:
                return json.load(f)
        else:
            # Create default skills database
            default_skills = self.create_default_skills_db()
            self.skills_db_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.skills_db_path, 'w') as f:
                json.dump(default_skills, f, indent=2)
            return default_skills
    
    def create_default_skills_db(self) -> Dict:
        return {
            "programming_languages": {
                "Python": {"category": "programming", "difficulty": "medium", "demand": "very_high"},
                "JavaScript": {"category": "programming", "difficulty": "medium", "demand": "very_high"},
                "Java": {"category": "programming", "difficulty": "medium", "demand": "high"},
                "C++": {"category": "programming", "difficulty": "hard", "demand": "medium"},
                "C#": {"category": "programming", "difficulty": "medium", "demand": "high"},
                "TypeScript": {"category": "programming", "difficulty": "medium", "demand": "high"},
                "Go": {"category": "programming", "difficulty": "medium", "demand": "high"},
                "Rust": {"category": "programming", "difficulty": "hard", "demand": "medium"},
                "Swift": {"category": "programming", "difficulty": "medium", "demand": "medium"},
                "Kotlin": {"category": "programming", "difficulty": "medium", "demand": "medium"},
                "Ruby": {"category": "programming", "difficulty": "easy", "demand": "medium"},
                "PHP": {"category": "programming", "difficulty": "easy", "demand": "medium"},
                "R": {"category": "programming", "difficulty": "medium", "demand": "medium"},
                "SQL": {"category": "programming", "difficulty": "easy", "demand": "very_high"}
            },
            "frameworks": {
                "React": {"category": "frontend", "difficulty": "medium", "demand": "very_high"},
                "Angular": {"category": "frontend", "difficulty": "medium", "demand": "high"},
                "Vue.js": {"category": "frontend", "difficulty": "easy", "demand": "high"},
                "Django": {"category": "backend", "difficulty": "medium", "demand": "high"},
                "Flask": {"category": "backend", "difficulty": "easy", "demand": "medium"},
                "Spring Boot": {"category": "backend", "difficulty": "medium", "demand": "high"},
                "Express.js": {"category": "backend", "difficulty": "easy", "demand": "high"},
                "FastAPI": {"category": "backend", "difficulty": "easy", "demand": "high"},
                "Next.js": {"category": "fullstack", "difficulty": "medium", "demand": "high"},
                "Ruby on Rails": {"category": "fullstack", "difficulty": "medium", "demand": "medium"},
                ".NET": {"category": "backend", "difficulty": "medium", "demand": "high"},
                "Laravel": {"category": "backend", "difficulty": "medium", "demand": "medium"}
            },
            "cloud_platforms": {
                "AWS": {"category": "cloud", "difficulty": "hard", "demand": "very_high"},
                "Azure": {"category": "cloud", "difficulty": "hard", "demand": "high"},
                "Google Cloud": {"category": "cloud", "difficulty": "hard", "demand": "high"},
                "Docker": {"category": "devops", "difficulty": "medium", "demand": "very_high"},
                "Kubernetes": {"category": "devops", "difficulty": "hard", "demand": "very_high"},
                "Terraform": {"category": "devops", "difficulty": "medium", "demand": "high"},
                "Jenkins": {"category": "devops", "difficulty": "medium", "demand": "medium"},
                "GitHub Actions": {"category": "devops", "difficulty": "easy", "demand": "high"}
            },
            "databases": {
                "PostgreSQL": {"category": "database", "difficulty": "medium", "demand": "very_high"},
                "MySQL": {"category": "database", "difficulty": "easy", "demand": "high"},
                "MongoDB": {"category": "database", "difficulty": "easy", "demand": "high"},
                "Redis": {"category": "database", "difficulty": "medium", "demand": "high"},
                "Elasticsearch": {"category": "database", "difficulty": "hard", "demand": "medium"},
                "Oracle": {"category": "database", "difficulty": "hard", "demand": "medium"},
                "Cassandra": {"category": "database", "difficulty": "hard", "demand": "medium"}
            },
            "data_science": {
                "Machine Learning": {"category": "ai_ml", "difficulty": "hard", "demand": "very_high"},
                "Deep Learning": {"category": "ai_ml", "difficulty": "hard", "demand": "very_high"},
                "TensorFlow": {"category": "ai_ml", "difficulty": "hard", "demand": "high"},
                "PyTorch": {"category": "ai_ml", "difficulty": "hard", "demand": "high"},
                "Scikit-learn": {"category": "ai_ml", "difficulty": "medium", "demand": "high"},
                "Pandas": {"category": "data", "difficulty": "easy", "demand": "very_high"},
                "NumPy": {"category": "data", "difficulty": "easy", "demand": "very_high"},
                "Data Visualization": {"category": "data", "difficulty": "medium", "demand": "high"},
                "Statistics": {"category": "data", "difficulty": "medium", "demand": "high"},
                "NLP": {"category": "ai_ml", "difficulty": "hard", "demand": "high"},
                "Computer Vision": {"category": "ai_ml", "difficulty": "hard", "demand": "high"}
            },
            "soft_skills": {
                "Communication": {"category": "soft", "difficulty": "medium", "demand": "very_high"},
                "Leadership": {"category": "soft", "difficulty": "hard", "demand": "very_high"},
                "Problem Solving": {"category": "soft", "difficulty": "medium", "demand": "very_high"},
                "Teamwork": {"category": "soft", "difficulty": "easy", "demand": "very_high"},
                "Project Management": {"category": "soft", "difficulty": "medium", "demand": "high"},
                "Time Management": {"category": "soft", "difficulty": "medium", "demand": "high"},
                "Critical Thinking": {"category": "soft", "difficulty": "medium", "demand": "high"},
                "Adaptability": {"category": "soft", "difficulty": "medium", "demand": "high"},
                "Creativity": {"category": "soft", "difficulty": "medium", "demand": "medium"},
                "Presentation": {"category": "soft", "difficulty": "medium", "demand": "high"}
            },
            "tools": {
                "Git": {"category": "tool", "difficulty": "easy", "demand": "very_high"},
                "Jira": {"category": "tool", "difficulty": "easy", "demand": "high"},
                "Slack": {"category": "tool", "difficulty": "easy", "demand": "high"},
                "VS Code": {"category": "tool", "difficulty": "easy", "demand": "high"},
                "Postman": {"category": "tool", "difficulty": "easy", "demand": "high"},
                "Figma": {"category": "tool", "difficulty": "medium", "demand": "high"},
                "Tableau": {"category": "tool", "difficulty": "medium", "demand": "medium"},
                "Power BI": {"category": "tool", "difficulty": "medium", "demand": "medium"}
            }
        }
    
    def organize_skills_by_category(self) -> Dict:
        categories = {}
        for category, skills in self.skills_db.items():
            for skill_name, skill_info in skills.items():
                skill_category = skill_info['category']
                if skill_category not in categories:
                    categories[skill_category] = []
                categories[skill_category].append(skill_name)
        return categories
    
    def calculate_job_match_score(self, user_skills: List[str], job_requirements: Dict) -> Dict:
        job_skills = job_requirements.get('skills_required', [])
        experience_level = job_requirements.get('experience_level', 'Mid-Level')
        
        # Normalize skills for comparison
        user_skills_normalized = [self.normalize_skill(skill) for skill in user_skills]
        job_skills_normalized = [self.normalize_skill(skill) for skill in job_skills]
        
        # Calculate exact matches
        exact_matches = []
        partial_matches = []
        missing_skills = []
        
        for job_skill in job_skills_normalized:
            matched = False
            for user_skill in user_skills_normalized:
                similarity = self.calculate_similarity(user_skill, job_skill)
                if similarity >= 0.95:  # Exact match
                    exact_matches.append(job_skill)
                    matched = True
                    break
                elif similarity >= 0.7:  # Partial match
                    partial_matches.append((job_skill, user_skill, similarity))
                    matched = True
                    break
            
            if not matched:
                missing_skills.append(job_skill)
        
        # Calculate base score
        if job_skills:
            exact_score = len(exact_matches) / len(job_skills) * 60
            partial_score = len(partial_matches) / len(job_skills) * 20
        else:
            exact_score = 30  # Default if no skills specified
            partial_score = 10
        
        # Experience level bonus
        experience_bonus = self.calculate_experience_bonus(
            user_skills, experience_level
        )
        
        # Additional skills bonus (user has more than required)
        extra_skills = len(user_skills) - len(job_skills)
        extra_bonus = min(extra_skills * 2, 10) if extra_skills > 0 else 0
        
        # Calculate final score
        total_score = min(exact_score + partial_score + experience_bonus + extra_bonus, 100)
        
        # Determine match category
        if total_score >= 85:
            match_category = "Perfect Match"
        elif total_score >= 70:
            match_category = "Strong Match"
        elif total_score >= 50:
            match_category = "Good Match"
        elif total_score >= 30:
            match_category = "Possible Match"
        else:
            match_category = "Stretch Opportunity"
        
        return {
            'score': round(total_score, 1),
            'category': match_category,
            'exact_matches': exact_matches,
            'partial_matches': [(js, us, round(s*100, 1)) for js, us, s in partial_matches],
            'missing_skills': missing_skills,
            'breakdown': {
                'skill_match': round(exact_score + partial_score, 1),
                'experience_bonus': round(experience_bonus, 1),
                'extra_skills_bonus': round(extra_bonus, 1)
            },
            'recommendations': self.generate_recommendations(missing_skills, match_category)
        }
    
    def normalize_skill(self, skill: str) -> str:
        # Normalize skill name for comparison
        skill = skill.lower().strip()
        
        # Common abbreviations and variations
        replacements = {
            'js': 'javascript',
            'ts': 'typescript',
            'py': 'python',
            'ml': 'machine learning',
            'dl': 'deep learning',
            'ai': 'artificial intelligence',
            'db': 'database',
            'aws': 'amazon web services',
            'gcp': 'google cloud platform',
            'k8s': 'kubernetes',
            'ci/cd': 'continuous integration',
            'react.js': 'react',
            'vue.js': 'vue',
            'node.js': 'nodejs',
            'node': 'nodejs'
        }
        
        for abbr, full in replacements.items():
            if skill == abbr:
                skill = full
        
        return skill
    
    def calculate_similarity(self, skill1: str, skill2: str) -> float:
        # Calculate similarity between two skill names
        return SequenceMatcher(None, skill1, skill2).ratio()
    
    def calculate_experience_bonus(self, user_skills: List[str], experience_level: str) -> float:
        # Estimate experience based on number and complexity of skills
        skill_count = len(user_skills)
        
        # Count advanced skills
        advanced_skills = 0
        for skill in user_skills:
            skill_info = self.find_skill_info(skill)
            if skill_info and skill_info.get('difficulty') in ['hard', 'medium']:
                advanced_skills += 1
        
        # Calculate bonus based on experience level requirements
        if experience_level in ['Junior', 'Entry']:
            if skill_count >= 5:
                return 15
            elif skill_count >= 3:
                return 10
            else:
                return 5
        elif experience_level == 'Mid-Level':
            if advanced_skills >= 5 and skill_count >= 10:
                return 15
            elif advanced_skills >= 3 and skill_count >= 7:
                return 10
            else:
                return 5
        elif experience_level in ['Senior', 'Lead']:
            if advanced_skills >= 7 and skill_count >= 15:
                return 15
            elif advanced_skills >= 5 and skill_count >= 10:
                return 10
            else:
                return 3
        
        return 5  # Default bonus
    
    def find_skill_info(self, skill_name: str) -> Optional[Dict]:
        skill_normalized = self.normalize_skill(skill_name)
        
        for category, skills in self.skills_db.items():
            for skill, info in skills.items():
                if self.normalize_skill(skill) == skill_normalized:
                    return info
        
        return None
    
    def generate_recommendations(self, missing_skills: List[str], match_category: str) -> List[str]:
        recommendations = []
        
        if match_category == "Perfect Match":
            recommendations.append("You're an excellent fit for this position!")
            recommendations.append("Highlight your relevant project experience in your application")
            recommendations.append("Emphasize your expertise in the required skills")
        elif match_category == "Strong Match":
            recommendations.append("You have most of the required skills for this role")
            if missing_skills:
                recommendations.append(f"Consider learning: {', '.join(missing_skills[:3])}")
            recommendations.append("Focus on demonstrating practical experience with your matching skills")
        elif match_category == "Good Match":
            recommendations.append("You have a solid foundation for this role")
            recommendations.append(f"Priority skills to develop: {', '.join(missing_skills[:3])}")
            recommendations.append("Consider taking online courses or working on projects with these technologies")
        elif match_category == "Possible Match":
            recommendations.append("This role could be a growth opportunity")
            recommendations.append("Focus on transferable skills in your application")
            recommendations.append(f"Key skills to acquire: {', '.join(missing_skills[:5])}")
        else:
            recommendations.append("This is a stretch role that could accelerate your growth")
            recommendations.append("Consider it if you're looking for a significant challenge")
            recommendations.append("You'll need to demonstrate strong learning ability and motivation")
        
        return recommendations
    
    def analyze_skill_gaps(self, user_skills: List[str], target_skills: List[str]) -> Dict:
        user_skills_normalized = [self.normalize_skill(s) for s in user_skills]
        target_skills_normalized = [self.normalize_skill(s) for s in target_skills]
        
        # Find gaps
        missing_skills = []
        existing_skills = []
        
        for target_skill in target_skills_normalized:
            found = False
            for user_skill in user_skills_normalized:
                if self.calculate_similarity(user_skill, target_skill) >= 0.8:
                    existing_skills.append(target_skill)
                    found = True
                    break
            
            if not found:
                missing_skills.append(target_skill)
        
        # Prioritize missing skills
        prioritized_skills = self.prioritize_skills(missing_skills)
        
        # Generate learning plan
        learning_plan = self.generate_learning_plan(prioritized_skills)
        
        return {
            'existing_skills': existing_skills,
            'missing_skills': missing_skills,
            'skill_coverage': round(len(existing_skills) / len(target_skills) * 100, 1) if target_skills else 0,
            'prioritized_skills': prioritized_skills,
            'learning_plan': learning_plan,
            'estimated_time': self.estimate_learning_time(missing_skills)
        }
    
    def prioritize_skills(self, skills: List[str]) -> List[Dict]:
        prioritized = []
        
        for skill in skills:
            skill_info = self.find_skill_info(skill)
            if skill_info:
                priority_score = 0
                
                # Higher demand = higher priority
                if skill_info['demand'] == 'very_high':
                    priority_score += 3
                elif skill_info['demand'] == 'high':
                    priority_score += 2
                else:
                    priority_score += 1
                
                # Easier skills = higher priority (quicker wins)
                if skill_info['difficulty'] == 'easy':
                    priority_score += 2
                elif skill_info['difficulty'] == 'medium':
                    priority_score += 1
                
                prioritized.append({
                    'skill': skill,
                    'priority_score': priority_score,
                    'difficulty': skill_info['difficulty'],
                    'demand': skill_info['demand'],
                    'category': skill_info['category']
                })
            else:
                prioritized.append({
                    'skill': skill,
                    'priority_score': 1,
                    'difficulty': 'medium',
                    'demand': 'medium',
                    'category': 'unknown'
                })
        
        # Sort by priority score
        prioritized.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return prioritized
    
    def generate_learning_plan(self, prioritized_skills: List[Dict]) -> List[Dict]:
        learning_plan = []
        
        for i, skill_info in enumerate(prioritized_skills[:10]):  # Top 10 skills
            skill = skill_info['skill']
            difficulty = skill_info['difficulty']
            
            # Estimate learning time
            if difficulty == 'easy':
                time_estimate = "1-2 weeks"
            elif difficulty == 'medium':
                time_estimate = "3-4 weeks"
            else:
                time_estimate = "6-8 weeks"
            
            learning_plan.append({
                'order': i + 1,
                'skill': skill,
                'time_estimate': time_estimate,
                'resources': [
                    f"Online course for {skill}",
                    f"Practice projects with {skill}",
                    f"Documentation and tutorials for {skill}"
                ],
                'practice_project': f"Build a small project using {skill}"
            })
        
        return learning_plan
    
    def estimate_learning_time(self, skills: List[str]) -> str:
        total_weeks = 0
        
        for skill in skills:
            skill_info = self.find_skill_info(skill)
            if skill_info:
                if skill_info['difficulty'] == 'easy':
                    total_weeks += 1.5
                elif skill_info['difficulty'] == 'medium':
                    total_weeks += 3.5
                else:
                    total_weeks += 7
            else:
                total_weeks += 3  # Default
        
        if total_weeks < 4:
            return "Less than 1 month"
        elif total_weeks < 12:
            return f"{int(total_weeks/4)}-{int(total_weeks/4)+1} months"
        else:
            return f"{int(total_weeks/4)} months"
    
    def get_skill_suggestions(self, current_skills: List[str], career_path: str) -> List[str]:
        suggestions = []
        
        # Based on career path, suggest complementary skills
        career_skills_map = {
            'software_engineer': ['Git', 'Docker', 'AWS', 'Testing', 'CI/CD'],
            'data_scientist': ['Python', 'Machine Learning', 'Statistics', 'SQL', 'Visualization'],
            'product_manager': ['Analytics', 'Communication', 'Project Management', 'SQL', 'Design'],
            'ux_designer': ['Figma', 'User Research', 'Prototyping', 'HTML/CSS', 'JavaScript'],
            'devops_engineer': ['Docker', 'Kubernetes', 'AWS', 'Terraform', 'CI/CD']
        }
        
        if career_path in career_skills_map:
            recommended = career_skills_map[career_path]
            current_normalized = [self.normalize_skill(s) for s in current_skills]
            
            for skill in recommended:
                if self.normalize_skill(skill) not in current_normalized:
                    suggestions.append(skill)
        
        return suggestions[:5]  # Return top 5 suggestions