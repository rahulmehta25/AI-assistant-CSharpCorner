import re
from typing import Dict, List, Optional
from datetime import datetime
import json
from pathlib import Path

class ApplicationAssistant:
    def __init__(self, templates_path: str = "data/templates/"):
        self.templates_path = Path(templates_path)
        self.templates_path.mkdir(parents=True, exist_ok=True)
        self.resume_keywords_db = self.load_resume_keywords()
        self.cover_letter_templates = self.load_cover_letter_templates()
    
    def load_resume_keywords(self) -> Dict:
        # ATS-friendly keywords by category
        return {
            'action_verbs': [
                'Developed', 'Implemented', 'Designed', 'Led', 'Managed',
                'Created', 'Optimized', 'Improved', 'Achieved', 'Delivered',
                'Built', 'Established', 'Launched', 'Increased', 'Reduced',
                'Streamlined', 'Collaborated', 'Analyzed', 'Solved', 'Mentored'
            ],
            'technical_skills': {
                'software_engineering': [
                    'Software Development', 'System Design', 'API Development',
                    'Database Management', 'Version Control', 'Code Review',
                    'Testing', 'Debugging', 'Performance Optimization', 'Security'
                ],
                'data_science': [
                    'Data Analysis', 'Machine Learning', 'Statistical Modeling',
                    'Data Visualization', 'Big Data', 'ETL', 'A/B Testing',
                    'Predictive Analytics', 'Deep Learning', 'Feature Engineering'
                ],
                'product_management': [
                    'Product Strategy', 'Roadmapping', 'User Research',
                    'Market Analysis', 'Stakeholder Management', 'Agile/Scrum',
                    'Product Launch', 'Metrics Analysis', 'Go-to-Market', 'MVP'
                ],
                'devops': [
                    'CI/CD', 'Infrastructure as Code', 'Containerization',
                    'Cloud Architecture', 'Monitoring', 'Automation', 'Deployment',
                    'Scalability', 'Reliability', 'Security'
                ]
            },
            'soft_skills': [
                'Communication', 'Leadership', 'Problem-solving', 'Teamwork',
                'Time Management', 'Adaptability', 'Critical Thinking',
                'Project Management', 'Presentation', 'Mentoring'
            ],
            'certifications': [
                'AWS Certified', 'Google Cloud Certified', 'Azure Certified',
                'PMP', 'Scrum Master', 'Six Sigma', 'CISSP', 'CPA'
            ]
        }
    
    def load_cover_letter_templates(self) -> Dict:
        return {
            'standard': {
                'opening': "I am writing to express my strong interest in the {position} role at {company}. With {experience_years} years of experience in {field}, I am confident that my skills and passion make me an ideal candidate for this position.",
                'body_paragraph_1': "In my current role as {current_position} at {current_company}, I have {achievement_1}. This experience has allowed me to develop strong skills in {skill_1} and {skill_2}, which directly align with your requirements.",
                'body_paragraph_2': "I am particularly drawn to {company} because {company_reason}. Your emphasis on {company_value} resonates with my professional values, and I am excited about the opportunity to contribute to {company_goal}.",
                'closing': "I am eager to bring my expertise in {key_skill} to your team and contribute to {company}'s continued success. Thank you for considering my application. I look forward to discussing how my background and skills would be an asset to your organization."
            },
            'career_change': {
                'opening': "I am excited to apply for the {position} role at {company}. While my background is in {previous_field}, I have been actively developing skills in {new_field} and am eager to transition my career in this direction.",
                'body_paragraph_1': "My experience in {previous_field} has provided me with transferable skills that are highly relevant to {new_field}. Specifically, I have developed {transferable_skill_1} and {transferable_skill_2}, which will enable me to excel in this new role.",
                'body_paragraph_2': "To prepare for this career transition, I have {preparation_action}. Additionally, I have completed {relevant_course_or_project}, which has given me hands-on experience with {relevant_skill}.",
                'closing': "I am passionate about making this career transition and believe that my unique background, combined with my newly acquired skills in {new_field}, would bring a fresh perspective to your team. I would welcome the opportunity to discuss how I can contribute to {company}'s success."
            },
            'entry_level': {
                'opening': "As a recent graduate with a degree in {degree} from {university}, I am thrilled to apply for the {position} role at {company}. Your company's reputation for {company_strength} makes this an ideal opportunity to begin my career.",
                'body_paragraph_1': "During my academic journey, I {academic_achievement}. I also completed {relevant_project_or_internship}, where I gained practical experience in {relevant_skill}.",
                'body_paragraph_2': "Beyond my academic achievements, I have demonstrated {soft_skill_1} and {soft_skill_2} through {extracurricular_activity}. These experiences have prepared me to contribute meaningfully to your team from day one.",
                'closing': "I am eager to bring my fresh perspective, strong work ethic, and enthusiasm to {company}. I am confident that my academic foundation and practical experience make me a strong candidate for this position. Thank you for your consideration."
            }
        }
    
    def analyze_job_description(self, job_description: str) -> Dict:
        # Extract key information from job description
        job_description_lower = job_description.lower()
        
        # Extract required skills
        required_skills = []
        skill_patterns = [
            r'required skills?:?(.*?)(?:preferred|desired|responsibilities|qualifications|$)',
            r'must have:?(.*?)(?:nice to have|preferred|$)',
            r'requirements?:?(.*?)(?:responsibilities|preferred|$)'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, job_description_lower, re.DOTALL)
            for match in matches:
                skills = re.findall(r'[•\-\*]\s*([^\n]+)', match)
                required_skills.extend(skills)
        
        # Extract preferred skills
        preferred_skills = []
        preferred_patterns = [
            r'preferred skills?:?(.*?)(?:responsibilities|about|$)',
            r'nice to have:?(.*?)(?:responsibilities|about|$)',
            r'desired:?(.*?)(?:responsibilities|about|$)'
        ]
        
        for pattern in preferred_patterns:
            matches = re.findall(pattern, job_description_lower, re.DOTALL)
            for match in matches:
                skills = re.findall(r'[•\-\*]\s*([^\n]+)', match)
                preferred_skills.extend(skills)
        
        # Extract keywords
        keywords = self.extract_keywords(job_description)
        
        # Identify key technologies
        technologies = self.extract_technologies(job_description)
        
        # Determine experience level
        experience_level = self.determine_experience_level(job_description)
        
        return {
            'required_skills': required_skills,
            'preferred_skills': preferred_skills,
            'keywords': keywords,
            'technologies': technologies,
            'experience_level': experience_level,
            'action_verbs': self.suggest_action_verbs(job_description)
        }
    
    def extract_keywords(self, text: str) -> List[str]:
        # Common important keywords in job descriptions
        keyword_patterns = [
            r'\b(python|java|javascript|c\+\+|golang|ruby|php|swift|kotlin)\b',
            r'\b(react|angular|vue|django|flask|spring|express|rails)\b',
            r'\b(aws|azure|gcp|docker|kubernetes|terraform)\b',
            r'\b(sql|nosql|postgresql|mysql|mongodb|redis)\b',
            r'\b(machine learning|deep learning|ai|data science|analytics)\b',
            r'\b(agile|scrum|kanban|devops|ci\/cd)\b',
            r'\b(leadership|management|communication|teamwork|problem-solving)\b'
        ]
        
        keywords = set()
        text_lower = text.lower()
        
        for pattern in keyword_patterns:
            matches = re.findall(pattern, text_lower)
            keywords.update(matches)
        
        return list(keywords)
    
    def extract_technologies(self, text: str) -> List[str]:
        # Extract specific technologies mentioned
        tech_pattern = r'\b([A-Z][a-zA-Z]+(?:\.[a-zA-Z]+)?)\b'
        technologies = re.findall(tech_pattern, text)
        
        # Filter common technologies
        common_tech = [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'React', 'Angular',
            'Vue', 'Node', 'Django', 'Flask', 'Spring', 'Docker', 'Kubernetes',
            'AWS', 'Azure', 'GCP', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis',
            'Git', 'Jenkins', 'Terraform', 'Ansible', 'GraphQL', 'REST'
        ]
        
        found_tech = []
        for tech in technologies:
            if tech in common_tech and tech not in found_tech:
                found_tech.append(tech)
        
        return found_tech
    
    def determine_experience_level(self, text: str) -> str:
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['senior', 'sr.', 'lead', 'principal', '5+ years', '7+ years', '10+ years']):
            return 'Senior'
        elif any(word in text_lower for word in ['junior', 'jr.', 'entry', 'graduate', '0-2 years', '1-2 years']):
            return 'Junior'
        elif any(word in text_lower for word in ['mid-level', 'intermediate', '3-5 years', '2-4 years']):
            return 'Mid-Level'
        else:
            return 'Mid-Level'  # Default
    
    def suggest_action_verbs(self, job_description: str) -> List[str]:
        # Suggest relevant action verbs based on job type
        if 'manage' in job_description.lower() or 'lead' in job_description.lower():
            return ['Led', 'Managed', 'Directed', 'Supervised', 'Coordinated']
        elif 'develop' in job_description.lower() or 'engineer' in job_description.lower():
            return ['Developed', 'Built', 'Implemented', 'Designed', 'Created']
        elif 'analyze' in job_description.lower() or 'data' in job_description.lower():
            return ['Analyzed', 'Evaluated', 'Assessed', 'Investigated', 'Examined']
        else:
            return self.resume_keywords_db['action_verbs'][:5]
    
    def optimize_resume(self, resume_text: str, job_analysis: Dict) -> Dict:
        suggestions = []
        
        # Check for keywords
        missing_keywords = []
        for keyword in job_analysis['keywords']:
            if keyword.lower() not in resume_text.lower():
                missing_keywords.append(keyword)
        
        if missing_keywords:
            suggestions.append({
                'type': 'keywords',
                'priority': 'high',
                'message': f"Add these keywords to match the job description: {', '.join(missing_keywords[:5])}"
            })
        
        # Check for action verbs
        has_action_verbs = any(verb.lower() in resume_text.lower() 
                              for verb in self.resume_keywords_db['action_verbs'])
        
        if not has_action_verbs:
            suggestions.append({
                'type': 'action_verbs',
                'priority': 'medium',
                'message': f"Start bullet points with action verbs like: {', '.join(job_analysis['action_verbs'])}"
            })
        
        # Check for quantifiable achievements
        has_numbers = bool(re.search(r'\d+%|\$\d+|\d+\s*(user|customer|project|team)', resume_text))
        
        if not has_numbers:
            suggestions.append({
                'type': 'quantification',
                'priority': 'high',
                'message': "Add quantifiable achievements (e.g., 'Increased sales by 25%', 'Managed team of 10')"
            })
        
        # Check for technologies
        missing_tech = []
        for tech in job_analysis['technologies']:
            if tech.lower() not in resume_text.lower():
                missing_tech.append(tech)
        
        if missing_tech:
            suggestions.append({
                'type': 'technologies',
                'priority': 'high',
                'message': f"Include these technologies if you have experience: {', '.join(missing_tech)}"
            })
        
        # Calculate ATS score
        keyword_matches = len([k for k in job_analysis['keywords'] if k.lower() in resume_text.lower()])
        total_keywords = len(job_analysis['keywords']) if job_analysis['keywords'] else 1
        ats_score = min((keyword_matches / total_keywords) * 100, 100)
        
        return {
            'ats_score': round(ats_score, 1),
            'suggestions': suggestions,
            'missing_keywords': missing_keywords,
            'missing_technologies': missing_tech,
            'recommended_sections': self.recommend_resume_sections(job_analysis['experience_level'])
        }
    
    def recommend_resume_sections(self, experience_level: str) -> List[str]:
        base_sections = ['Contact Information', 'Summary/Objective', 'Experience', 'Education', 'Skills']
        
        if experience_level == 'Senior':
            return base_sections + ['Leadership Experience', 'Key Achievements', 'Publications/Patents']
        elif experience_level == 'Junior':
            return base_sections + ['Projects', 'Coursework', 'Extracurricular Activities']
        else:
            return base_sections + ['Projects', 'Certifications']
    
    def generate_cover_letter(self, user_info: Dict, job_info: Dict, template_type: str = 'standard') -> str:
        template = self.cover_letter_templates.get(template_type, self.cover_letter_templates['standard'])
        
        # Prepare variables for template
        variables = {
            'position': job_info.get('position', 'the position'),
            'company': job_info.get('company', 'your company'),
            'experience_years': user_info.get('experience_years', 'several'),
            'field': user_info.get('field', 'this field'),
            'current_position': user_info.get('current_position', 'my current role'),
            'current_company': user_info.get('current_company', 'my current company'),
            'achievement_1': user_info.get('achievement', 'achieved significant results'),
            'skill_1': user_info.get('skills', [''])[0] if user_info.get('skills') else 'relevant skills',
            'skill_2': user_info.get('skills', ['', ''])[1] if len(user_info.get('skills', [])) > 1 else 'technical expertise',
            'company_reason': job_info.get('company_reason', 'of your innovative approach and market leadership'),
            'company_value': job_info.get('company_value', 'innovation and excellence'),
            'company_goal': job_info.get('company_goal', 'your mission'),
            'key_skill': user_info.get('key_skill', 'my expertise')
        }
        
        # Generate cover letter
        cover_letter = []
        
        # Date and greeting
        cover_letter.append(datetime.now().strftime("%B %d, %Y"))
        cover_letter.append("")
        cover_letter.append(f"Dear Hiring Manager,")
        cover_letter.append("")
        
        # Body paragraphs
        cover_letter.append(template['opening'].format(**variables))
        cover_letter.append("")
        cover_letter.append(template['body_paragraph_1'].format(**variables))
        cover_letter.append("")
        cover_letter.append(template['body_paragraph_2'].format(**variables))
        cover_letter.append("")
        cover_letter.append(template['closing'].format(**variables))
        cover_letter.append("")
        
        # Signature
        cover_letter.append("Sincerely,")
        cover_letter.append(user_info.get('name', '[Your Name]'))
        
        return '\n'.join(cover_letter)
    
    def generate_interview_questions(self, job_title: str, job_description: str, experience_level: str) -> Dict:
        questions = {
            'behavioral': [],
            'technical': [],
            'situational': [],
            'questions_to_ask': []
        }
        
        # Behavioral questions
        questions['behavioral'] = [
            "Tell me about yourself and your background.",
            "Why are you interested in this position?",
            "What are your greatest strengths and weaknesses?",
            "Describe a challenging project you worked on and how you overcame obstacles.",
            "Tell me about a time you had to work with a difficult team member.",
            "How do you handle tight deadlines and pressure?",
            "Describe a situation where you had to learn something new quickly."
        ]
        
        # Technical questions based on job title
        if 'engineer' in job_title.lower() or 'developer' in job_title.lower():
            questions['technical'] = [
                "Explain your approach to system design.",
                "How do you ensure code quality?",
                "Describe your experience with version control and CI/CD.",
                "Walk me through your debugging process.",
                "How do you optimize application performance?",
                "Explain a complex technical concept to a non-technical person."
            ]
        elif 'data' in job_title.lower() or 'analyst' in job_title.lower():
            questions['technical'] = [
                "How do you approach data cleaning and preparation?",
                "Explain your process for exploratory data analysis.",
                "Describe a machine learning model you've implemented.",
                "How do you validate your models?",
                "What metrics do you use to measure success?",
                "How do you communicate findings to stakeholders?"
            ]
        elif 'product' in job_title.lower() or 'manager' in job_title.lower():
            questions['technical'] = [
                "How do you prioritize features?",
                "Describe your approach to user research.",
                "How do you measure product success?",
                "Walk me through your product development process.",
                "How do you handle conflicting stakeholder requirements?",
                "Describe a product launch you've managed."
            ]
        
        # Situational questions
        questions['situational'] = [
            "How would you handle a situation where you disagree with your manager?",
            "What would you do if you noticed a colleague making a mistake?",
            "How would you approach a project with unclear requirements?",
            "What would you do if you couldn't meet a deadline?",
            "How would you handle receiving critical feedback?"
        ]
        
        # Questions to ask the interviewer
        questions['questions_to_ask'] = [
            "What does a typical day look like in this role?",
            "What are the biggest challenges facing the team right now?",
            "How do you measure success in this position?",
            "What opportunities are there for professional development?",
            "Can you describe the team culture?",
            "What are the next steps in the interview process?",
            "What do you enjoy most about working here?"
        ]
        
        return questions
    
    def create_application_tracker_entry(self, job_info: Dict, user_actions: Dict) -> Dict:
        return {
            'job_id': job_info.get('id'),
            'company': job_info.get('company'),
            'position': job_info.get('title'),
            'application_date': datetime.now().isoformat(),
            'status': 'applied',
            'job_url': job_info.get('url'),
            'match_score': job_info.get('match_score'),
            'resume_version': user_actions.get('resume_version', 'default'),
            'cover_letter_sent': user_actions.get('cover_letter_sent', False),
            'notes': user_actions.get('notes', ''),
            'follow_up_date': (datetime.now().replace(day=datetime.now().day + 7)).isoformat(),
            'interview_dates': [],
            'contact_person': user_actions.get('contact_person', ''),
            'salary_expectation': user_actions.get('salary_expectation', '')
        }