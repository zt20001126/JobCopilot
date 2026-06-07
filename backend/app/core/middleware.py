from collections import defaultdict, deque
from time import monotonic, perf_counter
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

from app.core.config import get_settings
from app.utils.logger import get_logger, request_id_context


logger = get_logger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """注入请求标识，并记录不包含业务正文的访问日志。"""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        request.state.request_id = request_id
        token = request_id_context.set(request_id)
        started_at = perf_counter()
        try:
            response = await call_next(request)
            latency_ms = int((perf_counter() - started_at) * 1000)
            response.headers["X-Request-ID"] = request_id
            logger.info(
                "%s %s",
                request.method,
                request.url.path,
                extra={
                    "status_code": response.status_code,
                    "latency_ms": latency_ms,
                },
            )
            return response
        finally:
            request_id_context.reset(token)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """MVP 单实例内存限流；多实例部署时应替换为 Redis。"""

    def __init__(self, app: object) -> None:
        super().__init__(app)
        self.settings = get_settings()
        self.requests: defaultdict[str, deque[float]] = defaultdict(deque)

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        if (
            request.method == "POST"
            and request.url.path == "/api/v1/greeting/generate"
        ):
            client_key = request.client.host if request.client else "unknown"
            now = monotonic()
            timestamps = self.requests[client_key]
            window_start = now - self.settings.rate_limit_window_seconds
            while timestamps and timestamps[0] <= window_start:
                timestamps.popleft()
            if len(timestamps) >= self.settings.rate_limit_requests:
                request_id = getattr(request.state, "request_id", str(uuid4()))
                return JSONResponse(
                    status_code=429,
                    content={
                        "request_id": request_id,
                        "error_code": "RATE_LIMITED",
                        "message": "请求过于频繁，请稍后重试",
                    },
                    headers={"X-Request-ID": request_id},
                )
            timestamps.append(now)

        return await call_next(request)
