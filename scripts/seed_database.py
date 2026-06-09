#!/usr/bin/env python3
"""
Database Seed Script
Populates the database with sample career data, roadmap templates, and skill taxonomy
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import uuid

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database setup
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/career_assistant"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def load_json_file(filepath: str) -> dict:
    """Load a JSON file"""
    with open(filepath, "r") as f:
        return json.load(f)


def seed_careers(session):
    """Seed careers from JSON files"""
    print("Seeding careers...")

    careers_dir = project_root / "data" / "careers"
    if not careers_dir.exists():
        print(f"  Warning: {careers_dir} not found, skipping careers")
        return

    count = 0
    for career_file in careers_dir.glob("*.json"):
        if career_file.name in ["career_summary.json", "stats.json", "onet_scrape_summary.json"]:
            continue

        try:
            career_data = load_json_file(career_file)

            # Insert into database
            session.execute(
                """
                INSERT INTO careers (
                    id, soc_code, title, description, category, cluster,
                    median_salary, growth_rate, employment_outlook,
                    education_level, experience_level, skills, tasks,
                    knowledge, abilities, interests, work_styles,
                    related_occupations, is_remote_friendly, automation_risk,
                    created_at, updated_at
                ) VALUES (
                    :id, :soc_code, :title, :description, :category, :cluster,
                    :median_salary, :growth_rate, :employment_outlook,
                    :education_level, :experience_level, :skills, :tasks,
                    :knowledge, :abilities, :interests, :work_styles,
                    :related_occupations, :is_remote_friendly, :automation_risk,
                    :created_at, :updated_at
                ) ON CONFLICT (soc_code) DO UPDATE SET
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    skills = EXCLUDED.skills,
                    updated_at = EXCLUDED.updated_at
                """,
                {
                    "id": str(uuid.uuid4()),
                    "soc_code": career_data.get("soc_code", career_data.get("id", "")),
                    "title": career_data.get("title", ""),
                    "description": career_data.get("description", ""),
                    "category": career_data.get("category", "General"),
                    "cluster": career_data.get("cluster", ""),
                    "median_salary": career_data.get("median_salary"),
                    "growth_rate": career_data.get("growth_rate", ""),
                    "employment_outlook": career_data.get("employment_outlook", ""),
                    "education_level": career_data.get("education_level", ""),
                    "experience_level": career_data.get("experience_level", ""),
                    "skills": json.dumps(career_data.get("skills", [])),
                    "tasks": json.dumps(career_data.get("tasks", [])),
                    "knowledge": json.dumps(career_data.get("knowledge", [])),
                    "abilities": json.dumps(career_data.get("abilities", [])),
                    "interests": json.dumps(career_data.get("interests", [])),
                    "work_styles": json.dumps(career_data.get("work_styles", [])),
                    "related_occupations": json.dumps(career_data.get("related_careers", [])),
                    "is_remote_friendly": career_data.get("remote_friendly", False),
                    "automation_risk": career_data.get("automation_risk", "Medium"),
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }
            )
            count += 1
        except Exception as e:
            print(f"  Error loading {career_file.name}: {e}")

    session.commit()
    print(f"  Seeded {count} careers")


def seed_skills_taxonomy(session):
    """Seed skills taxonomy"""
    print("Seeding skills taxonomy...")

    skills_data = [
        # Technical Skills
        {"name": "Python", "category": "Programming Languages", "subcategory": "Backend", "demand_level": "high"},
        {"name": "JavaScript", "category": "Programming Languages", "subcategory": "Full-Stack", "demand_level": "high"},
        {"name": "TypeScript", "category": "Programming Languages", "subcategory": "Full-Stack", "demand_level": "high"},
        {"name": "Java", "category": "Programming Languages", "subcategory": "Backend", "demand_level": "high"},
        {"name": "Go", "category": "Programming Languages", "subcategory": "Backend", "demand_level": "medium"},
        {"name": "Rust", "category": "Programming Languages", "subcategory": "Systems", "demand_level": "medium"},
        {"name": "SQL", "category": "Databases", "subcategory": "Query Languages", "demand_level": "high"},
        {"name": "PostgreSQL", "category": "Databases", "subcategory": "Relational", "demand_level": "high"},
        {"name": "MongoDB", "category": "Databases", "subcategory": "NoSQL", "demand_level": "medium"},
        {"name": "Redis", "category": "Databases", "subcategory": "Cache", "demand_level": "medium"},

        # Cloud & DevOps
        {"name": "AWS", "category": "Cloud Platforms", "subcategory": "Infrastructure", "demand_level": "high"},
        {"name": "Azure", "category": "Cloud Platforms", "subcategory": "Infrastructure", "demand_level": "high"},
        {"name": "GCP", "category": "Cloud Platforms", "subcategory": "Infrastructure", "demand_level": "medium"},
        {"name": "Docker", "category": "DevOps", "subcategory": "Containerization", "demand_level": "high"},
        {"name": "Kubernetes", "category": "DevOps", "subcategory": "Orchestration", "demand_level": "high"},
        {"name": "Terraform", "category": "DevOps", "subcategory": "IaC", "demand_level": "medium"},
        {"name": "CI/CD", "category": "DevOps", "subcategory": "Automation", "demand_level": "high"},
        {"name": "Git", "category": "DevOps", "subcategory": "Version Control", "demand_level": "high"},

        # AI/ML
        {"name": "Machine Learning", "category": "AI/ML", "subcategory": "Core", "demand_level": "high"},
        {"name": "Deep Learning", "category": "AI/ML", "subcategory": "Neural Networks", "demand_level": "high"},
        {"name": "Natural Language Processing", "category": "AI/ML", "subcategory": "NLP", "demand_level": "high"},
        {"name": "Computer Vision", "category": "AI/ML", "subcategory": "CV", "demand_level": "medium"},
        {"name": "TensorFlow", "category": "AI/ML", "subcategory": "Frameworks", "demand_level": "medium"},
        {"name": "PyTorch", "category": "AI/ML", "subcategory": "Frameworks", "demand_level": "high"},
        {"name": "LLMs", "category": "AI/ML", "subcategory": "Generative AI", "demand_level": "high"},

        # Frontend
        {"name": "React", "category": "Frontend", "subcategory": "Frameworks", "demand_level": "high"},
        {"name": "Vue.js", "category": "Frontend", "subcategory": "Frameworks", "demand_level": "medium"},
        {"name": "Angular", "category": "Frontend", "subcategory": "Frameworks", "demand_level": "medium"},
        {"name": "HTML/CSS", "category": "Frontend", "subcategory": "Core", "demand_level": "high"},
        {"name": "Tailwind CSS", "category": "Frontend", "subcategory": "Styling", "demand_level": "medium"},

        # Data
        {"name": "Data Analysis", "category": "Data", "subcategory": "Analytics", "demand_level": "high"},
        {"name": "Data Visualization", "category": "Data", "subcategory": "Visualization", "demand_level": "medium"},
        {"name": "ETL", "category": "Data", "subcategory": "Engineering", "demand_level": "medium"},
        {"name": "Apache Spark", "category": "Data", "subcategory": "Big Data", "demand_level": "medium"},
        {"name": "Pandas", "category": "Data", "subcategory": "Libraries", "demand_level": "high"},

        # Soft Skills
        {"name": "Communication", "category": "Soft Skills", "subcategory": "Interpersonal", "demand_level": "high"},
        {"name": "Problem Solving", "category": "Soft Skills", "subcategory": "Cognitive", "demand_level": "high"},
        {"name": "Leadership", "category": "Soft Skills", "subcategory": "Management", "demand_level": "high"},
        {"name": "Teamwork", "category": "Soft Skills", "subcategory": "Interpersonal", "demand_level": "high"},
        {"name": "Critical Thinking", "category": "Soft Skills", "subcategory": "Cognitive", "demand_level": "high"},
        {"name": "Project Management", "category": "Soft Skills", "subcategory": "Management", "demand_level": "medium"},
        {"name": "Agile/Scrum", "category": "Soft Skills", "subcategory": "Methodology", "demand_level": "high"},
    ]

    count = 0
    for skill in skills_data:
        try:
            session.execute(
                """
                INSERT INTO skills_taxonomy (id, name, category, subcategory, demand_level, created_at)
                VALUES (:id, :name, :category, :subcategory, :demand_level, :created_at)
                ON CONFLICT DO NOTHING
                """,
                {
                    "id": str(uuid.uuid4()),
                    "name": skill["name"],
                    "category": skill["category"],
                    "subcategory": skill["subcategory"],
                    "demand_level": skill["demand_level"],
                    "created_at": datetime.utcnow(),
                }
            )
            count += 1
        except Exception as e:
            print(f"  Error inserting skill {skill['name']}: {e}")

    session.commit()
    print(f"  Seeded {count} skills")


def seed_achievements(session):
    """Seed achievements for gamification"""
    print("Seeding achievements...")

    achievements = [
        {
            "name": "profile_complete",
            "display_name": "Profile Pioneer",
            "description": "Complete your career profile",
            "category": "onboarding",
            "points": 50,
            "rarity": "common",
        },
        {
            "name": "first_roadmap",
            "display_name": "Pathfinder",
            "description": "Create your first career roadmap",
            "category": "roadmap",
            "points": 100,
            "rarity": "common",
        },
        {
            "name": "skill_assessment",
            "display_name": "Self-Aware",
            "description": "Complete a skill assessment",
            "category": "assessment",
            "points": 75,
            "rarity": "common",
        },
        {
            "name": "ten_applications",
            "display_name": "Job Hunter",
            "description": "Apply to 10 jobs through the platform",
            "category": "applications",
            "points": 150,
            "rarity": "uncommon",
        },
        {
            "name": "first_interview",
            "display_name": "Interview Ready",
            "description": "Get your first interview",
            "category": "applications",
            "points": 200,
            "rarity": "uncommon",
        },
        {
            "name": "milestone_complete",
            "display_name": "Milestone Master",
            "description": "Complete 5 roadmap milestones",
            "category": "roadmap",
            "points": 250,
            "rarity": "uncommon",
        },
        {
            "name": "skill_master",
            "display_name": "Skill Master",
            "description": "Achieve expert level in 3 skills",
            "category": "skills",
            "points": 500,
            "rarity": "rare",
        },
        {
            "name": "career_changer",
            "display_name": "Career Transformer",
            "description": "Successfully transition to a new career",
            "category": "career",
            "points": 1000,
            "rarity": "epic",
        },
        {
            "name": "mentor",
            "display_name": "Career Mentor",
            "description": "Help 5 other users with their career journey",
            "category": "community",
            "points": 750,
            "rarity": "rare",
        },
        {
            "name": "early_adopter",
            "display_name": "Early Adopter",
            "description": "Join during the beta period",
            "category": "special",
            "points": 100,
            "rarity": "legendary",
        },
    ]

    count = 0
    for achievement in achievements:
        try:
            session.execute(
                """
                INSERT INTO achievements (
                    id, name, display_name, description, category,
                    points, rarity, is_active, created_at
                ) VALUES (
                    :id, :name, :display_name, :description, :category,
                    :points, :rarity, :is_active, :created_at
                ) ON CONFLICT (name) DO UPDATE SET
                    display_name = EXCLUDED.display_name,
                    description = EXCLUDED.description,
                    points = EXCLUDED.points
                """,
                {
                    "id": str(uuid.uuid4()),
                    "name": achievement["name"],
                    "display_name": achievement["display_name"],
                    "description": achievement["description"],
                    "category": achievement["category"],
                    "points": achievement["points"],
                    "rarity": achievement["rarity"],
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                }
            )
            count += 1
        except Exception as e:
            print(f"  Error inserting achievement {achievement['name']}: {e}")

    session.commit()
    print(f"  Seeded {count} achievements")


def seed_demo_user(session):
    """Seed a demo user for testing"""
    print("Seeding demo user...")

    demo_user_id = str(uuid.uuid4())

    try:
        # Create user
        session.execute(
            """
            INSERT INTO users (id, email, username, full_name, is_active, is_verified, created_at)
            VALUES (:id, :email, :username, :full_name, :is_active, :is_verified, :created_at)
            ON CONFLICT (email) DO NOTHING
            """,
            {
                "id": demo_user_id,
                "email": "demo@example.com",
                "username": "demo_user",
                "full_name": "Demo User",
                "is_active": True,
                "is_verified": True,
                "created_at": datetime.utcnow(),
            }
        )

        # Create profile
        session.execute(
            """
            INSERT INTO career_profiles (
                id, user_id, current_role, target_role, experience_years,
                education_level, location, skills, interests, career_goals, created_at
            ) VALUES (
                :id, :user_id, :current_role, :target_role, :experience_years,
                :education_level, :location, :skills, :interests, :career_goals, :created_at
            ) ON CONFLICT (user_id) DO NOTHING
            """,
            {
                "id": str(uuid.uuid4()),
                "user_id": demo_user_id,
                "current_role": "Junior Software Developer",
                "target_role": "Senior Software Engineer",
                "experience_years": 2,
                "education_level": "Bachelor's Degree",
                "location": "San Francisco, CA",
                "skills": json.dumps(["Python", "JavaScript", "React", "SQL"]),
                "interests": json.dumps(["AI/ML", "Cloud Computing", "System Design"]),
                "career_goals": json.dumps(["Lead a team", "Work on impactful products"]),
                "created_at": datetime.utcnow(),
            }
        )

        session.commit()
        print("  Demo user created (demo@example.com)")

    except Exception as e:
        print(f"  Error creating demo user: {e}")


def main():
    """Main seed function"""
    print("=" * 50)
    print("AI Career Assistant - Database Seeder")
    print("=" * 50)
    print(f"Database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
    print()

    session = SessionLocal()

    try:
        seed_careers(session)
        seed_skills_taxonomy(session)
        seed_achievements(session)
        seed_demo_user(session)

        print()
        print("=" * 50)
        print("Database seeding complete!")
        print("=" * 50)

    except Exception as e:
        print(f"Error during seeding: {e}")
        session.rollback()
        sys.exit(1)

    finally:
        session.close()


if __name__ == "__main__":
    main()
