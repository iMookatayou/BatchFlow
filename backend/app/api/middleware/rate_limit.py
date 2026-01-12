from __future__ import annotations

import time
from typing import Callable, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Minimal in-memory rate limit stub.
    Production should replace with Redis-based limiter.
    """

    def __init__(
        self,
        app,
        enabled: bool = False,
        requests_per_minute: int = 120,
    ) -> None:
        super().__init__(app)
        self.enabled = enabled
        self.rpm = requests_per_minute
        self._store: dict[str, tuple[int, float]] = {}  

    def _key(self, request: Request) -> str:
        # prefer user id header if present else ip
        return request.headers.get("X-User-Id") or (request.client.host if request.client else "unknown")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not self.enabled:
            return await call_next(request)

        key = self._key(request)
        now = time.time()
        window = 60.0

        count, start = self._store.get(key, (0, now))
        if now - start >= window:
            count, start = 0, now

        count += 1
        self._store[key] = (count, start)

        if count > self.rpm:
            return JSONResponse(
                status_code=429,
                content={"code": "RATE_LIMITED", "message": "Too many requests", "details": {"rpm": self.rpm}},
            )

        return await call_next(request)
