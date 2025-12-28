from __future__ import annotations

from datetime import date, datetime
from typing import Callable, Dict, Tuple

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.services.unit_of_work import UnitOfWork
from app.infrastructure.db.models.order import Order
from app.infrastructure.db.models.delivery_batch import DeliveryBatch
from app.infrastructure.db.models.delivery_batch_order import DeliveryBatchOrder


# NOTE:
# - status ของ order / batch อาจเป็น enum ของระบบคุณ
# - เพื่อไม่เดา business enum → รับเป็น parameter
DEFAULT_ELIGIBLE_ORDER_STATUS = 1   # เช่น PENDING / READY
DEFAULT_BATCH_STATUS = 1            # เช่น OPEN


def run_create_batches(
    uow_factory: Callable[[], UnitOfWork],
    delivery_date: date,
    eligible_order_status: int = DEFAULT_ELIGIBLE_ORDER_STATUS,
    batch_status: int = DEFAULT_BATCH_STATUS,
) -> Dict[str, int]:
    """
    Create delivery batches and attach eligible orders.

    Idempotent:
    - run ซ้ำได้
    - order ที่ attach แล้วจะไม่ attach ซ้ำ
    - batch ที่ถูก lock แล้วจะไม่ถูกแก้

    Returns summary counts.
    """
    created_batches = 0
    attached_orders = 0

    # ---------- STEP 1: ดึง orders ที่ eligible ----------
    uow = uow_factory()
    with uow:
        orders = (
            uow.session.execute(
                select(Order).where(
                    and_(
                        Order.delivery_date == delivery_date,
                        Order.status == eligible_order_status,
                    )
                )
            )
            .scalars()
            .all()
        )

    if not orders:
        return {
            "delivery_date": delivery_date.isoformat(),
            "batches_created": 0,
            "orders_attached": 0,
        }

    # ---------- STEP 2: group orders by (delivery_date, zone_id) ----------
    groups: Dict[Tuple[date, int | None], list[Order]] = {}
    for order in orders:
        key = (order.delivery_date, order.zone_id)
        groups.setdefault(key, []).append(order)

    # ---------- STEP 3: create / reuse batch + attach orders ----------
    for (d_date, zone_id), group_orders in groups.items():
        uow2 = uow_factory()
        with uow2:
            # 3.1 หา batch ที่ยังไม่ lock
            batch = (
                uow2.session.execute(
                    select(DeliveryBatch).where(
                        and_(
                            DeliveryBatch.delivery_date == d_date,
                            DeliveryBatch.zone_id == zone_id,
                            DeliveryBatch.locked_at.is_(None),
                        )
                    )
                )
                .scalar_one_or_none()
            )

            # 3.2 ถ้าไม่มี batch → create ใหม่
            if not batch:
                now = datetime.utcnow()
                batch = DeliveryBatch(
                    public_id=None,
                    batch_code=f"{d_date.isoformat()}-{zone_id or 'ALL'}",
                    delivery_date=d_date,
                    zone_id=zone_id,
                    cutoff_at=now,   # NOTE: ถ้ามี cutoff rule จริง ค่อยย้าย logic มาตรงนี้
                    status=batch_status,
                    locked_at=None,
                    dispatched_at=None,
                    completed_at=None,
                    created_at=now,
                    updated_at=now,
                )
                uow2.session.add(batch)
                uow2.session.flush()
                created_batches += 1

            # 3.3 attach orders (idempotent)
            for order in group_orders:
                exists = (
                    uow2.session.execute(
                        select(DeliveryBatchOrder).where(
                            and_(
                                DeliveryBatchOrder.batch_id == batch.id,
                                DeliveryBatchOrder.order_id == order.id,
                            )
                        )
                    )
                    .first()
                )

                if exists:
                    continue

                link = DeliveryBatchOrder(
                    batch_id=batch.id,
                    order_id=order.id,
                    created_at=datetime.utcnow(),
                )
                uow2.session.add(link)
                attached_orders += 1

    return {
        "delivery_date": delivery_date.isoformat(),
        "batches_created": created_batches,
        "orders_attached": attached_orders,
    }
