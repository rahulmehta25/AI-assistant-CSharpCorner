# AI-Powered Career Recommendation Engine

## Overview
A sophisticated ML-based career recommendation system that provides personalized career suggestions for students based on their comprehensive profile including skills, interests, academic performance, and personality traits.

## Features

### 1. Hybrid Recommendation Approach
- **Collaborative Filtering**: Learns from similar student success patterns
- **Content-Based Filtering**: Matches skills and interests to career requirements
- **Personality Matching**: Uses OCEAN model for personality-career fit
- **Academic Alignment**: Considers GPA and education level requirements

### 2. Comprehensive Student Profiling
- Skills assessment with proficiency levels (1-5 scale)
- Holland Code (RIASEC) interest profiling
- OCEAN personality trait mapping
- Academic strength analysis
- Work experience consideration
- Preferred work environment matching

### 3. Explainable AI
- Clear reasons for each recommendation
- Transparency in scoring methodology
- Skill gap identification
- Personalized learning paths
- Confidence scores for recommendations

## Module Structure

### `modules/recommendation_engine.py`
Main recommendation engine with:
- `RecommendationEngine`: Core recommendation logic
- `StudentProfile`: Student data model
- `CareerRecommendation`: Recommendation output model
- Matching algorithms for skills, interests, personality, and academics
- Learning path generation
- Diversity ensuring in recommendations

### `modules/skills_assessment.py`
Comprehensive assessment system with:
- `SkillsAssessment`: Main assessment class
- Skill level evaluation (Beginner to Expert)
- Holland Code interest profiling
- OCEAN personality assessment
- Academic strength analysis
- Learning style identification

### Data Models (`data/recommendation_models/`)
- `career_embeddings.json`: Vector representations of careers
- `skill_mappings.json`: Skill-to-career mappings with weights
- `interest_profiles.json`: Interest category to career mappings

## Usage Example

```python
from modules.recommendation_engine import RecommendationEngine, StudentProfile
from modules.skills_assessment import SkillsAssessment

# Create student profile
student = StudentProfile(
    student_id="STU001",
    name="Jane Doe",
    age=20,
    education_level="undergraduate",
    gpa=3.5,
    major="Computer Science",
    interests=["technology", "problem-solving", "innovation"],
    skills={
        "Python": 4,
        "Data Analysis": 3,
        "Communication": 4,
        "Machine Learning": 2
    },
    personality_traits={
        "openness": 0.8,
        "conscientiousness": 0.7,
        "extraversion": 0.6,
        "agreeableness": 0.75,
        "neuroticism": 0.3
    },
    preferred_work_environment=["collaborative", "innovative", "remote-friendly"]
)

# Get recommendations
engine = RecommendationEngine()
recommendations = engine.recommend_careers(student, top_n=10)

# Display results
for rec in recommendations:
    print(f"{rec.title}: {rec.match_score:.1%} match")
    print(f"Reasons: {rec.reasons[0]}")
    print(f"Learning Path: {rec.learning_path[0]}")
```

## Key Algorithms

### 1. Match Score Calculation
```
match_score = 
    skill_score * 0.35 +
    interest_score * 0.25 +
    personality_score * 0.15 +
    academic_score * 0.15 +
    collaborative_score * 0.10
```

### 2. Skill Matching
- Exact match checking
- Partial match with similarity scoring
- Skill gap identification
- Proficiency level weighting

### 3. Interest Profiling (Holland Codes)
- RIASEC model implementation
- Primary, secondary, and tertiary codes
- Career family mapping
- Interest-career alignment scoring

### 4. Personality-Career Fit (OCEAN Model)
- Openness to experience
- Conscientiousness
- Extraversion
- Agreeableness
- Neuroticism (inverse scoring)

## Output Format

Each recommendation includes:
1. **Career Title and ID**
2. **Match Score** (0-100%)
3. **Confidence Level** (based on data completeness)
4. **Explanation Reasons** (why this career was recommended)
5. **Skill Gaps** (skills to develop)
6. **Learning Path** (personalized roadmap)
7. **Growth Potential** (career outlook)
8. **Salary Range** (entry-level expectations)

## Testing

Run the test suite:
```bash
python test_recommendation_engine.py
```

This will:
- Test with diverse student profiles
- Handle edge cases (minimal data, expert profiles, career changers)
- Generate sample recommendations
- Save results to `data/recommendations/`

## Integration with Career Data

The engine integrates with O*NET career data stored in `data/careers/`:
- Reads career descriptions and requirements
- Extracts skill requirements per level
- Uses growth rates and salary information
- Maps to education requirements

## Performance Metrics

- Processes 85+ careers per recommendation
- Generates top 10 recommendations in <1 second
- Handles incomplete profiles gracefully
- Ensures diversity in recommendations
- Provides explainable reasoning for each match

## Future Enhancements

1. **Machine Learning Models**
   - Train on historical student success data
   - Implement neural collaborative filtering
   - Use BERT for semantic skill matching

2. **Enhanced Data Sources**
   - Real-time job market integration
   - Industry trend analysis
   - Alumni success tracking

3. **Advanced Features**
   - Multi-objective optimization
   - Temporal career path planning
   - Geographic preference matching
   - Company culture alignment

## Dependencies

- Python 3.7+
- scikit-learn
- numpy
- Standard library (json, pathlib, dataclasses, logging)