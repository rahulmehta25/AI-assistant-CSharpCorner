#!/usr/bin/env python3
"""
Student Pathway System Demonstration

This script demonstrates the capabilities of the StudentPathwaySystem
by creating and displaying detailed pathways for different student scenarios.

Usage: python test_student_pathways.py
"""

import sys
import json
from modules.student_pathways import StudentPathwaySystem, StudentLevel


def print_separator(title, char='-', width=70):
    """Print a formatted separator with title"""
    print(f"\n{char * width}")
    print(f"{title:^{width}}")
    print(f"{char * width}")


def print_milestone_details(milestones, max_items=5):
    """Print detailed milestone information"""
    print(f"\nMilestones ({len(milestones)} total, showing first {min(max_items, len(milestones))}):")
    for i, milestone in enumerate(milestones[:max_items]):
        priority_indicator = "⚠️" if milestone.priority == "high" else "📋" if milestone.priority == "medium" else "📌"
        print(f"  {i+1}. {priority_indicator} {milestone.title}")
        print(f"     Deadline: {milestone.deadline}")
        print(f"     Category: {milestone.category}")
        print(f"     {milestone.description}")
        print()


def print_course_details(courses, max_items=5):
    """Print detailed course information"""
    print(f"\nRecommended Courses ({len(courses)} total, showing first {min(max_items, len(courses))}):")
    for i, course in enumerate(courses[:max_items]):
        course_indicator = "🎓" if course.course_type == "AP" else "📚" if course.course_type == "honors" else "📖"
        print(f"  {i+1}. {course_indicator} {course.course_name} ({course.course_type})")
        print(f"     {course.description}")
        print(f"     Difficulty: {course.difficulty_level} | Relevance: {course.relevance_score}")
        if course.prerequisites:
            print(f"     Prerequisites: {', '.join(course.prerequisites)}")
        print()


def print_activity_details(activities, max_items=5):
    """Print detailed activity information"""
    print(f"\nRecommended Activities ({len(activities)} total, showing first {min(max_items, len(activities))}):")
    for i, activity in enumerate(activities[:max_items]):
        activity_indicator = "🏆" if activity.type == "competition" else "👥" if activity.type == "club" else "🤝" if activity.type == "volunteer" else "💼"
        print(f"  {i+1}. {activity_indicator} {activity.name} ({activity.type})")
        print(f"     {activity.description}")
        print(f"     Time commitment: {activity.time_commitment}")
        print(f"     Skills gained: {', '.join(activity.skills_gained[:4])}...")
        print(f"     Career relevance: {activity.career_relevance}")
        print()


def print_timeline_summary(timeline):
    """Print timeline summary"""
    print("\nTimeline Highlights:")
    for month, tasks in timeline.items():
        if tasks:  # Only show months with tasks
            print(f"  {month}: {len(tasks)} task(s)")
            for task in tasks[:2]:  # Show first 2 tasks per month
                print(f"    • {task}")
            if len(tasks) > 2:
                print(f"    • ... and {len(tasks) - 2} more")
        

def demonstrate_pathway(system, title, **kwargs):
    """Demonstrate a complete pathway"""
    print_separator(title)
    
    # Generate pathway
    pathway = system.generate_pathway(**kwargs)
    
    # Get summary
    summary = system.get_pathway_summary(pathway)
    
    # Print pathway overview
    print(f"\n📊 PATHWAY OVERVIEW")
    print(f"Student Level: {pathway.student_level.value.replace('_', ' ').title()}")
    print(f"Career Field: {pathway.career_field.title()}")
    if pathway.onet_code:
        print(f"O*NET Code: {pathway.onet_code}")
    print(f"Total Milestones: {summary['total_milestones']} ({summary['high_priority_milestones']} high priority)")
    print(f"Courses to Take: {summary['recommended_courses']}")
    print(f"Activities: {summary['activities']}")
    print(f"Skills to Develop: {summary['skills_to_develop']}")
    print(f"\n🎯 Focus Areas: {', '.join(summary['focus_areas'])}")
    print(f"🚀 Next Milestone: {summary['next_milestone']}")
    
    # Print detailed sections
    print_milestone_details(pathway.milestones)
    print_course_details(pathway.courses)
    print_activity_details(pathway.activities)
    
    # Skills to develop
    print(f"\n💡 Skills to Develop ({len(pathway.skills_to_develop)} total):")
    for i, skill in enumerate(pathway.skills_to_develop[:8], 1):
        print(f"  {i}. {skill}")
    if len(pathway.skills_to_develop) > 8:
        print(f"  ... and {len(pathway.skills_to_develop) - 8} more")
    
    print_timeline_summary(pathway.timeline)
    
    return pathway


