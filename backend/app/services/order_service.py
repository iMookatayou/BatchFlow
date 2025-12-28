from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import hashlib

from sqlalchemy import select, and_

from app.services.unit_of_work import UnitOfWork
from app.infrastructure.db.models.order import Order
from app.infrastructure.db.models.order_item import OrderItem


# TODO: ปรับให้ตรงกับ enum/status จริงของโปรเจกต์
ORDER_STATUS_PENDING = 1


@dataclass
class OrderService:
    uow: UnitOfWork

    # ---------- helpers ----------

    def _build_generated_key(self, subscription_id: int, delivery_date: date) -> str:
        # deterministic business key (unique constraint exists)
        return f"sub:{subscription_id}|delivery:{delivery_date.isoformat()}"

    def _build_order_no(self, generated_key: str) -> str:
        # deterministic + unique (derived from generated_key)
        digest = hashlib.sha1(generated_key.encode("utf-8")).hexdigest()[:12].upper()
        return f"O{digest}"

    def _order_item_exists(self, order_id: int, variant_id: int) -> bool:
        stmt = (
            select(OrderItem.id)
            .where(
                and_(
                    OrderItem.order_id == order_id,
                    OrderItem.variant_id == variant_id,
                )
            )
            .limit(1)
        )
        return self.uow.session.execute(stmt).first() is not None

    # ---------- main use case ----------

    def generate_from_subscription(
        self,
        subscription_id: int,
        delivery_date: date,
    ) -> tuple[Order, bool]:
        """
        Returns (order, was_created)

        Rules:
        - ALWAYS lock subscription row before checking/creating order
        - One subscription = one transaction
        - Idempotent via Order.generated_key
        - OrderItem price comes from SubscriptionItem.unit_amount
        """
        with self.uow:
            # 1) lock subscription
            sub = self.uow.subscriptions.lock_by_id(subscription_id)
            if not sub:
                raise ValueError("SUBSCRIPTION_NOT_FOUND")

            # 2) active + due checks (based on real schema)
            if sub.deleted_at is not None or sub.canceled_at is not None or sub.paused_at is not None:
                raise ValueError("SUBSCRIPTION_NOT_ACTIVE")

            if sub.next_run_date > delivery_date:
                raise ValueError("SUBSCRIPTION_NOT_DUE")

            # 3) idempotent order check
            generated_key = self._build_generated_key(sub.id, delivery_date)
            existing = self.uow.orders.get_by_generated_key(generated_key)
            if existing:
                return existing, False

            if sub.default_address_id is None:
                raise ValueError("SUBSCRIPTION_DEFAULT_ADDRESS_REQUIRED")

            now = datetime.utcnow()

            # 4) create Order
            order = Order(
                generated_key=generated_key,
                order_no=self._build_order_no(generated_key),
                user_id=sub.user_id,
                subscription_id=sub.id,
                status=ORDER_STATUS_PENDING,
                delivery_date=delivery_date,
                zone_id=None,  # routing can assign later
                shipping_address_id=sub.default_address_id,
                notes=None,
                currency="THB",
                subtotal_amount=0,
                shipping_amount=0,
                total_amount=0,
                created_at=now,
                updated_at=now,
            )
            self.uow.orders.add(order)
            self.uow.session.flush()  # ensure order.id

            # 5) generate OrderItems from SubscriptionItems
            subtotal = 0

            for si in sub.items:
                if si.is_active != 1:
                    continue

                qty = int(si.quantity)
                if qty <= 0:
                    continue

                if si.variant is None:
                    raise ValueError("SUBSCRIPTION_ITEM_VARIANT_MISSING")

                unit_amount = int(si.unit_amount)
                if unit_amount < 0:
                    raise ValueError("SUBSCRIPTION_ITEM_PRICE_INVALID")

                # idempotent on (order_id, variant_id)
                if self._order_item_exists(order.id, si.variant_id):
                    continue

                line_total = unit_amount * qty

                oi = OrderItem(
                    order_id=order.id,
                    variant_id=si.variant_id,
                    sku=si.variant.sku,
                    name=si.variant.name or "",
                    quantity=qty,
                    unit_amount=unit_amount,
                    line_total_amount=line_total,
                    created_at=now,
                    updated_at=now,
                )
                self.uow.session.add(oi)

                subtotal += line_total

            # 6) finalize totals
            order.subtotal_amount = subtotal
            order.total_amount = subtotal + int(order.shipping_amount or 0)
            order.updated_at = now
            self.uow.session.add(order)

            self.uow.session.flush()
            return order, True
