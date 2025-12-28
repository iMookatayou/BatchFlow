from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import (
    health_router,
    subscriptions_router,
    orders_router,
    delivery_batches_router,
)

router = APIRouter(prefix="/api/v1")

router.include_router(health_router)
router.include_router(subscriptions_router)
router.include_router(orders_router)
router.include_router(delivery_batches_router)
