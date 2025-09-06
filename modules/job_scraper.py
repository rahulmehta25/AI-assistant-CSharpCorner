import requests
from bs4 import BeautifulSoup
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import time
import hashlib
from pathlib import Path
import re

class JobScraper:
    def __init__(self, cache_dir: str = "data/cache/"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_duration = 86400  # 24 hours
        
        # Headers to avoid being blocked
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Job board configurations
        self.job_boards = {
            'indeed': {
                'base_url': 'https://www.indeed.com/jobs',
                'params': {
                    'q': '',  # job title
                    'l': '',  # location
                    'start': 0
                }
            },
            'linkedin': {
                'base_url': 'https://www.linkedin.com/jobs/search',
                'params': {
                    'keywords': '',
                    'location': ''
                }
            }
        }
    
    def search_jobs(self, job_title: str, location: str = "Remote", 
                   skills: List[str] = None, experience_level: str = None,
                   max_results: int = 20) -> List[Dict]:
        
        # Check cache first
        cache_key = self.generate_cache_key(job_title, location, skills, experience_level)
        cached_results = self.get_cached_results(cache_key)
        
        if cached_results:
            return cached_results[:max_results]
        
        # Scrape new results
        all_jobs = []
        
        # For now, we'll use mock data to demonstrate functionality
        # In production, you would implement actual scraping
        all_jobs.extend(self.get_mock_jobs(job_title, location, skills, experience_level))
        
        # Cache results
        self.cache_results(cache_key, all_jobs)
        
        return all_jobs[:max_results]
    
    def get_mock_jobs(self, job_title: str, location: str, 
                     skills: List[str] = None, experience_level: str = None) -> List[Dict]:
        
        # Generate realistic mock job data
        mock_jobs = []
        
        job_templates = [
            {
                'company': 'Tech Corp',
                'description_template': 'Looking for a {title} to join our growing team. Experience with {skills} required.',
                'benefits': ['Health insurance', '401k', 'Remote work', 'Flexible hours'],
                'salary_multiplier': 1.2
            },
            {
                'company': 'StartupXYZ',
                'description_template': 'Fast-paced startup seeking {title}. Must be proficient in {skills}.',
                'benefits': ['Stock options', 'Unlimited PTO', 'Learning budget'],
                'salary_multiplier': 1.0
            },
            {
                'company': 'Enterprise Solutions Inc',
                'description_template': 'Enterprise company hiring {title}. Strong background in {skills} essential.',
                'benefits': ['Comprehensive healthcare', 'Pension', 'Training programs'],
                'salary_multiplier': 1.3
            },
            {
                'company': 'Digital Innovations',
                'description_template': 'Join our innovative team as a {title}. Experience with {skills} is a plus.',
                'benefits': ['Remote-first', 'Equipment budget', 'Conference attendance'],
                'salary_multiplier': 1.1
            },
            {
                'company': 'Global Tech Solutions',
                'description_template': 'Seeking experienced {title} with expertise in {skills}.',
                'benefits': ['International opportunities', 'Relocation assistance', 'Visa sponsorship'],
                'salary_multiplier': 1.4
            }
        ]
        
        base_salary = self.estimate_salary(job_title, experience_level)
        
        for i, template in enumerate(job_templates):
            job_id = f"job_{hashlib.md5(f'{template["company"]}_{job_title}_{i}'.encode()).hexdigest()[:8]}"
            
            # Calculate salary range
            salary_min = int(base_salary * template['salary_multiplier'] * 0.9)
            salary_max = int(base_salary * template['salary_multiplier'] * 1.1)
            
            # Generate requirements based on experience level
            requirements = self.generate_requirements(experience_level, skills)
            
            job = {
                'id': job_id,
                'title': job_title,
                'company': template['company'],
                'location': location,
                'salary_range': f"${salary_min:,} - ${salary_max:,}",
                'description': template['description_template'].format(
                    title=job_title,
                    skills=', '.join(skills[:3]) if skills else 'relevant technologies'
                ),
                'requirements': requirements,
                'benefits': template['benefits'],
                'posted_date': (datetime.now() - timedelta(days=i*2)).strftime("%Y-%m-%d"),
                'url': f"https://example.com/jobs/{job_id}",
                'application_deadline': (datetime.now() + timedelta(days=30-i*3)).strftime("%Y-%m-%d"),
                'remote': 'Remote' in location or i % 2 == 0,
                'experience_level': experience_level or self.infer_experience_level(job_title),
                'job_type': 'Full-time',
                'skills_required': skills or [],
                'match_score': 0  # Will be calculated by skills matcher
            }
            
            mock_jobs.append(job)
        
        # Add some variety with different job titles
        related_titles = self.get_related_job_titles(job_title)
        for related_title in related_titles[:3]:
            for i, template in enumerate(job_templates[:2]):
                job_id = f"job_{hashlib.md5(f'{template["company"]}_{related_title}_{i}'.encode()).hexdigest()[:8]}"
                
                salary_min = int(base_salary * template['salary_multiplier'] * 0.85)
                salary_max = int(base_salary * template['salary_multiplier'] * 1.05)
                
                job = {
                    'id': job_id,
                    'title': related_title,
                    'company': f"{template['company']} ({related_title})",
                    'location': location,
                    'salary_range': f"${salary_min:,} - ${salary_max:,}",
                    'description': template['description_template'].format(
                        title=related_title,
                        skills=', '.join(skills[:3]) if skills else 'relevant technologies'
                    ),
                    'requirements': self.generate_requirements(experience_level, skills),
                    'benefits': template['benefits'],
                    'posted_date': (datetime.now() - timedelta(days=i*3+5)).strftime("%Y-%m-%d"),
                    'url': f"https://example.com/jobs/{job_id}",
                    'application_deadline': (datetime.now() + timedelta(days=25-i*2)).strftime("%Y-%m-%d"),
                    'remote': 'Remote' in location or i % 3 == 0,
                    'experience_level': experience_level or 'Mid-Level',
                    'job_type': 'Full-time',
                    'skills_required': skills or [],
                    'match_score': 0
                }
                
                mock_jobs.append(job)
        
        return mock_jobs
    
    def estimate_salary(self, job_title: str, experience_level: str = None) -> int:
        # Base salaries by job category
        salary_map = {
            'software': 95000,
            'data': 105000,
            'product': 110000,
            'design': 85000,
            'marketing': 75000,
            'sales': 80000,
            'engineer': 95000,
            'developer': 90000,
            'analyst': 80000,
            'manager': 100000,
            'director': 130000,
            'architect': 120000,
            'scientist': 110000
        }
        
        # Find matching category
        base_salary = 85000  # default
        job_title_lower = job_title.lower()
        
        for keyword, salary in salary_map.items():
            if keyword in job_title_lower:
                base_salary = salary
                break
        
        # Adjust for experience level
        if experience_level:
            level_multipliers = {
                'Junior': 0.7,
                'Entry': 0.6,
                'Mid-Level': 1.0,
                'Senior': 1.4,
                'Lead': 1.6,
                'Principal': 1.8,
                'Expert': 2.0
            }
            
            multiplier = level_multipliers.get(experience_level, 1.0)
            base_salary = int(base_salary * multiplier)
        
        return base_salary
    
    def generate_requirements(self, experience_level: str, skills: List[str] = None) -> List[str]:
        base_requirements = []
        
        # Experience-based requirements
        if experience_level == 'Junior' or experience_level == 'Entry':
            base_requirements.extend([
                "0-2 years of relevant experience",
                "Bachelor's degree in related field or equivalent experience",
                "Strong communication skills",
                "Eagerness to learn and grow"
            ])
        elif experience_level == 'Mid-Level':
            base_requirements.extend([
                "3-5 years of relevant experience",
                "Bachelor's degree in related field",
                "Proven track record of successful projects",
                "Strong problem-solving skills"
            ])
        elif experience_level == 'Senior':
            base_requirements.extend([
                "5+ years of relevant experience",
                "Bachelor's or Master's degree in related field",
                "Leadership and mentoring experience",
                "Expert-level technical skills"
            ])
        else:
            base_requirements.extend([
                "Relevant experience in the field",
                "Strong technical and soft skills",
                "Ability to work independently"
            ])
        
        # Add skill-specific requirements
        if skills:
            for skill in skills[:5]:
                base_requirements.append(f"Proficiency in {skill}")
        
        return base_requirements
    
    def get_related_job_titles(self, job_title: str) -> List[str]:
        # Map of related job titles
        related_titles_map = {
            'software engineer': ['Software Developer', 'Full Stack Developer', 'Backend Engineer', 'Frontend Engineer'],
            'data scientist': ['Data Analyst', 'Machine Learning Engineer', 'Data Engineer', 'Business Analyst'],
            'product manager': ['Product Owner', 'Program Manager', 'Project Manager', 'Business Analyst'],
            'ux designer': ['UI Designer', 'Product Designer', 'Visual Designer', 'Interaction Designer'],
            'marketing manager': ['Digital Marketing Specialist', 'Content Manager', 'Brand Manager', 'Growth Manager'],
            'sales manager': ['Account Executive', 'Business Development Manager', 'Sales Representative', 'Account Manager'],
            'devops engineer': ['Site Reliability Engineer', 'Cloud Engineer', 'Infrastructure Engineer', 'Platform Engineer']
        }
        
        job_title_lower = job_title.lower()
        
        for key, related in related_titles_map.items():
            if key in job_title_lower or job_title_lower in key:
                return related
        
        # Default related titles
        return [f"Senior {job_title}", f"{job_title} II", f"Lead {job_title}"]
    
    def infer_experience_level(self, job_title: str) -> str:
        title_lower = job_title.lower()
        
        if any(word in title_lower for word in ['junior', 'jr', 'entry', 'associate']):
            return 'Junior'
        elif any(word in title_lower for word in ['senior', 'sr', 'lead', 'principal']):
            return 'Senior'
        elif any(word in title_lower for word in ['director', 'vp', 'head']):
            return 'Executive'
        else:
            return 'Mid-Level'
    
    def generate_cache_key(self, job_title: str, location: str, 
                          skills: List[str] = None, experience_level: str = None) -> str:
        # Create unique cache key
        key_parts = [job_title, location]
        if skills:
            key_parts.extend(sorted(skills))
        if experience_level:
            key_parts.append(experience_level)
        
        key_string = '_'.join(key_parts).lower().replace(' ', '_')
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_cached_results(self, cache_key: str) -> Optional[List[Dict]]:
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            # Check if cache is still valid
            file_age = time.time() - cache_file.stat().st_mtime
            if file_age < self.cache_duration:
                with open(cache_file, 'r') as f:
                    return json.load(f)
        
        return None
    
    def cache_results(self, cache_key: str, results: List[Dict]):
        cache_file = self.cache_dir / f"{cache_key}.json"
        with open(cache_file, 'w') as f:
            json.dump(results, f, indent=2)
    
    def parse_salary(self, salary_text: str) -> Optional[Tuple[int, int]]:
        # Extract salary range from text
        salary_pattern = r'\$?([\d,]+)\s*-\s*\$?([\d,]+)'
        match = re.search(salary_pattern, salary_text)
        
        if match:
            min_salary = int(match.group(1).replace(',', ''))
            max_salary = int(match.group(2).replace(',', ''))
            return (min_salary, max_salary)
        
        return None
    
    def filter_jobs(self, jobs: List[Dict], filters: Dict) -> List[Dict]:
        filtered_jobs = jobs
        
        if filters.get('min_salary'):
            filtered_jobs = [
                job for job in filtered_jobs
                if self.parse_salary(job.get('salary_range', ''))
                and self.parse_salary(job['salary_range'])[0] >= filters['min_salary']
            ]
        
        if filters.get('remote_only'):
            filtered_jobs = [
                job for job in filtered_jobs
                if job.get('remote', False)
            ]
        
        if filters.get('experience_level'):
            filtered_jobs = [
                job for job in filtered_jobs
                if job.get('experience_level') == filters['experience_level']
            ]
        
        if filters.get('companies'):
            filtered_jobs = [
                job for job in filtered_jobs
                if job.get('company') in filters['companies']
            ]
        
        return filtered_jobs