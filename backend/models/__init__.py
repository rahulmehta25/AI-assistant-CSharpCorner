"""
SQLAlchemy Models for AI Career Assistant
"""

from backend.models.base import Base, get_db, engine, SessionLocal
from backend.models.user import User, CareerProfile
from backend.models.roadmap import Roadmap, RoadmapMilestone
from backend.models.job import SavedJob, Application
from backend.models.conversation import Conversation, ConversationMessage
from backend.models.assessment import SkillAssessment, SkillAssessmentQuestion
from backend.models.achievement import Achievement, UserAchievement
from backend.models.career import Career, SkillsTaxonomy
from backend.models.queue import JobQueue, AIResponseCache
from backend.models.audit import AuditLog

__all__ = [
    "Base",
    "get_db",
    "engine",
    "SessionLocal",
    "User",
    "CareerProfile",
    "Roadmap",
    "RoadmapMilestone",
    "SavedJob",
    "Application",
    "Conversation",
    "ConversationMessage",
    "SkillAssessment",
    "SkillAssessmentQuestion",
    "Achievement",
    "UserAchievement",
    "Career",
    "SkillsTaxonomy",
    "JobQueue",
    "AIResponseCache",
    "AuditLog",
]
