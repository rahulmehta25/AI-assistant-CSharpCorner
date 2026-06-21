"""
Common dependencies for FastAPI.
"""

from typing import Optional

from fastapi import Header, Request

from core.logging import set_request_id


async def get_request_id_dependency(
    request: Request,
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
) -> str:
    """
    Get or generate request ID and set in context.
    """
    request_id = set_request_id(x_request_id)
    # Store in request state for later use
    request.state.request_id = request_id
    return request_id


async def get_pagination(
    page: int = 1,
    page_size: int = 20,
) -> tuple[int, int]:
    """
    Get pagination parameters.
    Returns (offset, limit).
    """
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 20
    if page_size > 100:
        page_size = 100

    offset = (page - 1) * page_size
    return offset, page_size
