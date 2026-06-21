"""
FastAPI middleware for logging, error handling, and request tracking.
"""

import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import settings
from core.exceptions import AppException
from core.logging import get_logger, set_request_id, get_request_id

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging requests and setting request IDs.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Set request ID
        request_id = request.headers.get("X-Request-ID")
        request_id = set_request_id(request_id)
        request.state.request_id = request_id

        # Log request start
        start_time = time.time()

        logger.info(
            f"Request started",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else "unknown",
            }
        )

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log request completion
        logger.info(
            f"Request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            }
        )

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Set up exception handlers for the application.
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        """Handle custom application exceptions."""
        request_id = getattr(request.state, "request_id", None) or get_request_id()

        logger.warning(
            f"Application error: {exc.message}",
            extra={
                "error_code": exc.error_code,
                "status_code": exc.status_code,
                "details": exc.details,
            }
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "error_code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
                "request_id": request_id,
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions."""
        request_id = getattr(request.state, "request_id", None) or get_request_id()

        logger.error(
            f"Unhandled exception: {str(exc)}",
            exc_info=True,
        )

        # Don't expose internal errors in production
        if settings.is_production:
            message = "An internal error occurred"
            details = {}
        else:
            message = str(exc)
            details = {"exception_type": type(exc).__name__}

        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "error_code": "INTERNAL_ERROR",
                "message": message,
                "details": details,
                "request_id": request_id,
            },
        )
