#!/usr/bin/env python3
"""
Script to generate comprehensive career database from O*NET data
"""

from modules.onet_scraper import ONetScraper
import json
from pathlib import Path

def main():
    print("=" * 60)
    print("Career Database Generator")
    print("=" * 60)
    
    # Initialize scraper
    scraper = ONetScraper()
    
    # Generate all careers
    print("\nGenerating career files...")
    careers = scraper.generate_all_careers()
    
    # Display summary
    print("\n" + "=" * 60)
    print("Generation Complete!")
    print("=" * 60)
    
    # Count careers by category
    categories = {}
    for career in careers:
        cat = career['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nCareers by Category:")
    for cat, count in sorted(categories.items()):
        print(f"  - {cat.title()}: {count} careers")
    
    print(f"\nTotal careers generated: {len(careers)}")
    print(f"Career files saved to: data/careers/")
    
    # Create a quick stats file
    stats_file = Path("data/careers/stats.json")
    stats = {
        "total_careers": len(careers),
        "categories": categories,
        "generation_date": str(Path("data/careers").stat().st_mtime)
    }
    
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"\nYou can now run 'python main.py' to use the application with all careers!")

if __name__ == "__main__":
    main()