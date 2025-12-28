# app/jobs/tasks/lock_batches.py
from __future__ import annotations

from datetime import date, datetime
from typing import Callable

from app.services.unit_of_work import UnitOfWork
from app.services.delivery_batch_service import DeliveryBatchService


def run_lock_batches(
    uow_factory: Callable[[], UnitOfWork],
    delivery_date: date,
    now: datetime,
) -> dict:
    uow = uow_factory()
    svc = DeliveryBatchService(uow)

    locked = svc.lock_batches_if_due(delivery_date=delivery_date, now=now)

    return {
        "delivery_date": delivery_date.isoformat(),
        "locked": locked,
        "now": now.isoformat(),
    }
