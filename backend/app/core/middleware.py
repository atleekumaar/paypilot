"""Request correlation ID and structured observability middleware."""

import contextvars
import logging
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("paypilot.access")

# Context variable for correlation ID
request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")


def get_current_request_id() -> str:
    """Return the active request ID or empty string."""
    return request_id_ctx.get()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware enforcing request correlation IDs across the application."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract or generate request ID
        req_id = request.headers.get("X-Request-ID") or f"req_{uuid.uuid4().hex[:12]}"
        token = request_id_ctx.set(req_id)

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000
            response.headers["X-Request-ID"] = req_id
            
            # Log structured access info
            logger.info(
                f"{request.method} {request.url.path} - {response.status_code} ({duration_ms:.1f}ms) [request_id={req_id}]"
            )
            return response
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"{request.method} {request.url.path} - Unhandled exception: {exc} ({duration_ms:.1f}ms) [request_id={req_id}]"
            )
            raise
        finally:
            request_id_ctx.reset(token)

