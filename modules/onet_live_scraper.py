import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
import re
from urllib.parse import urljoin

class ONetLiveScraper:
    def __init__(self, output_path: str = "data/careers/"):
        self.base_url = "https://www.onetonline.org"
        self.output_path = Path(output_path)
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_bright_outlook_careers(self, max_careers: int = 50) -> List[Dict]:
        """Fetch careers from O*NET's Bright Outlook section"""
        print("Fetching Bright Outlook careers from O*NET...")
        careers = []
        
        # URLs with parameters for bright outlook careers
        bright_urls = [
            f"{self.base_url}/find/bright?b=1&g=Go",  # Rapid growth
            f"{self.base_url}/find/bright?b=2&g=Go",  # Numerous openings
            f"{self.base_url}/find/bright?b=3&g=Go",  # New and emerging
        ]
        
        for bright_url in bright_urls:
            if len(careers) >= max_careers:
                break
                
            try:
                response = self.session.get(bright_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find career links - they're in table rows with occupation titles
                # Look for links with pattern /link/summary/XX-XXXX.XX
                career_links = soup.find_all('a', href=re.compile(r'/link/summary/[\d\-\.]+'))
                
                for link in career_links:
                    if len(careers) >= max_careers:
                        break
                        
                    career_code = link['href'].split('/')[-1]
                    career_title = link.get_text(strip=True)
                    
                    # Skip if already added or if it's just a code
                    if not any(c['code'] == career_code for c in careers):
                        if career_title and not career_title.replace('.', '').replace('-', '').isdigit():
                            careers.append({
                                'code': career_code,
                                'title': career_title,
                                'url': urljoin(self.base_url, link['href'])
                            })
                
                print(f"Found {len(careers)} careers so far...")
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"Error fetching bright outlook careers: {e}")
        
        # If we still need more careers, try other categories
        if len(careers) < max_careers:
            # Try searching for popular careers directly
            popular_careers = [
                ("15-1252.00", "Software Developers"),
                ("29-1141.00", "Registered Nurses"),
                ("13-2011.00", "Accountants and Auditors"),
                ("15-1254.00", "Web Developers"),
                ("29-1123.00", "Physical Therapists"),
                ("11-1021.00", "General and Operations Managers"),
                ("13-1111.00", "Management Analysts"),
                ("15-1212.00", "Information Security Analysts"),
                ("15-1211.00", "Computer Systems Analysts"),
                ("41-3031.00", "Securities, Commodities, and Financial Services Sales Agents"),
                ("13-2051.00", "Financial Analysts"),
                ("11-2021.00", "Marketing Managers"),
                ("15-1299.08", "Computer Systems Engineers/Architects"),
                ("29-1171.00", "Nurse Practitioners"),
                ("15-1256.00", "Software Quality Assurance Analysts and Testers"),
                ("13-1161.00", "Market Research Analysts and Marketing Specialists"),
                ("11-3021.00", "Computer and Information Systems Managers"),
                ("17-2051.00", "Civil Engineers"),
                ("29-1071.00", "Physician Assistants"),
                ("15-2051.00", "Data Scientists"),
                ("11-9041.00", "Architectural and Engineering Managers"),
                ("17-2141.00", "Mechanical Engineers"),
                ("29-2061.00", "Licensed Practical and Licensed Vocational Nurses"),
                ("31-9092.00", "Medical Assistants"),
                ("17-2071.00", "Electrical Engineers"),
                ("13-1081.00", "Logisticians"),
                ("11-3031.00", "Financial Managers"),
                ("15-1221.00", "Computer and Information Research Scientists"),
                ("17-2112.00", "Industrial Engineers"),
                ("27-1024.00", "Graphic Designers")
            ]
            
            for code, title in popular_careers:
                if len(careers) >= max_careers:
                    break
                    
                if not any(c['code'] == code for c in careers):
                    careers.append({
                        'code': code,
                        'title': title,
                        'url': f"{self.base_url}/link/summary/{code}"
                    })
        
        print(f"Total careers found: {len(careers)}")
        return careers[:max_careers]
    
    def scrape_career_details(self, career: Dict) -> Dict:
        """Scrape detailed information for a specific career"""
        print(f"Scraping details for: {career['title']}")
        
        try:
            response = self.session.get(career['url'])
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            career_data = {
                'code': career['code'],
                'title': career['title'],
                'description': self.extract_description(soup),
                'tasks': self.extract_tasks(soup),
                'skills': self.extract_skills(career['code']),
                'knowledge': self.extract_knowledge(career['code']),
                'abilities': self.extract_abilities(career['code']),
                'education': self.extract_education(soup),
                'salary': self.extract_salary(soup),
                'outlook': self.extract_outlook(soup),
                'work_values': self.extract_work_values(soup),
                'interests': self.extract_interests(soup)
            }
            
            time.sleep(1)  # Rate limiting
            return career_data
            
        except Exception as e:
            print(f"Error scraping {career['title']}: {e}")
            return None
    
    def extract_description(self, soup: BeautifulSoup) -> str:
        """Extract career description"""
        try:
            # Look for the summary section
            summary = soup.find('div', {'class': 'reportrtd'})
            if not summary:
                summary = soup.find('p', string=re.compile(r'.*'))
            
            if summary:
                return summary.get_text(strip=True)[:500]  # First 500 chars
            
            return "Professional in this field responsible for various specialized tasks and duties."
        except:
            return "Career description not available."
    
    def extract_tasks(self, soup: BeautifulSoup) -> List[str]:
        """Extract main tasks/activities"""
        tasks = []
        try:
            # Look for tasks section
            tasks_section = soup.find('div', {'id': 'Tasks'})
            if not tasks_section:
                tasks_section = soup.find('h2', string='Tasks')
                if tasks_section:
                    tasks_section = tasks_section.find_next_sibling('ul')
            
            if tasks_section:
                task_items = tasks_section.find_all('li')[:10]  # Top 10 tasks
                tasks = [item.get_text(strip=True) for item in task_items]
            
            if not tasks:
                # Default tasks
                tasks = [
                    "Perform core professional duties",
                    "Collaborate with team members",
                    "Maintain professional standards",
                    "Document work and progress",
                    "Continuously improve skills"
                ]
        except:
            pass
        
        return tasks
    
    def extract_skills(self, career_code: str) -> List[str]:
        """Extract skills for the career"""
        skills = []
        try:
            skills_url = f"{self.base_url}/link/details/{career_code}/Skills"
            response = self.session.get(skills_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find skill items
                skill_rows = soup.find_all('tr', {'class': 'report2'})[:15]
                
                for row in skill_rows:
                    skill_name = row.find('a')
                    if skill_name:
                        skills.append(skill_name.get_text(strip=True))
            
            if not skills:
                # Default skills based on career title
                skills = self.get_default_skills(career_code)
                
        except Exception as e:
            print(f"Error extracting skills: {e}")
            skills = self.get_default_skills(career_code)
        
        return skills
    
    def extract_knowledge(self, career_code: str) -> List[str]:
        """Extract knowledge areas"""
        knowledge = []
        try:
            knowledge_url = f"{self.base_url}/link/details/{career_code}/Knowledge"
            response = self.session.get(knowledge_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                knowledge_rows = soup.find_all('tr', {'class': 'report2'})[:10]
                
                for row in knowledge_rows:
                    knowledge_item = row.find('a')
                    if knowledge_item:
                        knowledge.append(knowledge_item.get_text(strip=True))
        except:
            pass
        
        return knowledge
    
    def extract_abilities(self, career_code: str) -> List[str]:
        """Extract required abilities"""
        abilities = []
        try:
            abilities_url = f"{self.base_url}/link/details/{career_code}/Abilities"
            response = self.session.get(abilities_url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                ability_rows = soup.find_all('tr', {'class': 'report2'})[:10]
                
                for row in ability_rows:
                    ability_item = row.find('a')
                    if ability_item:
                        abilities.append(ability_item.get_text(strip=True))
        except:
            pass
        
        return abilities
    
    def extract_education(self, soup: BeautifulSoup) -> Dict:
        """Extract education requirements"""
        education = {
            'typical_level': "Bachelor's degree",
            'preferred': "Bachelor's degree or higher",
            'certifications': []
        }
        
        try:
            # Look for education section
            edu_section = soup.find('div', {'id': 'Education'})
            if edu_section:
                edu_text = edu_section.get_text()
                
                if 'doctoral' in edu_text.lower() or 'ph.d' in edu_text.lower():
                    education['typical_level'] = "Doctoral degree"
                elif 'master' in edu_text.lower():
                    education['typical_level'] = "Master's degree"
                elif 'bachelor' in edu_text.lower():
                    education['typical_level'] = "Bachelor's degree"
                elif 'associate' in edu_text.lower():
                    education['typical_level'] = "Associate's degree"
                elif 'high school' in edu_text.lower():
                    education['typical_level'] = "High school diploma"
        except:
            pass
        
        return education
    
    def extract_salary(self, soup: BeautifulSoup) -> Dict:
        """Extract salary information"""
        # Default salaries if extraction fails
        salary = {
            'median': 65000,
            'entry': 45000,
            'experienced': 95000,
            'top': 125000
        }
        
        try:
            # Look for wage/salary information in various formats
            # Try to find wage data in the page
            wage_patterns = [
                r'\$(\d{1,3},?\d{3,})',  # $XX,XXX or $XXX,XXX
                r'(\d{2,3}),(\d{3})\s*(?:per year|annual)',  # XX,XXX per year
                r'median.*?\$(\d{1,3},?\d{3,})',  # median wage
            ]
            
            page_text = soup.get_text()
            
            for pattern in wage_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                if matches:
                    # Extract the first valid number
                    if isinstance(matches[0], tuple):
                        number_str = ''.join(matches[0])
                    else:
                        number_str = matches[0]
                    
                    # Clean and convert to integer
                    number_str = number_str.replace(',', '').replace('$', '')
                    if number_str.isdigit():
                        extracted_salary = int(number_str)
                        
                        # Only use if it's a reasonable salary (not hourly wage)
                        if extracted_salary > 20000:
                            salary['median'] = extracted_salary
                            break
            
            # If we found a median, calculate other levels
            if salary['median'] > 20000:
                salary['entry'] = int(salary['median'] * 0.7)
                salary['experienced'] = int(salary['median'] * 1.5)
                salary['top'] = int(salary['median'] * 2)
            else:
                # Use category-based defaults if extraction failed
                pass
                
        except Exception as e:
            print(f"  Salary extraction error: {e}")
        
        return salary
    
    def extract_outlook(self, soup: BeautifulSoup) -> Dict:
        """Extract job outlook information"""
        outlook = {
            'growth_rate': "8%",
            'growth_description': "As fast as average",
            'openings_per_year': 10000
        }
        
        try:
            outlook_section = soup.find('div', {'id': 'Outlook'})
            if outlook_section:
                outlook_text = outlook_section.get_text()
                
                # Extract growth percentage
                growth_match = re.search(r'(\d+)%', outlook_text)
                if growth_match:
                    outlook['growth_rate'] = f"{growth_match.group(1)}%"
                
                if 'faster than average' in outlook_text.lower():
                    outlook['growth_description'] = "Faster than average"
                elif 'much faster' in outlook_text.lower():
                    outlook['growth_description'] = "Much faster than average"
                elif 'slower' in outlook_text.lower():
                    outlook['growth_description'] = "Slower than average"
        except:
            pass
        
        return outlook
    
    def extract_work_values(self, soup: BeautifulSoup) -> List[str]:
        """Extract work values"""
        return [
            "Achievement",
            "Independence", 
            "Recognition",
            "Relationships",
            "Support",
            "Working Conditions"
        ]
    
    def extract_interests(self, soup: BeautifulSoup) -> List[str]:
        """Extract career interests (Holland codes)"""
        interests = []
        try:
            # Look for interests/Holland codes
            interests_section = soup.find('div', {'id': 'Interests'})
            if interests_section:
                interests_text = interests_section.get_text()
                
                holland_codes = ['Realistic', 'Investigative', 'Artistic', 
                                'Social', 'Enterprising', 'Conventional']
                
                for code in holland_codes:
                    if code in interests_text:
                        interests.append(code)
        except:
            interests = ["Investigative", "Realistic"]
        
        return interests
    
    def get_default_skills(self, career_title: str) -> List[str]:
        """Get default skills based on career type"""
        if 'engineer' in career_title.lower():
            return ["Problem Solving", "Mathematics", "Design", "Analysis", "Project Management"]
        elif 'developer' in career_title.lower() or 'programmer' in career_title.lower():
            return ["Programming", "Problem Solving", "Debugging", "Version Control", "Testing"]
        elif 'analyst' in career_title.lower():
            return ["Data Analysis", "Critical Thinking", "Communication", "Research", "Reporting"]
        elif 'manager' in career_title.lower():
            return ["Leadership", "Communication", "Planning", "Decision Making", "Team Building"]
        else:
            return ["Communication", "Problem Solving", "Time Management", "Teamwork", "Attention to Detail"]
    
    def convert_to_career_format(self, onet_data: Dict) -> Dict:
        """Convert O*NET data to our career format"""
        career_id = onet_data['title'].lower().replace(' ', '_').replace('/', '_').replace(',', '')
        
        # Determine category
        category = self.determine_category(onet_data['title'])
        
        # Create progression levels using O*NET data
        base_salary = onet_data['salary']['median']
        
        career_format = {
            "id": career_id,
            "title": onet_data['title'],
            "category": category,
            "description": onet_data['description'],
            "onet_code": onet_data['code'],
            "growth_rate": onet_data['outlook']['growth_rate'],
            "growth_description": onet_data['outlook']['growth_description'],
            "levels": {
                "Entry": {
                    "years": "0-2",
                    "salary_range": f"${onet_data['salary']['entry']:,} - ${int(onet_data['salary']['entry'] * 1.2):,}",
                    "skills": onet_data['skills'][:5] if onet_data['skills'] else ["Basic Skills"],
                    "knowledge": onet_data['knowledge'][:3] if onet_data['knowledge'] else [],
                    "certifications": [],
                    "projects": [
                        f"Complete foundational {onet_data['title'].lower()} training",
                        "Shadow experienced professionals",
                        "Complete first independent project"
                    ],
                    "milestones": onet_data['tasks'][:3] if onet_data['tasks'] else ["Complete training"],
                    "education": onet_data['education']['typical_level']
                },
                "Junior": {
                    "years": "2-4",
                    "salary_range": f"${int(base_salary * 0.8):,} - ${base_salary:,}",
                    "skills": onet_data['skills'][:8] if onet_data['skills'] else ["Intermediate Skills"],
                    "knowledge": onet_data['knowledge'][:5] if onet_data['knowledge'] else [],
                    "certifications": onet_data['education']['certifications'][:2] if onet_data['education']['certifications'] else [],
                    "projects": [
                        "Lead small projects independently",
                        "Contribute to major initiatives",
                        "Mentor new team members"
                    ],
                    "milestones": onet_data['tasks'][3:6] if len(onet_data['tasks']) > 3 else ["Gain experience"],
                    "education": onet_data['education']['typical_level']
                },
                "Mid-Level": {
                    "years": "4-7",
                    "salary_range": f"${base_salary:,} - ${onet_data['salary']['experienced']:,}",
                    "skills": onet_data['skills'][:12] if onet_data['skills'] else ["Advanced Skills"],
                    "knowledge": onet_data['knowledge'][:7] if onet_data['knowledge'] else [],
                    "abilities": onet_data['abilities'][:5] if onet_data['abilities'] else [],
                    "certifications": onet_data['education']['certifications'] if onet_data['education']['certifications'] else [],
                    "projects": [
                        "Lead cross-functional projects",
                        "Develop new processes or systems",
                        "Train and develop team members"
                    ],
                    "milestones": onet_data['tasks'][6:9] if len(onet_data['tasks']) > 6 else ["Lead projects"],
                    "education": onet_data['education']['preferred']
                },
                "Senior": {
                    "years": "7-10",
                    "salary_range": f"${onet_data['salary']['experienced']:,} - ${onet_data['salary']['top']:,}",
                    "skills": onet_data['skills'] if onet_data['skills'] else ["Expert Skills"],
                    "knowledge": onet_data['knowledge'] if onet_data['knowledge'] else [],
                    "abilities": onet_data['abilities'][:8] if onet_data['abilities'] else [],
                    "certifications": ["Advanced certifications", "Industry recognition"],
                    "projects": [
                        "Lead department initiatives",
                        "Drive strategic improvements",
                        "Represent organization externally"
                    ],
                    "milestones": [
                        "Become recognized expert",
                        "Lead major initiatives",
                        "Influence industry practices"
                    ],
                    "education": f"{onet_data['education']['preferred']} + extensive experience"
                },
                "Expert": {
                    "years": "10+",
                    "salary_range": f"${onet_data['salary']['top']:,}+",
                    "skills": ["Industry Leadership", "Strategic Vision", "Innovation"] + (onet_data['skills'][:3] if onet_data['skills'] else []),
                    "knowledge": ["Industry Expertise", "Strategic Planning"] + (onet_data['knowledge'][:3] if onet_data['knowledge'] else []),
                    "abilities": onet_data['abilities'] if onet_data['abilities'] else [],
                    "certifications": ["Executive programs", "Industry fellow"],
                    "projects": [
                        "Shape organizational strategy",
                        "Industry thought leadership",
                        "Transformational initiatives"
                    ],
                    "milestones": [
                        "Executive leadership role",
                        "Industry recognition",
                        "Leave lasting legacy"
                    ],
                    "education": "Advanced degree + executive education"
                }
            },
            "work_values": onet_data['work_values'],
            "interests": onet_data['interests'],
            "tasks": onet_data['tasks'],
            "related_careers": [],
            "industry_trends": [],
            "remote_friendly": self.is_remote_friendly(onet_data['title']),
            "automation_risk": self.assess_automation_risk(onet_data['title'])
        }
        
        return career_format
    
    def determine_category(self, title: str) -> str:
        """Determine career category from title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['software', 'computer', 'data', 'developer', 'programmer', 'network', 'security', 'database']):
            return "technology"
        elif any(word in title_lower for word in ['nurse', 'doctor', 'physician', 'medical', 'health', 'therapist', 'dental']):
            return "healthcare"
        elif any(word in title_lower for word in ['manager', 'analyst', 'accountant', 'finance', 'marketing', 'sales', 'business']):
            return "business"
        elif any(word in title_lower for word in ['engineer', 'engineering']):
            return "engineering"
        elif any(word in title_lower for word in ['teacher', 'professor', 'instructor', 'education', 'trainer']):
            return "education"
        elif any(word in title_lower for word in ['designer', 'artist', 'writer', 'creative', 'media']):
            return "creative"
        elif any(word in title_lower for word in ['electrician', 'plumber', 'mechanic', 'technician', 'construction']):
            return "trades"
        elif any(word in title_lower for word in ['scientist', 'researcher', 'chemist', 'biologist', 'physicist']):
            return "science"
        else:
            return "general"
    
    def is_remote_friendly(self, title: str) -> bool:
        """Determine if career is remote-friendly"""
        remote_friendly = ['software', 'developer', 'programmer', 'data', 'analyst', 
                          'writer', 'designer', 'marketing', 'consultant']
        return any(word in title.lower() for word in remote_friendly)
    
    def assess_automation_risk(self, title: str) -> str:
        """Assess automation risk for career"""
        high_risk = ['clerk', 'operator', 'assembler', 'teller']
        low_risk = ['manager', 'therapist', 'nurse', 'teacher', 'engineer', 'designer']
        
        title_lower = title.lower()
        if any(word in title_lower for word in high_risk):
            return "High"
        elif any(word in title_lower for word in low_risk):
            return "Low"
        else:
            return "Medium"
    
    def scrape_and_save_all(self, max_careers: int = 50):
        """Main method to scrape and save all careers"""
        print("=" * 60)
        print("Starting O*NET Live Data Scraping")
        print("=" * 60)
        
        # Get list of careers
        careers = self.get_bright_outlook_careers(max_careers)
        
        if not careers:
            print("No careers found to scrape")
            return
        
        print(f"\nFound {len(careers)} careers to process")
        
        successful = 0
        failed = 0
        
        for i, career in enumerate(careers, 1):
            print(f"\n[{i}/{len(careers)}] Processing: {career['title']}")
            
            # Scrape details
            career_data = self.scrape_career_details(career)
            
            if career_data:
                # Convert to our format
                formatted_career = self.convert_to_career_format(career_data)
                
                # Save to file
                filename = self.output_path / f"{formatted_career['id']}.json"
                with open(filename, 'w') as f:
                    json.dump(formatted_career, f, indent=2)
                
                print(f"✓ Saved: {formatted_career['title']}")
                successful += 1
            else:
                print(f"✗ Failed: {career['title']}")
                failed += 1
            
            # Rate limiting
            time.sleep(2)
        
        # Save summary
        summary = {
            "total_scraped": successful,
            "failed": failed,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source": "O*NET Online"
        }
        
        summary_file = self.output_path / "onet_scrape_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print("\n" + "=" * 60)
        print(f"Scraping Complete!")
        print(f"Successfully scraped: {successful} careers")
        print(f"Failed: {failed} careers")
        print("=" * 60)