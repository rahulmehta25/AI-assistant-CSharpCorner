"""
FastAPI Application - Main entry point.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse

from core.config import settings
from core.logging import setup_logging, get_logger

from .middleware import RequestLoggingMiddleware, setup_exception_handlers
from .routes import (
    auth_router,
    careers_router,
    conversation_router,
    health_router,
    interview_router,
    jobs_router,
    resume_router,
    student_router,
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    setup_logging()
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

    yield

    # Shutdown
    logger.info("Shutting down application")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        description="""
# AI Career Assistant API

A production-grade API for AI-powered career development.

## Features

- **Career Roadmaps**: Generate personalized 5-10 year career roadmaps
- **Job Search & Matching**: Search jobs and get AI-powered match scores
- **Resume Analysis**: ATS compatibility scoring and improvement suggestions
- **Cover Letter Generation**: AI-generated personalized cover letters
- **Interview Preparation**: Custom interview questions and preparation guides
- **Skill Gap Analysis**: Identify skills to develop for career transitions
- **AI Chat**: Conversational career advisor with memory

## Authentication

The API supports two authentication methods:

1. **JWT Bearer Token**: Use `/auth/token` to obtain a token
2. **API Key**: Use the `X-API-Key` header

## Rate Limiting

- Standard endpoints: 100 requests per minute
- AI endpoints: 20 requests per minute

Rate limit headers are included in responses:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`
        """,
        version=settings.app_version,
        docs_url=None,  # Custom docs
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
    )

    # Request logging middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Exception handlers
    setup_exception_handlers(app)

    # Routes
    app.include_router(health_router)
    app.include_router(auth_router, prefix="/api")
    app.include_router(careers_router, prefix="/api")
    app.include_router(jobs_router, prefix="/api")
    app.include_router(resume_router, prefix="/api")
    app.include_router(interview_router, prefix="/api")
    app.include_router(conversation_router, prefix="/api")
    app.include_router(student_router, prefix="/api")

    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """API root - returns basic info."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "active",
            "docs": "/docs",
        }

    # Custom Swagger UI
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{settings.app_name} - Docs",
            swagger_ui_parameters={
                "persistAuthorization": True,
                "displayRequestDuration": True,
            },
        )

    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=settings.workers if not settings.debug else 1,
    )
