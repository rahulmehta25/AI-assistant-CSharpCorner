"""
Conversation Service - Chat history management with context windowing and summarization.
"""

import uuid
from datetime import datetime
from typing import Any, AsyncIterator, Dict, List, Optional

from core.cache import cache, CacheNamespace
from core.config import settings
from core.exceptions import NotFoundError
from core.logging import get_logger
from models.conversation import (
    ConversationHistory,
    ConversationMessage,
    ConversationRequest,
    ConversationResponse,
    ConversationSummary,
    MessageRole,
)

from .ai_service import ai_service

logger = get_logger(__name__)

try:
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


class ConversationService:
    """
    Service for managing conversations with memory management.
    Features:
    - Context windowing (keeps last N messages)
    - Conversation summarization
    - Persistent storage via cache
    """

    def __init__(self):
        self._max_messages = settings.conversation_max_messages
        self._summary_threshold = settings.conversation_summary_threshold

    def _generate_conversation_id(self) -> str:
        """Generate a unique conversation ID."""
        return f"conv_{uuid.uuid4().hex[:12]}"

    async def _get_conversation(self, conversation_id: str) -> Optional[ConversationHistory]:
        """Get conversation from cache."""
        data = await cache.get(CacheNamespace.CONVERSATION, conversation_id)
        if data:
            return ConversationHistory(**data)
        return None

    async def _save_conversation(self, conversation: ConversationHistory) -> None:
        """Save conversation to cache."""
        # Update timestamp
        conversation.updated_at = datetime.utcnow()

        await cache.set(
            CacheNamespace.CONVERSATION,
            conversation.conversation_id,
            conversation.model_dump(mode="json"),
            ttl=86400 * 7,  # Keep conversations for 7 days
        )

    async def create_conversation(
        self,
        user_id: str,
        initial_message: Optional[str] = None,
    ) -> ConversationHistory:
        """Create a new conversation."""
        conversation_id = self._generate_conversation_id()

        conversation = ConversationHistory(
            conversation_id=conversation_id,
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            messages=[],
        )

        if initial_message:
            conversation.messages.append(
                ConversationMessage(
                    role=MessageRole.USER,
                    content=initial_message,
                )
            )

        await self._save_conversation(conversation)
        logger.info(f"Created conversation {conversation_id} for user {user_id}")

        return conversation

    async def get_conversation(
        self,
        conversation_id: str,
        user_id: str,
    ) -> ConversationHistory:
        """Get an existing conversation."""
        conversation = await self._get_conversation(conversation_id)

        if not conversation:
            raise NotFoundError("Conversation", conversation_id)

        if conversation.user_id != user_id:
            raise NotFoundError("Conversation", conversation_id)

        return conversation

    async def add_message(
        self,
        conversation_id: str,
        user_id: str,
        role: MessageRole,
        content: str,
    ) -> ConversationHistory:
        """Add a message to the conversation."""
        conversation = await self.get_conversation(conversation_id, user_id)

        conversation.messages.append(
            ConversationMessage(
                role=role,
                content=content,
            )
        )

        # Check if we need to summarize
        if len(conversation.messages) >= self._summary_threshold:
            await self._maybe_summarize(conversation)

        # Apply context windowing
        if len(conversation.messages) > self._max_messages:
            conversation.messages = conversation.messages[-self._max_messages:]

        await self._save_conversation(conversation)
        return conversation

    async def _maybe_summarize(self, conversation: ConversationHistory) -> None:
        """Summarize older messages if threshold reached."""
        if len(conversation.messages) < self._summary_threshold:
            return

        # Get messages to summarize (keep last 10 for immediate context)
        messages_to_summarize = conversation.messages[:-10]
        if not messages_to_summarize:
            return

        try:
            # Build summary prompt
            prompt = ai_service.create_prompt(
                system_message="Summarize the following conversation concisely, preserving key context and decisions.",
                human_template="Conversation:\n{messages}\n\nProvide a brief summary.",
            )

            # Format messages
            formatted = "\n".join([
                f"{m.role.value}: {m.content}"
                for m in messages_to_summarize
            ])

            summary = await ai_service.invoke(prompt, {"messages": formatted})

            # Update conversation summary
            if conversation.summary:
                conversation.summary = f"{conversation.summary}\n\n{summary}"
            else:
                conversation.summary = summary

            # Keep only recent messages plus add summary as context
            conversation.messages = conversation.messages[-10:]

            logger.info(f"Summarized conversation {conversation.conversation_id}")

        except Exception as e:
            logger.warning(f"Failed to summarize conversation: {e}")
            # Continue without summarization

    def _build_langchain_messages(
        self,
        conversation: ConversationHistory,
    ) -> List:
        """Convert conversation history to LangChain messages."""
        if not LANGCHAIN_AVAILABLE:
            return []

        messages = []

        # Add summary as system context if available
        if conversation.summary:
            messages.append(SystemMessage(content=f"Previous conversation summary: {conversation.summary}"))

        # Add messages
        for msg in conversation.messages:
            if msg.role == MessageRole.USER:
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == MessageRole.ASSISTANT:
                messages.append(AIMessage(content=msg.content))
            elif msg.role == MessageRole.SYSTEM:
                messages.append(SystemMessage(content=msg.content))

        return messages

    async def chat(
        self,
        request: ConversationRequest,
        user_id: str,
    ) -> ConversationResponse:
        """
        Process a chat message and get AI response.

        Args:
            request: Chat request with message and optional conversation_id
            user_id: User ID

        Returns:
            AI response with conversation ID
        """
        # Get or create conversation
        if request.conversation_id:
            conversation = await self.get_conversation(request.conversation_id, user_id)
        else:
            conversation = await self.create_conversation(user_id)

        # Add user message
        await self.add_message(
            conversation.conversation_id,
            user_id,
            MessageRole.USER,
            request.message,
        )

        # Build prompt with history
        prompt = ai_service.get_career_advisor_prompt()

        # Get history for context
        history = self._build_langchain_messages(conversation)

        # Generate response
        try:
            response = await ai_service.invoke(
                prompt,
                {
                    "message": request.message,
                    "history": history,
                },
            )
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            response = "I apologize, but I encountered an error processing your request. Please try again."

        # Add assistant response
        await self.add_message(
            conversation.conversation_id,
            user_id,
            MessageRole.ASSISTANT,
            response,
        )

        return ConversationResponse(
            conversation_id=conversation.conversation_id,
            message=response,
            role=MessageRole.ASSISTANT,
        )

    async def stream_chat(
        self,
        request: ConversationRequest,
        user_id: str,
    ) -> AsyncIterator[str]:
        """
        Stream a chat response.

        Yields:
            Response chunks
        """
        # Get or create conversation
        if request.conversation_id:
            conversation = await self.get_conversation(request.conversation_id, user_id)
        else:
            conversation = await self.create_conversation(user_id)

        # Add user message
        await self.add_message(
            conversation.conversation_id,
            user_id,
            MessageRole.USER,
            request.message,
        )

        # Build prompt with history
        prompt = ai_service.get_career_advisor_prompt()
        history = self._build_langchain_messages(conversation)

        # Stream response
        full_response = ""
        try:
            async for chunk in ai_service.stream(
                prompt,
                {
                    "message": request.message,
                    "history": history,
                },
            ):
                full_response += chunk
                yield chunk

        except Exception as e:
            logger.error(f"Stream chat failed: {e}")
            error_msg = "I apologize, but I encountered an error. Please try again."
            full_response = error_msg
            yield error_msg

        # Save assistant response
        await self.add_message(
            conversation.conversation_id,
            user_id,
            MessageRole.ASSISTANT,
            full_response,
        )

    async def list_conversations(
        self,
        user_id: str,
        limit: int = 20,
    ) -> List[ConversationSummary]:
        """
        List conversations for a user.
        Note: In production, this would query a database.
        """
        # This is a simplified implementation
        # In production, you'd query a database index
        return []

    async def delete_conversation(
        self,
        conversation_id: str,
        user_id: str,
    ) -> bool:
        """Delete a conversation."""
        conversation = await self.get_conversation(conversation_id, user_id)
        if conversation:
            await cache.delete(CacheNamespace.CONVERSATION, conversation_id)
            logger.info(f"Deleted conversation {conversation_id}")
            return True
        return False


# Global instance
conversation_service = ConversationService()
