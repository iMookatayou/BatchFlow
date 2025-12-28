# app/services/subscription_service.py
from __future__ import annotations

from datetime import date

from app.services.unit_of_work import UnitOfWork
from app.domain.exceptions import DomainError

class SubscriptionService:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    def pause(self, subscription_id: int, reason: str | None = None) -> None:
        with self.uow:
            sub = self.uow.subscriptions.lock_by_id(subscription_id)
            if not sub:
                raise DomainError("SUBSCRIPTION_NOT_FOUND")
            if sub.status not in ("ACTIVE",):  # example
                raise DomainError("SUBSCRIPTION_NOT_PAUSABLE")

            sub.status = "PAUSED"
            if hasattr(sub, "pause_reason"):
                sub.pause_reason = reason

    def resume(self, subscription_id: int) -> None:
        with self.uow:
            sub = self.uow.subscriptions.lock_by_id(subscription_id)
            if not sub:
                raise DomainError("SUBSCRIPTION_NOT_FOUND")
            if sub.status not in ("PAUSED",):
                raise DomainError("SUBSCRIPTION_NOT_RESUMABLE")

            sub.status = "ACTIVE"

    def cancel(self, subscription_id: int) -> None:
        with self.uow:
            sub = self.uow.subscriptions.lock_by_id(subscription_id)
            if not sub:
                raise DomainError("SUBSCRIPTION_NOT_FOUND")
            if sub.status in ("CANCELED",):
                return  # idempotent cancel

            sub.status = "CANCELED"
