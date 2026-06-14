"""
Structured logging with request ID tracking.
"""

import json
import logging
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Dict, Optional

from .config import settings

# Context variable for request ID
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def get_request_id() -> Optional[str]:
    """Get the current request ID from context."""
    return request_id_var.get()


def set_request_id(request_id: Optional[str] = None) -> str:
    """Set request ID in context, generating one if not provided."""
    if request_id is None:
        request_id = str(uuid.uuid4())[:8]
    request_id_var.set(request_id)
    return request_id


class JSONFormatter(logging.Formatter):
    """JSON log formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add request ID if available
        request_id = get_request_id()
        if request_id:
            log_data["request_id"] = request_id

        # Add location info
        log_data["location"] = {
            "file": record.filename,
            "line": record.lineno,
            "function": record.funcName,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in (
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "pathname", "process", "processName", "relativeCreated",
                "stack_info", "exc_info", "exc_text", "message",
            ):
                log_data[key] = value

        return json.dumps(log_data, default=str)


class TextFormatter(logging.Formatter):
    """Human-readable text formatter for development."""

    def format(self, record: logging.LogRecord) -> str:
        request_id = get_request_id()
        request_id_str = f"[{request_id}] " if request_id else ""

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        base_format = f"{timestamp} | {record.levelname:8} | {request_id_str}{record.name} | {record.getMessage()}"

        if record.exc_info:
            base_format += f"\n{self.formatException(record.exc_info)}"

        return base_format


def setup_logging() -> None:
    """Configure application logging."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level))

    # Clear existing handlers
    root_logger.handlers.clear()

    # Choose formatter based on settings
    if settings.log_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler if configured
    if settings.log_file:
        file_handler = logging.FileHandler(settings.log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that includes request ID in all log messages."""

    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        request_id = get_request_id()
        if request_id:
            kwargs.setdefault("extra", {})["request_id"] = request_id
        return msg, kwargs


def get_context_logger(name: str) -> LoggerAdapter:
    """Get a logger adapter that includes request context."""
    logger = logging.getLogger(name)
    return LoggerAdapter(logger, {})
