#!/usr/bin/env python3
"""
Comprehensive Validation Script for Student Pathways Integration

This script validates:
1. All grade levels (HS Freshman to College Senior)
2. Multiple career fields
3. O*NET code integration with real data
4. API endpoint functionality
5. Data consistency and completeness
"""

import sys
import json
import requests
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Test configuration
API_BASE_URL = "http://localhost:8001"
TIMEOUT = 30

@dataclass
class ValidationResult:
    test_name: str
    status: str  # PASS, FAIL, ERROR
    details: Dict[str, Any]
    error_message: Optional[str] = None

class StudentPathwayValidator:
    """Comprehensive validator for student pathway system"""
    
    def __init__(self):
        self.results: List[ValidationResult] = []
        self.passed = 0
        self.failed = 0
        self.errors = 0
    
    def run_all_validations(self) -> bool:
        """Run all validation tests"""
        print("🚀 STUDENT PATHWAY SYSTEM - COMPREHENSIVE VALIDATION")
        print("=" * 70)
        
        # 1. Test all grade levels
        self.validate_all_grade_levels()
        
        # 2. Test different career fields
        self.validate_career_fields()
        
        # 3. Test with real O*NET codes
        self.validate_onet_integration()
        
        # 4. Test API consistency
        self.validate_api_consistency()
        
        # 5. Test edge cases
        self.validate_edge_cases()
        
        # Generate report
        return self.generate_report()
    
    def validate_all_grade_levels(self):
        """Test all possible grade levels"""
        print("\\n📚 TESTING ALL GRADE LEVELS")
        print("-" * 40)
        
        grade_levels = [
            # High School
            ("freshman_hs", "High School Freshman"),
            ("sophomore_hs", "High School Sophomore"),
            ("junior_hs", "High School Junior"),
            ("senior_hs", "High School Senior"),
            # College
            ("freshman_college", "College Freshman"),
            ("sophomore_college", "College Sophomore"),
            ("junior_college", "College Junior"),
            ("senior_college", "College Senior")
        ]
        
        for level_code, level_name in grade_levels:
            self._test_grade_level(level_code, level_name)
    
    def _test_grade_level(self, level_code: str, level_name: str):
        """Test a specific grade level"""
        payload = {
            "student_level": level_code,
            "interests": ["technology", "problem-solving"],
            "current_skills": ["mathematics", "communication"],
            "career_goals": ["computer science"],
            "gpa": 3.5
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/student-pathways",
                json=payload,
                timeout=TIMEOUT
            )
            
            if response.status_code != 200:
                self._record_failure(
                    f"Grade Level - {level_name}",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return
            
            data = response.json()
            
            # Validate response structure
            validations = {
                "has_student_level": "student_level" in data,
                "has_milestones": "milestones" in data and len(data["milestones"]) > 0,
                "has_courses": "courses" in data,
                "has_activities": "activities" in data and len(data["activities"]) > 0,
                "has_skills": "skills_to_develop" in data and len(data["skills_to_develop"]) > 0,
                "has_timeline": "timeline" in data,
                "has_summary": "summary" in data,
                "correct_level": data.get("student_level") == level_code
            }
            
            # Grade-specific validations
            if "hs" in level_code:
                validations["hs_has_college_prep"] = any(
                    "college" in m["title"].lower() or "application" in m["category"].lower()
                    for m in data.get("milestones", [])
                )
            else:
                validations["college_has_career_prep"] = any(
                    "internship" in m["title"].lower() or "job" in m["title"].lower()
                    for m in data.get("milestones", [])
                )
            
            if all(validations.values()):
                self._record_success(
                    f"Grade Level - {level_name}",
                    {
                        "milestones_count": len(data.get("milestones", [])),
                        "courses_count": len(data.get("courses", [])),
                        "activities_count": len(data.get("activities", [])),
                        "skills_count": len(data.get("skills_to_develop", [])),
                        "focus_areas": data.get("summary", {}).get("focus_areas", [])
                    }
                )
            else:
                failed_checks = [k for k, v in validations.items() if not v]
                self._record_failure(
                    f"Grade Level - {level_name}",
                    f"Failed validations: {', '.join(failed_checks)}"
                )
                
        except Exception as e:
            self._record_error(f"Grade Level - {level_name}", str(e))
    
    def validate_career_fields(self):
        """Test different career fields"""
        print("\\n💼 TESTING DIFFERENT CAREER FIELDS")
        print("-" * 40)
        
        career_tests = [
            {
                "field": "computer science",
                "interests": ["programming", "algorithms", "technology"],
                "skills": ["python", "mathematics"],
                "expected_activities": ["Robotics Club", "Hackathons", "ACM"]
            },
            {
                "field": "business",
                "interests": ["leadership", "finance", "entrepreneurship"],
                "skills": ["communication", "analysis"],
                "expected_activities": ["DECA", "Business Club", "Case Competition"]
            },
            {
                "field": "engineering",
                "interests": ["design", "problem-solving", "mathematics"],
                "skills": ["physics", "calculus"],
                "expected_activities": ["Science Olympiad", "Robotics Club"]
            },
            {
                "field": "medicine",
                "interests": ["biology", "helping others", "research"],
                "skills": ["chemistry", "biology"],
                "expected_activities": ["Science Olympiad", "Volunteer Work"]
            },
            {
                "field": "art",
                "interests": ["creativity", "design", "visual arts"],
                "skills": ["drawing", "creativity"],
                "expected_activities": ["Art Club", "Theater"]
            }
        ]
        
        for test in career_tests:
            self._test_career_field(test)
    
    def _test_career_field(self, test_data: Dict):
        """Test a specific career field"""
        payload = {
            "student_level": "junior_hs",
            "interests": test_data["interests"],
            "current_skills": test_data["skills"],
            "career_goals": [test_data["field"]],
            "gpa": 3.6
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/student-pathways",
                json=payload,
                timeout=TIMEOUT
            )
            
            if response.status_code != 200:
                self._record_failure(
                    f"Career Field - {test_data['field'].title()}",
                    f"HTTP {response.status_code}: {response.text}"
                )
                return
            
            data = response.json()
            
            # Check if pathway matches career field
            career_match = data.get("career_field", "").lower() == test_data["field"].lower()
            
            # Check for relevant activities
            activity_names = [a["name"] for a in data.get("activities", [])]
            has_relevant_activities = any(
                expected_activity.lower() in activity_name.lower()
                for expected_activity in test_data["expected_activities"]
                for activity_name in activity_names
            )
            
            if career_match and len(data.get("milestones", [])) > 0:
                self._record_success(
                    f"Career Field - {test_data['field'].title()}",
                    {
                        "career_field": data.get("career_field"),
                        "milestones": len(data.get("milestones", [])),
                        "activities": activity_names,
                        "has_relevant_activities": has_relevant_activities
                    }
                )
            else:
                self._record_failure(
                    f"Career Field - {test_data['field'].title()}",
                    f"Career match: {career_match}, Milestones: {len(data.get('milestones', []))}"
                )
                
        except Exception as e:
            self._record_error(f"Career Field - {test_data['field'].title()}", str(e))
    
    def validate_onet_integration(self):
        """Test O*NET code integration"""
        print("\\n🔗 TESTING O*NET INTEGRATION")
        print("-" * 40)
        
        # First, get available careers from the API
        try:
            response = requests.get(f"{API_BASE_URL}/api/careers", timeout=TIMEOUT)
            if response.status_code == 200:
                careers = response.json()
                print(f"✅ Found {len(careers)} careers in database")
                
                # Test with a few real careers
                test_careers = careers[:5]  # Test first 5 careers
                
                for career in test_careers:
                    self._test_onet_career(career)
                    
            else:
                self._record_failure(
                    "O*NET Integration - API Access",
                    f"Could not fetch careers: HTTP {response.status_code}"
                )
                
        except Exception as e:
            self._record_error("O*NET Integration - Setup", str(e))
    
    def _test_onet_career(self, career: Dict):
        """Test pathway generation with a specific O*NET career"""
        soc_code = career.get("soc_code") or career.get("onet_code")
        title = career.get("title", "Unknown Career")
        
        if not soc_code:
            return  # Skip careers without O*NET codes
        
        payload = {
            "student_level": "sophomore_college",
            "interests": ["technology", "problem-solving"],
            "current_skills": ["analysis", "communication"],
            "career_goals": [title.lower()],
            "gpa": 3.4
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/student-pathways",
                json=payload,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                self._record_success(
                    f"O*NET Career - {title[:30]}...",
                    {
                        "soc_code": soc_code,
                        "generated_pathway": True,
                        "milestones": len(data.get("milestones", [])),
                        "activities": len(data.get("activities", []))
                    }
                )
            else:
                self._record_failure(
                    f"O*NET Career - {title[:30]}...",
                    f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            self._record_error(f"O*NET Career - {title[:30]}...", str(e))
    
    def validate_api_consistency(self):
        """Test API consistency and performance"""
        print("\\n⚡ TESTING API CONSISTENCY")
        print("-" * 40)
        
        # Test same request multiple times
        payload = {
            "student_level": "junior_hs",
            "interests": ["mathematics", "programming"],
            "current_skills": ["algebra", "python"],
            "career_goals": ["computer science"],
            "gpa": 3.7
        }
        
        responses = []
        response_times = []
        
        for i in range(3):
            try:
                start_time = time.time()
                response = requests.post(
                    f"{API_BASE_URL}/api/student-pathways",
                    json=payload,
                    timeout=TIMEOUT
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    responses.append(response.json())
                    response_times.append(response_time)
                    
            except Exception as e:
                self._record_error(f"Consistency Test - Request {i+1}", str(e))
                return
        
        if len(responses) >= 2:
            # Check consistency
            first_response = responses[0]
            consistent = all(
                r.get("student_level") == first_response.get("student_level") and
                r.get("career_field") == first_response.get("career_field") and
                len(r.get("milestones", [])) == len(first_response.get("milestones", []))
                for r in responses[1:]
            )
            
            avg_response_time = sum(response_times) / len(response_times)
            
            if consistent and avg_response_time < 5.0:  # 5 second threshold
                self._record_success(
                    "API Consistency",
                    {
                        "consistent_responses": True,
                        "average_response_time": f"{avg_response_time:.2f}s",
                        "requests_tested": len(responses)
                    }
                )
            else:
                self._record_failure(
                    "API Consistency",
                    f"Consistent: {consistent}, Avg time: {avg_response_time:.2f}s"
                )
    
    def validate_edge_cases(self):
        """Test edge cases and error handling"""
        print("\\n🔍 TESTING EDGE CASES")
        print("-" * 40)
        
        edge_cases = [
            {
                "name": "Empty Interests & Skills",
                "payload": {
                    "student_level": "sophomore_hs",
                    "interests": [],
                    "current_skills": [],
                    "career_goals": ["computer science"]
                },
                "should_succeed": True
            },
            {
                "name": "Very High GPA",
                "payload": {
                    "student_level": "senior_hs",
                    "interests": ["academics"],
                    "current_skills": ["study skills"],
                    "career_goals": ["medicine"],
                    "gpa": 4.0,
                    "standardized_scores": {"SAT": 1600, "ACT": 36}
                },
                "should_succeed": True
            },
            {
                "name": "Unknown Career Field",
                "payload": {
                    "student_level": "freshman_college",
                    "interests": ["unusual interests"],
                    "current_skills": ["rare skills"],
                    "career_goals": ["underwater basket weaving"]
                },
                "should_succeed": True  # Should default gracefully
            }
        ]
        
        for case in edge_cases:
            self._test_edge_case(case)
    
    def _test_edge_case(self, case: Dict):
        """Test a specific edge case"""
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/student-pathways",
                json=case["payload"],
                timeout=TIMEOUT
            )
            
            if case["should_succeed"] and response.status_code == 200:
                data = response.json()
                has_basic_structure = (
                    "student_level" in data and
                    "milestones" in data and
                    "activities" in data
                )
                
                if has_basic_structure:
                    self._record_success(
                        f"Edge Case - {case['name']}",
                        {"response_valid": True, "milestones": len(data.get("milestones", []))}
                    )
                else:
                    self._record_failure(
                        f"Edge Case - {case['name']}",
                        "Missing basic response structure"
                    )
            else:
                self._record_failure(
                    f"Edge Case - {case['name']}",
                    f"HTTP {response.status_code}: Expected success"
                )
                
        except Exception as e:
            self._record_error(f"Edge Case - {case['name']}", str(e))
    
    def _record_success(self, test_name: str, details: Dict[str, Any]):
        """Record a successful test"""
        self.results.append(ValidationResult(
            test_name=test_name,
            status="PASS",
            details=details
        ))
        self.passed += 1
        print(f"✅ {test_name}")
    
    def _record_failure(self, test_name: str, error_message: str):
        """Record a failed test"""
        self.results.append(ValidationResult(
            test_name=test_name,
            status="FAIL",
            details={},
            error_message=error_message
        ))
        self.failed += 1
        print(f"❌ {test_name}: {error_message}")
    
    def _record_error(self, test_name: str, error_message: str):
        """Record a test error"""
        self.results.append(ValidationResult(
            test_name=test_name,
            status="ERROR",
            details={},
            error_message=error_message
        ))
        self.errors += 1
        print(f"⚠️  {test_name}: {error_message}")
    
    def generate_report(self) -> bool:
        """Generate final validation report"""
        print("\\n" + "=" * 70)
        print("VALIDATION RESULTS SUMMARY")
        print("=" * 70)
        
        total_tests = len(self.results)
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.passed} ✅")
        print(f"Failed: {self.failed} ❌")
        print(f"Errors: {self.errors} ⚠️")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Detailed results by category
        categories = {}
        for result in self.results:
            category = result.test_name.split(" - ")[0]
            if category not in categories:
                categories[category] = {"pass": 0, "fail": 0, "error": 0}
            categories[category][result.status.lower()] += 1
        
        print("\\n📊 Results by Category:")
        for category, stats in categories.items():
            total_cat = sum(stats.values())
            pass_rate = (stats["pass"] / total_cat * 100) if total_cat > 0 else 0
            print(f"  {category}: {stats['pass']}/{total_cat} ({pass_rate:.0f}%)")
        
        # Save detailed results
        try:
            results_data = {
                "summary": {
                    "total_tests": total_tests,
                    "passed": self.passed,
                    "failed": self.failed,
                    "errors": self.errors,
                    "success_rate": success_rate,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                },
                "results": [
                    {
                        "test_name": r.test_name,
                        "status": r.status,
                        "details": r.details,
                        "error_message": r.error_message
                    }
                    for r in self.results
                ]
            }
            
            output_file = "/Users/rahulmehta/Desktop/AI-ML Projects/Career Assistant/AI-assistant-CSharpCorner/pathway_validation_results.json"
            with open(output_file, 'w') as f:
                json.dump(results_data, f, indent=2)
            
            print(f"\\n💾 Detailed results saved to: pathway_validation_results.json")
            
        except Exception as e:
            print(f"\\n⚠️  Could not save results: {e}")
        
        # Final assessment
        if success_rate >= 85:
            print("\\n🎉 VALIDATION PASSED - System is working well!")
            return True
        elif success_rate >= 70:
            print("\\n⚠️  VALIDATION WARNING - Some issues found")
            return False
        else:
            print("\\n❌ VALIDATION FAILED - Significant issues detected")
            return False


def main():
    """Main validation runner"""
    print("🧪 Starting Student Pathway System Validation...")
    print("This will test the complete system integration\\n")
    
    validator = StudentPathwayValidator()
    success = validator.run_all_validations()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())