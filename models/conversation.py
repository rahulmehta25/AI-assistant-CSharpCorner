"""
Conversation and chat models.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Message roles in conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationMessage(BaseModel):
    """Single conversation message."""

    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConversationRequest(BaseModel):
    """Request for conversation/chat."""

    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    stream: bool = Field(default=False, description="Stream the response")


class ConversationResponse(BaseModel):
    """Conversation response."""

    conversation_id: str
    message: str
    role: MessageRole = Field(default=MessageRole.ASSISTANT)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Context
    context_used: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)

    # Metadata
    tokens_used: Optional[int] = None
    model: Optional[str] = None


class ConversationHistory(BaseModel):
    """Full conversation history."""

    conversation_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    messages: List[ConversationMessage]
    summary: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConversationSummary(BaseModel):
    """Conversation summary for listing."""

    conversation_id: str
    title: Optional[str] = None
    preview: str = Field(..., description="First few words of conversation")
    message_count: int
    created_at: datetime
    updated_at: datetime


class ConversationListResponse(BaseModel):
    """List of conversations."""

    conversations: List[ConversationSummary]
    total: int
    page: int
    page_size: int


class StreamChunk(BaseModel):
    """Streaming response chunk."""

    conversation_id: str
    chunk: str
    done: bool = False
    metadata: Optional[Dict[str, Any]] = None
