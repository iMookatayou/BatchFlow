from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.logging import get_logger

log = get_logger("app.errors")


def _normalize_detail(detail: Any) -> Dict[str, Any]:
    """
    Normalize FastAPI/HTTPException detail to a dict structure:
    {"code": "...", "message": "...", "details": {...}}
    """
    if isinstance(detail, dict):
        code = detail.get("code") or "ERROR"
        message = detail.get("message")
        details = {k: v for k, v in detail.items() if k not in ("code", "message")}
        return {"code": code, "message": message, "details": details or None}

    # e.g. plain string
    if isinstance(detail, str):
        return {"code": "ERROR", "message": detail, "details": None}

    return {"code": "ERROR", "message": None, "details": {"raw": detail}}


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        payload = _normalize_detail(exc.detail)
        return JSONResponse(status_code=exc.status_code, content=payload)

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        payload = _normalize_detail(getattr(exc, "detail", None))
        return JSONResponse(status_code=exc.status_code, content=payload)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        # log full exception server-side
        log.exception("Unhandled exception", extra={"path": str(request.url.path)})
        return JSONResponse(status_code=500, content={"code": "INTERNAL_ERROR", "message": None, "details": None})
