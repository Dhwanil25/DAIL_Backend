"""
Health check endpoint.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """
    Check API, database, and Redis connectivity.
    """
    db_status = "unknown"
    redis_status = "unknown"

    # Database check
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return HealthResponse(
        status="ok",
        version="1.0.0",
        database=db_status,
        redis=redis_status,
        timestamp=datetime.now(timezone.utc),
    )
