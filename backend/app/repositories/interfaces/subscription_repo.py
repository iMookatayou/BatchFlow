from __future__ import annotations

from datetime import date
from typing import Protocol

from app.infrastructure.db.models.subscription import Subscription


class SubscriptionRepo(Protocol):
    def get_by_id(self, subscription_id: int) -> Subscription | None: ...

    def lock_by_id(self, subscription_id: int) -> Subscription | None: ...

    def list_due_active(self, cycle_date: date, limit: int, offset: int = 0) -> list[Subscription]: ...
