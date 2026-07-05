"""
Career and Skills Taxonomy models (reference data)
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class Career(Base):
    __tablename__ = "careers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    soc_code: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(100))
    cluster: Mapped[Optional[str]] = mapped_column(String(100))
    median_salary: Mapped[Optional[int]] = mapped_column(Integer)
    salary_range_min: Mapped[Optional[int]] = mapped_column(Integer)
    salary_range_max: Mapped[Optional[int]] = mapped_column(Integer)
    growth_rate: Mapped[Optional[str]] = mapped_column(String(50))
    employment_outlook: Mapped[Optional[str]] = mapped_column(String(100))
    education_level: Mapped[Optional[str]] = mapped_column(String(100))
    experience_level: Mapped[Optional[str]] = mapped_column(String(100))
    skills: Mapped[dict] = mapped_column(JSONB, default=list)
    tasks: Mapped[dict] = mapped_column(JSONB, default=list)
    knowledge: Mapped[dict] = mapped_column(JSONB, default=list)
    abilities: Mapped[dict] = mapped_column(JSONB, default=list)
    interests: Mapped[dict] = mapped_column(JSONB, default=list)
    work_styles: Mapped[dict] = mapped_column(JSONB, default=list)
    work_environment: Mapped[dict] = mapped_column(JSONB, default=list)
    related_occupations: Mapped[dict] = mapped_column(JSONB, default=list)
    certifications: Mapped[dict] = mapped_column(JSONB, default=list)
    tools_technology: Mapped[dict] = mapped_column(JSONB, default=list)
    is_remote_friendly: Mapped[bool] = mapped_column(Boolean, default=False)
    automation_risk: Mapped[Optional[str]] = mapped_column(String(20))
    bright_outlook: Mapped[bool] = mapped_column(Boolean, default=False)
    green_economy: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<Career {self.title}>"


class SkillsTaxonomy(Base):
    __tablename__ = "skills_taxonomy"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100))
    subcategory: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    related_skills: Mapped[dict] = mapped_column(JSONB, default=list)
    demand_level: Mapped[Optional[str]] = mapped_column(String(20))
    learning_resources: Mapped[dict] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<SkillsTaxonomy {self.name}>"
