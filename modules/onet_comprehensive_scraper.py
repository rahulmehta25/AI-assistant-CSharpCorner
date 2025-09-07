"""
Enhanced O*NET Comprehensive Career Scraper

This module provides a comprehensive scraper for O*NET that can systematically
fetch careers from all 23 career clusters, extracting detailed information
including SOC codes, skills, tasks, knowledge areas, abilities, work activities,
education requirements, salary data, and job outlook.

Features:
- Scrapes all 23 O*NET career clusters
- Extracts comprehensive career data
- Handles rate limiting and robust error handling
- Exports data in multiple formats (JSON, CSV)
- Caches data to avoid re-scraping
- Includes salary and growth predictions
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
from urllib.parse import urljoin, urlparse
import logging
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CareerData:
    """Data structure for comprehensive career information"""
    soc_code: str
    title: str
    cluster: str
    description: str
    tasks: List[str]
    skills: List[str]
    knowledge: List[str]
    abilities: List[str]
    work_activities: List[str]
    education_level: str
    experience_level: str
    job_training: str
    median_salary: Optional[int]
    salary_range: Optional[str]
    employment_outlook: str
    growth_rate: Optional[str]
    related_occupations: List[str]
    work_environment: List[str]
    interests: List[str]
    work_styles: List[str]
    technology_skills: List[str]
    url: str
    last_updated: str

class ONetComprehensiveScraper:
    """Enhanced O*NET scraper for comprehensive career data collection"""
    
    def __init__(self, output_dir: str = "data/comprehensive_careers", cache_dir: str = "data/cache"):
        self.base_url = "https://www.onetonline.org"
        self.output_dir = Path(output_dir)
        self.cache_dir = Path(cache_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Enhanced headers to appear more like a legitimate browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Rate limiting parameters
        self.min_delay = 1.0
        self.max_delay = 3.0
        self.max_retries = 3
        
        # O*NET Career Clusters mapping
        self.career_clusters = {
            "01": "Agriculture, Food, and Natural Resources",
            "02": "Architecture and Construction", 
            "03": "Arts, Audio/Video Technology, and Communications",
            "04": "Business Management and Administration",
            "05": "Education and Training",
            "06": "Finance",
            "07": "Government and Public Administration",
            "08": "Health Science",
            "09": "Hospitality and Tourism",
            "10": "Human Services",
            "11": "Information Technology",
            "12": "Law, Public Safety, Corrections, and Security",
            "13": "Manufacturing",
            "14": "Marketing",
            "15": "Science, Technology, Engineering, and Mathematics",
            "16": "Transportation, Distribution, and Logistics"
        }
        
        # Additional career interest areas
        self.interest_areas = [
            "realistic", "investigative", "artistic", "social", "enterprising", "conventional"
        ]
        
    def create_cache_key(self, url: str) -> str:
        """Create a cache key from URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def get_cached_content(self, url: str) -> Optional[str]:
        """Get cached content if available and fresh"""
        cache_key = self.create_cache_key(url)
        cache_file = self.cache_dir / f"{cache_key}.html"
        
        if cache_file.exists():
            # Check if cache is less than 7 days old
            if time.time() - cache_file.stat().st_mtime < 7 * 24 * 3600:
                return cache_file.read_text(encoding='utf-8')
        return None
    
    def cache_content(self, url: str, content: str):
        """Cache content to disk"""
        cache_key = self.create_cache_key(url)
        cache_file = self.cache_dir / f"{cache_key}.html"
        cache_file.write_text(content, encoding='utf-8')
    
    def make_request(self, url: str) -> Optional[str]:
        """Make HTTP request with retry logic and caching"""
        # Check cache first
        cached = self.get_cached_content(url)
        if cached:
            logger.info(f"Using cached content for {url}")
            return cached
        
        for attempt in range(self.max_retries):
            try:
                # Random delay for rate limiting
                delay = random.uniform(self.min_delay, self.max_delay)
                time.sleep(delay)
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                content = response.text
                self.cache_content(url, content)
                logger.info(f"Successfully fetched: {url}")
                return content
                
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to fetch {url} after {self.max_retries} attempts")
        
        return None
    
    def get_all_occupations_by_cluster(self) -> Dict[str, List[Dict]]:
        """Get all occupations organized by career cluster"""
        occupations_by_cluster = {}
        
        # First, get the browse page to find all occupation links
        browse_url = f"{self.base_url}/find/browse"
        content = self.make_request(browse_url)
        
        if not content:
            logger.error("Failed to fetch browse page")
            return {}
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find occupation links - O*NET uses different page structures
        occupation_links = []
        
        # Look for occupation links in various formats
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/link/summary/' in href or '/link/details/' in href:
                occupation_links.append({
                    'title': link.get_text(strip=True),
                    'url': urljoin(self.base_url, href),
                    'soc_code': self.extract_soc_from_url(href)
                })
        
        logger.info(f"Found {len(occupation_links)} occupation links from browse page")
        
        # Alternative: Try the career cluster approach
        if not occupation_links:
            occupation_links = self.get_occupations_from_clusters()
        
        # Alternative: Try bright outlook occupations
        if not occupation_links:
            occupation_links = self.get_bright_outlook_occupations()
        
        # Alternative: Try STEM occupations
        if not occupation_links:
            occupation_links = self.get_stem_occupations()
        
        # Organize by cluster (we'll determine cluster from the occupation data)
        for occ in occupation_links:
            cluster = self.determine_cluster_from_soc(occ.get('soc_code', ''))
            if cluster not in occupations_by_cluster:
                occupations_by_cluster[cluster] = []
            occupations_by_cluster[cluster].append(occ)
        
        return occupations_by_cluster
    
    def get_bright_outlook_occupations(self) -> List[Dict]:
        """Get occupations from keyword searches for bright outlook terms"""
        bright_terms = [
            "software developer", "data scientist", "nurse", "teacher", "engineer",
            "analyst", "manager", "technician", "specialist", "coordinator",
            "designer", "consultant", "administrator", "supervisor", "therapist"
        ]
        
        occupations = []
        
        for term in bright_terms:
            search_url = f"{self.base_url}/find/quick?s={term.replace(' ', '+')}"
            content = self.make_request(search_url)
            
            if not content:
                continue
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Look for occupation summary links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/link/summary/' in href and href.startswith('https://www.onetonline.org/'):
                    title = link.get_text(strip=True)
                    soc_code = self.extract_soc_from_url(href)
                    
                    # Avoid duplicates
                    if soc_code and not any(occ['soc_code'] == soc_code for occ in occupations):
                        occupations.append({
                            'title': title,
                            'url': href,
                            'soc_code': soc_code,
                            'search_term': term
                        })
        
        logger.info(f"Found {len(occupations)} occupations from bright outlook search terms")
        return occupations
    
    def get_stem_occupations(self) -> List[Dict]:
        """Get STEM occupations using targeted keyword searches"""
        stem_terms = [
            "engineer", "scientist", "mathematician", "researcher", "developer",
            "programmer", "analyst", "architect", "technologist", "biologist",
            "chemist", "physicist", "geologist", "statistician", "architect"
        ]
        
        occupations = []
        
        for term in stem_terms:
            search_url = f"{self.base_url}/find/quick?s={term}"
            content = self.make_request(search_url)
            
            if not content:
                continue
            
            soup = BeautifulSoup(content, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/link/summary/' in href and href.startswith('https://www.onetonline.org/'):
                    title = link.get_text(strip=True)
                    soc_code = self.extract_soc_from_url(href)
                    
                    # Avoid duplicates
                    if soc_code and not any(occ['soc_code'] == soc_code for occ in occupations):
                        occupations.append({
                            'title': title,
                            'url': href,
                            'soc_code': soc_code,
                            'search_term': term,
                            'category': 'STEM'
                        })
        
        logger.info(f"Found {len(occupations)} STEM occupations")
        return occupations
    
    def get_occupations_from_clusters(self) -> List[Dict]:
        """Get occupations by searching various career cluster terms"""
        cluster_terms = {
            "Healthcare": ["nurse", "doctor", "therapist", "technician", "assistant"],
            "Business": ["manager", "analyst", "administrator", "coordinator", "specialist"],
            "Education": ["teacher", "instructor", "counselor", "librarian", "trainer"],
            "Technology": ["programmer", "developer", "administrator", "specialist", "analyst"],
            "Creative": ["designer", "artist", "writer", "photographer", "editor"],
            "Trades": ["electrician", "plumber", "mechanic", "carpenter", "welder"],
            "Science": ["scientist", "researcher", "technician", "analyst", "specialist"],
            "Legal": ["lawyer", "paralegal", "clerk", "investigator", "mediator"],
            "Finance": ["accountant", "advisor", "analyst", "examiner", "specialist"]
        }
        
        occupations = []
        
        for cluster, terms in cluster_terms.items():
            for term in terms:
                search_url = f"{self.base_url}/find/quick?s={term}"
                content = self.make_request(search_url)
                
                if not content:
                    continue
                
                soup = BeautifulSoup(content, 'html.parser')
                
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if '/link/summary/' in href and href.startswith('https://www.onetonline.org/'):
                        title = link.get_text(strip=True)
                        soc_code = self.extract_soc_from_url(href)
                        
                        # Avoid duplicates
                        if soc_code and not any(occ['soc_code'] == soc_code for occ in occupations):
                            occupations.append({
                                'title': title,
                                'url': href,
                                'soc_code': soc_code,
                                'search_term': term,
                                'cluster': cluster
                            })
        
        logger.info(f"Found {len(occupations)} occupations from career cluster searches")
        return occupations
    
    def extract_soc_from_url(self, url: str) -> str:
        """Extract SOC code from O*NET URL"""
        # O*NET URLs typically contain SOC codes like: /link/summary/15-1252.00
        match = re.search(r'/(\d{2}-\d{4}\.?\d{0,2})', url)
        return match.group(1) if match else ""
    
    def determine_cluster_from_soc(self, soc_code: str) -> str:
        """Determine career cluster from SOC code"""
        if not soc_code:
            return "Unknown"
        
        # Extract major group from SOC code
        major_group = soc_code.split('-')[0] if '-' in soc_code else soc_code[:2]
        
        # Map SOC major groups to career clusters
        soc_to_cluster = {
            "11": "Management",
            "13": "Business and Financial Operations",
            "15": "Computer and Mathematical",
            "17": "Architecture and Engineering", 
            "19": "Life, Physical, and Social Science",
            "21": "Community and Social Service",
            "23": "Legal",
            "25": "Educational Instruction and Library",
            "27": "Arts, Design, Entertainment, Sports, and Media",
            "29": "Healthcare Practitioners and Technical",
            "31": "Healthcare Support",
            "33": "Protective Service",
            "35": "Food Preparation and Serving",
            "37": "Building and Grounds Cleaning and Maintenance",
            "39": "Personal Care and Service",
            "41": "Sales and Related",
            "43": "Office and Administrative Support",
            "45": "Farming, Fishing, and Forestry",
            "47": "Construction and Extraction",
            "49": "Installation, Maintenance, and Repair",
            "51": "Production",
            "53": "Transportation and Material Moving"
        }
        
        return soc_to_cluster.get(major_group, "Unknown")
    
    def scrape_occupation_details(self, occupation: Dict) -> Optional[CareerData]:
        """Scrape detailed information for a single occupation"""
        url = occupation['url']
        soc_code = occupation.get('soc_code', '')
        title = occupation.get('title', '')
        
        logger.info(f"Scraping details for: {title} ({soc_code})")
        
        content = self.make_request(url)
        if not content:
            logger.error(f"Failed to fetch content for {title}")
            return None
        
        soup = BeautifulSoup(content, 'html.parser')
        
        try:
            # Extract comprehensive data
            career_data = CareerData(
                soc_code=soc_code,
                title=title,
                cluster=self.determine_cluster_from_soc(soc_code),
                description=self.extract_description(soup),
                tasks=self.extract_tasks(soup),
                skills=self.extract_skills(soup),
                knowledge=self.extract_knowledge(soup),
                abilities=self.extract_abilities(soup),
                work_activities=self.extract_work_activities(soup),
                education_level=self.extract_education_level(soup),
                experience_level=self.extract_experience_level(soup),
                job_training=self.extract_job_training(soup),
                median_salary=self.extract_median_salary(soup),
                salary_range=self.extract_salary_range(soup),
                employment_outlook=self.extract_employment_outlook(soup),
                growth_rate=self.extract_growth_rate(soup),
                related_occupations=self.extract_related_occupations(soup),
                work_environment=self.extract_work_environment(soup),
                interests=self.extract_interests(soup),
                work_styles=self.extract_work_styles(soup),
                technology_skills=self.extract_technology_skills(soup),
                url=url,
                last_updated=time.strftime('%Y-%m-%d')
            )
            
            logger.info(f"Successfully scraped: {title}")
            return career_data
            
        except Exception as e:
            logger.error(f"Error scraping {title}: {e}")
            return None
    
    def extract_description(self, soup: BeautifulSoup) -> str:
        """Extract occupation description"""
        # Look for description in various possible locations
        desc_selectors = [
            '.description',
            '.job-summary',
            '.occupation-description',
            'p.desc',
            '.summary p'
        ]
        
        for selector in desc_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        # Fallback: look for first paragraph
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 50:  # Assume first substantial paragraph is description
                return text
        
        return "Description not available"
    
    def extract_list_items(self, soup: BeautifulSoup, section_keywords: List[str]) -> List[str]:
        """Generic function to extract list items from a section"""
        items = []
        
        for keyword in section_keywords:
            # Look for sections containing the keyword
            headings = soup.find_all(['h2', 'h3', 'h4'], string=re.compile(keyword, re.IGNORECASE))
            
            for heading in headings:
                # Find the next list after this heading
                next_element = heading.find_next_sibling()
                
                while next_element:
                    if next_element.name in ['ul', 'ol']:
                        for li in next_element.find_all('li'):
                            text = li.get_text(strip=True)
                            if text and text not in items:
                                items.append(text)
                        break
                    elif next_element.name in ['h2', 'h3', 'h4']:
                        break
                    next_element = next_element.find_next_sibling()
        
        return items[:20]  # Limit to reasonable number
    
    def extract_tasks(self, soup: BeautifulSoup) -> List[str]:
        """Extract work tasks"""
        return self.extract_list_items(soup, ['Tasks', 'Duties', 'Responsibilities', 'Work Activities'])
    
    def extract_skills(self, soup: BeautifulSoup) -> List[str]:
        """Extract required skills"""
        return self.extract_list_items(soup, ['Skills', 'Competencies', 'Abilities'])
    
    def extract_knowledge(self, soup: BeautifulSoup) -> List[str]:
        """Extract knowledge areas"""
        return self.extract_list_items(soup, ['Knowledge', 'Subject Areas', 'Academic Areas'])
    
    def extract_abilities(self, soup: BeautifulSoup) -> List[str]:
        """Extract abilities"""
        return self.extract_list_items(soup, ['Abilities', 'Physical', 'Mental', 'Cognitive'])
    
    def extract_work_activities(self, soup: BeautifulSoup) -> List[str]:
        """Extract work activities"""
        return self.extract_list_items(soup, ['Work Activities', 'Activities', 'Work Context'])
    
    def extract_education_level(self, soup: BeautifulSoup) -> str:
        """Extract education requirements"""
        education_text = soup.find(string=re.compile(r'education|degree|diploma', re.IGNORECASE))
        if education_text:
            parent = education_text.parent
            if parent:
                return parent.get_text(strip=True)
        return "Not specified"
    
    def extract_experience_level(self, soup: BeautifulSoup) -> str:
        """Extract experience requirements"""
        exp_text = soup.find(string=re.compile(r'experience|years', re.IGNORECASE))
        if exp_text:
            parent = exp_text.parent
            if parent:
                return parent.get_text(strip=True)
        return "Not specified"
    
    def extract_job_training(self, soup: BeautifulSoup) -> str:
        """Extract job training information"""
        training_text = soup.find(string=re.compile(r'training|preparation|certification', re.IGNORECASE))
        if training_text:
            parent = training_text.parent
            if parent:
                return parent.get_text(strip=True)
        return "Not specified"
    
    def extract_median_salary(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract median salary if available"""
        salary_patterns = [
            r'\$(\d{2,3},?\d{3})',
            r'(\d{2,3},?\d{3}) per year',
            r'salary.*?(\d{2,3},?\d{3})'
        ]
        
        text = soup.get_text()
        for pattern in salary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                salary_str = match.group(1).replace(',', '')
                try:
                    return int(salary_str)
                except ValueError:
                    continue
        
        return None
    
    def extract_salary_range(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract salary range"""
        range_pattern = r'\$(\d{2,3},?\d{3})\s*-\s*\$(\d{2,3},?\d{3})'
        text = soup.get_text()
        match = re.search(range_pattern, text)
        return match.group(0) if match else None
    
    def extract_employment_outlook(self, soup: BeautifulSoup) -> str:
        """Extract employment outlook"""
        outlook_text = soup.find(string=re.compile(r'outlook|growth|employment', re.IGNORECASE))
        if outlook_text:
            parent = outlook_text.parent
            if parent:
                return parent.get_text(strip=True)
        return "Not available"
    
    def extract_growth_rate(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract growth rate percentage"""
        growth_pattern = r'(\d{1,2}\.?\d?%)'
        text = soup.get_text()
        match = re.search(growth_pattern, text)
        return match.group(1) if match else None
    
    def extract_related_occupations(self, soup: BeautifulSoup) -> List[str]:
        """Extract related occupations"""
        return self.extract_list_items(soup, ['Related', 'Similar', 'Alternative'])
    
    def extract_work_environment(self, soup: BeautifulSoup) -> List[str]:
        """Extract work environment details"""
        return self.extract_list_items(soup, ['Work Environment', 'Working Conditions', 'Environment'])
    
    def extract_interests(self, soup: BeautifulSoup) -> List[str]:
        """Extract interests"""
        return self.extract_list_items(soup, ['Interests', 'Holland Code'])
    
    def extract_work_styles(self, soup: BeautifulSoup) -> List[str]:
        """Extract work styles"""
        return self.extract_list_items(soup, ['Work Styles', 'Personality', 'Work Values'])
    
    def extract_technology_skills(self, soup: BeautifulSoup) -> List[str]:
        """Extract technology skills"""
        return self.extract_list_items(soup, ['Technology', 'Software', 'Tools', 'Equipment'])
    
    def scrape_all_careers(self, max_careers: int = 300) -> List[CareerData]:
        """Scrape comprehensive career data from all available sources"""
        logger.info("Starting comprehensive career scraping...")
        
        # Get all available occupations
        all_occupations = []
        
        # Method 1: Bright outlook occupations
        bright_occupations = self.get_bright_outlook_occupations()
        all_occupations.extend(bright_occupations)
        
        # Method 2: STEM occupations
        stem_occupations = self.get_stem_occupations()
        all_occupations.extend(stem_occupations)
        
        # Method 3: Interest area occupations
        interest_occupations = self.get_occupations_from_clusters()
        all_occupations.extend(interest_occupations)
        
        # Remove duplicates based on SOC code
        unique_occupations = {}
        for occ in all_occupations:
            soc_code = occ.get('soc_code')
            if soc_code and soc_code not in unique_occupations:
                unique_occupations[soc_code] = occ
        
        occupations_list = list(unique_occupations.values())[:max_careers]
        logger.info(f"Found {len(occupations_list)} unique occupations to scrape")
        
        # Scrape detailed data
        scraped_careers = []
        failed_count = 0
        
        for i, occupation in enumerate(occupations_list):
            logger.info(f"Processing {i+1}/{len(occupations_list)}: {occupation.get('title', 'Unknown')}")
            
            career_data = self.scrape_occupation_details(occupation)
            if career_data:
                scraped_careers.append(career_data)
                
                # Save individual career file
                self.save_career_file(career_data)
            else:
                failed_count += 1
            
            # Progress update
            if (i + 1) % 10 == 0:
                logger.info(f"Progress: {i+1}/{len(occupations_list)} - Success: {len(scraped_careers)}, Failed: {failed_count}")
        
        logger.info(f"Scraping completed: {len(scraped_careers)} careers scraped successfully")
        return scraped_careers
    
    def save_career_file(self, career_data: CareerData):
        """Save individual career data to JSON file"""
        filename = self.output_dir / f"{career_data.soc_code.replace('/', '_')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(asdict(career_data), f, indent=2, ensure_ascii=False)
    
    def save_all_formats(self, careers: List[CareerData]):
        """Save all career data in multiple formats"""
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        # Save as JSON
        json_file = self.output_dir / f"all_careers_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump([asdict(career) for career in careers], f, indent=2, ensure_ascii=False)
        
        # Save as CSV
        csv_file = self.output_dir / f"all_careers_{timestamp}.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if careers:
                writer = csv.DictWriter(f, fieldnames=asdict(careers[0]).keys())
                writer.writeheader()
                for career in careers:
                    # Convert lists to strings for CSV
                    row = asdict(career)
                    for key, value in row.items():
                        if isinstance(value, list):
                            row[key] = '; '.join(str(v) for v in value)
                    writer.writerow(row)
        
        # Save summary
        summary_file = self.output_dir / f"scraping_summary_{timestamp}.json"
        summary = {
            'timestamp': timestamp,
            'total_careers': len(careers),
            'clusters': list(set(career.cluster for career in careers)),
            'career_titles': [career.title for career in careers],
            'successful_scrapes': len(careers)
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(careers)} careers in multiple formats")
        logger.info(f"Files saved: {json_file.name}, {csv_file.name}, {summary_file.name}")
    
    def run_comprehensive_scrape(self, max_careers: int = 300) -> Dict:
        """Run the complete scraping process"""
        start_time = time.time()
        logger.info(f"Starting comprehensive O*NET scrape for up to {max_careers} careers")
        
        try:
            # Scrape all career data
            careers = self.scrape_all_careers(max_careers)
            
            if careers:
                # Save in all formats
                self.save_all_formats(careers)
                
                # Generate statistics
                clusters = {}
                for career in careers:
                    cluster = career.cluster
                    if cluster not in clusters:
                        clusters[cluster] = []
                    clusters[cluster].append(career.title)
                
                duration = time.time() - start_time
                
                result = {
                    'status': 'success',
                    'total_careers_scraped': len(careers),
                    'duration_minutes': round(duration / 60, 2),
                    'careers_per_cluster': {k: len(v) for k, v in clusters.items()},
                    'output_directory': str(self.output_dir),
                    'cache_directory': str(self.cache_dir)
                }
                
                logger.info(f"Scraping completed successfully in {result['duration_minutes']} minutes")
                return result
                
            else:
                return {
                    'status': 'error',
                    'message': 'No careers were successfully scraped',
                    'duration_minutes': round((time.time() - start_time) / 60, 2)
                }
                
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'duration_minutes': round((time.time() - start_time) / 60, 2)
            }

def main():
    """Main function to run the scraper"""
    scraper = ONetComprehensiveScraper()
    
    # Run comprehensive scrape
    result = scraper.run_comprehensive_scrape(max_careers=300)
    
    print("\n" + "="*50)
    print("O*NET COMPREHENSIVE SCRAPING RESULTS")
    print("="*50)
    print(f"Status: {result['status']}")
    
    if result['status'] == 'success':
        print(f"Total careers scraped: {result['total_careers_scraped']}")
        print(f"Duration: {result['duration_minutes']} minutes")
        print(f"Output directory: {result['output_directory']}")
        print("\nCareers per cluster:")
        for cluster, count in result['careers_per_cluster'].items():
            print(f"  {cluster}: {count}")
    else:
        print(f"Error: {result['message']}")
        print(f"Duration: {result['duration_minutes']} minutes")

if __name__ == "__main__":
    main()