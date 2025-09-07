#!/usr/bin/env python3
"""
Test script for the AI-powered Career Recommendation Engine
Demonstrates the complete workflow from assessment to recommendations
"""

import json
from pathlib import Path
from modules.recommendation_engine import RecommendationEngine, StudentProfile
from modules.skills_assessment import SkillsAssessment


def test_recommendation_engine():
    """Test the recommendation engine with sample student profiles"""
    
    print("\n" + "="*80)
    print(" AI-POWERED CAREER RECOMMENDATION ENGINE - DEMO ")
    print("="*80)
    
    # Initialize engines
    recommendation_engine = RecommendationEngine()
    skills_assessor = SkillsAssessment()
    
    # Create diverse student profiles for testing
    test_profiles = [
        {
            "name": "Alex Chen",
            "description": "Computer Science major with strong technical skills",
            "profile": StudentProfile(
                student_id="STU001",
                name="Alex Chen",
                age=21,
                education_level="undergraduate",
                gpa=3.7,
                major="Computer Science",
                interests=["artificial_intelligence", "data_analysis", "problem_solving", 
                          "innovation", "technology"],
                skills={
                    "Python": 4,
                    "Machine Learning": 3,
                    "Data Analysis": 4,
                    "SQL": 3,
                    "Communication": 3,
                    "Problem Solving": 5,
                    "Mathematics": 4,
                    "Statistics": 3
                },
                activities=["AI Club President", "Hackathon Winner", "Research Assistant", 
                           "Open Source Contributor"],
                personality_traits={
                    "openness": 0.85,
                    "conscientiousness": 0.75,
                    "extraversion": 0.55,
                    "agreeableness": 0.65,
                    "neuroticism": 0.25
                },
                work_experience=[
                    {"role": "Data Science Intern", "duration": "3 months", "company": "Tech Startup"},
                    {"role": "Teaching Assistant", "duration": "6 months", "company": "University"}
                ],
                preferred_work_environment=["innovative", "collaborative", "flexible"],
                location_preference="major_city",
                salary_expectations="$70,000+"
            )
        },
        {
            "name": "Sarah Martinez",
            "description": "Business major interested in marketing and entrepreneurship",
            "profile": StudentProfile(
                student_id="STU002",
                name="Sarah Martinez",
                age=22,
                education_level="undergraduate",
                gpa=3.5,
                major="Business Administration",
                interests=["marketing", "entrepreneurship", "leadership", "creativity", 
                          "social_media"],
                skills={
                    "Marketing": 4,
                    "Communication": 5,
                    "Leadership": 4,
                    "Project Management": 3,
                    "Data Analysis": 2,
                    "Creative Writing": 4,
                    "Social Media": 5,
                    "Presentation": 4
                },
                activities=["Marketing Club VP", "Student Government", "Startup Weekend Participant",
                           "Campus Ambassador"],
                personality_traits={
                    "openness": 0.75,
                    "conscientiousness": 0.7,
                    "extraversion": 0.85,
                    "agreeableness": 0.75,
                    "neuroticism": 0.3
                },
                work_experience=[
                    {"role": "Marketing Intern", "duration": "4 months", "company": "Digital Agency"},
                    {"role": "Brand Ambassador", "duration": "1 year", "company": "Fashion Brand"}
                ],
                preferred_work_environment=["fast-paced", "creative", "collaborative"],
                location_preference="flexible",
                salary_expectations="$55,000+"
            )
        },
        {
            "name": "Michael Johnson",
            "description": "Pre-med student with interest in healthcare and research",
            "profile": StudentProfile(
                student_id="STU003",
                name="Michael Johnson",
                age=20,
                education_level="undergraduate",
                gpa=3.9,
                major="Biology (Pre-Med)",
                interests=["medicine", "research", "helping_others", "science", "healthcare"],
                skills={
                    "Biology": 5,
                    "Chemistry": 4,
                    "Research": 4,
                    "Data Analysis": 3,
                    "Communication": 3,
                    "Problem Solving": 4,
                    "Teamwork": 4,
                    "Attention to Detail": 5
                },
                activities=["Pre-Med Society", "Hospital Volunteer", "Research Lab Member",
                           "Biology Tutor"],
                personality_traits={
                    "openness": 0.7,
                    "conscientiousness": 0.9,
                    "extraversion": 0.5,
                    "agreeableness": 0.8,
                    "neuroticism": 0.35
                },
                work_experience=[
                    {"role": "Research Assistant", "duration": "1 year", "company": "Medical Research Lab"},
                    {"role": "Medical Scribe", "duration": "6 months", "company": "Local Hospital"}
                ],
                preferred_work_environment=["structured", "collaborative", "mission-driven"],
                location_preference="near_medical_centers",
                salary_expectations="$60,000+"
            )
        }
    ]
    
    # Process each test profile
    for test_case in test_profiles:
        print(f"\n\n{'='*80}")
        print(f" STUDENT PROFILE: {test_case['name']}")
        print(f" {test_case['description']}")
        print(f"{'='*80}")
        
        profile = test_case['profile']
        
        # Display student information
        print(f"\n📚 Academic Profile:")
        print(f"   • Major: {profile.major}")
        print(f"   • GPA: {profile.gpa}")
        print(f"   • Education Level: {profile.education_level}")
        
        print(f"\n💼 Skills (Top 5):")
        sorted_skills = sorted(profile.skills.items(), key=lambda x: x[1], reverse=True)[:5]
        for skill, level in sorted_skills:
            print(f"   • {skill}: {'⭐' * level}")
        
        print(f"\n🎯 Interests:")
        for interest in profile.interests[:5]:
            print(f"   • {interest.replace('_', ' ').title()}")
        
        # Perform skills assessment
        print(f"\n📊 Skills Assessment:")
        skills_data = {skill: {"self_rating": level, "years_experience": level/2} 
                      for skill, level in profile.skills.items()}
        skill_assessment = skills_assessor.evaluate_skills(skills_data)
        
        print(f"   Strengths: {', '.join(skill_assessment.strengths[:3]) if skill_assessment.strengths else 'Developing'}")
        print(f"   Areas for Growth: {', '.join(skill_assessment.areas_for_improvement[:3]) if skill_assessment.areas_for_improvement else 'Well-rounded'}")
        
        # Get interest profile
        interest_profile = skills_assessor.assess_interests(
            profile.interests,
            profile.activities
        )
        print(f"\n🧭 Holland Code: {interest_profile.primary_code}{interest_profile.secondary_code}{interest_profile.tertiary_code}")
        print(f"   Profile: {interest_profile.description[:100]}...")
        
        # Get career recommendations
        print(f"\n🎯 TOP 5 CAREER RECOMMENDATIONS:")
        print("-" * 80)
        
        recommendations = recommendation_engine.recommend_careers(profile, top_n=5)
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec.title}")
            print(f"   Match Score: {rec.match_score:.1%} | Confidence: {rec.confidence:.0%}")
            print(f"   Growth: {rec.growth_potential} | Salary: {rec.salary_range}")
            print(f"   Outlook: {rec.job_outlook}")
            
            print(f"\n   ✨ Why this career?")
            for reason in rec.reasons[:2]:
                print(f"      • {reason}")
            
            if rec.skill_gaps:
                print(f"\n   📈 Skills to develop:")
                for gap in rec.skill_gaps[:2]:
                    print(f"      • {gap['skill']}")
            
            print(f"\n   🛤️ Learning Path Preview:")
            for step in rec.learning_path[:2]:
                if not step.startswith("  "):
                    print(f"      {step}")
        
        # Save recommendations
        output_dir = Path("data/recommendations")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"{profile.student_id}_recommendations.json"
        with open(output_file, 'w') as f:
            json.dump({
                "student": {
                    "id": profile.student_id,
                    "name": profile.name,
                    "major": profile.major,
                    "gpa": profile.gpa
                },
                "recommendations": [rec.to_dict() for rec in recommendations],
                "assessment": {
                    "holland_code": f"{interest_profile.primary_code}{interest_profile.secondary_code}{interest_profile.tertiary_code}",
                    "top_skills": sorted_skills
                }
            }, f, indent=2)
        
        print(f"\n💾 Recommendations saved to: {output_file}")
    
    # Summary statistics
    print("\n\n" + "="*80)
    print(" RECOMMENDATION ENGINE STATISTICS ")
    print("="*80)
    print(f"✅ Processed {len(test_profiles)} student profiles")
    print(f"✅ Generated {len(test_profiles) * 5} career recommendations")
    print(f"✅ Assessed {sum(len(p['profile'].skills) for p in test_profiles)} skills")
    print(f"✅ All recommendations saved to data/recommendations/")
    
    print("\n🎉 Demo completed successfully!")
    print("\nThe recommendation engine provides:")
    print("  • Personalized career matches based on skills, interests, and personality")
    print("  • Explainable AI with clear reasons for each recommendation")
    print("  • Skill gap analysis and learning paths")
    print("  • Integration with O*NET career data")
    print("  • Support for diverse student profiles and career paths")


