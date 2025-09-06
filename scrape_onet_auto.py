#!/usr/bin/env python3
"""
Automated script to scrape live career data from O*NET Online
"""

from modules.onet_live_scraper import ONetLiveScraper

def main():
    print("=" * 60)
    print("O*NET Live Data Scraper (Automated)")
    print("=" * 60)
    print("\nFetching real career data from O*NET Online...")
    print("This process may take several minutes due to rate limiting.")
    
    # Set number of careers to scrape
    max_careers = 20
    
    print(f"\nScraping {max_careers} careers from O*NET...")
    
    # Initialize scraper
    scraper = ONetLiveScraper()
    
    try:
        # Run the scraping
        scraper.scrape_and_save_all(max_careers)
        
        print("\n✓ Scraping completed successfully!")
        print("Career files have been updated in data/careers/")
        
    except Exception as e:
        print(f"\n✗ Error during scraping: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()