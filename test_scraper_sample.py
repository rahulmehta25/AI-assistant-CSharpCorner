#!/usr/bin/env python3
"""
Quick test script to verify the comprehensive scraper with just 5 careers
"""

from modules.onet_comprehensive_scraper import ONetComprehensiveScraper
import json

def main():
    print("Testing O*NET Comprehensive Scraper with 5 careers...")
    
    # Create scraper
    scraper = ONetComprehensiveScraper()
    
    # Test just bright outlook terms with first 2 terms
    bright_terms = ["software developer", "data scientist"]
    test_occupations = []
    
    for term in bright_terms:
        search_url = f"{scraper.base_url}/find/quick?s={term.replace(' ', '+')}"
        content = scraper.make_request(search_url)
        
        if content:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/link/summary/' in href and href.startswith('https://www.onetonline.org/'):
                    title = link.get_text(strip=True)
                    soc_code = scraper.extract_soc_from_url(href)
                    
                    if soc_code and not any(occ['soc_code'] == soc_code for occ in test_occupations):
                        test_occupations.append({
                            'title': title,
                            'url': href,
                            'soc_code': soc_code
                        })
                        
                        if len(test_occupations) >= 5:  # Limit to 5 careers
                            break
                
                if len(test_occupations) >= 5:
                    break
            
            if len(test_occupations) >= 5:
                break
    
    print(f"Found {len(test_occupations)} test occupations:")
    for i, occ in enumerate(test_occupations):
        print(f"  {i+1}. {occ['title']} ({occ['soc_code']})")
    
    # Scrape details for each
    scraped_careers = []
    for i, occ in enumerate(test_occupations):
        print(f"\nScraping {i+1}/{len(test_occupations)}: {occ['title']}")
        career_data = scraper.scrape_occupation_details(occ)
        
        if career_data:
            scraped_careers.append(career_data)
            scraper.save_career_file(career_data)
            
            # Show summary
            print(f"  ✅ Success!")
            print(f"     - Description: {career_data.description[:100]}...")
            print(f"     - Median Salary: ${career_data.median_salary:,}" if career_data.median_salary else "     - Salary: Not available")
            print(f"     - Growth Rate: {career_data.growth_rate}" if career_data.growth_rate else "     - Growth: Not available")
            print(f"     - Knowledge Areas: {len(career_data.knowledge)}")
        else:
            print(f"  ❌ Failed to scrape {occ['title']}")
    
    # Save summary
    if scraped_careers:
        scraper.save_all_formats(scraped_careers)
    
    print(f"\n{'='*60}")
    print(f"TEST COMPLETED")
    print(f"Successfully scraped: {len(scraped_careers)}/{len(test_occupations)} careers")
    print(f"Files saved in: {scraper.output_dir}")
    print('='*60)
    
    return scraped_careers

if __name__ == "__main__":
    main()