#!/usr/bin/env python3
"""
Run the AI Career Assistant API server.
"""

import uvicorn

from core.config import settings


def main():
    """Run the API server."""
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Environment: {settings.environment}")
    print(f"Server: http://{settings.host}:{settings.port}")
    print(f"Docs: http://{settings.host}:{settings.port}/docs")
    print()

    uvicorn.run(
        "api.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=settings.workers if not settings.debug else 1,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
