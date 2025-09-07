"""
Live Job Posting Scraper Module
Comprehensive job scraper that fetches real job postings from multiple sources.
"""

import asyncio
import json
import logging
import os
import re
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin, quote_plus
import aiohttp
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import pandas as pd
from difflib import SequenceMatcher


class JobScrapingError(Exception):
    """Custom exception for job scraping errors"""
    pass


class RateLimiter:
    """Rate limiting utility for web scraping"""
    
    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self.requests = []
    
    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = time.time()
        # Remove requests older than 1 minute
        self.requests = [req_time for req_time in self.requests if now - req_time < 60]
        
        if len(self.requests) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.requests[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
                self.requests = []
        
        self.requests.append(now)


class JobCacheManager:
    """Manage caching of job listings"""
    
    def __init__(self, cache_dir: str, ttl_hours: int = 2):
        self.cache_dir = cache_dir
        self.ttl_hours = ttl_hours
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, query: str, location: str, source: str) -> str:
        """Generate cache key for query"""
        key_string = f"{source}_{query}_{location}".lower()
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_cached_jobs(self, query: str, location: str, source: str) -> Optional[List[Dict]]:
        """Get cached jobs if available and not expired"""
        cache_key = self._get_cache_key(query, location, source)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check if cache is expired
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time > timedelta(hours=self.ttl_hours):
                return None
            
            return cache_data['jobs']
        except Exception as e:
            logging.warning(f"Error reading cache: {e}")
            return None
    
    def cache_jobs(self, query: str, location: str, source: str, jobs: List[Dict]):
        """Cache job listings"""
        cache_key = self._get_cache_key(query, location, source)
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'location': location,
            'source': source,
            'jobs': jobs
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.warning(f"Error caching jobs: {e}")


