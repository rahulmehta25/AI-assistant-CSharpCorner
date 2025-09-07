#!/usr/bin/env python3
"""
Debug script to understand O*NET website structure
"""

import requests
from bs4 import BeautifulSoup
import json
import time

def analyze_page(url, description):
    print(f"\n{'='*60}")
    print(f"ANALYZING: {description}")
    print(f"URL: {url}")
    print('='*60)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.text):,} characters")
        
        # Save HTML for manual inspection
        filename = f"debug_{description.lower().replace(' ', '_')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"HTML saved to: {filename}")
        
        # Look for different link patterns
        occupation_patterns = [
            ('Summary Links', lambda href: '/link/summary/' in href),
            ('Details Links', lambda href: '/link/details/' in href),
            ('Occupation Links', lambda href: 'occupation' in href.lower()),
            ('SOC Code Links', lambda href: any(char.isdigit() for char in href) and '-' in href),
            ('Career Links', lambda href: 'career' in href.lower()),
            ('Job Links', lambda href: 'job' in href.lower()),
        ]
        
        for pattern_name, pattern_func in occupation_patterns:
            matching_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if pattern_func(href):
                    text = link.get_text(strip=True)
                    matching_links.append((text[:60], href))
            
            print(f"\n{pattern_name}: {len(matching_links)} found")
            for i, (text, href) in enumerate(matching_links[:5]):
                print(f"  {i+1}. '{text}' -> {href}")
        
        # Look for specific content sections
        potential_sections = [
            'main', 'content', 'results', 'occupations', 'careers',
            'bright-outlook', 'list', 'table'
        ]
        
        print(f"\nContent Sections:")
        for section in potential_sections:
            elements = soup.find_all(['div', 'section', 'main'], class_=lambda x: x and section in str(x).lower())
            if elements:
                print(f"  {section}: {len(elements)} elements found")
                
        # Look for any data in script tags (might be JSON)
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and ('occupation' in script.string.lower() or 'career' in script.string.lower()):
                print(f"\nRelevant script content found (first 200 chars):")
                print(script.string[:200])
                break
        
        return soup
        
    except Exception as e:
        print(f"Error analyzing {url}: {e}")
        return None

def main():
    # Test different O*NET URLs
    test_urls = [
        ("https://www.onetonline.org/find/bright", "Bright Outlook"),
        ("https://www.onetonline.org/find/stem", "STEM Careers"),
        ("https://www.onetonline.org/find/green", "Green Economy"),
        ("https://www.onetonline.org/find/browse", "Browse All"),
        ("https://www.onetonline.org/", "Main Page"),
    ]
    
    for url, description in test_urls:
        analyze_page(url, description)
        time.sleep(2)  # Be respectful
    
    print(f"\n{'='*60}")
    print("ANALYSIS COMPLETE")
    print("Check the generated HTML files to manually inspect the page structure")
    print('='*60)

if __name__ == "__main__":
    main()