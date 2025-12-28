from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from app.services.unit_of_work import UnitOfWork
from app.infrastructure.db.models.order import Order


@dataclass
class DeliveryBatchService:
    uow: UnitOfWork

    def attach_order(self, order_id: int, cutoff_at: datetime) -> int:
        """
        Group by (delivery_date, zone_id), reuse or create OPEN batch.
        Idempotent: re-run will not duplicate join rows.
        Enforced: cannot attach to locked batch.
        """
        with self.uow:
            order = self.uow.session.get(Order, order_id)
            if not order:
                raise ValueError("ORDER_NOT_FOUND")

            # Uses real Order fields
            delivery_date = order.delivery_date
            zone_id = order.zone_id  # can be None per schema

            batch = self.uow.batches.get_open_for_update(delivery_date=delivery_date, zone_id=zone_id)
            if not batch:
                batch = self.uow.batches.create_open(delivery_date=delivery_date, zone_id=zone_id, cutoff_at=cutoff_at)

            # Hard enforcement via schema field
            if batch.locked_at is not None:
                raise ValueError("BATCH_LOCKED")

            self.uow.batches.add_order(batch, order)
            self.uow.session.flush()
            return batch.id

    def lock_batches_if_due(self, delivery_date: date, now: datetime) -> int:
        """
        Lock all OPEN batches for delivery_date where now >= cutoff_at.
        Safe to re-run (idempotent).
        """
        with self.uow:
            return self.uow.batches.lock_due_batches(delivery_date=delivery_date, now=now)
