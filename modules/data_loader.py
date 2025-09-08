"""
Data Loader for O*NET Career Data
Loads and serves actual scraped O*NET data to the API
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path

class DataLoader:
    def __init__(self):
        # Get absolute path relative to the script location
        script_dir = Path(__file__).parent.parent
        self.data_dir = script_dir / "data" / "comprehensive_careers"
        self.careers = {}
        self.load_all_careers()
    
    def load_all_careers(self):
        """Load all career data from JSON files"""
        if not self.data_dir.exists():
            print(f"Warning: Data directory {self.data_dir} does not exist")
            return
        
        # First try to load the consolidated file
        consolidated_files = list(self.data_dir.glob("all_careers_*.json"))
        
        if consolidated_files:
            # Use the most recent consolidated file
            latest_file = max(consolidated_files, key=lambda f: f.stat().st_mtime)
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    careers_list = json.load(f)
                    for career in careers_list:
                        if 'soc_code' in career:
                            self.careers[career['soc_code']] = career
                print(f"Loaded {len(self.careers)} careers from {latest_file.name}")
            except Exception as e:
                print(f"Error loading consolidated file {latest_file}: {e}")
        
        # Also load individual career files
        for json_file in self.data_dir.glob("*.json"):
            if not json_file.name.startswith("all_careers") and not json_file.name.startswith("scraping"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        career = json.load(f)
                        if 'soc_code' in career:
                            self.careers[career['soc_code']] = career
                except Exception as e:
                    print(f"Error loading {json_file}: {e}")
        
        print(f"Total careers loaded: {len(self.careers)}")
        if len(self.careers) == 0:
            print(f"Warning: No careers loaded from {self.data_dir}")
    
    def get_all_careers(self) -> List[Dict]:
        """Get all careers as a list"""
        return list(self.careers.values())
    
    def get_career(self, soc_code: str) -> Optional[Dict]:
        """Get a specific career by SOC code"""
        return self.careers.get(soc_code)
    
    def search_careers(self, query: str) -> List[Dict]:
        """Search careers by title or description"""
        query_lower = query.lower()
        results = []
        
        for career in self.careers.values():
            if (query_lower in career.get('title', '').lower() or 
                query_lower in career.get('description', '').lower() or
                query_lower in career.get('cluster', '').lower()):
                results.append(career)
        
        return results
    
    def get_careers_by_cluster(self, cluster: str) -> List[Dict]:
        """Get all careers in a specific cluster"""
        return [c for c in self.careers.values() if c.get('cluster', '').lower() == cluster.lower()]
    
    def get_bright_outlook_careers(self) -> List[Dict]:
        """Get careers with bright outlook"""
        return [c for c in self.careers.values() if 'bright' in c.get('employment_outlook', '').lower()]
    
    def get_high_growth_careers(self) -> List[Dict]:
        """Get careers with high growth rate"""
        careers_with_growth = []
        for career in self.careers.values():
            growth = career.get('growth_rate', '0%')
            if growth and growth != '0%':
                try:
                    growth_num = int(growth.replace('%', ''))
                    if growth_num > 20:
                        careers_with_growth.append(career)
                except:
                    pass
        return careers_with_growth

# Global instance
data_loader = DataLoader()