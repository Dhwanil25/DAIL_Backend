"""
API Dependencies — shared FastAPI dependencies for injection.
"""

from typing import Optional

import redis.asyncio as aioredis
from fastapi import Depends, Header, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings, Settings
from app.database import get_db


async def get_settings_dep() -> Settings:
    """Inject application settings."""
    return get_settings()


async def get_redis(request: Request) -> Optional[aioredis.Redis]:
    """Inject Redis client from app state."""
    return getattr(request.app.state, "redis", None)


async def get_current_user(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> Optional[str]:
    """
    Extract the current user/API key from request headers.
    Returns None for public endpoints; raises 401 for protected ones.
    """
    # For now, API keys are optional — public read access
    return x_api_key


async def require_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
) -> str:
    """Require an API key for write operations."""
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required. Pass it in the X-API-Key header.",
        )
    return x_api_key


class PaginationDep:
    """Reusable pagination dependency."""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size
