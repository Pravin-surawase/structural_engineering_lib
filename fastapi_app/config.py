"""
Application Configuration.

Uses pydantic-settings for type-safe environment variable handling.
Settings can be overridden via environment variables or .env file.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    api_title: str = "Structural Engineering API"
    api_version: str = "0.21.5"
    api_prefix: str = "/api/v1"

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    reload: bool = False

    # CORS Settings
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_allow_headers: list[str] = [
        "Authorization",
        "Content-Type",
        "X-Request-ID",
        "Accept",
    ]

    # Authentication
    # WARNING: Set AUTH_ENABLED=true in production deployments
    auth_enabled: bool = False

    # Rate Limiting
    rate_limit_per_minute: int = 120  # Global API rate limit per client IP
    rate_limit_enabled: bool = True  # Set to False in tests or dev

    # Batch Processing
    max_batch_size: int = 500

    # Upload Limits
    max_upload_size_bytes: int = 10 * 1024 * 1024  # 10 MB

    # Logging
    log_level: str = "INFO"

    class Config:
        """Pydantic settings configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.

    Uses lru_cache for performance - settings are loaded once
    and reused for all subsequent calls.

    Returns:
        Settings: Application settings instance
    """
    return Settings()
