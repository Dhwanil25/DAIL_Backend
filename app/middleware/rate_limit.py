"""
Rate Limiting Middleware

Simple Redis-based sliding window rate limiter.
Falls back to no-op if Redis is unavailable.
"""

import time
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import get_settings

settings = get_settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-IP rate limiting using Redis sliding window."""

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path.endswith("/health"):
            return await call_next(request)

        redis = getattr(request.app.state, "redis", None)
        if not redis:
            return await call_next(request)

        # Get client identifier
        client_ip = request.client.host if request.client else "unknown"
        api_key = request.headers.get("X-API-Key", "")
        identifier = api_key or client_ip

        try:
            # Check per-minute limit
            minute_key = f"rl:min:{identifier}:{int(time.time()) // 60}"
            count = await redis.incr(minute_key)
            if count == 1:
                await redis.expire(minute_key, 60)

            if count > settings.RATE_LIMIT_PER_MINUTE:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "detail": f"Maximum {settings.RATE_LIMIT_PER_MINUTE} requests per minute",
                        "retry_after": 60,
                    },
                    headers={"Retry-After": "60"},
                )

            # Check per-hour limit
            hour_key = f"rl:hr:{identifier}:{int(time.time()) // 3600}"
            hour_count = await redis.incr(hour_key)
            if hour_count == 1:
                await redis.expire(hour_key, 3600)

            if hour_count > settings.RATE_LIMIT_PER_HOUR:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "detail": f"Maximum {settings.RATE_LIMIT_PER_HOUR} requests per hour",
                        "retry_after": 3600,
                    },
                    headers={"Retry-After": "3600"},
                )

            # Add rate limit headers to response
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_PER_MINUTE)
            response.headers["X-RateLimit-Remaining"] = str(
                max(0, settings.RATE_LIMIT_PER_MINUTE - count)
            )
            return response

        except Exception:
            # If Redis fails, don't block the request
            return await call_next(request)
