#!/usr/bin/env python3
"""
Test script for OpenAI GPT-4 integration
Tests the AI-powered career recommendation features
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Add modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import the recommendation engine
from modules.recommendation_engine import RecommendationEngine, StudentProfile

def test_openai_connection():
    """Test if OpenAI is properly configured"""
    print("\n" + "="*60)
    print("Testing OpenAI Connection")
    print("="*60)
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ OpenAI API key not configured!")
        print("Please add your OpenAI API key to the .env file:")
        print("OPENAI_API_KEY=sk-your-actual-api-key-here")
        return False
    
    print("✅ OpenAI API key found in .env file")
    
    # Initialize engine
    engine = RecommendationEngine()
    
    if engine.openai_client:
        print("✅ OpenAI client initialized successfully")
        return True
    else:
        print("❌ Failed to initialize OpenAI client")
        return False

def test_ai_recommendations():
    """Test AI-powered career recommendations"""
    print("\n" + "="*60)
    print("Testing AI-Powered Career Recommendations")
    print("="*60)
    
    # Create test student profile
    test_profile = {
        'name': 'Test Student',
        'age': 22,
        'education_level': 'undergraduate',
        'gpa': 3.7,
        'major': 'Computer Science',
        'interests': ['technology', 'problem-solving', 'innovation'],
        'skills': ['Python', 'Data Analysis', 'Machine Learning', 'Communication'],
        'personality_traits': {
            'openness': 0.8,
            'conscientiousness': 0.7,
            'extraversion': 0.6,
            'agreeableness': 0.7,
            'neuroticism': 0.3
        },
        'work_experience': [
            {'role': 'Software Intern', 'duration': '3 months'}
        ],
        'preferred_work_environment': ['remote-friendly', 'innovative'],
        'location_preference': 'flexible',
        'salary_expectations': '$70,000+'
    }
    
    print("\nTest Profile:")
    print(f"  Name: {test_profile['name']}")
    print(f"  Major: {test_profile['major']}")
    print(f"  Skills: {', '.join(test_profile['skills'])}")
    print(f"  Interests: {', '.join(test_profile['interests'])}")
    
    # Initialize engine and get recommendations
    engine = RecommendationEngine()
    
    if not engine.openai_client:
        print("\n⚠️  OpenAI not available - using traditional recommendations only")
    else:
        print("\n✅ Using OpenAI GPT-4 for enhanced recommendations")
    
    # Get recommendations
    recommendations = engine.generate_recommendations(test_profile)
    
    print(f"\n📊 Generated {len(recommendations)} career recommendations")
    
    # Display top 3 recommendations
    print("\nTop 3 Career Recommendations:")
    print("-" * 40)
    
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"\n{i}. {rec.get('title', 'Unknown Career')}")
        print(f"   Match Score: {rec.get('match_score', 0):.1%}")
        print(f"   Confidence: {rec.get('confidence', 0):.0%}")
        
        # Check for AI insights
        if 'ai_insights' in rec:
            insights = rec['ai_insights']
            print("\n   🤖 AI-Powered Insights:")
            print(f"   • Success Probability: {insights.get('success_probability', 0):.0%}")
            print(f"   • Timeline: {insights.get('timeline_estimate', 'Unknown')}")
            
            if insights.get('key_strengths'):
                print("\n   Key Strengths:")
                for strength in insights['key_strengths'][:2]:
                    print(f"   • {strength}")
            
            if insights.get('development_areas'):
                print("\n   Areas to Develop:")
                for area in insights['development_areas'][:2]:
                    print(f"   • {area}")
        else:
            print("   ℹ️  No AI insights available (traditional analysis only)")

def test_skill_gap_analysis():
    """Test AI-powered skill gap analysis"""
    print("\n" + "="*60)
    print("Testing AI-Powered Skill Gap Analysis")
    print("="*60)
    
    engine = RecommendationEngine()
    
    if not engine.openai_client:
        print("⚠️  OpenAI not available - skipping skill gap analysis test")
        return
    
    # Test skills
    current_skills = {
        'Python': 4,
        'JavaScript': 2,
        'Data Analysis': 3,
        'Communication': 4
    }
    
    required_skills = [
        'Machine Learning',
        'Deep Learning',
        'TensorFlow',
        'PyTorch',
        'Data Science',
        'Statistics',
        'Cloud Computing'
    ]
    
    print("\nCurrent Skills:")
    for skill, level in current_skills.items():
        print(f"  • {skill}: Level {level}/5")
    
    print("\nRequired Skills for AI Engineer:")
    for skill in required_skills[:5]:
        print(f"  • {skill}")
    
    # Get AI analysis
    analysis = engine.get_ai_skill_gap_analysis(current_skills, required_skills)
    
    if analysis:
        print("\n🤖 AI Skill Gap Analysis:")
        print(f"\nCritical Gaps:")
        for gap in analysis.get('critical_gaps', [])[:3]:
            print(f"  • {gap}")
        
        print(f"\nLearning Priorities:")
        for priority in analysis.get('learning_priorities', [])[:3]:
            print(f"  • {priority}")
        
        print(f"\nEstimated Time: {analysis.get('estimated_time', 'Unknown')}")
        print("\n✅ Skill gap analysis successful!")
    else:
        print("\n❌ Failed to get skill gap analysis")

def test_resume_generation():
    """Test AI-powered resume suggestions"""
    print("\n" + "="*60)
    print("Testing AI-Powered Resume Generation")
    print("="*60)
    
    engine = RecommendationEngine()
    
    if not engine.openai_client:
        print("⚠️  OpenAI not available - skipping resume generation test")
        return
    
    test_profile = {
        'skills': ['Python', 'Machine Learning', 'Data Analysis', 'SQL'],
        'experience': '2 years',
        'education_level': "Bachelor's in Computer Science"
    }
    
    target_career = "Data Scientist"
    
    print(f"\nGenerating resume suggestions for: {target_career}")
    print(f"Profile: {test_profile['education_level']}, {test_profile['experience']} experience")
    
    suggestions = engine.generate_ai_resume_suggestions(test_profile, target_career)
    
    if suggestions:
        print("\n🤖 AI Resume Suggestions:")
        print("-" * 40)
        print(suggestions[:500] + "..." if len(suggestions) > 500 else suggestions)
        print("\n✅ Resume suggestions generated successfully!")
    else:
        print("\n❌ Failed to generate resume suggestions")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("AI Career Assistant - OpenAI Integration Test")
    print("="*60)
    
    # Test OpenAI connection
    if not test_openai_connection():
        print("\n⚠️  Please configure your OpenAI API key to enable AI features")
        print("The system will still work with traditional ML-based recommendations")
    
    # Test AI features
    test_ai_recommendations()
    test_skill_gap_analysis()
    test_resume_generation()
    
    print("\n" + "="*60)
    print("Test Complete!")
    print("="*60)
    
    print("\n📝 Next Steps:")
    if os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here":
        print("1. Add your OpenAI API key to the .env file")
        print("2. Restart the API server")
        print("3. Run this test again to verify AI features")
    else:
        print("1. The AI features are ready to use!")
        print("2. Access the web interface at http://localhost:5173")
        print("3. The API is available at http://localhost:8001")

if __name__ == "__main__":
    main()