"""
Common response models used across the API.
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


class SuccessResponse(BaseModel):
    """Generic success response."""

    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error: bool = True
    error_code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional error details")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: List[T]
    total: int = Field(..., description="Total number of items")
    page: int = Field(default=1, ge=1, description="Current page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    pages: int = Field(..., description="Total number of pages")

    @classmethod
    def create(cls, items: List[T], total: int, page: int = 1, page_size: int = 20):
        pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(items=items, total=total, page=page, page_size=page_size, pages=pages)


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status (healthy/unhealthy)")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    checks: Dict[str, bool] = Field(default_factory=dict, description="Individual service checks")
    environment: str = Field(..., description="Current environment")


class CacheInfo(BaseModel):
    """Cache information."""

    key: str
    cached: bool
    ttl_remaining: Optional[int] = None
    cached_at: Optional[datetime] = None


class RateLimitInfo(BaseModel):
    """Rate limit information returned in headers."""

    limit: int = Field(..., description="Request limit")
    remaining: int = Field(..., description="Remaining requests")
    reset_at: datetime = Field(..., description="When the limit resets")
