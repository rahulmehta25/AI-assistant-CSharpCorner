#!/usr/bin/env python3
"""
Job Search Assistant - Integration script for live job scraping and matching
Demonstrates how to use the LiveJobScraper and JobMatcher together
"""

import asyncio
import json
import argparse
import sys
import os
from typing import Dict, List, Optional
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.live_job_scraper import LiveJobScraper
from modules.job_matcher import JobMatcher, UserProfile


class JobSearchAssistant:
    """Comprehensive job search assistant combining scraping and matching"""
    
    def __init__(self):
        self.scraper = LiveJobScraper()
        self.matcher = JobMatcher()
    
    async def search_and_match_jobs(
        self,
        user_profile: UserProfile,
        search_queries: List[Dict[str, str]],
        sources: List[str] = None,
        limit: int = 50
    ) -> Dict[str, any]:
        """
        Complete job search and matching workflow
        
        Args:
            user_profile: User profile for matching
            search_queries: List of search queries [{"query": "...", "location": "..."}]
            sources: Job sources to search (default: ['indeed'])
            limit: Maximum jobs to return
        """
        
        if sources is None:
            sources = ['indeed']
        
        print("🔍 Starting comprehensive job search...")
        
        # Step 1: Scrape jobs from multiple queries
        all_jobs = []
        search_results = {}
        
        for i, search_params in enumerate(search_queries, 1):
            query = search_params['query']
            location = search_params.get('location', '')
            
            print(f"\n🎯 Search {i}: '{query}' in '{location}'")
            
            try:
                results = await self.scraper.search_jobs(
                    query=query,
                    location=location,
                    sources=sources
                )
                
                jobs_found = results['total_jobs']
                print(f"   ✅ Found {jobs_found} jobs")
                
                search_results[f"search_{i}"] = results
                all_jobs.extend(results['combined'])
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                continue
        
        print(f"\n📊 Total jobs collected: {len(all_jobs)}")
        
        # Step 2: Remove duplicates and rank jobs
        if all_jobs:
            print("🎯 Ranking jobs for user profile...")
            
            ranked_jobs = self.matcher.rank_jobs_for_user(all_jobs, user_profile, limit=limit)
            
            # Step 3: Generate match report
            match_report = self.matcher.generate_match_report(ranked_jobs, user_profile)
            
            # Compile comprehensive results
            comprehensive_results = {
                'user_profile': {
                    'user_id': user_profile.user_id,
                    'skills': user_profile.skills,
                    'experience_years': user_profile.experience_years,
                    'preferred_locations': user_profile.preferred_locations,
                    'salary_expectations': user_profile.salary_expectations
                },
                'search_metadata': {
                    'queries': search_queries,
                    'sources': sources,
                    'total_jobs_scraped': len(all_jobs),
                    'jobs_ranked': len(ranked_jobs),
                    'search_time': datetime.now().isoformat()
                },
                'match_report': match_report,
                'top_matches': ranked_jobs[:20],  # Top 20 matches
                'scraping_results': search_results
            }
            
            return comprehensive_results
        
        else:
            return {
                'error': 'No jobs found',
                'search_metadata': {
                    'queries': search_queries,
                    'sources': sources,
                    'search_time': datetime.now().isoformat()
                }
            }
    
    def display_results(self, results: Dict[str, any]):
        """Display formatted search results"""
        
        if 'error' in results:
            print(f"❌ {results['error']}")
            return
        
        match_report = results['match_report']
        top_matches = results['top_matches']
        metadata = results['search_metadata']
        
        print("\n" + "="*80)
        print("📈 JOB SEARCH RESULTS")
        print("="*80)
        
        print(f"🎯 Search Summary:")
        print(f"   • Jobs Scraped: {metadata['total_jobs_scraped']}")
        print(f"   • Jobs Ranked: {metadata['jobs_ranked']}")
        print(f"   • Sources: {', '.join(metadata['sources'])}")
        
        print(f"\n📊 Match Distribution:")
        dist = match_report['match_distribution']
        print(f"   🟢 Excellent (80%+): {dist['excellent']}")
        print(f"   🟡 Good (60-80%): {dist['good']}")
        print(f"   🟠 Potential (40-60%): {dist['potential']}")
        print(f"   🔴 Poor (<40%): {dist['poor']}")
        
        if match_report.get('top_companies'):
            print(f"\n🏢 Top Companies:")
            for company, count in list(match_report['top_companies'].items())[:5]:
                print(f"   • {company}: {count} jobs")
        
        if match_report.get('recommendations'):
            print(f"\n💡 Recommendations:")
            for rec in match_report['recommendations'][:3]:
                print(f"   • {rec}")
        
        print(f"\n🎯 TOP JOB MATCHES")
        print("-" * 50)
        
        for i, job in enumerate(top_matches[:10], 1):
            score = job['match_score']
            print(f"\n{i}. {job['title']}")
            print(f"   🏢 {job['company']} | 📍 {job['location']}")
            print(f"   📊 Match Score: {score['overall_score']:.1%}")
            
            # Detailed scores
            print(f"      Skills: {score['skill_score']:.1%} | Experience: {score['experience_score']:.1%}")
            print(f"      Location: {score['location_score']:.1%} | Salary: {score['salary_score']:.1%}")
            
            # Salary
            if job.get('salary_info'):
                salary = job['salary_info']
                if salary.get('min_salary') and salary.get('max_salary'):
                    print(f"   💰 ${salary['min_salary']:,.0f} - ${salary['max_salary']:,.0f}")
            
            # Key reasons
            if score['match_reasons']:
                reasons = '; '.join(score['match_reasons'][:2])
                print(f"   ✅ {reasons}")
            
            # Concerns
            if score['concerns']:
                concerns = '; '.join(score['concerns'][:2])
                print(f"   ⚠️  {concerns}")
    
    def save_results(self, results: Dict[str, any], filename: str = None) -> str:
        """Save search results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"job_search_results_{timestamp}.json"
        
        output_path = os.path.join("data/cache/jobs", filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return output_path
    
    async def close(self):
        """Clean up resources"""
        await self.scraper.close()


def create_sample_profiles() -> Dict[str, UserProfile]:
    """Create sample user profiles for different roles"""
    
    profiles = {}
    
    # Software Engineer Profile
    profiles['software_engineer'] = UserProfile(
        user_id="software_engineer_001",
        skills=[
            "Python", "JavaScript", "React", "Node.js", "SQL", "PostgreSQL",
            "AWS", "Docker", "Git", "REST API", "Django", "Flask"
        ],
        experience_level="mid",
        experience_years=5,
        preferred_locations=["San Francisco", "New York", "Remote", "Seattle"],
        salary_expectations={"min": 120000, "max": 180000, "period": "year"},
        job_titles=["Software Engineer", "Full Stack Developer", "Backend Developer"],
        industries=["Technology", "Finance", "Healthcare"],
        work_preferences={"remote": True, "hybrid": True, "onsite": True},
        education_level="Bachelor's Degree",
        certifications=["AWS Certified Developer"],
        languages=["English"],
        career_goals=["Tech Lead", "Senior Engineer"]
    )
    
    # Data Scientist Profile
    profiles['data_scientist'] = UserProfile(
        user_id="data_scientist_001",
        skills=[
            "Python", "R", "SQL", "Machine Learning", "TensorFlow", "PyTorch",
            "Pandas", "NumPy", "Scikit-learn", "Tableau", "AWS", "Statistics"
        ],
        experience_level="senior",
        experience_years=7,
        preferred_locations=["San Francisco", "New York", "Boston", "Remote"],
        salary_expectations={"min": 140000, "max": 200000, "period": "year"},
        job_titles=["Data Scientist", "ML Engineer", "Senior Data Scientist"],
        industries=["Technology", "Finance", "Healthcare", "E-commerce"],
        work_preferences={"remote": True, "hybrid": True, "onsite": False},
        education_level="Master's Degree",
        certifications=["Google Cloud Professional ML Engineer"],
        languages=["English", "Python"],
        career_goals=["Principal Data Scientist", "ML Lead", "AI Research"]
    )
    
    # DevOps Engineer Profile
    profiles['devops_engineer'] = UserProfile(
        user_id="devops_engineer_001",
        skills=[
            "AWS", "Kubernetes", "Docker", "Terraform", "Jenkins", "Python",
            "Linux", "CI/CD", "Monitoring", "Ansible", "Git", "Shell Scripting"
        ],
        experience_level="senior",
        experience_years=6,
        preferred_locations=["Seattle", "Austin", "Denver", "Remote"],
        salary_expectations={"min": 130000, "max": 170000, "period": "year"},
        job_titles=["DevOps Engineer", "Site Reliability Engineer", "Cloud Engineer"],
        industries=["Technology", "Finance", "Startups"],
        work_preferences={"remote": True, "hybrid": True, "onsite": True},
        education_level="Bachelor's Degree",
        certifications=["AWS Solutions Architect", "Certified Kubernetes Administrator"],
        languages=["English"],
        career_goals=["Principal DevOps Engineer", "Infrastructure Lead"]
    )
    
    return profiles


async def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description='Job Search Assistant')
    parser.add_argument('--profile', choices=['software_engineer', 'data_scientist', 'devops_engineer'], 
                       default='software_engineer', help='User profile to use')
    parser.add_argument('--queries', nargs='+', 
                       default=['python developer san francisco', 'software engineer remote'],
                       help='Search queries in format "query location"')
    parser.add_argument('--sources', nargs='+', default=['indeed'], 
                       help='Job sources to search')
    parser.add_argument('--limit', type=int, default=50, 
                       help='Maximum number of jobs to return')
    parser.add_argument('--save', action='store_true', 
                       help='Save results to file')
    
    args = parser.parse_args()
    
    # Parse search queries
    search_queries = []
    for query_str in args.queries:
        parts = query_str.rsplit(' ', 1)  # Split on last space
        if len(parts) == 2:
            query, location = parts
        else:
            query, location = parts[0], ""
        search_queries.append({"query": query, "location": location})
    
    # Get user profile
    profiles = create_sample_profiles()
    user_profile = profiles[args.profile]
    
    print(f"🚀 Job Search Assistant")
    print(f"👤 Profile: {args.profile}")
    print(f"🔍 Queries: {len(search_queries)}")
    print(f"📊 Sources: {', '.join(args.sources)}")
    
    assistant = JobSearchAssistant()
    
    try:
        # Run comprehensive search
        results = await assistant.search_and_match_jobs(
            user_profile=user_profile,
            search_queries=search_queries,
            sources=args.sources,
            limit=args.limit
        )
        
        # Display results
        assistant.display_results(results)
        
        # Save results if requested
        if args.save:
            output_path = assistant.save_results(results)
            print(f"\n💾 Results saved to: {output_path}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await assistant.close()


if __name__ == "__main__":
    asyncio.run(main())