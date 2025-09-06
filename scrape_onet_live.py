#!/usr/bin/env python3
"""
Script to scrape live career data from O*NET Online
"""

from modules.onet_live_scraper import ONetLiveScraper
import sys

def main():
    print("=" * 60)
    print("O*NET Live Data Scraper")
    print("=" * 60)
    print("\nThis will fetch real career data from O*NET Online.")
    print("The process may take several minutes due to rate limiting.")
    
    # Ask for confirmation
    response = input("\nDo you want to proceed? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Scraping cancelled.")
        return
    
    # Ask for number of careers
    try:
        max_careers = input("\nHow many careers to scrape? (default: 30, max: 100): ")
        if max_careers:
            max_careers = min(int(max_careers), 100)
        else:
            max_careers = 30
    except ValueError:
        max_careers = 30
    
    print(f"\nStarting scrape of {max_careers} careers...")
    
    # Initialize scraper
    scraper = ONetLiveScraper()
    
    try:
        # Run the scraping
        scraper.scrape_and_save_all(max_careers)
        
        print("\n✓ Scraping completed successfully!")
        print("Career files have been updated in data/careers/")
        print("\nYou can now run 'python main.py' to use the updated careers.")
        
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error during scraping: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()