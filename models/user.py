"""
User profile models.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, EmailStr, field_validator


class UserPreferences(BaseModel):
    """User preferences for job matching and recommendations."""

    remote_work: bool = Field(default=True, description="Prefers remote work")
    hybrid_work: bool = Field(default=True, description="Open to hybrid work")
    onsite_work: bool = Field(default=True, description="Open to onsite work")
    willing_to_relocate: bool = Field(default=False, description="Willing to relocate")
    preferred_company_sizes: List[str] = Field(
        default=["startup", "mid-size", "enterprise"],
        description="Preferred company sizes"
    )
    preferred_industries: List[str] = Field(default_factory=list)


class SalaryExpectations(BaseModel):
    """Salary expectations."""

    min_salary: int = Field(..., ge=0, description="Minimum expected salary")
    max_salary: int = Field(..., ge=0, description="Maximum expected salary")
    currency: str = Field(default="USD", description="Currency code")
    period: str = Field(default="year", description="Salary period (year/month/hour)")


class WorkExperience(BaseModel):
    """Work experience entry."""

    company: str = Field(..., description="Company name")
    title: str = Field(..., description="Job title")
    start_date: str = Field(..., description="Start date (YYYY-MM)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM) or null for current")
    description: Optional[str] = Field(None, description="Role description")
    skills_used: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)


class Education(BaseModel):
    """Education entry."""

    institution: str = Field(..., description="School/university name")
    degree: str = Field(..., description="Degree type")
    field_of_study: str = Field(..., description="Major/field of study")
    graduation_year: Optional[int] = Field(None, description="Graduation year")
    gpa: Optional[float] = Field(None, ge=0, le=4.0, description="GPA (0-4 scale)")


class UserProfileCreate(BaseModel):
    """Create user profile request."""

    email: EmailStr = Field(..., description="User email")
    name: str = Field(..., min_length=1, max_length=100, description="Full name")
    password: str = Field(..., min_length=8, description="Password")


class UserProfileUpdate(BaseModel):
    """Update user profile request."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    experience_level: Optional[str] = Field(None, description="entry/junior/mid/senior/executive")
    experience_years: Optional[int] = Field(None, ge=0, le=50)
    current_role: Optional[str] = Field(None)
    target_role: Optional[str] = Field(None)
    skills: Optional[List[str]] = Field(None)
    interests: Optional[List[str]] = Field(None)
    career_goals: Optional[List[str]] = Field(None)
    education_level: Optional[str] = Field(None)
    preferred_locations: Optional[List[str]] = Field(None)
    salary_expectations: Optional[SalaryExpectations] = Field(None)
    preferences: Optional[UserPreferences] = Field(None)
    work_experience: Optional[List[WorkExperience]] = Field(None)
    education: Optional[List[Education]] = Field(None)
    certifications: Optional[List[str]] = Field(None)
    languages: Optional[List[str]] = Field(None)

    @field_validator("experience_level")
    @classmethod
    def validate_experience_level(cls, v):
        if v is not None:
            valid_levels = ["entry", "junior", "mid", "senior", "executive"]
            if v.lower() not in valid_levels:
                raise ValueError(f"experience_level must be one of {valid_levels}")
            return v.lower()
        return v


class UserProfile(BaseModel):
    """Full user profile."""

    user_id: str = Field(..., description="Unique user ID")
    email: EmailStr = Field(..., description="User email")
    name: str = Field(..., description="Full name")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    # Career info
    experience_level: str = Field(default="entry", description="Current experience level")
    experience_years: int = Field(default=0, ge=0, description="Years of experience")
    current_role: Optional[str] = Field(None, description="Current job title")
    target_role: Optional[str] = Field(None, description="Target job title")

    # Skills and interests
    skills: List[str] = Field(default_factory=list, description="Current skills")
    interests: List[str] = Field(default_factory=list, description="Professional interests")
    career_goals: List[str] = Field(default_factory=list, description="Career goals")

    # Education
    education_level: str = Field(default="High School", description="Highest education level")
    education: List[Education] = Field(default_factory=list, description="Education history")

    # Work
    work_experience: List[WorkExperience] = Field(default_factory=list)

    # Preferences
    preferred_locations: List[str] = Field(default_factory=list)
    salary_expectations: Optional[SalaryExpectations] = None
    preferences: UserPreferences = Field(default_factory=UserPreferences)

    # Additional
    certifications: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True
