"""
Pydantic v2 models for API requests and responses.
"""

from .user import (
    UserProfile,
    UserProfileCreate,
    UserProfileUpdate,
    UserPreferences,
)
from .career import (
    Career,
    CareerSummary,
    CareerSearchQuery,
    CareerSearchResult,
    CareerRoadmapRequest,
    CareerRoadmap,
    Milestone,
    Certification,
    Project,
    SalaryProgression,
    AlternativePath,
)
from .job import (
    JobPosting,
    JobSearchQuery,
    JobSearchResult,
    JobMatchScore,
    JobMatchRequest,
)
from .resume import (
    ResumeAnalysisRequest,
    ResumeAnalysisResult,
    ResumeSuggestion,
    CoverLetterRequest,
    CoverLetterResult,
)
from .skills import (
    SkillGapRequest,
    SkillGapAnalysis,
    SkillAssessment,
    SkillRecommendation,
)
from .interview import (
    InterviewPrepRequest,
    InterviewPrepResult,
    InterviewQuestion,
)
from .conversation import (
    ConversationMessage,
    ConversationRequest,
    ConversationResponse,
    ConversationHistory,
)
from .student import (
    StudentLevel,
    StudentPathwayRequest,
    StudentPathway,
    PathwayMilestone,
    CourseRecommendation,
    ActivityRecommendation,
)
from .common import (
    PaginatedResponse,
    HealthResponse,
    ErrorResponse,
    SuccessResponse,
)
from .auth import (
    TokenRequest,
    TokenResponse,
    APIKeyCreate,
    APIKeyResponse,
)

__all__ = [
    # User
    "UserProfile",
    "UserProfileCreate",
    "UserProfileUpdate",
    "UserPreferences",
    # Career
    "Career",
    "CareerSummary",
    "CareerSearchQuery",
    "CareerSearchResult",
    "CareerRoadmapRequest",
    "CareerRoadmap",
    "Milestone",
    "Certification",
    "Project",
    "SalaryProgression",
    "AlternativePath",
    # Job
    "JobPosting",
    "JobSearchQuery",
    "JobSearchResult",
    "JobMatchScore",
    "JobMatchRequest",
    # Resume
    "ResumeAnalysisRequest",
    "ResumeAnalysisResult",
    "ResumeSuggestion",
    "CoverLetterRequest",
    "CoverLetterResult",
    # Skills
    "SkillGapRequest",
    "SkillGapAnalysis",
    "SkillAssessment",
    "SkillRecommendation",
    # Interview
    "InterviewPrepRequest",
    "InterviewPrepResult",
    "InterviewQuestion",
    # Conversation
    "ConversationMessage",
    "ConversationRequest",
    "ConversationResponse",
    "ConversationHistory",
    # Student
    "StudentLevel",
    "StudentPathwayRequest",
    "StudentPathway",
    "PathwayMilestone",
    "CourseRecommendation",
    "ActivityRecommendation",
    # Common
    "PaginatedResponse",
    "HealthResponse",
    "ErrorResponse",
    "SuccessResponse",
    # Auth
    "TokenRequest",
    "TokenResponse",
    "APIKeyCreate",
    "APIKeyResponse",
]
