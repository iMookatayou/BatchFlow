from __future__ import annotations

from typing import Dict, Any


def openapi_tags() -> list[Dict[str, Any]]:
    return [
        {"name": "health", "description": "Service health checks"},
        {"name": "subscriptions", "description": "Subscription management"},
        {"name": "orders", "description": "Orders (stub)"},
        {"name": "delivery_batches", "description": "Delivery batches (stub)"},
    ]
