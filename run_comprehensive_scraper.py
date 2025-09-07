#!/usr/bin/env python3
"""
Runner script for the O*NET Comprehensive Career Scraper

This script provides a user-friendly interface to run the comprehensive
O*NET scraper with various options and configurations.
"""

import sys
import argparse
from pathlib import Path
from modules.onet_comprehensive_scraper import ONetComprehensiveScraper
import json

def main():
    parser = argparse.ArgumentParser(
        description="O*NET Comprehensive Career Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_comprehensive_scraper.py --max-careers 100
  python run_comprehensive_scraper.py --max-careers 500 --output-dir custom_output
  python run_comprehensive_scraper.py --test-mode
        """
    )
    
    parser.add_argument(
        '--max-careers',
        type=int,
        default=300,
        help='Maximum number of careers to scrape (default: 300)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/comprehensive_careers',
        help='Output directory for scraped data (default: data/comprehensive_careers)'
    )
    
    parser.add_argument(
        '--cache-dir',
        type=str,
        default='data/cache',
        help='Cache directory for storing temporary files (default: data/cache)'
    )
    
    parser.add_argument(
        '--test-mode',
        action='store_true',
        help='Run in test mode with only 10 careers'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Adjust parameters for test mode
    if args.test_mode:
        args.max_careers = 10
        print("Running in TEST MODE - will scrape only 10 careers")
    
    print("O*NET Comprehensive Career Scraper")
    print("=" * 50)
    print(f"Max careers to scrape: {args.max_careers}")
    print(f"Output directory: {args.output_dir}")
    print(f"Cache directory: {args.cache_dir}")
    print("=" * 50)
    
    # Create scraper instance
    scraper = ONetComprehensiveScraper(
        output_dir=args.output_dir,
        cache_dir=args.cache_dir
    )
    
    # Confirm before starting
    if not args.test_mode:
        response = input("\nThis will scrape career data from O*NET. Continue? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Scraping cancelled.")
            return
    
    print("\nStarting comprehensive scrape...")
    print("This may take 10-30 minutes depending on the number of careers.")
    print("Progress updates will be shown every 10 careers.\n")
    
    # Run the scraper
    try:
        result = scraper.run_comprehensive_scrape(max_careers=args.max_careers)
        
        # Display results
        print("\n" + "="*60)
        print("SCRAPING RESULTS")
        print("="*60)
        
        if result['status'] == 'success':
            print(f"✅ SUCCESS: Scraped {result['total_careers_scraped']} careers")
            print(f"⏱️  Duration: {result['duration_minutes']} minutes")
            print(f"📁 Output: {result['output_directory']}")
            print(f"💾 Cache: {result['cache_directory']}")
            
            print("\n📊 CAREERS BY CLUSTER:")
            for cluster, count in sorted(result['careers_per_cluster'].items()):
                print(f"  {cluster}: {count} careers")
            
            # Show next steps
            print("\n🎯 NEXT STEPS:")
            print("1. Check the output directory for individual career JSON files")
            print("2. Review the summary files for aggregated data") 
            print("3. Import the CSV file into your analysis tools")
            print("4. Use the JSON data in your career assistant application")
            
        else:
            print(f"❌ ERROR: {result['message']}")
            print(f"⏱️  Duration: {result['duration_minutes']} minutes")
            
            print("\n🔧 TROUBLESHOOTING:")
            print("1. Check your internet connection")
            print("2. Verify O*NET website is accessible")
            print("3. Try reducing --max-careers for a smaller test")
            print("4. Check logs for specific error details")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
        print("Partial results may be saved in the output directory")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check the logs and try again")
        sys.exit(1)

if __name__ == "__main__":
    main()