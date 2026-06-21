"""
Conversation/Chat endpoints.
"""

from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from api.dependencies.auth import get_current_user, get_current_user_optional
from api.dependencies.rate_limit import rate_limit_ai
from models.auth import CurrentUser
from models.conversation import (
    ConversationHistory,
    ConversationRequest,
    ConversationResponse,
)
from services.conversation_service import conversation_service

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ConversationResponse)
async def chat(
    request: ConversationRequest,
    user: CurrentUser = Depends(get_current_user),
    _: None = Depends(rate_limit_ai),
):
    """
    Send a message to the AI career advisor.

    Features:
    - Conversation memory (maintains context across messages)
    - Context windowing (keeps recent messages)
    - Automatic summarization of long conversations

    Pass `conversation_id` to continue an existing conversation.
    """
    return await conversation_service.chat(request, user.user_id)


@router.post("/stream")
async def chat_stream(
    request: ConversationRequest,
    user: CurrentUser = Depends(get_current_user),
    _: None = Depends(rate_limit_ai),
):
    """
    Stream a response from the AI career advisor.

    Same features as /chat but returns a streaming response.
    """
    async def generate():
        async for chunk in conversation_service.stream_chat(request, user.user_id):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )


@router.get("/{conversation_id}", response_model=ConversationHistory)
async def get_conversation(
    conversation_id: str,
    user: CurrentUser = Depends(get_current_user),
):
    """
    Get a conversation history by ID.
    """
    return await conversation_service.get_conversation(conversation_id, user.user_id)


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user: CurrentUser = Depends(get_current_user),
):
    """
    Delete a conversation.
    """
    await conversation_service.delete_conversation(conversation_id, user.user_id)
    return {"deleted": True}
