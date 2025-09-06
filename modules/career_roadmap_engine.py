import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import os

class CareerRoadmapEngine:
    def __init__(self, data_path: str = "data/careers/"):
        self.data_path = Path(data_path)
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.careers = self.load_careers()
        self.skill_levels = ["Beginner", "Junior", "Mid-Level", "Senior", "Expert"]
    
    def load_careers(self) -> Dict:
        careers = {}
        career_files = self.data_path.glob("*.json")
        
        for file in career_files:
            with open(file, 'r') as f:
                career_data = json.load(f)
                career_name = file.stem
                careers[career_name] = career_data
        
        # If no careers exist, create default ones
        if not careers:
            careers = self.create_default_careers()
        
        return careers
    
    def create_default_careers(self) -> Dict:
        default_careers = {
            "software_engineer": {
                "title": "Software Engineer",
                "description": "Design, develop, and maintain software applications",
                "levels": {
                    "Junior": {
                        "years": "0-2",
                        "salary_range": "$60,000 - $85,000",
                        "skills": ["Programming basics", "Git", "Data structures", "Algorithms", "Testing"],
                        "certifications": [],
                        "projects": [
                            "Personal portfolio website",
                            "Todo list application",
                            "Simple REST API"
                        ],
                        "milestones": [
                            "Complete CS fundamentals course",
                            "Build 3 personal projects",
                            "Contribute to open source"
                        ]
                    },
                    "Mid-Level": {
                        "years": "2-5",
                        "salary_range": "$85,000 - $120,000",
                        "skills": ["System design", "Database optimization", "CI/CD", "Cloud basics", "Agile"],
                        "certifications": ["AWS Certified Developer"],
                        "projects": [
                            "Full-stack web application",
                            "Microservices architecture",
                            "Mobile app"
                        ],
                        "milestones": [
                            "Lead a feature development",
                            "Mentor junior developers",
                            "Present at team meetings"
                        ]
                    },
                    "Senior": {
                        "years": "5-8",
                        "salary_range": "$120,000 - $160,000",
                        "skills": ["Architecture design", "Performance optimization", "Security", "Leadership", "DevOps"],
                        "certifications": ["AWS Solutions Architect", "Certified Kubernetes Administrator"],
                        "projects": [
                            "Enterprise application",
                            "Distributed system",
                            "Open source library"
                        ],
                        "milestones": [
                            "Architect major system",
                            "Lead team of 5+ developers",
                            "Drive technical decisions"
                        ]
                    },
                    "Expert": {
                        "years": "8+",
                        "salary_range": "$160,000+",
                        "skills": ["Strategic planning", "Innovation", "Cross-team collaboration", "Technical vision"],
                        "certifications": ["Technical leadership courses"],
                        "projects": [
                            "Company-wide initiatives",
                            "Technical standards",
                            "Innovation projects"
                        ],
                        "milestones": [
                            "Define technical roadmap",
                            "Speak at conferences",
                            "Patent or publication"
                        ]
                    }
                }
            },
            "data_scientist": {
                "title": "Data Scientist",
                "description": "Analyze complex data to help companies make better decisions",
                "levels": {
                    "Junior": {
                        "years": "0-2",
                        "salary_range": "$70,000 - $95,000",
                        "skills": ["Python/R", "Statistics", "SQL", "Data visualization", "Machine learning basics"],
                        "certifications": ["Google Data Analytics Certificate"],
                        "projects": [
                            "Exploratory data analysis project",
                            "Predictive model",
                            "Data dashboard"
                        ],
                        "milestones": [
                            "Complete ML course",
                            "Build portfolio on Kaggle",
                            "Master visualization tools"
                        ]
                    },
                    "Mid-Level": {
                        "years": "2-5",
                        "salary_range": "$95,000 - $130,000",
                        "skills": ["Deep learning", "Big data", "A/B testing", "Feature engineering", "Model deployment"],
                        "certifications": ["AWS Machine Learning Specialty"],
                        "projects": [
                            "End-to-end ML pipeline",
                            "Real-time analytics system",
                            "Computer vision project"
                        ],
                        "milestones": [
                            "Deploy models to production",
                            "Lead data science project",
                            "Publish analysis findings"
                        ]
                    },
                    "Senior": {
                        "years": "5-8",
                        "salary_range": "$130,000 - $170,000",
                        "skills": ["MLOps", "Research", "Business strategy", "Team leadership", "Advanced statistics"],
                        "certifications": ["Professional certifications in specialized areas"],
                        "projects": [
                            "Company ML platform",
                            "Novel algorithm implementation",
                            "Cross-functional initiatives"
                        ],
                        "milestones": [
                            "Build data science team",
                            "Define ML strategy",
                            "Publish research paper"
                        ]
                    },
                    "Expert": {
                        "years": "8+",
                        "salary_range": "$170,000+",
                        "skills": ["AI strategy", "Innovation leadership", "Executive communication", "Research direction"],
                        "certifications": ["Executive education programs"],
                        "projects": [
                            "AI transformation initiatives",
                            "Industry partnerships",
                            "Cutting-edge research"
                        ],
                        "milestones": [
                            "Lead AI/ML department",
                            "Keynote speaker",
                            "Industry recognition"
                        ]
                    }
                }
            },
            "product_manager": {
                "title": "Product Manager",
                "description": "Drive product strategy and execution from conception to launch",
                "levels": {
                    "Junior": {
                        "years": "0-2",
                        "salary_range": "$75,000 - $100,000",
                        "skills": ["User research", "Agile/Scrum", "Analytics", "Wireframing", "Communication"],
                        "certifications": ["Certified Scrum Product Owner"],
                        "projects": [
                            "Feature specification",
                            "User journey mapping",
                            "MVP launch"
                        ],
                        "milestones": [
                            "Complete PM course",
                            "Launch first feature",
                            "Conduct user interviews"
                        ]
                    },
                    "Mid-Level": {
                        "years": "2-5",
                        "salary_range": "$100,000 - $140,000",
                        "skills": ["Product strategy", "Roadmapping", "Stakeholder management", "Data analysis", "Go-to-market"],
                        "certifications": ["Product Management Certificate"],
                        "projects": [
                            "Full product launch",
                            "Market expansion",
                            "Platform integration"
                        ],
                        "milestones": [
                            "Own product line",
                            "Increase key metrics 20%+",
                            "Build cross-functional relationships"
                        ]
                    },
                    "Senior": {
                        "years": "5-8",
                        "salary_range": "$140,000 - $180,000",
                        "skills": ["Vision setting", "P&L management", "Team building", "Strategic partnerships", "Innovation"],
                        "certifications": ["Executive Product Management"],
                        "projects": [
                            "New product category",
                            "International launch",
                            "Platform strategy"
                        ],
                        "milestones": [
                            "Define product vision",
                            "Manage PM team",
                            "Drive $10M+ revenue"
                        ]
                    },
                    "Expert": {
                        "years": "8+",
                        "salary_range": "$180,000+",
                        "skills": ["Executive leadership", "Portfolio management", "Market strategy", "Board presentations"],
                        "certifications": ["MBA or equivalent experience"],
                        "projects": [
                            "Company product strategy",
                            "M&A integration",
                            "Market disruption"
                        ],
                        "milestones": [
                            "VP/CPO role",
                            "Industry thought leader",
                            "Portfolio transformation"
                        ]
                    }
                }
            }
        }
        
        # Save default careers to files
        for career_key, career_data in default_careers.items():
            file_path = self.data_path / f"{career_key}.json"
            with open(file_path, 'w') as f:
                json.dump(career_data, f, indent=2)
        
        return default_careers
    
    def generate_roadmap(self, user_profile: Dict) -> Dict:
        current_role = user_profile.get('current_role', '').lower().replace(' ', '_')
        target_role = user_profile.get('target_role', '').lower().replace(' ', '_')
        experience_years = user_profile.get('experience_years', 0)
        current_skills = user_profile.get('skills', [])
        
        # Find matching career path
        target_career = self.find_career(target_role)
        if not target_career:
            target_career = self.careers.get('software_engineer')  # Default fallback
        
        # Determine current and target levels
        current_level = self.determine_level(experience_years)
        target_level = self.determine_target_level(current_level, user_profile.get('timeline', '2 years'))
        
        # Generate personalized roadmap
        roadmap = {
            'current_position': {
                'role': current_role.replace('_', ' ').title(),
                'level': current_level,
                'experience': experience_years
            },
            'target_position': {
                'role': target_career['title'],
                'level': target_level,
                'expected_timeline': self.calculate_timeline(current_level, target_level)
            },
            'gap_analysis': self.analyze_skill_gaps(current_skills, target_career, target_level),
            'learning_path': self.create_learning_path(target_career, current_level, target_level),
            'milestones': self.create_milestones(target_career, current_level, target_level),
            'resources': self.recommend_resources(target_career, target_level)
        }
        
        return roadmap
    
    def find_career(self, role_name: str) -> Optional[Dict]:
        # Try exact match first
        if role_name in self.careers:
            return self.careers[role_name]
        
        # Try partial match
        for career_key, career_data in self.careers.items():
            if role_name in career_key or career_key in role_name:
                return career_data
            if role_name in career_data['title'].lower():
                return career_data
        
        return None
    
    def determine_level(self, experience_years: int) -> str:
        if experience_years < 2:
            return "Junior"
        elif experience_years < 5:
            return "Mid-Level"
        elif experience_years < 8:
            return "Senior"
        else:
            return "Expert"
    
    def determine_target_level(self, current_level: str, timeline: str) -> str:
        level_progression = ["Junior", "Mid-Level", "Senior", "Expert"]
        current_index = level_progression.index(current_level)
        
        # Parse timeline
        if "1 year" in timeline.lower():
            target_index = min(current_index + 1, len(level_progression) - 1)
        elif "2 year" in timeline.lower():
            target_index = min(current_index + 1, len(level_progression) - 1)
        elif "3 year" in timeline.lower() or "5 year" in timeline.lower():
            target_index = min(current_index + 2, len(level_progression) - 1)
        else:
            target_index = min(current_index + 1, len(level_progression) - 1)
        
        return level_progression[target_index]
    
    def calculate_timeline(self, current_level: str, target_level: str) -> str:
        level_progression = ["Junior", "Mid-Level", "Senior", "Expert"]
        current_index = level_progression.index(current_level)
        target_index = level_progression.index(target_level)
        
        years_needed = (target_index - current_index) * 2
        if years_needed == 0:
            return "Already at target level"
        elif years_needed == 2:
            return "1-2 years"
        elif years_needed == 4:
            return "3-5 years"
        else:
            return f"{years_needed-1}-{years_needed+1} years"
    
    def analyze_skill_gaps(self, current_skills: List[str], target_career: Dict, target_level: str) -> Dict:
        required_skills = []
        
        # Collect all skills up to target level
        level_progression = ["Junior", "Mid-Level", "Senior", "Expert"]
        target_index = level_progression.index(target_level)
        
        for i in range(target_index + 1):
            level = level_progression[i]
            if level in target_career['levels']:
                required_skills.extend(target_career['levels'][level]['skills'])
        
        # Normalize skills for comparison
        current_skills_lower = [skill.lower() for skill in current_skills]
        
        missing_skills = []
        for skill in required_skills:
            if skill.lower() not in current_skills_lower:
                missing_skills.append(skill)
        
        return {
            'current_skills': current_skills,
            'required_skills': required_skills,
            'missing_skills': missing_skills,
            'skill_match_percentage': round((1 - len(missing_skills) / len(required_skills)) * 100, 1) if required_skills else 0
        }
    
    def create_learning_path(self, target_career: Dict, current_level: str, target_level: str) -> List[Dict]:
        learning_path = []
        level_progression = ["Junior", "Mid-Level", "Senior", "Expert"]
        
        current_index = level_progression.index(current_level)
        target_index = level_progression.index(target_level)
        
        for i in range(current_index, target_index + 1):
            level = level_progression[i]
            if level in target_career['levels']:
                level_data = target_career['levels'][level]
                
                phase = {
                    'level': level,
                    'duration': level_data['years'],
                    'skills_to_learn': level_data['skills'],
                    'certifications': level_data['certifications'],
                    'projects': level_data['projects'],
                    'expected_salary': level_data['salary_range']
                }
                learning_path.append(phase)
        
        return learning_path
    
    def create_milestones(self, target_career: Dict, current_level: str, target_level: str) -> List[Dict]:
        milestones = []
        level_progression = ["Junior", "Mid-Level", "Senior", "Expert"]
        
        current_index = level_progression.index(current_level)
        target_index = level_progression.index(target_level)
        
        milestone_id = 1
        for i in range(current_index, target_index + 1):
            level = level_progression[i]
            if level in target_career['levels']:
                level_milestones = target_career['levels'][level]['milestones']
                
                for milestone in level_milestones:
                    milestones.append({
                        'id': milestone_id,
                        'level': level,
                        'description': milestone,
                        'completed': False,
                        'target_date': self.calculate_milestone_date(i - current_index, len(level_milestones))
                    })
                    milestone_id += 1
        
        return milestones
    
    def calculate_milestone_date(self, level_offset: int, total_milestones: int) -> str:
        # Calculate approximate date for milestone
        months_per_level = 24  # 2 years per level
        months_offset = level_offset * months_per_level
        
        target_date = datetime.now() + timedelta(days=months_offset * 30)
        return target_date.strftime("%B %Y")
    
    def recommend_resources(self, target_career: Dict, target_level: str) -> Dict:
        resources = {
            'courses': [
                "C# Corner courses relevant to " + target_career['title'],
                "Coursera specializations",
                "Udemy professional courses",
                "LinkedIn Learning paths"
            ],
            'books': [
                "Industry-standard textbooks",
                "Best practices guides",
                "Case study collections"
            ],
            'communities': [
                "Professional associations",
                "Online forums and Discord servers",
                "Local meetup groups",
                "LinkedIn groups"
            ],
            'practice': [
                "GitHub projects",
                "Kaggle competitions",
                "Hackathons",
                "Open source contributions"
            ]
        }
        
        return resources
    
    def get_career_list(self) -> List[str]:
        return [career_data['title'] for career_data in self.careers.values()]
    
    def get_career_details(self, career_name: str) -> Optional[Dict]:
        career = self.find_career(career_name.lower().replace(' ', '_'))
        return career