class LiveJobScraper:
    """Comprehensive job scraper for multiple sources"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "data/job_sources.json"
        self.config = self._load_config()
        self.cache_manager = JobCacheManager(
            self.config['cache_settings']['cache_directory'],
            self.config['cache_settings']['ttl_hours']
        ) if self.config['cache_settings']['enabled'] else None
        self.rate_limiters = {}
        self.session = None
        self.driver = None
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize rate limiters for each source
        for source_name, source_config in self.config['job_sources'].items():
            if source_config['enabled']:
                self.rate_limiters[source_name] = RateLimiter(
                    source_config['rate_limit']['requests_per_minute']
                )
    
    def _load_config(self) -> Dict:
        """Load job sources configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise JobScrapingError(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise JobScrapingError(f"Invalid JSON in configuration file: {e}")
    
    def _setup_selenium(self) -> webdriver.Chrome:
        """Set up Selenium WebDriver"""
        if self.driver:
            return self.driver
        
        chrome_options = Options()
        selenium_config = self.config['scraping_settings']['selenium_options']
        
        if selenium_config['headless']:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument(f'--window-size={selenium_config["window_size"][0]},{selenium_config["window_size"][1]}')
        chrome_options.add_argument(f'--user-agent={selenium_config["user_agent"]}')
        
        if selenium_config['disable_images']:
            chrome_options.add_experimental_option("prefs", {
                "profile.managed_default_content_settings.images": 2
            })
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return self.driver
        except Exception as e:
            raise JobScrapingError(f"Failed to initialize Selenium driver: {e}")
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=self.config['scraping_settings']['timeout_seconds'])
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove HTML entities
        text = text.replace('&nbsp;', ' ').replace('&amp;', '&')
        return text
    
    def _extract_salary(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract salary information from text"""
        if not text:
            return None
        
        # Common salary patterns
        patterns = [
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*-\s*\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(per\s+hour|hourly|/hr|annually|per\s+year|/year)?',
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(per\s+hour|hourly|/hr|annually|per\s+year|/year)',
            r'(\d{1,3}(?:,\d{3})*)\s*-\s*(\d{1,3}(?:,\d{3})*)\s*k\s*(per\s+year|annually)?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                groups = match.groups()
                result = {
                    'raw': text,
                    'min_salary': None,
                    'max_salary': None,
                    'period': 'year'  # default
                }
                
                if len(groups) >= 2 and groups[1]:
                    # Range pattern
                    result['min_salary'] = float(groups[0].replace(',', ''))
                    result['max_salary'] = float(groups[1].replace(',', ''))
                elif len(groups) >= 1:
                    # Single value
                    result['min_salary'] = result['max_salary'] = float(groups[0].replace(',', ''))
                
                # Determine period
                period_text = groups[-1] if groups[-1] else ''
                if 'hour' in period_text or '/hr' in period_text:
                    result['period'] = 'hour'
                elif 'k' in text.lower():
                    # Convert K values to actual numbers
                    if result['min_salary']:
                        result['min_salary'] *= 1000
                    if result['max_salary']:
                        result['max_salary'] *= 1000
                
                return result
        
        return {'raw': text, 'min_salary': None, 'max_salary': None, 'period': 'year'}
    
    def _is_duplicate(self, job: Dict, existing_jobs: List[Dict]) -> bool:
        """Check if job is a duplicate of existing jobs"""
        if not self.config['filtering']['duplicate_detection']['enabled']:
            return False
        
        threshold = self.config['filtering']['duplicate_detection']['similarity_threshold']
        fields = self.config['filtering']['duplicate_detection']['fields_to_compare']
        
        for existing_job in existing_jobs:
            similarities = []
            for field in fields:
                job_text = job.get(field, '').lower().strip()
                existing_text = existing_job.get(field, '').lower().strip()
                if job_text and existing_text:
                    similarity = SequenceMatcher(None, job_text, existing_text).ratio()
                    similarities.append(similarity)
            
            if similarities and sum(similarities) / len(similarities) >= threshold:
                return True
        
        return False
    
    def _filter_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Apply filtering rules to job listings"""
        filtered_jobs = []
        exclude_keywords = [kw.lower() for kw in self.config['filtering']['exclude_keywords']]
        required_fields = self.config['filtering']['required_fields']
        min_salary = self.config['filtering']['min_salary']
        
        for job in jobs:
            # Check required fields
            if any(not job.get(field) for field in required_fields):
                continue
            
            # Check exclude keywords
            job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
            if any(keyword in job_text for keyword in exclude_keywords):
                continue
            
            # Check minimum salary
            salary_info = job.get('salary_info')
            if (min_salary > 0 and salary_info and 
                salary_info.get('min_salary') and 
                salary_info['min_salary'] < min_salary):
                continue
            
            # Check for duplicates
            if not self._is_duplicate(job, filtered_jobs):
                filtered_jobs.append(job)
        
        return filtered_jobs
    
    async def _scrape_indeed(self, query: str, location: str = "") -> List[Dict]:
        """Scrape jobs from Indeed"""
        source_config = self.config['job_sources']['indeed']
        jobs = []
        
        try:
            # Check cache first
            if self.cache_manager:
                cached_jobs = self.cache_manager.get_cached_jobs(query, location, 'indeed')
                if cached_jobs:
                    self.logger.info(f"Using cached Indeed results for '{query}' in '{location}'")
                    return cached_jobs
            
            # Rate limiting
            if 'indeed' in self.rate_limiters:
                await self.rate_limiters['indeed'].wait_if_needed()
            
            # Set up Selenium
            driver = self._setup_selenium()
            
            # Build search URL
            params = {
                'q': query,
                'l': location,
                'fromage': '7',  # Last 7 days
                'limit': '50'
            }
            
            search_url = f"{source_config['base_url']}/jobs?" + "&".join([f"{k}={quote_plus(str(v))}" for k, v in params.items()])
            
            self.logger.info(f"Scraping Indeed: {search_url}")
            driver.get(search_url)
            
            # Wait for job listings to load
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, source_config['selectors']['job_listings']))
                )
            except TimeoutException:
                self.logger.warning("Timeout waiting for Indeed job listings")
                return jobs
            
            # Scrape multiple pages
            page_count = 0
            max_pages = self.config['scraping_settings']['max_pages_per_source']
            
            while page_count < max_pages:
                # Get job listings from current page
                job_elements = driver.find_elements(By.CSS_SELECTOR, source_config['selectors']['job_listings'])
                
                for job_element in job_elements:
                    try:
                        # Extract job data
                        job_data = {
                            'source': 'indeed',
                            'scraped_at': datetime.now().isoformat(),
                            'title': '',
                            'company': '',
                            'location': '',
                            'salary_raw': '',
                            'salary_info': None,
                            'description': '',
                            'url': '',
                            'job_id': ''
                        }
                        
                        # Job title
                        title_elem = job_element.find_element(By.CSS_SELECTOR, source_config['selectors']['job_title'])
                        job_data['title'] = self._clean_text(title_elem.text) if title_elem else ''
                        
                        # Company
                        try:
                            company_elem = job_element.find_element(By.CSS_SELECTOR, source_config['selectors']['company'])
                            job_data['company'] = self._clean_text(company_elem.text)
                        except:
                            pass
                        
                        # Location
                        try:
                            location_elem = job_element.find_element(By.CSS_SELECTOR, source_config['selectors']['location'])
                            job_data['location'] = self._clean_text(location_elem.text)
                        except:
                            pass
                        
                        # Salary
                        try:
                            salary_elem = job_element.find_element(By.CSS_SELECTOR, source_config['selectors']['salary'])
                            job_data['salary_raw'] = self._clean_text(salary_elem.text)
                            job_data['salary_info'] = self._extract_salary(job_data['salary_raw'])
                        except:
                            pass
                        
                        # Job URL
                        try:
                            url_elem = job_element.find_element(By.CSS_SELECTOR, source_config['selectors']['job_url'])
                            job_data['url'] = urljoin(source_config['base_url'], url_elem.get_attribute('href'))
                            # Extract job ID from URL
                            job_id_match = re.search(r'jk=([^&]+)', job_data['url'])
                            job_data['job_id'] = job_id_match.group(1) if job_id_match else ''
                        except:
                            pass
                        
                        # Basic description (summary)
                        try:
                            desc_elem = job_element.find_element(By.CSS_SELECTOR, ".job-snippet")
                            job_data['description'] = self._clean_text(desc_elem.text)
                        except:
                            pass
                        
                        if job_data['title'] and job_data['company']:
                            jobs.append(job_data)
                        
                    except Exception as e:
                        self.logger.warning(f"Error extracting Indeed job: {e}")
                        continue
                
                # Try to go to next page
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, source_config['selectors']['next_page'])
                    if next_button and next_button.is_enabled():
                        driver.execute_script("arguments[0].click();", next_button)
                        await asyncio.sleep(3)  # Wait for page to load
                        page_count += 1
                    else:
                        break
                except:
                    break
            
            # Cache results
            if self.cache_manager and jobs:
                self.cache_manager.cache_jobs(query, location, 'indeed', jobs)
            
            self.logger.info(f"Scraped {len(jobs)} jobs from Indeed")
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error scraping Indeed: {e}")
            return jobs
    
    async def _scrape_glassdoor(self, query: str, location: str = "") -> List[Dict]:
        """Scrape jobs from Glassdoor (simplified version due to anti-bot measures)"""
        # Note: Glassdoor has strong anti-bot measures, so this is a simplified implementation
        jobs = []
        
        try:
            # Check cache first
            if self.cache_manager:
                cached_jobs = self.cache_manager.get_cached_jobs(query, location, 'glassdoor')
                if cached_jobs:
                    self.logger.info(f"Using cached Glassdoor results for '{query}' in '{location}'")
                    return cached_jobs
            
            # Rate limiting
            if 'glassdoor' in self.rate_limiters:
                await self.rate_limiters['glassdoor'].wait_if_needed()
            
            self.logger.info("Glassdoor scraping is limited due to anti-bot measures")
            # Implementation would go here with more sophisticated bot detection evasion
            
        except Exception as e:
            self.logger.error(f"Error scraping Glassdoor: {e}")
        
        return jobs
    
    async def _scrape_linkedin(self, query: str, location: str = "") -> List[Dict]:
        """Scrape jobs from LinkedIn (simplified version due to login requirements)"""
        # Note: LinkedIn requires authentication for most job data
        jobs = []
        
        try:
            # Check cache first
            if self.cache_manager:
                cached_jobs = self.cache_manager.get_cached_jobs(query, location, 'linkedin')
                if cached_jobs:
                    self.logger.info(f"Using cached LinkedIn results for '{query}' in '{location}'")
                    return cached_jobs
            
            # Rate limiting
            if 'linkedin' in self.rate_limiters:
                await self.rate_limiters['linkedin'].wait_if_needed()
            
            self.logger.info("LinkedIn scraping requires authentication - using public job search")
            # Implementation would go here with LinkedIn public job search
            
        except Exception as e:
            self.logger.error(f"Error scraping LinkedIn: {e}")
        
        return jobs
    
    def match_to_onet_careers(self, jobs: List[Dict], onet_careers_path: str = "data/careers") -> List[Dict]:
        """Match job postings to O*NET career codes"""
        if not os.path.exists(onet_careers_path):
            self.logger.warning(f"O*NET careers directory not found: {onet_careers_path}")
            return jobs
        
        # Load O*NET career data
        onet_careers = {}
        for filename in os.listdir(onet_careers_path):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(onet_careers_path, filename), 'r', encoding='utf-8') as f:
                        career_data = json.load(f)
                        if 'career_code' in career_data:
                            onet_careers[career_data['career_code']] = career_data
                except Exception as e:
                    continue
        
        # Match jobs to careers
        for job in jobs:
            best_match = None
            best_score = 0
            
            job_title = job.get('title', '').lower()
            job_description = job.get('description', '').lower()
            
            for career_code, career_data in onet_careers.items():
                career_title = career_data.get('title', '').lower()
                alt_titles = [title.lower() for title in career_data.get('alternate_titles', [])]
                tasks = ' '.join(career_data.get('tasks', [])).lower()
                
                # Calculate similarity score
                title_similarity = SequenceMatcher(None, job_title, career_title).ratio()
                alt_title_similarities = [SequenceMatcher(None, job_title, alt_title).ratio() for alt_title in alt_titles]
                max_alt_similarity = max(alt_title_similarities) if alt_title_similarities else 0
                task_similarity = SequenceMatcher(None, job_description, tasks).ratio() if tasks else 0
                
                # Combined score
                score = (title_similarity * 0.5 + max_alt_similarity * 0.3 + task_similarity * 0.2)
                
                if score > best_score and score >= self.config['onet_integration']['career_matching_threshold']:
                    best_match = {
                        'career_code': career_code,
                        'career_title': career_data.get('title'),
                        'match_score': score
                    }
                    best_score = score
            
            job['onet_match'] = best_match
        
        return jobs
    
    async def search_jobs(self, query: str, location: str = "", sources: List[str] = None) -> Dict[str, List[Dict]]:
        """Search for jobs across multiple sources"""
        if sources is None:
            sources = [name for name, config in self.config['job_sources'].items() if config['enabled']]
        
        results = {}
        all_jobs = []
        
        # Scrape from each enabled source
        scraping_tasks = []
        
        for source in sources:
            if source not in self.config['job_sources'] or not self.config['job_sources'][source]['enabled']:
                continue
            
            if source == 'indeed':
                scraping_tasks.append(('indeed', self._scrape_indeed(query, location)))
            elif source == 'glassdoor':
                scraping_tasks.append(('glassdoor', self._scrape_glassdoor(query, location)))
            elif source == 'linkedin':
                scraping_tasks.append(('linkedin', self._scrape_linkedin(query, location)))
        
        # Execute all scraping tasks concurrently
        if scraping_tasks:
            tasks = [task for _, task in scraping_tasks]
            source_names = [name for name, _ in scraping_tasks]
            
            completed_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(completed_results):
                source_name = source_names[i]
                if isinstance(result, Exception):
                    self.logger.error(f"Error scraping {source_name}: {result}")
                    results[source_name] = []
                else:
                    results[source_name] = result
                    all_jobs.extend(result)
        
        # Filter and deduplicate
        filtered_jobs = self._filter_jobs(all_jobs)
        
        # Match to O*NET careers if enabled
        if self.config['onet_integration']['enabled']:
            filtered_jobs = self.match_to_onet_careers(filtered_jobs)
        
        # Limit total results
        max_jobs = self.config['scraping_settings']['max_jobs_per_query']
        if len(filtered_jobs) > max_jobs:
            # Sort by recency and take top results
            filtered_jobs.sort(key=lambda x: x.get('scraped_at', ''), reverse=True)
            filtered_jobs = filtered_jobs[:max_jobs]
        
        results['combined'] = filtered_jobs
        results['total_jobs'] = len(filtered_jobs)
        results['search_metadata'] = {
            'query': query,
            'location': location,
            'sources_used': sources,
            'scraped_at': datetime.now().isoformat(),
            'jobs_found': {source: len(jobs) for source, jobs in results.items() if source != 'combined' and source != 'total_jobs'}
        }
        
        return results
    
    def export_jobs(self, jobs_data: Dict, filename: str = None) -> str:
        """Export job data to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"job_search_{timestamp}.json"
        
        export_path = os.path.join("data/cache/jobs", filename)
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(jobs_data, f, indent=2, ensure_ascii=False)
        
        return export_path
    
    async def close(self):
        """Clean up resources"""
        if self.session:
            await self.session.close()
        if self.driver:
            self.driver.quit()


# Example usage and testing
async def main():
    """Example usage of the LiveJobScraper"""
    scraper = LiveJobScraper()
    
    try:
        # Search for software engineer jobs
        results = await scraper.search_jobs(
            query="software engineer python",
            location="San Francisco, CA",
            sources=['indeed']
        )
        
        print(f"Found {results['total_jobs']} jobs total")
        for source, jobs in results.items():
            if source not in ['combined', 'total_jobs', 'search_metadata']:
                print(f"{source}: {len(jobs)} jobs")
        
        # Export results
        if results['combined']:
            export_path = scraper.export_jobs(results)
            print(f"Results exported to: {export_path}")
        
        # Display sample jobs
        sample_jobs = results['combined'][:3]
        for job in sample_jobs:
            print(f"\nTitle: {job['title']}")
            print(f"Company: {job['company']}")
            print(f"Location: {job['location']}")
            print(f"Source: {job['source']}")
            if job.get('onet_match'):
                print(f"O*NET Match: {job['onet_match']['career_title']} ({job['onet_match']['match_score']:.2f})")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())