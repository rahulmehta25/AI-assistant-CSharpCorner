"""
User and Career Profile models
"""

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    avatar_url: Mapped[Optional[str]] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    auth_provider: Mapped[str] = mapped_column(String(50), default="local")
    auth_provider_id: Mapped[Optional[str]] = mapped_column(String(255))
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    career_profile: Mapped[Optional["CareerProfile"]] = relationship(
        "CareerProfile", back_populates="user", uselist=False
    )
    roadmaps: Mapped[List["Roadmap"]] = relationship(
        "Roadmap", back_populates="user", cascade="all, delete-orphan"
    )
    saved_jobs: Mapped[List["SavedJob"]] = relationship(
        "SavedJob", back_populates="user", cascade="all, delete-orphan"
    )
    applications: Mapped[List["Application"]] = relationship(
        "Application", back_populates="user", cascade="all, delete-orphan"
    )
    conversations: Mapped[List["Conversation"]] = relationship(
        "Conversation", back_populates="user", cascade="all, delete-orphan"
    )
    skill_assessments: Mapped[List["SkillAssessment"]] = relationship(
        "SkillAssessment", back_populates="user", cascade="all, delete-orphan"
    )
    achievements: Mapped[List["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class CareerProfile(Base):
    __tablename__ = "career_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    current_role: Mapped[Optional[str]] = mapped_column(String(255))
    target_role: Mapped[Optional[str]] = mapped_column(String(255))
    experience_years: Mapped[int] = mapped_column(Integer, default=0)
    education_level: Mapped[Optional[str]] = mapped_column(String(100))
    location: Mapped[Optional[str]] = mapped_column(String(255))
    remote_preference: Mapped[str] = mapped_column(String(50), default="hybrid")
    salary_expectation_min: Mapped[Optional[int]] = mapped_column(Integer)
    salary_expectation_max: Mapped[Optional[int]] = mapped_column(Integer)
    bio: Mapped[Optional[str]] = mapped_column(Text)
    linkedin_url: Mapped[Optional[str]] = mapped_column(Text)
    github_url: Mapped[Optional[str]] = mapped_column(Text)
    portfolio_url: Mapped[Optional[str]] = mapped_column(Text)
    resume_url: Mapped[Optional[str]] = mapped_column(Text)
    skills: Mapped[dict] = mapped_column(JSONB, default=list)
    interests: Mapped[dict] = mapped_column(JSONB, default=list)
    career_goals: Mapped[dict] = mapped_column(JSONB, default=list)
    work_preferences: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="career_profile")

    def __repr__(self) -> str:
        return f"<CareerProfile user_id={self.user_id}>"


# Import for type hints (avoid circular imports)
from backend.models.roadmap import Roadmap
from backend.models.job import SavedJob, Application
from backend.models.conversation import Conversation
from backend.models.assessment import SkillAssessment
from backend.models.achievement import UserAchievement
