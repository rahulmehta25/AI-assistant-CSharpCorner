"""
Job Matcher Module
Matches job postings to users based on skills, experience, location, and preferences.
"""

import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd


@dataclass
class UserProfile:
    """User profile for job matching"""
    user_id: str
    skills: List[str]
    experience_level: str  # 'entry', 'mid', 'senior', 'executive'
    experience_years: int
    preferred_locations: List[str]
    salary_expectations: Dict[str, Any]  # {'min': 50000, 'max': 100000, 'period': 'year'}
    job_titles: List[str]
    industries: List[str]
    work_preferences: Dict[str, Any]  # {'remote': True, 'hybrid': True, 'onsite': False}
    education_level: str
    certifications: List[str]
    languages: List[str]
    career_goals: List[str]


@dataclass
class JobMatchScore:
    """Job match score breakdown"""
    overall_score: float
    skill_score: float
    experience_score: float
    location_score: float
    salary_score: float
    title_score: float
    industry_score: float
    work_preference_score: float
    match_reasons: List[str]
    concerns: List[str]


class JobMatcher:
    """Advanced job matching engine"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "data/job_sources.json"
        self.config = self._load_config()
        self.skill_synonyms = self._load_skill_synonyms()
        self.location_aliases = self._load_location_aliases()
        
        # Matching weights from config
        weights = self.config.get('onet_integration', {})
        self.weights = {
            'skills': weights.get('skills_matching_weight', 0.4),
            'experience': weights.get('experience_matching_weight', 0.3),
            'location': weights.get('location_matching_weight', 0.2),
            'salary': weights.get('salary_matching_weight', 0.1)
        }
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize TF-IDF vectorizer for text similarity
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
    
    def _load_config(self) -> Dict:
        """Load configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _load_skill_synonyms(self) -> Dict[str, List[str]]:
        """Load skill synonyms for better matching"""
        synonyms = {
            'python': ['python programming', 'python development', 'python scripting'],
            'javascript': ['js', 'javascript programming', 'node.js', 'nodejs'],
            'java': ['java programming', 'java development'],
            'react': ['reactjs', 'react.js', 'react development'],
            'angular': ['angularjs', 'angular.js'],
            'vue': ['vuejs', 'vue.js'],
            'sql': ['mysql', 'postgresql', 'sql server', 'database'],
            'machine learning': ['ml', 'artificial intelligence', 'ai', 'data science'],
            'aws': ['amazon web services', 'cloud computing'],
            'docker': ['containerization', 'containers'],
            'kubernetes': ['k8s', 'container orchestration'],
            'git': ['version control', 'github', 'gitlab'],
            'agile': ['scrum', 'agile methodology', 'agile development'],
            'rest api': ['restful api', 'api development', 'web api'],
            'microservices': ['micro-services', 'service-oriented architecture'],
            'devops': ['ci/cd', 'continuous integration', 'continuous deployment'],
            'full stack': ['full-stack', 'fullstack developer'],
            'frontend': ['front-end', 'ui development', 'web development'],
            'backend': ['back-end', 'server-side development'],
            'mobile development': ['ios', 'android', 'react native', 'flutter'],
            'project management': ['pmp', 'scrum master', 'program management'],
            'data analysis': ['data analytics', 'business intelligence', 'bi'],
            'cybersecurity': ['information security', 'infosec', 'security'],
            'cloud': ['cloud computing', 'aws', 'azure', 'gcp'],
            'blockchain': ['cryptocurrency', 'smart contracts', 'web3'],
            'ux/ui': ['user experience', 'user interface', 'design'],
            'quality assurance': ['qa', 'testing', 'test automation']
        }
        return synonyms
    
    def _load_location_aliases(self) -> Dict[str, List[str]]:
        """Load location aliases for better matching"""
        aliases = {
            'san francisco': ['sf', 'san francisco bay area', 'bay area', 'silicon valley'],
            'new york': ['nyc', 'new york city', 'manhattan', 'brooklyn'],
            'los angeles': ['la', 'los angeles county', 'hollywood'],
            'chicago': ['chicagoland', 'chicago metropolitan area'],
            'boston': ['greater boston', 'boston metro'],
            'seattle': ['seattle metro', 'greater seattle', 'puget sound'],
            'austin': ['austin metro', 'central texas'],
            'denver': ['denver metro', 'front range'],
            'atlanta': ['atlanta metro', 'greater atlanta'],
            'washington dc': ['dc', 'washington', 'dmv', 'northern virginia'],
            'remote': ['work from home', 'telecommute', 'distributed', 'anywhere']
        }
        return aliases
    
    def _normalize_skills(self, skills: List[str]) -> List[str]:
        """Normalize and expand skills using synonyms"""
        normalized_skills = set()
        
        for skill in skills:
            skill_lower = skill.lower().strip()
            normalized_skills.add(skill_lower)
            
            # Add synonyms
            for main_skill, synonyms in self.skill_synonyms.items():
                if skill_lower == main_skill or skill_lower in synonyms:
                    normalized_skills.add(main_skill)
                    normalized_skills.update(synonyms)
        
        return list(normalized_skills)
    
    def _normalize_location(self, location: str) -> List[str]:
        """Normalize location using aliases"""
        location_lower = location.lower().strip()
        normalized_locations = [location_lower]
        
        # Add aliases
        for main_location, aliases in self.location_aliases.items():
            if location_lower == main_location or location_lower in aliases:
                normalized_locations.append(main_location)
                normalized_locations.extend(aliases)
        
        return list(set(normalized_locations))
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from job description text"""
        if not text:
            return []
        
        text_lower = text.lower()
        found_skills = []
        
        # Check for known skills and their synonyms
        for main_skill, synonyms in self.skill_synonyms.items():
            all_variations = [main_skill] + synonyms
            for variation in all_variations:
                if variation in text_lower:
                    found_skills.append(main_skill)
                    break
        
        return list(set(found_skills))
    
    def _calculate_skill_similarity(self, user_skills: List[str], job_skills: List[str], job_text: str = "") -> Tuple[float, List[str]]:
        """Calculate skill similarity between user and job"""
        if not user_skills:
            return 0.0, []
        
        # Normalize skills
        user_skills_norm = self._normalize_skills(user_skills)
        job_skills_norm = self._normalize_skills(job_skills)
        
        # Extract additional skills from job text
        extracted_skills = self._extract_skills_from_text(job_text)
        job_skills_norm.extend(extracted_skills)
        job_skills_norm = list(set(job_skills_norm))
        
        if not job_skills_norm:
            return 0.0, []
        
        # Calculate overlap
        matching_skills = []
        for user_skill in user_skills_norm:
            for job_skill in job_skills_norm:
                similarity = SequenceMatcher(None, user_skill, job_skill).ratio()
                if similarity > 0.8:  # High similarity threshold
                    matching_skills.append(user_skill)
                    break
        
        # Calculate skill match score
        skill_score = len(matching_skills) / len(user_skills_norm)
        
        # Bonus for exact matches
        exact_matches = set(user_skills_norm) & set(job_skills_norm)
        if exact_matches:
            skill_score += 0.1 * len(exact_matches) / len(user_skills_norm)
        
        return min(skill_score, 1.0), matching_skills
    
    def _calculate_experience_similarity(self, user_experience: int, user_level: str, job_text: str) -> Tuple[float, List[str]]:
        """Calculate experience level similarity"""
        experience_patterns = {
            'entry': [r'entry.level', r'junior', r'0.2 years', r'new grad', r'recent graduate'],
            'mid': [r'mid.level', r'2.5 years', r'3.7 years', r'experienced', r'intermediate'],
            'senior': [r'senior', r'5.10 years', r'8.12 years', r'lead', r'principal'],
            'executive': [r'director', r'manager', r'executive', r'vp', r'chief', r'head of']
        }
        
        job_text_lower = job_text.lower() if job_text else ""
        job_experience_level = 'mid'  # default
        reasons = []
        
        # Detect job experience level from text
        for level, patterns in experience_patterns.items():
            for pattern in patterns:
                if re.search(pattern, job_text_lower):
                    job_experience_level = level
                    break
        
        # Experience level mapping to years
        level_to_years = {
            'entry': 1,
            'mid': 4,
            'senior': 8,
            'executive': 12
        }
        
        user_years = user_experience
        job_years = level_to_years.get(job_experience_level, 4)
        
        # Calculate similarity based on experience gap
        years_diff = abs(user_years - job_years)
        if years_diff == 0:
            score = 1.0
            reasons.append(f"Perfect experience match ({user_years} years)")
        elif years_diff <= 2:
            score = 0.8
            reasons.append(f"Close experience match (user: {user_years}, job: {job_years} years)")
        elif years_diff <= 4:
            score = 0.6
            reasons.append(f"Moderate experience match (user: {user_years}, job: {job_years} years)")
        else:
            score = 0.3
            reasons.append(f"Experience gap (user: {user_years}, job: {job_years} years)")
        
        # Level match bonus
        if user_level == job_experience_level:
            score += 0.2
            reasons.append(f"Experience level match: {user_level}")
        
        return min(score, 1.0), reasons
    
    def _calculate_location_similarity(self, user_locations: List[str], job_location: str) -> Tuple[float, List[str]]:
        """Calculate location similarity"""
        if not user_locations or not job_location:
            return 0.0, []
        
        job_location_norm = self._normalize_location(job_location)
        reasons = []
        max_score = 0.0
        
        for user_location in user_locations:
            user_location_norm = self._normalize_location(user_location)
            
            # Check for exact or alias matches
            for user_loc in user_location_norm:
                for job_loc in job_location_norm:
                    similarity = SequenceMatcher(None, user_loc, job_loc).ratio()
                    if similarity > 0.8:
                        max_score = max(max_score, similarity)
                        reasons.append(f"Location match: {user_location} → {job_location}")
                        break
            
            # Remote work bonus
            if 'remote' in user_location.lower() and 'remote' in job_location.lower():
                max_score = 1.0
                reasons.append("Remote work preference match")
        
        return min(max_score, 1.0), reasons
    
    def _calculate_salary_similarity(self, user_salary: Dict[str, Any], job_salary: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Calculate salary expectation similarity"""
        if not user_salary or not job_salary:
            return 0.5, ["Salary information not available"]  # Neutral score
        
        user_min = user_salary.get('min', 0)
        user_max = user_salary.get('max', float('inf'))
        job_min = job_salary.get('min_salary', 0)
        job_max = job_salary.get('max_salary', 0)
        
        reasons = []
        
        if job_min == 0 and job_max == 0:
            return 0.5, ["Job salary not specified"]
        
        # Convert to annual if needed
        if job_salary.get('period') == 'hour':
            job_min *= 2080  # 40 hours * 52 weeks
            job_max *= 2080 if job_max else job_min
        
        # Check overlap
        if job_max >= user_min and job_min <= user_max:
            # Calculate overlap percentage
            overlap_start = max(user_min, job_min)
            overlap_end = min(user_max, job_max)
            overlap_size = overlap_end - overlap_start
            
            user_range = user_max - user_min
            job_range = job_max - job_min if job_max > job_min else job_min * 0.2  # Assume 20% range for single values
            
            overlap_score = overlap_size / max(user_range, job_range)
            score = min(overlap_score + 0.5, 1.0)  # Base score + overlap bonus
            
            reasons.append(f"Salary overlap: ${job_min:,.0f}-${job_max:,.0f} vs expected ${user_min:,.0f}-${user_max:,.0f}")
            
            if job_min >= user_min:
                reasons.append("Job salary meets minimum expectations")
        elif job_max < user_min:
            score = 0.2
            reasons.append(f"Job salary below expectations: ${job_max:,.0f} < ${user_min:,.0f}")
        else:
            score = 0.8
            reasons.append(f"Job salary above expectations: ${job_min:,.0f} > ${user_max:,.0f}")
        
        return score, reasons
    
    def _calculate_title_similarity(self, user_titles: List[str], job_title: str) -> Tuple[float, List[str]]:
        """Calculate job title similarity"""
        if not user_titles or not job_title:
            return 0.0, []
        
        job_title_lower = job_title.lower()
        max_score = 0.0
        reasons = []
        
        for user_title in user_titles:
            user_title_lower = user_title.lower()
            similarity = SequenceMatcher(None, user_title_lower, job_title_lower).ratio()
            
            if similarity > max_score:
                max_score = similarity
            
            if similarity > 0.7:
                reasons.append(f"Title match: {user_title} → {job_title}")
        
        return max_score, reasons
    
    def match_job_to_user(self, job: Dict[str, Any], user_profile: UserProfile) -> JobMatchScore:
        """Match a single job to a user profile"""
        
        # Extract job information
        job_title = job.get('title', '')
        job_description = job.get('description', '')
        job_location = job.get('location', '')
        job_salary = job.get('salary_info', {})
        job_company = job.get('company', '')
        
        # Calculate individual similarity scores
        skill_score, skill_matches = self._calculate_skill_similarity(
            user_profile.skills, [], f"{job_title} {job_description}"
        )
        
        experience_score, exp_reasons = self._calculate_experience_similarity(
            user_profile.experience_years, user_profile.experience_level, job_description
        )
        
        location_score, location_reasons = self._calculate_location_similarity(
            user_profile.preferred_locations, job_location
        )
        
        salary_score, salary_reasons = self._calculate_salary_similarity(
            user_profile.salary_expectations, job_salary
        )
        
        title_score, title_reasons = self._calculate_title_similarity(
            user_profile.job_titles, job_title
        )
        
        # Additional scoring factors
        industry_score = 0.5  # Default neutral score
        work_preference_score = 0.7  # Default good score
        
        # Check for remote work preference
        if user_profile.work_preferences.get('remote') and 'remote' in job_description.lower():
            work_preference_score = 1.0
        
        # Calculate overall weighted score
        overall_score = (
            skill_score * self.weights['skills'] +
            experience_score * self.weights['experience'] +
            location_score * self.weights['location'] +
            salary_score * self.weights['salary']
        )
        
        # Add bonus factors
        overall_score += title_score * 0.1  # Title similarity bonus
        overall_score += industry_score * 0.05  # Industry match bonus
        overall_score += work_preference_score * 0.05  # Work preference bonus
        
        overall_score = min(overall_score, 1.0)
        
        # Compile reasons and concerns
        match_reasons = []
        concerns = []
        
        if skill_score > 0.7:
            match_reasons.extend(skill_matches[:3])  # Top 3 skill matches
        elif skill_score < 0.3:
            concerns.append("Limited skill match with job requirements")
        
        match_reasons.extend(exp_reasons)
        match_reasons.extend(location_reasons)
        match_reasons.extend(salary_reasons)
        match_reasons.extend(title_reasons)
        
        if experience_score < 0.5:
            concerns.append("Experience level mismatch")
        
        if location_score < 0.3:
            concerns.append("Location not preferred")
        
        if salary_score < 0.3:
            concerns.append("Salary below expectations")
        
        return JobMatchScore(
            overall_score=overall_score,
            skill_score=skill_score,
            experience_score=experience_score,
            location_score=location_score,
            salary_score=salary_score,
            title_score=title_score,
            industry_score=industry_score,
            work_preference_score=work_preference_score,
            match_reasons=match_reasons,
            concerns=concerns
        )
    
    def rank_jobs_for_user(self, jobs: List[Dict[str, Any]], user_profile: UserProfile, limit: int = 50) -> List[Dict[str, Any]]:
        """Rank jobs for a user and return top matches"""
        
        job_matches = []
        
        for job in jobs:
            match_score = self.match_job_to_user(job, user_profile)
            
            # Add match score to job data
            job_with_score = job.copy()
            job_with_score['match_score'] = asdict(match_score)
            job_matches.append(job_with_score)
        
        # Sort by overall score
        job_matches.sort(key=lambda x: x['match_score']['overall_score'], reverse=True)
        
        # Return top matches
        return job_matches[:limit]
    
    def generate_match_report(self, ranked_jobs: List[Dict[str, Any]], user_profile: UserProfile) -> Dict[str, Any]:
        """Generate a comprehensive match report"""
        
        if not ranked_jobs:
            return {
                'summary': 'No jobs found matching your criteria',
                'total_jobs': 0,
                'recommendations': []
            }
        
        total_jobs = len(ranked_jobs)
        excellent_matches = [job for job in ranked_jobs if job['match_score']['overall_score'] >= 0.8]
        good_matches = [job for job in ranked_jobs if 0.6 <= job['match_score']['overall_score'] < 0.8]
        potential_matches = [job for job in ranked_jobs if 0.4 <= job['match_score']['overall_score'] < 0.6]
        
        # Analyze common patterns
        top_companies = {}
        top_locations = {}
        common_skills = {}
        
        for job in ranked_jobs[:20]:  # Analyze top 20
            company = job.get('company', 'Unknown')
            location = job.get('location', 'Unknown')
            
            top_companies[company] = top_companies.get(company, 0) + 1
            top_locations[location] = top_locations.get(location, 0) + 1
        
        # Generate recommendations
        recommendations = []
        
        if excellent_matches:
            recommendations.append(f"Found {len(excellent_matches)} excellent job matches (80%+ compatibility)")
        
        if good_matches:
            recommendations.append(f"Found {len(good_matches)} good job matches (60-80% compatibility)")
        
        if potential_matches:
            recommendations.append(f"Found {len(potential_matches)} potential matches (40-60% compatibility)")
        
        # Skills gap analysis
        all_job_skills = set()
        for job in ranked_jobs[:10]:  # Top 10 jobs
            job_text = f"{job.get('title', '')} {job.get('description', '')}"
            job_skills = self._extract_skills_from_text(job_text)
            all_job_skills.update(job_skills)
        
        user_skills_norm = set(self._normalize_skills(user_profile.skills))
        missing_skills = all_job_skills - user_skills_norm
        
        if missing_skills:
            recommendations.append(f"Consider developing these in-demand skills: {', '.join(list(missing_skills)[:5])}")
        
        report = {
            'summary': f'Analyzed {total_jobs} jobs and found {len(excellent_matches)} excellent matches',
            'total_jobs': total_jobs,
            'match_distribution': {
                'excellent': len(excellent_matches),
                'good': len(good_matches),
                'potential': len(potential_matches),
                'poor': total_jobs - len(excellent_matches) - len(good_matches) - len(potential_matches)
            },
            'top_companies': dict(sorted(top_companies.items(), key=lambda x: x[1], reverse=True)[:10]),
            'top_locations': dict(sorted(top_locations.items(), key=lambda x: x[1], reverse=True)[:10]),
            'skill_gaps': list(missing_skills)[:10],
            'recommendations': recommendations,
            'user_profile_summary': {
                'skills_count': len(user_profile.skills),
                'experience_years': user_profile.experience_years,
                'preferred_locations': user_profile.preferred_locations,
                'salary_range': user_profile.salary_expectations
            }
        }
        
        return report
    
    def save_user_profile(self, profile: UserProfile, filename: str = None) -> str:
        """Save user profile to file"""
        if filename is None:
            filename = f"user_profile_{profile.user_id}.json"
        
        profile_dir = "data/user_profiles"
        os.makedirs(profile_dir, exist_ok=True)
        
        profile_path = os.path.join(profile_dir, filename)
        
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(profile), f, indent=2, ensure_ascii=False)
        
        return profile_path
    
    def load_user_profile(self, profile_path: str) -> UserProfile:
        """Load user profile from file"""
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile_data = json.load(f)
        
        return UserProfile(**profile_data)


