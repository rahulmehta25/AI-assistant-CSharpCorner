"""
Skill Assessment models
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, String, Text, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base

if TYPE_CHECKING:
    from backend.models.user import User


class SkillAssessment(Base):
    __tablename__ = "skill_assessments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    assessment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    skill_category: Mapped[Optional[str]] = mapped_column(String(100))
    target_role: Mapped[Optional[str]] = mapped_column(String(255))
    overall_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    skill_scores: Mapped[dict] = mapped_column(JSONB, default=dict)
    strengths: Mapped[dict] = mapped_column(JSONB, default=list)
    weaknesses: Mapped[dict] = mapped_column(JSONB, default=list)
    recommendations: Mapped[dict] = mapped_column(JSONB, default=list)
    gap_analysis: Mapped[dict] = mapped_column(JSONB, default=dict)
    ai_feedback: Mapped[Optional[str]] = mapped_column(Text)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="skill_assessments")
    questions: Mapped[List["SkillAssessmentQuestion"]] = relationship(
        "SkillAssessmentQuestion", back_populates="assessment", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<SkillAssessment {self.assessment_type}>"


class SkillAssessmentQuestion(Base):
    __tablename__ = "skill_assessment_questions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("skill_assessments.id", ondelete="CASCADE")
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[Optional[str]] = mapped_column(String(50))
    skill_tested: Mapped[Optional[str]] = mapped_column(String(100))
    difficulty_level: Mapped[Optional[str]] = mapped_column(String(20))
    options: Mapped[dict] = mapped_column(JSONB, default=list)
    correct_answer: Mapped[Optional[str]] = mapped_column(Text)
    user_answer: Mapped[Optional[str]] = mapped_column(Text)
    is_correct: Mapped[Optional[bool]] = mapped_column(Boolean)
    points_earned: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    time_taken_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    assessment: Mapped["SkillAssessment"] = relationship(
        "SkillAssessment", back_populates="questions"
    )

    def __repr__(self) -> str:
        return f"<SkillAssessmentQuestion {self.question_text[:50]}...>"
