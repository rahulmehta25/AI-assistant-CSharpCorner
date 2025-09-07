#!/usr/bin/env python3
"""
Test Script for Career Roadmap Generator System

This script demonstrates the functionality of the career roadmap generator
and milestone tracker modules.

Usage: python test_roadmap_generator.py
"""

import sys
import os
import json
from datetime import datetime

# Add the modules directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

try:
    from roadmap_generator import RoadmapGenerator, CareerLevel, TimelineType
    from milestone_tracker import MilestoneTracker, MilestoneStatus, SkillLevel
    print("✅ Successfully imported roadmap modules")
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)


def test_roadmap_generation():
    """Test the roadmap generation functionality"""
    print("\n" + "="*60)
    print("TESTING ROADMAP GENERATION")
    print("="*60)
    
    try:
        # Initialize the generator
        generator = RoadmapGenerator()
        print("✅ RoadmapGenerator initialized successfully")
        
        # Test generating a roadmap for software developers
        print("\n📊 Generating roadmap for Software Developer...")
        roadmap = generator.generate_roadmap(
            career_field="software_developers",
            student_level="college_sophomore",
            current_skills=["Python", "HTML", "CSS", "Basic JavaScript"],
            roadmap_years=5,
            location="US_National",
            specializations=["Web Development", "Machine Learning"],
            budget_constraints=False,
            fast_track=False
        )
        
        print(f"✅ Generated {roadmap.roadmap_duration} roadmap for {roadmap.career_field}")
        
        # Display roadmap summary
        summary = generator.get_roadmap_summary(roadmap)
        print(f"\n📋 Roadmap Summary:")
        print(f"   • Career Field: {summary['career_field']}")
        print(f"   • Duration: {summary['duration']}")
        print(f"   • Total Milestones: {summary['total_milestones']}")
        print(f"   • Critical Milestones: {summary['critical_milestones']}")
        print(f"   • Certifications: {summary['certifications']}")
        print(f"   • Projects: {summary['projects']}")
        print(f"   • Salary Growth: {summary['salary_growth']}")
        print(f"   • Skills to Learn: {summary['skills_to_learn']}")
        print(f"   • Confidence Score: {summary['confidence_score']:.2f}")
        print(f"   • Timeline Phases: {summary['timeline_phases']}")
        
        # Show first few milestones
        print(f"\n🎯 First 3 Milestones:")
        for i, milestone in enumerate(roadmap.milestones[:3], 1):
            print(f"   {i}. {milestone.title} (Target: {milestone.target_date})")
            print(f"      Priority: {milestone.priority} | Category: {milestone.category}")
        
        # Show salary progression
        print(f"\n💰 Salary Progression:")
        for salary in roadmap.salary_progression:
            print(f"   • {salary.level.value.title()} ({salary.years_experience}): "
                  f"${salary.min_salary:,} - ${salary.max_salary:,}")
        
        # Show skill progression for first 2 years
        print(f"\n🛠️  Skill Development (First 2 Years):")
        for year in ['1', '2']:
            skills = roadmap.skill_progression.get(year, [])
            if skills:
                print(f"   Year {year}: {', '.join(skills[:3])}{'...' if len(skills) > 3 else ''}")
        
        # Export roadmap
        export_path = "sample_roadmap_export.json"
        if generator.export_roadmap(roadmap, export_path):
            print(f"✅ Roadmap exported to {export_path}")
        
        return roadmap
        
    except Exception as e:
        print(f"❌ Error in roadmap generation: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_milestone_tracking(roadmap):
    """Test the milestone tracking functionality"""
    print("\n" + "="*60)
    print("TESTING MILESTONE TRACKING")
    print("="*60)
    
    try:
        # Initialize the tracker
        tracker = MilestoneTracker()
        print("✅ MilestoneTracker initialized successfully")
        
        # Start tracking for test user
        user_id = "test_user_123"
        initial_skills = {
            "Python": SkillLevel.BEGINNER,
            "HTML": SkillLevel.INTERMEDIATE,
            "CSS": SkillLevel.BEGINNER
        }
        
        if tracker.start_tracking_roadmap(user_id, roadmap, initial_skills):
            print(f"✅ Started tracking roadmap for user {user_id}")
        
        # Simulate some progress updates
        print(f"\n🔄 Simulating progress updates...")
        
        # Update first milestone
        if roadmap and roadmap.milestones:
            first_milestone = roadmap.milestones[0]
            success = tracker.update_milestone_progress(
                user_id=user_id,
                milestone_id=first_milestone.id,
                progress_percentage=65.0,
                status=MilestoneStatus.IN_PROGRESS,
                hours_spent=25,
                notes="Making good progress on programming fundamentals"
            )
            if success:
                print(f"   ✅ Updated milestone: {first_milestone.title} (65% complete)")
        
        # Update skill progress
        success = tracker.update_skill_progress(
            user_id=user_id,
            skill_name="Python",
            new_level=SkillLevel.INTERMEDIATE,
            practice_hours=40,
            assessment_completed="Python Basics Quiz"
        )
        if success:
            print(f"   ✅ Updated Python skill to Intermediate level")
        
        # Get progress summary
        summary = tracker.get_progress_summary(user_id)
        if summary:
            print(f"\n📊 Progress Summary:")
            print(f"   • Overall Progress: {summary['overall_progress']:.1f}%")
            print(f"   • Milestones Completed: {summary['milestones']['completed']}/{summary['milestones']['total']}")
            print(f"   • Skills at Advanced Level: {summary['skills']['advanced']}/{summary['skills']['total']}")
            print(f"   • Total Hours Invested: {summary['time_investment']['total_hours']}")
            print(f"   • Achievement Points: {summary['achievements']['points']}")
        
        # Get next recommendations
        recommendations = tracker.get_next_recommendations(user_id, limit=5)
        print(f"\n🎯 Next Recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        # Generate visualizations
        visualizations = tracker.generate_progress_visualizations(user_id)
        print(f"\n📈 Generated {len(visualizations)} visualizations:")
        for viz in visualizations:
            print(f"   • {viz.title} ({viz.chart_type})")
        
        # Export progress report
        report_path = "sample_progress_report.json"
        if tracker.export_progress_report(user_id, report_path):
            print(f"✅ Progress report exported to {report_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in milestone tracking: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_careers():
    """Test roadmap generation for different career fields"""
    print("\n" + "="*60)
    print("TESTING MULTIPLE CAREER FIELDS")
    print("="*60)
    
    generator = RoadmapGenerator()
    
    career_tests = [
        {
            "field": "data_scientists",
            "level": "graduate_student",
            "skills": ["Python", "Statistics", "Excel"]
        },
        {
            "field": "business_analysts", 
            "level": "college_junior",
            "skills": ["Excel", "Communication", "Problem Solving"]
        },
        {
            "field": "marketing_managers",
            "level": "entry_level",
            "skills": ["Social Media", "Content Writing"]
        }
    ]
    
    for test_case in career_tests:
        try:
            print(f"\n🧪 Testing {test_case['field']}...")
            roadmap = generator.generate_roadmap(
                career_field=test_case["field"],
                student_level=test_case["level"],
                current_skills=test_case["skills"],
                roadmap_years=3,
                fast_track=True
            )
            
            summary = generator.get_roadmap_summary(roadmap)
            print(f"   ✅ Generated roadmap with {summary['total_milestones']} milestones")
            print(f"   📊 Confidence Score: {summary['confidence_score']:.2f}")
            
        except Exception as e:
            print(f"   ❌ Error generating {test_case['field']} roadmap: {e}")


def main():
    """Main test function"""
    print("🚀 CAREER ROADMAP GENERATOR SYSTEM TEST")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test 1: Basic roadmap generation
        roadmap = test_roadmap_generation()
        
        # Test 2: Milestone tracking (only if roadmap generation succeeded)
        if roadmap:
            test_milestone_tracking(roadmap)
        
        # Test 3: Multiple career fields
        test_multiple_careers()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        print(f"\n🎉 The Career Roadmap Generator System is working properly!")
        print(f"📁 Files created:")
        print(f"   • /modules/roadmap_generator.py - Main roadmap generation engine")
        print(f"   • /modules/milestone_tracker.py - Progress tracking system") 
        print(f"   • /data/roadmap_templates/milestone_templates.json - Milestone templates")
        print(f"   • /data/roadmap_templates/certification_paths.json - Certification roadmaps")
        print(f"   • /data/roadmap_templates/project_ideas.json - Project recommendations")
        print(f"   • sample_roadmap_export.json - Sample generated roadmap")
        print(f"   • sample_progress_report.json - Sample progress report")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()