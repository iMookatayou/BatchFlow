from __future__ import annotations

from fastapi import FastAPI

from app.api.v1.router import router as v1_router
from app.settings import settings
from app.logging import configure_logging
from app.errors import register_error_handlers
from app.docs import openapi_tags

from app.api.middleware.request_id import RequestIdMiddleware
from app.api.middleware.rate_limit import RateLimitMiddleware


def create_app() -> FastAPI:
    configure_logging(settings.environment)

    app = FastAPI(
        title=settings.app_name,
        openapi_tags=openapi_tags(),
    )

    # middleware
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(
        RateLimitMiddleware,
        enabled=settings.rate_limit_enabled,
        requests_per_minute=settings.rate_limit_rpm,
    )

    # routers
    app.include_router(v1_router)

    # error handlers (make errors consistent)
    register_error_handlers(app)

    return app


app = create_app()
