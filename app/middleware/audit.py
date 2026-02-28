"""
Audit Middleware

Logs all API requests with timing, user context, and request IDs.
Provides correlation IDs for tracing requests across services.
"""

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

import structlog

logger = structlog.get_logger()


class AuditMiddleware(BaseHTTPMiddleware):
    """Log every API request with timing and context."""

    async def dispatch(self, request: Request, call_next):
        # Generate request ID for correlation
        request_id = str(uuid.uuid4())[:8]

        # Attach to request state for downstream use
        request.state.request_id = request_id

        # Extract user context
        api_key = request.headers.get("X-API-Key", "anonymous")
        client_ip = request.client.host if request.client else "unknown"

        start_time = time.perf_counter()

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log request
            logger.info(
                "api_request",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
                client_ip=client_ip,
                api_key=api_key[:8] + "..." if len(api_key) > 8 else api_key,
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "api_request_error",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                error=str(exc),
                duration_ms=round(duration_ms, 2),
                client_ip=client_ip,
            )
            raise
