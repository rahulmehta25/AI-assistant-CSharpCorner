# O*NET Comprehensive Career Scraper

## Overview

This enhanced O*NET scraper systematically fetches comprehensive career data from all career categories available on O*NET OnLine. Unlike basic scrapers, this tool extracts detailed information for hundreds of careers including SOC codes, descriptions, skills, knowledge areas, abilities, work activities, education requirements, salary data, and job outlook.

## Features

- **Comprehensive Data Extraction**: Fetches 15+ data points per career
- **Smart Search Strategy**: Uses targeted keyword searches across career clusters
- **Rate Limiting & Caching**: Respectful scraping with built-in delays and caching
- **Multiple Output Formats**: JSON, CSV, and individual career files
- **Error Handling**: Robust retry logic and error recovery
- **Progress Tracking**: Real-time logging and progress updates
- **Scalable**: Can scrape 200-300+ careers systematically

## Quick Start

### 1. Test Run (5 careers)
```bash
python test_scraper_sample.py
```

### 2. Small Batch (10 careers)
```bash
python run_comprehensive_scraper.py --test-mode
```

### 3. Full Scrape (300 careers)
```bash
python run_comprehensive_scraper.py --max-careers 300
```

### 4. Custom Configuration
```bash
python run_comprehensive_scraper.py --max-careers 100 --output-dir custom_output --verbose
```

## What Gets Scraped

For each career, the scraper extracts:

### Basic Information
- **SOC Code**: Standard Occupational Classification code
- **Title**: Official occupation title
- **Cluster**: Career cluster classification
- **Description**: Detailed job description

### Skills & Requirements
- **Tasks**: List of work tasks and responsibilities
- **Skills**: Required technical and soft skills
- **Knowledge**: Knowledge areas needed
- **Abilities**: Physical and mental abilities required
- **Work Activities**: Day-to-day work activities

### Education & Experience
- **Education Level**: Required education (Bachelor's, Master's, etc.)
- **Experience Level**: Years of experience needed
- **Job Training**: Training and certification requirements

### Economic Data
- **Median Salary**: Annual median salary
- **Salary Range**: Salary range if available
- **Employment Outlook**: Job growth outlook
- **Growth Rate**: Projected growth percentage

### Work Environment
- **Related Occupations**: Similar career paths
- **Work Environment**: Working conditions and environment
- **Interests**: Holland Code interest areas
- **Work Styles**: Personality and work style preferences
- **Technology Skills**: Software and technology requirements

## Output Files

### Individual Career Files
- Location: `data/comprehensive_careers/[SOC-CODE].json`
- Format: JSON with complete career data
- Example: `15-1252.00.json` for Software Developers

### Aggregated Data
- `all_careers_[timestamp].json`: All careers in one JSON file
- `all_careers_[timestamp].csv`: CSV format for analysis
- `scraping_summary_[timestamp].json`: Summary statistics

### Cache Files
- Location: `data/cache/`
- Purpose: Stores web pages to avoid re-downloading
- Retention: 7 days

## Sample Output

```json
{
  "soc_code": "15-1252.00",
  "title": "Software Developers",
  "cluster": "Computer and Mathematical",
  "description": "Research, design, and develop computer and network software...",
  "tasks": ["Design software systems", "Write and test code", ...],
  "skills": ["Programming", "Problem Solving", "Critical Thinking", ...],
  "knowledge": ["Computers and Electronics", "Mathematics", ...],
  "median_salary": 133080,
  "growth_rate": "95%",
  "employment_outlook": "Bright Outlook",
  "education_level": "Bachelor's degree",
  "related_occupations": ["Computer Programmers", "Web Developers", ...]
}
```

## Career Categories Covered

The scraper targets these major career areas:

### Technology
- Software Developers, Data Scientists, System Administrators
- Web Developers, Database Administrators, Security Analysts

### Healthcare
- Nurses, Doctors, Therapists, Medical Technicians
- Healthcare Administrators, Medical Assistants

### Business & Finance
- Managers, Analysts, Administrators, Coordinators
- Accountants, Financial Advisors, Consultants

### Education & Training
- Teachers, Instructors, Counselors, Librarians
- Training Specialists, Education Administrators

### Engineering & Science
- Engineers (all types), Scientists, Researchers
- Architects, Technologists, Specialists

