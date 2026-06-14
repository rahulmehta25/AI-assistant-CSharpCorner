"""
Achievement and Gamification models
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, String, Text, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base

if TYPE_CHECKING:
    from backend.models.user import User


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(50))
    icon_url: Mapped[Optional[str]] = mapped_column(Text)
    points: Mapped[int] = mapped_column(Integer, default=0)
    rarity: Mapped[str] = mapped_column(String(20), default="common")
    criteria: Mapped[dict] = mapped_column(JSONB, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    user_achievements: Mapped[List["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="achievement"
    )

    def __repr__(self) -> str:
        return f"<Achievement {self.name}>"


class UserAchievement(Base):
    __tablename__ = "user_achievements"
    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="unique_user_achievement"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    achievement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("achievements.id", ondelete="CASCADE")
    )
    progress: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    unlocked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="achievements")
    achievement: Mapped["Achievement"] = relationship(
        "Achievement", back_populates="user_achievements"
    )

    def __repr__(self) -> str:
        return f"<UserAchievement user={self.user_id} achievement={self.achievement_id}>"