def main():
    """Main demonstration function"""
    print("🎓 STUDENT PATHWAY SYSTEM DEMONSTRATION")
    print("=" * 70)
    print("This system creates personalized career pathways for high school")
    print("and college students, mapping O*NET careers to educational paths.")
    
    # Initialize system
    print("\nInitializing Student Pathway System...")
    system = StudentPathwaySystem()
    print("✅ System initialized successfully!")
    
    # Demonstration scenarios
    scenarios = [
        {
            "title": "HIGH SCHOOL SOPHOMORE - EXPLORING STEM",
            "student_level": StudentLevel.SOPHOMORE_HS,
            "career_field": "computer science",
            "interests": ["technology", "problem-solving", "games"],
            "current_skills": ["basic math", "some programming"],
            "gpa": 3.4
        },
        {
            "title": "HIGH SCHOOL JUNIOR - PRE-MED TRACK",
            "student_level": StudentLevel.JUNIOR_HS,
            "career_field": "medicine",
            "interests": ["helping people", "biology", "research"],
            "current_skills": ["biology", "chemistry", "volunteer experience"],
            "gpa": 3.9,
            "standardized_scores": {"SAT": 1450}
        },
        {
            "title": "COLLEGE FRESHMAN - UNDECIDED ENGINEERING",
            "student_level": StudentLevel.FRESHMAN_COLLEGE,
            "career_field": "engineering",
            "interests": ["design", "building", "mathematics"],
            "current_skills": ["calculus", "physics", "teamwork"],
            "gpa": 3.3
        },
        {
            "title": "COLLEGE JUNIOR - BUSINESS & ENTREPRENEURSHIP",
            "student_level": StudentLevel.JUNIOR_COLLEGE,
            "career_field": "business",
            "onet_code": "11-1021.00",
            "interests": ["leadership", "innovation", "finance"],
            "current_skills": ["business fundamentals", "presentation", "leadership"],
            "gpa": 3.7
        },
        {
            "title": "HIGH SCHOOL SENIOR - LIBERAL ARTS",
            "student_level": StudentLevel.SENIOR_HS,
            "career_field": "liberal arts",
            "interests": ["writing", "history", "cultural studies"],
            "current_skills": ["writing", "research", "critical thinking"],
            "gpa": 3.6,
            "standardized_scores": {"SAT": 1320, "ACT": 29}
        }
    ]
    
    # Run demonstrations
    pathways = []
    for scenario in scenarios:
        pathway = demonstrate_pathway(system, **scenario)
        pathways.append(pathway)
    
    # Summary comparison
    print_separator("PATHWAY COMPARISON SUMMARY")
    print(f"\n{'Scenario':<35} {'Level':<15} {'Career':<15} {'Milestones':<12} {'Focus Areas'}")
    print("-" * 90)
    
    for i, pathway in enumerate(pathways):
        summary = system.get_pathway_summary(pathway)
        level = pathway.student_level.value.replace('_', ' ').title()[:14]
        career = pathway.career_field.title()[:14]
        milestones = f"{summary['total_milestones']}"
        focus = ', '.join(summary['focus_areas'][:2])[:25] + "..." if len(summary['focus_areas']) > 2 else ', '.join(summary['focus_areas'])
        
        print(f"{scenarios[i]['title'][:34]:<35} {level:<15} {career:<15} {milestones:<12} {focus}")
    
    # Export sample pathway
    print_separator("EXPORTING SAMPLE PATHWAY")
    sample_pathway = pathways[0]  # Export first pathway as sample
    export_path = "sample_pathway_export.json"
    
    if system.export_pathway_to_json(sample_pathway, export_path):
        print(f"✅ Sample pathway exported to: {export_path}")
        print(f"This file contains the complete pathway data in JSON format.")
    else:
        print("❌ Failed to export sample pathway")
    
    print_separator("DEMONSTRATION COMPLETE", "=")
    print("🎉 All pathway demonstrations completed successfully!")
    print("\nKey Features Demonstrated:")
    print("• ✅ Grade/year-specific milestone generation")
    print("• ✅ Career-aligned course recommendations")  
    print("• ✅ Extracurricular activity suggestions")
    print("• ✅ Skills gap analysis and development planning")
    print("• ✅ Month-by-month timeline creation")
    print("• ✅ Multi-level pathway support (HS and College)")
    print("• ✅ JSON export functionality")
    
    print(f"\nThe system successfully created {len(pathways)} personalized pathways")
    print("with detailed guidance for different student situations.")


if __name__ == "__main__":
    main()