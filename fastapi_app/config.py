"""
Application Configuration.

Uses pydantic-settings for type-safe environment variable handling.
Settings can be overridden via environment variables or .env file.
"""

from functools import lru_cache
from pydantic import model_validator
from pydantic_settings import BaseSettings

_PRODUCTION_ENVIRONMENTS = frozenset({"production", "prod", "staging"})
_INSECURE_JWT_SECRET_MARKERS = ("change", "dev-secret")
MINIMUM_JWT_SECRET_LENGTH = 32


def is_insecure_jwt_secret(secret: str) -> bool:
    """Return whether a JWT secret is empty, short, or a known placeholder."""
    normalized = secret.strip()
    return len(normalized) < MINIMUM_JWT_SECRET_LENGTH or any(
        marker in normalized.lower() for marker in _INSECURE_JWT_SECRET_MARKERS
    )


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    api_title: str = "Structural Engineering API"
    api_version: str = "0.24.0"
    api_prefix: str = "/api/v1"

    # Server Configuration
    # Keep local/library execution private by default. Container entrypoints opt in
    # to external binding explicitly with ``--host 0.0.0.0``.
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False
    reload: bool = False

    # Deployment Profile
    # Development and tests keep their existing unauthenticated local defaults.
    # Production-like profiles must opt into authentication below.
    environment: str = "development"

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
    # Production-like environments require this to be True.
    auth_enabled: bool = False
    jwt_secret_key: str = "dev-secret-key-change-in-production"

    # Rate Limiting
    rate_limit_per_minute: int = 120  # Global API rate limit per client IP
    rate_limit_enabled: bool = True  # Set to False in tests or dev

    # Batch Processing
    max_batch_size: int = 500

    # Bounded workflow execution remains unreachable unless a local/test process
    # opts in explicitly. This is not enabled by the production compose profile.
    workflow_runner_enabled: bool = False

    # Upload Limits
    max_upload_size_bytes: int = 10 * 1024 * 1024  # 10 MB

    # Logging
    log_level: str = "INFO"

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        """Refuse public deployment profiles without usable authentication."""
        if self.environment.lower() not in _PRODUCTION_ENVIRONMENTS:
            return self

        if not self.auth_enabled:
            raise ValueError(
                "AUTH_ENABLED=true is required when ENVIRONMENT is production, prod, or staging."
            )

        if is_insecure_jwt_secret(self.jwt_secret_key):
            raise ValueError(
                "JWT_SECRET_KEY must be non-default and at least 32 characters "
                "when ENVIRONMENT is production, prod, or staging."
            )

        return self

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
