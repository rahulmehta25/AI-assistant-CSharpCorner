"""
Application configuration using Pydantic Settings.
Loads from environment variables and .env file.
"""

from functools import lru_cache
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = Field(default="AI Career Assistant API", description="Application name")
    app_version: str = Field(default="2.0.0", description="API version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="development", description="Environment (development/staging/production)")

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8001, description="Server port")
    workers: int = Field(default=1, description="Number of workers")

    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )

    # Security
    secret_key: str = Field(
        default="change-this-secret-key-in-production",
        description="Secret key for JWT signing"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiration_hours: int = Field(default=24, description="JWT token expiration in hours")
    api_key_header: str = Field(default="X-API-Key", description="API key header name")

    # API Keys
    gemini_api_key: Optional[str] = Field(default=None, description="Gemini API key")
    indeed_api_key: Optional[str] = Field(default=None, description="Indeed API key")
    linkedin_api_key: Optional[str] = Field(default=None, description="LinkedIn API key")

    # AI Model Settings
    gemini_model: str = Field(default="gemini-2.0-flash", description="Gemini model to use")
    gemini_temperature: float = Field(default=0.7, description="AI response temperature")
    gemini_max_tokens: int = Field(default=2000, description="Max tokens per response")

    # Database
    database_type: str = Field(default="sqlite", description="Database type")
    database_url: str = Field(default="sqlite:///./data/users.db", description="Database URL")

    # Redis/Cache
    redis_url: Optional[str] = Field(default=None, description="Redis URL for caching")
    cache_ttl_seconds: int = Field(default=3600, description="Default cache TTL")
    cache_roadmap_ttl: int = Field(default=86400, description="Roadmap cache TTL (24 hours)")
    cache_resume_ttl: int = Field(default=3600, description="Resume analysis cache TTL")

    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(default=100, description="Max requests per window")
    rate_limit_window_seconds: int = Field(default=60, description="Rate limit window in seconds")
    rate_limit_ai_requests: int = Field(default=20, description="AI endpoint rate limit")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json/text)")
    log_file: Optional[str] = Field(default=None, description="Log file path")

    # Data Paths
    careers_data_path: str = Field(default="data/careers", description="Path to career data")
    roadmap_templates_path: str = Field(default="data/roadmap_templates", description="Path to roadmap templates")
    education_pathways_path: str = Field(default="data/education_pathways", description="Path to education pathways")

    # Scraping
    scraping_cache_duration: int = Field(default=86400, description="Scraping cache duration")
    scraping_max_retries: int = Field(default=3, description="Max scraping retries")
    scraping_timeout: int = Field(default=30, description="Scraping timeout")

    # Conversation Memory
    conversation_max_messages: int = Field(default=50, description="Max messages to keep in memory")
    conversation_summary_threshold: int = Field(default=20, description="Messages before summarization")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("log_level", mode="before")
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            return "INFO"
        return v.upper()

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