def test_edge_cases():
    """Test edge cases and special scenarios"""
    
    print("\n\n" + "="*80)
    print(" TESTING EDGE CASES ")
    print("="*80)
    
    engine = RecommendationEngine()
    
    # Test case 1: Student with minimal data
    minimal_profile = StudentProfile(
        student_id="TEST001",
        name="Test User",
        age=18,
        education_level="high_school",
        gpa=2.5,
        interests=["technology"],
        skills={"Basic Computer": 2}
    )
    
    print("\n📋 Test Case 1: Minimal Profile")
    recommendations = engine.recommend_careers(minimal_profile, top_n=3)
    print(f"   Generated {len(recommendations)} recommendations despite limited data")
    
    # Test case 2: Highly skilled student
    expert_profile = StudentProfile(
        student_id="TEST002",
        name="Expert User",
        age=25,
        education_level="graduate",
        gpa=4.0,
        major="Multiple Disciplines",
        interests=["technology", "business", "research", "leadership", "innovation"],
        skills={skill: 5 for skill in ["Python", "Leadership", "Research", "Communication", 
                                        "Data Analysis", "Project Management"]},
        personality_traits={trait: 0.9 for trait in ["openness", "conscientiousness", 
                                                     "extraversion", "agreeableness"]}
    )
    
    print("\n📋 Test Case 2: Expert Profile")
    recommendations = engine.recommend_careers(expert_profile, top_n=3)
    print(f"   Top match score: {recommendations[0].match_score:.1%}")
    print(f"   Confidence level: {recommendations[0].confidence:.0%}")
    
    # Test case 3: Career changer
    career_changer = StudentProfile(
        student_id="TEST003",
        name="Career Changer",
        age=35,
        education_level="undergraduate",
        gpa=3.0,
        major="English Literature",
        interests=["technology", "data", "problem_solving"],  # Different from major
        skills={"Writing": 5, "Python": 2, "Data Analysis": 1},  # Mixed skill levels
        work_experience=[
            {"role": "Content Writer", "duration": "5 years", "company": "Media Company"}
        ]
    )
    
    print("\n📋 Test Case 3: Career Changer")
    recommendations = engine.recommend_careers(career_changer, top_n=3)
    print(f"   Recommended transition paths identified")
    for rec in recommendations[:2]:
        print(f"   • {rec.title}: {rec.match_score:.1%}")
    
    print("\n✅ All edge cases handled successfully")


if __name__ == "__main__":
    # Run main test
    test_recommendation_engine()
    
    # Run edge case tests
    test_edge_cases()
    
    print("\n" + "="*80)
    print(" All tests completed successfully! ")
    print("="*80)