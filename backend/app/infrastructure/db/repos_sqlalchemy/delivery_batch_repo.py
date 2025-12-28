from __future__ import annotations

from datetime import date, datetime
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.infrastructure.db.models.delivery_batch import DeliveryBatch
from app.infrastructure.db.models.order import Order
from app.infrastructure.db.models.delivery_batch_order import DeliveryBatchOrder


# TODO: ปรับให้ตรงกับ enum/status จริงของโปรเจกต์
DELIVERY_BATCH_STATUS_OPEN = 1
DELIVERY_BATCH_STATUS_LOCKED = 2


class SqlAlchemyDeliveryBatchRepo:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_open_for_update(self, delivery_date: date, zone_id: int | None) -> DeliveryBatch | None:
        """
        Get OPEN batch for (delivery_date, zone_id) and lock it (FOR UPDATE).
        """
        cond = [
            DeliveryBatch.delivery_date == delivery_date,
            DeliveryBatch.status == DELIVERY_BATCH_STATUS_OPEN,
            DeliveryBatch.locked_at.is_(None),
        ]
        if zone_id is None:
            cond.append(DeliveryBatch.zone_id.is_(None))
        else:
            cond.append(DeliveryBatch.zone_id == zone_id)

        stmt = select(DeliveryBatch).where(and_(*cond)).with_for_update()
        return self.session.execute(stmt).scalar_one_or_none()

    def create_open(self, delivery_date: date, zone_id: int | None, cutoff_at: datetime) -> DeliveryBatch:
        """
        Create an OPEN batch. batch_code is unique, so generate deterministic value.
        """
        zid = zone_id if zone_id is not None else 0
        batch_code = f"B{delivery_date.strftime('%Y%m%d')}-Z{zid}"

        now = datetime.utcnow()
        batch = DeliveryBatch(
            batch_code=batch_code,
            delivery_date=delivery_date,
            zone_id=zone_id,
            cutoff_at=cutoff_at,
            status=DELIVERY_BATCH_STATUS_OPEN,
            locked_at=None,
            dispatched_at=None,
            completed_at=None,
            created_at=now,
            updated_at=now,
        )
        self.session.add(batch)
        self.session.flush()
        return batch

    def has_order(self, batch_id: int, order_id: int) -> bool:
        stmt = (
            select(DeliveryBatchOrder.order_id)
            .where(
                and_(
                    DeliveryBatchOrder.batch_id == batch_id,
                    DeliveryBatchOrder.order_id == order_id,
                )
            )
            .limit(1)
        )
        return self.session.execute(stmt).first() is not None

    def add_order(self, batch: DeliveryBatch, order: Order) -> None:
        """
        Idempotent attach: no duplicate joins on re-run.
        """
        if self.has_order(batch.id, order.id):
            return
        link = DeliveryBatchOrder(
            batch_id=batch.id,
            order_id=order.id,
            created_at=datetime.utcnow(),
        )
        self.session.add(link)

    def lock_due_batches(self, delivery_date: date, now: datetime) -> int:
        """
        Lock all OPEN batches for delivery_date where now >= cutoff_at.
        Idempotent and concurrency-safe: locks rows before updating.
        """
        # find candidate ids first (no lock)
        ids_stmt = select(DeliveryBatch.id).where(
            and_(
                DeliveryBatch.delivery_date == delivery_date,
                DeliveryBatch.status == DELIVERY_BATCH_STATUS_OPEN,
                DeliveryBatch.locked_at.is_(None),
                DeliveryBatch.cutoff_at <= now,
            )
        )
        ids = [r[0] for r in self.session.execute(ids_stmt).all()]

        locked = 0
        for bid in ids:
            stmt = select(DeliveryBatch).where(DeliveryBatch.id == bid).with_for_update()
            batch = self.session.execute(stmt).scalar_one_or_none()
            if not batch:
                continue
            if batch.locked_at is not None:
                continue
            if batch.cutoff_at > now:
                continue

            batch.locked_at = now
            batch.status = DELIVERY_BATCH_STATUS_LOCKED
            batch.updated_at = datetime.utcnow()
            self.session.add(batch)
            locked += 1

        return locked
