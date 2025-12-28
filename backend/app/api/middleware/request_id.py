from __future__ import annotations

import uuid
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    - If client sends X-Request-Id: keep it
    - Otherwise generate one
    - Always return X-Request-Id in response
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        rid = request.headers.get("X-Request-Id") or uuid.uuid4().hex
        request.state.request_id = rid

        response = await call_next(request)
        response.headers["X-Request-Id"] = rid
        return response
