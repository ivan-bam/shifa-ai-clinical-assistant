import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from backend.observability.logging_config import get_logger

logger = get_logger("shifa.request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs every HTTP request with a short request ID and how long it took."""

    async def dispatch(self, request: Request, call_next):
        request_id = uuid.uuid4().hex[:8]
        request.state.request_id = request_id
        start = time.perf_counter()

        logger.info("%s | --> %s %s", request_id, request.method, request.url.path)

        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = (time.perf_counter() - start) * 1000
            logger.exception(
                "%s | !!! %s %s failed after %.0fms",
                request_id, request.method, request.url.path, elapsed_ms,
            )
            raise

        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s | <-- %s %s | %d | %.0fms",
            request_id, request.method, request.url.path,
            response.status_code, elapsed_ms,
        )
        # Expose the request ID so a physician's browser/frontend can reference it
        response.headers["X-Request-ID"] = request_id
        return response
