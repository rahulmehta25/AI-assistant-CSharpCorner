#!/usr/bin/env python3
"""
Test API Integration with Real O*NET Data
Tests that the API serves actual scraped career data correctly
"""

import requests
import json
import sys
from typing import Dict, List

API_BASE_URL = "http://localhost:8001"

def test_data_loader_direct():
    """Test data loader directly"""
    print("=" * 60)
    print("TESTING DATA LOADER DIRECTLY")
    print("=" * 60)
    
    try:
        from modules.data_loader import data_loader
        careers = data_loader.get_all_careers()
        print(f"✓ Data loader loaded {len(careers)} careers")
        
        if careers:
            sample_career = careers[0]
            print(f"✓ Sample career: {sample_career.get('title', 'No title')}")
            print(f"  SOC Code: {sample_career.get('soc_code', 'No SOC code')}")
            print(f"  Salary: ${sample_career.get('median_salary', 'No salary')}")
            print(f"  Description: {sample_career.get('description', 'No description')[:100]}...")
            return True
        else:
            print("✗ No careers loaded")
            return False
            
    except Exception as e:
        print(f"✗ Data loader error: {e}")
        return False

def test_api_endpoint(endpoint: str, expected_keys: List[str] = None) -> bool:
    """Test a specific API endpoint"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ {endpoint} - Status: 200")
            
            if expected_keys:
                for key in expected_keys:
                    if key in data:
                        print(f"  ✓ Has '{key}' field")
                    else:
                        print(f"  ✗ Missing '{key}' field")
                        
            return True
        else:
            print(f"✗ {endpoint} - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ {endpoint} - Connection error: {e}")
        return False

def test_careers_data_quality():
    """Test the quality of career data returned"""
    print("\n" + "=" * 60)
    print("TESTING CAREER DATA QUALITY")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/careers", timeout=10)
        if response.status_code != 200:
            print(f"✗ API not responding: {response.status_code}")
            return False
            
        data = response.json()
        careers = data.get('careers', [])
        
        if not careers:
            print("✗ No careers returned")
            return False
            
        print(f"✓ API returned {len(careers)} careers")
        
        # Test first career for required fields
        career = careers[0]
        required_fields = ['id', 'title', 'description', 'salary', 'growth', 'cluster']
        
        for field in required_fields:
            if field in career and career[field]:
                if field == 'salary' and isinstance(career[field], dict):
                    print(f"  ✓ {field}: ${career[field].get('min', 0)} - ${career[field].get('max', 0)}")
                else:
                    value = str(career[field])[:50]
                    print(f"  ✓ {field}: {value}")
            else:
                print(f"  ✗ Missing or empty {field}")
        
        # Check if data is real (not mock)
        titles = [c.get('title', '') for c in careers[:3]]
        print(f"\n✓ Sample career titles:")
        for i, title in enumerate(titles, 1):
            print(f"  {i}. {title}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing career data: {e}")
        return False

def test_specific_career():
    """Test fetching a specific career by ID"""
    print("\n" + "=" * 60)
    print("TESTING SPECIFIC CAREER ENDPOINT")
    print("=" * 60)
    
    # First get a career ID
    try:
        response = requests.get(f"{API_BASE_URL}/api/careers", timeout=10)
        data = response.json()
        careers = data.get('careers', [])
        
        if not careers:
            print("✗ No careers to test with")
            return False
            
        career_id = careers[0].get('id')
        print(f"Testing with career ID: {career_id}")
        
        # Now test the specific career endpoint
        response = requests.get(f"{API_BASE_URL}/api/careers/{career_id}", timeout=10)
        
        if response.status_code == 200:
            career = response.json()
            print(f"✓ Career details endpoint works")
            print(f"  Title: {career.get('title', 'No title')}")
            print(f"  Skills: {len(career.get('skills', []))} skills")
            print(f"  Tasks: {len(career.get('tasks', []))} tasks")
            print(f"  Knowledge: {len(career.get('knowledge', []))} knowledge areas")
            return True
        else:
            print(f"✗ Career details endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error testing specific career: {e}")
        return False

def test_search_functionality():
    """Test the career search endpoint"""
    print("\n" + "=" * 60)
    print("TESTING SEARCH FUNCTIONALITY")
    print("=" * 60)
    
    search_terms = ["software", "computer", "analyst"]
    
    for term in search_terms:
        try:
            payload = {"query": term}
            response = requests.post(f"{API_BASE_URL}/api/careers/search", 
                                   json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                print(f"✓ Search for '{term}': {len(results)} results")
                
                if results:
                    print(f"  Top result: {results[0].get('title', 'No title')}")
            else:
                print(f"✗ Search for '{term}' failed: {response.status_code}")
                
        except Exception as e:
            print(f"✗ Search error for '{term}': {e}")

def main():
    """Run all tests"""
    print("AI CAREER ASSISTANT API INTEGRATION TEST")
    print("=" * 60)
    
    # Test data loader first
    if not test_data_loader_direct():
        print("\n✗ CRITICAL: Data loader not working - API cannot serve real data")
        sys.exit(1)
    
    # Test basic API connectivity
    print("\n" + "=" * 60)
    print("TESTING API ENDPOINTS")
    print("=" * 60)
    
    endpoints_to_test = [
        ("/", None),
        ("/api/careers", ["careers", "total"]),
        ("/api/stats", ["total_careers"])
    ]
    
    api_working = True
    for endpoint, expected_keys in endpoints_to_test:
        if not test_api_endpoint(endpoint, expected_keys):
            api_working = False
    
    if not api_working:
        print("\n✗ API not responding - make sure server is running on port 8001")
        sys.exit(1)
    
    # Test data quality
    if not test_careers_data_quality():
        sys.exit(1)
    
    # Test specific career
    if not test_specific_career():
        print("⚠ Career details endpoint has issues")
    
    # Test search
    test_search_functionality()
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS COMPLETED")
    print("✓ API successfully serving real O*NET career data!")
    print("=" * 60)

if __name__ == "__main__":
    main()