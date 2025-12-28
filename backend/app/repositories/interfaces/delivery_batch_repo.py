from __future__ import annotations

from datetime import date
from typing import Protocol

from app.infrastructure.db.models.delivery_batch import DeliveryBatch
from app.infrastructure.db.models.order import Order


class DeliveryBatchRepo(Protocol):
    def get_open_for_update(self, delivery_date: date, zone_id: int | None) -> DeliveryBatch | None: ...

    def create_open(self, delivery_date: date, zone_id: int | None, cutoff_at) -> DeliveryBatch: ...

    def has_order(self, batch_id: int, order_id: int) -> bool: ...

    def add_order(self, batch: DeliveryBatch, order: Order) -> None: ...

    def lock_due_batches(self, delivery_date: date, now) -> int: ...