# Example usage and testing
def create_sample_user_profile() -> UserProfile:
    """Create a sample user profile for testing"""
    return UserProfile(
        user_id="test_user_001",
        skills=["Python", "JavaScript", "React", "SQL", "Machine Learning", "AWS"],
        experience_level="mid",
        experience_years=5,
        preferred_locations=["San Francisco", "Remote", "New York"],
        salary_expectations={"min": 120000, "max": 160000, "period": "year"},
        job_titles=["Software Engineer", "Full Stack Developer", "Backend Developer"],
        industries=["Technology", "Finance", "Healthcare"],
        work_preferences={"remote": True, "hybrid": True, "onsite": False},
        education_level="Bachelor's Degree",
        certifications=["AWS Certified Developer"],
        languages=["English", "Spanish"],
        career_goals=["Tech Lead", "Senior Engineer", "Startup Experience"]
    )


def main():
    """Example usage of the JobMatcher"""
    matcher = JobMatcher()
    
    # Create sample user profile
    user_profile = create_sample_user_profile()
    
    # Save profile
    profile_path = matcher.save_user_profile(user_profile)
    print(f"User profile saved to: {profile_path}")
    
    # Sample jobs data (would come from LiveJobScraper)
    sample_jobs = [
        {
            'title': 'Senior Python Developer',
            'company': 'Tech Corp',
            'location': 'San Francisco, CA',
            'description': 'We are looking for a senior Python developer with 5+ years of experience. Must have experience with Django, REST APIs, and AWS cloud services.',
            'salary_info': {'min_salary': 140000, 'max_salary': 170000, 'period': 'year'},
            'source': 'indeed'
        },
        {
            'title': 'Frontend React Developer',
            'company': 'Startup Inc',
            'location': 'Remote',
            'description': 'Remote React developer position. Need experience with React, TypeScript, and modern frontend tools.',
            'salary_info': {'min_salary': 110000, 'max_salary': 140000, 'period': 'year'},
            'source': 'indeed'
        },
        {
            'title': 'Data Scientist',
            'company': 'Analytics Co',
            'location': 'New York, NY',
            'description': 'Machine Learning engineer role. Python, TensorFlow, AWS experience required.',
            'salary_info': {'min_salary': 130000, 'max_salary': 180000, 'period': 'year'},
            'source': 'indeed'
        }
    ]
    
    # Rank jobs for user
    ranked_jobs = matcher.rank_jobs_for_user(sample_jobs, user_profile)
    
    # Generate match report
    report = matcher.generate_match_report(ranked_jobs, user_profile)
    
    # Display results
    print("\n" + "="*50)
    print("JOB MATCHING RESULTS")
    print("="*50)
    
    print(f"\nSummary: {report['summary']}")
    print(f"Total Jobs Analyzed: {report['total_jobs']}")
    
    print(f"\nMatch Distribution:")
    for category, count in report['match_distribution'].items():
        print(f"  {category.title()}: {count}")
    
    print(f"\nTop 3 Job Matches:")
    for i, job in enumerate(ranked_jobs[:3], 1):
        score = job['match_score']
        print(f"\n{i}. {job['title']} at {job['company']}")
        print(f"   Overall Score: {score['overall_score']:.2f}")
        print(f"   Skills: {score['skill_score']:.2f} | Experience: {score['experience_score']:.2f}")
        print(f"   Location: {score['location_score']:.2f} | Salary: {score['salary_score']:.2f}")
        print(f"   Reasons: {', '.join(score['match_reasons'][:2])}")
        if score['concerns']:
            print(f"   Concerns: {', '.join(score['concerns'][:2])}")


if __name__ == "__main__":
    main()