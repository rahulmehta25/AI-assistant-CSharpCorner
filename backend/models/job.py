"""
Job and Application models
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, String, Text, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base

if TYPE_CHECKING:
    from backend.models.user import User


class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    external_job_id: Mapped[Optional[str]] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255))
    job_url: Mapped[Optional[str]] = mapped_column(Text)
    salary_min: Mapped[Optional[int]] = mapped_column(Integer)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer)
    job_type: Mapped[Optional[str]] = mapped_column(String(50))
    experience_level: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)
    requirements: Mapped[dict] = mapped_column(JSONB, default=list)
    skills_required: Mapped[dict] = mapped_column(JSONB, default=list)
    match_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    match_details: Mapped[dict] = mapped_column(JSONB, default=dict)
    source: Mapped[Optional[str]] = mapped_column(String(100))
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False)
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    tags: Mapped[dict] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="saved_jobs")
    applications: Mapped[list["Application"]] = relationship(
        "Application", back_populates="saved_job"
    )

    def __repr__(self) -> str:
        return f"<SavedJob {self.title} at {self.company}>"


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    saved_job_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("saved_jobs.id", ondelete="SET NULL")
    )
    job_title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    job_url: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    response_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    interview_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    offer_amount: Mapped[Optional[int]] = mapped_column(Integer)
    resume_version: Mapped[Optional[str]] = mapped_column(Text)
    cover_letter: Mapped[Optional[str]] = mapped_column(Text)
    custom_responses: Mapped[dict] = mapped_column(JSONB, default=dict)
    interview_notes: Mapped[Optional[str]] = mapped_column(Text)
    feedback: Mapped[Optional[str]] = mapped_column(Text)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)
    follow_up_dates: Mapped[dict] = mapped_column(JSONB, default=list)
    contacts: Mapped[dict] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="applications")
    saved_job: Mapped[Optional["SavedJob"]] = relationship(
        "SavedJob", back_populates="applications"
    )

    def __repr__(self) -> str:
        return f"<Application {self.job_title} at {self.company}>"
