"""
API Routes module.
"""

from .careers import router as careers_router
from .jobs import router as jobs_router
from .resume import router as resume_router
from .interview import router as interview_router
from .conversation import router as conversation_router
from .student import router as student_router
from .auth import router as auth_router
from .health import router as health_router

__all__ = [
    "careers_router",
    "jobs_router",
    "resume_router",
    "interview_router",
    "conversation_router",
    "student_router",
    "auth_router",
    "health_router",
]
