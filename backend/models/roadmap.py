"""
Roadmap and Milestone models
"""

import uuid
from datetime import datetime, date
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Date, Integer, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base

if TYPE_CHECKING:
    from backend.models.user import User


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    target_role: Mapped[Optional[str]] = mapped_column(String(255))
    target_timeline: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="active")
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0)
    current_phase: Mapped[int] = mapped_column(Integer, default=1)
    total_phases: Mapped[int] = mapped_column(Integer, default=1)
    learning_path: Mapped[dict] = mapped_column(JSONB, default=list)
    milestones: Mapped[dict] = mapped_column(JSONB, default=list)
    gap_analysis: Mapped[dict] = mapped_column(JSONB, default=dict)
    ai_recommendations: Mapped[dict] = mapped_column(JSONB, default=list)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    target_completion_date: Mapped[Optional[date]] = mapped_column(Date)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="roadmaps")
    milestone_items: Mapped[List["RoadmapMilestone"]] = relationship(
        "RoadmapMilestone", back_populates="roadmap", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Roadmap {self.title}>"


class RoadmapMilestone(Base):
    __tablename__ = "roadmap_milestones"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    roadmap_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roadmaps.id", ondelete="CASCADE")
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    phase: Mapped[int] = mapped_column(Integer, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False)
    milestone_type: Mapped[Optional[str]] = mapped_column(String(50))
    target_date: Mapped[Optional[date]] = mapped_column(Date)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(50), default="pending")
    skills_required: Mapped[dict] = mapped_column(JSONB, default=list)
    resources: Mapped[dict] = mapped_column(JSONB, default=list)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    roadmap: Mapped["Roadmap"] = relationship("Roadmap", back_populates="milestone_items")

    def __repr__(self) -> str:
        return f"<RoadmapMilestone {self.title}>"