### Creative & Design
- Designers, Artists, Writers, Photographers
- Editors, Creative Directors

### Trades & Technical
- Electricians, Plumbers, Mechanics, Carpenters
- Technicians, Installers, Repair Workers

### Legal & Public Service
- Lawyers, Paralegals, Investigators
- Government Workers, Public Administrators

## Configuration

### Scraper Settings (`config/scraper_config.json`)
```json
{
  "rate_limiting": {
    "min_delay_seconds": 1.0,
    "max_delay_seconds": 3.0,
    "max_retries": 3
  },
  "cache_settings": {
    "enabled": true,
    "cache_duration_days": 7
  }
}
```

### Command Line Options
```bash
--max-careers N        # Maximum careers to scrape (default: 300)
--output-dir DIR       # Output directory (default: data/comprehensive_careers)
--cache-dir DIR        # Cache directory (default: data/cache)
--test-mode           # Scrape only 10 careers for testing
--verbose             # Enable verbose logging
```

## Performance & Timing

### Expected Timing
- **5 careers**: ~1 minute
- **50 careers**: ~10 minutes  
- **300 careers**: ~45-60 minutes

### Rate Limiting
- 1-3 second delay between requests
- Automatic retry on failures
- Respectful of O*NET servers

### Caching Benefits
- Subsequent runs much faster
- Cache valid for 7 days
- Reduces server load

## Advanced Usage

### Custom Career Lists
```python
from modules.onet_comprehensive_scraper import ONetComprehensiveScraper

scraper = ONetComprehensiveScraper()
careers = scraper.get_stem_occupations()  # Get only STEM careers
```

### Data Analysis
```python
import pandas as pd

# Load scraped data
df = pd.read_csv('data/comprehensive_careers/all_careers_20250906_162833.csv')

# Analyze salary by cluster
salary_by_cluster = df.groupby('cluster')['median_salary'].mean()
print(salary_by_cluster)
```

### Integration with Career Assistant
```python
from modules.onet_comprehensive_scraper import ONetComprehensiveScraper
import json

# Load comprehensive career data
with open('data/comprehensive_careers/all_careers_latest.json', 'r') as f:
    careers = json.load(f)

# Use in your career recommendation system
for career in careers:
    if career['median_salary'] > 100000:
        print(f"High-paying career: {career['title']}")
```

## Troubleshooting

### Common Issues

1. **No careers found**
   - Check internet connection
   - Verify O*NET website accessibility
   - Try reducing --max-careers

2. **Timeout errors**
   - Increase delays in scraper_config.json
   - Run smaller batches
   - Check for network issues

3. **Missing data fields**
   - Some careers may have incomplete data on O*NET
   - This is normal and handled gracefully

4. **Cache issues**
   - Clear cache directory if needed: `rm -rf data/cache/`
   - Disable caching temporarily for testing

### Debug Mode
```bash
# Enable detailed logging
python run_comprehensive_scraper.py --verbose --test-mode

# Debug page structure
python debug_onet_structure.py
```

## File Structure
```
project/
├── modules/
│   └── onet_comprehensive_scraper.py    # Main scraper class
├── config/
│   └── scraper_config.json              # Configuration settings  
├── data/
│   ├── comprehensive_careers/           # Output directory
│   │   ├── 15-1252.00.json             # Individual career files
│   │   ├── all_careers_timestamp.json   # Complete dataset
│   │   └── all_careers_timestamp.csv    # CSV format
│   └── cache/                           # Cached web pages
├── run_comprehensive_scraper.py         # Command-line interface
├── test_scraper_sample.py              # Quick test script
└── debug_onet_structure.py             # Debug utilities
```

## Contributing

To add new career categories or improve extraction:

1. Add search terms to cluster_terms in `get_occupations_from_clusters()`
2. Enhance extraction methods in the scraper class
3. Update configuration files as needed
4. Test with small batches first

## License & Ethics

- Respects O*NET's robots.txt and terms of service
- Rate-limited to avoid overwhelming servers  
- Data used for educational and research purposes
- Consider O*NET's usage policies for commercial use

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review log files for error details
3. Test with smaller batches first
4. Verify network connectivity and O*NET accessibility

---

**Happy Career Data Scraping!** 🚀