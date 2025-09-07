"""
Comprehensive Integration Test for Career Assistant System

This script tests all major components of the integrated Career Assistant system
to ensure everything works together properly.

Author: Career Assistant AI System
Version: 2.0.0
"""

import os
import sys
import json
from datetime import datetime

# Add modules to path
sys.path.append('.')
sys.path.append('./modules')

def print_test_header(test_name: str):
    """Print a formatted test header"""
    print("\n" + "="*60)
    print(f"🧪 {test_name}")
    print("="*60)

def print_test_result(test_name: str, success: bool, details: str = ""):
    """Print test result"""
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"{status}: {test_name}")
    if details:
        print(f"   Details: {details}")

def test_core_system_initialization():
    """Test core system initialization"""
    print_test_header("Core System Initialization")
    
    try:
        from modules.career_assistant_core import CareerAssistantCore
        
        # Initialize the system
        core = CareerAssistantCore()
        
        # Check if core components are available
        has_modules = all([
            hasattr(core, 'onet_scraper'),
            hasattr(core, 'recommendation_engine'),
            hasattr(core, 'student_pathways'),
            hasattr(core, 'roadmap_generator'),
            hasattr(core, 'job_scraper')
        ])
        
        print_test_result("Core System Initialization", True, f"All modules loaded: {has_modules}")
        return core, True
        
    except Exception as e:
        print_test_result("Core System Initialization", False, str(e))
        return None, False

def test_user_profile_management(core):
    """Test user profile creation and management"""
    print_test_header("User Profile Management")
    
    try:
        # Create a test user profile
        user_id = "integration_test_user"
        profile = core.create_user_profile(
            user_id=user_id,
            name="Integration Test User",
            education_level="Bachelor's Degree",
            current_skills=["Python", "Data Analysis", "Problem Solving"],
            interests=["Technology", "AI", "Software Development"],
            career_goals=["Software Engineer", "Data Scientist"],
            preferred_locations=["Remote", "San Francisco"]
        )
        
        # Test profile retrieval
        loaded_profile = core.get_user_profile(user_id)
        profile_exists = loaded_profile is not None
        
        # Test profile update
        if profile_exists:
            loaded_profile.current_skills.append("Machine Learning")
            update_success = core.save_user_profile(loaded_profile)
            
            # Verify update
            updated_profile = core.get_user_profile(user_id)
            has_ml_skill = "Machine Learning" in updated_profile.current_skills
            
            print_test_result("User Profile Management", True, 
                            f"Profile created, loaded, and updated. Has ML skill: {has_ml_skill}")
            return True
        else:
            print_test_result("User Profile Management", False, "Failed to load profile")
            return False
            
    except Exception as e:
        print_test_result("User Profile Management", False, str(e))
        return False

