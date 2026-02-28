"""
DAIL Backend - Application Configuration

Centralized settings management using Pydantic Settings.
All configuration is loaded from environment variables or .env file.
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────
    APP_NAME: str = "DAIL"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-to-a-random-secret-key"
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    # ── PostgreSQL ───────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://dail:dail_password@localhost:5432/dail_db"
    DATABASE_URL_SYNC: str = "postgresql://dail:dail_password@localhost:5432/dail_db"
    POSTGRES_USER: str = "dail"
    POSTGRES_PASSWORD: str = "dail_password"
    POSTGRES_DB: str = "dail_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    # ── Redis ────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600

    # ── Celery ───────────────────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ── CourtListener API ────────────────────────────────────────────────
    COURTLISTENER_API_TOKEN: str = ""
    COURTLISTENER_BASE_URL: str = "https://www.courtlistener.com/api/rest/v4"
    COURTLISTENER_RATE_LIMIT: int = 5000

    # ── Sentry ───────────────────────────────────────────────────────────
    SENTRY_DSN: Optional[str] = None

    # ── Rate Limiting ────────────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # ── Pagination ───────────────────────────────────────────────────────
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # ── Logging ──────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
