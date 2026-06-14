"""
Conversation and Message models for AI chat history
"""

import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base

if TYPE_CHECKING:
    from backend.models.user import User


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE")
    )
    title: Mapped[Optional[str]] = mapped_column(String(255))
    conversation_type: Mapped[str] = mapped_column(String(50), default="general")
    context: Mapped[dict] = mapped_column(JSONB, default=dict)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    message_count: Mapped[int] = mapped_column(Integer, default=0)
    last_message_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="conversations")
    messages: Mapped[List["ConversationMessage"]] = relationship(
        "ConversationMessage", back_populates="conversation", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Conversation {self.id}>"


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE")
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer)
    model_used: Mapped[Optional[str]] = mapped_column(String(100))
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    # Relationships
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages"
    )

    def __repr__(self) -> str:
        return f"<ConversationMessage {self.role}: {self.content[:50]}...>"
