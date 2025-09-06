import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
import re

class ONetScraper:
    def __init__(self, output_path: str = "data/careers/"):
        self.base_url = "https://www.onetonline.org"
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def get_popular_careers(self, limit: int = 50) -> List[Dict]:
        """Get list of popular careers from O*NET"""
        careers = []
        
        # O*NET Hot Technologies and High Growth careers
        hot_careers_urls = [
            "/find/bright?b=1",  # Bright Outlook occupations
            "/find/stem",  # STEM careers
            "/find/green",  # Green careers
        ]
        
        # Also include common career categories
        career_categories = {
            "technology": [
                "Software Developers",
                "Data Scientists", 
                "Information Security Analysts",
                "Web Developers",
                "Database Administrators",
                "Computer Systems Analysts",
                "Network Administrators",
                "Computer Programmers",
                "DevOps Engineers",
                "Cloud Architects"
            ],
            "healthcare": [
                "Registered Nurses",
                "Physicians",
                "Medical Assistants",
                "Physical Therapists",
                "Pharmacists",
                "Dental Hygienists",
                "Medical Technologists",
                "Healthcare Administrators"
            ],
            "business": [
                "Management Analysts",
                "Financial Analysts",
                "Marketing Managers",
                "Human Resources Specialists",
                "Accountants",
                "Project Managers",
                "Business Analysts",
                "Operations Managers",
                "Sales Managers",
                "Product Managers"
            ],
            "engineering": [
                "Mechanical Engineers",
                "Electrical Engineers",
                "Civil Engineers",
                "Chemical Engineers",
                "Aerospace Engineers",
                "Environmental Engineers",
                "Industrial Engineers",
                "Biomedical Engineers"
            ],
            "education": [
                "Elementary School Teachers",
                "High School Teachers",
                "Instructional Designers",
                "Training Specialists",
                "Education Administrators",
                "Special Education Teachers"
            ],
            "creative": [
                "Graphic Designers",
                "UX/UI Designers",
                "Content Writers",
                "Video Editors",
                "Photographers",
                "Art Directors",
                "Multimedia Artists"
            ],
            "trades": [
                "Electricians",
                "Plumbers",
                "HVAC Technicians",
                "Automotive Technicians",
                "Construction Managers",
                "Carpenters",
                "Welders"
            ],
            "science": [
                "Research Scientists",
                "Laboratory Technicians",
                "Environmental Scientists",
                "Chemists",
                "Biologists",
                "Physicists",
                "Geologists"
            ]
        }
        
        # Process each category
        for category, career_list in career_categories.items():
            for career_name in career_list[:limit//len(career_categories)]:
                career_data = self.create_career_template(career_name, category)
                careers.append(career_data)
                
                # Save individual career file
                self.save_career_file(career_data)
                
                # Be respectful with requests
                time.sleep(0.5)
        
        return careers
    
    def create_career_template(self, career_name: str, category: str) -> Dict:
        """Create a comprehensive career template with progression levels"""
        
        # Base salary estimates by category
        base_salaries = {
            "technology": 95000,
            "healthcare": 85000,
            "business": 80000,
            "engineering": 90000,
            "education": 55000,
            "creative": 60000,
            "trades": 55000,
            "science": 70000
        }
        
        base_salary = base_salaries.get(category, 65000)
        
        # Generate career ID
        career_id = career_name.lower().replace(" ", "_").replace("/", "_")
        
        career_data = {
            "id": career_id,
            "title": career_name,
            "category": category,
            "description": f"Professional {career_name} responsible for various duties in the {category} field.",
            "growth_rate": "10-15%",  # Could be scraped from O*NET
            "levels": {
                "Entry": {
                    "years": "0-2",
                    "salary_range": f"${int(base_salary * 0.6):,} - ${int(base_salary * 0.8):,}",
                    "skills": self.get_entry_skills(category),
                    "certifications": self.get_entry_certifications(category),
                    "projects": self.get_entry_projects(career_name, category),
                    "milestones": [
                        f"Complete foundational training in {career_name.lower()}",
                        "Gain hands-on experience through internships or entry positions",
                        "Build portfolio of work samples",
                        "Establish professional network"
                    ],
                    "education": self.get_education_requirements(category, "Entry")
                },
                "Junior": {
                    "years": "2-4",
                    "salary_range": f"${int(base_salary * 0.7):,} - ${int(base_salary * 0.9):,}",
                    "skills": self.get_junior_skills(category),
                    "certifications": self.get_junior_certifications(category),
                    "projects": self.get_junior_projects(career_name, category),
                    "milestones": [
                        "Master core competencies",
                        "Complete 3-5 independent projects",
                        "Obtain industry certification",
                        "Present work to stakeholders"
                    ],
                    "education": self.get_education_requirements(category, "Junior")
                },
                "Mid-Level": {
                    "years": "4-7",
                    "salary_range": f"${int(base_salary * 0.9):,} - ${int(base_salary * 1.2):,}",
                    "skills": self.get_mid_skills(category),
                    "certifications": self.get_mid_certifications(category),
                    "projects": self.get_mid_projects(career_name, category),
                    "milestones": [
                        "Lead project teams",
                        "Mentor junior staff",
                        "Develop specialized expertise",
                        "Contribute to strategic planning"
                    ],
                    "education": self.get_education_requirements(category, "Mid-Level")
                },
                "Senior": {
                    "years": "7-10",
                    "salary_range": f"${int(base_salary * 1.2):,} - ${int(base_salary * 1.6):,}",
                    "skills": self.get_senior_skills(category),
                    "certifications": self.get_senior_certifications(category),
                    "projects": self.get_senior_projects(career_name, category),
                    "milestones": [
                        "Lead department initiatives",
                        "Develop team members",
                        "Drive innovation",
                        "Represent organization externally"
                    ],
                    "education": self.get_education_requirements(category, "Senior")
                },
                "Expert": {
                    "years": "10+",
                    "salary_range": f"${int(base_salary * 1.5):,}+",
                    "skills": self.get_expert_skills(category),
                    "certifications": self.get_expert_certifications(category),
                    "projects": self.get_expert_projects(career_name, category),
                    "milestones": [
                        "Shape organizational strategy",
                        "Industry thought leadership",
                        "Executive advisory role",
                        "Build lasting legacy"
                    ],
                    "education": self.get_education_requirements(category, "Expert")
                }
            },
            "related_careers": self.get_related_careers(career_name, category),
            "industry_trends": self.get_industry_trends(category),
            "remote_friendly": category in ["technology", "creative", "business"],
            "automation_risk": "Low" if category in ["healthcare", "creative", "education"] else "Medium"
        }
        
        return career_data
    
    def get_entry_skills(self, category: str) -> List[str]:
        skills_map = {
            "technology": ["Programming Basics", "Version Control", "Problem Solving", "Documentation", "Testing"],
            "healthcare": ["Patient Care", "Medical Terminology", "Documentation", "Safety Protocols", "Communication"],
            "business": ["Microsoft Office", "Data Analysis", "Communication", "Time Management", "Research"],
            "engineering": ["CAD Software", "Mathematics", "Technical Drawing", "Problem Solving", "Safety"],
            "education": ["Lesson Planning", "Classroom Management", "Communication", "Assessment", "Technology"],
            "creative": ["Design Software", "Color Theory", "Typography", "Creativity", "Time Management"],
            "trades": ["Tool Usage", "Safety Protocols", "Blueprint Reading", "Physical Stamina", "Problem Solving"],
            "science": ["Laboratory Skills", "Data Collection", "Scientific Method", "Documentation", "Safety"]
        }
        return skills_map.get(category, ["Communication", "Problem Solving", "Time Management"])
    
    def get_junior_skills(self, category: str) -> List[str]:
        skills_map = {
            "technology": ["Advanced Programming", "Database Management", "API Development", "Cloud Basics", "Agile"],
            "healthcare": ["Advanced Procedures", "Patient Assessment", "Medical Software", "Team Collaboration", "Specialization Basics"],
            "business": ["Financial Analysis", "Project Management", "Strategic Planning", "Presentation Skills", "CRM Systems"],
            "engineering": ["Advanced CAD", "Project Management", "Quality Control", "Technical Writing", "Simulation Software"],
            "education": ["Curriculum Development", "Educational Technology", "Student Assessment", "Parent Communication", "Special Needs"],
            "creative": ["Advanced Design Tools", "Brand Development", "Client Management", "Portfolio Development", "Trend Analysis"],
            "trades": ["Advanced Techniques", "Project Estimation", "Client Relations", "Code Compliance", "Troubleshooting"],
            "science": ["Research Design", "Statistical Analysis", "Grant Writing", "Publication Writing", "Advanced Equipment"]
        }
        return skills_map.get(category, ["Advanced Skills", "Team Collaboration", "Project Management"])
    
    def get_mid_skills(self, category: str) -> List[str]:
        skills_map = {
            "technology": ["System Architecture", "DevOps", "Security", "Performance Optimization", "Team Leadership"],
            "healthcare": ["Clinical Leadership", "Department Management", "Policy Development", "Quality Improvement", "Mentoring"],
            "business": ["Strategic Management", "Budget Management", "Stakeholder Management", "Change Management", "Analytics"],
            "engineering": ["System Design", "Project Leadership", "Cost Analysis", "Regulatory Compliance", "Innovation"],
            "education": ["Department Leadership", "Program Development", "Grant Writing", "Community Engagement", "Policy"],
            "creative": ["Creative Direction", "Team Management", "Strategic Design", "Business Development", "Innovation"],
            "trades": ["Business Management", "Crew Leadership", "Contract Negotiation", "Quality Assurance", "Training"],
            "science": ["Research Leadership", "Lab Management", "Grant Management", "Collaboration", "Innovation"]
        }
        return skills_map.get(category, ["Leadership", "Strategic Planning", "Team Management"])
    
    def get_senior_skills(self, category: str) -> List[str]:
        skills_map = {
            "technology": ["Technical Strategy", "Enterprise Architecture", "Executive Communication", "Innovation Leadership", "Vendor Management"],
            "healthcare": ["Healthcare Administration", "Strategic Planning", "Regulatory Compliance", "Executive Leadership", "Innovation"],
            "business": ["Executive Leadership", "Corporate Strategy", "Board Reporting", "M&A", "Transformation"],
            "engineering": ["Technical Direction", "Portfolio Management", "Executive Advisory", "Industry Leadership", "Innovation Strategy"],
            "education": ["Educational Leadership", "Policy Development", "Budget Management", "Community Leadership", "Innovation"],
            "creative": ["Creative Strategy", "Agency Management", "Client Leadership", "Industry Innovation", "Thought Leadership"],
            "trades": ["Business Leadership", "Multi-site Management", "Industry Relations", "Strategic Growth", "Succession Planning"],
            "science": ["Research Direction", "Institutional Leadership", "Policy Influence", "International Collaboration", "Innovation"]
        }
        return skills_map.get(category, ["Executive Leadership", "Strategic Vision", "Industry Influence"])
    
    def get_expert_skills(self, category: str) -> List[str]:
        return ["Industry Thought Leadership", "Executive Advisory", "Board Governance", "Strategic Vision", "Legacy Building"]
    
    def get_entry_certifications(self, category: str) -> List[str]:
        cert_map = {
            "technology": ["CompTIA A+", "AWS Cloud Practitioner"],
            "healthcare": ["CPR Certification", "HIPAA Training"],
            "business": ["Microsoft Office Specialist", "Google Analytics"],
            "engineering": ["FE Exam", "AutoCAD Certification"],
            "education": ["Teaching License", "First Aid"],
            "creative": ["Adobe Certified", "Google UX Design"],
            "trades": ["Apprentice License", "OSHA 10"],
            "science": ["Lab Safety Certification", "Good Laboratory Practice"]
        }
        return cert_map.get(category, [])
    
    def get_junior_certifications(self, category: str) -> List[str]:
        cert_map = {
            "technology": ["AWS Developer", "Certified Scrum Developer"],
            "healthcare": ["Specialty Certification", "Advanced Life Support"],
            "business": ["PMP Associate", "Six Sigma Green Belt"],
            "engineering": ["PE License", "Specialized Software Cert"],
            "education": ["Subject Matter Certification", "Educational Technology"],
            "creative": ["Specialized Design Certification", "UX Certification"],
            "trades": ["Journeyman License", "Specialized Equipment"],
            "science": ["Specialized Technique Certification", "Quality Assurance"]
        }
        return cert_map.get(category, ["Professional Certification"])
    
    def get_mid_certifications(self, category: str) -> List[str]:
        cert_map = {
            "technology": ["AWS Solutions Architect", "Security+", "Kubernetes Admin"],
            "healthcare": ["Management Certification", "Quality Improvement"],
            "business": ["PMP", "Six Sigma Black Belt", "CPA"],
            "engineering": ["Project Management", "Lean Six Sigma"],
            "education": ["Administrative License", "Curriculum Specialist"],
            "creative": ["Creative Direction", "Brand Management"],
            "trades": ["Master License", "Inspector Certification"],
            "science": ["Project Management", "Clinical Research"]
        }
        return cert_map.get(category, ["Advanced Certification"])
    
    def get_senior_certifications(self, category: str) -> List[str]:
        cert_map = {
            "technology": ["TOGAF", "CISSP", "Executive Programs"],
            "healthcare": ["Healthcare Executive", "Board Certification"],
            "business": ["Executive MBA", "Board Governance"],
            "engineering": ["Executive Leadership", "Industry Fellow"],
            "education": ["Superintendent License", "Doctoral Degree"],
            "creative": ["Executive Programs", "Industry Awards"],
            "trades": ["Contractor License", "Business Management"],
            "science": ["Executive Leadership", "Research Excellence"]
        }
        return cert_map.get(category, ["Executive Certification"])
    
    def get_expert_certifications(self, category: str) -> List[str]:
        return ["Industry Fellow", "Honorary Degrees", "Lifetime Achievement"]
    
    def get_entry_projects(self, career: str, category: str) -> List[str]:
        return [
            f"Complete {career.lower()} fundamentals course",
            "Build portfolio with 3-5 sample projects",
            "Contribute to team projects",
            "Document learning journey"
        ]
    
    def get_junior_projects(self, career: str, category: str) -> List[str]:
        return [
            f"Lead small {career.lower()} project",
            "Improve existing processes",
            "Mentor new team members",
            "Present at team meetings"
        ]
    
    def get_mid_projects(self, career: str, category: str) -> List[str]:
        return [
            "Lead cross-functional initiative",
            "Develop new methodologies",
            "Build and manage team",
            "Drive measurable improvements"
        ]
    
    def get_senior_projects(self, career: str, category: str) -> List[str]:
        return [
            "Transform department operations",
            "Develop strategic initiatives",
            "Build industry partnerships",
            "Create innovation programs"
        ]
    
    def get_expert_projects(self, career: str, category: str) -> List[str]:
        return [
            "Shape industry standards",
            "Advisory board participation",
            "Thought leadership initiatives",
            "Legacy programs"
        ]
    
    def get_education_requirements(self, category: str, level: str) -> str:
        edu_map = {
            "technology": {
                "Entry": "Bachelor's in Computer Science or related",
                "Junior": "Bachelor's + certifications",
                "Mid-Level": "Bachelor's + advanced certifications",
                "Senior": "Bachelor's/Master's + extensive experience",
                "Expert": "Advanced degree preferred + industry recognition"
            },
            "healthcare": {
                "Entry": "Associate/Bachelor's in Healthcare",
                "Junior": "Bachelor's + clinical training",
                "Mid-Level": "Bachelor's/Master's + specialization",
                "Senior": "Master's/Doctorate + leadership training",
                "Expert": "Doctorate + executive education"
            },
            "business": {
                "Entry": "Bachelor's in Business or related",
                "Junior": "Bachelor's + relevant experience",
                "Mid-Level": "Bachelor's/MBA + certifications",
                "Senior": "MBA + executive training",
                "Expert": "MBA/Doctorate + board experience"
            }
        }
        
        default = {
            "Entry": "Bachelor's degree or equivalent",
            "Junior": "Bachelor's + 2 years experience",
            "Mid-Level": "Bachelor's + 5 years experience",
            "Senior": "Advanced degree + 7 years experience",
            "Expert": "Advanced degree + 10+ years experience"
        }
        
        return edu_map.get(category, default).get(level, "Bachelor's degree preferred")
    
    def get_related_careers(self, career: str, category: str) -> List[str]:
        # Generate related careers based on category
        related_map = {
            "technology": ["Software Engineer", "Data Analyst", "System Administrator", "DevOps Engineer"],
            "healthcare": ["Nurse Practitioner", "Medical Assistant", "Healthcare Administrator", "Clinical Specialist"],
            "business": ["Business Analyst", "Project Manager", "Operations Manager", "Financial Analyst"],
            "engineering": ["Project Engineer", "Design Engineer", "Quality Engineer", "Systems Engineer"],
            "education": ["Curriculum Developer", "Training Specialist", "Education Consultant", "Academic Advisor"],
            "creative": ["Art Director", "Brand Manager", "Content Creator", "User Experience Designer"],
            "trades": ["Project Manager", "Site Supervisor", "Quality Inspector", "Safety Manager"],
            "science": ["Research Analyst", "Lab Manager", "Data Scientist", "Technical Writer"]
        }
        
        return related_map.get(category, ["Specialist", "Consultant", "Manager", "Analyst"])
    
    def get_industry_trends(self, category: str) -> List[str]:
        trends_map = {
            "technology": ["AI/ML Integration", "Cloud Migration", "Cybersecurity Focus", "Remote Work", "Automation"],
            "healthcare": ["Telemedicine", "AI Diagnostics", "Personalized Medicine", "Mental Health Focus", "Preventive Care"],
            "business": ["Digital Transformation", "Data-Driven Decisions", "Sustainability", "Remote Teams", "Agile Methods"],
            "engineering": ["Sustainable Design", "Smart Systems", "3D Printing", "IoT Integration", "Green Technology"],
            "education": ["Online Learning", "Personalized Education", "STEM Focus", "Technology Integration", "Lifelong Learning"],
            "creative": ["Digital First", "AI Tools", "Sustainable Design", "Interactive Media", "Personal Branding"],
            "trades": ["Green Building", "Smart Home Tech", "Prefabrication", "Safety Technology", "Sustainable Materials"],
            "science": ["Interdisciplinary Research", "Big Data", "Open Science", "Sustainability", "Global Collaboration"]
        }
        
        return trends_map.get(category, ["Digital Transformation", "Sustainability", "Remote Work", "Continuous Learning"])
    
    def save_career_file(self, career_data: Dict):
        """Save individual career data to JSON file"""
        filename = self.output_path / f"{career_data['id']}.json"
        with open(filename, 'w') as f:
            json.dump(career_data, f, indent=2)
        print(f"Saved career: {career_data['title']}")
    
    def generate_all_careers(self):
        """Generate comprehensive career database"""
        print("Starting career generation...")
        careers = self.get_popular_careers(limit=100)
        
        # Save summary file
        summary_file = self.output_path / "career_summary.json"
        summary = {
            "total_careers": len(careers),
            "categories": list(set(c["category"] for c in careers)),
            "careers": [{"id": c["id"], "title": c["title"], "category": c["category"]} for c in careers]
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Generated {len(careers)} career files")
        return careers