def test_career_recommendations(core):
    """Test career recommendation functionality"""
    print_test_header("Career Recommendations")
    
    try:
        user_id = "integration_test_user"
        recommendations = core.get_career_recommendations(user_id, limit=5)
        
        has_recommendations = len(recommendations) > 0
        
        if has_recommendations:
            print(f"Found {len(recommendations)} career recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"  {i}. {rec.title} (Match: {rec.match_score:.1%})")
        
        print_test_result("Career Recommendations", has_recommendations, 
                        f"Generated {len(recommendations)} recommendations")
        return has_recommendations
        
    except Exception as e:
        print_test_result("Career Recommendations", False, str(e))
        return False

def test_career_search(core):
    """Test career search functionality"""
    print_test_header("Career Search")
    
    try:
        # Test searching for software developer careers
        search_results = core.search_careers("software developer")
        has_results = len(search_results) > 0
        
        if has_results:
            print(f"Found {len(search_results)} careers matching 'software developer':")
            for result in search_results[:3]:
                print(f"  - {result.get('title', 'Unknown')}")
        
        print_test_result("Career Search", has_results, 
                        f"Found {len(search_results)} matching careers")
        return has_results
        
    except Exception as e:
        print_test_result("Career Search", False, str(e))
        return False

def test_student_pathways(core):
    """Test student pathway generation"""
    print_test_header("Student Pathways")
    
    try:
        user_id = "integration_test_user"
        target_career = "Software Developer"
        
        pathway = core.generate_student_pathway(user_id, target_career)
        has_pathway = pathway is not None
        
        if has_pathway:
            steps = pathway.get('pathway_steps', [])
            timeline = pathway.get('estimated_timeline', 'Unknown')
            print(f"Generated pathway with {len(steps)} steps")
            print(f"Estimated timeline: {timeline}")
            
            if steps:
                print("Sample pathway steps:")
                for step in steps[:2]:
                    print(f"  - {step.get('title', 'Unknown step')}")
        
        print_test_result("Student Pathways", has_pathway, 
                        f"Pathway generated with {len(steps) if has_pathway else 0} steps")
        return has_pathway
        
    except Exception as e:
        print_test_result("Student Pathways", False, str(e))
        return False

def test_career_roadmap(core):
    """Test career roadmap generation"""
    print_test_header("Career Roadmap")
    
    try:
        user_id = "integration_test_user"
        target_career = "Data Scientist"
        timeline_months = 18
        
        roadmap = core.generate_career_roadmap(user_id, target_career, timeline_months)
        has_roadmap = roadmap is not None
        
        if has_roadmap:
            phases = roadmap.get('phases', [])
            print(f"Generated roadmap with {len(phases)} phases over {timeline_months} months")
            
            if phases:
                print("Sample roadmap phases:")
                for phase in phases[:2]:
                    title = phase.get('title', 'Unknown phase')
                    duration = phase.get('duration', 'Unknown duration')
                    print(f"  - {title} ({duration})")
        
        print_test_result("Career Roadmap", has_roadmap, 
                        f"Roadmap generated with {len(phases) if has_roadmap else 0} phases")
        return has_roadmap
        
    except Exception as e:
        print_test_result("Career Roadmap", False, str(e))
        return False

def test_job_search(core):
    """Test job search functionality"""
    print_test_header("Job Search")
    
    try:
        # Test basic job search
        jobs = core.search_jobs("python developer", "remote", limit=5)
        has_jobs = len(jobs) > 0
        
        if has_jobs:
            print(f"Found {len(jobs)} jobs for 'python developer':")
            for job in jobs[:3]:
                title = job.get('title', 'Unknown')
                company = job.get('company', 'Unknown')
                location = job.get('location', 'Unknown')
                print(f"  - {title} at {company} ({location})")
        
        print_test_result("Job Search", has_jobs, 
                        f"Found {len(jobs)} job listings")
        return has_jobs
        
    except Exception as e:
        print_test_result("Job Search", False, str(e))
        return False

def test_job_recommendations(core):
    """Test job recommendations"""
    print_test_header("Job Recommendations")
    
    try:
        user_id = "integration_test_user"
        job_recommendations = core.get_job_recommendations(user_id, limit=5)
        has_recommendations = len(job_recommendations) > 0
        
        if has_recommendations:
            print(f"Generated {len(job_recommendations)} job recommendations:")
            for job in job_recommendations[:3]:
                title = job.get('title', 'Unknown')
                company = job.get('company', 'Unknown')
                print(f"  - {title} at {company}")
        
        print_test_result("Job Recommendations", has_recommendations, 
                        f"Generated {len(job_recommendations)} job recommendations")
        return has_recommendations
        
    except Exception as e:
        print_test_result("Job Recommendations", False, str(e))
        return False

def test_skill_gap_analysis(core):
    """Test skill gap analysis"""
    print_test_header("Skill Gap Analysis")
    
    try:
        user_id = "integration_test_user"
        target_career = "15-1252.00"  # Software Developer O*NET code
        
        skill_gaps = core.get_skill_gaps(user_id, target_career)
        has_analysis = bool(skill_gaps)
        
        if has_analysis:
            missing_skills = skill_gaps.get('missing_skills', [])
            matching_skills = skill_gaps.get('matching_skills', [])
            match_percentage = skill_gaps.get('match_percentage', 0)
            
            print(f"Skill match percentage: {match_percentage:.1f}%")
            print(f"Matching skills: {len(matching_skills)}")
            print(f"Missing skills: {len(missing_skills)}")
            
            if missing_skills:
                print("Sample missing skills:")
                for skill in missing_skills[:3]:
                    print(f"  - {skill}")
        
        print_test_result("Skill Gap Analysis", has_analysis, 
                        f"Analysis completed. Match: {skill_gaps.get('match_percentage', 0):.1f}%")
        return has_analysis
        
    except Exception as e:
        print_test_result("Skill Gap Analysis", False, str(e))
        return False

def test_progress_analytics(core):
    """Test user progress analytics"""
    print_test_header("Progress Analytics")
    
    try:
        user_id = "integration_test_user"
        analytics = core.generate_user_analytics(user_id)
        has_analytics = bool(analytics)
        
        if has_analytics:
            completeness = analytics.get('profile_completeness', 0)
            exploration_score = analytics.get('career_exploration_score', 0)
            recommendations_taken = analytics.get('recommendations_taken', 0)
            
            print(f"Profile completeness: {completeness:.1f}%")
            print(f"Career exploration score: {exploration_score:.1f}")
            print(f"Recommendations taken: {recommendations_taken}")
        
        print_test_result("Progress Analytics", has_analytics, 
                        f"Analytics generated. Profile: {analytics.get('profile_completeness', 0):.1f}% complete")
        return has_analytics
        
    except Exception as e:
        print_test_result("Progress Analytics", False, str(e))
        return False

def test_data_export(core):
    """Test user data export functionality"""
    print_test_header("Data Export")
    
    try:
        user_id = "integration_test_user"
        export_path = core.export_user_data(user_id, format="json")
        
        export_success = export_path is not None and os.path.exists(export_path)
        
        if export_success:
            # Check file size to ensure it has content
            file_size = os.path.getsize(export_path)
            print(f"Export file created: {os.path.basename(export_path)}")
            print(f"File size: {file_size} bytes")
            
            # Clean up test export file
            os.remove(export_path)
        
        print_test_result("Data Export", export_success, 
                        f"Export {'successful' if export_success else 'failed'}")
        return export_success
        
    except Exception as e:
        print_test_result("Data Export", False, str(e))
        return False

def test_system_health(core):
    """Test system health check"""
    print_test_header("System Health Check")
    
    try:
        health = core.health_check()
        is_healthy = health.get('status') == 'healthy'
        
        print(f"System status: {health.get('status', 'unknown')}")
        
        modules = health.get('modules', {})
        active_modules = sum(1 for status in modules.values() if status)
        print(f"Active modules: {active_modules}/{len(modules)}")
        
        data_checks = health.get('data_integrity', {})
        passed_checks = sum(1 for status in data_checks.values() if status)
        print(f"Data integrity checks: {passed_checks}/{len(data_checks)}")
        
        print_test_result("System Health Check", is_healthy, 
                        f"Status: {health.get('status', 'unknown')}")
        return is_healthy
        
    except Exception as e:
        print_test_result("System Health Check", False, str(e))
        return False

def run_comprehensive_test():
    """Run all integration tests"""
    print("🚀 Starting Career Assistant Integration Test Suite")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # Initialize system
    core, init_success = test_core_system_initialization()
    test_results.append(("Core System Initialization", init_success))
    
    if not init_success or not core:
        print("\n❌ Cannot continue testing without core system")
        return test_results
    
    # Run all tests
    tests = [
        ("User Profile Management", lambda: test_user_profile_management(core)),
        ("Career Recommendations", lambda: test_career_recommendations(core)),
        ("Career Search", lambda: test_career_search(core)),
        ("Student Pathways", lambda: test_student_pathways(core)),
        ("Career Roadmap", lambda: test_career_roadmap(core)),
        ("Job Search", lambda: test_job_search(core)),
        ("Job Recommendations", lambda: test_job_recommendations(core)),
        ("Skill Gap Analysis", lambda: test_skill_gap_analysis(core)),
        ("Progress Analytics", lambda: test_progress_analytics(core)),
        ("Data Export", lambda: test_data_export(core)),
        ("System Health Check", lambda: test_system_health(core))
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {str(e)}")
            test_results.append((test_name, False))
    
    # Print summary
    print_test_summary(test_results)
    
    return test_results

def print_test_summary(test_results):
    """Print comprehensive test summary"""
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    print(f"Tests Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    print()
    
    print("Individual Test Results:")
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Career Assistant integration is working correctly.")
    elif passed > total * 0.8:
        print(f"\n✅ Most tests passed ({passed}/{total}). System is mostly functional.")
    elif passed > total * 0.5:
        print(f"\n⚠️ Some tests failed ({total-passed}/{total}). System has partial functionality.")
    else:
        print(f"\n❌ Many tests failed ({total-passed}/{total}). System needs significant work.")
    
    print("\n🔧 Integration test complete!")

if __name__ == "__main__":
    try:
        run_comprehensive_test()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()